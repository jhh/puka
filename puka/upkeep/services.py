from django.db.models import Sum

from puka.stuff.models import Item
from puka.upkeep.models import TaskItem


def item_quantity_needed(item: Item) -> int:
    result = TaskItem.objects.filter(item=item).aggregate(total=Sum("quantity"))
    return result["total"] or 0
