from django.contrib import admin

from .models import Bookmark


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "url",
        "tags",
        "created_at",
    )
    list_filter = ("created_at",)
    date_hierarchy = "created_at"
    exclude = ("title_description_search",)
