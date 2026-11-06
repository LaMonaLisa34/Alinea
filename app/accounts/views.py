from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.db import IntegrityError, transaction
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib.auth import update_session_auth_hash
from .forms import ProfileForm, RegistrationForm, DeleteAccountForm
from .models import User
from django.shortcuts import get_object_or_404
from django.db.models import ProtectedError, RestrictedError


@sensitive_post_parameters()
@require_http_methods(["GET", "HEAD", "POST"])
def account(request):
    """Affiche et traite les formulaires de connexion et d’inscription."""

    # Les préfixes distinguent les champs des deux formulaires.
    login_form = AuthenticationForm(request, prefix="login")
    registration_form = RegistrationForm(prefix="register")

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "login":
            login_form = AuthenticationForm(request, data=request.POST, prefix="login")

            # Ouvre une session après validation des identifiants.
            if login_form.is_valid():
                login(request, login_form.get_user())
                return redirect("home")

        elif action == "register":
            registration_form = RegistrationForm(request.POST, prefix="register")

            # Valide les champs et les règles de mot de passe avant sauvegarde.
            if registration_form.is_valid():
                try:
                    # Annule les écritures du bloc en cas d’échec.
                    with transaction.atomic():
                        registration_form.save()

                except IntegrityError:
                    # Traite un doublon créé entre la validation et la sauvegarde.
                    # Les autres erreurs d’intégrité sont propagées.
                    email = registration_form.cleaned_data["email"]
                    if not User.objects.filter(email__iexact=email).exists():
                        raise

                    registration_form.add_error(
                        "email",
                        "Cette adresse e-mail est déjà utilisée.",
                    )

                else:
                    messages.success(
                        request,
                        "Compte créé. Vous pouvez vous connecter.",
                    )

                    # Redirige après sauvegarde pour éviter une nouvelle
                    # soumission du formulaire au rafraîchissement.
                    return redirect(f"{reverse('accounts:account')}#connexion")

    # Après soumission, conserve le formulaire concerné et ses erreurs.
    # Lors d’un affichage initial, le paramètre « mode » choisit le formulaire.
    mode = (
        request.POST.get("action")
        if request.method == "POST"
        else request.GET.get("mode")
    )
    is_registration = mode == "register"

    return render(
        request,
        "accounts/account.html",
        {
            "is_registration": is_registration,
            "form": registration_form if is_registration else login_form,
        },
    )


@sensitive_post_parameters()
@never_cache
@login_required(login_url="accounts:account")
@require_http_methods(["GET", "HEAD", "POST"])
def profile(request):
    """Enregistre les informations et le mot de passe depuis un formulaire unique."""
    form = ProfileForm(
        data=request.POST if request.method == "POST" else None,
        instance=request.user,
    )

    if request.method == "POST" and form.is_valid():
        password_changed = bool(form.cleaned_data.get("new_password1"))
        profile_changed = any(field in form.changed_data for field in ("name", "email"))

        if not profile_changed and not password_changed:
            messages.info(request, "Aucune modification à enregistrer.")
            return redirect("accounts:profile")

        try:
            with transaction.atomic():
                user = form.save(commit=False)
                fields = ["name", "email", "updated_at"]

                if password_changed:
                    fields.append("password")

                # Enregistre tous les changements ensemble.
                user.save(update_fields=fields)

        except IntegrityError:
            email = form.cleaned_data["email"]
            duplicate_exists = (
                User.objects.filter(email__iexact=email)
                .exclude(pk=request.user.pk)
                .exists()
            )
            if not duplicate_exists:
                raise

            form.add_error("email", "Cette adresse e-mail est déjà utilisée.")

        else:
            if password_changed:
                # Maintient la session courante avec le nouveau mot de passe.
                update_session_auth_hash(request, user)

            messages.success(request, "Les modifications ont été enregistrées.")
            return redirect("accounts:profile")

    return render(
        request,
        "accounts/profile.html",
        {"form": form},
    )


@sensitive_post_parameters()
@never_cache
@login_required(login_url="accounts:account")
@require_http_methods(["GET", "HEAD", "POST"])
def delete_account(request):
    """Supprime le compte connecté après vérification et confirmation."""
    form = DeleteAccountForm(user=request.user)

    if request.method == "POST":
        try:
            with transaction.atomic():
                # Verrouille le compte pendant la validation et la suppression.
                user = get_object_or_404(
                    User.objects.select_for_update(),
                    pk=request.user.pk,
                )
                form = DeleteAccountForm(request.POST, user=user)

                if form.is_valid():
                    user.delete()
                else:
                    return render(
                        request,
                        "accounts/delete_account.html",
                        {"form": form},
                    )

        except (ProtectedError, RestrictedError):
            # Annule la suppression lorsqu’une relation la bloque.
            form.add_error(
                None,
                "La suppression est impossible car des données liées "
                "à votre compte empêchent cette opération.",
            )

        else:
            # Ferme la session uniquement après la suppression effective.
            logout(request)
            messages.success(request, "Votre compte a été supprimé.")
            return redirect("home")

    return render(
        request,
        "accounts/delete_account.html",
        {"form": form},
    )
