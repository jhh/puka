from __future__ import annotations

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field, Layout
from django.forms import ModelForm
from django.urls import reverse

from puka.core.forms import CancelButton, DeleteButton, PrimaryButton
from puka.stuff.models import Category, Location


class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = ("name",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.id is not None:
            action = reverse("stuff:category-edit", args=[self.instance.id])
            delete_button = DeleteButton("stuff:category-delete", self.instance.id, "category")
            autofocus = {}
        else:
            action = reverse("stuff:category-new")
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
                PrimaryButton("submit", "Save Category"),
                CancelButton("cancel", "Cancel", onclick="window.history.back();"),
                delete_button,
                css_class="mt-4 flex gap-x-4",
            ),
        )


class LocationForm(ModelForm):
    class Meta:
        model = Location
        fields = ("name",)

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
                PrimaryButton("submit", "Save location"),
                CancelButton("cancel", "Cancel", onclick="window.history.back();"),
                delete_button,
                css_class="mt-4 flex gap-x-4",
            ),
        )
