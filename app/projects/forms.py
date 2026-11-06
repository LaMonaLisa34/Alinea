from django import forms

from .models import EditorialProject


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
