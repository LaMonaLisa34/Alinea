import ipaddress
import socket
from dataclasses import dataclass
from urllib.parse import urlsplit

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator


class AIConnectionError(Exception):
    """Signale une erreur de connexion pouvant être présentée à l’utilisateur."""


@dataclass(frozen=True)
class Destination:
    """Décrit une destination résolue et autorisée."""

    scheme: str
    hostname: str
    port: int
    family: int
    address: tuple


# Plages privées admises uniquement pour l’origine locale explicitement
# autorisée par le déploiement. Elles ne constituent pas une autorisation globale.
LOCAL_NETWORKS = (
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("fc00::/7"),
)


def parse_origin(value):
    """Vérifie une adresse de base et retourne son origine normalisée."""
    if not isinstance(value, str):
        raise AIConnectionError("L’adresse du service est invalide.")

    try:
        URLValidator(schemes=["http", "https"])(value)
        parsed = urlsplit(value)
        port = parsed.port
    except (ValidationError, ValueError) as error:
        raise AIConnectionError("L’adresse du service est invalide.") from error

    if (
        not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path not in ("", "/")
        or "?" in value
        or "#" in value
        or "\\" in value
    ):
        raise AIConnectionError(
            "Utilisez une adresse de base sans identifiants ni paramètres."
        )

    if port is not None and not 1 <= port <= 65535:
        raise AIConnectionError("Le port du service est invalide.")

    return (
        parsed.scheme.lower(),
        parsed.hostname.lower(),
        port or (443 if parsed.scheme.lower() == "https" else 80),
    )


def resolve_destination(base_url):
    """Résout le service et contrôle toutes les adresses IP retournées."""
    scheme, hostname, port = parse_origin(base_url)

    local_origin = getattr(settings, "AI_OLLAMA_LOCAL_ORIGIN", "")
    local_allowed = bool(local_origin) and (
        (scheme, hostname, port) == parse_origin(local_origin)
    )

    if scheme != "https" and not local_allowed:
        raise AIConnectionError(
            "HTTPS est obligatoire, sauf pour le service local "
            "explicitement autorisé par l’administrateur."
        )

    try:
        addresses = socket.getaddrinfo(
            hostname,
            port,
            type=socket.SOCK_STREAM,
        )
    except socket.gaierror as error:
        raise AIConnectionError("Le nom du service est introuvable.") from error

    if not addresses:
        raise AIConnectionError("Aucune adresse réseau trouvée pour ce service.")

    # Refuse également les réponses DNS mêlant adresses publiques et interdites.
    for family, _, _, _, address in addresses:
        if family not in (socket.AF_INET, socket.AF_INET6):
            raise AIConnectionError("Ce type d’adresse réseau est interdit.")

        ip = ipaddress.ip_address(address[0])
        checked_ip = getattr(ip, "ipv4_mapped", None) or ip

        public_allowed = checked_ip.is_global and not checked_ip.is_multicast
        private_allowed = local_allowed and any(
            checked_ip in network for network in LOCAL_NETWORKS
        )

        if not public_allowed and not private_allowed:
            raise AIConnectionError("Cette destination réseau n’est pas autorisée.")

    family, _, _, _, address = addresses[0]

    return Destination(
        scheme=scheme,
        hostname=hostname,
        port=port,
        family=family,
        address=address,
    )
