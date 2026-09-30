from __future__ import annotations

import pytest
from django.urls import reverse
from pytest_django.asserts import assertContains

from puka.upkeep.models import Area
from tests.factories import AreaFactory, BookmarkFactory
from tests.utils import HTMX, assert_hx_location, assert_redirect

pytestmark = pytest.mark.django_db


@pytest.fixture
def area():
    return AreaFactory.create()


def test_create_area(admin_client):
    data = {"name": "Kitchen", "notes": "downstairs"}
    response = admin_client.post(reverse("upkeep:area-new"), data, headers=HTMX)

    assert_redirect(response, reverse("upkeep:area-list"))
    area = Area.objects.get()
    assert area.name == "Kitchen"
    assert area.notes == "downstairs"


def test_create_area_invalid(admin_client):
    response = admin_client.post(reverse("upkeep:area-new"), {"name": ""}, headers=HTMX)

    assert response.status_code == 200
    assertContains(response, "This field is required.")
    assert not Area.objects.exists()


def test_update_area(admin_client, area):
    data = {"name": "Renamed", "notes": ""}
    url = reverse("upkeep:area-edit", args=[area.pk])
    response = admin_client.post(url, data, headers=HTMX)

    assert_redirect(response, reverse("upkeep:area-list"))
    area.refresh_from_db()
    assert area.name == "Renamed"
    assert area.notes == ""


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


def test_delete_bookmark(admin_client, area):
    bookmark = BookmarkFactory.create()
    area.bookmarks.add(bookmark)
    url = reverse("upkeep:bookmark-delete", args=[area.pk])
    response = admin_client.post(url, {"bookmark_pk": bookmark.pk}, headers=HTMX)

    assert_hx_location(response, reverse("upkeep:area-detail", args=[area.pk]))
    assert not area.bookmarks.exists()
