from __future__ import annotations

import pytest
from django.utils import timezone

from puka.bookmarks.models import Bookmark


def create_bookmark(
    title: str,
    description: str = "description",
    url: str = "http://example.com",
    tags: list[str] | None = None,
) -> Bookmark:
    if tags is None:
        tags = ["foo", "bar"]
    ts = timezone.now()
    return Bookmark(
        title=title,
        description=description,
        url=url,
        tags=tags,
        created=ts,
        modified=ts,
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
