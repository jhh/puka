"""
Smoke tests over every named URL.

Every GET-able URL must render a full page (with ``<head>``). URLs that are swapped into
``#content`` by htmx must return a fragment (without ``<head>``) when ``HX-Request`` is set.
``test_every_named_url_is_covered`` fails when a URL is added without a matching case here.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

import pytest
from django.urls import URLPattern, URLResolver, get_resolver, reverse

from puka.core.views import get_template
from puka.stuff.models import Location
from tests.factories import (
    BookmarkFactory,
    ItemWithInventoryFactory,
    ScheduleFactory,
    TaskItemFactory,
)
from tests.utils import parse_html


class Kind(Enum):
    # GET returns a full page; with HX-Request it returns a fragment for #content.
    FRAGMENT = auto()
    # GET returns a full page and is never requested by non-boosted htmx.
    PAGE = auto()
    # POST/PATCH only; covered by the create/update/delete tests.
    ACTION = auto()


@dataclass(frozen=True)
class Case:
    name: str
    kind: Kind
    # Keys into the ``objects`` fixture, or literal ints, used as URL args.
    args: tuple[str | int, ...] = ()
    id: str | None = None


CASES = (
    Case("home", Kind.PAGE),
    Case("login", Kind.PAGE),
    Case("logout", Kind.ACTION),
    # bookmarks
    Case("bookmarks:list", Kind.FRAGMENT),
    Case("bookmarks:detail", Kind.PAGE, ("bookmark",)),
    Case("bookmarks:new", Kind.PAGE),
    Case("bookmarks:edit", Kind.PAGE, ("bookmark",)),
    Case("bookmarks:delete", Kind.ACTION, ("bookmark",)),
    Case("bookmarks:filter", Kind.FRAGMENT),
    Case("bookmarks:tags", Kind.FRAGMENT),
    # stuff
    Case("stuff:item-list", Kind.FRAGMENT),
    Case("stuff:item-detail", Kind.FRAGMENT, ("item",)),
    Case("stuff:item-new", Kind.FRAGMENT),
    Case("stuff:item-edit", Kind.FRAGMENT, ("item",)),
    Case("stuff:item-delete", Kind.ACTION, ("item",)),
    Case("stuff:location", Kind.FRAGMENT),
    Case("stuff:location-list", Kind.FRAGMENT, (0,), id="stuff:location-list-root"),
    Case("stuff:location-list", Kind.FRAGMENT, ("root_location",), id="stuff:location-list-child"),
    Case("stuff:location-detail", Kind.FRAGMENT, ("location",)),
    Case("stuff:location-new", Kind.FRAGMENT),
    Case("stuff:location-edit", Kind.FRAGMENT, ("location",)),
    Case("stuff:location-delete", Kind.ACTION, ("location",)),
    Case("stuff:inventory-new", Kind.FRAGMENT, ("item",)),
    Case("stuff:inventory-edit", Kind.FRAGMENT, ("inventory",)),
    Case("stuff:inventory-delete", Kind.ACTION, ("inventory",)),
    Case("stuff:inventory-adjust", Kind.ACTION, ("inventory",)),
    Case("stuff:bookmark-select", Kind.FRAGMENT, ("item",)),
    Case("stuff:bookmark-delete", Kind.ACTION, ("item",)),
    # upkeep
    Case("upkeep:home", Kind.FRAGMENT),
    Case("upkeep:task-list", Kind.FRAGMENT),
    Case("upkeep:task-detail", Kind.FRAGMENT, ("task",)),
    Case("upkeep:task-new", Kind.FRAGMENT),
    Case("upkeep:task-edit", Kind.FRAGMENT, ("task",)),
    Case("upkeep:task-delete", Kind.ACTION, ("task",)),
    Case("upkeep:area-list", Kind.FRAGMENT),
    Case("upkeep:area-detail", Kind.FRAGMENT, ("area",)),
    Case("upkeep:area-new", Kind.FRAGMENT),
    Case("upkeep:area-edit", Kind.FRAGMENT, ("area",)),
    Case("upkeep:area-delete", Kind.ACTION, ("area",)),
    Case("upkeep:schedule-new", Kind.FRAGMENT, ("task",)),
    Case("upkeep:schedule-edit", Kind.FRAGMENT, ("schedule",)),
    Case("upkeep:schedule-delete", Kind.ACTION, ("schedule",)),
    Case("upkeep:schedule-toggle", Kind.ACTION, ("schedule",)),
    Case("upkeep:task-item-new", Kind.FRAGMENT, ("task",)),
    Case("upkeep:task-item-edit", Kind.FRAGMENT, ("task_item",)),
    Case("upkeep:task-item-delete", Kind.ACTION, ("task_item",)),
    Case("upkeep:bookmark-select", Kind.FRAGMENT, ("area",)),
    Case("upkeep:bookmark-delete", Kind.ACTION, ("area",)),
)

# Named URLs that come from Django and aren't part of puka's UI.
EXCLUDED_NAMESPACES = {"admin"}
EXCLUDED_NAMES = {
    "password_change",
    "password_change_done",
    "password_reset",
    "password_reset_done",
    "password_reset_confirm",
    "password_reset_complete",
}


def _named_urls(resolver: URLResolver, namespace: str = "") -> set[str]:
    names: set[str] = set()
    for pattern in resolver.url_patterns:
        if isinstance(pattern, URLResolver):
            if pattern.namespace in EXCLUDED_NAMESPACES:
                continue
            prefix = f"{namespace}{pattern.namespace}:" if pattern.namespace else namespace
            names |= _named_urls(pattern, prefix)
        elif isinstance(pattern, URLPattern) and pattern.name:
            names.add(f"{namespace}{pattern.name}")
    return names - EXCLUDED_NAMES


def _params(*kinds: Kind):
    return [pytest.param(case, id=case.id or case.name) for case in CASES if case.kind in kinds]


def _by_name(*names: str):
    """Select representative cases by name for the sampled contract tests."""
    by_name = {case.name: case for case in CASES}
    return [pytest.param(by_name[name], id=name) for name in names]


@pytest.fixture
def objects(db) -> dict[str, int]:
    item = ItemWithInventoryFactory.create()
    inventory = item.inventories.get()
    schedule = ScheduleFactory.create()
    task = schedule.task
    task_item = TaskItemFactory.create(task=task, item=item)
    return {
        "bookmark": BookmarkFactory.create().pk,
        "item": item.pk,
        "inventory": inventory.pk,
        "location": inventory.location.pk,
        "root_location": Location.objects.get_parent(inventory.location).pk,
        "area": task.area.pk,
        "task": task.pk,
        "schedule": schedule.pk,
        "task_item": task_item.pk,
    }


def _url(case: Case, objects: dict[str, int]) -> str:
    args = [objects[arg] if isinstance(arg, str) else arg for arg in case.args]
    return reverse(case.name, args=args)


def test_every_named_url_is_covered():
    assert _named_urls(get_resolver()) == {case.name for case in CASES}


@pytest.mark.parametrize(
    ("headers", "fragment"),
    [
        ({}, False),
        ({"HX-Request": "false"}, False),
        ({"HX-Request": "true"}, True),
        ({"HX-Request": "true", "HX-Target": "div#content"}, True),
        ({"HX-Request": "true", "HX-Target": "body"}, False),
        ({"HX-Request": "true", "HX-Boosted": "true"}, False),
        ({"HX-Request": "true", "HX-History-Restore-Request": "true"}, False),
    ],
)
def test_get_template_response_contract(rf, headers, fragment):
    request = rf.get("/", headers=headers)
    template = "stuff/item_list.html"
    assert get_template(request, template, "#list-partial") == [
        template + "#list-partial" if fragment else template,
    ]


@pytest.mark.parametrize("case", _params(Kind.FRAGMENT, Kind.PAGE))
def test_response_contract(admin_client, objects, case):
    """Full GETs render the shell; htmx GETs render a fragment or a document."""
    url = _url(case, objects)

    response = admin_client.get(url)
    assert response.status_code == 200
    assert "<head>" in response.content.decode()
    page = parse_html(response.content)
    assert page.find("title")
    if case.name != "login":
        assert page.find("div", id="content")
        assert page.find("div", id="breadcrumbs")
        assert page.find("ul", id="sidebar")

    response = admin_client.get(url, headers={"HX-Request": "true"})
    assert response.status_code == 200
    content = response.content.decode()
    if case.kind is Kind.FRAGMENT:
        assert content.strip()
        assert "<head>" not in content
        assert "<html" not in content
    else:
        assert "<head>" in content

    response = admin_client.get(url, headers={"HX-Request": "true", "HX-Boosted": "true"})
    assert response.status_code == 200
    assert "<head>" in response.content.decode()
    assert "hx-swap-oob" not in response.content.decode()


@pytest.mark.parametrize(
    "case",
    _by_name("stuff:item-list", "stuff:item-detail", "upkeep:area-detail"),
)
@pytest.mark.parametrize(
    "headers",
    [
        {"HX-Request": "true", "HX-Target": "body"},
        {"HX-Request": "true", "HX-History-Restore-Request": "true"},
    ],
    ids=["body-target", "history-restore"],
)
def test_document_requests_preserve_shell(admin_client, objects, case, headers):
    response = admin_client.get(_url(case, objects), headers=headers)
    assert response.status_code == 200
    page = parse_html(response.content)
    assert page.find("head")
    assert len(page.find("div", id="content")) == 1
    assert len(page.find("div", id="breadcrumbs")) == 1
    assert len(page.find("ul", id="sidebar")) == 1
    assert "hx-swap-oob" not in response.content.decode()


@pytest.mark.parametrize(
    "case",
    _by_name(
        "bookmarks:list",
        "bookmarks:filter",
        "stuff:item-list",
        "upkeep:task-list",
        "upkeep:area-list",
        "stuff:item-detail",
        "stuff:location-detail",
        "upkeep:task-detail",
        "upkeep:area-detail",
    ),
)
def test_content_fragment_metadata_matches_full_page(admin_client, objects, case):
    url = _url(case, objects)
    full_response = admin_client.get(url)
    full = parse_html(full_response.content)
    response = admin_client.get(url, headers={"HX-Request": "true", "HX-Target": "div#content"})
    assert response.status_code == 200
    fragment = parse_html(response.content)
    (title,) = fragment.find("title")
    assert title.text == full.find("title")[0].text
    (crumbs,) = fragment.find("div", id="breadcrumbs")
    (sidebar,) = fragment.find("ul", id="sidebar")
    assert crumbs.attrs["hx-swap-oob"] == sidebar.attrs["hx-swap-oob"] == "true"
    assert not fragment.find("div", id="content")
    assert not fragment.find("header")
    trails = []
    for content in (full_response.content.decode(), response.content.decode()):
        start = content.index('id="breadcrumbs"')
        end = content.index("</ul>", start)
        trails.append(
            [
                (el.attrs.get("href"), el.text)
                for el in parse_html(content[start:end]).elements
                if el.text or el.tag == "a"
            ],
        )
    assert trails[0] == trails[1]
    full_active = {
        el.attrs["href"] for el in full.find("a") if "menu-active" in el.attrs.get("class", "")
    }
    fragment_active = {
        el.attrs["href"] for el in fragment.find("a") if "menu-active" in el.attrs.get("class", "")
    }
    assert fragment_active == full_active


def test_anonymous_redirects_to_login(client, objects):
    login = reverse("login")
    for case in CASES:
        if case.kind not in {Kind.FRAGMENT, Kind.PAGE}:
            continue
        response = client.get(_url(case, objects))
        if case.name == "login":
            assert response.status_code == 200
        else:
            assert response.status_code == 302
            assert response["Location"].startswith(login)
