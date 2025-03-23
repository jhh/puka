import logging

from django.db import transaction

from puka.stuff.models import Location

logger = logging.getLogger(__name__)


def adjust_inventory_quantity(inventory, quantity):
    """
    Adjust the quantity of an inventory item by the specified amount.

    Args:
        inventory: The inventory object to adjust
        quantity: The amount to adjust by (positive to add, negative to subtract)

    Raises:
        ValueError: If the adjustment would result in a negative inventory quantity

    Returns:
        None

    Note:
        The adjustment is performed within a database transaction to ensure atomicity.

    """
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


MIN_LOCATION_CODE_SEGMENTS = 2


def parse_location_code(code: str) -> tuple[str, str]:
    """
    Parse a location code into its parent and child components.

    Args:
        code: A string containing a hyphen-separated location code

    Returns:
        A tuple containing (parent_code, child_segment)

    Raises:
        ValueError: If any segment is empty or if the code contains less than the
                   minimum required number of segments

    """
    parts = code.split("-")

    if any(part.strip() == "" for part in parts):
        msg = "empty location code segment"
        raise ValueError(msg)

    if len(parts) < MIN_LOCATION_CODE_SEGMENTS:
        msg = "root location code"
        raise ValueError(msg)

    if len(parts) == MIN_LOCATION_CODE_SEGMENTS:
        return parts[0], parts[1]

    return "-".join(parts[:-1]), parts[-1]


def get_or_create_location(code: str) -> tuple[Location, bool]:
    """
    Get or create a location with the given location code.

    Args:
        code: The code of the location

    Returns:
        A tuple containing the location object and a boolean indicating if the location was created

    Raises:
        ValueError: If the location code is invalid
        Location.DoesNotExist: If the parent location does not exist

    """
    try:
        return Location.objects.get(code=code), False
    except Location.DoesNotExist:
        parent_code, _ = parse_location_code(code)
        parent = Location.objects.get(code=parent_code)
        child = parent.add_child(name=code, code=code)
        return Location.objects.get(pk=child.pk), True
