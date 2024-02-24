from __future__ import annotations

from django.urls import path
from django.urls import URLPattern
from django.urls import URLResolver

from .views import bookmark_create
from .views import bookmark_update
from .views import bookmarks

urlpatterns: list[URLPattern | URLResolver] = [
    path("", bookmarks, name="bookmarks"),
    path("new/", bookmark_create, name="bookmark-create"),
    path("edit/<int:pk>/", bookmark_update, name="bookmark-update"),
]
