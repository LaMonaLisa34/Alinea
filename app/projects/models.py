from django.conf import settings
from django.db import models


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
