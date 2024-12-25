from __future__ import annotations

import logging

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Case, Count, Value, When
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_http_methods, require_POST
from django_htmx.http import HttpResponseLocation, trigger_client_event

from .filters import BookmarkFilter
from .forms import BookmarkForm
from .models import Bookmark

logger = logging.getLogger(__name__)


@login_required
@require_GET
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

    # if htmx and paging, just render the li template, otherwise this is a htmx navigation to the list
    # search box on the main bookmarks page fakes a non-int page to force the li template
    if request.htmx:
        template = (
            "bookmarks/list.html#list-items-partial"
            if page_number
            else "bookmarks/list.html#list-partial"
        )
    else:
        template = "bookmarks/list.html"

    response = render(request, template, {"page_obj": page_obj})
    return trigger_client_event(response, "clearSearch", {}) if clear_search else response


@login_required
@require_GET
def bookmarks_filter(request):
    f = BookmarkFilter(request.GET, queryset=Bookmark.objects.prefetch_related("tags"))
    paginator = Paginator(f.qs, 25)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    if request.htmx:
        # if paging, just render the list items, otherwise this is a navigation to the list page contents
        template = (
            "bookmarks/list.html#list-items-partial"
            if page_number
            else "bookmarks/filter.html#filter-partial"
        )
    else:
        template = "bookmarks/filter.html"

    logger.debug("template: %s", template)
    return render(request, template, {"page_obj": page_obj, "filter": f})


@login_required
def bookmark_detail(request, pk):
    bookmark = get_object_or_404(Bookmark, pk=pk)
    return render(request, "bookmarks/detail.html", {"bookmark": bookmark})


@login_required
@require_http_methods(["GET", "POST"])
def bookmark_new(request):
    if request.method == "GET":
        form = BookmarkForm()
        return render(
            request,
            "bookmarks/form.html#form-partial" if request.htmx else "bookmarks/form.html",
            {"form": form, "title": "New Bookmark"},
        )

    if request.method == "POST":
        form = BookmarkForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseLocation(reverse("bookmarks:list"), target="#id_content")
        return render(request, "bookmarks/form.html", {"form": form, "title": "New Bookmark"})

    return None


@login_required
@require_http_methods(["GET", "POST"])
def bookmark_edit(request, pk):
    bookmark = get_object_or_404(Bookmark, pk=pk)

    if request.method == "GET":
        form = BookmarkForm(instance=bookmark)
        return render(
            request,
            "bookmarks/form.html#form-partial" if request.htmx else "bookmarks/form.html",
            {"form": form, "title": "Edit Bookmark"},
        )

    if request.method == "POST":
        form = BookmarkForm(request.POST, instance=bookmark)
        if form.is_valid():
            form.save()
            return HttpResponseLocation(reverse("bookmarks:list"), target="#id_content")
        return render(request, "bookmarks/form.html", {"form": form, "title": "Edit Bookmark"})

    return None


@login_required
@require_POST
def bookmark_delete(_request, pk):
    bookmark = get_object_or_404(Bookmark, pk=pk)
    logger.debug("delete: Bookmark %s", bookmark)
    bookmark.delete()
    return HttpResponseLocation(reverse("bookmarks:list"), target="#id_content")


@login_required
@require_GET
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
    return render(
        request,
        "bookmarks/tags.html#tags-partial" if request.htmx else "bookmarks/tags.html",
        {"tags": tags},
    )
