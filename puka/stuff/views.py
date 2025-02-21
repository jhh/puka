import logging

from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, TemplateView, UpdateView, View
from django_htmx.http import HttpResponseLocation
from treebeard.forms import movenodeform_factory

from puka.core.views import get_template
from puka.stuff.forms import LocationForm, ProductForm
from puka.stuff.models import Location, Product

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


class ProductListView(ListView):
    context_object_name = "products"
    paginate_by = 10

    def get_template_names(self):
        return get_template(self.request, "stuff/product_list.html", "#list-partial")

    def get_queryset(self):
        return Product.objects.all().select_related("location").prefetch_related("tags")


class ProductDetailView(DetailView):
    model = Product
    context_object_name = "product"

    def get_template_names(self):
        return get_template(self.request, "stuff/product_detail.html", "#detail-partial")


class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    success_url = reverse_lazy("stuff:product-list")

    def get_template_names(self):
        return get_template(self.request, "stuff/form.html", "#form-partial")


class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    success_url = reverse_lazy("stuff:product-list")

    def get_template_names(self):
        return get_template(self.request, "stuff/form.html", "#form-partial")


class ProductDeleteView(View):
    def post(self, _request, pk):
        product = get_object_or_404(Product, pk=pk)
        product.delete()
        return HttpResponseLocation(reverse("stuff:product-list"), target="#id_content")
