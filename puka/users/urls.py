from __future__ import annotations

from django.urls import URLPattern, URLResolver, path

from .views import logout_view

urlpatterns: list[URLPattern | URLResolver] = [
    path("logout/", logout_view, name="logout"),
]
