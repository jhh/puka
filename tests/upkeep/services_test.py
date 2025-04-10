from datetime import timedelta

import pytest

from puka.upkeep.services import get_areas_tasks_schedules, get_tasks_schedules


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
    row = t[0]
    assert row["area_name"] == area.name
    assert row["id"] == area.tasks.first().id


@pytest.mark.django_db
def test_get_tasks_schedules_none(area, start_date):
    t = get_tasks_schedules(99)
    assert len(t) == 0
