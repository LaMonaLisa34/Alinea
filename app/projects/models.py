from django.conf import settings
from django.db import models
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError


class EditorialProject(models.Model):
    """Représente le contexte de rédaction défini par un utilisateur."""

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(
        "Nom du projet",
        max_length=150,
    )
    description = models.TextField(
        "Description",
        blank=True,
    )
    editorial_guidelines = models.TextField(
        "Consignes générales",
        blank=True,
    )
    created_at = models.DateTimeField(
        "Date de création",
        auto_now_add=True,
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="editorial_projects",
        verbose_name="Propriétaire",
    )

    class Meta:
        db_table = "projects"
        verbose_name = "Projet éditorial"
        verbose_name_plural = "Projets éditoriaux"

    def __str__(self):
        return self.name


class ProjectReferenceSource(models.Model):
    """Définit une référence de projet sous forme de lien ou de texte."""

    class SourceType(models.TextChoices):
        URL = "url", "Lien web"
        TEXT = "text", "Texte"

    id = models.BigAutoField(primary_key=True)

    name = models.CharField(
        "Nom de la source",
        max_length=200,
    )
    source_type = models.CharField(
        "Type de source",
        max_length=10,
        choices=SourceType.choices,
        default=SourceType.URL,
    )
    url = models.TextField(
        "URL",
        blank=True,
        null=True,
        validators=[URLValidator(schemes=["http", "https"])],
    )
    text = models.TextField(
        "Texte de référence",
        blank=True,
        null=True,
    )
    is_priority = models.BooleanField(
        "Source prioritaire",
        default=False,
    )

    # Les références appartiennent au projet et sont supprimées avec celui-ci.
    project = models.ForeignKey(
        EditorialProject,
        on_delete=models.CASCADE,
        related_name="reference_sources",
        verbose_name="Projet éditorial",
    )

    class Meta:
        db_table = "sources"
        verbose_name = "Source de référence"
        verbose_name_plural = "Sources de référence"
        ordering = ["-is_priority", "name", "pk"]

    def clean(self):
        """Exige le contenu correspondant au type de source sélectionné."""
        super().clean()

        # Uniformise les contenus vides pour les champs facultatifs.
        self.url = (self.url or "").strip() or None
        self.text = (self.text or "").strip() or None

        errors = {}

        if self.source_type == self.SourceType.URL:
            if not self.url:
                errors["url"] = "Saisissez l’URL de la source."

            if self.text:
                errors["text"] = (
                    "Retirez le texte pour enregistrer une source de type lien web."
                )

        elif self.source_type == self.SourceType.TEXT:
            if not self.text:
                errors["text"] = "Saisissez le texte de référence."

            if self.url:
                errors["url"] = (
                    "Retirez l’URL pour enregistrer une source de type texte."
                )

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return self.name
