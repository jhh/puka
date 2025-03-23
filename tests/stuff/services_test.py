import pytest

from puka.stuff.models import Inventory, Item, Location
from puka.stuff.services import (
    adjust_inventory_quantity,
    get_or_create_location,
    parse_location_code,
)


@pytest.mark.django_db
def test_receive(location):
    item = Item.objects.create(name="Stuff", reorder_level=0)
    inventory = Inventory.objects.create(item=item, location=location, quantity=1)
    adjust_inventory_quantity(inventory, 2)

    inventory.refresh_from_db()
    assert inventory.quantity == 3


@pytest.mark.django_db
def test_consume(location):
    item = Item.objects.create(name="Stuff", reorder_level=0)
    inventory = Inventory.objects.create(item=item, location=location, quantity=1)
    adjust_inventory_quantity(inventory, -1)

    inventory.refresh_from_db()
    assert inventory.quantity == 0


@pytest.mark.django_db
def test_inventory_negative(location):
    item = Item.objects.create(name="Stuff", reorder_level=0)
    inventory = Inventory.objects.create(item=item, location=location, quantity=1)
    with pytest.raises(ValueError, match="-3"):
        adjust_inventory_quantity(inventory, -4)

    inventory.refresh_from_db()
    assert inventory.quantity == 1


@pytest.mark.parametrize(
    ("test_input", "parent", "child"),
    [
        ("S-B01", "S", "B01"),
        ("S-C01-02", "S-C01", "02"),
        ("S-C01-02-Z", "S-C01-02", "Z"),
    ],
)
def test_parse_location_code(test_input, parent, child):
    assert parse_location_code(test_input) == (parent, child)


EMPTY_LOCATION_CODE = "empty location code segment"
ROOT_LOCATION_CODE = "root location code"


@pytest.mark.parametrize(
    ("test_input", "exception_msg"),
    [
        ("", EMPTY_LOCATION_CODE),
        ("-", EMPTY_LOCATION_CODE),
        ("S", ROOT_LOCATION_CODE),
        ("S-", EMPTY_LOCATION_CODE),
        ("-S", EMPTY_LOCATION_CODE),
        ("-S-", EMPTY_LOCATION_CODE),
        ("S--", EMPTY_LOCATION_CODE),
        ("S- -", EMPTY_LOCATION_CODE),
        ("S-C01-", EMPTY_LOCATION_CODE),
        ("S-C01-02--", EMPTY_LOCATION_CODE),
    ],
)
def test_parse_location_code_invalid_input(test_input, exception_msg):
    with pytest.raises(ValueError, match=exception_msg):
        parse_location_code(test_input)


@pytest.mark.django_db
def test_get_or_create_location_parent_exists():
    with pytest.raises(Location.DoesNotExist):
        get_or_create_location("S-C01-02")


@pytest.mark.django_db
def test_get_or_create_location_code_valid():
    with pytest.raises(ValueError, match="empty location code segment"):
        get_or_create_location("S--C01-02-03")


@pytest.mark.django_db
@pytest.mark.usefixtures("location")  # load "A01-02" fixture
@pytest.mark.parametrize(
    ("test_input", "parent_code", "expected_created"),
    [
        ("A01-02", "A01", False),
        ("A01-03", "A01", True),
        ("A01-02-01", "A01-02", True),
    ],
)
def test_get_or_create_location(test_input, parent_code, expected_created):
    location, created = get_or_create_location(test_input)

    assert isinstance(location, Location)
    assert location.name == test_input
    assert location.code == test_input
    assert expected_created == created
    assert Location.objects.get(code=parent_code) == location.get_parent()
