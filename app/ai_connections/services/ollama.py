import http.client
import json
import socket
import ssl
import time
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeout
from threading import BoundedSemaphore, Event

from .network import AIConnectionError, resolve_destination

TEST_TIMEOUT = 30
SOCKET_TIMEOUT = 10
MAX_RESPONSE_BYTES = 64 * 1024
JSON_CONTENT_TYPE = "application/json"

# Limite les opérations réseau simultanées dans chaque processus Django.
_executor = ThreadPoolExecutor(max_workers=4)
_slots = BoundedSemaphore(4)


def remaining_time(deadline, cancelled):
    """Calcule le délai disponible avant la prochaine opération réseau."""
    remaining = deadline - time.monotonic()

    if cancelled.is_set() or remaining <= 0:
        raise AIConnectionError(
            "Le délai du test est dépassé. Vérifiez le service et réessayez."
        )

    return min(SOCKET_TIMEOUT, remaining)


def open_transport(destination, timeout):
    """Établit une connexion vers l’adresse IP préalablement autorisée."""
    transport = socket.socket(destination.family, socket.SOCK_STREAM)

    try:
        transport.settimeout(timeout)

        # Utilise directement l’IP validée, sans nouvelle résolution DNS.
        transport.connect(destination.address)

        if destination.scheme == "https":
            # Conserve la vérification du certificat pour le domaine d’origine.
            transport = ssl.create_default_context().wrap_socket(
                transport,
                server_hostname=destination.hostname,
            )

        return transport

    except Exception:
        # Libère la socket si la connexion ou la négociation TLS échoue.
        transport.close()
        raise


def validate_http_response(response):
    """Vérifie le statut HTTP et le type de contenu sans suivre de redirection."""
    if 300 <= response.status < 400:
        raise AIConnectionError(
            "Le service demande une redirection, qui a été refusée."
        )

    if response.status in (401, 403):
        raise AIConnectionError(
            "Le service refuse l’accès. Vérifiez son authentification."
        )

    if response.status == 404:
        raise AIConnectionError("Le modèle ou le point d’accès Ollama est introuvable.")

    if response.status != 200:
        raise AIConnectionError(
            "Le service IA a retourné une erreur. Réessayez ultérieurement."
        )

    content_type = response.getheader("Content-Type", "").split(";")[0].strip().lower()

    if content_type != JSON_CONTENT_TYPE:
        raise AIConnectionError("Le service n’a pas retourné une réponse JSON.")


def read_response_body(response, transport, deadline, cancelled):
    """Lit la réponse en limitant sa taille et les délais entre opérations."""
    body = bytearray()

    # Une réponse entièrement consommée peut avoir déjà fermé la connexion.
    while not response.isclosed():
        transport.settimeout(remaining_time(deadline, cancelled))
        chunk = response.read1(4096)

        if not chunk:
            break

        body.extend(chunk)

        if len(body) > MAX_RESPONSE_BYTES:
            raise AIConnectionError(
                "La réponse du service dépasse la taille autorisée."
            )

    return body


def extract_generated_text(body):
    """Vérifie le format Ollama et extrait le texte d’une génération terminée."""
    try:
        result = json.loads(body)
    except ValueError as error:
        raise AIConnectionError("La réponse JSON du service est invalide.") from error

    if not isinstance(result, dict):
        raise AIConnectionError("Le format de réponse est incompatible.")

    text = result.get("response")

    if result.get("done") is not True or not isinstance(text, str) or not text.strip():
        raise AIConnectionError(
            "Le service n’a pas retourné de génération terminée contenant du texte."
        )

    # Limite le texte destiné au message affiché dans l’interface.
    return text.strip()[:500]


def perform_test(base_url, model_name, deadline, cancelled):
    """Envoie une génération courte au service après contrôle de la destination."""
    connection = None
    transport = None

    try:
        destination = resolve_destination(base_url)
        timeout = remaining_time(deadline, cancelled)

        connection_class = (
            http.client.HTTPSConnection
            if destination.scheme == "https"
            else http.client.HTTPConnection
        )
        connection = connection_class(
            destination.hostname,
            destination.port,
            timeout=timeout,
        )

        transport = open_transport(destination, timeout)
        connection.sock = transport
        transport.settimeout(remaining_time(deadline, cancelled))

        payload = json.dumps(
            {
                "model": model_name,
                "prompt": "Réponds en français par une courte phrase de salutation.",
                "stream": False,
                "options": {
                    "num_predict": 24,
                },
            }
        ).encode("utf-8")

        connection.request(
            "POST",
            "/api/generate",
            body=payload,
            headers={
                "Content-Type": JSON_CONTENT_TYPE,
                "Accept": JSON_CONTENT_TYPE,
                "Connection": "close",
            },
        )

        with connection.getresponse() as response:
            validate_http_response(response)
            body = read_response_body(
                response,
                transport,
                deadline,
                cancelled,
            )

        return extract_generated_text(body)

    except ssl.SSLError as error:
        raise AIConnectionError(
            "La connexion HTTPS n’a pas pu être établie ou vérifiée."
        ) from error

    except TimeoutError as error:
        raise AIConnectionError("Le service met trop de temps à répondre.") from error

    except (OSError, http.client.HTTPException) as error:
        raise AIConnectionError(
            "Impossible de communiquer avec le service IA."
        ) from error

    finally:
        if connection is not None:
            connection.close()

        if transport is not None:
            transport.close()


def check_ollama_connection(base_url, model_name):
    """Limite l’attente du test, y compris pendant la résolution DNS."""
    if not _slots.acquire(blocking=False):
        raise AIConnectionError(
            "Plusieurs tests sont déjà en cours. Réessayez dans un instant."
        )

    cancelled = Event()
    deadline = time.monotonic() + TEST_TIMEOUT

    try:
        future = _executor.submit(
            perform_test,
            base_url,
            model_name,
            deadline,
            cancelled,
        )
    except Exception:
        _slots.release()
        raise

    # Libère la place à la fin effective du travail, même après un délai dépassé.
    future.add_done_callback(lambda _: _slots.release())

    try:
        return future.result(timeout=TEST_TIMEOUT)

    except FutureTimeout as error:
        cancelled.set()
        future.cancel()

        raise AIConnectionError(
            "Le test a dépassé 30 secondes. Le modèle peut être en cours de chargement."
        ) from error
