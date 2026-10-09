from __future__ import annotations

from datetime import date

import pytest
from django.urls import reverse
from pytest_django.asserts import assertContains

from puka.upkeep.models import Task
from tests.factories import AreaFactory, ScheduleFactory, TaskFactory
from tests.utils import HTMX, assert_hx_location, assert_redirect

pytestmark = pytest.mark.django_db


@pytest.fixture
def task():
    return TaskFactory.create()


def test_create_task(admin_client):
    area = AreaFactory.create()
    data = {
        "area": area.pk,
        "name": "Change filter",
        "interval": 3,
        "frequency": "months",
        "notes": "",
    }
    response = admin_client.post(reverse("upkeep:task-new"), data, headers=HTMX)

    task = Task.objects.get()
    assert_redirect(response, reverse("upkeep:task-detail", args=[task.pk]))
    assert task.area == area
    assert task.name == "Change filter"
    assert task.interval == 3


def test_create_task_initial_area(admin_client):
    area = AreaFactory.create()
    url = reverse("upkeep:task-new") + f"?area={area.pk}"
    response = admin_client.get(url, headers=HTMX)
    assert response.context["form"].initial["area"] == str(area.pk)


def test_create_task_invalid(admin_client):
    data = {"name": "No area", "frequency": "fortnights"}
    response = admin_client.post(reverse("upkeep:task-new"), data, headers=HTMX)

    assert response.status_code == 200
    assertContains(response, "This field is required.")
    assertContains(response, "Select a valid choice.")
    assert not Task.objects.exists()


def test_update_task(admin_client, task):
    data = {
        "area": task.area.pk,
        "name": "Renamed",
        "interval": "",
        "frequency": "weeks",
        "notes": "",
    }
    url = reverse("upkeep:task-edit", args=[task.pk])
    response = admin_client.post(url, data, headers=HTMX)

    assert_redirect(response, reverse("upkeep:task-detail", args=[task.pk]))
    task.refresh_from_db()
    assert task.name == "Renamed"
    assert task.interval is None
    assert task.frequency == "weeks"


def test_delete_task(admin_client, task):
    response = admin_client.post(reverse("upkeep:task-delete", args=[task.pk]), headers=HTMX)

    assert_hx_location(response, reverse("upkeep:task-list"))
    assert not Task.objects.exists()


def test_task_list_due_date_order(admin_client):
    sooner = TaskFactory.create(name="Sooner")
    later = TaskFactory.create(name="Later")
    TaskFactory.create(name="Undated")
    ScheduleFactory.create(task=sooner, due_date=date(2024, 1, 1))
    ScheduleFactory.create(task=later, due_date=date(2024, 6, 1))

    response = admin_client.get(reverse("upkeep:task-list"))

    assert [task.name for task in response.context["tasks"]] == ["Sooner", "Later", "Undated"]
