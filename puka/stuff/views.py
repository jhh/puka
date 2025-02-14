import logging

from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, ListView, TemplateView, UpdateView, View
from django_htmx.http import HttpResponseLocation
from treebeard.forms import movenodeform_factory

from puka.core.views import get_template
from puka.stuff.forms import CategoryForm, LocationForm
from puka.stuff.models import Category, Location

logger = logging.getLogger(__name__)


class HomeView(TemplateView):
    def get_template_names(self):
        return get_template(self.request, "stuff/home.html", "#home-partial")


class CategoryListView(ListView):
    model = Category
    context_object_name = "categories"

    def get_template_names(self):
        return get_template(self.request, "stuff/category_list.html", "#list-partial")


class CategoryCreateView(CreateView):
    model = Category
    form_class = CategoryForm
    success_url = reverse_lazy("stuff:category-list")

    def get_template_names(self):
        return get_template(self.request, "stuff/form.html", "#form-partial")


class CategoryUpdateView(UpdateView):
    model = Category
    form_class = CategoryForm
    success_url = reverse_lazy("stuff:category-list")

    def get_template_names(self):
        return get_template(self.request, "stuff/form.html", "#form-partial")


class CategoryDeleteView(View):
    def post(self, _request, pk):
        category = get_object_or_404(Category, pk=pk)
        category.delete()
        return HttpResponseLocation(reverse("stuff:category-list"), target="#id_content")


class LocationListView(ListView):
    model = Location
    template_name = "stuff/location_list.html"
    context_object_name = "locations"

    def get_template_names(self):
        return get_template(self.request, "stuff/location_list.html", "#list-partial")

    def get_queryset(self):
        pk = self.kwargs.get("pk")
        if pk:
            self.parent = get_object_or_404(Location, pk=pk)
            return self.parent.get_children()
        return Location.get_root_nodes()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["parent_id"] = self.kwargs.get("pk")
        if hasattr(self, "parent"):
            context["parent_name"] = self.parent.name
        return context


class LocationCreateView(CreateView):
    model = Location
    success_url = reverse_lazy("stuff:location-list-root")

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
    success_url = reverse_lazy("stuff:location-list-root")

    def get_template_names(self):
        return get_template(self.request, "stuff/form.html", "#form-partial")

    def get_form_class(self):
        return movenodeform_factory(Location, form=LocationForm)


class LocationDeleteView(View):
    def post(self, _request, pk):
        location = get_object_or_404(Location, pk=pk)
        location.delete()
        return HttpResponseLocation(reverse("stuff:location-list-root"), target="#id_content")
