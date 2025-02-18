import pytest

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
def test_product_full_text_search(location):
    create_product("Cars", "Boat", location)
    create_product("commodo mollit quis anim aliquip", "boats", location)

    results = Product.objects.with_text("car")
    assert len(results) == 1

    results = Product.objects.with_text("boats")
    assert len(results) == 2
