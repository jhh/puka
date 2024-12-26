from __future__ import annotations

from django.conf import settings
from django.contrib import admin
from django.urls import URLPattern, URLResolver, include, path
from django.views.generic import RedirectView

urlpatterns: list[URLPattern | URLResolver] = [
    path("", RedirectView.as_view(url="/bookmarks/", permanent=False)),
    path("bookmarks/", include("puka.bookmarks.urls", namespace="bookmarks")),
    path("stuff/", include("puka.stuff.urls", namespace="stuff")),
    path("upkeep/", include("puka.upkeep.urls", namespace="upkeep")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("users/", include("puka.users.urls")),
    path("admin/", admin.site.urls),
]


if "debug_toolbar" in settings.INSTALLED_APPS:  # pragma: no cover
    import debug_toolbar

    urlpatterns = [*urlpatterns, path("__debug__/", include(debug_toolbar.urls))]
