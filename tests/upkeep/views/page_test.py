"""Markup of the converted upkeep pages."""

from __future__ import annotations

from datetime import date

import pytest
from django.urls import reverse

from tests.factories import (
    AreaFactory,
    BookmarkFactory,
    InventoryFactory,
    LocationFactory,
    ScheduleFactory,
    TaskFactory,
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
    assert [el.attrs["id"] for el in page.find("h2")] == [
        "schedules-heading",
        "consumables-heading",
    ]
    assert [el.attrs["aria-labelledby"] for el in page.find("section")] == [
        "schedules-heading",
        "consumables-heading",
    ]
    assert page.find("a", href=reverse("upkeep:schedule-edit", args=[schedule.pk]))
    assert page.find("a", href=reverse("upkeep:task-item-edit", args=[task_item.pk]))
    assert page.find("a", href=reverse("upkeep:area-detail", args=[task.area_id]))
    assert "6 months" in content
    (delete,) = page.find("button", hx_post=reverse("upkeep:task-delete", args=[task.pk]))
    assert delete.attrs["hx-confirm"] == "Are you sure you want to delete this task?"
    assert not [button for button in page.find("button") if "popovertarget" in button.attrs]
    for name in ("upkeep:task-edit", "upkeep:schedule-new", "upkeep:task-item-new"):
        (link,) = page.find("a", href=reverse(name, args=[task.pk]))
        assert "btn" in link.attrs["class"].split()
        assert link.attrs["hx-get"] == link.attrs["href"]
        assert link.attrs["hx-target"] == "#content"
        assert link.attrs["hx-push-url"] == "true"
    assert [el.text for el in page.find("dt")] == ["Area", "Notes", "Interval", "Duration"]


def test_task_detail_empty_states(admin_client):
    task = ScheduleFactory.create().task
    task.schedules.all().delete()
    content = admin_client.get(reverse("upkeep:task-detail", args=[task.pk])).content.decode()
    assert "No schedules" in content
    assert "No consumables" in content


def test_task_detail_shows_latest_complete_and_upcoming_schedules(admin_client):
    task = TaskFactory.create()
    old = ScheduleFactory.create(
        task=task,
        due_date=date(2024, 1, 1),
        completion_date=date(2024, 1, 2),
    )
    latest = ScheduleFactory.create(
        task=task,
        due_date=date(2024, 2, 1),
        completion_date=date(2024, 2, 3),
    )
    upcoming = ScheduleFactory.create(task=task, due_date=date(2024, 3, 1))
    later = ScheduleFactory.create(task=task, due_date=date(2024, 4, 1))

    page = parse_html(
        admin_client.get(reverse("upkeep:task-detail", args=[task.pk]), headers=HTMX).content,
    )

    toggles = page.find("input", type="checkbox")
    assert [el.attrs["hx-patch"] for el in toggles] == [
        reverse("upkeep:schedule-toggle", args=[latest.pk]),
        reverse("upkeep:schedule-toggle", args=[upcoming.pk]),
        reverse("upkeep:schedule-toggle", args=[later.pk]),
    ]
    assert "checked" in toggles[0].attrs
    assert "checked" not in toggles[1].attrs
    assert page.find("a", href=reverse("upkeep:schedule-edit", args=[latest.pk]))
    assert page.find("a", href=reverse("upkeep:schedule-edit", args=[upcoming.pk]))
    assert not page.find("a", href=reverse("upkeep:schedule-edit", args=[old.pk]))


def test_task_detail_without_upcoming_shows_only_latest_complete(admin_client):
    task = TaskFactory.create()
    ScheduleFactory.create(task=task, due_date=date(2024, 1, 1), completion_date=date(2024, 1, 2))
    latest = ScheduleFactory.create(
        task=task,
        due_date=date(2024, 2, 1),
        completion_date=date(2024, 2, 3),
    )

    page = parse_html(
        admin_client.get(reverse("upkeep:task-detail", args=[task.pk]), headers=HTMX).content,
    )

    (toggle,) = page.find("input", type="checkbox")
    assert toggle.attrs["hx-patch"] == reverse("upkeep:schedule-toggle", args=[latest.pk])
    assert "checked" in toggle.attrs


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


def test_area_detail_sections_and_actions(admin_client):
    area = AreaFactory.create()
    bookmark = BookmarkFactory.create()
    bookmark.tags.add("manual")
    area.bookmarks.add(bookmark)
    content = admin_client.get(
        reverse("upkeep:area-detail", args=[area.pk]),
        headers=HTMX,
    ).content.decode()
    assert "No tasks in this area" in content
    page = parse_html(content)

    assert [el.attrs["id"] for el in page.find("h2")] == ["tasks-heading", "bookmarks-heading"]
    assert [el.attrs["aria-labelledby"] for el in page.find("section")] == [
        "tasks-heading",
        "bookmarks-heading",
    ]
    assert [el.text for el in page.find("dt")] == ["Name", "Location", "Notes"]
    (badge,) = (el for el in page.find("span") if el.text == "manual")
    assert {"badge-info", "badge-soft"} <= set(badge.attrs["class"].split())
    assert page.find("a", href=bookmark.url)
    assert not [button for button in page.find("button") if "popovertarget" in button.attrs]
    (delete,) = page.find("button", hx_post=reverse("upkeep:area-delete", args=[area.pk]))
    assert delete.attrs["hx-confirm"] == "Are you sure you want to delete this area?"
    for path in (
        reverse("upkeep:area-edit", args=[area.pk]),
        reverse("upkeep:task-new") + f"?area={area.pk}",
        reverse("upkeep:bookmark-select", args=[area.pk]),
    ):
        (link,) = page.find("a", href=path)
        assert "btn" in link.attrs["class"].split()
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
