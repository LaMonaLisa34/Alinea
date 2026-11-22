from django.urls import path

from . import views

app_name = "content_models"

urlpatterns = [
    path("", views.template_list, name="list"),
    path(
        "<int:template_pk>/",
        views.template_editor,
        name="editor",
    ),
    path(
        "<int:template_pk>/blocs/ajouter/",
        views.block_create,
        name="block_create",
    ),
    path(
        "<int:template_pk>/blocs/<int:block_pk>/modifier/",
        views.block_update,
        name="block_update",
    ),
    path(
        "<int:template_pk>/blocs/<int:block_pk>/deplacer/",
        views.block_move,
        name="block_move",
    ),
    path(
        "<int:template_pk>/blocs/<int:block_pk>/supprimer/",
        views.block_delete,
        name="block_delete",
    ),
]
