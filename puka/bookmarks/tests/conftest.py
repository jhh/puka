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
    return Bookmark(
        title=title,
        description=description,
        url=url,
        tags=tags,
    )


@pytest.fixture
def hipsum_bookmark(db):
    bookmark = create_bookmark(
        title="Hexagon bespoke succulents",
        description="Tumeric tumblr poutine",
        url="https://hipsum.co/",
        tags=["thundercats", "humblebrag"],
    )
    bookmark.save()
    return bookmark


@pytest.fixture
def basic_bookmark() -> Bookmark:
    return create_bookmark("basic bookmark")
