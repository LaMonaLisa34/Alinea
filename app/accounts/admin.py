from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import BaseUserCreationForm, UserChangeForm

from .models import User


class EmailValidationMixin:
    """Normalise l’adresse e-mail et refuse les doublons sans distinction de casse."""

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        users = User.objects.filter(email__iexact=email)

        if self.instance.pk:
            users = users.exclude(pk=self.instance.pk)

        if users.exists():
            raise forms.ValidationError("Cette adresse e-mail est déjà utilisée.")

        return email


class AdminUserCreationForm(EmailValidationMixin, BaseUserCreationForm):
    """Crée un compte depuis l’administration avec validation du mot de passe."""

    class Meta:
        model = User
        fields = (
            "email",
            "name",
            "terms_accepted_at",
            "privacy_policy_accepted_at",
        )


class AdminUserChangeForm(EmailValidationMixin, UserChangeForm):
    """Modifie un compte sans éditer directement son mot de passe haché."""

    class Meta:
        model = User
        fields = "__all__"


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Configure la consultation et la gestion des comptes Alinea."""

    form = AdminUserChangeForm
    add_form = AdminUserCreationForm

    # Présentation de la liste des comptes.
    list_display = (
        "email",
        "name",
        "account_active",
        "is_staff",
        "is_superuser",
        "created_at",
    )
    list_filter = ("is_staff", "is_superuser", "groups")
    search_fields = ("email", "name")
    ordering = ("email",)
    list_per_page = 25
    date_hierarchy = "created_at"

    # Les dates automatiques et l’état calculé ne sont pas modifiables.
    readonly_fields = (
        "created_at",
        "updated_at",
        "last_login",
        "account_active",
    )

    # Organisation du formulaire de modification.
    fieldsets = (
        (
            "Identité",
            {
                "fields": ("email", "name", "password"),
            },
        ),
        (
            "Droits et permissions",
            {
                "fields": (
                    "role",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            "Conditions et confidentialité",
            {
                "fields": (
                    "terms_accepted_at",
                    "privacy_policy_accepted_at",
                ),
            },
        ),
        (
            "État et historique",
            {
                "fields": (
                    "account_active",
                    "deleted_at",
                    "created_at",
                    "updated_at",
                    "last_login",
                ),
            },
        ),
    )

    # Organisation du formulaire de création.
    add_fieldsets = (
        (
            "Identité",
            {
                "fields": ("email", "name", "password1", "password2"),
            },
        ),
        (
            "Conditions et confidentialité",
            {
                "fields": (
                    "terms_accepted_at",
                    "privacy_policy_accepted_at",
                ),
            },
        ),
    )

    filter_horizontal = ("groups", "user_permissions")

    @admin.display(boolean=True, description="Compte actif")
    def account_active(self, obj):
        """Affiche l’état du compte calculé depuis sa date de suppression."""
        return obj.is_active


admin.site.site_header = "Administration Alinea"
admin.site.site_title = "Alinea"
admin.site.index_title = "Gestion de l’application"
