from __future__ import annotations

from django.conf import settings
from django.contrib import admin
from django.urls import URLPattern, URLResolver, include, path
from django.views.generic import TemplateView

from puka.core.views import view_404

urlpatterns: list[URLPattern | URLResolver] = [
    path("", TemplateView.as_view(template_name="overview.html"), name="home"),
    path("bookmarks/", include("puka.bookmarks.urls", namespace="bookmarks")),
    path("stuff/", include("puka.stuff.urls", namespace="stuff")),
    path("upkeep/", include("puka.upkeep.urls", namespace="upkeep")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("users/", include("puka.users.urls")),
    path("admin/", admin.site.urls),
    path("404/", view_404),
]


if "debug_toolbar" in settings.INSTALLED_APPS:  # pragma: no cover
    urlpatterns = [*urlpatterns, path("__debug__/", include("debug_toolbar.urls"))]

if "django_browser_reload" in settings.INSTALLED_APPS:  # pragma: no cover
    urlpatterns = [*urlpatterns, path("__reload__/", include("django_browser_reload.urls"))]
