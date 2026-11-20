import json
import socket
import time
from concurrent.futures import TimeoutError as FutureTimeout
from threading import Event
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .forms import AIConnectionForm
from .models import AIConnection
from .services.network import (
    AIConnectionError,
    Destination,
    parse_origin,
    resolve_destination,
)
from .services.ollama import (
    MAX_RESPONSE_BYTES,
    check_ollama_connection,
    extract_generated_text,
    perform_test,
    read_response_body,
    validate_http_response,
)

User = get_user_model()

NETWORK_MODULE = "ai_connections.services.network"
OLLAMA_MODULE = "ai_connections.services.ollama"


class AIConnectionFormTests(TestCase):
    """Vérifie la validation des paramètres sans contacter le service IA."""

    def test_ollama_requires_address_and_model(self):
        """Exige les deux paramètres de la connexion personnelle."""
        form = AIConnectionForm(
            data={
                "mode": AIConnection.Mode.OLLAMA,
                "base_url": "",
                "model_name": "",
            },
        )

        self.assertFalse(form.is_valid())
        self.assertIn("base_url", form.errors)
        self.assertIn("model_name", form.errors)

    def test_valid_ollama_configuration(self):
        """Accepte une configuration personnelle correctement renseignée."""
        form = AIConnectionForm(
            data={
                "mode": AIConnection.Mode.OLLAMA,
                "base_url": "http://host.docker.internal:11434/",
                "model_name": "qwen2.5:7b",
            },
        )

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(
            form.cleaned_data["base_url"],
            "http://host.docker.internal:11434",
        )

    def test_invalid_service_addresses_are_rejected(self):
        """Refuse les protocoles et composants incompatibles avec une origine."""
        addresses = (
            "ftp://ollama.example.com",
            "https://user:secret@ollama.example.com",
            "https://ollama.example.com/api/generate",
            "https://ollama.example.com?target=other",
            "https://ollama.example.com#section",
            "https://ollama.example.com:70000",
        )

        for address in addresses:
            with self.subTest(address=address):
                form = AIConnectionForm(
                    data={
                        "mode": AIConnection.Mode.OLLAMA,
                        "base_url": address,
                        "model_name": "qwen2.5:7b",
                    },
                )

                self.assertFalse(form.is_valid())
                self.assertIn("base_url", form.errors)

    def test_alinea_mode_clears_personal_parameters(self):
        """N’enregistre pas les paramètres personnels en mode Alinea."""
        form = AIConnectionForm(
            data={
                "mode": AIConnection.Mode.ALINEA,
                "base_url": "http://host.docker.internal:11434",
                "model_name": "qwen2.5:7b",
            },
        )

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["base_url"], "")
        self.assertEqual(form.cleaned_data["model_name"], "")


