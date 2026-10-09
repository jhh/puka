"""
Constant-query rendering guards for template optimization (PLAN.md, Step 3).

Fixture creation and authentication are outside measurement. Direct view dispatch
separates context preparation from deferred template rendering; client requests add
middleware/session overhead. Budgets are ceilings so optimizations can lower them.
See docs/template-baselines.md for the recorded counts and dataset shape.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import pytest
from django.db import connection
from django.template.response import TemplateResponse
from django.test.utils import CaptureQueriesContext
from django.urls import resolve, reverse
from django_htmx.middleware import HtmxDetails

from tests.factories import (
    AreaFactory,
    BookmarkFactory,
    InventoryFactory,
    ItemFactory,
    LocationFactory,
    ScheduleFactory,
    TaskFactory,
    TaskItemFactory,
)
from tests.utils import HTMX

pytestmark = pytest.mark.django_db


@dataclass(frozen=True)
class QueryCase:
    name: str
    preparation: int
    rendering: int
    object_key: str | None = None


CASES = (
    QueryCase("stuff:item-list", 1, 3),
    QueryCase("upkeep:task-list", 1, 1),
    QueryCase("upkeep:area-list", 1, 1),
    QueryCase("stuff:item-detail", 5, 0, "item"),
    QueryCase("stuff:location-detail", 2, 1, "location"),
    QueryCase("upkeep:task-detail", 3, 0, "task"),
    QueryCase("upkeep:area-detail", 4, 0, "area"),
)


@pytest.fixture(params=[1, 3, 15], ids=["small", "larger", "paginated"])
def related_objects(request):
    size = request.param
    locations = [
        LocationFactory.create(code=f"A01-{index + 1:02}", name=f"Location {index}")
        for index in range(size)
    ]
    items = [ItemFactory.create(name=f"Baseline item {index}") for index in range(size)]
    bookmarks = [
        BookmarkFactory.create(url=f"https://example.com/baseline/{index}", active=True)
        for index in range(size)
    ]
    for index, bookmark in enumerate(bookmarks):
        bookmark.tags.add("baseline", f"bookmark-{index}")
    for index, item in enumerate(items):
        item.tags.add("upkeep", f"item-{index}")
        item.bookmarks.add(*bookmarks)
        for location in locations:
            InventoryFactory.create(item=item, location=location, quantity=10)

    areas = [AreaFactory.create(name=f"Baseline area {index}") for index in range(size)]
    for area in areas:
        area.bookmarks.add(*bookmarks)
    tasks = [
        TaskFactory.create(area=areas[0], name=f"Baseline task {index}") for index in range(size)
    ]
    for task in tasks:
        ScheduleFactory.create(task=task, due_date=date(2026, 1, 1))
        ScheduleFactory.create(
            task=task,
            due_date=date(2025, 1, 1),
            completion_date=date(2025, 1, 1),
        )
        for item in items:
            TaskItemFactory.create(task=task, item=item, quantity=1)
    return {
        "size": size,
        "item": items[0].pk,
        "location": locations[0].pk,
        "area": areas[0].pk,
        "task": tasks[0].pk,
    }


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.name)
def test_rendering_query_baseline(  # noqa: PLR0913
    *,
    admin_client,
    admin_user,
    rf,
    related_objects,
    case,
    record_property,
):
    args = [related_objects[case.object_key]] if case.object_key else []
    url = reverse(case.name, args=args)
    match = resolve(url)

    for mode, headers in (("full", {}), ("fragment", HTMX)):
        request = rf.get(url, headers=headers)
        request.user = admin_user
        request.htmx = HtmxDetails(request)

        with CaptureQueriesContext(connection) as preparation:
            response = match.func(request, *match.args, **match.kwargs)
        assert isinstance(response, TemplateResponse)
        assert response.status_code == 200
        with CaptureQueriesContext(connection) as rendering:
            response.render()
        with CaptureQueriesContext(connection) as total:
            client_response = admin_client.get(url, headers=headers)
        assert client_response.status_code == 200
        auth_queries = [
            query
            for query in total
            if 'FROM "django_session"' in query["sql"] or 'FROM "users_customuser"' in query["sql"]
        ]
        overhead = len(auth_queries)
        assert overhead == 2
        assert len(total) == len(preparation) + len(rendering) + overhead
        assert len(preparation) <= case.preparation, preparation.captured_queries
        assert len(rendering) <= case.rendering, rendering.captured_queries
        assert ("<head>" in response.content.decode()) == (mode == "full")
        for name, count in (
            ("preparation", len(preparation)),
            ("rendering", len(rendering)),
            ("authentication", overhead),
            ("total", len(total)),
        ):
            record_property(f"{mode}-{name}", count)


def test_item_results_fragment_query_budget(admin_client, related_objects):
    with CaptureQueriesContext(connection) as queries:
        response = admin_client.get(
            reverse("stuff:item-list"),
            headers={"HX-Request": "true", "HX-Target": "#item-results"},
        )
    assert response.status_code == 200
    assert len(queries) <= 6, queries.captured_queries
    assert len(response.context["items"]) == related_objects["size"]
