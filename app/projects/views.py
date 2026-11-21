from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import EditorialProjectForm, ProjectReferenceSourceForm
from .models import EditorialProject, ProjectReferenceSource


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
        return redirect("projects:sources", pk=project.pk)

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


@login_required(login_url="accounts:account")
@require_http_methods(["POST"])
def project_delete(request, pk):
    """Supprime un projet appartenant à l’utilisateur connecté."""
    project = get_object_or_404(
        EditorialProject,
        pk=pk,
        owner=request.user,
    )

    project.delete()
    messages.success(request, "Le projet a été supprimé.")
    return redirect("dashboard:index")


@login_required(login_url="accounts:account")
@require_http_methods(["GET", "HEAD", "POST"])
def project_sources(request, pk):
    """Liste les sources du projet et traite l’ajout d’une référence."""
    project = get_object_or_404(
        EditorialProject,
        pk=pk,
        owner=request.user,
    )

    form = ProjectReferenceSourceForm(
        data=request.POST if request.method == "POST" else None,
    )

    if request.method == "POST" and form.is_valid():
        # Le projet est attribué côté serveur après contrôle des droits.
        source = form.save(commit=False)
        source.project = project
        source.save()

        messages.success(request, "La source de référence a été ajoutée.")
        return redirect("projects:sources", pk=project.pk)

    return render(
        request,
        "projects/project_sources.html",
        {
            "project": project,
            "sources": project.reference_sources.all(),
            "form": form,
            "projects": EditorialProject.objects.filter(
                owner=request.user,
            ).order_by("-created_at", "-pk"),
        },
    )


@login_required(login_url="accounts:account")
@require_http_methods(["GET", "HEAD", "POST"])
def project_source_edit(request, pk, source_pk):
    """Modifie une référence depuis la page des sources du projet."""
    project = get_object_or_404(
        EditorialProject,
        pk=pk,
        owner=request.user,
    )

    source = get_object_or_404(
        ProjectReferenceSource,
        pk=source_pk,
        project=project,
    )

    form = ProjectReferenceSourceForm(
        data=request.POST if request.method == "POST" else None,
        instance=source,
    )

    if request.method == "POST" and form.is_valid():
        form.save()

        messages.success(request, "La source de référence a été modifiée.")
        return redirect("projects:sources", pk=project.pk)

    return render(
        request,
        "projects/project_sources.html",
        {
            "project": project,
            "sources": project.reference_sources.all(),
            "form": form,
            "editing_source": source,
            "projects": EditorialProject.objects.filter(
                owner=request.user,
            ).order_by("-created_at", "-pk"),
        },
    )


@login_required(login_url="accounts:account")
@require_http_methods(["POST"])
def project_source_delete(request, pk, source_pk):
    """Supprime une source du projet après contrôle des droits."""
    project = get_object_or_404(
        EditorialProject,
        pk=pk,
        owner=request.user,
    )

    source = get_object_or_404(
        ProjectReferenceSource,
        pk=source_pk,
        project=project,
    )

    if request.POST.get("confirm_deletion") != "yes":
        messages.error(request, "Confirmez la suppression de la source.")
        return redirect("projects:sources", pk=project.pk)

    source.delete()

    messages.success(request, "La source de référence a été supprimée.")
    return redirect("projects:sources", pk=project.pk)
