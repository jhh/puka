from __future__ import annotations

import logging

from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.generic import ListView
from django_htmx.http import HttpResponseLocation

from puka.bookmarks.filters import BookmarkFilter
from puka.bookmarks.models import Bookmark
from puka.core.views import get_template
from puka.upkeep.models import Area

logger = logging.getLogger(__name__)


class BookmarkSelectView(ListView):
    model = Bookmark
    context_object_name = "bookmarks"
    paginate_by = 10

    def get_template_names(self):
        return get_template(self.request, "bookmarks/_select.html", "#filter-partial")

    def get_queryset(self):
        self.filter = BookmarkFilter(
            self.request.GET,
            queryset=Bookmark.objects.prefetch_related("tags"),
        )
        return self.filter.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter"] = self.filter
        return context

    def post(self, request, pk):
        area = Area.objects.get(pk=pk)
        bookmark_pk = request.POST.get("bookmark_pk")
        bookmark = Bookmark.objects.get(pk=bookmark_pk)
        area.bookmarks.add(bookmark)
        return HttpResponseLocation(
            reverse("upkeep:area-detail", args=[area.pk]),
            target="#id_content",
        )


@require_POST
def bookmark_delete_view(request, pk):
    area = Area.objects.get(pk=pk)
    bookmark_pk = request.POST.get("bookmark_pk")
    bookmark = Bookmark.objects.get(pk=bookmark_pk)
    area.bookmarks.remove(bookmark)
    return HttpResponseLocation(reverse("upkeep:area-detail", args=[pk]), target="#id_content")
