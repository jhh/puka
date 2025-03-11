import logging

from django.db import transaction

logger = logging.getLogger(__name__)


def adjust_inventory_quantity(inventory, quantity):
    adjusted_quantity = inventory.quantity + quantity
    if adjusted_quantity < 0:
        logger.warning(
            'Inventory "%s" quantity cannot be negative: %d (adjustment=%d)',
            inventory,
            adjusted_quantity,
            quantity,
        )
        raise ValueError(adjusted_quantity)

    inventory.quantity = adjusted_quantity
    logger.info(
        'Inventory "%s" (%s) quantity adjusted to %d',
        inventory,
        inventory.location.name,
        adjusted_quantity,
    )

    with transaction.atomic():
        inventory.save()
