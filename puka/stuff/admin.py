# Register your models here.
from __future__ import annotations

from django.contrib import admin
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

from puka.stuff.models import Category, InventoryTransaction, Location, Product


@admin.register(Location)
class LocationAdmin(TreeAdmin):
    form = movenodeform_factory(Location)


admin.site.register(Category)
admin.site.register(Product)
admin.site.register(InventoryTransaction)
