from django import forms
from django.contrib.auth.forms import BaseUserCreationForm
from django.utils import timezone
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

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


class ProfileForm(forms.ModelForm):
    """Modifie le profil et, facultativement, le mot de passe."""

    current_password = forms.CharField(
        label="Mot de passe actuel",
        strip=False,
        help_text="Confirmez vos modifications avec votre mot de passe actuel.",
        widget=forms.PasswordInput(
            attrs={"autocomplete": "current-password"},
        ),
    )
    new_password1 = forms.CharField(
        label="Nouveau mot de passe",
        required=False,
        strip=False,
        help_text="Laissez vide pour conserver votre mot de passe.",
        widget=forms.PasswordInput(
            attrs={"autocomplete": "new-password"},
        ),
    )
    new_password2 = forms.CharField(
        label="Confirmer le nouveau mot de passe",
        required=False,
        strip=False,
        widget=forms.PasswordInput(
            attrs={"autocomplete": "new-password"},
        ),
    )

    class Meta:
        model = User
        fields = ("name", "email")
        labels = {
            "name": "Nom",
            "email": "Adresse e-mail",
        }
        widgets = {
            "name": forms.TextInput(attrs={"autocomplete": "name"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
        }

    def clean_email(self):
        """Normalise l’adresse et refuse celle d’un autre compte."""
        email = self.cleaned_data["email"].strip().lower()
        users = User.objects.filter(email__iexact=email).exclude(
            pk=self.instance.pk,
        )

        if users.exists():
            raise forms.ValidationError("Cette adresse e-mail est déjà utilisée.")

        return email

    def clean_current_password(self):
        """Confirme l’identité avant toute modification."""
        password = self.cleaned_data["current_password"]

        if not self.instance.check_password(password):
            raise forms.ValidationError("Le mot de passe actuel est incorrect.")

        return password

    def clean(self):
        """Exige une confirmation identique lorsqu’un changement est demandé."""
        cleaned_data = super().clean()
        password1 = cleaned_data.get("new_password1")
        password2 = cleaned_data.get("new_password2")

        if password1 and not password2:
            self.add_error(
                "new_password2",
                "Confirmez votre nouveau mot de passe.",
            )
        elif password2 and not password1:
            self.add_error(
                "new_password1",
                "Saisissez votre nouveau mot de passe.",
            )
        elif password1 and password1 != password2:
            self.add_error(
                "new_password2",
                "Les deux mots de passe ne correspondent pas.",
            )

        return cleaned_data

    def _post_clean(self):
        """Valide le nouveau mot de passe avec les informations du profil modifiées."""
        super()._post_clean()

        password = self.cleaned_data.get("new_password1")

        if password and "new_password2" not in self.errors:
            try:
                validate_password(password, user=self.instance)
            except ValidationError as error:
                self.add_error("new_password1", error)

    def save(self, commit=True):
        """Prépare le profil et hache le nouveau mot de passe s’il est renseigné."""
        user = super().save(commit=False)
        password = self.cleaned_data.get("new_password1")

        if password:
            user.set_password(password)

        if commit:
            user.save()

        return user


class DeleteAccountForm(forms.Form):
    """Confirme l’identité et la demande explicite de suppression du compte."""

    current_password = forms.CharField(
        label="Mot de passe actuel",
        strip=False,
        widget=forms.PasswordInput(
            attrs={"autocomplete": "current-password"},
        ),
        error_messages={
            "required": "Saisissez votre mot de passe actuel.",
        },
    )
    confirm_deletion = forms.BooleanField(
        label="Je confirme la suppression définitive de mon compte.",
        error_messages={
            "required": "Confirmez la suppression pour continuer.",
        },
    )

    def __init__(self, *args, user, **kwargs):
        """Associe la confirmation au compte fourni par la vue."""
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_current_password(self):
        """Contrôle le mot de passe du compte concerné."""
        password = self.cleaned_data["current_password"]

        if not self.user.check_password(password):
            raise forms.ValidationError("Le mot de passe actuel est incorrect.")

        return password
