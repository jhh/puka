from __future__ import annotations

from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from treebeard.forms import MoveNodeForm

from puka.stuff.models import Inventory, Item, Location
from puka.stuff.services import parse_location_code


class LocationFormContext:
    cancel_url: str
    delete_url: str


class LocationForm(LocationFormContext, MoveNodeForm):
    template_name = "stuff/forms/location.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk is None:
            self.fields["name"].widget.attrs["autofocus"] = True


class ItemForm(ModelForm):
    template_name = "stuff/forms/item.html"

    location_code = forms.CharField(max_length=25, empty_value=None, required=False)
    quantity = forms.IntegerField(min_value=0, required=False)
    bookmark_url = forms.URLField(max_length=255, empty_value=None, required=False)

    class Meta:
        model = Item
        fields = ("name", "reorder_level", "tags", "notes")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs["autocomplete"] = "off"
        if self.instance.pk is None:
            self.fields["name"].widget.attrs["autofocus"] = True

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

        if Location.objects.filter(code=value).exists():
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

        quantity = self.cleaned_data.get("quantity")
        if not quantity or quantity <= 0:
            msg = "Quantity must be greater than zero if location provided."
            self.add_error("quantity", msg)


class InventoryForm(ModelForm):
    template_name = "stuff/forms/inventory.html"

    class Meta:
        model = Inventory
        fields = ("item", "location", "quantity")
        widgets = {"item": forms.HiddenInput()}  # noqa: RUF012


class LocationInventoryForm(LocationFormContext, ModelForm):
    template_name = "stuff/forms/location_inventory.html"

    class Meta:
        model = Inventory
        fields = ("item", "quantity")


class LocationItemForm(LocationFormContext, ItemForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["location_code"].disabled = True
        self.fields["location_code"].widget = forms.HiddenInput()
        self.fields["quantity"] = forms.IntegerField(min_value=1, initial=1)


class InventoryQuantityForm(LocationFormContext, ModelForm):
    template_name = "stuff/forms/location_inventory.html"

    class Meta:
        model = Inventory
        fields = ("quantity",)


class DestinationField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.name} ({obj.code})"


class InventoryMoveForm(LocationFormContext, forms.Form):
    template_name = "stuff/forms/location_inventory.html"

    destination = DestinationField(queryset=Location.objects.all(), label="Move to")
    quantity = forms.IntegerField(min_value=1, label="Quantity to move")

    def __init__(self, *args, inventory, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["destination"] = DestinationField(
            queryset=Location.objects.exclude(pk=inventory.location_id),
            label="Move to",
        )
        self.fields["quantity"].widget.attrs["max"] = inventory.quantity
        self.initial["quantity"] = inventory.quantity
        self.inventory = inventory

    def clean_quantity(self):
        quantity = self.cleaned_data["quantity"]
        if quantity > self.inventory.quantity:
            msg = "You cannot move more than the available quantity."
            raise ValidationError(msg)
        return quantity
