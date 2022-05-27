from __future__ import annotations

import pytest
from django.utils import timezone

from ..models import Bookmark


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
        title=title, description=description, url=url, tags=tags, created=ts, modified=ts
    )


@pytest.fixture
def bookmark_A() -> Bookmark:
    return create_bookmark("A")


def test_something(db, bookmark_A: Bookmark):
    bookmark_A.save()
    assert Bookmark.objects.all().count() == 1


def test_str(bookmark_A):
    assert bookmark_A.__str__() == bookmark_A.title
