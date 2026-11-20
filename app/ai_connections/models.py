from django.conf import settings
from django.db import models


class AIConnection(models.Model):
    """Conserve le mode de connexion IA choisi par un utilisateur."""

    class Mode(models.TextChoices):
        ALINEA = "alinea", "Service Alinea"
        OLLAMA = "ollama", "Ollama personnel"

    # Chaque utilisateur dispose d’une seule configuration IA.
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ai_connection",
        verbose_name="Utilisateur",
    )

    mode = models.CharField(
        "Mode de connexion",
        max_length=20,
        choices=Mode.choices,
        default=Mode.ALINEA,
    )

    # Ces champs concernent uniquement la connexion personnelle.
    base_url = models.URLField(
        "Adresse du service",
        max_length=500,
        blank=True,
    )
    model_name = models.CharField(
        "Nom du modèle",
        max_length=150,
        blank=True,
    )

    created_at = models.DateTimeField(
        "Date de création",
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        "Date de modification",
        auto_now=True,
    )

    class Meta:
        db_table = "ai_connections"
        verbose_name = "Connexion IA"
        verbose_name_plural = "Connexions IA"

    def __str__(self):
        return f"Connexion IA de l’utilisateur {self.user_id}"
