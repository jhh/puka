from __future__ import annotations

from django.urls import URLPattern, URLResolver, path
from django_filters.views import FilterView

from .models import Bookmark
from .views import bookmark_create, bookmark_update, bookmarks

urlpatterns: list[URLPattern | URLResolver] = [
    path("", bookmarks, name="bookmarks"),
    path(
        "filter/",
        FilterView.as_view(
            model=Bookmark,
            filterset_fields=["title", "url", "active", "created"],
        ),
        name="bookmark-list",
    ),
    path("new/", bookmark_create, name="bookmark-create"),
    path("edit/<int:pk>/", bookmark_update, name="bookmark-update"),
]
