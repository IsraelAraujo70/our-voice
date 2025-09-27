"""Main URL configuration for OUR Voice backend."""

from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/token/", obtain_auth_token, name="api-token"),
    path("api/", include("config.api_router")),
    path("healthz/", TemplateView.as_view(template_name="healthcheck.txt"), name="healthcheck"),
]
