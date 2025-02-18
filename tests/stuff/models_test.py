import pytest
from django.db import models

from puka.stuff.models import Location, Product


@pytest.fixture
def location():
    return Location.add_root(name="Test Location")


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
