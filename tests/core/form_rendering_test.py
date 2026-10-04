"""
Form rendering tests.

These pin down what each form renders (fields, the ``hx-post`` action, submit, cancel and
delete controls, and errors) independently of how it's rendered.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

import pytest
from django.urls import reverse

from puka.stuff.models import Inventory, Item, Location
from puka.upkeep.models import Area, Schedule, Task, TaskItem
from tests.factories import (
    BookmarkFactory,
    ItemFactory,
    ItemWithInventoryFactory,
    ScheduleFactory,
    TaskItemFactory,
)
from tests.utils import HTMX, parse_html

pytestmark = pytest.mark.django_db

# A URL as (url name, args), where args are keys into the ``objects`` fixture or ints.
Url = tuple[str, tuple[str | int, ...]]


@dataclass(frozen=True)
class FormCase:
    id: str
    url: Url
    fields: set[str]
    submit: str
    cancel: Url
    # Forms posting back to the page's own URL (``url``) with hx-post.
    delete: Url | None = None
    delete_noun: str = ""
    autofocus: str | None = None
    hidden: frozenset[str] = frozenset()


FORM_CASES = (
    FormCase(
        "item-new",
        ("stuff:item-new", ()),
        {"name", "reorder_level", "tags", "notes", "location_code", "quantity", "bookmark_url"},
        "Save item",
        ("stuff:item-list", ()),
        autofocus="name",
    ),
    FormCase(
        "item-edit",
        ("stuff:item-edit", ("item",)),
        {"name", "reorder_level", "tags", "notes"},
        "Save item",
        ("stuff:item-list", ()),
        delete=("stuff:item-delete", ("item",)),
        delete_noun="item",
    ),
    FormCase(
        "location-new",
        ("stuff:location-new", ()),
        {"name", "code", "treebeard_position", "treebeard_ref_node"},
        "Save location",
        ("stuff:location-list", (0,)),
        autofocus="name",
    ),
    FormCase(
        "location-edit",
        ("stuff:location-edit", ("location",)),
        {"name", "code", "treebeard_position", "treebeard_ref_node"},
        "Save location",
        ("stuff:location-list", (0,)),
        delete=("stuff:location-delete", ("location",)),
        delete_noun="location",
    ),
    FormCase(
        "inventory-new",
        ("stuff:inventory-new", ("item",)),
        {"item", "location", "quantity"},
        "Save item",
        ("stuff:item-list", ()),
        hidden=frozenset({"item"}),
    ),
    FormCase(
        "inventory-edit",
        ("stuff:inventory-edit", ("inventory",)),
        {"item", "location", "quantity"},
        "Save item",
        ("stuff:item-list", ()),
        delete=("stuff:inventory-delete", ("inventory",)),
        delete_noun="item",
        hidden=frozenset({"item"}),
    ),
    FormCase(
        "area-new",
        ("upkeep:area-new", ()),
        {"name", "notes"},
        "Save area",
        ("upkeep:area-list", ()),
        autofocus="name",
    ),
    FormCase(
        "area-edit",
        ("upkeep:area-edit", ("area",)),
        {"name", "notes"},
        "Save area",
        ("upkeep:area-list", ()),
        delete=("upkeep:area-delete", ("area",)),
        delete_noun="area",
    ),
    FormCase(
        "task-new",
        ("upkeep:task-new", ()),
        {"area", "name", "interval", "frequency", "notes"},
        "Save task",
        ("upkeep:task-list", ()),
        autofocus="name",
    ),
    FormCase(
        "task-edit",
        ("upkeep:task-edit", ("task",)),
        {"area", "name", "interval", "frequency", "notes"},
        "Save task",
        ("upkeep:task-list", ()),
        delete=("upkeep:task-delete", ("task",)),
        delete_noun="task",
    ),
    FormCase(
        "schedule-new",
        ("upkeep:schedule-new", ("task",)),
        {"task", "due_date", "completion_date", "notes"},
        "Save schedule",
        ("upkeep:home", ()),
    ),
    FormCase(
        "schedule-edit",
        ("upkeep:schedule-edit", ("schedule",)),
        {"task", "due_date", "completion_date", "notes"},
        "Save schedule",
        ("upkeep:home", ()),
        delete=("upkeep:schedule-delete", ("schedule",)),
        delete_noun="schedule",
    ),
    FormCase(
        "task-item-new",
        ("upkeep:task-item-new", ("task",)),
        {"task", "item", "quantity"},
        "Save item",
        ("upkeep:home", ()),
    ),
    FormCase(
        "task-item-edit",
        ("upkeep:task-item-edit", ("task_item",)),
        {"task", "item", "quantity"},
        "Save item",
        ("upkeep:home", ()),
        delete=("upkeep:task-item-delete", ("task_item",)),
        delete_noun="item",
    ),
)


@pytest.fixture
def objects() -> dict[str, int]:
    item = ItemWithInventoryFactory.create()
    inventory = item.inventories.get()
    upkeep_item = ItemFactory.create(name="Furnace Filter")
    upkeep_item.tags.add("upkeep")
    schedule = ScheduleFactory.create()
    task_item = TaskItemFactory.create(task=schedule.task, item=upkeep_item)
    return {
        "bookmark": BookmarkFactory.create().pk,
        "item": item.pk,
        "upkeep_item": upkeep_item.pk,
        "inventory": inventory.pk,
        "location": inventory.location.pk,
        "area": schedule.task.area.pk,
        "task": schedule.task.pk,
        "schedule": schedule.pk,
        "task_item": task_item.pk,
    }


def _reverse(url: Url, objects: dict[str, int]) -> str:
    name, args = url
    return reverse(name, args=[objects[a] if isinstance(a, str) else a for a in args])


@pytest.fixture(params=FORM_CASES, ids=lambda case: case.id)
def form_case(request) -> FormCase:
    return request.param


@pytest.fixture
def form_page(admin_client, objects, form_case):
    response = admin_client.get(_reverse(form_case.url, objects), headers=HTMX)
    assert response.status_code == 200
    return parse_html(response.content)


def test_form_action(form_page, form_case, objects):
    (form,) = form_page.forms
    assert form.attrs["hx-post"] == _reverse(form_case.url, objects)
    assert form.attrs["method"] == "post"
    assert form_page.find("input", name="csrfmiddlewaretoken")


def test_form_fields(form_page, form_case):
    assert form_page.field_names() == form_case.fields
    for name in form_case.fields:
        el = form_page.field(name)
        assert el.attrs["id"] == f"id_{name}"
        assert (el.attrs.get("type") == "hidden") == (name in form_case.hidden)


def test_form_labels(form_page, form_case):
    labelled = {el.attrs.get("for") for el in form_page.find("label")}
    visible = form_case.fields - form_case.hidden
    assert {f"id_{name}" for name in visible} <= labelled


def test_form_autofocus(form_page, form_case):
    autofocused = {el.attrs["name"] for el in form_page.elements if "autofocus" in el.attrs}
    assert autofocused == ({form_case.autofocus} if form_case.autofocus else set())


def test_form_submit(form_page, form_case):
    (submit,) = (
        el
        for el in form_page.elements
        if el.tag in {"input", "button"} and el.attrs.get("type") == "submit"
    )
    assert form_case.submit in {submit.attrs.get("value"), submit.text}


def test_form_cancel(form_page, form_case, objects):
    cancel_url = _reverse(form_case.cancel, objects)
    (cancel,) = form_page.find("a", hx_get=cancel_url)
    assert cancel.text == "Cancel"
    assert cancel.attrs["href"] == cancel_url
    assert cancel.attrs["hx-target"] == "#content"
    assert cancel.attrs["hx-push-url"] == "true"


def test_form_delete(form_page, form_case, objects):
    buttons = [el for el in form_page.find("button") if el.text == "Delete"]
    if form_case.delete is None:
        assert not buttons
        return
    (button,) = buttons
    assert button.attrs["type"] == "button"
    assert button.attrs["hx-post"] == _reverse(form_case.delete, objects)
    assert button.attrs["hx-confirm"] == f"Delete this {form_case.delete_noun}?"


# (form url, POST data, field with the error, error message, a submitted value to redisplay)
ERROR_CASES = (
    (
        ("stuff:item-new", ()),
        {"name": "", "reorder_level": "x", "notes": "keep me"},
        "name",
        "This field is required.",
        "keep me",
    ),
    (
        ("stuff:item-new", ()),
        {"name": "New", "reorder_level": 1, "location_code": "A01-05", "quantity": 0},
        "quantity",
        "Quantity must be greater than zero if location provided.",
        "A01-05",
    ),
    (
        ("stuff:location-new", ()),
        {"name": "", "code": "Z9", "treebeard_position": "sorted-child"},
        "name",
        "This field is required.",
        "Z9",
    ),
    (
        ("stuff:inventory-edit", ("inventory",)),
        {"item": "item", "location": "location", "quantity": -1},
        "quantity",
        "Ensure this value is greater than or equal to 0.",
        "-1",
    ),
    (
        ("upkeep:area-new", ()),
        {"name": "", "notes": "keep me"},
        "name",
        "This field is required.",
        "keep me",
    ),
    (
        ("upkeep:task-new", ()),
        {"name": "keep me", "frequency": "fortnights"},
        "frequency",
        "Select a valid choice.",
        "keep me",
    ),
    (
        ("upkeep:schedule-new", ("task",)),
        {"task": "task", "due_date": "not a date"},
        "due_date",
        "Enter a valid date.",
        "not a date",
    ),
    (
        ("upkeep:task-item-new", ("task",)),
        {"task": "task", "item": "upkeep_item", "quantity": "x"},
        "quantity",
        "Enter a whole number.",
        "x",
    ),
)


@pytest.mark.parametrize(
    ("url", "data", "field", "message", "value"),
    ERROR_CASES,
    ids=[f"{case[0][0]}-{case[2]}" for case in ERROR_CASES],
)
def test_form_errors(admin_client, objects, url, data, field, message, value):  # noqa: PLR0913
    data = {k: objects.get(v, v) if isinstance(v, str) else v for k, v in data.items()}
    response = admin_client.post(_reverse(url, objects), data, headers=HTMX)

    assert response.status_code == 200
    content = response.content.decode()
    assert "<head>" not in content
    assert message in content
    assert value in content
    page = parse_html(content)
    assert page.forms[0].attrs["hx-post"] == _reverse(url, objects)
    el = page.field(field)
    assert el.attrs.get("aria-invalid") == "true"


def test_invalid_form_preserves_database_and_returns_errors(admin_client, objects, form_case):
    models = (Item, Location, Inventory, Area, Task, Schedule, TaskItem)
    before = {model: list(model.objects.order_by("pk").values()) for model in models}
    url = _reverse(form_case.url, objects)
    response = admin_client.post(
        url,
        {"notes": "keep invalid notes", "quantity": "x"},
        headers=HTMX,
    )

    assert response.status_code == 200
    assert "<head>" not in response.content.decode()
    assert "Location" not in response
    assert "HX-Location" not in response
    assert response.context["form"].errors
    page = parse_html(response.content)
    (form,) = page.forms
    assert form.attrs["hx-post"] == url
    assert page.field_names() == form_case.fields
    assert page.find("input", name="csrfmiddlewaretoken")
    if "notes" in form_case.fields:
        assert page.field("notes").text == "keep invalid notes"
    assert {model: list(model.objects.order_by("pk").values()) for model in models} == before


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="Step 2: form fragments have no explicit response target",
)
def test_invalid_form_targets_content(admin_client, objects, form_case):
    url = _reverse(form_case.url, objects)
    response = admin_client.post(url, {}, headers=HTMX)
    assert response.status_code == 200
    (form,) = parse_html(response.content).forms
    assert form.attrs.get("hx-target") == "#content"


def test_location_form_parent_choices(admin_client, objects):
    location = Location.objects.get(pk=objects["location"])
    parent = Location.objects.get_parent(location)
    url = reverse("stuff:location-new") + f"?parent={parent.pk}"
    page = parse_html(admin_client.get(url, headers=HTMX).content)

    parents = page.options("treebeard_ref_node")
    assert "selected" in parents[str(parent.pk)].attrs
    assert parents[""].text == "-- root --"
    assert set(page.options("treebeard_position")) == {"sorted-child", "sorted-sibling"}


def test_task_item_form_offers_upkeep_items_only(admin_client, objects):
    url = reverse("upkeep:task-item-new", args=[objects["task"]])
    page = parse_html(admin_client.get(url, headers=HTMX).content)

    assert set(page.options("item")) == {"", str(objects["upkeep_item"])}


def test_schedule_form_task_choices_include_area(admin_client, objects):
    url = reverse("upkeep:schedule-new", args=[objects["task"]])
    page = parse_html(admin_client.get(url, headers=HTMX).content)

    area = Area.objects.get(pk=objects["area"])
    assert page.options("task")[str(objects["task"])].text == f"{area.name}: Test Task"


# Bookmark, filter and login forms.


@pytest.mark.parametrize("name", ["bookmarks:new", "bookmarks:edit"])
def test_bookmark_form(admin_client, objects, name):
    args = [objects["bookmark"]] if name == "bookmarks:edit" else []
    page = parse_html(admin_client.get(reverse(name, args=args)).content)

    # The full page has other forms (e.g. logout); the bookmark form has the title field.
    index = page.field("title").form
    assert index is not None
    form = page.forms[index]
    assert form.attrs["method"] == "post"
    assert "hx-post" not in form.attrs
    assert page.field_names(index) == {"title", "description", "url", "tags", "active"}
    assert page.field("active").attrs["type"] == "checkbox"
    (cancel,) = (el for el in page.find("a") if el.text == "Cancel")
    assert cancel.attrs["href"] == reverse("bookmarks:list")


def test_bookmark_form_errors(admin_client):
    data = {"title": "keep me", "url": "not_a_url"}
    response = admin_client.post(reverse("bookmarks:new"), data)

    assert response.status_code == 200
    content = response.content.decode()
    assert "Enter a valid URL." in content
    assert "keep me" in content
    assert parse_html(content).field("url").attrs.get("aria-invalid") == "true"


def test_bookmark_filter_form(admin_client):
    page = parse_html(admin_client.get(reverse("bookmarks:filter"), headers=HTMX).content)

    (form,) = page.forms
    assert form.attrs["method"] == "get"
    assert page.field_names() == {"text", "tags", "url", "created", "active"}
    assert [el.text for el in page.find("button")] == ["Search"]


@pytest.mark.parametrize(
    ("name", "key"),
    [("stuff:bookmark-select", "item"), ("upkeep:bookmark-select", "area")],
)
def test_bookmark_select_form(admin_client, objects, name, key):
    url = reverse(name, args=[objects[key]])
    page = parse_html(admin_client.get(url, headers=HTMX).content)

    (form,) = page.forms
    assert form.attrs["method"] == "get"
    assert form.attrs["hx-get"] == url
    assert form.attrs["hx-target"] == "#content"
    assert page.field_names() == {"text", "created", "url", "tags", "active"}
    (link,) = page.find("button", hx_post=url)
    assert json.loads(link.attrs["hx-vals"]) == {"bookmark_pk": objects["bookmark"]}


def test_login_form(client):
    page = parse_html(client.get(reverse("login")).content)

    (form,) = page.forms
    assert form.attrs["method"].lower() == "post"
    assert page.field_names() == {"username", "password"}
    assert all(el.attrs.get("href") != "#" for el in page.find("a"))
    assert page.field("password").attrs["type"] == "password"
    assert page.find("input", name="csrfmiddlewaretoken")


def test_login_form_errors(client):
    response = client.post(reverse("login"), {"username": "nobody", "password": "wrong"})

    assert response.status_code == 200
    assert "Please enter a correct username and password." in response.content.decode()
