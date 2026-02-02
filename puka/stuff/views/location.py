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
            self.ancestors = [(node.pk, node.name) for node in parent.get_ancestors()]
        self.ancestors.append((parent.pk, parent.name))
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

    def get_initial(self):
        return {"_ref_node_id": self.request.GET.get("parent")}


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
