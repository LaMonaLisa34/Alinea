from urllib.parse import urlsplit

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from .models import AIConnection


class AIConnectionForm(forms.ModelForm):
    """Valide les paramètres du service sans effectuer d’appel réseau."""

    base_url = forms.CharField(
        label="Adresse du service",
        max_length=500,
        required=False,
        help_text="Adresse de base d’Ollama, sans le chemin /api/generate.",
        widget=forms.URLInput(
            attrs={
                "placeholder": "http://host.docker.internal:11434",
                "autocomplete": "off",
            },
        ),
    )

    class Meta:
        model = AIConnection
        fields = ("mode", "base_url", "model_name")
        widgets = {
            "model_name": forms.TextInput(
                attrs={
                    "placeholder": "qwen2.5:7b",
                    "autocomplete": "off",
                },
            ),
        }
        help_texts = {
            "model_name": ("Nom exact d’un modèle installé, par exemple qwen2.5:7b."),
        }

    def clean(self):
        """Applique les règles correspondant au mode sélectionné."""
        cleaned_data = super().clean()
        mode = cleaned_data.get("mode")

        if mode == AIConnection.Mode.ALINEA:
            # Les paramètres du service Alinea sont définis côté serveur.
            cleaned_data["base_url"] = ""
            cleaned_data["model_name"] = ""
            return cleaned_data

        if mode != AIConnection.Mode.OLLAMA:
            return cleaned_data

        base_url = cleaned_data.get("base_url")
        model_name = cleaned_data.get("model_name")

        if "base_url" not in self.errors:
            if not base_url:
                self.add_error(
                    "base_url",
                    "Saisissez l’adresse de votre service Ollama.",
                )
            else:
                try:
                    cleaned_data["base_url"] = self.validate_base_url(base_url)
                except ValidationError as error:
                    self.add_error("base_url", error)

        if not model_name and "model_name" not in self.errors:
            self.add_error(
                "model_name",
                "Saisissez le nom du modèle à utiliser.",
            )

        return cleaned_data

    @staticmethod
    def validate_base_url(value):
        """Valide la structure de l’adresse, sans autoriser son accès réseau."""
        validator = URLValidator(schemes=["http", "https"])
        validator(value)

        try:
            parsed = urlsplit(value)
            port = parsed.port
        except ValueError as error:
            raise ValidationError(
                "L’adresse ou le port du service est invalide."
            ) from error

        if not parsed.hostname:
            raise ValidationError("Saisissez une adresse de service valide.")

        if parsed.username is not None or parsed.password is not None:
            raise ValidationError(
                "L’adresse ne doit pas contenir d’identifiant ni de mot de passe."
            )

        if parsed.path not in ("", "/") or "?" in value or "#" in value:
            raise ValidationError(
                "Saisissez uniquement l’adresse de base du service, "
                "sans chemin, paramètres ni fragment."
            )

        if port is not None and not 1 <= port <= 65535:
            raise ValidationError("Le port doit être compris entre 1 et 65535.")

        return value.rstrip("/")
