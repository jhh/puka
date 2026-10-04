import datetime
from datetime import timedelta

import pytest
from django.db import IntegrityError

from puka.upkeep.models import Area, Schedule, Task, TaskItem
from puka.upkeep.services import item_quantity_needed
from tests.factories import (
    InventoryFactory,
    ItemFactory,
    LocationFactory,
    TaskFactory,
    TaskItemFactory,
)


@pytest.mark.django_db
def test_area(area):
    areas = Area.objects.all()
    assert len(Area.objects.all()) == 1
    assert areas[0].tasks.count() == 4
    assert areas[0].name == area.name


@pytest.mark.django_db
def test_area_first_due_no_tasks():
    area = Area.objects.create(name="Test Area")
    assert area.first_due_schedule() is None


@pytest.mark.django_db
def test_area_first_due_no_schedules():
    area = Area.objects.create(name="Test Area")
    Task.objects.create(name="Test Task", area=area)
    assert area.tasks.count() == 1
    task = area.tasks.first()
    assert task
    assert task.schedules.count() == 0
    assert area.first_due_schedule() is None


@pytest.mark.django_db
def test_first_due_schedule(area, start_date):
    assert area.first_due_schedule().due_date == start_date


@pytest.mark.django_db
def test_first_due_equality(area):
    first_due_schedule = area.first_due_schedule()
    task: Task = area.tasks.first()
    assert first_due_schedule == task.first_due_schedule()


def test_task_is_recurring():
    task = Task(name="test", interval=None)
    assert not task.is_recurring()


# https://www.timeanddate.com/date/dateadded.html
@pytest.mark.parametrize(
    ("interval", "frequency", "expected_delta"),
    [
        (1, "days", timedelta(days=1)),
        (2, "weeks", timedelta(days=14)),
        (4, "weeks", timedelta(days=28)),
        (1, "months", timedelta(days=31)),
        (2, "months", timedelta(days=60)),  # 2024 is leap year
    ],
)
def test_task_next_date(interval, frequency, expected_delta):
    task = Task(name="test", interval=interval, frequency=frequency)
    start_date = datetime.datetime(year=2024, month=1, day=1, tzinfo=datetime.UTC)
    delta: datetime.timedelta = task.next_date(start_date) - start_date
    assert delta == expected_delta


def test_task_next_date_today():
    task = Task(name="test", interval=1, frequency="days")
    next_date = task.next_date()
    expected_next_date = datetime.datetime.now(datetime.UTC) + timedelta(days=1)
    assert next_date.year == expected_next_date.year
    assert next_date.month == expected_next_date.month
    assert next_date.day == expected_next_date.day


def test_task_not_recurring():
    task = Task(name="test", frequency="days")
    start_date = datetime.datetime(year=2024, month=1, day=1, tzinfo=datetime.UTC)
    assert task.next_date(start_date) == start_date


def test_task_bad_frequency():
    task = Task(name="test", interval=1, frequency="bad")
    with pytest.raises(ValueError, match="Invalid frequency: bad"):
        task.next_date()


@pytest.mark.django_db
def test_task_manager():
    a = Area.objects.create(name="Test Area")
    t = Task.objects.create(area=a, name="test 1", interval=1, frequency="days")

    # Replace datetime.date.today() with datetime.datetime.now(datetime.UTC).date()
    today = datetime.datetime.now(datetime.UTC).date()

    s = Schedule.objects.create(task=t, due_date=today)
    tasks = Task.objects.get_upcoming_due_tasks(within_days=1)
    assert len(tasks) == 1

    s.completion_date = today
    s.save()
    tasks = Task.objects.get_upcoming_due_tasks(within_days=1)
    assert len(tasks) == 0

    Schedule.objects.create(task=t, due_date=today)
    s = Schedule.objects.create(task=t, due_date=today + timedelta(days=2))
    tasks = Task.objects.get_upcoming_due_tasks(within_days=1)
    assert len(tasks) == 1

    t = Task.objects.create(area=a, name="test 2", interval=1, frequency="days")
    Schedule.objects.create(task=t, due_date=today + timedelta(days=2))
    tasks = Task.objects.get_upcoming_due_tasks(within_days=2)
    assert len(tasks) == 3

    s.completion_date = today
    s.save()
    tasks = Task.objects.get_upcoming_due_tasks(within_days=2)
    assert len(tasks) == 2


@pytest.mark.django_db
def test_task_consumable_unique(area, filter_item):
    tasks = Task.objects.all()
    TaskItem.objects.create(task=tasks[0], item=filter_item, quantity=1)
    with pytest.raises(IntegrityError):
        TaskItem.objects.create(task=tasks[0], item=filter_item, quantity=1)


@pytest.mark.django_db
def test_task_consumable_needed(area, salt_item):
    tasks = Task.objects.all()
    TaskItem.objects.create(task=tasks[0], item=salt_item, quantity=1)
    assert item_quantity_needed(salt_item) == 1
    TaskItem.objects.create(task=tasks[1], item=salt_item, quantity=2)
    assert item_quantity_needed(salt_item) == 3
    TaskItem.objects.create(task=tasks[2], item=salt_item, quantity=3)
    assert item_quantity_needed(salt_item) == 6


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("quantities", "required", "expected"),
    [([], 1, False), ([], 0, True), ([0], 1, False), ([2, 3], 5, True), ([2, 3], 6, False)],
)
def test_task_stock_status(quantities, required, expected, django_assert_num_queries):
    task = TaskFactory.create()
    item = ItemFactory.create()
    TaskItemFactory.create(task=task, item=item, quantity=required)
    for index, quantity in enumerate(quantities):
        location = LocationFactory.create(code=f"A01-{index + 1:02}")
        InventoryFactory.create(item=item, location=location, quantity=quantity)

    with django_assert_num_queries(1):
        assert task.are_consumables_stocked() is expected
    prepared = Task.objects.with_stock_status().get(pk=task.pk)
    with django_assert_num_queries(0):
        assert prepared.are_consumables_stocked() is expected


@pytest.mark.django_db
def test_task_stock_status_without_consumables(django_assert_num_queries):
    task = TaskFactory.create()
    with django_assert_num_queries(1):
        assert task.are_consumables_stocked()
    prepared = Task.objects.with_stock_status().get(pk=task.pk)
    with django_assert_num_queries(0):
        assert prepared.are_consumables_stocked()


@pytest.mark.django_db
def test_task_stock_status_shared_items_and_missing_consumable():
    first = TaskFactory.create(name="First task")
    second = TaskFactory.create(name="Second task", area=first.area)
    shared = ItemFactory.create(name="Shared supply")
    missing = ItemFactory.create(name="Missing supply")
    InventoryFactory.create(item=shared, quantity=5)
    TaskItemFactory.create(task=first, item=shared, quantity=5)
    TaskItemFactory.create(task=second, item=shared, quantity=5)
    # Each task is checked independently, not against the combined requirement.
    statuses = {
        task.pk: task.are_consumables_stocked() for task in Task.objects.with_stock_status()
    }
    assert statuses == {first.pk: True, second.pk: True}
    TaskItemFactory.create(task=second, item=missing, quantity=1)
    statuses = {
        task.pk: task.are_consumables_stocked() for task in Task.objects.with_stock_status()
    }
    assert statuses == {first.pk: True, second.pk: False}
