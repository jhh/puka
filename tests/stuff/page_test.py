"""Markup of the converted stuff pages."""

from __future__ import annotations

import pytest
from django.urls import reverse

from puka.stuff.models import Location
from tests.factories import ItemFactory, ItemWithInventoryFactory
from tests.utils import HTMX, parse_html

pytestmark = pytest.mark.django_db


def test_item_detail_tabs_and_quantity_buttons(admin_client):
    item = ItemWithInventoryFactory.create()
    inventory = item.inventories.get()
    url = reverse("stuff:item-detail", args=[item.pk])
    page = parse_html(admin_client.get(url, headers=HTMX).content)

    assert [el.text for el in page.find("button", role="tab")] == [
        "Details",
        "Inventory",
        "Bookmarks",
    ]
    assert len(page.find("div", role="tabpanel")) == 3
    adjust = reverse("stuff:inventory-adjust", args=[inventory.pk])
    buttons = page.find("button", hx_post=adjust)
    assert [b.attrs["hx-vals"] for b in buttons] == ['{"quantity": -1}', '{"quantity": 1}']
    assert all(b.attrs["hx-target"] == f"#id_quantity_{inventory.pk}" for b in buttons)
    (delete,) = page.find("button", hx_post=reverse("stuff:item-delete", args=[item.pk]))
    assert delete.attrs["hx-confirm"] == "Are you sure you want to delete this item?"
    (trigger,) = page.find("button", popovertarget="item-manage-menu")
    assert trigger.text == "Manage"
    (menu,) = page.find("ul", id="item-manage-menu")
    assert "popover" in menu.attrs
    for name in ("stuff:item-edit", "stuff:inventory-new", "stuff:bookmark-select"):
        (link,) = page.find("a", href=reverse(name, args=[item.pk]))
        assert link.attrs["hx-get"] == link.attrs["href"]
        assert link.attrs["hx-target"] == "#content"
        assert link.attrs["hx-push-url"] == "true"
    for link in page.find("a"):
        assert link.attrs.get("href") != "#"


def test_item_detail_empty_states(admin_client):
    item = ItemFactory.create()
    content = admin_client.get(reverse("stuff:item-detail", args=[item.pk])).content.decode()
    assert "Not stocked anywhere" in content
    assert "No bookmarks" in content


def test_item_list_empty_and_pagination(admin_client):
    content = admin_client.get(reverse("stuff:item-list") + "?query=zzz").content.decode()
    assert "No items found" in content
    for i in range(25):
        ItemFactory.create(name=f"Item {i:02}")
    page = parse_html(admin_client.get(reverse("stuff:item-list"), headers=HTMX).content)
    (nxt,) = page.find("a", hx_get="?page=2")
    assert nxt.text == "Next"


def test_location_list_links_and_copy(admin_client):
    inventory = ItemWithInventoryFactory.create().inventories.get()
    leaf = inventory.location
    root = Location.objects.get_parent(leaf)

    page = parse_html(
        admin_client.get(reverse("stuff:location-list", args=[0]), headers=HTMX).content,
    )
    (link,) = page.find("a", href=reverse("stuff:location-list", args=[root.pk]))
    assert link.attrs["hx-get"] == link.attrs["href"]
    (copy,) = page.find("button", **{"aria-label": "Copy code"})
    assert copy.attrs["x-on:click"] == f"navigator.clipboard.writeText('{root.code}')"
    (add,) = (
        a
        for a in page.find("a")
        if a.attrs.get("href", "").startswith(reverse("stuff:location-new"))
    )
    assert add.attrs["href"].endswith("?parent=0")

    page = parse_html(
        admin_client.get(reverse("stuff:location-list", args=[root.pk]), headers=HTMX).content,
    )
    assert page.find("a", href=reverse("stuff:location-detail", args=[leaf.pk]))


def test_location_detail_breadcrumbs(admin_client):
    leaf = ItemWithInventoryFactory.create().inventories.get().location
    root = Location.objects.get_parent(leaf)
    page = parse_html(admin_client.get(reverse("stuff:location-detail", args=[leaf.pk])).content)
    (crumbs,) = page.find("div", id="breadcrumbs")
    hrefs = [
        a.attrs["href"] for a in page.elements[page.elements.index(crumbs) :][:12] if a.tag == "a"
    ]
    assert reverse("stuff:location-list", args=[root.pk]) in hrefs


@pytest.mark.parametrize("name", ["stuff:item-detail", "stuff:location-detail"])
def test_shared_inventory_controls_on_detail_pages(admin_client, name):
    item = ItemWithInventoryFactory.create(reorder_level=0, notes="Saved notes")
    inventory = item.inventories.get()
    inventory.quantity = 0
    inventory.save()
    pk = item.pk if name == "stuff:item-detail" else inventory.location.pk
    response = admin_client.get(reverse(name, args=[pk]), headers=HTMX)
    assert response.status_code == 200
    page = parse_html(response.content)
    (quantity,) = page.find("span", id=f"id_quantity_{inventory.pk}")
    assert quantity.text == "0"
    buttons = page.find("button", hx_post=reverse("stuff:inventory-adjust", args=[inventory.pk]))
    assert [button.attrs["aria-label"] for button in buttons] == ["Remove one", "Add one"]
    assert all(button.attrs["hx-target"] == f"#id_quantity_{inventory.pk}" for button in buttons)
    if name == "stuff:item-detail":
        assert [el.text for el in page.find("dt")][:3] == ["Name", "Notes", "Reorder Level"]
        assert [el.text for el in page.find("dd")][:3] == [item.name, "Saved notes", "0"]
        assert page.find("button", hx_get=reverse("stuff:inventory-edit", args=[inventory.pk]))
    else:
        assert [el.text for el in page.find("dt")][:2] == ["Name", "Code"]
        assert not page.find("button", hx_get=reverse("stuff:inventory-edit", args=[inventory.pk]))
