from __future__ import annotations

import json
from dataclasses import dataclass, field
from html.parser import HTMLParser
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.http import HttpResponse

HTMX = {"HX-Request": "true"}


@dataclass
class Element:
    tag: str
    attrs: dict[str, str]
    text: str = ""
    # Index of the enclosing <form> in ``Page.forms``, or None.
    form: int | None = None
    # The enclosing <select> of an <option>.
    parent: Element | None = field(default=None, repr=False, compare=False)


@dataclass
class Page:
    elements: list[Element] = field(default_factory=list)
    forms: list[Element] = field(default_factory=list)

    def find(self, tag: str, **attrs: str) -> list[Element]:
        """Elements with ``tag`` whose attributes include ``attrs`` (``hx_post`` -> ``hx-post``)."""
        wanted = {name.replace("_", "-"): value for name, value in attrs.items()}
        return [
            el
            for el in self.elements
            if el.tag == tag and all(el.attrs.get(k) == v for k, v in wanted.items())
        ]

    def field_names(self, form: int = 0) -> set[str]:
        """Names of the input, select and textarea fields in a form, minus the CSRF token."""
        return {
            el.attrs["name"]
            for el in self.elements
            if el.form == form
            and el.tag in {"input", "select", "textarea"}
            and "name" in el.attrs
            and el.attrs.get("type") != "submit"
            and el.attrs["name"] != "csrfmiddlewaretoken"
        }

    def field(self, name: str) -> Element:
        (el,) = (
            el
            for el in self.elements
            if el.tag in {"input", "select", "textarea"} and el.attrs.get("name") == name
        )
        return el

    def options(self, name: str) -> dict[str, Element]:
        """Return the <option>s of the <select> named ``name``, keyed by value."""
        select = self.field(name)
        return {
            el.attrs["value"]: el
            for el in self.elements
            if el.tag == "option" and el.parent is select
        }


class _Parser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.page = Page()
        self._form: int | None = None
        self._select: Element | None = None
        self._last: Element | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        el = Element(tag, {name: value or "" for name, value in attrs}, form=self._form)
        if tag == "option":
            el.parent = self._select
        elif tag == "select":
            self._select = el
        if tag == "form":
            self.page.forms.append(el)
            self._form = len(self.page.forms) - 1
            el.form = self._form
        self.page.elements.append(el)
        self._last = el

    def handle_endtag(self, tag: str) -> None:
        if tag == "form":
            self._form = None
        elif tag == "select":
            self._select = None
        self._last = None

    def handle_data(self, data: str) -> None:
        if self._last is not None:
            self._last.text += data.strip()


def parse_html(content: bytes | str) -> Page:
    """Parse HTML into a flat list of elements, remembering which form each one is in."""
    parser = _Parser()
    parser.feed(content.decode() if isinstance(content, bytes) else content)
    return parser.page


def assert_hx_location(response: HttpResponse, path: str, target: str = "#content") -> None:
    """Assert the response tells htmx to navigate to ``path``, swapping into ``target``."""
    assert response.status_code == 200
    assert json.loads(response["HX-Location"]) == {"path": path, "target": target}


def assert_redirect(response: HttpResponse, path: str) -> None:
    assert response.status_code == 302
    assert response["Location"] == path
