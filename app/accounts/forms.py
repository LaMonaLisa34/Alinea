from django import forms
from django.contrib.auth.forms import BaseUserCreationForm
from django.utils import timezone

from .models import User


class RegistrationForm(BaseUserCreationForm):
    """Gère l’inscription et l’acceptation des documents associés.

    Les champs de mot de passe, leur validation et leur hachage sont
    pris en charge par BaseUserCreationForm.
    """

    # Ces cases sont obligatoires et ne correspondent pas à des colonnes en base.
    accept_terms = forms.BooleanField(
        label="J’accepte les conditions d’utilisation.",
    )
    acknowledge_privacy_policy = forms.BooleanField(
        label="J’ai pris connaissance de la politique de confidentialité.",
    )

    class Meta:
        model = User
        fields = ("name", "email")
        labels = {
            "name": "Nom",
            "email": "Adresse e-mail",
        }

    def clean_email(self):
        """Normalise l’adresse e-mail et refuse les doublons sans distinction de casse."""
        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Cette adresse e-mail est déjà utilisée.")

        return email

    def save(self, commit=True):
        """Prépare le compte et renseigne les dates d’acceptation."""
        # Prépare l’utilisateur avec son mot de passe haché, sans l’enregistrer.
        user = super().save(commit=False)

        # Utilise un même horodatage pour les deux confirmations du formulaire.
        now = timezone.now()
        user.terms_accepted_at = now
        user.privacy_policy_accepted_at = now

        # Permet à la vue de différer l’enregistrement avec commit=False.
        if commit:
            user.save()

        return user
