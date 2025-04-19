import pytest
from django.core import serializers
from django.db import models

from puka.bookmarks.models import Bookmark
from puka.stuff.models import Item


@pytest.mark.django_db
def test_with_text_returns_queryset(filter_item):
    qs = Item.objects.with_text("Filter")
    assert isinstance(qs, models.QuerySet)


@pytest.mark.django_db
def test_with_text_filters_correctly(filter_item, salt_item, container_item):
    qs = Item.objects.with_text("Salt")
    results = list(qs)

    assert qs.count() == 1
    assert results[0].name == salt_item.name


@pytest.mark.django_db
def test_with_text_orders_by_rank(filter_item, salt_item, container_item):
    qs = Item.objects.with_text("water")
    results = list(qs)

    assert len(results) == 3
    assert results[0].name == filter_item.name
    assert results[1].name == salt_item.name
    assert results[2].name == container_item.name


@pytest.mark.django_db
def test_item_with_inventory(item_with_inventory_factory):
    item = item_with_inventory_factory(inventory__quantity=5)
    assert item.inventories.first().quantity == 5


@pytest.mark.django_db
def test_search_returns_queryset(salt_item):
    qs = Item.objects.search("Salt")
    assert isinstance(qs, models.QuerySet)


@pytest.mark.django_db
def test_search_filters_text_correctly(filter_item, salt_item, container_item):
    qs = Item.objects.search("Yellow")
    results = list(qs)

    assert len(results) == 1
    assert results[0].name == salt_item.name


@pytest.mark.django_db
def test_search_filters_tags_correctly(filter_item, salt_item, container_item):
    filter_item.tags.add("python")
    salt_item.tags.add("python", "django")
    container_item.tags.add("javascript")

    qs = Item.objects.search("#python")
    results = list(qs)

    assert len(results) == 2
    assert any(result.name == filter_item.name for result in results)
    assert any(result.name == salt_item.name for result in results)


@pytest.mark.django_db
def test_search_tags_are_case_and_whitespace_insensitive(filter_item, salt_item):
    filter_item.tags.add("python")
    salt_item.tags.add("python", "django")

    qs = Item.objects.search(" #Python")
    results = list(qs)

    assert len(results) == 2
    assert any(result.name == filter_item.name for result in results)
    assert any(result.name == salt_item.name for result in results)


@pytest.mark.django_db
def test_search_locations_filter_correctly(item_with_inventory_factory, location_factory):
    # A01-02
    item_with_inventory_factory(name="AAA")
    # A01-03
    location = location_factory(name="A01-03", code="A01-03")
    item_with_inventory_factory(name="CCC", inventory__location=location)
    # A02-01
    location = location_factory(name="A02-01", code="A02-01")
    item_with_inventory_factory(inventory__location=location)

    qs = Item.objects.search("@A01")
    results = list(qs)

    assert len(results) == 2
    assert any(result.name == "AAA" for result in results)
    assert any(result.name == "CCC" for result in results)


@pytest.mark.django_db
def test_search_locations_are_case_insensitive(item_with_inventory_factory, location_factory):
    # A01-02
    item_with_inventory_factory()
    # A01-03
    location = location_factory(name="A01-03", code="A01-03")
    item_with_inventory_factory(name="CCC", inventory__location=location)
    # A02-01
    location = location_factory(name="A02-01", code="A02-01")
    item_with_inventory_factory(name="EEE", inventory__location=location)

    qs = Item.objects.search("@a02-01")
    results = list(qs)

    assert len(results) == 1
    assert results[0].name == "EEE"


@pytest.mark.django_db
def test_search_blank_returns_all_items(filter_item, salt_item, container_item):
    qs = Item.objects.search("  ")
    results = list(qs)

    assert len(results) == 3


@pytest.mark.django_db
def test_search_empty_returns_all_items(filter_item, salt_item):
    qs = Item.objects.search("")
    results = list(qs)

    assert len(results) == 2


@pytest.mark.django_db
def test_search_location_sorted_by_name(item_with_inventory_factory, location_factory):
    # Z02-11
    location = location_factory(name="Z02-11", code="Z02-11")
    item_with_inventory_factory(name="EEE", inventory__location=location)
    # Z02-02
    location = location_factory(name="Z02-02", code="Z02-02")
    item_with_inventory_factory(name="CCC", inventory__location=location)
    # Z02-01
    location = location_factory(name="Z02-01", code="Z02-01")
    item_with_inventory_factory(name="ZZZ", inventory__location=location)

    qs = Item.objects.search("@Z")
    results = list(qs)

    assert len(results) == 3
    assert results[0].name == "ZZZ"
    assert results[1].name == "CCC"
    assert results[2].name == "EEE"


@pytest.mark.django_db
def test_deserialize_with_natural_foreign_key(flannel_bookmark, flannel_bookmark_item_json):
    for deserialized_item in serializers.deserialize(
        "json",
        flannel_bookmark_item_json,
        use_natural_foreign_keys=True,
        use_natural_primary_keys=True,
    ):
        deserialized_item.save()

    assert Item.objects.all().count() == 1
    assert Bookmark.objects.all().count() == 1

    item = Item.objects.first()
    assert item
    bookmarks = list(item.bookmarks.all())
    assert len(bookmarks) == 1
    assert bookmarks[0].title == flannel_bookmark.title
    assert bookmarks[0].description == flannel_bookmark.description
    assert bookmarks[0].url == flannel_bookmark.url


@pytest.mark.django_db
def test_item_quantity(inventory_factory, location_factory):
    inventory = inventory_factory()
    item = inventory.item
    assert item.quantity() == 10

    location = location_factory(name="A", code="A")
    inventory_factory(item=item, location=location, quantity=3)

    assert item.quantity() == 13

    location = location_factory(name="B", code="B")
    inventory_factory(item=item, location=location, quantity=5)

    assert item.quantity() == 18
