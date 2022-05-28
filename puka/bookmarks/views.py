from __future__ import annotations

from django.core.paginator import Paginator
from django.shortcuts import render
from django.views.decorators.http import require_GET

from .forms import BookmarkForm
from .models import Bookmark


@require_GET
def bookmarks(request):
    bookmark_list = Bookmark.objects.all()
    paginator = Paginator(bookmark_list, 25)

    form = BookmarkForm()

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        "bookmarks.html",
        {
            "form": form,
            "page_obj": page_obj,
        },
    )


@require_GET
def new(request):
    form = BookmarkForm()
    return render(
        request,
        "partials/edit_form.html",
        {
            "form": form,
            "show_form": True,
        },
    )


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
