"""Markup of the converted upkeep pages."""

from __future__ import annotations

import pytest
from django.urls import reverse

from tests.factories import AreaFactory, BookmarkFactory, ScheduleFactory, TaskItemFactory
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


def test_task_detail_empty_states(admin_client):
    task = ScheduleFactory.create().task
    task.schedules.all().delete()
    content = admin_client.get(reverse("upkeep:task-detail", args=[task.pk])).content.decode()
    assert "No schedules" in content
    assert "No consumables" in content


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
