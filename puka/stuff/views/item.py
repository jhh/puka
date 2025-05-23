import logging
from types import MappingProxyType

from django.db import transaction
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView, View
from django_htmx.http import HttpResponseLocation

from puka.core.views import get_template
from puka.stuff.forms import InventoryForm, ItemForm
from puka.stuff.models import Bookmark, Inventory, Item
from puka.stuff.services import adjust_inventory_quantity, get_or_create_location

logger = logging.getLogger(__name__)


class ItemListView(ListView):
    context_object_name = "items"
    paginate_by = 10

    def get_template_names(self):
        return get_template(self.request, "stuff/item_list.html", "#list-partial")

    def get_queryset(self):
        if "query" in self.request.GET:
            query = self.request.GET["query"]
            query_set = Item.objects.search(query)
            self.extra_context = {"query": query}
        else:
            query_set = Item.objects.all().order_by("name")

        return (
            query_set.annotate(quantity=Sum("inventories__quantity"))
            .prefetch_related("locations")
            .prefetch_related("tags")
        )


class ItemDetailView(DetailView):
    model = Item
    context_object_name = "item"
    extra_context = MappingProxyType({"bookmark_delete_url": "stuff:bookmark-delete"})

    def get_template_names(self):
        return get_template(self.request, "stuff/item_detail.html", "#detail-partial")

    def get_queryset(self):
        return (
            Item.objects.annotate(quantity=Sum("inventories__quantity"))
            .prefetch_related("bookmarks")
            .prefetch_related("locations")
            .prefetch_related("tags")
        )


class ItemCreateView(CreateView):
    model = Item
    form_class = ItemForm
    success_url = reverse_lazy("stuff:item-list")

    def get_template_names(self):
        return get_template(self.request, "stuff/form.html", "#form-partial")

    @transaction.atomic
    def form_valid(self, form):
        self.object: Item = form.save()

        location_code = form.cleaned_data["location_code"]
        quantity = form.cleaned_data["quantity"]

        if location_code and quantity:
            location, _ = get_or_create_location(location_code)
            Inventory.objects.create(item=self.object, location=location, quantity=quantity)

        bookmark_url = form.cleaned_data["bookmark_url"]
        if bookmark_url:
            bookmark, _ = Bookmark.objects.get_or_create(
                url=bookmark_url,
                defaults={"title": self.object.name, "active": False},
            )
            bookmark.tags.add("stuff")
            self.object.bookmarks.add(bookmark)

        return super().form_valid(form)


class ItemUpdateView(UpdateView):
    model = Item
    form_class = ItemForm
    success_url = reverse_lazy("stuff:item-list")

    def get_template_names(self):
        return get_template(self.request, "stuff/form.html", "#form-partial")


class ItemDeleteView(View):
    def post(self, _request, pk):
        item = get_object_or_404(Item, pk=pk)
        item.delete()
        return HttpResponseLocation(reverse("stuff:item-list"), target="#id_content")


def adjust_inventory(request, pk):
    quantity = int(request.POST.get("quantity", 0))
    inventory = get_object_or_404(Inventory, pk=pk)
    adjust_inventory_quantity(inventory, quantity)
    return HttpResponse(str(inventory.quantity), content_type="text/plain")


class InventoryCreateView(CreateView):
    model = Inventory
    form_class = InventoryForm

    def get_template_names(self):
        return get_template(self.request, "stuff/form.html", "#form-partial")

    def get_initial(self):
        return {"item": self.kwargs["pk"]}


class InventoryUpdateView(UpdateView):
    model = Inventory
    form_class = InventoryForm

    def get_template_names(self):
        return get_template(self.request, "stuff/form.html", "#form-partial")


class InventoryDeleteView(View):
    def post(self, _request, pk):
        inventory = get_object_or_404(Inventory, pk=pk)
        item_id = inventory.item.id
        inventory.delete()
        return HttpResponseLocation(
            reverse("stuff:item-detail", kwargs={"pk": item_id}),
            target="#id_content",
        )
