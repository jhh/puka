from __future__ import annotations

from django.urls import URLPattern, URLResolver, path

from .views import (
    bookmark_create,
    bookmark_delete,
    bookmark_detail,
    bookmark_edit,
    bookmark_new,
    bookmark_update,
    bookmarks,
    bookmarks_filter,
)

urlpatterns: list[URLPattern | URLResolver] = [
    path("", bookmarks, name="bookmarks"),
    path("<int:pk>/", bookmark_detail, name="bookmark-detail"),
    path("new/", bookmark_new, name="bookmark-new"),
    path("<int:pk>/edit/", bookmark_edit, name="bookmark-edit"),
    path("<int:pk>/delete/", bookmark_delete, name="bookmark-delete"),
    #
    #
    #
    #
    path(
        "<int:pk>/delete/",
        bookmark_detail,
        {"template_name": "bookmarks/bookmark_confirm_delete.html"},
        name="bookmark-delete",
    ),
    path("filter/", bookmarks_filter, name="bookmark-filter"),
    path("new/", bookmark_create, name="bookmark-create"),
    path("edit/<int:pk>/", bookmark_update, name="bookmark-update"),
]
