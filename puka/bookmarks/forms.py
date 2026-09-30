from __future__ import annotations

from django.forms import ModelForm, TextInput

from puka.bookmarks.models import Bookmark


class BookmarkForm(ModelForm):
    template_name = "bookmarks/forms/bookmark.html"

    class Meta:
        model = Bookmark
        fields = ("title", "description", "url", "tags", "active")
        # A plain text input, not type="url", so the server validates and reports errors.
        widgets = {"url": TextInput()}  # noqa: RUF012
