from __future__ import annotations

import datetime

import pytest
from django.urls import reverse
from pytest_django.asserts import assertContains

from puka.upkeep.models import Schedule
from tests.factories import ScheduleFactory, TaskFactory
from tests.utils import HTMX, assert_hx_location, assert_redirect

pytestmark = pytest.mark.django_db


@pytest.fixture
def schedule():
    return ScheduleFactory.create()


def test_create_schedule(admin_client):
    task = TaskFactory.create()
    data = {"task": task.pk, "due_date": "2026-06-01", "completion_date": "", "notes": "n"}
    url = reverse("upkeep:schedule-new", args=[task.pk])
    response = admin_client.post(url, data, headers=HTMX)

    assert_redirect(response, reverse("upkeep:task-detail", args=[task.pk]))
    schedule = Schedule.objects.get()
    assert schedule.task == task
    assert schedule.due_date == datetime.date(2026, 6, 1)
    assert schedule.completion_date is None


def test_create_schedule_initial(admin_client):
    task = TaskFactory.create(interval=None)
    url = reverse("upkeep:schedule-new", args=[task.pk])
    response = admin_client.get(url, headers=HTMX)

    initial = response.context["form"].initial
    assert initial["task"] == task.pk
    assert initial["due_date"] == task.next_date()


def test_create_schedule_invalid(admin_client):
    task = TaskFactory.create()
    data = {"task": task.pk, "due_date": "not a date"}
    url = reverse("upkeep:schedule-new", args=[task.pk])
    response = admin_client.post(url, data, headers=HTMX)

    assert response.status_code == 200
    assertContains(response, "Enter a valid date.")
    assert not Schedule.objects.exists()


def test_update_schedule(admin_client, schedule):
    data = {
        "task": schedule.task.pk,
        "due_date": "2024-02-01",
        "completion_date": "2024-02-02",
        "notes": "",
    }
    url = reverse("upkeep:schedule-edit", args=[schedule.pk])
    response = admin_client.post(url, data, headers=HTMX)

    assert_redirect(response, reverse("upkeep:task-detail", args=[schedule.task.pk]))
    schedule.refresh_from_db()
    assert schedule.due_date == datetime.date(2024, 2, 1)
    assert schedule.completion_date == datetime.date(2024, 2, 2)


def test_delete_schedule(admin_client, schedule):
    url = reverse("upkeep:schedule-delete", args=[schedule.pk])
    response = admin_client.post(url, headers=HTMX)

    assert_hx_location(response, reverse("upkeep:task-detail", args=[schedule.task.pk]))
    assert not Schedule.objects.exists()


def test_toggle_schedule(admin_client, schedule):
    url = reverse("upkeep:schedule-toggle", args=[schedule.pk])
    task_detail = reverse("upkeep:task-detail", args=[schedule.task.pk])

    response = admin_client.patch(url, headers=HTMX)
    assert_hx_location(response, task_detail)
    schedule.refresh_from_db()
    assert schedule.completion_date == datetime.datetime.now(datetime.UTC).date()

    response = admin_client.patch(url, headers=HTMX)
    assert_hx_location(response, task_detail)
    schedule.refresh_from_db()
    assert schedule.completion_date is None


def test_toggle_schedule_rejects_post(admin_client, schedule):
    response = admin_client.post(reverse("upkeep:schedule-toggle", args=[schedule.pk]))
    assert response.status_code == 405
