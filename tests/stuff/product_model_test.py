import pytest
from django.db import models

from puka.stuff.models import Location, Product


@pytest.fixture
def location():
    root = Location.add_root(name="A01")
    return Location.objects.get(pk=root.pk).add_child(name="A01-02")


def create_product(name, notes, location):
    return Product.objects.create(
        name=name,
        current_stock=0,
        reorder_level=0,
        location=location,
        notes=notes,
    )


@pytest.mark.django_db
def test_with_text_returns_queryset(location):
    create_product("Test Product", "Some notes", location)
    qs = Product.objects.with_text("Test")
    assert isinstance(qs, models.QuerySet)


@pytest.mark.django_db
def test_with_text_filters_correctly(location):
    create_product("Python Tutorial", "A description", location)
    create_product("Django Guide", "Another description", location)
    create_product("JavaScript Basics", "Yet another description", location)

    qs = Product.objects.with_text("Python")
    results = list(qs)

    assert qs.count() == 1
    assert results[0].name == "Python Tutorial"


@pytest.mark.django_db
def test_with_text_orders_by_rank(location):
    create_product("Advanced Python", "Deep Dive into Python", location)
    create_product("Python Programming", "Learn Programming", location)
    create_product("Programming Basics", "Introduction to Python", location)

    qs = Product.objects.with_text("Python")
    results = list(qs)

    assert len(results) == 3
    assert results[0].name == "Advanced Python"
    assert results[1].name == "Python Programming"
    assert results[2].name == "Programming Basics"


@pytest.mark.django_db
def test_with_locations_filters_correctly(location):
    create_product("Advanced Python", "A01", location)
    create_product("Python Programming", "A01-02", location)
    create_product("Programming Basics", "Introduction to Python", location)

    qs = Product.objects.with_text("A01-02")
    results = list(qs)

    assert len(results) == 1
    assert results[0].name == "Python Programming"


@pytest.mark.django_db
def test_with_locations_orders_by_rank(location):
    create_product("Advanced Python", "A01", location)
    create_product("Python Programming", "A01-02", location)
    create_product("Programming Basics", "Introduction to Python", location)

    qs = Product.objects.with_text("A01")
    results = list(qs)

    assert len(results) == 2
    assert results[0].name == "Advanced Python"
    assert results[1].name == "Python Programming"


@pytest.mark.django_db
def test_search_returns_queryset(location):
    create_product("Test Product", "Some notes", location)
    qs = Product.objects.search("Test")
    assert isinstance(qs, models.QuerySet)


@pytest.mark.django_db
def test_search_filters_text_correctly(location):
    create_product("Python Tutorial", "A description", location)
    create_product("Django Guide", "Another description", location)
    create_product("JavaScript Basics", "Yet another description", location)

    qs = Product.objects.search("Python")
    results = list(qs)

    assert len(results) == 1
    assert results[0].name == "Python Tutorial"


@pytest.mark.django_db
def test_search_filters_tags_correctly(location):
    p = create_product("Python Tutorial", "A description", location)
    p.tags.add("python")
    p = create_product("Django Guide", "Another description", location)
    p.tags.add("python", "django")
    p = create_product("JavaScript Basics", "Yet another description", location)
    p.tags.add("javascript")

    qs = Product.objects.search("#python")
    results = list(qs)

    assert len(results) == 2
    assert any(result.name == "Python Tutorial" for result in results)
    assert any(result.name == "Django Guide" for result in results)


@pytest.mark.django_db
def test_search_tags_are_case_and_whitespace_insensitive(location):
    p = create_product("Python Tutorial", "A description", location)
    p.tags.add("python")
    p = create_product("Django Guide", "Another description", location)
    p.tags.add("python", "django")

    qs = Product.objects.search(" #Python")
    results = list(qs)

    assert len(results) == 2
    assert any(result.name == "Python Tutorial" for result in results)
    assert any(result.name == "Django Guide" for result in results)


@pytest.mark.django_db
def test_search_locations_filter_correctly(location):
    # A01-02
    create_product("AAA", "BBB", location)
    # A01-03
    location = Location.objects.get(pk=location.pk).add_sibling(name="A01-03")
    create_product("CCC", "DDD", location)
    # A02-01
    location = Location.objects.get(pk=location.pk).add_sibling(name="A02-01")
    create_product("EEE", "FFF", location)

    qs = Product.objects.search("@A01")
    results = list(qs)

    assert len(results) == 2
    assert any(result.name == "AAA" for result in results)
    assert any(result.name == "CCC" for result in results)


@pytest.mark.django_db
def test_search_locations_are_case_insensitive(location):
    # A01-02
    create_product("AAA", "BBB", location)
    # A01-03
    location = Location.objects.get(pk=location.pk).add_sibling(name="A01-03")
    create_product("CCC", "DDD", location)
    # A02-01
    location = Location.objects.get(pk=location.pk).add_sibling(name="A02-01")
    create_product("EEE", "FFF", location)

    qs = Product.objects.search("@a02-01")
    results = list(qs)

    assert len(results) == 1
    assert results[0].name == "EEE"
