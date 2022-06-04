from __future__ import annotations

from django.conf import settings
from django.contrib import admin
from django.urls import include
from django.urls import path
from django.urls import URLPattern
from django.urls import URLResolver

from puka.bookmarks.views import bookmark_create
from puka.bookmarks.views import bookmark_update
from puka.bookmarks.views import bookmarks
from puka.bookmarks.views import cancel

urlpatterns: list[URLPattern | URLResolver] = [
    path("", bookmarks, name="bookmarks"),
    path("new/", bookmark_create, name="bookmark-create"),
    path("edit/<int:pk>/", bookmark_update, name="bookmark-update"),
    path("cancel/", cancel, name="bookmark-cancel"),
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
]


if "debug_toolbar" in settings.INSTALLED_APPS:
    import debug_toolbar

    urlpatterns = [*urlpatterns, path("__debug__/", include(debug_toolbar.urls))]
