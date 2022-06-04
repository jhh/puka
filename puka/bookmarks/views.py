from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.views.decorators.http import require_http_methods
from django_htmx.http import trigger_client_event

from .forms import BookmarkForm
from .models import Bookmark


@login_required
@require_GET
def bookmarks(request):
    query = request.GET
    if "t" in query:
        bookmark_list = Bookmark.objects.with_tags(query.getlist("t"))
    else:
        bookmark_list = Bookmark.objects.all()
    paginator = Paginator(bookmark_list, 25)

    if request.htmx:
        template_name = "partials/bookmarks.html"
    else:
        template_name = "index.html"

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        template_name,
        {
            "page_obj": page_obj,
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
def new(request):
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
            return trigger_client_event(response, "bookmark-added", {})

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
