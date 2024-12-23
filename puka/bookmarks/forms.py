from __future__ import annotations

from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Div, Field, Layout
from crispy_tailwind.layout import Button, Submit
from django.forms import ModelForm
from django.urls import reverse

from .models import Bookmark


class PrimaryButton(Submit):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault(
            "css_class",
            "rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-xs hover:bg-indigo-500 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600",
        )
        super().__init__(*args, **kwargs)


class CancelButton(Button):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("css_class", "text-sm/6 font-semibold text-gray-900")
        super().__init__(*args, **kwargs)


class DeleteButton(HTML):
    def __init__(self, *args, **kwargs):
        super().__init__(
            f"""<button type="button"
            class="rounded-md bg-white px-3 py-2 text-sm font-semibold text-red-600 ring-1 shadow-xs ring-red-300 ring-inset hover:bg-gray-50 ml-auto"
            hx-post="{{% url 'bookmark-delete' {kwargs["pk"]} %}}"
            hx-confirm="Delete this bookmark?">Delete</button>""",
        )


class BookmarkForm(ModelForm):
    class Meta:
        model = Bookmark
        fields = ["title", "description", "url", "tags", "active"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        is_edit = self.instance.id is not None

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_action = (
            reverse("bookmark-edit", args=[self.instance.id])
            if is_edit
            else reverse("bookmark-new")
        )
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
                CancelButton("cancel", "Cancel", onclick="window.history.back();"),
                DeleteButton(pk=self.instance.id) if is_edit else None,
                css_class="mt-4 flex gap-x-4",
            ),
        )
