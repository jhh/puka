"""Inventory search swaps only results, keeping the toolbar and its input alive."""

from __future__ import annotations

from urllib.parse import parse_qs, urlsplit

import pytest
from django.urls import reverse

from tests.factories import ItemFactory
from tests.utils import parse_html

pytestmark = pytest.mark.django_db
RESULTS_HEADERS = {"HX-Request": "true", "HX-Target": "#item-results"}


@pytest.fixture
def search_items():
    items = [ItemFactory.create(name=f"Filter {index:02}") for index in range(21)]
    for item in items:
        item.tags.add("parts & café+#")
    other = ItemFactory.create(name="Other item")
    other.tags.add("other")
    return items, other


@pytest.mark.parametrize("target", ["#item-results", "div#item-results"])
def test_search_response_is_results_only(admin_client, search_items, target):
    items, _ = search_items
    response = admin_client.get(
        reverse("stuff:item-list"),
        {"query": "#parts & café+#"},
        headers={**RESULTS_HEADERS, "HX-Target": target},
    )
    assert response.status_code == 200
    assert list(response.context["items"]) == items[:10]
    page = parse_html(response.content)
    assert page.find("table")
    assert page.find("nav", aria_label="Pagination")
    assert not page.find("input")
    assert not page.find("head")
    assert not page.find("title")
    assert not page.find("div", id="breadcrumbs")
    assert not page.find("ul", id="sidebar")
    assert not page.find("div", id="item-results")
    assert not page.find("a", href=reverse("stuff:item-new"))


@pytest.mark.parametrize(
    "headers",
    [
        {},
        {"HX-Request": "true", "HX-Target": "#content"},
        {**RESULTS_HEADERS, "HX-Boosted": "true"},
        {**RESULTS_HEADERS, "HX-History-Restore-Request": "true"},
        {"HX-Request": "true", "HX-Target": "body"},
    ],
)
def test_navigation_keeps_toolbar(admin_client, headers):
    response = admin_client.get(reverse("stuff:item-list"), {"query": "#parts"}, headers=headers)
    assert response.status_code == 200
    page = parse_html(response.content)
    search = page.field("query")
    assert search.attrs["value"] == "#parts"
    assert search.attrs["hx-target"] == "#item-results"
    assert search.attrs["hx-get"] == reverse("stuff:item-list")
    assert search.attrs["hx-sync"] == "this:replace"
    assert page.find("div", id="item-results")
    (new,) = page.find("a", href=reverse("stuff:item-new"))
    assert new.attrs["hx-target"] == "#content"


def test_results_pagination_keeps_query_and_filter_click_resets_page(admin_client, search_items):
    items, _ = search_items
    response = admin_client.get(
        reverse("stuff:item-list"),
        {"query": "#parts & café+#"},
        headers=RESULTS_HEADERS,
    )
    page = parse_html(response.content)
    (next_link,) = (link for link in page.find("a") if link.text == "Next")
    assert next_link.attrs["hx-target"] == "#item-results"
    assert next_link.attrs["hx-push-url"] == "true"
    assert next_link.attrs["hx-get"] == next_link.attrs["href"]
    assert parse_qs(urlsplit(next_link.attrs["href"]).query) == {
        "page": ["2"],
        "query": ["#parts & café+#"],
    }
    response = admin_client.get(
        reverse("stuff:item-list") + next_link.attrs["href"],
        headers=RESULTS_HEADERS,
    )
    assert list(response.context["items"]) == items[10:20]
    page = parse_html(response.content)
    tag_link = next(
        link
        for link in page.find("a")
        if link.attrs.get("href", "").startswith(reverse("stuff:item-list") + "?query=")
    )
    assert parse_qs(urlsplit(tag_link.attrs["href"]).query) == {"query": ["#parts & café+#"]}
    response = admin_client.get(
        tag_link.attrs["href"],
        headers={"HX-Request": "true", "HX-Target": "#content"},
    )
    assert response.context["page_obj"].number == 1
    assert parse_html(response.content).field("query").attrs["value"] == "#parts & café+#"


def test_empty_and_cleared_search_results(admin_client, search_items):
    empty = admin_client.get(
        reverse("stuff:item-list"),
        {"query": "#missing"},
        headers=RESULTS_HEADERS,
    )
    assert empty.status_code == 200
    assert b"No items found" in empty.content
    cleared = admin_client.get(
        reverse("stuff:item-list"),
        {"query": ""},
        headers=RESULTS_HEADERS,
    )
    assert cleared.status_code == 200
    assert cleared.context["page_obj"].paginator.count == 22
    assert cleared.context["page_obj"].number == 1
