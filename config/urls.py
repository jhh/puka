from __future__ import annotations

from django.conf import settings
from django.contrib import admin
from django.urls import include
from django.urls import path
from django.urls import URLPattern
from django.urls import URLResolver

from puka.bookmarks.views import bookmarks

urlpatterns: list[URLPattern | URLResolver] = [
    path("", bookmarks, name="bookmarks"),
    path("admin/", admin.site.urls),
]


if "debug_toolbar" in settings.INSTALLED_APPS:
    import debug_toolbar

    urlpatterns = [*urlpatterns, path("__debug__/", include(debug_toolbar.urls))]
