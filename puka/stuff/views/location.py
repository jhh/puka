import logging

from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView, View
from django_htmx.http import HttpResponseLocation
from treebeard.forms import movenodeform_factory

from puka.core.views import get_template
from puka.stuff.forms import LocationForm
from puka.stuff.models import Location

logger = logging.getLogger(__name__)


class LocationListView(ListView):
    context_object_name = "locations"

    def get_template_names(self):
        return get_template(self.request, "stuff/location_list.html", "#list-partial")

    def get_queryset(self):
        # "stuff:location" has no pk and lists the root nodes, like pk 0.
        pk = self.kwargs.get("pk", 0)

        if pk == 0:
            self.ancestors = []
            return Location.objects.get_root_nodes()

        parent = get_object_or_404(Location, pk=pk)
        self.ancestors = [(node.pk, node.name) for node in Location.objects.get_ancestors(parent)]
        self.ancestors.append((parent.pk, parent.name))
        return Location.objects.get_children(parent)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["parent_id"] = self.kwargs.get("pk", 0)
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
        context["ancestors"] = Location.objects.get_ancestors(self.object)
        return context


class LocationCreateView(CreateView):
    model = Location
    success_url = reverse_lazy("stuff:location-list", args=[0])

    def get_template_names(self):
        return get_template(self.request, "stuff/form.html", "#form-partial")

    def get_form_class(self):
        return movenodeform_factory(Location, form=LocationForm)

    def get_initial(self):
        # parent=0 (or missing) means a new root node, which treebeard represents as None.
        parent = self.request.GET.get("parent")
        return {
            "treebeard_position": "sorted-child",
            "treebeard_ref_node": parent if parent and parent != "0" else None,
        }


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
        return HttpResponseLocation(reverse("stuff:location-list", args=[0]), target="#content")
