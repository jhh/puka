from __future__ import annotations

import logging
from typing import cast

from django.db.models import Count, Prefetch
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView, UpdateView, View
from django_htmx.http import HttpResponseLocation
from treebeard.forms import movenodeform_factory

from puka.core.views import get_template
from puka.stuff.forms import LocationForm
from puka.stuff.models import Inventory, Location

logger = logging.getLogger(__name__)


class LocationListView(ListView):
    context_object_name = "locations"

    def get_template_names(self):
        return get_template(self.request, "stuff/location_list.html", "#list-partial")

    def get_queryset(self):
        # "stuff:location" has no pk and lists the root nodes, like pk 0.
        pk = self.kwargs.get("pk", 0)

        if pk == 0:
            self.location = None
            self.ancestors = []
            return Location.objects.get_root_nodes().annotate(inventory_count=Count("inventories"))

        parent = get_object_or_404(Location, pk=pk)
        self.location = parent
        self.ancestors = [(node.pk, node.name) for node in Location.objects.get_ancestors(parent)]
        self.ancestors.append((parent.pk, parent.name))
        return Location.objects.get_children(parent).annotate(inventory_count=Count("inventories"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["parent_id"] = self.kwargs.get("pk", 0)
        context["ancestors"] = self.ancestors
        context["location"] = self.location
        if self.location:
            parent = Location.objects.get_parent(self.location)
            context["up_id"] = parent.pk if parent else 0
            context["inventories"] = self.location.inventories.select_related("item").order_by(
                "item__name",
            )
        return context


class LocationDetailView(DetailView):
    model = Location
    template_name = "stuff/location_detail.html"
    context_object_name = "location"

    def get_queryset(self):
        return Location.objects.prefetch_related(
            Prefetch("inventories", queryset=Inventory.objects.select_related("item")),
        )

    def get_template_names(self):
        return get_template(self.request, "stuff/location_detail.html", "#detail-partial")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["ancestors"] = Location.objects.get_ancestors(self.object)
        return context


class LocationCreateView(CreateView):
    model = Location

    def get_template_names(self):
        return get_template(self.request, "stuff/location_form.html", "#form-partial")

    def get_form_class(self):
        return movenodeform_factory(Location, form=LocationForm)

    def get_initial(self):
        # parent=0 (or missing) means a new root node, which treebeard represents as None.
        parent = self.request.GET.get("parent")
        return {
            "treebeard_position": "sorted-child",
            "treebeard_ref_node": parent if parent and parent != "0" else None,
        }

    def get_success_url(self):
        parent = Location.objects.get_parent(self.object)
        return reverse("stuff:location-list", args=[parent.pk if parent else 0])

    def get_form(self, form_class=None):
        form = cast("LocationForm", super().get_form(form_class))
        parent = self.request.GET.get("parent", "0") or "0"
        if parent != "0":
            parent = get_object_or_404(Location, pk=parent).pk
        form.cancel_url = reverse("stuff:location-list", args=[parent])
        return form

    def get_context_data(self, **kwargs):
        return super().get_context_data(form_title="Add location", **kwargs)


class LocationUpdateView(UpdateView):
    model = Location

    def get_template_names(self):
        return get_template(self.request, "stuff/location_form.html", "#form-partial")

    def get_form_class(self):
        return movenodeform_factory(Location, form=LocationForm)

    def get_success_url(self):
        return reverse("stuff:location-list", args=[self.object.pk])

    def get_form(self, form_class=None):
        form = cast("LocationForm", super().get_form(form_class))
        form.cancel_url = self.get_success_url()
        return form

    def get_context_data(self, **kwargs):
        return super().get_context_data(form_title=f"Edit {self.object.name}", **kwargs)


class LocationDeleteView(View):
    def post(self, request, pk):
        location = get_object_or_404(Location, pk=pk)
        parent = Location.objects.get_parent(location)
        url = reverse("stuff:location-list", args=[parent.pk if parent else 0])
        location.delete()
        if request.htmx:
            return HttpResponseLocation(url, target="#content")
        return redirect(url)
