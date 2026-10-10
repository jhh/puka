"""Markup of the converted stuff pages."""

from __future__ import annotations

import pytest
from django.urls import reverse

from puka.stuff.models import Inventory, Location
from tests.factories import BookmarkFactory, ItemFactory, ItemWithInventoryFactory, LocationFactory
from tests.utils import HTMX, parse_html

pytestmark = pytest.mark.django_db


def test_item_detail_sections_and_quantity_buttons(admin_client):
    item = ItemWithInventoryFactory.create()
    inventory = item.inventories.get()
    url = reverse("stuff:item-detail", args=[item.pk])
    response = admin_client.get(url, headers=HTMX)
    page = parse_html(response.content)

    assert [el.attrs["id"] for el in page.find("h2")] == [
        "inventory-heading",
        "bookmarks-heading",
    ]
    assert [el.attrs["aria-labelledby"] for el in page.find("section")] == [
        "inventory-heading",
        "bookmarks-heading",
    ]
    assert page.find("table")
    (location,) = page.find(
        "a",
        href=reverse("stuff:location-list", args=[inventory.location_id]),
    )
    assert location.text == inventory.location.name
    assert location.attrs["hx-get"] == location.attrs["href"]
    assert location.attrs["hx-target"] == "#content"
    assert "max-w-4xl" not in response.content.decode()
    adjust = reverse("stuff:inventory-adjust", args=[inventory.pk])
    buttons = page.find("button", hx_post=adjust)
    assert all(b.attrs["hx-target"] == f"#id_quantity_{inventory.pk}" for b in buttons)
    (delete,) = page.find("button", hx_post=reverse("stuff:item-delete", args=[item.pk]))
    assert delete.attrs["hx-confirm"] == "Are you sure you want to delete this item?"
    assert not page.find("button", popovertarget="item-manage-menu")
    (edit,) = page.find("a", href=reverse("stuff:item-edit", args=[item.pk]))
    assert "btn" in edit.attrs["class"].split()
    (up,) = (
        link
        for link in page.find("a", href=reverse("stuff:item-list"))
        if "btn" in link.attrs.get("class", "").split()
    )
    assert up.attrs["hx-get"] == reverse("stuff:item-list")
    assert up.attrs["hx-target"] == "#content"
    for name in ("stuff:item-edit", "stuff:inventory-new", "stuff:bookmark-select"):
        (link,) = page.find("a", href=reverse(name, args=[item.pk]))
        assert link.attrs["hx-get"] == link.attrs["href"]
        assert link.attrs["hx-target"] == "#content"
        assert link.attrs["hx-push-url"] == "true"


def test_item_detail_empty_states(admin_client):
    item = ItemFactory.create()
    content = admin_client.get(reverse("stuff:item-detail", args=[item.pk])).content.decode()
    assert "Not stocked anywhere" in content
    assert "No bookmarks" in content


def test_item_and_bookmark_tags_use_matching_info_badges(admin_client):
    item = ItemFactory.create(notes="Compact header notes", reorder_level=3)
    item.tags.add("electronics")
    bookmark = BookmarkFactory.create()
    bookmark.tags.add("manual")
    item.bookmarks.add(bookmark)
    response = admin_client.get(reverse("stuff:item-detail", args=[item.pk]), headers=HTMX)
    page = parse_html(response.content)

    assert not page.find("h2", id="details-heading")
    assert not page.find("dl")
    (notes,) = page.find("p", id="item-notes")
    assert notes.text == item.notes
    (reorder_level,) = page.find("span", id="item-reorder-level")
    assert reorder_level.text == "3"
    for name in ("electronics", "manual"):
        (badge,) = (span for span in page.find("span") if span.text == name)
        classes = badge.attrs["class"].split()
        assert "badge-info" in classes
        assert "badge-soft" in classes
        assert "badge-neutral" not in classes
        assert "badge-error" not in classes
    assert "Manage this item's details" not in response.content.decode()


@pytest.mark.parametrize(
    ("quantity", "variant"),
    [(0, "warning"), (2, "warning"), (3, "success"), (4, "success")],
)
def test_item_reorder_badge_compares_stock_with_minimum(admin_client, quantity, variant):
    item = ItemWithInventoryFactory.create(reorder_level=3)
    inventory = item.inventories.get()
    inventory.quantity = quantity
    inventory.save()
    response = admin_client.get(reverse("stuff:item-detail", args=[item.pk]), headers=HTMX)
    page = parse_html(response.content)
    (badge,) = page.find("span", id="item-reorder-level")
    assert f"badge-{variant}" in badge.attrs["class"].split()


def test_item_reorder_badge_uses_stock_across_locations(admin_client):
    item = ItemWithInventoryFactory.create(reorder_level=12)
    location = LocationFactory.create(name="Other shelf", code="A01-03")
    Inventory.objects.create(item=item, location=location, quantity=2)
    response = admin_client.get(reverse("stuff:item-detail", args=[item.pk]), headers=HTMX)
    page = parse_html(response.content)
    (badge,) = page.find("span", id="item-reorder-level")
    assert "badge-success" in badge.attrs["class"].split()


