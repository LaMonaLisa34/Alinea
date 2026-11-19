from django.urls import path

from . import views

app_name = "projects"

urlpatterns = [
    path("nouveau/", views.project_create, name="create"),
    path("<int:pk>/", views.project_detail, name="detail"),
    path("<int:pk>/supprimer/", views.project_delete, name="delete"),
]
