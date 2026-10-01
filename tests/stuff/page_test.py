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
    assert delete.attrs["hx-confirm"]
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
