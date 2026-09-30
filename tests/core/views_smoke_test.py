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

from puka.stuff.models import Location
from tests.factories import (
    BookmarkFactory,
    ItemWithInventoryFactory,
    ScheduleFactory,
    TaskItemFactory,
)


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


@pytest.mark.parametrize("case", _params(Kind.FRAGMENT, Kind.PAGE))
def test_full_page(admin_client, objects, case):
    response = admin_client.get(_url(case, objects))
    assert response.status_code == 200
    assert "<head>" in response.content.decode()


@pytest.mark.parametrize("case", _params(Kind.FRAGMENT))
def test_htmx_fragment(admin_client, objects, case):
    response = admin_client.get(_url(case, objects), headers={"HX-Request": "true"})
    assert response.status_code == 200
    content = response.content.decode()
    assert content.strip()
    assert "<head>" not in content
    assert "<html" not in content


@pytest.mark.parametrize("name", ["bookmarks:list", "stuff:item-detail"])
def test_boosted_request_gets_full_page(admin_client, objects, name):
    case = next(case for case in CASES if case.name == name)
    headers = {"HX-Request": "true", "HX-Boosted": "true"}
    response = admin_client.get(_url(case, objects), headers=headers)
    assert response.status_code == 200
    assert "<head>" in response.content.decode()


@pytest.mark.parametrize("case", _params(Kind.FRAGMENT, Kind.PAGE))
def test_anonymous_redirects_to_login(client, objects, case):
    response = client.get(_url(case, objects))
    if case.name == "login":
        assert response.status_code == 200
    else:
        assert response.status_code == 302
        assert response["Location"].startswith(reverse("login"))
