from __future__ import annotations

from django.contrib import admin

from .models import Bookmark


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "url",
        "tags",
        "created",
        "modified",
    )
    list_filter = ("created", "modified")
    date_hierarchy = "created"
