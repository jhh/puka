from __future__ import annotations

from django.core.paginator import Paginator
from django.shortcuts import render
from django.views.decorators.http import require_GET

from .models import Bookmark


@require_GET
def bookmarks(request):
    bookmark_list = Bookmark.objects.all()
    paginator = Paginator(bookmark_list, 25)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "bookmarks.html", {"page_obj": page_obj})
