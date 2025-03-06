# Register your models here.
from __future__ import annotations

from django.contrib import admin
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

from puka.stuff.models import Inventory, InventoryTransaction, Item, Location


@admin.register(Location)
class LocationAdmin(TreeAdmin):
    form = movenodeform_factory(Location)


admin.site.register(Item)
admin.site.register(Inventory)
admin.site.register(InventoryTransaction)
