import logging
from itertools import chain
from operator import attrgetter
from typing import Any

from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import CharField, Count, Sum, Value

from puka.stuff.models import Item
from puka.upkeep.models import Area, Schedule, Task, TaskItem

logger = logging.getLogger(__name__)


def item_quantity_needed(item: Item) -> int:
    result = TaskItem.objects.filter(item=item).aggregate(total=Sum("quantity"))
    return result["total"] or 0


def get_areas_tasks_schedules() -> list[dict[str, Any]]:
    """Return all areas with count of tasks and task with the soonest due_date and id."""
    area_queryset = (
        Area.objects.prefetch_related("tasks__schedules").annotate(task_count=Count("tasks")).all()
    )

    areas = []
    for area in area_queryset:
        row = {"id": area.id, "name": area.name, "task_count": area.task_count}

        schedules: list[Schedule] = []
        for task in area.tasks.all():
            schedules += task.schedules.filter(completion_date__isnull=True).all()

        if schedules:
            first = min(schedules, key=attrgetter("due_date"))
            row |= {"due_date": first.due_date, "due_task_id": first.task_id}

        areas.append(row)
    return areas


def get_tasks_schedules(area=None) -> list[dict[str, Any]]:
    """Return all tasks, optionally filtered by area, with area name and next due_date."""
    tasks_queryset = Task.objects.select_related("area").prefetch_related("schedules")

    if area:
        tasks_queryset = tasks_queryset.filter(area=area)

    tasks = []
    for task in tasks_queryset:
        row = {"id": task.id, "area_name": task.area.name, "name": task.name}

        schedules = task.schedules.filter(completion_date__isnull=True).all()
        if schedules:
            first = min(schedules, key=attrgetter("due_date"))
            row |= {"due_date": first.due_date}

        tasks.append(row)
    return tasks


def get_upcoming_due_tasks(within_days=14) -> list[dict[str, Any]]:
    """Return all upcoming tasks due with within_days with due date."""
    tasks_queryset = Task.objects.get_upcoming_due_tasks(within_days=within_days).select_related()

    tasks = []
    for task in tasks_queryset:
        task_consumables = TaskItem.objects.filter(task=task).all()
        is_ready = True
        for tc in task_consumables:
            if tc.quantity > tc.item.quantity():
                is_ready = False

        tasks.append(
            {
                "id": task.id,
                "name": task.name,
                "area": task.area.name,
                "due_date": task.first_due_schedule().due_date,
                "is_ready": is_ready,
            },
        )

    return tasks


def search_areas_and_tasks(query_text, limit=None):
    """
    Perform a full-text search across both Area and Task models.

    Args:
        query_text (str): The text to search for
        limit (int, optional): Maximum number of results to return per model

    Returns:
        list: Combined search results from both models, sorted by relevance

    """
    search_query = SearchQuery(query_text)

    # Search Areas
    area_results = (
        Area.objects.annotate(
            search_vector=SearchVector("name", weight="A") + SearchVector("notes", weight="B"),
            rank=SearchRank("search_vector", search_query),
            model_name=Value("area", output_field=CharField()),
        )
        .filter(search_vector=search_query)
        .order_by("-rank")
    )

    # Search Tasks
    task_results = (
        Task.objects.annotate(
            search_vector=SearchVector("name", weight="A") + SearchVector("notes", weight="B"),
            rank=SearchRank("search_vector", search_query),
            model_name=Value("task", output_field=CharField()),
        )
        .filter(search_vector=search_query)
        .order_by("-rank")
    )

    # Apply limit to each query if specified
    if limit:
        area_results = area_results[:limit]
        task_results = task_results[:limit]

    # Combine results and sort by rank
    return sorted(chain(area_results, task_results), key=attrgetter("rank"), reverse=True)
