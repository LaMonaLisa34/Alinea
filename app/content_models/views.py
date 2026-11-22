from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.db.models import Max

from projects.models import EditorialProject

from .forms import ContentBlockForm, ContentTemplateForm
from .models import ContentTemplate, ContentBlock


@login_required(login_url="accounts:account")
@require_http_methods(["GET", "HEAD", "POST"])
def template_list(request, project_pk):
    """Affiche les modèles du projet et enregistre les nouveaux modèles."""
    project = get_object_or_404(
        EditorialProject,
        pk=project_pk,
        owner=request.user,
    )
    form = ContentTemplateForm(
        data=request.POST if request.method == "POST" else None,
    )

    if request.method == "POST" and form.is_valid():
        # L’association au projet est définie côté serveur après vérification du propriétaire.
        content_template = form.save(commit=False)
        content_template.project = project
        content_template.save()
        messages.success(request, "Le modèle de contenu a été créé.")
        return redirect(
            "content_models:editor",
            project_pk=project.pk,
            template_pk=content_template.pk,
        )

    return render(
        request,
        "content_models/template_list.html",
        {
            "project": project,
            "templates": project.content_templates.all(),
            "form": form,
            "projects": EditorialProject.objects.filter(
                owner=request.user,
            ).order_by("-created_at", "-pk"),
        },
    )


