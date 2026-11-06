from django.contrib.auth.views import LoginView
from django.urls import path, reverse_lazy
from django.contrib.auth.views import LogoutView

from . import views

app_name = "accounts"

urlpatterns = [
    path("compte/", views.account, name="account"),
    path(
        "connexion/",
        LoginView.as_view(
            template_name="accounts/account.html",
            next_page=reverse_lazy("dashboard:index"),
        ),
        name="login",
    ),
    path(
        "deconnexion/",
        LogoutView.as_view(
            next_page=reverse_lazy("home"),
        ),
        name="logout",
    ),
    path("profil/", views.profile, name="profile"),
    path(
        "profil/suppression/",
        views.delete_account,
        name="delete_account",
    ),
]
