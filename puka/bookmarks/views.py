from __future__ import annotations

import logging

from django.core.paginator import Paginator
from django.db.models import Case, Count, Value, When
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django_htmx.http import HttpResponseLocation, trigger_client_event

from puka.core.views import get_template

from .filters import BookmarkFilter
from .forms import BookmarkForm
from .models import Bookmark

logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
def bookmarks(request: HttpRequest) -> HttpResponse:
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

    template = get_template(request, "bookmarks/index.html", "#list-items-partial")

    response = render(request, template, {"page_obj": page_obj})
    return trigger_client_event(response, "clearSearch", {}) if clear_search else response


@require_http_methods(["GET"])
def bookmarks_filter(request):
    f = BookmarkFilter(request.GET, queryset=Bookmark.objects.prefetch_related("tags"))
    paginator = Paginator(f.qs, 25)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # if paging, just render the list items, otherwise this is a navigation to the filter page contents
    if request.headers.get("HX-Request"):
        template = (
            "bookmarks/index.html#list-items-partial"
            if page_number
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
def bookmark_new(request):
    if request.method == "GET":
        form = BookmarkForm()
        template = get_template(request, "bookmarks/form.html", "#form-partial")
        return render(request, template, {"form": form, "title": "New Bookmark"})

    if request.method == "POST":
        form = BookmarkForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseLocation(reverse("bookmarks:list"), target="#id_content")
        return render(request, "bookmarks/form.html", {"form": form, "title": "New Bookmark"})

    return HttpResponse()


@require_http_methods(["GET", "POST"])
def bookmark_edit(request, pk):
    bookmark = get_object_or_404(Bookmark, pk=pk)

    if request.method == "GET":
        form = BookmarkForm(instance=bookmark)
        template = get_template(request, "bookmarks/form.html", "#form-partial")
        return render(request, template, {"form": form, "title": "Edit Bookmark"})

    if request.method == "POST":
        form = BookmarkForm(request.POST, instance=bookmark)
        if form.is_valid():
            form.save()
            return HttpResponseLocation(reverse("bookmarks:list"), target="#id_content")
        return render(request, "bookmarks/form.html", {"form": form, "title": "Edit Bookmark"})

    return HttpResponse()


@require_http_methods(["POST"])
def bookmark_delete(_request, pk):
    bookmark = get_object_or_404(Bookmark, pk=pk)
    logger.debug("delete: Bookmark %s", bookmark)
    bookmark.delete()
    return HttpResponseLocation(reverse("bookmarks:list"), target="#id_content")


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
