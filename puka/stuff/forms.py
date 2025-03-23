from __future__ import annotations

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field, Layout
from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.urls import reverse
from treebeard.forms import MoveNodeForm

from puka.core.forms import CancelButton, DeleteButton, PrimaryButton
from puka.stuff.models import Inventory, Item, Location
from puka.stuff.services import parse_location_code


class LocationForm(MoveNodeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.id is not None:
            action = reverse("stuff:location-edit", args=[self.instance.id])
            delete_button = DeleteButton("stuff:location-delete", self.instance.id, "location")
            autofocus = {}
        else:
            action = reverse("stuff:location-new")
            delete_button = None
            autofocus = {"autofocus": ""}

        self.helper = FormHelper()
        self.helper.attrs = {"hx-post": action}
        self.helper.layout = Layout(
            Div(
                Field("name", wrapper_class="sm:col-span-6", **autofocus),
                css_class="grid grid-cols-1 gap-x-6 gap-y-4 sm:grid-cols-6",
            ),
            Div(
                Field("_position", wrapper_class="sm:col-span-6"),
                css_class="grid grid-cols-1 gap-x-6 gap-y-4 sm:grid-cols-6",
            ),
            Div(
                Field("_ref_node_id", wrapper_class="sm:col-span-6"),
                css_class="grid grid-cols-1 gap-x-6 gap-y-4 sm:grid-cols-6",
            ),
            Div(
                PrimaryButton("submit", "Save location"),
                CancelButton("cancel", "Cancel", onclick="window.history.back();"),
                delete_button,
                css_class="mt-4 flex gap-x-4",
            ),
        )


class ItemForm(ModelForm):
    location_code = forms.CharField(max_length=25, empty_value=None, required=False)
    quantity = forms.IntegerField(min_value=0, required=False)
    bookmark_url = forms.URLField(max_length=255, empty_value=None, required=False)

    class Meta:
        model = Item
        fields = ("name", "reorder_level", "tags", "notes")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.id:
            action = reverse("stuff:item-edit", args=[self.instance.id])
            delete_button = DeleteButton("stuff:item-delete", self.instance.id, "item")
            autofocus = {}
            extra_fields = (None, None, None)
        else:
            action = reverse("stuff:item-new")
            delete_button = None
            autofocus = {"autofocus": ""}
            extra_fields = (
                Field("location_code", wrapper_class="sm:col-span-4"),
                Field("quantity", wrapper_class="sm:col-span-2"),
                Field("bookmark_url", wrapper_class="sm:col-span-6"),
            )

        self.helper = FormHelper()
        self.helper.attrs = {"hx-post": action}
        self.helper.layout = Layout(
            Div(
                Field("name", wrapper_class="sm:col-span-6", autocomplete="off", **autofocus),
                Field("reorder_level", wrapper_class="sm:col-span-2"),
                Field("tags", wrapper_class="sm:col-span-4"),
                Field("notes", wrapper_class="sm:col-span-6"),
                *extra_fields,
                css_class="grid grid-cols-1 gap-x-6 gap-y-4 sm:grid-cols-6",
            ),
            Div(
                PrimaryButton("submit", "Save item"),
                CancelButton("cancel", "Cancel", onclick="window.history.back();"),
                delete_button,
                css_class="mt-4 flex gap-x-4",
            ),
        )

    def clean_name(self):
        value = self.cleaned_data["name"]

        if self.instance.id:
            return value

        try:
            Item.objects.get(name=value)
        except Item.DoesNotExist:
            return value

        msg = "This item already exists."
        raise ValidationError(msg)

    def clean_location_code(self):
        value = self.cleaned_data["location_code"]
        if not value:
            return value

        try:
            parent, _ = parse_location_code(value)
        except ValueError as e:
            msg = f"Enter a value with a valid location code ({e})."
            raise ValidationError(msg) from e

        try:
            Location.objects.get(code=parent)
        except Location.DoesNotExist as e:
            msg = f"Enter a location code with a valid parent location code ({parent} not found)."
            raise ValidationError(msg) from e

        return value

    def clean(self):
        if "location_code" not in self.cleaned_data or not self.cleaned_data["location_code"]:
            return

        quantity = self.cleaned_data["quantity"]
        if not quantity or quantity <= 0:
            msg = "Quantity must be greater than zero if location provided."
            self.add_error("quantity", msg)


class InventoryForm(ModelForm):
    class Meta:
        model = Inventory
        fields = ("item", "location", "quantity")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.id is not None:
            action = reverse("stuff:inventory-edit", args=[self.instance.id])
            delete_button = DeleteButton("stuff:inventory-delete", self.instance.id, "item")
        else:
            action = reverse("stuff:inventory-new", args=[self.initial["item"]])
            delete_button = None

        self.helper = FormHelper()
        self.helper.attrs = {"hx-post": action}
        self.helper.layout = Layout(
            Field("item", type="hidden"),
            Div(
                Field("location", wrapper_class="sm:col-span-4"),
                Field("quantity", wrapper_class="sm:col-span-2"),
                css_class="grid grid-cols-1 gap-x-6 gap-y-4 sm:grid-cols-6",
            ),
            Div(
                PrimaryButton("submit", "Save item"),
                CancelButton("cancel", "Cancel", onclick="window.history.back();"),
                delete_button,
                css_class="mt-4 flex gap-x-4",
            ),
        )
