import pytest

from puka.stuff.models import Inventory, Item
from puka.stuff.services import adjust_inventory_quantity


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
