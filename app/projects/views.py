from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import EditorialProjectForm
from .models import EditorialProject


@login_required(login_url="accounts:account")
@require_http_methods(["GET", "HEAD", "POST"])
def project_create(request):
    """Crée un projet éditorial appartenant à l’utilisateur connecté."""
    form = EditorialProjectForm(
        data=request.POST if request.method == "POST" else None,
    )

    if request.method == "POST" and form.is_valid():
        # Le propriétaire est défini côté serveur à partir de la session.
        project = form.save(commit=False)
        project.owner = request.user
        project.save()

        messages.success(request, "Votre projet éditorial a été créé.")
        return redirect("projects:detail", pk=project.pk)

    return render(
        request,
        "projects/project_create.html",
        {
            "form": form,
            "projects": EditorialProject.objects.filter(
                owner=request.user,
            ).order_by("-created_at", "-pk"),
        },
    )


@login_required(login_url="accounts:account")
@require_http_methods(["GET", "HEAD", "POST"])
def project_detail(request, pk):
    """Affiche et modifie un projet appartenant à l’utilisateur connecté."""
    # Restreint la consultation et la modification aux projets du propriétaire.
    project = get_object_or_404(
        EditorialProject,
        pk=pk,
        owner=request.user,
    )

    form = EditorialProjectForm(
        data=request.POST if request.method == "POST" else None,
        instance=project,
    )

    if request.method == "POST" and form.is_valid():
        form.save()

        messages.success(
            request,
            "Les modifications du projet ont été enregistrées.",
        )

        # Redirige vers le mode lecture et évite une nouvelle soumission.
        return redirect("projects:detail", pk=project.pk)

    return render(
        request,
        "projects/project_overview.html",
        {
            "form": form,
            "project": project,
            "projects": EditorialProject.objects.filter(
                owner=request.user,
            ).order_by("-created_at", "-pk"),
        },
    )
