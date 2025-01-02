from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, ListView, TemplateView, UpdateView, View
from django_htmx.http import HttpResponseLocation

from puka.stuff.forms import CategoryForm
from puka.stuff.models import Category


class HomeView(TemplateView):
    def get_template_names(self):
        if self.request.htmx:
            return ["stuff/home.html#home-partial"]
        return ["stuff/home.html"]


class CategoryListView(ListView):
    model = Category
    context_object_name = "categories"

    def get_template_names(self):
        if self.request.htmx:
            return ["stuff/category_list.html#list-partial"]
        return ["stuff/category_list.html"]


class CategoryCreateView(CreateView):
    model = Category
    form_class = CategoryForm
    success_url = reverse_lazy("stuff:category-list")

    def get_template_names(self):
        if self.request.htmx:
            return ["stuff/form.html#form-partial"]
        return ["stuff/form.html"]


class CategoryUpdateView(UpdateView):
    model = Category
    form_class = CategoryForm
    success_url = reverse_lazy("stuff:category-list")

    def get_template_names(self):
        if self.request.htmx:
            return ["stuff/form.html#form-partial"]
        return ["stuff/form.html"]


class CategoryDeleteView(View):
    def post(self, _request, pk):
        category = get_object_or_404(Category, pk=pk)
        category.delete()
        return HttpResponseLocation(reverse("stuff:category-list"), target="#id_content")
