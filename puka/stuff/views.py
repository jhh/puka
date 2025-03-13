import logging

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, TemplateView, UpdateView, View
from django_htmx.http import HttpResponseLocation
from treebeard.forms import movenodeform_factory

from puka.core.views import get_template
from puka.stuff.forms import ItemForm, LocationForm
from puka.stuff.models import Inventory, Item, Location
from puka.stuff.services import adjust_inventory_quantity

logger = logging.getLogger(__name__)


class HomeView(TemplateView):
    def get_template_names(self):
        return get_template(self.request, "stuff/home.html", "#home-partial")


class LocationListView(ListView):
    template_name = "stuff/location_list.html"
    context_object_name = "locations"

    def get_template_names(self):
        return get_template(self.request, "stuff/location_list.html", "#list-partial")

    def get_queryset(self):
        pk = self.kwargs.get("pk")

        if pk == 0:
            self.ancestors = []
            return Location.get_root_nodes()

        parent = get_object_or_404(Location, pk=pk)
        if hasattr(parent, "get_ancestors"):
            self.ancestors = [(node.id, node.name) for node in parent.get_ancestors()]
        self.ancestors.append((parent.id, parent.name))
        return parent.get_children()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["parent_id"] = self.kwargs.get("pk")
        context["ancestors"] = self.ancestors
        return context


class LocationDetailView(DetailView):
    model = Location
    template_name = "stuff/location_detail.html"
    context_object_name = "location"

    def get_template_names(self):
        return get_template(self.request, "stuff/location_detail.html", "#detail-partial")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["ancestors"] = self.object.get_ancestors()
        return context


class LocationCreateView(CreateView):
    model = Location
    success_url = reverse_lazy("stuff:location-list", args=[0])

    def get_template_names(self):
        return get_template(self.request, "stuff/form.html", "#form-partial")

    def get_form_class(self):
        return movenodeform_factory(Location, form=LocationForm)

    def get(self, request, *args, **kwargs):
        if "parent" in request.GET:
            self.initial = {"_ref_node_id": request.GET["parent"]}
        return super().get(request, *args, **kwargs)


class LocationUpdateView(UpdateView):
    model = Location
    success_url = reverse_lazy("stuff:location-list", args=[0])

    def get_template_names(self):
        return get_template(self.request, "stuff/form.html", "#form-partial")

    def get_form_class(self):
        return movenodeform_factory(Location, form=LocationForm)


class LocationDeleteView(View):
    def post(self, _request, pk):
        location = get_object_or_404(Location, pk=pk)
        location.delete()
        return HttpResponseLocation(reverse("stuff:location-list", args=[0]), target="#id_content")


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

    def get_template_names(self):
        return get_template(self.request, "stuff/item_detail.html", "#detail-partial")

    def get_queryset(self):
        return (
            Item.objects.annotate(quantity=Sum("inventories__quantity"))
            .prefetch_related("locations")
            .prefetch_related("tags")
        )


class ItemCreateView(CreateView):
    model = Item
    form_class = ItemForm
    success_url = reverse_lazy("stuff:item-list")

    def get_template_names(self):
        return get_template(self.request, "stuff/form.html", "#form-partial")


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


def adjust_inventory(_request, pk, quantity):
    quantity = int(quantity)
    inventory = get_object_or_404(Inventory, pk=pk)
    adjust_inventory_quantity(inventory, quantity)
    return HttpResponse(str(inventory.quantity), content_type="text/plain")
