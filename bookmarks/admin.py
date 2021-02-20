from django.contrib import admin

from .models import Bookmark


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "description",
        "url",
        "tags",
        "created_at",
        "title_description_search",
    )
    list_filter = ("created_at",)
    date_hierarchy = "created_at"
