from __future__ import annotations

import pytest
from django.urls import reverse
from pytest_django.asserts import assertContains

from puka.stuff.models import Inventory, Item, Location
from puka.stuff.services import move_inventory
from tests.factories import ItemFactory, ItemWithInventoryFactory, LocationFactory
from tests.utils import HTMX, assert_hx_location, assert_redirect, parse_html

pytestmark = pytest.mark.django_db


@pytest.fixture
def stock():
    return ItemWithInventoryFactory.create().inventories.get()


@pytest.fixture
def destination():
    return LocationFactory.create(name="Other shelf", code="A01-03")


def inventory_url(action, stock, location=None):
    return reverse(
        f"stuff:location-inventory-{action}",
        args=[location.pk if location else stock.location_id, stock.pk],
    )


def test_location_browser_shows_direct_inventory_and_children(admin_client, stock):
    parent = Location.objects.get_parent(stock.location)
    item = ItemFactory.create(name="Stored on parent")
    Inventory.objects.create(location=parent, item=item, quantity=4)
    response = admin_client.get(reverse("stuff:location-list", args=[parent.pk]), headers=HTMX)
    assertContains(response, item.name)
    assert stock.item.name not in response.content.decode()
    page = parse_html(response.content)
    assert page.find("a", href=reverse("stuff:location-list", args=[stock.location_id]))
    assert page.find("a", href=reverse("stuff:location-list", args=[0]))


@pytest.mark.parametrize("headers", [{}, HTMX])
def test_leaf_browser_shows_inventory_and_actions(admin_client, stock, headers):
    response = admin_client.get(
        reverse("stuff:location-list", args=[stock.location_id]),
        headers=headers,
    )
    assertContains(response, stock.item.name)
    assertContains(response, "Nothing stored here", count=0)
    page = parse_html(response.content)
    for action in ("edit", "move"):
        (link,) = page.find("a", href=inventory_url(action, stock))
        assert link.attrs["hx-get"] == link.attrs["href"]
        assert link.attrs["hx-target"] == "#content"
        assert "aria-disabled" not in link.attrs
        assert "{%" not in link.attrs
    parent = Location.objects.get_parent(stock.location)
    assert page.find("a", href=reverse("stuff:location-list", args=[parent.pk]))


def test_add_existing_inventory(admin_client, destination):
    item = ItemFactory.create()
    url = reverse("stuff:location-inventory-new", args=[destination.pk])
    response = admin_client.post(url, {"item": item.pk, "quantity": 3}, headers=HTMX)
    assert_redirect(response, reverse("stuff:location-list", args=[destination.pk]))
    assert Inventory.objects.get(item=item, location=destination).quantity == 3


def test_zero_stock_cannot_be_moved_from_browser(admin_client, stock):
    stock.quantity = 0
    stock.save()
    response = admin_client.get(
        reverse("stuff:location-list", args=[stock.location_id]),
        headers=HTMX,
    )
    page = parse_html(response.content)
    assert not page.find("a", href=inventory_url("move", stock))
    (button,) = page.find("button", **{"aria-label": f"Move {stock.item.name}"})
    assert "disabled" in button.attrs


def test_add_duplicate_inventory_displays_error(admin_client, stock):
    url = reverse("stuff:location-inventory-new", args=[stock.location_id])
    response = admin_client.post(url, {"item": stock.item_id, "quantity": 3}, headers=HTMX)
    assertContains(response, "This item is already stored here.")
    stock.refresh_from_db()
    assert stock.quantity == 10
    assert Inventory.objects.count() == 1


@pytest.mark.parametrize("quantity", [0, 12])
def test_edit_quantity(admin_client, stock, quantity):
    response = admin_client.post(
        inventory_url("edit", stock),
        {"quantity": quantity},
        headers=HTMX,
    )
    assert_redirect(response, reverse("stuff:location-list", args=[stock.location_id]))
    stock.refresh_from_db()
    assert stock.quantity == quantity


def test_edit_quantity_negative(admin_client, stock):
    response = admin_client.post(inventory_url("edit", stock), {"quantity": -1}, headers=HTMX)
    assertContains(response, "Ensure this value is greater than or equal to 0.")
    stock.refresh_from_db()
    assert stock.quantity == 10


