from __future__ import annotations

import json

import pytest
from django.core import serializers

from puka.bookmarks.models import Bookmark


def test_str(unsaved_bookmark):
    assert unsaved_bookmark.__str__() == unsaved_bookmark.title


@pytest.mark.django_db
def test_save(unsaved_bookmark):
    unsaved_bookmark.save()
    assert Bookmark.objects.all().count() == 1


@pytest.mark.django_db
def test_ordered(all_bookmarks):
    qs = Bookmark.objects.all()
    assert qs.ordered


@pytest.mark.django_db
def test_with_tags(
    succulents_bookmark,
    typewriter_bookmark,
    flannel_bookmark,
):
    qs = Bookmark.active_objects.with_tags(["artisan"])
    assert len(qs) == 1
    assert qs.contains(flannel_bookmark)

    qs = Bookmark.active_objects.with_tags(["humblebrag"])
    assert len(qs) == 1
    assert qs.contains(succulents_bookmark)

    qs = Bookmark.active_objects.with_tags(["thundercats"])
    assert len(qs) == 2
    assert qs.contains(succulents_bookmark)
    assert qs.contains(typewriter_bookmark)

    qs = Bookmark.active_objects.with_tags(["banjo"])
    assert len(qs) == 2
    assert qs.contains(typewriter_bookmark)
    assert qs.contains(flannel_bookmark)

    qs = Bookmark.active_objects.with_tags(["banjo", "thundercats"])
    assert len(qs) == 3
    assert qs.contains(succulents_bookmark)
    assert qs.contains(typewriter_bookmark)
    assert qs.contains(flannel_bookmark)


@pytest.mark.django_db
def test_with_text(
    succulents_bookmark,
    typewriter_bookmark,
    flannel_bookmark,
):
    qs = Bookmark.active_objects.with_text("tumeric")
    assert len(qs) == 1
    assert qs.contains(succulents_bookmark)


@pytest.mark.django_db
def test_serialize_with_natural_primary_key(typewriter_bookmark, typewriter_json):
    data = serializers.serialize(
        "json",
        [typewriter_bookmark],
        indent=2,
        use_natural_primary_keys=True,
    )
    result = json.loads(data)
    assert result[0]["model"] == typewriter_json[0]["model"]
    assert result[0]["fields"]["title"] == typewriter_json[0]["fields"]["title"]
    assert result[0]["fields"]["description"] == typewriter_json[0]["fields"]["description"]
    assert result[0]["fields"]["url"] == typewriter_json[0]["fields"]["url"]
    assert result[0]["fields"]["active"] == typewriter_json[0]["fields"]["active"]
    assert "pk" not in result[0]
