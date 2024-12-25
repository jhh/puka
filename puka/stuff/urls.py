from __future__ import annotations

from django.urls import URLPattern, URLResolver, path

from puka.stuff.views import home_view

app_name = "stuff"
urlpatterns: list[URLPattern | URLResolver] = [
    path("", home_view, name="home"),
]
