from __future__ import annotations

from django.urls import URLPattern, URLResolver, path

from .views import (
    bookmark_delete,
    bookmark_detail,
    bookmark_edit,
    bookmark_new,
    bookmarks,
    bookmarks_filter,
    tags_list,
)

urlpatterns: list[URLPattern | URLResolver] = [
    path("", bookmarks, name="bookmarks"),
    path("<int:pk>/", bookmark_detail, name="bookmark-detail"),
    path("new/", bookmark_new, name="bookmark-new"),
    path("<int:pk>/edit/", bookmark_edit, name="bookmark-edit"),
    path("<int:pk>/delete/", bookmark_delete, name="bookmark-delete"),
    path("filter/", bookmarks_filter, name="bookmark-filter"),
    path("tags/", tags_list, name="bookmark-tags"),
]
