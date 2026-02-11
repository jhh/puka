from __future__ import annotations

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field, Layout
from django.forms import ModelForm
from django.urls import reverse

from puka.bookmarks.models import Bookmark
from puka.core.forms import CancelButton, DeleteButton, PrimaryButton


class BookmarkForm(ModelForm):
    class Meta:
        model = Bookmark
        fields = ("title", "description", "url", "tags", "active")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.id is not None:
            action = reverse("bookmarks:edit", args=[self.instance.id])
            delete_button = DeleteButton("bookmarks:delete", self.instance.id, "bookmark")
        else:
            action = reverse("bookmarks:new")
            delete_button = None

        self.helper = FormHelper()
        self.helper.attrs = {"hx-post": action}
        self.helper.layout = Layout(
            Div(
                Field("title", wrapper_class="sm:col-span-6", autofocus=""),
                Field("description", wrapper_class="sm:col-span-6"),
                Field("url", wrapper_class="sm:col-span-6"),
                Field("tags", wrapper_class="sm:col-span-4"),
                Field("active", wrapper_class="sm:col-span-2"),
                css_class="grid grid-cols-1 gap-x-6 gap-y-4 sm:grid-cols-6",
            ),
            Div(
                PrimaryButton("submit", "Save Bookmark"),
                CancelButton("bookmarks:list"),
                delete_button,
                css_class="mt-4 flex gap-x-4",
            ),
        )
