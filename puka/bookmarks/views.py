from __future__ import annotations

import logging

from django.core.paginator import Paginator
from django.db.models import Case, Count, Value, When
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django_htmx.http import HttpResponseLocation, trigger_client_event

from puka.core.views import get_template, is_htmx_fragment

from .filters import BookmarkFilter
from .forms import BookmarkForm
from .models import Bookmark

logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
def bookmarks(request):
    clear_search = False

    match request.GET:
        case {"tags": tag}:
            bm = Bookmark.active_objects.with_tags([tag])
        case {"q": search} if search.startswith("#"):
            tag = search.lstrip("#")
            bm = Bookmark.active_objects.with_tags([tag])
        case {"q": search} if search.strip():
            bm = Bookmark.active_objects.with_text(search)
        case _:
            bm = Bookmark.active_objects.all()
            clear_search = True

    paginator = Paginator(bm.prefetch_related("tags"), 25)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    if is_htmx_fragment(request):
        # A tag link on the tags page swaps into the whole content block, so it
        # needs the toolbar and list wrapper; search/infinite scroll only want
        # the rows.
        if (request.htmx.target or "").endswith("#content"):
            template = "bookmarks/bookmark_list.html#list-partial"
        else:
            template = "bookmarks/bookmark_list.html#list-items-partial"
    else:
        template = "bookmarks/bookmark_list.html"

    response = render(
        request,
        template,
        {"page_obj": page_obj, "update_breadcrumbs": not page_number},
    )
    return trigger_client_event(response, "clearSearch", {}) if clear_search else response


@require_http_methods(["GET"])
def bookmarks_filter(request):
    f = BookmarkFilter(request.GET, queryset=Bookmark.objects.prefetch_related("tags"))
    paginator = Paginator(f.qs, 25)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Paging and tag clicks replace rows; content navigation includes the filter form.
    if is_htmx_fragment(request):
        template = (
            "bookmarks/bookmark_list.html#rows"
            if (request.htmx.target or "").endswith("#id_bookmarks")
            or (page_number and not (request.htmx.target or "").endswith("#content"))
            else "bookmarks/filter.html#filter-partial"
        )
    else:
        template = "bookmarks/filter.html"

    logger.debug("template: %s", template)
    return render(request, template, {"page_obj": page_obj, "filter": f})


def bookmark_detail(request, pk):
    bookmark = get_object_or_404(Bookmark, pk=pk)
    return render(request, "bookmarks/detail.html", {"bookmark": bookmark})


@require_http_methods(["GET", "POST"])
def bookmark_create(request):
    if request.method == "GET":
        form = BookmarkForm()
        return render(request, "bookmarks/form.html", {"form": form, "title": "New Bookmark"})

    form = BookmarkForm(request.POST)
    if form.is_valid():
        form.save()
        return redirect(reverse("bookmarks:list"))
    return render(request, "bookmarks/form.html", {"form": form, "title": "New Bookmark"})


@require_http_methods(["GET", "POST"])
def bookmark_update(request, pk):
    bookmark = get_object_or_404(Bookmark, pk=pk)

    if request.method == "GET":
        form = BookmarkForm(instance=bookmark)
        template = "bookmarks/form.html"
        return render(request, template, {"form": form, "title": "Edit Bookmark"})

    form = BookmarkForm(request.POST, instance=bookmark)
    if form.is_valid():
        form.save()
        return redirect(reverse("bookmarks:list"))
    return render(request, "bookmarks/form.html", {"form": form, "title": "Edit Bookmark"})


@require_http_methods(["POST"])
def bookmark_delete(_request, pk):
    bookmark = get_object_or_404(Bookmark, pk=pk)
    logger.debug("delete: Bookmark %s", bookmark)
    bookmark.delete()
    return HttpResponseLocation(reverse("bookmarks:list"), target="#content")


@require_http_methods(["GET"])
def tags_list(request):
    tags = Bookmark.tags.annotate(
        num_times=Count(Bookmark.tags.through.tag_relname()),
        bucket=Case(
            When(
                num_times__gt=100,
                then=Value("> 100"),
            ),
            When(
                num_times__gte=50,
                num_times__lte=100,
                then=Value("50—100"),
            ),
            When(
                num_times__gte=10,
                num_times__lt=50,
                then=Value("10—50"),
            ),
            When(
                num_times__gte=5,
                num_times__lt=10,
                then=Value("5—10"),
            ),
            default=Value("< 5"),
        ),
    ).order_by("-num_times")
    template = get_template(request, "bookmarks/tags.html", "#tags-partial")
    return render(request, template, {"tags": tags})
