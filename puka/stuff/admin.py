# Register your models here.
from __future__ import annotations

from django.contrib import admin
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

from puka.stuff.models import Category, Inventory, Item, Location


@admin.register(Location)
class LocationAdmin(TreeAdmin):
    form = movenodeform_factory(Location)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)


admin.site.register(Item)
admin.site.register(Inventory)
