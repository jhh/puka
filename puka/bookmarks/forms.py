from __future__ import annotations

from django.forms import CheckboxInput
from django.forms import ModelForm
from django.forms import Textarea
from django.forms import TextInput
from django.forms import URLInput

from .models import Bookmark


class BookmarkForm(ModelForm):
    class Meta:
        model = Bookmark
        fields = ["title", "description", "url", "tags", "active"]
        widgets = {
            "title": TextInput(attrs={"class": "dj-input-text"}),
            "description": Textarea(attrs={"class": "dj-input-textarea"}),
            "url": URLInput(attrs={"class": "dj-input-url"}),
            "tags": TextInput(attrs={"class": "dj-input-text"}),
            "active": CheckboxInput(attrs={"class": "hidden"}),
        }
