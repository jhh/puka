from __future__ import annotations

from django import template
from django.utils.safestring import mark_safe
from markdown_it import MarkdownIt

register = template.Library()

# Raw HTML is escaped (html=False) and unsafe link schemes such as
# javascript: are rejected by markdown-it's link validation, so the output
# is safe to mark as such.
_md = MarkdownIt("commonmark", {"html": False, "breaks": True})


@register.filter
def markdown(value: str | None) -> str:
    return mark_safe(_md.render(value or ""))  # noqa: S308
