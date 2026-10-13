# Register your models here.
from __future__ import annotations

from django.contrib import admin

from puka.upkeep.models import Area, Schedule, Task


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ("name", "location")
    list_select_related = ("location",)


admin.site.register(Task)
admin.site.register(Schedule)