@login_required(login_url="accounts:account")
@require_http_methods(["GET", "HEAD", "POST"])
def template_editor(request, project_pk, template_pk):
    """Affiche l’éditeur de blocs et traite la modification des métadonnées du modèle."""
    project = get_object_or_404(
        EditorialProject,
        pk=project_pk,
        owner=request.user,
    )
    # Le modèle doit appartenir au projet dont l’utilisateur est propriétaire.
    content_template = get_object_or_404(
        ContentTemplate,
        pk=template_pk,
        project=project,
    )
    form = ContentTemplateForm(
        data=request.POST if request.method == "POST" else None,
        instance=content_template,
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(
            request,
            "Les informations du modèle ont été enregistrées.",
        )
        return redirect(
            "content_models:editor",
            project_pk=project.pk,
            template_pk=content_template.pk,
        )
    blocks = list(
        content_template.blocks.prefetch_related("parameters"),
    )
    # Un préfixe propre à chaque bloc évite les collisions de noms et d’identifiants HTML.
    block_forms = [
        ContentBlockForm(
            instance=block,
            prefix=f"block-{block.pk}",
        )
        for block in blocks
    ]

    return render(
        request,
        "content_models/template_editor.html",
        {
            "project": project,
            "content_template": content_template,
            "form": form,
            "block_forms": block_forms,
            "block_types": ContentBlock.BlockType.choices,
            "templates": project.content_templates.all(),
            "projects": EditorialProject.objects.filter(
                owner=request.user,
            ).order_by("-created_at", "-pk"),
        },
    )


@login_required(login_url="accounts:account")
@require_http_methods(["POST"])
def block_create(request, project_pk, template_pk):
    """Ajoute un bloc du type demandé à la fin du modèle autorisé."""
    try:
        block_type = ContentBlock.BlockType(
            request.POST.get("block_type"),
        )
    except ValueError:
        messages.error(request, "Le type de bloc demandé est invalide.")
        # Vérifier l’accès au modèle également lorsque le type de bloc est invalide.
        get_object_or_404(
            ContentTemplate,
            pk=template_pk,
            project_id=project_pk,
            project__owner=request.user,
        )
        return redirect(
            "content_models:editor",
            project_pk=project_pk,
            template_pk=template_pk,
        )

    with transaction.atomic():
        # Le verrou sur le modèle sérialise les ajouts concurrents avant le calcul de la position.
        content_template = get_object_or_404(
            ContentTemplate.objects.select_for_update(),
            pk=template_pk,
            project_id=project_pk,
            project__owner=request.user,
        )
        last_position = content_template.blocks.aggregate(
            last=Max("position"),
        )["last"]
        position = 0 if last_position is None else last_position + 1
        ContentBlock.objects.create(
            content_template=content_template,
            name=f"Bloc {block_type.label.lower()}",
            block_type=block_type.value,
            instruction="",
            position=position,
        )
    messages.success(request, "Le bloc a été ajouté au modèle.")
    return redirect(
        "content_models:editor",
        project_pk=project_pk,
        template_pk=template_pk,
    )


@login_required(login_url="accounts:account")
@require_http_methods(["POST"])
def block_update(request, project_pk, template_pk, block_pk):
    """Enregistre un bloc valide ou affiche ses erreurs dans l’éditeur."""
    project = get_object_or_404(
        EditorialProject,
        pk=project_pk,
        owner=request.user,
    )
    content_template = get_object_or_404(
        ContentTemplate,
        pk=template_pk,
        project=project,
    )
    block = get_object_or_404(
        ContentBlock,
        pk=block_pk,
        content_template=content_template,
    )
    block_form = ContentBlockForm(
        data=request.POST,
        instance=block,
        prefix=f"block-{block.pk}",
    )

    if block_form.is_valid():
        block_form.save()
        messages.success(
            request,
            "Le bloc a été modifié.",
        )
        return redirect(
            "content_models:editor",
            project_pk=project.pk,
            template_pk=content_template.pk,
        )
    # Réutiliser le formulaire soumis pour préserver les valeurs saisies et les erreurs de validation.
    blocks = list(
        content_template.blocks.prefetch_related("parameters"),
    )
    block_forms = [
        block_form
        if item.pk == block.pk
        else ContentBlockForm(
            instance=item,
            prefix=f"block-{item.pk}",
        )
        for item in blocks
    ]

    return render(
        request,
        "content_models/template_editor.html",
        {
            "project": project,
            "content_template": content_template,
            "form": ContentTemplateForm(instance=content_template),
            "block_forms": block_forms,
            "block_types": ContentBlock.BlockType.choices,
            "projects": EditorialProject.objects.filter(
                owner=request.user,
            ).order_by("-created_at", "-pk"),
        },
    )


@login_required(login_url="accounts:account")
@require_http_methods(["POST"])
def block_move(request, project_pk, template_pk, block_pk):
    """Déplace un bloc d’une position vers le haut ou vers le bas dans son modèle."""

    with transaction.atomic():
        content_template = get_object_or_404(
            ContentTemplate.objects.select_for_update(),
            pk=template_pk,
            project_id=project_pk,
            project__owner=request.user,
        )
        block = get_object_or_404(
            ContentBlock,
            pk=block_pk,
            content_template=content_template,
        )
        direction = request.POST.get("direction")
        if direction not in ("up", "down"):
            messages.error(request, "Le déplacement demandé est invalide.")
        else:
            blocks = list(
                content_template.blocks.order_by("position", "pk"),
            )
            index = next(
                index for index, item in enumerate(blocks) if item.pk == block.pk
            )
            target = index + (-1 if direction == "up" else 1)
            if 0 <= target < len(blocks):
                blocks[index], blocks[target] = blocks[target], blocks[index]
                # Réindexer les blocs à partir de zéro pour conserver des positions contiguës.
                for position, item in enumerate(blocks):
                    item.position = position
                ContentBlock.objects.bulk_update(blocks, ["position"])
    return redirect(
        "content_models:editor",
        project_pk=project_pk,
        template_pk=template_pk,
    )


@login_required(login_url="accounts:account")
@require_http_methods(["POST"])
def block_delete(request, project_pk, template_pk, block_pk):
    """Supprime un bloc autorisé et réindexe les blocs restants."""

    with transaction.atomic():
        content_template = get_object_or_404(
            ContentTemplate.objects.select_for_update(),
            pk=template_pk,
            project_id=project_pk,
            project__owner=request.user,
        )
        block = get_object_or_404(
            ContentBlock,
            pk=block_pk,
            content_template=content_template,
        )
        block.delete()
        # Réindexer les blocs restants pour supprimer les écarts de position.
        blocks = list(
            content_template.blocks.order_by("position", "pk"),
        )
        for position, item in enumerate(blocks):
            item.position = position
        if blocks:
            ContentBlock.objects.bulk_update(blocks, ["position"])
    messages.success(request, "Le bloc a été supprimé.")
    return redirect(
        "content_models:editor",
        project_pk=project_pk,
        template_pk=template_pk,
    )
