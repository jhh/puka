from __future__ import annotations

import pytest
from django.urls import reverse

from puka.upkeep.models import TaskItem
from tests.factories import ItemFactory, TaskFactory, TaskItemFactory
from tests.utils import HTMX, assert_hx_location, assert_redirect

pytestmark = pytest.mark.django_db


@pytest.fixture
def upkeep_item():
    item = ItemFactory.create(name="Furnace Filter")
    item.tags.add("upkeep")
    return item


def test_create_task_item(admin_client, upkeep_item):
    task = TaskFactory.create()
    data = {"task": task.pk, "item": upkeep_item.pk, "quantity": 2}
    url = reverse("upkeep:task-item-new", args=[task.pk])
    response = admin_client.post(url, data, headers=HTMX)

    assert_redirect(response, reverse("upkeep:task-detail", args=[task.pk]))
    task_item = TaskItem.objects.get()
    assert task_item.task == task
    assert task_item.item == upkeep_item
    assert task_item.quantity == 2


def test_create_task_item_initial(admin_client):
    task = TaskFactory.create()
    response = admin_client.get(reverse("upkeep:task-item-new", args=[task.pk]), headers=HTMX)
    assert response.context["form"].initial == {"task": task.pk, "quantity": 1}


def test_update_task_item(admin_client, upkeep_item):
    task_item = TaskItemFactory.create(item=upkeep_item)
    data = {"task": task_item.task.pk, "item": upkeep_item.pk, "quantity": 5}
    url = reverse("upkeep:task-item-edit", args=[task_item.pk])
    response = admin_client.post(url, data, headers=HTMX)

    assert_redirect(response, reverse("upkeep:task-detail", args=[task_item.task.pk]))
    task_item.refresh_from_db()
    assert task_item.quantity == 5


def test_delete_task_item(admin_client):
    task_item = TaskItemFactory.create()
    url = reverse("upkeep:task-item-delete", args=[task_item.pk])
    response = admin_client.post(url, headers=HTMX)

    assert_hx_location(response, reverse("upkeep:task-detail", args=[task_item.task.pk]))
    assert not TaskItem.objects.exists()
