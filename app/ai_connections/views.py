from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods

from projects.models import EditorialProject

from .forms import AIConnectionForm
from .models import AIConnection
from .services.network import AIConnectionError
from .services.ollama import check_ollama_connection


@never_cache
@login_required(login_url="accounts:account")
@require_http_methods(["GET", "HEAD", "POST"])
def configuration(request):
    """Affiche, enregistre et teste la configuration IA du compte connecté."""
    connection = AIConnection.objects.filter(
        user=request.user,
    ).first()

    form = AIConnectionForm(
        data=request.POST if request.method == "POST" else None,
        instance=connection,
    )

    if request.method == "POST" and form.is_valid():
        # Attribue la configuration au compte connecté, indépendamment
        # des éventuels identifiants ajoutés aux données du formulaire.
        connection = form.save(commit=False)
        connection.user = request.user
        connection.save()

        # Conserve la configuration même lorsque le service est indisponible.
        if connection.mode == AIConnection.Mode.OLLAMA:
            try:
                response_text = check_ollama_connection(
                    connection.base_url,
                    connection.model_name,
                )
            except AIConnectionError as error:
                messages.error(
                    request,
                    f"Configuration enregistrée, mais le test a échoué : {error}",
                )
            else:
                messages.success(
                    request,
                    "Configuration enregistrée. "
                    f"Le modèle a répondu au test : {response_text}",
                )
        else:
            messages.warning(
                request,
                "Configuration enregistrée. "
                "Le test du service Alinea n’est pas encore disponible.",
            )

        # Évite de relancer l’enregistrement et le test au rafraîchissement.
        return redirect("ai_connections:configuration")

    # Conserve les valeurs saisies et les erreurs après une soumission invalide.
    return render(
        request,
        "ai_connections/configuration.html",
        {
            "form": form,
            "projects": EditorialProject.objects.filter(
                owner=request.user,
            ).order_by("-created_at", "-pk"),
        },
    )
