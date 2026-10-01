from __future__ import annotations

import pytest
from django.urls import reverse

from tests.conftest import create_bookmark
from tests.factories import ItemFactory, ScheduleFactory
from tests.utils import parse_html

pytestmark = pytest.mark.django_db


def test_overview_counts_and_links(admin_client):
    create_bookmark("one", url="https://example.com/1", tags=["a", "b"])
    create_bookmark("two", url="https://example.com/2", tags=["b"])
    inactive = create_bookmark("three", url="https://example.com/3", tags=["c"])
    inactive.active = False
    inactive.save()
    ItemFactory.create(name="Salt")
    ScheduleFactory.create()

    response = admin_client.get(reverse("home"))
    assert response.context["counts"] == {"bookmarks": 2, "items": 1, "tasks": 1, "tags": 3}

    page = parse_html(response.content)
    cards = [a for a in page.find("a") if "card" in a.attrs.get("class", "").split()]
    assert [a.attrs["href"] for a in cards] == [
        reverse("bookmarks:list"),
        reverse("stuff:item-list"),
        reverse("upkeep:task-list"),
        reverse("bookmarks:tags"),
    ]
    numbers = [el.text for el in page.find("p") if "text-3xl" in el.attrs.get("class", "")]
    assert numbers == ["2", "1", "1", "3"]
    assert "XXX" not in response.content.decode()


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