def test_item_reorder_badge_can_refresh_without_replacing_page(admin_client):
    item = ItemWithInventoryFactory.create(reorder_level=12)
    inventory = item.inventories.get()
    url = reverse("stuff:item-detail", args=[item.pk])
    headers = {**HTMX, "HX-Target": "span#item-reorder-status"}
    response = admin_client.get(url, headers=headers)
    page = parse_html(response.content)
    (badge,) = page.find("span", id="item-reorder-level")
    assert "badge-warning" in badge.attrs["class"].split()
    assert not page.find("h1")
    (status,) = page.find("span", id="item-reorder-status")
    assert status.attrs["hx-swap"] == "outerHTML"
    assert status.attrs["hx-trigger"] == f"inventoryChanged[detail.item_id=={item.pk}] from:window"

    inventory.quantity = 12
    inventory.save()
    response = admin_client.get(url, headers=headers)
    page = parse_html(response.content)
    (badge,) = page.find("span", id="item-reorder-level")
    assert badge.text == "12"
    assert "badge-success" in badge.attrs["class"].split()


@pytest.mark.parametrize(
    ("quantity", "variant"),
    [(0, "warning"), (2, "warning"), (3, "success"), (4, "success")],
)
def test_item_list_reorder_badge_compares_stock_with_minimum(admin_client, quantity, variant):
    item = ItemWithInventoryFactory.create(reorder_level=3)
    inventory = item.inventories.get()
    inventory.quantity = quantity
    inventory.save()
    page = parse_html(admin_client.get(reverse("stuff:item-list"), headers=HTMX).content)

    (quantity_cell,) = (
        el for el in page.find("span") if "tabular-nums" in el.attrs.get("class", "").split()
    )
    assert quantity_cell.text == str(quantity)
    assert any(
        el.text == "Minimum stock" and "sr-only" in el.attrs.get("class", "").split()
        for el in page.find("span")
    )
    label = "Below minimum stock of 3" if variant == "warning" else "Minimum stock of 3 met"
    (badge,) = page.find("span", **{"aria-label": label})
    assert badge.text == "3"
    classes = badge.attrs["class"].split()
    assert f"badge-{variant}" in classes
    assert "badge-soft" in classes


def test_item_list_reorder_badge_hidden_without_reorder_level(admin_client):
    ItemFactory.create(reorder_level=0)
    page = parse_html(admin_client.get(reverse("stuff:item-list"), headers=HTMX).content)

    (quantity_cell,) = (
        el for el in page.find("span") if "tabular-nums" in el.attrs.get("class", "").split()
    )
    assert quantity_cell.text == "0"
    assert not any("badge" in el.attrs.get("class", "").split() for el in page.find("span"))


def test_item_list_orders_below_minimum_items_first(
    admin_client,
    inventory_factory,
    location_factory,
):
    below_a = ItemFactory.create(name="Below A", reorder_level=5)
    below_b = ItemFactory.create(name="Below B", reorder_level=2)
    met = ItemFactory.create(name="Met", reorder_level=2)
    ItemFactory.create(name="No minimum", reorder_level=0)
    inventory_factory(item=below_a, location=location_factory(name="A", code="A"), quantity=1)
    inventory_factory(item=below_b, location=location_factory(name="B", code="B"), quantity=0)
    inventory_factory(item=met, location=location_factory(name="C", code="C"), quantity=5)
    page = parse_html(admin_client.get(reverse("stuff:item-list"), headers=HTMX).content)

    names = [
        link.text
        for link in page.find("a")
        if {"link-hover", "font-semibold"} <= set(link.attrs.get("class", "").split())
    ]
    assert names == ["Below A", "Below B", "Met", "No minimum"]


def test_item_list_empty_and_pagination(admin_client):
    content = admin_client.get(reverse("stuff:item-list") + "?query=zzz").content.decode()
    assert "No items found" in content
    for i in range(25):
        ItemFactory.create(name=f"Item {i:02}")
    page = parse_html(admin_client.get(reverse("stuff:item-list"), headers=HTMX).content)
    (nxt,) = page.find("a", hx_get="?page=2")
    assert nxt.text == "Next"


def test_item_list_table_grows_with_its_rows(admin_client):
    # The page-size menu is pointless if a fixed height keeps the table from growing.
    ItemFactory.create(name="Item")
    page = parse_html(admin_client.get(reverse("stuff:item-list"), headers=HTMX).content)
    (wrapper,) = (
        element
        for element in page.find("div")
        if "overflow-x-auto" in element.attrs.get("class", "")
    )
    assert "h-[" not in wrapper.attrs["class"]
    assert "max-h-[" not in wrapper.attrs["class"]
    assert "overflow-y-auto" not in wrapper.attrs["class"]


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
    assert page.find("a", href=reverse("stuff:location-list", args=[leaf.pk]))

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
        (notes,) = page.find("p", id="item-notes")
        assert notes.text == "Saved notes"
        assert not page.find("span", id="item-reorder-level")
        assert page.find("a", hx_get=reverse("stuff:inventory-edit", args=[inventory.pk]))
    else:
        assert [el.text for el in page.find("dt")][:2] == ["Name", "Code"]
        assert not page.find("button", hx_get=reverse("stuff:inventory-edit", args=[inventory.pk]))
