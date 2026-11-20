from django.urls import path

from . import views

app_name = "projects"

urlpatterns = [
    path("nouveau/", views.project_create, name="create"),
    path("<int:pk>/", views.project_detail, name="detail"),
    path("<int:pk>/supprimer/", views.project_delete, name="delete"),
    path(
        "<int:pk>/sources/",
        views.project_sources,
        name="sources",
    ),
    path(
        "<int:pk>/sources/<int:source_pk>/modifier/",
        views.project_source_edit,
        name="source_edit",
    ),
    path(
        "<int:pk>/sources/<int:source_pk>/supprimer/",
        views.project_source_delete,
        name="source_delete",
    ),
]
