"""Top tags on the item list and the single active tag filter."""

from __future__ import annotations

from urllib.parse import parse_qs, urlsplit

import pytest
from django.urls import reverse

from puka.stuff.models import Item
from tests.factories import ItemFactory
from tests.utils import parse_html

pytestmark = pytest.mark.django_db
RESULTS_HEADERS = {"HX-Request": "true", "HX-Target": "#item-results"}
CONTENT_HEADERS = {"HX-Request": "true", "HX-Target": "#content"}


def tag_links(page):
    """Links that set the single tag filter (item-row tag links use ?query=)."""
    return [
        link for link in page.find("a") if "tag" in parse_qs(urlsplit(link.attrs["href"]).query)
    ]


def query(link):
    return parse_qs(urlsplit(link.attrs["href"]).query)


def test_top_tags_rank_tags_within_search_and_category(admin_client, category_factory):
    tools = category_factory(name="Tools")
    electronics = category_factory(name="Electronics")
    for index in range(3):
        item = ItemFactory.create(name=f"Tool {index}", category=tools)
        item.tags.add("common")
    drill = ItemFactory.create(name="Drill", category=tools)
    drill.tags.add("common", "cordless")
    saw = ItemFactory.create(name="Saw", category=tools)
    saw.tags.add("cordless")
    radio = ItemFactory.create(name="Radio", category=electronics)
    radio.tags.add("radio")

    response = admin_client.get(
        reverse("stuff:item-list"),
        {"category": tools.pk},
        headers=RESULTS_HEADERS,
    )

    assert [tag.name for tag in response.context["top_tags"]] == ["common", "cordless"]
    page = parse_html(response.content)
    links = tag_links(page)
    assert [query(link)["tag"] for link in links] == [["common"], ["cordless"]]
    for link in links:
        assert link.attrs["hx-get"] == link.attrs["href"]
        assert link.attrs["hx-target"] == "#content"
        assert link.attrs["hx-push-url"] == "true"
        assert query(link)["category"] == [str(tools.pk)]


def test_top_tags_are_limited_to_one_scrolling_row(admin_client):
    for index in range(12):
        item = ItemFactory.create(name=f"Item {index:02}")
        item.tags.add(f"tag-{index:02}")

    response = admin_client.get(reverse("stuff:item-list"), headers=RESULTS_HEADERS)

    assert [tag.name for tag in response.context["top_tags"]] == [
        f"tag-{index:02}" for index in range(10)
    ]
    page = parse_html(response.content)
    (tag_list,) = page.find("ul", aria_label="Filter by tag")
    assert {"flex-nowrap", "overflow-x-auto"} <= set(tag_list.attrs["class"].split())


def test_tag_filter_composes_with_query_and_category(admin_client, category_factory):
    tools = category_factory(name="Tools")
    electronics = category_factory(name="Electronics")
    hammer = ItemFactory.create(name="Claw hammer", category=tools)
    hammer.tags.add("metal")
    ItemFactory.create(name="Hammer drill", category=tools).tags.add("wood")
    radio = ItemFactory.create(name="Claw radio", category=electronics)
    radio.tags.add("metal")

    response = admin_client.get(
        reverse("stuff:item-list"),
        {"query": "claw", "category": tools.pk, "tag": "metal"},
        headers=RESULTS_HEADERS,
    )

    assert list(response.context["items"]) == [hammer]
    assert response.context["active_tag"].name == "metal"
    assert response.context["page_obj"].number == 1


def test_tag_click_replaces_the_active_tag_and_keeps_other_filters(
    admin_client,
    category_factory,
):
    tools = category_factory(name="Tools")
    for index in range(12):
        item = ItemFactory.create(name=f"Item {index:02}", category=tools)
        item.tags.add("common", "metal")

    response = admin_client.get(
        reverse("stuff:item-list"),
        {"category": tools.pk, "tag": "common", "page": 2},
        headers=RESULTS_HEADERS,
    )
    assert response.context["page_obj"].number == 2
    page = parse_html(response.content)

    (active_link,) = page.find("a", title="Remove tag filter: common")
    assert query(active_link) == {"category": [str(tools.pk)], "page": ["1"]}
    (active_badge,) = (
        span
        for span in page.find("span")
        if span.text == "common" and "badge-primary" in span.attrs.get("class", "").split()
    )
    assert active_badge

    (metal_link,) = (link for link in tag_links(page) if query(link)["tag"] == ["metal"])
    assert query(metal_link) == {
        "category": [str(tools.pk)],
        "tag": ["metal"],
        "page": ["1"],
    }

    response = admin_client.get(metal_link.attrs["href"], headers=CONTENT_HEADERS)
    assert response.status_code == 200
    assert response.context["active_tag"].name == "metal"
    assert response.context["page_obj"].number == 1
    assert all("metal" in item.tags.names() for item in response.context["items"])
    filtered_page = parse_html(response.content)
    assert filtered_page.field("tag").attrs["value"] == "metal"
    assert {"query", "category", "tag"} <= filtered_page.field_names()


def test_clicking_the_active_tag_clears_it(admin_client, category_factory):
    tools = category_factory(name="Tools")
    for index in range(12):
        item = ItemFactory.create(name=f"Item {index:02}", category=tools)
        item.tags.add("metal")

    response = admin_client.get(
        reverse("stuff:item-list"),
        {"category": tools.pk, "tag": "metal", "page": 2},
        headers=RESULTS_HEADERS,
    )
    page = parse_html(response.content)
    (active_link,) = page.find("a", title="Remove tag filter: metal")

    response = admin_client.get(active_link.attrs["href"], headers=CONTENT_HEADERS)
    assert response.status_code == 200
    assert response.context["active_tag"] is None
    assert response.context["page_obj"].number == 1
    assert response.context["page_obj"].paginator.count == 12
    assert Item.objects.filter(tags__name="metal").count() == 12


def test_tag_filter_round_trips_hostile_tag_names(admin_client):
    tag_name = "parts & café+#"
    item = ItemFactory.create(name="Matching item")
    item.tags.add(tag_name)
    ItemFactory.create(name="Unrelated item")

    response = admin_client.get(reverse("stuff:item-list"), headers=RESULTS_HEADERS)
    page = parse_html(response.content)
    (link,) = tag_links(page)
    assert query(link) == {"tag": [tag_name], "page": ["1"]}

    response = admin_client.get(link.attrs["href"], headers=RESULTS_HEADERS)
    assert [obj.pk for obj in response.context["items"]] == [item.pk]
    assert response.context["active_tag"].name == tag_name


def test_active_tag_stays_visible_when_outside_the_top_n(admin_client):
    for index in range(12):
        item = ItemFactory.create(name=f"Popular {index:02}")
        item.tags.add("popular")
    for index in range(10):
        item = ItemFactory.create(name=f"Other {index:02}")
        item.tags.add(f"other-{index:02}")
    rare = ItemFactory.create(name="Rare item")
    rare.tags.add("rare")

    response = admin_client.get(
        reverse("stuff:item-list"),
        {"tag": "rare"},
        headers=RESULTS_HEADERS,
    )

    top_tags = [tag.name for tag in response.context["top_tags"]]
    assert top_tags[0] == "rare"
    assert "popular" in top_tags
    assert len(top_tags) == 11
    page = parse_html(response.content)
    (active_link,) = page.find("a", title="Remove tag filter: rare")
    assert query(active_link) == {"page": ["1"]}
