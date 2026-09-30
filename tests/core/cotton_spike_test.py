"""
Cotton integration checks (PLAN.md, phase 2).

The fixtures in ``tests/templates/`` go through the same pre-commit hooks (djangofmt, djade)
as the app templates, so these tests also catch a formatter rewriting Cotton syntax.
"""

from __future__ import annotations

import copy
from pathlib import Path

import pytest
from django.conf import settings
from django.template import engines
from django.template.backends.django import DjangoTemplates, Template
from django.template.loader import get_template, render_to_string
from django.template.loaders.cached import Loader as CachedLoader
from django.test import override_settings

from tests.utils import parse_html

TEST_TEMPLATES = Path(__file__).resolve().parent.parent / "templates"


def _templates_with_test_dir():
    templates = copy.deepcopy(settings.TEMPLATES)
    templates[0]["DIRS"] = [*templates[0]["DIRS"], str(TEST_TEMPLATES)]
    return templates


@pytest.fixture(autouse=True)
def test_templates():
    with override_settings(TEMPLATES=_templates_with_test_dir()):
        yield


def _buttons(html: str):
    return parse_html(html).find("button")


def test_loaders_are_cached_cotton_first():
    backend = engines["django"]
    assert isinstance(backend, DjangoTemplates)
    (loader,) = backend.engine.template_loaders
    assert isinstance(loader, CachedLoader)
    names = [type(child).__module__ for child in loader.loaders]
    assert names == [
        "django_cotton.cotton_loader",
        "django.template.loaders.filesystem",
        "django.template.loaders.app_directories",
    ]


def test_full_page_renders_components():
    html = render_to_string("spike/page.html", {"name": "one", "open": False})

    assert "<head>" in html
    assert "<c-" not in html
    toggle, save = _buttons(html)
    assert toggle.attrs["class"].split() == ["btn", "btn-sm"]
    assert save.attrs["class"].split() == ["btn", "btn-primary"]
    (card,) = parse_html(html).find("div", id="card")
    assert card.attrs["class"] == "card"


def test_partial_renders_through_cotton_loader():
    html = render_to_string("spike/page.html#card-partial", {"name": "two"})

    assert "<head>" not in html
    assert "Toggle" not in html
    (save,) = _buttons(html)
    assert save.text == "Save"
    assert parse_html(html).find("h2")[0].text == "Card two"


def test_partial_from_include():
    html = render_to_string("spike/include.html", {"name": "three"})

    assert html.strip().startswith("<section>")
    assert "<head>" not in html
    (save,) = _buttons(html)
    assert save.attrs["hx-confirm"] == "Save three?"


def test_partial_is_cached():
    first = get_template("spike/page.html#card-partial")
    second = get_template("spike/page.html#card-partial")
    assert isinstance(first, Template)
    assert isinstance(second, Template)
    assert first.template is second.template
    assert render_to_string("spike/page.html#card-partial", {"name": "a"}) != render_to_string(
        "spike/page.html#card-partial",
        {"name": "b"},
    )


def test_attrs_pass_through():
    html = render_to_string("spike/page.html", {"name": "four", "open": False})
    toggle, save = _buttons(html)

    # htmx and Alpine attributes reach the element; declared <c-vars> don't.
    assert save.attrs["hx-post"] == "/save/"
    assert save.attrs["hx-confirm"] == "Save four?"
    assert toggle.attrs["x-bind:class"] == "{ 'btn-active': open }"
    assert toggle.attrs["x-on:click"] == "open = !open"
    for el in (toggle, save):
        assert "variant" not in el.attrs
        assert "size" not in el.attrs
        assert el.attrs["type"] == "button"


def test_htmx_view_partial_with_components(rf):
    """``get_template`` in ``puka.core.views`` resolves ``#partial`` names with Cotton."""
    from puka.core.views import get_template as view_template  # noqa: PLC0415

    request = rf.get("/", headers={"HX-Request": "true"})
    (name,) = view_template(request, "spike/page.html", "#card-partial")
    html = get_template(name).render({"name": "five"}, request)

    assert "<head>" not in html
    assert _buttons(html)[0].attrs["hx-post"] == "/save/"
