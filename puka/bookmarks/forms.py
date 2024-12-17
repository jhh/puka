from __future__ import annotations

from django.forms import CheckboxInput, ModelForm, Textarea, TextInput, URLInput
from taggit.forms import TagWidget

from .models import Bookmark


class BookmarkForm(ModelForm):
    class Meta:
        model = Bookmark
        fields = ["title", "description", "url", "tags", "active"]
        widgets = {
            "title": TextInput(attrs={"class": "dj-input-text"}),
            "description": Textarea(attrs={"class": "dj-input-textarea"}),
            "url": URLInput(attrs={"class": "dj-input-url"}),
            "tags": TagWidget(attrs={"class": "dj-input-text"}),
            # "tags": TextInput(attrs={"class": "dj-input-text"}),
            "active": CheckboxInput(attrs={"class": "hidden"}),
        }
