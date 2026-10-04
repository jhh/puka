from __future__ import annotations

from datetime import date, timedelta
from io import StringIO
from unittest.mock import patch

import pytest
from django.core.management import call_command
from django.core.paginator import Paginator
from django.db.models import QuerySet

from puka.upkeep.services import (
    get_areas_tasks_schedules,
    get_tasks_schedules,
)
from tests.factories import AreaFactory, ItemFactory, ScheduleFactory, TaskFactory, TaskItemFactory


@pytest.mark.django_db
def test_get_areas_tasks_schedules(area, start_date):
    a = get_areas_tasks_schedules()
    assert len(a) == 1
    row = a[0]
    assert row["name"] == area.name
    assert row["id"] == area.id
    assert row["task_count"] == 4


@pytest.mark.django_db
def test_get_areas_tasks_schedules_due_date(area, start_date):
    a = get_areas_tasks_schedules()
    row = a[0]
    assert row["due_date"] == start_date
    assert row["due_task_id"] == area.tasks.first().id

    # complete the first schedule of the first task
    s = area.tasks.first().schedules.first()
    s.completion_date = start_date
    s.save()

    # should get the second schedule of the first task
    a = get_areas_tasks_schedules()
    row = a[0]
    assert row["due_date"] == start_date + timedelta(days=1)
    assert row["due_task_id"] == area.tasks.first().id


@pytest.mark.django_db
def test_get_areas_tasks_schedules_none():
    a = get_areas_tasks_schedules()
    assert len(a) == 0


@pytest.mark.django_db
def test_get_tasks_schedules(area, start_date):
    t = get_tasks_schedules()
    assert len(t) == 4
    t = get_tasks_schedules(area.id)
    assert len(t) == 4
    # The service does not promise an ordering; compare the complete result set.
    assert {row["area_name"] for row in t} == {area.name}
    assert {row["id"] for row in t} == set(area.tasks.values_list("id", flat=True))


@pytest.mark.django_db
def test_get_tasks_schedules_none(area, start_date):
    t = get_tasks_schedules(99)
    assert len(t) == 0


@pytest.mark.django_db
def test_area_summary_empty_and_completed_schedules():
    empty = AreaFactory.create(name="Empty")
    completed = AreaFactory.create(name="Completed")
    task = TaskFactory.create(area=completed)
    ScheduleFactory.create(task=task, completion_date=date(2024, 1, 1))
    rows = {row["id"]: row for row in get_areas_tasks_schedules()}
    assert rows[empty.pk]["task_count"] == 0
    assert rows[completed.pk]["task_count"] == 1
    assert all(row["due_date"] is None and row["due_task_id"] is None for row in rows.values())


@pytest.mark.django_db
def test_area_summary_search_keeps_relevance_order():
    title_match = AreaFactory.create(name="Water", notes="")
    notes_match = AreaFactory.create(name="Other", notes="Water")
    AreaFactory.create(name="Unrelated", notes="")
    rows = list(get_areas_tasks_schedules("water"))
    assert [row["id"] for row in rows] == [title_match.pk, notes_match.pk]


@pytest.mark.django_db
def test_area_summary_is_lazy_and_paginated(django_assert_num_queries):
    areas = [AreaFactory.create(name=f"Area {index}") for index in range(15)]
    for area in areas:
        for index in range(2):
            task = TaskFactory.create(area=area)
            ScheduleFactory.create(task=task, due_date=date(2024, 1, index + 2))
            ScheduleFactory.create(
                task=task,
                due_date=date(2023, 1, 1),
                completion_date=date(2023, 1, 1),
            )
    with django_assert_num_queries(0):
        queryset = get_areas_tasks_schedules()
        assert isinstance(queryset, QuerySet)
        paginator = Paginator(queryset, 10)
    with django_assert_num_queries(2) as queries:
        rows = list(paginator.page(1))
    assert len(rows) == 10
    assert [row["id"] for row in rows] == [area.pk for area in areas[:10]]
    assert all(row["task_count"] == 2 and row["due_date"] == date(2024, 1, 2) for row in rows)
    assert "LIMIT 10" in queries.captured_queries[-1]["sql"]
    with django_assert_num_queries(1):
        assert len(list(paginator.page(2))) == 5


@pytest.mark.django_db
@pytest.mark.parametrize("size", [1, 3, 15])
def test_notification_stock_rendering_has_constant_queries(
    size,
    django_assert_num_queries,
    monkeypatch,
):
    monkeypatch.delenv("PUKA_TASK_WITHIN", raising=False)
    monkeypatch.delenv("PUKA_SUPPLIES_WITHIN", raising=False)
    area = AreaFactory.create()
    item = ItemFactory.create()
    tasks = [TaskFactory.create(area=area, name=f"Notify task {index}") for index in range(size)]
    for task in tasks:
        ScheduleFactory.create(task=task)
        TaskItemFactory.create(task=task, item=item, quantity=1)
    with (
        patch("puka.upkeep.management.commands.notify.send_mail") as send_mail,
        django_assert_num_queries(1),
    ):
        call_command("notify", stdout=StringIO())
    send_mail.assert_called_once()
    html = send_mail.call_args.kwargs["html_message"]
    assert html.count("out-of-stock") == size
    assert all(task.name in html for task in tasks)
