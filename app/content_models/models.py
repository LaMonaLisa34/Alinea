from django.core.validators import MinValueValidator
from django.db import models


class ContentTemplate(models.Model):
    """Définit un modèle de rédaction réutilisable dans un projet éditorial."""

    content_template_id = models.BigAutoField(primary_key=True)

    name = models.CharField(
        "Nom du modèle",
        max_length=150,
    )
    description = models.TextField(
        "Description",
        blank=True,
        null=True,
    )
    project = models.ForeignKey(
        "projects.EditorialProject",
        on_delete=models.CASCADE,
        related_name="content_templates",
        verbose_name="Projet éditorial",
    )

    class Meta:
        db_table = "content_templates"
        verbose_name = "Modèle de contenu"
        verbose_name_plural = "Modèles de contenu"
        ordering = ["name", "pk"]

    def __str__(self):
        return self.name


class ContentBlock(models.Model):
    """Définit un bloc ordonné appartenant à un modèle de rédaction."""

    class BlockType(models.TextChoices):
        TEXT = "text", "Texte"
        NUMBER = "number", "Nombre"
        BOOLEAN = "boolean", "Booléen"
        LIST = "list", "Liste"
        MULTIPLE_CHOICE = "multiple_choice", "Choix multiple"
        SEO = "seo", "Bloc SEO"
        TITLE = "title", "Titre"
        TABLE = "table", "Tableau"
        URL = "url", "URL"
        DATE = "date", "Date"

    content_block_id = models.BigAutoField(primary_key=True)

    name = models.CharField(
        "Nom du bloc",
        max_length=150,
    )
    block_type = models.CharField(
        "Type de bloc",
        max_length=30,
        choices=BlockType.choices,
    )
    instruction = models.TextField(
        "Consignes de rédaction",
        blank=True,
        null=True,
    )
    position = models.IntegerField(
        "Position",
        validators=[MinValueValidator(0)],
    )
    content_template = models.ForeignKey(
        ContentTemplate,
        on_delete=models.CASCADE,
        related_name="blocks",
        verbose_name="Modèle de contenu",
    )

    class Meta:
        db_table = "content_blocks"
        verbose_name = "Bloc de contenu"
        verbose_name_plural = "Blocs de contenu"
        ordering = ["position", "pk"]

    def __str__(self):
        return self.name


class BlockParameter(models.Model):
    """Définit un paramètre de configuration associé à un bloc."""

    block_parameter_id = models.BigAutoField(primary_key=True)

    name = models.CharField(
        "Nom du paramètre",
        max_length=100,
    )
    value = models.TextField(
        "Valeur",
    )
    content_block = models.ForeignKey(
        ContentBlock,
        on_delete=models.CASCADE,
        related_name="parameters",
        verbose_name="Bloc de contenu",
    )

    class Meta:
        db_table = "block_parameters"
        verbose_name = "Paramètre de bloc"
        verbose_name_plural = "Paramètres de bloc"
        ordering = ["name", "pk"]
        constraints = [
            models.UniqueConstraint(
                fields=["content_block", "name"],
                name="unique_parameter_name_per_block",
            ),
        ]

    def __str__(self):
        return self.name
