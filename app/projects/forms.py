from django import forms

from .models import EditorialProject, ProjectReferenceSource


class EditorialProjectForm(forms.ModelForm):
    """Valide les informations saisies lors de la création d’un projet."""

    class Meta:
        model = EditorialProject
        fields = ("name", "description", "editorial_guidelines")
        widgets = {
            "name": forms.TextInput(
                attrs={"placeholder": "Ex. : Encyclopédie des races équines"},
            ),
            "description": forms.Textarea(attrs={"rows": 3}),
            "editorial_guidelines": forms.Textarea(attrs={"rows": 5}),
        }


class ProjectReferenceSourceForm(forms.ModelForm):
    """Valide une référence de projet sous forme de lien web ou de texte."""

    class Meta:
        model = ProjectReferenceSource
        fields = (
            "name",
            "source_type",
            "url",
            "text",
            "is_priority",
        )

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": "Nom de la référence",
                },
            ),
            "source_type": forms.Select(),
            "url": forms.URLInput(
                attrs={
                    "placeholder": "https://exemple.fr/reference",
                },
            ),
            "text": forms.Textarea(
                attrs={
                    "placeholder": "Saisissez ou collez votre texte de référence.",
                    "rows": 5,
                },
            ),
        }

        help_texts = {
            "source_type": "Choisissez un lien web ou un texte fourni directement.",
            "url": "Adresse de la page ou du document de référence.",
            "text": "Notes, extrait ou documentation à utiliser pour la rédaction.",
            "is_priority": (
                "Indique que cette source est à privilégier "
                "pour les rédactions du projet."
            ),
        }
