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
    request_query = request.GET
    clear_search = True
    query = QueryDict(mutable=True)

    if "t" in request_query:
        tags = request_query.getlist("t")
        bookmark_list = Bookmark.active_objects.with_tags(tags)
        query.setlist("t", tags)
    elif "q" in request_query:
        search: str = request_query.get("q")
        if search.startswith("#"):
            tag = search.lstrip("#")
            query["t"] = tag
            bookmark_list = Bookmark.active_objects.with_tags([tag])
        elif search.strip():
            query["q"] = search
            bookmark_list = Bookmark.active_objects.with_text(search)
        else:
            bookmark_list = Bookmark.active_objects.all()
        clear_search = False

    else:
        bookmark_list = Bookmark.active_objects.all()
    paginator = Paginator(bookmark_list.prefetch_related("tags"), 25)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    response = render(
        request,
        "bookmarks/_list_ul.html" if request.htmx else "bookmarks/list.html",
        {
            "page_obj": page_obj,
            "query": query.urlencode(),
        },
    )

    return trigger_client_event(response, "clearSearch", {}) if clear_search else response


@login_required
@require_GET
def bookmarks_filter(request):
    f = BookmarkFilter(request.GET, queryset=Bookmark.objects.prefetch_related("tags"))
    paginator = Paginator(f.qs, 25)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    query = request.GET.copy()
    if "page" in query:
        query.pop("page")

    return render(
        request,
        "bookmarks/_list_ul.html" if request.htmx else "bookmarks/bookmark_filter.html",
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
