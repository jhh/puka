"""Tag links replace filters and safely round-trip through ordinary and htmx requests."""

from __future__ import annotations

from urllib.parse import parse_qs, urlsplit

import pytest
from django.urls import reverse

from tests.factories import AreaFactory, BookmarkFactory, ItemFactory
from tests.utils import parse_html

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize("tag", ["two words", "tools & parts", "C++", "#priority", "café 日本語"])
@pytest.mark.parametrize(
    "source",
    [
        "bookmarks:list",
        "bookmarks:filter",
        "bookmarks:tags",
        "stuff:item-list",
        "stuff:item-detail",
        "upkeep:area-detail",
    ],
)
@pytest.mark.parametrize("htmx", [False, True], ids=["ordinary", "htmx"])
def test_tag_link_round_trip(admin_client, tag, source, htmx):
    bookmark = BookmarkFactory.create(active=True, title="Matching bookmark")
    bookmark.tags.add(tag)
    BookmarkFactory.create(active=True, title="Unrelated bookmark")
    item = ItemFactory.create(name="Matching item")
    item.tags.add(tag)
    item.bookmarks.add(bookmark)
    ItemFactory.create(name="Unrelated item")
    area = AreaFactory.create()
    area.bookmarks.add(bookmark)
    args = {"stuff:item-detail": [item.pk], "upkeep:area-detail": [area.pk]}.get(source, [])
    response = admin_client.get(
        reverse(source, args=args),
        {"page": 1, "active": "True", "url": "", "q": ""},
    )
    assert response.status_code == 200
    page = parse_html(response.content)
    inventory = source in {"stuff:item-list", "stuff:item-detail"}
    (link,) = (
        el
        for el in page.find("a")
        if ("?query=" if inventory else "?tags=") in el.attrs.get("href", "")
    )
    href = link.attrs["href"]
    assert link.attrs["hx-get"] == href
    parts = urlsplit(href)
    assert not parts.fragment
    tag_value = f'"{tag}"' if source in {"bookmarks:filter", "upkeep:area-detail"} else tag
    assert parse_qs(parts.query) == (
        {"query": ["#" + tag]} if inventory else {"tags": [tag_value]}
    )
    destination = parts.path or reverse(source)
    headers = {"HX-Request": "true", "HX-Target": link.attrs["hx-target"]} if htmx else {}
    filtered = admin_client.get(destination + "?" + parts.query, headers=headers)
    assert filtered.status_code == 200
    objects = filtered.context["items"] if inventory else filtered.context["page_obj"]
    assert [obj.pk for obj in objects] == [item.pk if inventory else bookmark.pk]
    assert filtered.context["page_obj"].number == 1
    assert bool(parse_html(filtered.content).find("head")) is not htmx


@pytest.mark.parametrize("source", ["stuff:item-detail", "upkeep:area-detail"])
def test_attached_bookmark_tag_link_round_trip(admin_client, source):
    bookmark = BookmarkFactory.create(active=False)
    bookmark.tags.add("parts & café+#")
    owner = ItemFactory.create() if source == "stuff:item-detail" else AreaFactory.create()
    owner.bookmarks.add(bookmark)
    page = parse_html(admin_client.get(reverse(source, args=[owner.pk])).content)
    (link,) = (el for el in page.find("a") if "?tags=" in el.attrs.get("href", ""))
    assert urlsplit(link.attrs["href"]).path == reverse("bookmarks:filter")
    assert parse_qs(urlsplit(link.attrs["href"]).query) == {"tags": ['"parts & café+#"']}
    for headers in ({}, {"HX-Request": "true", "HX-Target": "#content"}):
        response = admin_client.get(link.attrs["href"], headers=headers)
        assert response.status_code == 200
        assert [obj.pk for obj in response.context["page_obj"]] == [bookmark.pk]


@pytest.mark.parametrize("source", ["bookmarks:list", "bookmarks:filter"])
def test_bookmark_tag_click_resets_pagination_and_other_filters(admin_client, source):
    for index in range(26):
        bookmark = BookmarkFactory.create(
            url=f"https://example.com/tag/{index}",
            active=True,
        )
        bookmark.tags.add("two words")
    response = admin_client.get(reverse(source), {"page": 2, "active": "True", "url": "example"})
    assert response.status_code == 200
    assert response.context["page_obj"].number == 2
    page = parse_html(response.content)
    (link,) = (el for el in page.find("a") if "?tags=" in el.attrs.get("href", ""))
    tag_value = '"two words"' if source == "bookmarks:filter" else "two words"
    assert parse_qs(urlsplit(link.attrs["href"]).query) == {"tags": [tag_value]}
    for headers in ({}, {"HX-Request": "true", "HX-Target": "#id_bookmarks"}):
        response = admin_client.get(reverse(source) + link.attrs["href"], headers=headers)
        assert response.status_code == 200
        assert response.context["page_obj"].number == 1
        assert response.context["page_obj"].paginator.count == 26
