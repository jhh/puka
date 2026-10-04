"""Markup of the converted upkeep pages."""

from __future__ import annotations

import pytest
from django.urls import reverse

from tests.factories import (
    AreaFactory,
    BookmarkFactory,
    InventoryFactory,
    LocationFactory,
    ScheduleFactory,
    TaskItemFactory,
)
from tests.utils import HTMX, parse_html

pytestmark = pytest.mark.django_db


def test_task_detail(admin_client):
    schedule = ScheduleFactory.create()
    task = schedule.task
    task_item = TaskItemFactory.create(task=task)
    content = admin_client.get(
        reverse("upkeep:task-detail", args=[task.pk]),
        headers=HTMX,
    ).content.decode()
    page = parse_html(content)

    (toggle,) = page.find("input", type="checkbox")
    assert toggle.attrs["hx-patch"] == reverse("upkeep:schedule-toggle", args=[schedule.pk])
    assert "checked" not in toggle.attrs
    assert page.find("a", href=reverse("upkeep:schedule-edit", args=[schedule.pk]))
    assert page.find("a", href=reverse("upkeep:task-item-edit", args=[task_item.pk]))
    assert page.find("a", href=reverse("upkeep:area-detail", args=[task.area_id]))
    assert "6 months" in content
    (delete,) = page.find("button", hx_post=reverse("upkeep:task-delete", args=[task.pk]))
    assert delete.attrs["hx-confirm"] == "Are you sure you want to delete this task?"
    (trigger,) = page.find("button", popovertarget="task-manage-menu")
    assert trigger.text == "Manage"
    (menu,) = page.find("ul", id="task-manage-menu")
    assert "popover" in menu.attrs
    for name in ("upkeep:task-edit", "upkeep:schedule-new", "upkeep:task-item-new"):
        (link,) = page.find("a", href=reverse(name, args=[task.pk]))
        assert link.attrs["hx-get"] == link.attrs["href"]
        assert link.attrs["hx-target"] == "#content"
        assert link.attrs["hx-push-url"] == "true"
    assert [el.text for el in page.find("dt")] == ["Notes", "Interval", "Duration"]


def test_task_detail_empty_states(admin_client):
    task = ScheduleFactory.create().task
    task.schedules.all().delete()
    content = admin_client.get(reverse("upkeep:task-detail", args=[task.pk])).content.decode()
    assert "No schedules" in content
    assert "No consumables" in content


@pytest.mark.parametrize("quantities", [[], [0], [2, 3]])
def test_task_detail_displays_prepared_stock_total(admin_client, quantities):
    task_item = TaskItemFactory.create(quantity=6)
    for index, quantity in enumerate(quantities):
        location = LocationFactory.create(code=f"A01-{index + 1:02}")
        InventoryFactory.create(item=task_item.item, location=location, quantity=quantity)
    response = admin_client.get(
        reverse("upkeep:task-detail", args=[task_item.task.pk]),
        headers=HTMX,
    )
    assert response.status_code == 200
    assert response.context["task_consumables"][0].on_hand == sum(quantities)
    # With no schedules there is just the consumables table's one data row.
    cells = [cell.text for cell in parse_html(response.content).find("td")]
    assert cells[2:4] == ["6", str(sum(quantities))]


def test_area_detail_bookmarks_inside_definition_list(admin_client):
    area = AreaFactory.create()
    area.bookmarks.add(BookmarkFactory.create())
    content = admin_client.get(
        reverse("upkeep:area-detail", args=[area.pk]),
        headers=HTMX,
    ).content.decode()
    dl = content[content.index("<dl") : content.index("</dl>")]
    assert "<dd" in dl[dl.index("Bookmarks") :]
    assert "No tasks in this area" in content
    page = parse_html(content)
    assert page.find("a", href=reverse("upkeep:task-new") + f"?area={area.pk}")
    (trigger,) = page.find("button", popovertarget="area-manage-menu")
    assert trigger.text == "Manage"
    (menu,) = page.find("ul", id="area-manage-menu")
    assert "popover" in menu.attrs
    (delete,) = page.find("button", hx_post=reverse("upkeep:area-delete", args=[area.pk]))
    assert delete.attrs["hx-confirm"] == "Are you sure you want to delete this area?"
    for path in (
        reverse("upkeep:area-edit", args=[area.pk]),
        reverse("upkeep:task-new") + f"?area={area.pk}",
        reverse("upkeep:bookmark-select", args=[area.pk]),
    ):
        (link,) = page.find("a", href=path)
        assert link.attrs["hx-get"] == path
        assert link.attrs["hx-target"] == "#content"
        assert link.attrs["hx-push-url"] == "true"


@pytest.mark.parametrize(
    ("url", "empty"),
    [("upkeep:task-list", "No tasks"), ("upkeep:area-list", "No areas")],
)
def test_lists_empty_state(admin_client, url, empty):
    assert empty in admin_client.get(reverse(url)).content.decode()


def test_task_list_stock_badge(admin_client):
    ScheduleFactory.create()
    page = parse_html(admin_client.get(reverse("upkeep:task-list"), headers=HTMX).content)
    badges = [el for el in page.find("span") if "badge" in el.attrs.get("class", "")]
    assert [b.text for b in badges] == ["in stock"]
    for link in page.find("a"):
        assert link.attrs.get("href") != "#"


@pytest.mark.parametrize("name", ["upkeep:task-list", "upkeep:area-detail"])
def test_prepared_shortage_stock_badge(admin_client, name):
    task_item = TaskItemFactory.create()
    args = [task_item.task.area_id] if name == "upkeep:area-detail" else []
    response = admin_client.get(reverse(name, args=args), headers=HTMX)
    assert response.status_code == 200
    badges = [
        el.text
        for el in parse_html(response.content).find("span")
        if "badge" in el.attrs.get("class", "")
    ]
    assert badges == ["out of stock"]
