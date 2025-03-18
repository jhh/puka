from __future__ import annotations

import logging

from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.generic import ListView
from django_htmx.http import HttpResponseLocation

from puka.bookmarks.filters import BookmarkFilter
from puka.bookmarks.models import Bookmark
from puka.core.views import get_template
from puka.stuff.models import Item

logger = logging.getLogger(__name__)


class BookmarkListView(ListView):
    model = Bookmark
    template_name = "bookmarks/list.html"
    context_object_name = "bookmarks"
    paginate_by = 10

    def get_template_names(self):
        return get_template(self.request, "stuff/bookmark_select.html", "#filter-partial")

    def get_queryset(self):
        self.filter = BookmarkFilter(
            self.request.GET,
            queryset=Bookmark.objects.prefetch_related("tags"),
        )
        return self.filter.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter"] = self.filter
        context["item_id"] = self.kwargs.get("pk")
        return context


@require_POST
def bookmark_add_view(request, item_pk):
    item = Item.objects.get(pk=item_pk)
    bookmark_pk = request.POST.get("bookmark_pk")
    bookmark = Bookmark.objects.get(pk=bookmark_pk)
    item.bookmarks.add(bookmark)
    return HttpResponseLocation(reverse("stuff:item-detail", args=[item_pk]), target="#id_content")


@require_POST
def bookmark_delete_view(request, item_pk):
    item = Item.objects.get(pk=item_pk)
    bookmark_pk = request.POST.get("bookmark_pk")
    bookmark = Bookmark.objects.get(pk=bookmark_pk)
    item.bookmarks.remove(bookmark)
    return HttpResponseLocation(reverse("stuff:item-detail", args=[item_pk]), target="#id_content")
