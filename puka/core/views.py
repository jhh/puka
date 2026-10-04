from django.http import HttpRequest
from django.shortcuts import render
from django_htmx.middleware import HtmxDetails


def is_htmx_fragment(request: HttpRequest) -> bool:
    """Keep boosted, body-targeted and history-restore requests as complete pages."""
    htmx = HtmxDetails(request)
    return (
        bool(htmx)
        and not htmx.boosted
        and not htmx.history_restore_request
        and htmx.target != "body"
    )


def get_template(request: HttpRequest, template: str, partial: str) -> list[str]:
    """
    Return a template path based on request type (full page vs htmx partial).

    Ordinary targeted htmx requests receive the named partial. Boosted navigation
    and history restoration need the full document and application shell.

    """
    if is_htmx_fragment(request):
        template += partial
    return [template]


def view_404(request):
    return render(request, "404.html", status=404)


def overview(request):
    # Imported here: core is imported by the other apps' views.
    from puka.bookmarks.models import Bookmark  # noqa: PLC0415
    from puka.stuff.models import Item  # noqa: PLC0415
    from puka.upkeep.models import Task  # noqa: PLC0415

    counts = {
        "bookmarks": Bookmark.active_objects.count(),
        "items": Item.objects.count(),
        "tasks": Task.objects.count(),
        "tags": Bookmark.tags.count(),
    }
    return render(request, "overview.html", {"counts": counts})
