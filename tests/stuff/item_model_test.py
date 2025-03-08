import pytest
from django.db import models

from puka.stuff.models import Inventory, Item, Location


@pytest.fixture
def location():
    root = Location.add_root(name="A01", code="A01")
    return Location.objects.get(pk=root.pk).add_child(name="A01-02", code="A01-02")


def create_item(name, notes, location):
    item = Item.objects.create(
        name=name,
        reorder_level=0,
        notes=notes,
    )
    Inventory.objects.create(item=item, location=location, quantity=1)
    return item


@pytest.mark.django_db
def test_with_text_returns_queryset(location):
    create_item("Test Item", "Some notes", location)
    qs = Item.objects.with_text("Test")
    assert isinstance(qs, models.QuerySet)


@pytest.mark.django_db
def test_with_text_filters_correctly(location):
    create_item("Python Tutorial", "A description", location)
    create_item("Django Guide", "Another description", location)
    create_item("JavaScript Basics", "Yet another description", location)

    qs = Item.objects.with_text("Python")
    results = list(qs)

    assert qs.count() == 1
    assert results[0].name == "Python Tutorial"


@pytest.mark.django_db
def test_with_text_orders_by_rank(location):
    create_item("Advanced Python", "Deep Dive into Python", location)
    create_item("Python Programming", "Learn Programming", location)
    create_item("Programming Basics", "Introduction to Python", location)

    qs = Item.objects.with_text("Python")
    results = list(qs)

    assert len(results) == 3
    assert results[0].name == "Advanced Python"
    assert results[1].name == "Python Programming"
    assert results[2].name == "Programming Basics"


@pytest.mark.django_db
def test_with_locations_filters_correctly(location):
    create_item("Advanced Python", "A01", location)
    create_item("Python Programming", "A01-02", location)
    create_item("Programming Basics", "Introduction to Python", location)

    qs = Item.objects.with_text("A01-02")
    results = list(qs)

    assert len(results) == 1
    assert results[0].name == "Python Programming"


@pytest.mark.django_db
def test_with_locations_orders_by_rank(location):
    create_item("Advanced Python", "A01", location)
    create_item("Python Programming", "A01-02", location)
    create_item("Programming Basics", "Introduction to Python", location)

    qs = Item.objects.with_text("A01")
    results = list(qs)

    assert len(results) == 2
    assert results[0].name == "Advanced Python"
    assert results[1].name == "Python Programming"


@pytest.mark.django_db
def test_search_returns_queryset(location):
    create_item("Test Item", "Some notes", location)
    qs = Item.objects.search("Test")
    assert isinstance(qs, models.QuerySet)


@pytest.mark.django_db
def test_search_filters_text_correctly(location):
    create_item("Python Tutorial", "A description", location)
    create_item("Django Guide", "Another description", location)
    create_item("JavaScript Basics", "Yet another description", location)

    qs = Item.objects.search("Python")
    results = list(qs)

    assert len(results) == 1
    assert results[0].name == "Python Tutorial"


@pytest.mark.django_db
def test_search_filters_tags_correctly(location):
    p = create_item("Python Tutorial", "A description", location)
    p.tags.add("python")
    p = create_item("Django Guide", "Another description", location)
    p.tags.add("python", "django")
    p = create_item("JavaScript Basics", "Yet another description", location)
    p.tags.add("javascript")

    qs = Item.objects.search("#python")
    results = list(qs)

    assert len(results) == 2
    assert any(result.name == "Python Tutorial" for result in results)
    assert any(result.name == "Django Guide" for result in results)


@pytest.mark.django_db
def test_search_tags_are_case_and_whitespace_insensitive(location):
    p = create_item("Python Tutorial", "A description", location)
    p.tags.add("python")
    p = create_item("Django Guide", "Another description", location)
    p.tags.add("python", "django")

    qs = Item.objects.search(" #Python")
    results = list(qs)

    assert len(results) == 2
    assert any(result.name == "Python Tutorial" for result in results)
    assert any(result.name == "Django Guide" for result in results)


@pytest.mark.django_db
def test_search_locations_filter_correctly(location):
    # A01-02
    create_item("AAA", "BBB", location)
    # A01-03
    location = Location.objects.get(pk=location.pk).add_sibling(name="AAA-01-03", code="A01-03")
    create_item("CCC", "DDD", location)
    # A02-01
    location = Location.objects.get(pk=location.pk).add_sibling(name="A02-01", code="A02-01")
    create_item("EEE", "FFF", location)

    qs = Item.objects.search("@A01")
    results = list(qs)

    assert len(results) == 2
    assert any(result.name == "AAA" for result in results)
    assert any(result.name == "CCC" for result in results)


@pytest.mark.django_db
def test_search_locations_are_case_insensitive(location):
    # A01-02
    create_item("AAA", "BBB", location)
    # A01-03
    location = Location.objects.get(pk=location.pk).add_sibling(name="A01-03", code="A01-03")
    create_item("CCC", "DDD", location)
    # A02-01
    location = Location.objects.get(pk=location.pk).add_sibling(name="AAA-02-01", code="A02-01")
    create_item("EEE", "FFF", location)

    qs = Item.objects.search("@a02-01")
    results = list(qs)

    assert len(results) == 1
    assert results[0].name == "EEE"


@pytest.mark.django_db
def test_search_blank_returns_all_items(location):
    create_item("AAA", "BBB", location)
    create_item("CCC", "DDD", location)
    create_item("EEE", "FFF", location)

    qs = Item.objects.search("  ")
    results = list(qs)

    assert len(results) == 3


@pytest.mark.django_db
def test_search_empty_returns_all_items(location):
    create_item("AAA", "BBB", location)
    create_item("CCC", "DDD", location)

    qs = Item.objects.search("")
    results = list(qs)

    assert len(results) == 2


@pytest.mark.django_db
def test_search_location_sorted_by_name(location):
    # Z02-11
    location = Location.objects.get(pk=location.pk).add_sibling(name="Z02-11", code="Z02-11")
    create_item("EEE", "", location)
    # Z02-02
    location = Location.objects.get(pk=location.pk).add_sibling(name="Z02-02", code="Z02-02")
    create_item("CCC", "", location)
    # Z02-01
    location = Location.objects.get(pk=location.pk).add_sibling(name="Z02-01", code="Z02-01")
    create_item("ZZZ", "", location)

    qs = Item.objects.search("@Z")
    results = list(qs)

    assert len(results) == 3
    assert results[0].name == "ZZZ"
    assert results[1].name == "CCC"
    assert results[2].name == "EEE"
