from django.contrib import admin
from django.shortcuts import render
from django.urls import path
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET", "HEAD"])
def home(request):
    return render(request, "home.html")


urlpatterns = [
    path("", home, name="home"),
    path("admin/", admin.site.urls),
]