@pytest.mark.parametrize("quantity", [3, 10])
@pytest.mark.parametrize("existing", [False, True])
def test_move_inventory(admin_client, stock, destination, quantity, existing):
    if existing:
        Inventory.objects.create(item=stock.item, location=destination, quantity=5)
    response = admin_client.post(
        inventory_url("move", stock),
        {"destination": destination.pk, "quantity": quantity},
        headers=HTMX,
    )
    assert_redirect(response, reverse("stuff:location-list", args=[stock.location_id]))
    target = Inventory.objects.get(item=stock.item, location=destination)
    assert target.quantity == quantity + (5 if existing else 0)
    source = Inventory.objects.filter(pk=stock.pk).first()
    if quantity == 10:
        assert source is None
    else:
        assert source is not None
        assert source.quantity == 10 - quantity
    assert stock.item.quantity() == 10 + (5 if existing else 0)


@pytest.mark.parametrize("quantity", [-1, 0, 11])
def test_invalid_move_quantity(admin_client, stock, destination, quantity):
    response = admin_client.post(
        inventory_url("move", stock),
        {"destination": destination.pk, "quantity": quantity},
        headers=HTMX,
    )
    assert response.status_code == 200
    assert response.context["form"].errors
    stock.refresh_from_db()
    assert stock.quantity == 10
    assert not Inventory.objects.filter(location=destination).exists()


def test_same_location_move_rejected(admin_client, stock):
    response = admin_client.post(
        inventory_url("move", stock),
        {"destination": stock.location_id, "quantity": 3},
        headers=HTMX,
    )
    assert response.status_code == 200
    assert response.context["form"].errors
    stock.refresh_from_db()
    assert stock.quantity == 10


def test_move_rechecks_available_quantity(stock, destination):
    Inventory.objects.filter(pk=stock.pk).update(quantity=2)
    with pytest.raises(ValueError, match="available quantity"):
        move_inventory(stock, destination, 3)
    assert not Inventory.objects.filter(location=destination).exists()


@pytest.mark.parametrize("action", ["edit", "move", "delete"])
def test_inventory_actions_are_scoped_to_location(admin_client, stock, destination, action):
    url = inventory_url(action, stock, destination)
    response = admin_client.post(url, {"quantity": 1}, headers=HTMX)
    assert response.status_code == 404
    assert Inventory.objects.filter(pk=stock.pk).exists()


def test_remove_inventory_keeps_item(admin_client, stock):
    response = admin_client.post(inventory_url("delete", stock), headers=HTMX)
    assert_hx_location(response, reverse("stuff:location-list", args=[stock.location_id]))
    assert not Inventory.objects.filter(pk=stock.pk).exists()
    assert Item.objects.filter(pk=stock.item_id).exists()


@pytest.mark.parametrize("root", [False, True])
def test_create_item_in_location(admin_client, stock, root):
    location = Location.objects.get_parent(stock.location) if root else stock.location
    url = reverse("stuff:location-item-new", args=[location.pk])
    response = admin_client.post(
        url,
        {
            "name": "New item",
            "reorder_level": 1,
            "quantity": 2,
            "location_code": "tampered",
            "tags": "test",
        },
        headers=HTMX,
    )
    assert_redirect(response, reverse("stuff:location-list", args=[location.pk]))
    assert Inventory.objects.get(item__name="New item", location=location).quantity == 2


def test_form_cancels_back_to_location(admin_client, stock):
    for action in ("edit", "move"):
        response = admin_client.get(inventory_url(action, stock), headers=HTMX)
        page = parse_html(response.content)
        assert page.find("a", href=reverse("stuff:location-list", args=[stock.location_id]))
        assert "<head>" not in response.content.decode()


@pytest.mark.parametrize("quantity", [-1, 0, ""])
def test_create_location_item_invalid_quantity(admin_client, stock, quantity):
    response = admin_client.post(
        reverse("stuff:location-item-new", args=[stock.location_id]),
        {"name": "New item", "reorder_level": 1, "tags": "test", "quantity": quantity},
        headers=HTMX,
    )
    assert response.status_code == 200
    assert response.context["form"].errors
    assert not Item.objects.filter(name="New item").exists()
