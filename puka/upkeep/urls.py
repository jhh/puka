from __future__ import annotations

from django.urls import URLPattern, URLResolver, path

from puka.upkeep.views.area import AreaListView
from puka.upkeep.views.home import home_view

app_name = "upkeep"
urlpatterns: list[URLPattern | URLResolver] = [
    path("", home_view, name="home"),
    path("area/", AreaListView.as_view(), name="area-list"),
]