@override_settings(AI_OLLAMA_LOCAL_ORIGIN="")
class NetworkPolicyTests(SimpleTestCase):
    """Vérifie les destinations autorisées sans effectuer de résolution réelle."""

    @staticmethod
    def dns_answer(address, port=443):
        """Construit une réponse DNS IPv4 pour les tests."""
        return (
            socket.AF_INET,
            socket.SOCK_STREAM,
            socket.IPPROTO_TCP,
            "",
            (address, port),
        )

    def test_origin_is_normalized(self):
        """Normalise le domaine et attribue le port HTTPS par défaut."""
        self.assertEqual(
            parse_origin("https://OLLAMA.example.com/"),
            ("https", "ollama.example.com", 443),
        )

    def test_public_https_destination_is_allowed(self):
        """Retourne l’adresse publique qui devra être utilisée par le transport."""
        with patch(
            f"{NETWORK_MODULE}.socket.getaddrinfo",
            return_value=[self.dns_answer("8.8.8.8")],
        ):
            destination = resolve_destination("https://ollama.example.com")

        self.assertEqual(destination.hostname, "ollama.example.com")
        self.assertEqual(destination.address, ("8.8.8.8", 443))
        self.assertEqual(destination.family, socket.AF_INET)

    def test_http_without_local_exception_is_rejected(self):
        """Refuse HTTP avant toute résolution DNS en l’absence d’exception."""
        with patch(f"{NETWORK_MODULE}.socket.getaddrinfo") as resolver:
            with self.assertRaises(AIConnectionError):
                resolve_destination("http://ollama.example.com")

        resolver.assert_not_called()

    def test_non_public_destinations_are_rejected(self):
        """Refuse les réseaux privés, la boucle locale et les adresses spéciales."""
        addresses = (
            "10.0.0.5",
            "172.16.0.5",
            "192.168.1.5",
            "127.0.0.1",
            "169.254.169.254",
            "0.0.0.0",
            "224.0.0.1",
        )

        for address in addresses:
            with self.subTest(address=address):
                with patch(
                    f"{NETWORK_MODULE}.socket.getaddrinfo",
                    return_value=[self.dns_answer(address)],
                ):
                    with self.assertRaises(AIConnectionError):
                        resolve_destination("https://ollama.example.com")

    def test_mixed_dns_response_is_rejected(self):
        """Refuse une réponse contenant une IP publique et une IP interdite."""
        with patch(
            f"{NETWORK_MODULE}.socket.getaddrinfo",
            return_value=[
                self.dns_answer("8.8.8.8"),
                self.dns_answer("127.0.0.1"),
            ],
        ):
            with self.assertRaises(AIConnectionError):
                resolve_destination("https://ollama.example.com")

    @override_settings(
        AI_OLLAMA_LOCAL_ORIGIN="http://host.docker.internal:11434",
    )
    def test_explicit_local_origin_is_allowed(self):
        """Autorise le service privé explicitement désigné par le déploiement."""
        with patch(
            f"{NETWORK_MODULE}.socket.getaddrinfo",
            return_value=[self.dns_answer("192.168.65.254", 11434)],
        ):
            destination = resolve_destination(
                "http://host.docker.internal:11434",
            )

        self.assertEqual(destination.address, ("192.168.65.254", 11434))

    @override_settings(
        AI_OLLAMA_LOCAL_ORIGIN="http://host.docker.internal:11434",
    )
    def test_local_exception_does_not_authorize_other_ports(self):
        """Limite l’exception locale au port configuré."""
        with patch(f"{NETWORK_MODULE}.socket.getaddrinfo") as resolver:
            with self.assertRaises(AIConnectionError):
                resolve_destination("http://host.docker.internal:8000")

        resolver.assert_not_called()

    def test_ipv6_loopback_is_rejected(self):
        """Applique également le filtrage à la boucle locale IPv6."""
        answer = (
            socket.AF_INET6,
            socket.SOCK_STREAM,
            socket.IPPROTO_TCP,
            "",
            ("::1", 443, 0, 0),
        )

        with patch(
            f"{NETWORK_MODULE}.socket.getaddrinfo",
            return_value=[answer],
        ):
            with self.assertRaises(AIConnectionError):
                resolve_destination("https://ollama.example.com")

    def test_dns_failure_is_reported(self):
        """Transforme un échec DNS en erreur compréhensible."""
        with patch(
            f"{NETWORK_MODULE}.socket.getaddrinfo",
            side_effect=socket.gaierror(),
        ):
            with self.assertRaisesMessage(
                AIConnectionError,
                "Le nom du service est introuvable.",
            ):
                resolve_destination("https://ollama.example.com")


