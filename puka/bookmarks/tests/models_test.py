from __future__ import annotations

import pytest

from ..models import Bookmark


@pytest.mark.django_db
def test_something(basic_bookmark):
    basic_bookmark.save()
    assert Bookmark.objects.all().count() == 1


def test_str(basic_bookmark):
    assert basic_bookmark.__str__() == basic_bookmark.title
