from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.db import IntegrityError, transaction
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_http_methods

from .forms import RegistrationForm
from .models import User


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
