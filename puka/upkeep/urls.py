from __future__ import annotations

from django.urls import URLPattern, URLResolver, path

from puka.upkeep.views import home_view

app_name = "upkeep"
urlpatterns: list[URLPattern | URLResolver] = [
    path("", home_view, name="home"),
]
