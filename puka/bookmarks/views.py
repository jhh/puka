from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import QueryDict
from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.views.decorators.http import require_http_methods
from django_htmx.http import trigger_client_event

from .forms import BookmarkForm
from .models import Bookmark


@login_required
@require_GET
def bookmarks(request):
    request_query = request.GET
    clear_search = True
    query = QueryDict(mutable=True)

    if "t" in request_query:
        tags = request_query.getlist("t")
        bookmark_list = Bookmark.objects.with_tags(tags)
        query.setlist("t", tags)
    elif "q" in request_query:
        search: str = request_query.get("q")
        if search.startswith("#"):
            tag = search.lstrip("#")
            query["t"] = tag
            bookmark_list = Bookmark.objects.with_tags([tag])
        elif search.strip():
            query["q"] = search
            bookmark_list = Bookmark.objects.with_text(search)
        else:
            bookmark_list = Bookmark.objects.all()
        clear_search = False

    else:
        bookmark_list = Bookmark.objects.all()
    paginator = Paginator(bookmark_list, 25)

    if request.htmx:
        template_name = "partials/bookmarks.html"
    else:
        template_name = "index.html"

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    response = render(
        request,
        template_name,
        {
            "page_obj": page_obj,
            "query": query.urlencode(),
        },
    )

    return trigger_client_event(response, "clearSearch", {}) if clear_search else response


@login_required
@require_http_methods(["GET", "POST"])
def bookmark_create(request):
    if request.method == "POST":
        form = BookmarkForm(request.POST)
        if form.is_valid():
            form.save()
            response = render(
                request,
                "partials/edit_form.html",
                {
                    "form": form,
                    "show_form": False,
                },
            )
            return trigger_client_event(response, "bookmarkAdded", {})

    # GET
    return render(
        request,
        "partials/edit_form.html",
        {
            "form": BookmarkForm(),
            "show_form": True,
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
def bookmark_update(request, pk):
    bookmark = Bookmark.objects.get(pk=pk)
    if request.method == "POST":
        form = BookmarkForm(request.POST, instance=bookmark)
        if form.is_valid():
            form.save()
            response = render(
                request,
                "partials/edit_form.html",
                {
                    "form": form,
                    "show_form": False,
                },
            )
            return trigger_client_event(response, "bookmarkAdded", {})

    # GET
    return render(
        request,
        "partials/edit_form.html",
        {
            "form": BookmarkForm(instance=bookmark),
            "show_form": True,
        },
    )


@login_required
@require_GET
def cancel(request):
    form = BookmarkForm()
    return render(
        request,
        "partials/edit_form.html",
        {
            "form": form,
            "show_form": False,
        },
    )
