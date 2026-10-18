from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from django.urls import reverse
from django.utils.formats import date_format

from puka.stuff.models import Location
from tests.conftest import create_bookmark
from tests.factories import (
    AreaFactory,
    InventoryFactory,
    ItemFactory,
    ScheduleFactory,
    TaskFactory,
    TaskItemFactory,
)
from tests.utils import parse_html

pytestmark = pytest.mark.django_db


def test_overview_counts_and_links(admin_client):
    create_bookmark("one", url="https://example.com/1", tags=["a", "b"])
    create_bookmark("two", url="https://example.com/2", tags=["b"])
    inactive = create_bookmark("three", url="https://example.com/3", tags=["c"])
    inactive.active = False
    inactive.save()
    ItemFactory.create(name="Salt").tags.add("c", "d")
    ScheduleFactory.create()

    response = admin_client.get(reverse("home"))
    assert response.context["counts"] == {
        "bookmarks": 2,
        "items": 1,
        # The schedule's task creates an area, which creates the None location.
        "locations": 1,
        "tasks": 1,
        "bookmark_tags": 3,
        "item_tags": 2,
    }

    page = parse_html(response.content)
    cards = [a for a in page.find("a") if "card" in a.attrs.get("class", "").split()]
    assert [a.attrs["href"] for a in cards] == [
        reverse("bookmarks:list"),
        reverse("stuff:item-list"),
        reverse("stuff:location-list", args=[0]),
        reverse("upkeep:task-list"),
    ]
    numbers = [el.text for el in page.find("p") if "text-3xl" in el.attrs.get("class", "")]
    assert numbers == ["2", "1", "1", "1"]

    # The Tags card links each count row to its tags page.
    tag_links = [
        el for el in page.find("a") if "hover:bg-base-200" in el.attrs.get("class", "").split()
    ]
    assert [el.attrs["href"] for el in tag_links] == [
        reverse("bookmarks:tags"),
        reverse("stuff:item-tags"),
    ]
    tag_rows = []
    for link in tag_links:
        index = page.elements.index(link)
        tag_rows.append((page.elements[index + 1].text, page.elements[index + 2].text))
    assert tag_rows == [("3", "bookmark"), ("2", "item")]
    assert "XXX" not in response.content.decode()


def test_overview_upcoming_tasks(admin_client):
    today = datetime.now(UTC).date()
    area = AreaFactory.create(name="Garden")

    due_soon = TaskFactory.create(area=area, name="Water plants")
    ScheduleFactory.create(task=due_soon, due_date=today + timedelta(days=3))

    stocked = ItemFactory.create(name="Stocked supply")
    InventoryFactory.create(item=stocked, quantity=5)
    stocked_later = TaskFactory.create(area=area, name="Mow lawn")
    ScheduleFactory.create(task=stocked_later, due_date=today + timedelta(days=20))
    TaskItemFactory.create(task=stocked_later, item=stocked, quantity=1)

    shortage = ItemFactory.create(name="Short supply")
    short_later = TaskFactory.create(area=area, name="Replace filter")
    ScheduleFactory.create(task=short_later, due_date=today + timedelta(days=25))
    TaskItemFactory.create(task=short_later, item=shortage, quantity=2)

    too_far = TaskFactory.create(area=area, name="Too far")
    ScheduleFactory.create(task=too_far, due_date=today + timedelta(days=40))
    TaskItemFactory.create(task=too_far, item=shortage, quantity=1)

    response = admin_client.get(reverse("home"))
    tasks = list(response.context["upcoming_tasks"])
    assert [task.name for task in tasks] == ["Water plants", "Replace filter"]
    assert [task.are_consumables_stocked() for task in tasks] == [True, False]
    assert [task.due_soon for task in tasks] == [True, False]


def test_overview_upcoming_tasks_table(admin_client):
    today = datetime.now(UTC).date()
    soon_date = today + timedelta(days=3)
    later_date = today + timedelta(days=25)

    root = Location.objects.add_root({"name": "Cloyster", "code": "C"})
    studio = Location.objects.add_child(root, {"name": "Studio", "code": "S"})
    area = AreaFactory.create(name="Studio Air Purifier", location=studio)
    due_soon = TaskFactory.create(area=area, name="Water plants")
    ScheduleFactory.create(task=due_soon, due_date=soon_date)
    out_of_stock = TaskFactory.create(area=area, name="Replace filter")
    ScheduleFactory.create(task=out_of_stock, due_date=later_date)
    TaskItemFactory.create(task=out_of_stock)

    response = admin_client.get(reverse("home"))
    page = parse_html(response.content)

    assert next(el.text for el in page.find("h2")) == "Upcoming Tasks"
    assert [el.text for el in page.find("th")] == ["Task", "Area", "Due", "Consumables"]
    for task in (due_soon, out_of_stock):
        (link,) = page.find("a", href=reverse("upkeep:task-detail", args=[task.pk]))
        assert link.text == task.name
        assert link.attrs["hx-get"] == link.attrs["href"]
        assert link.attrs["hx-target"] == "#content"

    content = response.content.decode()
    assert "Cloyster Studio Air Purifier" in content
    assert date_format(soon_date) in content
    badges = [el.text for el in page.find("span") if "badge" in el.attrs.get("class", "")]
    assert badges == ["in stock", "out of stock"]


def test_overview_without_upcoming_tasks(admin_client):
    response = admin_client.get(reverse("home"))
    assert "No upcoming tasks" in response.content.decode()


def test_404_page(admin_client):
    response = admin_client.get("/404/")
    assert response.status_code == 404
    page = parse_html(response.content)
    assert page.find("h1")[0].text == "Page not found"
    (home,) = page.find("a", href=reverse("home"))
    assert "btn-primary" in home.attrs["class"]
    assert page.find("link", rel="stylesheet")
    assert "<c-" not in response.content.decode()


def test_unknown_url_is_404(admin_client, settings):
    settings.DEBUG = False
    response = admin_client.get("/no/such/page/")
    assert response.status_code == 404
    assert b"Page not found" in response.content
