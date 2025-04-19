from __future__ import annotations

from django.urls import URLPattern, URLResolver, path

from puka.upkeep.views.area import AreaCreateView, AreaDeleteView, AreaListView, AreaUpdateView
from puka.upkeep.views.home import HomeListView
from puka.upkeep.views.task import (
    TaskCreateView,
    TaskDeleteView,
    TaskDetailView,
    TaskListView,
    TaskUpdateView,
)

app_name = "upkeep"
urlpatterns: list[URLPattern | URLResolver] = [
    # Task
    path("", HomeListView.as_view(), name="home"),
    path("task/", TaskListView.as_view(), name="task-list"),
    path("task/<int:pk>/", TaskDetailView.as_view(), name="task-detail"),
    path("task/new/", TaskCreateView.as_view(), name="task-new"),
    path("task/<int:pk>/edit/", TaskUpdateView.as_view(), name="task-edit"),
    path("task/<int:pk>/delete/", TaskDeleteView.as_view(), name="task-delete"),
    # Area
    path("area/", AreaListView.as_view(), name="area-list"),
    path("area/new/", AreaCreateView.as_view(), name="area-new"),
    path("area/<int:pk>/edit/", AreaUpdateView.as_view(), name="area-edit"),
    path("area/<int:pk>/delete/", AreaDeleteView.as_view(), name="area-delete"),
]
