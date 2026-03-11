from __future__ import annotations

from django.forms import CheckboxInput, ModelForm, Textarea, TextInput
from taggit.forms import TagWidget

from puka.bookmarks.models import Bookmark


class BookmarkForm(ModelForm):
    class Meta:
        model = Bookmark
        fields = ("title", "description", "url", "tags", "active")
        widgets = {  # noqa: RUF012
            "title": TextInput(attrs={"class": "input w-full"}),
            "description": Textarea(attrs={"class": "textarea w-full"}),
            "url": TextInput(attrs={"class": "input w-full"}),
            "tags": TagWidget(attrs={"class": "input w-full"}),
            "active": CheckboxInput(attrs={"class": "checkbox checkbox-sm"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
