from __future__ import annotations

import pytest
from faker import Faker
from pytest_factoryboy import register

from puka.bookmarks.models import Bookmark
from puka.stuff.forms import ItemForm

from .factories import BookmarkFactory, ItemFactory, ItemWithInventoryFactory, LocationFactory


def create_bookmark(
    title: str,
    description: str = "description",
    url: str = "http://example.com",
    tags: list[str] | None = None,
) -> Bookmark:
    if tags is None:
        tags = ["foo", "bar"]
    bookmark = Bookmark(
        title=title,
        description=description,
        url=url,
    )
    bookmark.save()
    bookmark.tags.set(tags)
    return bookmark


@pytest.fixture
def succulents_bookmark():
    return create_bookmark(
        title="Hexagon bespoke succulents",
        description="Tumeric tumblr poutine.",
        url="https://hipsum.co/kombucha",
        tags=["thundercats", "humblebrag"],
    )


@pytest.fixture
def typewriter_bookmark():
    return create_bookmark(
        title="Tote bag typewriter aesthetic",
        description="Before they sold out.",
        url="https://normcore.org/?q=shaman",
        tags=["banjo", "thundercats"],
    )


@pytest.fixture
def flannel_bookmark():
    return create_bookmark(
        title="Flannel four dollar toast",
        description=" Kale chips aesthetic.",
        url="https://organic.com/",
        tags=["artisan", "banjo"],
    )


@pytest.fixture
def all_bookmarks(
    succulents_bookmark,
    typewriter_bookmark,
    flannel_bookmark,
):
    return [
        succulents_bookmark,
        typewriter_bookmark,
        flannel_bookmark,
    ]


@pytest.fixture
def unsaved_bookmark() -> Bookmark:
    return Bookmark(title="unsaved bookmark", url="http://example.com")


register(BookmarkFactory)

register(LocationFactory)

register(ItemFactory)
register(ItemFactory, "filter_item", name="Water Filter", notes="Purifies water")
register(ItemFactory, "salt_item", name="Water Softener Salt", notes="Yellow bag")
register(ItemFactory, "container_item", name="Deli Container", notes="Also holds water")

register(ItemWithInventoryFactory)


@pytest.fixture
def items(filter_item, salt_item, container_item):
    return [
        filter_item,
        salt_item,
        container_item,
    ]


@pytest.fixture
def item_form_data(location):
    faker = Faker()
    return {
        "name": faker.sentence(),
        "notes": faker.paragraph(),
        "tags": ",".join(faker.words(nb=3)),
        "reorder_level": 3,
        "location_code": location.code,
        "quantity": 10,
        "bookmark_url": faker.url(),
    }


@pytest.fixture
def item_form(item_form_data):
    return ItemForm(data=item_form_data)
