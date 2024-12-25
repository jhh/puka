from __future__ import annotations

import pytest

from puka.bookmarks.models import Bookmark


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
