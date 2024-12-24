from __future__ import annotations

import logging

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import QueryDict
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_http_methods, require_POST
from django_htmx.http import HttpResponseClientRedirect, trigger_client_event

from .filters import BookmarkFilter
from .forms import BookmarkForm
from .models import Bookmark

logger = logging.getLogger(__name__)


@login_required
@require_GET
def bookmarks(request):
    clear_search = True
    query = QueryDict(mutable=True)

    if "t" in request.GET:
        tags = request.GET.getlist("t")
        bookmarks = Bookmark.active_objects.with_tags(tags)
        query.setlist("t", tags)
    elif "q" in request.GET:
        search: str = request.GET.get("q")
        if search.startswith("#"):
            tag = search.lstrip("#")
            query["t"] = tag
            bookmarks = Bookmark.active_objects.with_tags([tag])
        elif search.strip():
            query["q"] = search
            bookmarks = Bookmark.active_objects.with_text(search)
        else:
            bookmarks = Bookmark.active_objects.all()
        clear_search = False

    else:
        bookmarks = Bookmark.active_objects.all()
    paginator = Paginator(bookmarks.prefetch_related("tags"), 25)

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

    response = render(request, template, {"page_obj": page_obj, "query": query.urlencode()})
    return trigger_client_event(response, "clearSearch", {}) if clear_search else response


@login_required
@require_GET
def bookmarks_filter(request):
    f = BookmarkFilter(request.GET, queryset=Bookmark.objects.prefetch_related("tags"))
    paginator = Paginator(f.qs, 25)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    if page_number:
        query = request.GET.copy()
        query.pop("page")
    else:
        query = request.GET

    if request.htmx:
        # if paging, just render the list items, otherwise this is a navigation to the list page contents
        template = (
            "bookmarks/list.html#list-items-partial"
            if page_number
            else "bookmarks/filter.html#filter-partial"
        )
    else:
        template = "bookmarks/filter.html"

    logger.debug("template: %s, query: %s", template, query)
    return render(
        request,
        template,
        {"page_obj": page_obj, "filter": f, "query": query.urlencode()},
    )


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
            return redirect("bookmarks")
        return render(request, "bookmarks/form.html", {"form": form, "title": "New Bookmark"})


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
            return redirect("bookmarks")
        return render(request, "bookmarks/form.html", {"form": form, "title": "Edit Bookmark"})


@login_required
@require_POST
def bookmark_delete(request, pk):
    bookmark = get_object_or_404(Bookmark, pk=pk)
    logger.debug("delete: Bookmark %s", bookmark)
    bookmark.delete()
    return HttpResponseClientRedirect(reverse("bookmarks"))
