# Register your models here.
from __future__ import annotations

from django.contrib import admin

from puka.stuff.models import Category, InventoryTransaction, Location, Product

admin.site.register(Category)
admin.site.register(Location)
admin.site.register(Product)
admin.site.register(InventoryTransaction)
