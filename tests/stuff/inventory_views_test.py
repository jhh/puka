from __future__ import annotations

import json

import pytest
from django.urls import reverse
from pytest_django.asserts import assertContains

from puka.stuff.models import Bookmark, Inventory
from tests.factories import ItemFactory, ItemWithInventoryFactory, LocationFactory
from tests.utils import HTMX, assert_hx_location, assert_redirect

pytestmark = pytest.mark.django_db


@pytest.fixture
def inventory() -> Inventory:
    return ItemWithInventoryFactory.create().inventories.get()


@pytest.fixture
def item():
    return ItemFactory.create()


@pytest.fixture
def other_location():
    return LocationFactory.create(name="A01-03", code="A01-03")


def test_create_inventory(admin_client, item, other_location):
    data = {"item": item.pk, "location": other_location.pk, "quantity": 4}
    url = reverse("stuff:inventory-new", args=[item.pk])
    response = admin_client.post(url, data, headers=HTMX)

    assert_redirect(response, reverse("stuff:item-detail", args=[item.pk]))
    inventory = Inventory.objects.get(item=item)
    assert inventory.location == other_location
    assert inventory.quantity == 4


def test_create_inventory_initial_item(admin_client, item):
    url = reverse("stuff:inventory-new", args=[item.pk])
    response = admin_client.get(url, headers=HTMX)
    assert response.context["form"].initial["item"] == item.pk


def test_create_inventory_invalid(admin_client, item, other_location):
    data = {"item": item.pk, "location": other_location.pk, "quantity": -1}
    url = reverse("stuff:inventory-new", args=[item.pk])
    response = admin_client.post(url, data, headers=HTMX)

    assert response.status_code == 200
    assertContains(response, "Ensure this value is greater than or equal to 0.")
    assert not Inventory.objects.exists()


def test_update_inventory(admin_client, inventory, other_location):
    data = {"item": inventory.item.pk, "location": other_location.pk, "quantity": 7}
    url = reverse("stuff:inventory-edit", args=[inventory.pk])
    response = admin_client.post(url, data, headers=HTMX)

    assert_redirect(response, reverse("stuff:item-detail", args=[inventory.item.pk]))
    inventory.refresh_from_db()
    assert inventory.location == other_location
    assert inventory.quantity == 7


def test_delete_inventory(admin_client, inventory):
    item_pk = inventory.item.pk
    response = admin_client.post(
        reverse("stuff:inventory-delete", args=[inventory.pk]),
        headers=HTMX,
    )

    assert_hx_location(response, reverse("stuff:item-detail", args=[item_pk]))
    assert not Inventory.objects.filter(pk=inventory.pk).exists()


@pytest.mark.parametrize(("adjustment", "expected"), [(1, 11), (-3, 7)])
def test_adjust_inventory(admin_client, inventory, adjustment, expected):
    url = reverse("stuff:inventory-adjust", args=[inventory.pk])
    response = admin_client.post(url, {"quantity": adjustment}, headers=HTMX)

    assert response.status_code == 200
    assert response["Content-Type"].startswith("text/plain")
    assert response.content.decode() == str(expected)
    assert json.loads(response["HX-Trigger"]) == {
        "inventoryChanged": {"item_id": inventory.item_id},
    }
    inventory.refresh_from_db()
    assert inventory.quantity == expected


def test_update_item(admin_client, item):
    data = {"name": "Renamed", "reorder_level": 5, "tags": "foo", "notes": "n"}
    response = admin_client.post(reverse("stuff:item-edit", args=[item.pk]), data, headers=HTMX)

    assert_redirect(response, reverse("stuff:item-list"))
    item.refresh_from_db()
    assert item.name == "Renamed"
    assert item.reorder_level == 5


def test_delete_item(admin_client, item):
    response = admin_client.post(reverse("stuff:item-delete", args=[item.pk]), headers=HTMX)

    assert_hx_location(response, reverse("stuff:item-list"))
    assert not type(item).objects.filter(pk=item.pk).exists()


def test_select_bookmark(admin_client, item, bookmark):
    url = reverse("stuff:bookmark-select", args=[item.pk])
    response = admin_client.post(url, {"bookmark_pk": bookmark.pk}, headers=HTMX)

    assert_hx_location(response, reverse("stuff:item-detail", args=[item.pk]))
    assert list(item.bookmarks.all()) == [bookmark]


def test_delete_bookmark(admin_client, item, bookmark):
    item.bookmarks.add(bookmark)
    url = reverse("stuff:bookmark-delete", args=[item.pk])
    response = admin_client.post(url, {"bookmark_pk": bookmark.pk}, headers=HTMX)

    assert_hx_location(response, reverse("stuff:item-detail", args=[item.pk]))
    assert not item.bookmarks.exists()
    assert Bookmark.objects.filter(pk=bookmark.pk).exists()
