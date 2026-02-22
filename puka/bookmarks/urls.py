from __future__ import annotations

from django.urls import URLPattern, URLResolver, path

from .views import (
    bookmark_create,
    bookmark_delete,
    bookmark_detail,
    bookmark_update,
    bookmarks,
    bookmarks_filter,
    tags_list,
)

app_name = "bookmarks"
urlpatterns: list[URLPattern | URLResolver] = [
    path("", bookmarks, name="list"),
    path("<int:pk>/", bookmark_detail, name="detail"),
    path("new/", bookmark_create, name="new"),
    path("<int:pk>/edit/", bookmark_update, name="edit"),
    path("<int:pk>/delete/", bookmark_delete, name="delete"),
    path("filter/", bookmarks_filter, name="filter"),
    path("tags/", tags_list, name="tags"),
]
