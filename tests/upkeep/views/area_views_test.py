from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from django.urls import reverse
from django.utils.formats import date_format
from pytest_django.asserts import assertContains

from puka.upkeep.models import Area
from tests.factories import (
    AreaFactory,
    BookmarkFactory,
    LocationFactory,
    ScheduleFactory,
    TaskFactory,
)
from tests.utils import HTMX, assert_hx_location, assert_redirect, parse_html

pytestmark = pytest.mark.django_db


@pytest.fixture
def area():
    return AreaFactory.create()


def test_create_area(admin_client, location):
    data = {"name": "Kitchen", "notes": "downstairs", "location": location.pk}
    response = admin_client.post(reverse("upkeep:area-new"), data, headers=HTMX)

    assert_redirect(response, reverse("upkeep:area-list"))
    area = Area.objects.get()
    assert area.name == "Kitchen"
    assert area.notes == "downstairs"
    assert area.location == location


def test_create_area_invalid(admin_client):
    response = admin_client.post(reverse("upkeep:area-new"), {"name": ""}, headers=HTMX)

    assert response.status_code == 200
    assertContains(response, "This field is required.")
    assert not Area.objects.exists()


def test_create_area_requires_location(admin_client):
    response = admin_client.post(reverse("upkeep:area-new"), {"name": "Kitchen"}, headers=HTMX)

    assert response.status_code == 200
    assertContains(response, "This field is required.")
    assert not Area.objects.exists()


def test_create_area_form_has_no_default_location(admin_client):
    response = admin_client.get(reverse("upkeep:area-new"), headers=HTMX)

    form = response.context["form"]
    assert form["location"].value() is None
    assert form.fields["location"].required


def test_area_form_location_options(admin_client):
    location = LocationFactory.create(name="Garage", code="G")
    response = admin_client.get(reverse("upkeep:area-new"), headers=HTMX)

    options = parse_html(response.content).options("location")
    assert options[str(location.pk)].text == "Garage (G)"


def test_update_area(admin_client, area):
    data = {"name": "Renamed", "notes": "", "location": area.location_id}
    url = reverse("upkeep:area-edit", args=[area.pk])
    response = admin_client.post(url, data, headers=HTMX)

    assert_redirect(response, reverse("upkeep:area-list"))
    area.refresh_from_db()
    assert area.name == "Renamed"
    assert area.notes == ""


def test_update_area_location(admin_client, area):
    location = LocationFactory.create(name="Garage", code="G")
    data = {"name": area.name, "notes": "", "location": location.pk}
    url = reverse("upkeep:area-edit", args=[area.pk])
    response = admin_client.post(url, data, headers=HTMX)

    assert_redirect(response, reverse("upkeep:area-list"))
    area.refresh_from_db()
    assert area.location == location


def test_area_detail_shows_location(admin_client, area):
    location = LocationFactory.create(name="Garage", code="G")
    area.location = location
    area.save()
    response = admin_client.get(reverse("upkeep:area-detail", args=[area.pk]), headers=HTMX)

    page = parse_html(response.content)
    (link,) = page.find("a", href=reverse("stuff:location-detail", args=[location.pk]))
    assert link.text == "Garage (G)"


def test_area_detail_highlights_past_due_date(admin_client, area):
    today = datetime.now(UTC).date()
    past_due = TaskFactory.create(area=area, name="Past due")
    ScheduleFactory.create(task=past_due, due_date=today - timedelta(days=1))
    due_today = TaskFactory.create(area=area, name="Due today")
    ScheduleFactory.create(task=due_today, due_date=today)

    response = admin_client.get(reverse("upkeep:area-detail", args=[area.pk]), headers=HTMX)
    page = parse_html(response.content)

    (past_due_cell,) = (
        el for el in page.find("td") if el.text == date_format(today - timedelta(days=1))
    )
    assert {"font-semibold", "text-error"} <= set(past_due_cell.attrs["class"].split())

    (due_today_cell,) = (el for el in page.find("td") if el.text == date_format(today))
    assert "text-error" not in due_today_cell.attrs["class"]


def test_area_list_shows_location(admin_client, area):
    location = LocationFactory.create(name="Garage", code="G")
    area.location = location
    area.save()
    response = admin_client.get(reverse("upkeep:area-list"), headers=HTMX)

    assertContains(response, ">Garage<")


def test_delete_area(admin_client, area):
    response = admin_client.post(reverse("upkeep:area-delete", args=[area.pk]), headers=HTMX)

    assert_hx_location(response, reverse("upkeep:area-list"))
    assert not Area.objects.exists()


def test_select_bookmark(admin_client, area):
    bookmark = BookmarkFactory.create()
    url = reverse("upkeep:bookmark-select", args=[area.pk])
    response = admin_client.post(url, {"bookmark_pk": bookmark.pk}, headers=HTMX)

    assert_hx_location(response, reverse("upkeep:area-detail", args=[area.pk]))
    assert list(area.bookmarks.all()) == [bookmark]


def test_select_bookmark_without_selection_adds_nothing(admin_client, area):
    url = reverse("upkeep:bookmark-select", args=[area.pk])
    response = admin_client.post(url, headers=HTMX)

    assert_hx_location(response, reverse("upkeep:area-detail", args=[area.pk]))
    assert not area.bookmarks.exists()


def test_delete_bookmark(admin_client, area):
    bookmark = BookmarkFactory.create()
    area.bookmarks.add(bookmark)
    url = reverse("upkeep:bookmark-delete", args=[area.pk])
    response = admin_client.post(url, {"bookmark_pk": bookmark.pk}, headers=HTMX)

    assert_hx_location(response, reverse("upkeep:area-detail", args=[area.pk]))
    assert not area.bookmarks.exists()
