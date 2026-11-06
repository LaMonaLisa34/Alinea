from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.http import require_safe

from projects.models import EditorialProject


@login_required(login_url="accounts:account")
@require_safe
def dashboard(request):
    """Présente l’espace de travail de l’utilisateur connecté."""
    projects = EditorialProject.objects.filter(
        owner=request.user,
    ).order_by("-created_at", "-pk")

    return render(
        request,
        "dashboard/dashboard.html",
        {"projects": projects},
    )
