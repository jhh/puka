from __future__ import annotations

from django.conf import settings


def tailwind_css(request):
    return {
        "TAILWIND_CSS": settings.TAILWIND_CSS,
    }
