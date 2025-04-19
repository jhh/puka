from __future__ import annotations

from django.urls import URLPattern, URLResolver, path

from puka.upkeep.views.area import AreaCreateView, AreaDeleteView, AreaListView, AreaUpdateView
from puka.upkeep.views.home import HomeListView
from puka.upkeep.views.item import (
    TaskItemCreateView,
    TaskItemDeleteView,
    TaskItemUpdateView,
)
from puka.upkeep.views.schedule import (
    ScheduleCreateView,
    ScheduleDeleteView,
    ScheduleToggleView,
    ScheduleUpdateView,
)
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
    # Schedule
    path("task/<int:pk>/schedule/new/", ScheduleCreateView.as_view(), name="schedule-new"),
    path("schedule/<int:pk>/edit/", ScheduleUpdateView.as_view(), name="schedule-edit"),
    path("schedule/<int:pk>/delete/", ScheduleDeleteView.as_view(), name="schedule-delete"),
    path("schedule/<int:pk>/toggle/", ScheduleToggleView.as_view(), name="schedule-toggle"),
    # TaskItem
    path("task/<int:pk>/item/new/", TaskItemCreateView.as_view(), name="task-item-new"),
    path("item/<int:pk>/edit/", TaskItemUpdateView.as_view(), name="task-item-edit"),
    path("item/<int:pk>/delete/", TaskItemDeleteView.as_view(), name="task-item-delete"),
]
