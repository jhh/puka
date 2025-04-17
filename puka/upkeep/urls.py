from __future__ import annotations

from django.urls import URLPattern, URLResolver, path

from puka.upkeep.views.area import AreaListView
from puka.upkeep.views.home import HomeListView
from puka.upkeep.views.task import TaskDetailView

app_name = "upkeep"
urlpatterns: list[URLPattern | URLResolver] = [
    path("", HomeListView.as_view(), name="home"),
    path("task/<int:pk>/", TaskDetailView.as_view(), name="task-detail"),
    path("area/", AreaListView.as_view(), name="area-list"),
]