class OllamaServiceTests(SimpleTestCase):
    """Vérifie les réponses et les appels du connecteur avec des transports simulés."""

    def test_http_errors_are_reported(self):
        """Refuse les redirections et les principaux statuts d’erreur."""
        cases = (
            (302, "redirection"),
            (401, "refuse l’accès"),
            (403, "refuse l’accès"),
            (404, "introuvable"),
            (500, "retourné une erreur"),
        )

        for status, expected_message in cases:
            with self.subTest(status=status):
                response = MagicMock()
                response.status = status

                with self.assertRaisesMessage(
                    AIConnectionError,
                    expected_message,
                ):
                    validate_http_response(response)

    def test_non_json_response_is_rejected(self):
        """Refuse une réponse HTML même si son statut HTTP est valide."""
        response = MagicMock()
        response.status = 200
        response.getheader.return_value = "text/html"

        with self.assertRaisesMessage(
            AIConnectionError,
            "réponse JSON",
        ):
            validate_http_response(response)

    def test_valid_generation_is_extracted(self):
        """Extrait uniquement le texte d’une génération terminée."""
        body = json.dumps(
            {"done": True, "response": " Bonjour ! "},
        ).encode()

        self.assertEqual(extract_generated_text(body), "Bonjour !")

    def test_invalid_generation_is_rejected(self):
        """Refuse le JSON invalide et les réponses incompatibles ou incomplètes."""
        bodies = (
            b"not-json",
            b"\xff",
            b"[]",
            b'{"done": false, "response": "Bonjour"}',
            b'{"done": true, "response": ""}',
            b'{"done": true, "response": 42}',
        )

        for body in bodies:
            with self.subTest(body=body):
                with self.assertRaises(AIConnectionError):
                    extract_generated_text(body)

    def test_oversized_response_is_rejected(self):
        """Interrompt la lecture lorsque la taille maximale est dépassée."""
        response = MagicMock()
        response.isclosed.return_value = False
        response.read1.return_value = b"x" * 4096
        transport = MagicMock()

        with self.assertRaisesMessage(
            AIConnectionError,
            "taille autorisée",
        ):
            read_response_body(
                response,
                transport,
                time.monotonic() + 30,
                Event(),
            )

        self.assertEqual(
            response.read1.call_count,
            MAX_RESPONSE_BYTES // 4096 + 1,
        )

    def test_closed_response_is_not_read_again(self):
        """Évite de manipuler une connexion après consommation de la réponse."""
        response = MagicMock()
        response.isclosed.side_effect = [False, True]
        response.read1.return_value = b'{"done": true}'
        transport = MagicMock()

        body = read_response_body(
            response,
            transport,
            time.monotonic() + 30,
            Event(),
        )

        self.assertEqual(body, b'{"done": true}')
        self.assertEqual(transport.settimeout.call_count, 1)
        self.assertEqual(response.read1.call_count, 1)

    def test_generation_uses_validated_destination(self):
        """Utilise le transport validé et envoie la demande au chemin prévu."""
        destination = Destination(
            scheme="http",
            hostname="host.docker.internal",
            port=11434,
            family=socket.AF_INET,
            address=("192.168.65.254", 11434),
        )

        response = MagicMock()
        response.status = 200
        response.getheader.return_value = "application/json"
        response.isclosed.side_effect = [False, True]
        response.read1.return_value = b'{"done": true, "response": "Bonjour !"}'

        with (
            patch(
                f"{OLLAMA_MODULE}.resolve_destination",
                return_value=destination,
            ),
            patch(f"{OLLAMA_MODULE}.open_transport") as open_transport,
            patch(
                f"{OLLAMA_MODULE}.http.client.HTTPConnection",
            ) as connection_class,
        ):
            connection = connection_class.return_value
            connection.getresponse.return_value.__enter__.return_value = response

            text = perform_test(
                "http://host.docker.internal:11434",
                "qwen2.5:7b",
                time.monotonic() + 30,
                Event(),
            )

        self.assertEqual(text, "Bonjour !")
        self.assertEqual(
            open_transport.call_args.args[0],
            destination,
        )
        self.assertIs(connection.sock, open_transport.return_value)

        connection.request.assert_called_once()
        args, kwargs = connection.request.call_args
        self.assertEqual(args, ("POST", "/api/generate"))

        payload = json.loads(kwargs["body"])
        self.assertEqual(payload["model"], "qwen2.5:7b")
        self.assertIs(payload["stream"], False)
        self.assertEqual(payload["options"]["num_predict"], 24)
        connection.close.assert_called_once()

    def test_global_timeout_is_reported(self):
        """Retourne une erreur lorsque l’attente du travail dépasse le délai."""
        with (
            patch(f"{OLLAMA_MODULE}._slots") as slots,
            patch(f"{OLLAMA_MODULE}._executor") as executor,
        ):
            slots.acquire.return_value = True
            future = executor.submit.return_value
            future.result.side_effect = FutureTimeout()

            with self.assertRaisesMessage(
                AIConnectionError,
                "dépassé 30 secondes",
            ):
                check_ollama_connection(
                    "http://host.docker.internal:11434",
                    "qwen2.5:7b",
                )

            future.cancel.assert_called_once()

            # Le signal d’annulation est transmis au travail réseau.
            cancelled = executor.submit.call_args.args[4]
            self.assertTrue(cancelled.is_set())


