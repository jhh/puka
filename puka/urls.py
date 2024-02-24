from __future__ import annotations

from django.conf import settings
from django.contrib import admin
from django.urls import include
from django.urls import path
from django.urls import URLPattern
from django.urls import URLResolver
from django.views.generic import RedirectView

urlpatterns: list[URLPattern | URLResolver] = [
    path("", RedirectView.as_view(url="/bookmarks/", permanent=False)),
    path("bookmarks/", include("puka.bookmarks.urls")),
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
]


if "debug_toolbar" in settings.INSTALLED_APPS:  # pragma: no cover
    import debug_toolbar

    urlpatterns = [*urlpatterns, path("__debug__/", include(debug_toolbar.urls))]
