"""The markdown template filter renders Markdown without allowing raw HTML."""

from __future__ import annotations

import pytest
from django.template import Context, Template
from django.urls import reverse

from puka.core.templatetags.markdown import markdown
from tests.factories import ItemFactory
from tests.utils import HTMX


def test_renders_basic_markdown():
    html = markdown("**bold** and a [link](https://example.com)\n\n- one\n- two")
    assert "<strong>bold</strong>" in html
    assert '<a href="https://example.com">link</a>' in html
    assert "<ul>" in html
    assert html.count("<li>") == 2


def test_single_newlines_become_line_breaks():
    assert "<br />" in markdown("first\nsecond")


@pytest.mark.parametrize("value", [None, ""])
def test_empty_values_render_nothing(value):
    assert markdown(value) == ""


def test_raw_html_is_escaped():
    html = markdown("<script>alert(1)</script> <b>hi</b>")
    assert "<script>" not in html
    assert "<b>" not in html
    assert "&lt;script&gt;" in html


def test_unsafe_link_schemes_are_not_linked():
    html = markdown("[x](javascript:alert(1))")
    assert "href" not in html


def test_filter_is_loadable_from_templates():
    template = Template("{% load markdown %}{{ text|markdown }}")
    assert "<em>hi</em>" in template.render(Context({"text": "*hi*"}))


@pytest.mark.django_db
def test_item_detail_renders_notes_as_markdown(admin_client):
    item = ItemFactory.create(notes="## Specs\n\n- **12V** supply\n\n<script>x()</script>")
    response = admin_client.get(reverse("stuff:item-detail", args=[item.pk]), headers=HTMX)
    content = response.content.decode()
    assert "<h2>Specs</h2>" in content
    assert "<strong>12V</strong>" in content
    assert "<script>x()</script>" not in content
