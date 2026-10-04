"""Shared presentation components for detail pages; all render without database access."""

from __future__ import annotations

from django.urls import reverse

from tests.core.components_test import classes, only, page


def test_detail_row_value_slot_and_attrs():
    result = page(
        '<c-ui.detail-row label="{{ label }}" class="mb-2" id="notes"'
        ' hx-target="#content" x-show="visible"><a href="/item/">{{ value }}</a>'
        "</c-ui.detail-row>",
        label='Notes "quoted"',
        value="A & B",
    )
    root = result.elements[0]
    assert classes(root) == ["py-4", "sm:grid", "sm:grid-cols-3", "sm:gap-4", "mb-2"]
    assert root.attrs["id"] == "notes"
    assert root.attrs["hx-target"] == "#content"
    assert root.attrs["x-show"] == "visible"
    assert only(result, "dt").text == 'Notes "quoted"'
    assert only(result, "a").text == "A & B"
    assert classes(only(result, "dd")) == [
        "mt-1",
        "text-sm",
        "text-base-content/70",
        "sm:col-span-2",
        "sm:mt-0",
    ]
    assert "label" not in root.attrs


def test_detail_row_preserves_zero_value():
    result = page('<c-ui.detail-row label="Quantity">{{ quantity }}</c-ui.detail-row>', quantity=0)
    assert only(result, "dd").text == "0"


def test_inventory_quantity_controls_and_slot():
    result = page(
        '<c-ui.inventory-quantity :inventory_id="7" :quantity="0" class="justify-end"'
        ' id="controls" x-show="visible"><a href="/edit/">edit</a></c-ui.inventory-quantity>',
        inventory_id=999,
        quantity=999,
    )
    root = result.elements[0]
    assert classes(root) == ["flex", "items-center", "gap-2", "justify-end"]
    assert root.attrs["id"] == "controls"
    assert root.attrs["x-show"] == "visible"
    assert "inventory_id" not in root.attrs
    assert "quantity" not in root.attrs
    minus, plus = result.find("button")
    assert [button.attrs["aria-label"] for button in (minus, plus)] == ["Remove one", "Add one"]
    assert [button.attrs["hx-vals"] for button in (minus, plus)] == [
        '{"quantity": -1}',
        '{"quantity": 1}',
    ]
    for button in (minus, plus):
        assert button.attrs["type"] == "button"
        assert button.attrs["hx-post"] == reverse("stuff:inventory-adjust", args=[7])
        assert button.attrs["hx-target"] == "#id_quantity_7"
        assert "btn-circle" in classes(button)
    assert only(result, "span", id="id_quantity_7").text == "0"
    assert only(result, "a").attrs["href"] == "/edit/"


def test_manage_dropdown_popover_and_slot():
    result = page(
        '<c-layout.manage-dropdown id="manage-test" class="ml-2" x-show="visible">'
        '<li><a href="/edit/" hx-get="/edit/">Edit</a></li>'
        "</c-layout.manage-dropdown>",
    )
    root = result.elements[0]
    assert classes(root) == ["ml-2"]
    assert root.attrs["x-show"] == "visible"
    trigger = only(result, "button")
    assert trigger.text == "Manage"
    assert trigger.attrs["type"] == "button"
    assert trigger.attrs["popovertarget"] == "manage-test"
    assert trigger.attrs["style"] == "anchor-name: --manage-test-anchor"
    menu = only(result, "ul")
    assert menu.attrs["id"] == "manage-test"
    assert "popover" in menu.attrs
    assert menu.attrs["style"] == "position-anchor: --manage-test-anchor"
    assert only(result, "a").attrs["hx-get"] == "/edit/"
    assert not result.find("details")
    assert not result.find("summary")


def test_manage_dropdown_ids_are_unique():
    result = page(
        '<c-layout.manage-dropdown id="first-menu" />'
        '<c-layout.manage-dropdown id="second-menu" />',
    )
    assert [button.attrs["popovertarget"] for button in result.find("button")] == [
        "first-menu",
        "second-menu",
    ]
    assert [menu.attrs["id"] for menu in result.find("ul")] == ["first-menu", "second-menu"]
