from __future__ import annotations

from django.urls import URLPattern, URLResolver, path

from .views import bookmark_create, bookmark_update, bookmarks, bookmarks_filter

urlpatterns: list[URLPattern | URLResolver] = [
    path("", bookmarks, name="bookmarks"),
    path("filter/", bookmarks_filter, name="bookmark-filter"),
    path("new/", bookmark_create, name="bookmark-create"),
    path("edit/<int:pk>/", bookmark_update, name="bookmark-update"),
]
