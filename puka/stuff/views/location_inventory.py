from __future__ import annotations

from typing import TYPE_CHECKING, cast

from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import CreateView, FormView, UpdateView, View
from django.views.generic.edit import FormMixin
from django_htmx.http import HttpResponseLocation

from puka.core.views import get_template
from puka.stuff.forms import (
    InventoryMoveForm,
    InventoryQuantityForm,
    LocationFormContext,
    LocationInventoryForm,
    LocationItemForm,
)
from puka.stuff.models import Inventory, Location
from puka.stuff.services import move_inventory
from puka.stuff.views.item import ItemCreateView

if TYPE_CHECKING:
    from django.http import HttpRequest


class LocationInventoryMixin(FormMixin):
    kwargs: dict[str, int]
    request: HttpRequest
    form_title: str

    def get_location(self):
        return get_object_or_404(Location, pk=self.kwargs["location_pk"])

    def get_queryset(self):
        return Inventory.objects.filter(location=self.get_location()).select_related("item")

    def get_template_names(self):
        return get_template(self.request, "stuff/location_form.html", "#form-partial")

    def get_success_url(self):
        return reverse("stuff:location-list", args=[self.kwargs["location_pk"]])

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        cast("LocationFormContext", form).cancel_url = self.get_success_url()
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["location"] = self.get_location()
        context["form_title"] = self.form_title
        return context


class LocationInventoryCreateView(LocationInventoryMixin, CreateView):
    model = Inventory
    form_class = LocationInventoryForm
    form_title = "Add inventory item"

    def get_initial(self):
        return {"quantity": 1}

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.instance.location = self.get_location()
        return form

    @transaction.atomic
    def form_valid(self, form):
        # Location is not an editable field; validate the item/location constraint explicitly.
        try:
            form.instance.validate_unique()
            form.instance.validate_constraints()
        except ValidationError:
            form.add_error("item", "This item is already stored here. Edit its quantity instead.")
            return self.form_invalid(form)
        return super().form_valid(form)


class LocationInventoryUpdateView(LocationInventoryMixin, UpdateView):
    model = Inventory
    form_class = InventoryQuantityForm
    form_title = "Edit inventory quantity"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.delete_url = reverse(
            "stuff:location-inventory-delete",
            args=[self.kwargs["location_pk"], self.object.pk],
        )
        return form


class LocationItemCreateView(LocationInventoryMixin, ItemCreateView):
    form_class = LocationItemForm
    form_title = "Create item in this location"

    def get_initial(self):
        return {"location_code": self.get_location().code, "quantity": 1}


class LocationInventoryMoveView(LocationInventoryMixin, FormView):
    form_class = InventoryMoveForm
    form_title = "Move inventory item"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["inventory"] = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        return kwargs

    def form_valid(self, form):
        try:
            move_inventory(
                form.inventory,
                form.cleaned_data["destination"],
                form.cleaned_data["quantity"],
            )
        except ValueError as error:
            form.add_error("quantity", str(error))
            return self.form_invalid(form)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["inventory"] = context["form"].inventory
        return context


class LocationInventoryDeleteView(LocationInventoryMixin, View):
    def post(self, request, **_kwargs):
        inventory = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        inventory.delete()
        if request.htmx:
            return HttpResponseLocation(self.get_success_url(), target="#content")
        return redirect(self.get_success_url())