class AIConnectionViewTests(TestCase):
    """Vérifie l’enregistrement, le test et l’isolation des configurations."""

    @classmethod
    def setUpTestData(cls):
        """Prépare deux comptes possédant chacun leur configuration."""
        now = timezone.now()
        common_fields = {
            "terms_accepted_at": now,
            "privacy_policy_accepted_at": now,
        }

        cls.user = User.objects.create_user(
            email="owner@example.com",
            name="Owner",
            **common_fields,
        )
        cls.other_user = User.objects.create_user(
            email="other@example.com",
            name="Other User",
            **common_fields,
        )

        cls.connection = AIConnection.objects.create(
            user=cls.user,
            mode=AIConnection.Mode.OLLAMA,
            base_url="https://owner.example.com",
            model_name="owner-model",
        )
        cls.other_connection = AIConnection.objects.create(
            user=cls.other_user,
            mode=AIConnection.Mode.OLLAMA,
            base_url="https://other.example.com",
            model_name="other-model",
        )

    def setUp(self):
        self.url = reverse("ai_connections:configuration")

    def configuration_data(self, **overrides):
        """Construit les paramètres valides d’une connexion personnelle."""
        data = {
            "mode": AIConnection.Mode.OLLAMA,
            "base_url": "http://host.docker.internal:11434",
            "model_name": "qwen2.5:7b",
        }
        data.update(overrides)
        return data

    def test_anonymous_user_cannot_access_configuration(self):
        """Exige une session pour consulter ou enregistrer la configuration."""
        for method in ("get", "post"):
            with self.subTest(method=method):
                if method == "get":
                    response = self.client.get(self.url)
                else:
                    response = self.client.post(
                        self.url,
                        self.configuration_data(),
                    )

                self.assertRedirects(
                    response,
                    f"{reverse('accounts:account')}?next={self.url}",
                    fetch_redirect_response=False,
                )

    def test_page_displays_only_current_user_configuration(self):
        """Préremplit le formulaire avec la configuration du compte connecté."""
        self.client.force_login(self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "ai_connections/configuration.html",
        )
        self.assertEqual(
            response.context["form"].instance.pk,
            self.connection.pk,
        )
        self.assertNotContains(response, self.other_connection.base_url)
        self.assertNotContains(response, self.other_connection.model_name)

    @patch(
        "ai_connections.views.check_ollama_connection",
        return_value="Bonjour !",
    )
    def test_valid_configuration_is_saved_and_tested(self, check_connection):
        """Enregistre les paramètres puis affiche le résultat de génération."""
        self.client.force_login(self.user)

        response = self.client.post(
            self.url,
            self.configuration_data(),
        )

        self.assertRedirects(
            response,
            self.url,
            fetch_redirect_response=False,
        )

        self.connection.refresh_from_db()
        self.assertEqual(self.connection.model_name, "qwen2.5:7b")
        self.assertEqual(
            self.connection.base_url,
            "http://host.docker.internal:11434",
        )

        check_connection.assert_called_once_with(
            "http://host.docker.internal:11434",
            "qwen2.5:7b",
        )

        messages = [str(message) for message in get_messages(response.wsgi_request)]
        self.assertTrue(
            any("Le modèle a répondu au test : Bonjour !" in text for text in messages)
        )

    @patch(
        "ai_connections.views.check_ollama_connection",
        side_effect=AIConnectionError("Service inaccessible."),
    )
    def test_failed_test_preserves_saved_configuration(self, check_connection):
        """Conserve les paramètres enregistrés lorsque le service ne répond pas."""
        self.client.force_login(self.user)

        response = self.client.post(
            self.url,
            self.configuration_data(),
        )

        self.connection.refresh_from_db()
        self.assertEqual(self.connection.model_name, "qwen2.5:7b")
        check_connection.assert_called_once()

        messages = [str(message) for message in get_messages(response.wsgi_request)]
        self.assertTrue(
            any(
                "Configuration enregistrée, mais le test a échoué" in text
                for text in messages
            )
        )

    @patch("ai_connections.views.check_ollama_connection")
    def test_invalid_configuration_is_not_saved_or_tested(self, check_connection):
        """Refuse une soumission invalide avant tout appel au service."""
        self.client.force_login(self.user)

        response = self.client.post(
            self.url,
            self.configuration_data(model_name=""),
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("model_name", response.context["form"].errors)

        self.connection.refresh_from_db()
        self.assertEqual(self.connection.model_name, "owner-model")
        check_connection.assert_not_called()

    @patch(
        "ai_connections.views.check_ollama_connection",
        return_value="Bonjour !",
    )
    def test_post_cannot_target_another_user_configuration(self, check_connection):
        """Ignore les identifiants ajoutés pour cibler la configuration d’autrui."""
        self.client.force_login(self.user)

        self.client.post(
            self.url,
            self.configuration_data(
                user=self.other_user.pk,
                user_id=self.other_user.pk,
                id=self.other_connection.pk,
            ),
        )

        self.other_connection.refresh_from_db()
        self.assertEqual(
            self.other_connection.base_url,
            "https://other.example.com",
        )
        self.assertEqual(
            self.other_connection.model_name,
            "other-model",
        )
        self.assertEqual(
            self.other_connection.user_id,
            self.other_user.pk,
        )

        self.connection.refresh_from_db()
        self.assertEqual(self.connection.user_id, self.user.pk)
        self.assertEqual(self.connection.model_name, "qwen2.5:7b")
        self.assertEqual(AIConnection.objects.count(), 2)

    @patch(
        "ai_connections.views.check_ollama_connection",
        return_value="Bonjour !",
    )
    def test_configuration_persists_after_new_session(self, check_connection):
        """Retrouve les paramètres après fermeture et réouverture de session."""
        self.client.force_login(self.user)
        self.client.post(self.url, self.configuration_data())
        self.client.logout()
        self.client.force_login(self.user)

        response = self.client.get(self.url)

        form = response.context["form"]
        self.assertEqual(
            form["base_url"].value(),
            "http://host.docker.internal:11434",
        )
        self.assertEqual(form["model_name"].value(), "qwen2.5:7b")

    @patch("ai_connections.views.check_ollama_connection")
    def test_alinea_mode_reports_unavailable_test(self, check_connection):
        """Signale l’indisponibilité du test Alinea sans contacter Ollama."""
        self.client.force_login(self.user)

        response = self.client.post(
            self.url,
            {"mode": AIConnection.Mode.ALINEA},
        )

        check_connection.assert_not_called()
        self.connection.refresh_from_db()
        self.assertEqual(self.connection.mode, AIConnection.Mode.ALINEA)

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(
                "pas encore disponible" in str(message) and "warning" in message.tags
                for message in messages
            )
        )
