from __future__ import annotations

import pytest
from django.urls import reverse
from pytest_django.asserts import assertContains

from puka.stuff.models import Inventory, Item, Location
from tests.factories import ItemWithInventoryFactory
from tests.utils import HTMX, assert_hx_location, assert_redirect

pytestmark = pytest.mark.django_db

LOCATION_ROOT = reverse("stuff:location-list", args=[0])


def test_create_root_location(admin_client):
    data = {
        "name": "Garage",
        "code": "G",
        "treebeard_position": "sorted-child",
        "treebeard_ref_node": "",
    }
    response = admin_client.post(reverse("stuff:location-new"), data, headers=HTMX)

    assert_redirect(response, LOCATION_ROOT)
    location = Location.objects.get(code="G")
    assert location.name == "Garage"
    assert location.depth == 1


def test_create_child_location(admin_client, location):
    parent = Location.objects.get_parent(location)
    data = {
        "name": "Shelf",
        "code": "A01-09",
        "treebeard_position": "sorted-child",
        "treebeard_ref_node": parent.pk,
    }
    response = admin_client.post(reverse("stuff:location-new"), data, headers=HTMX)

    assert_redirect(response, reverse("stuff:location-list", args=[parent.pk]))
    child = Location.objects.get(code="A01-09")
    assert Location.objects.get_parent(child) == parent


def test_create_location_initial_parent(admin_client, location):
    parent = Location.objects.get_parent(location)
    url = reverse("stuff:location-new") + f"?parent={parent.pk}"
    response = admin_client.get(url, headers=HTMX)

    assert response.context["form"].initial["treebeard_ref_node"] == str(parent.pk)


@pytest.mark.parametrize("parent", ["0", ""])
def test_create_location_root_parent(admin_client, parent):
    url = reverse("stuff:location-new") + f"?parent={parent}"
    response = admin_client.get(url, headers=HTMX)

    assert response.context["form"].initial["treebeard_ref_node"] is None


def test_create_location_invalid(admin_client):
    data = {"name": "", "code": "", "treebeard_position": "sorted-child"}
    response = admin_client.post(reverse("stuff:location-new"), data, headers=HTMX)

    assert response.status_code == 200
    assert not Location.objects.exists()
    assertContains(response, "This field is required.")
    assert "<head>" not in response.content.decode()


def test_update_location(admin_client, location):
    parent = Location.objects.get_parent(location)
    data = {
        "name": "Renamed",
        "code": location.code,
        "treebeard_position": "sorted-child",
        "treebeard_ref_node": parent.pk,
    }
    url = reverse("stuff:location-edit", args=[location.pk])
    response = admin_client.post(url, data, headers=HTMX)

    assert_redirect(response, reverse("stuff:location-list", args=[location.pk]))
    location.refresh_from_db()
    assert location.name == "Renamed"
    assert Location.objects.get_parent(location) == parent


def test_update_location_invalid(admin_client, location):
    data = {"name": "", "code": location.code, "treebeard_position": "sorted-child"}
    url = reverse("stuff:location-edit", args=[location.pk])
    response = admin_client.post(url, data, headers=HTMX)

    assert response.status_code == 200
    assertContains(response, "This field is required.")
    location.refresh_from_db()
    assert location.name == "A01-02"


def test_delete_location(admin_client, location):
    parent = Location.objects.get_parent(location)
    url = reverse("stuff:location-delete", args=[location.pk])
    response = admin_client.post(url, headers=HTMX)

    assert_hx_location(response, reverse("stuff:location-list", args=[parent.pk]))
    assert not Location.objects.filter(pk=location.pk).exists()


def test_delete_location_not_found(admin_client):
    response = admin_client.post(reverse("stuff:location-delete", args=[999]), headers=HTMX)
    assert response.status_code == 404


def test_delete_parent_removes_descendants_and_inventory_not_items(admin_client):
    item = ItemWithInventoryFactory.create()
    inventory = item.inventories.get()
    parent = Location.objects.get_parent(inventory.location)
    response = admin_client.post(reverse("stuff:location-delete", args=[parent.pk]), headers=HTMX)
    assert_hx_location(response, LOCATION_ROOT)
    assert not Location.objects.filter(pk__in=[parent.pk, inventory.location_id]).exists()
    assert not Inventory.objects.filter(pk=inventory.pk).exists()
    assert Item.objects.filter(pk=item.pk).exists()


def test_delete_location_without_htmx_returns_to_parent(admin_client, location):
    parent = Location.objects.get_parent(location)
    response = admin_client.post(reverse("stuff:location-delete", args=[location.pk]))
    assert_redirect(response, reverse("stuff:location-list", args=[parent.pk]))


def test_create_form_keeps_parent_on_submission(admin_client, location):
    url = reverse("stuff:location-new") + f"?parent={location.pk}"
    response = admin_client.get(url, headers=HTMX)
    assertContains(response, f'hx-post="{url}"')
    assert response.context["form"].cancel_url == reverse(
        "stuff:location-list",
        args=[location.pk],
    )
