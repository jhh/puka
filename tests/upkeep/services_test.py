from datetime import timedelta

import pytest

from puka.stuff.models import Inventory
from puka.upkeep.models import TaskItem
from puka.upkeep.services import (
    get_areas_tasks_schedules,
    get_tasks_schedules,
    get_upcoming_due_tasks,
)


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


@pytest.mark.django_db
def test_get_upcoming_due_tasks_is_ready(area, filter_item, start_date, location):
    # arrange - task that uses 1 consumable, 3 consumable in inventory
    task = area.tasks.first()
    TaskItem.objects.create(task=task, item=filter_item, quantity=1)
    inventory = Inventory.objects.create(item=filter_item, location=location, quantity=3)
    schedule = task.first_due_schedule()

    # act
    tasks = get_upcoming_due_tasks()
    assert len(tasks) == 9  # area fixture has 3 tasks with 3 schedules each
    assert tasks[0]["id"] == task.id
    assert tasks[0]["due_date"] == schedule.due_date

    # assert
    assert tasks[0]["is_ready"]

    # arrange
    inventory.quantity = 0
    inventory.save()

    # act
    tasks = get_upcoming_due_tasks()

    # assert
    assert not tasks[0]["is_ready"]
