"""The ``page_size`` query parameter selects items per page on list views."""

from __future__ import annotations

import pytest
from django.urls import reverse

from puka.core.pagination import DEFAULT_PAGE_SIZE, PAGE_SIZE_OPTIONS
from tests.factories import AreaFactory, ItemFactory, TaskFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def tasks():
    return [TaskFactory.create(name=f"Task {index:02}") for index in range(30)]


def test_page_size_defaults_to_ten(admin_client, tasks):
    response = admin_client.get(reverse("upkeep:task-list"))
    page_obj = response.context["page_obj"]

    assert page_obj.paginator.per_page == DEFAULT_PAGE_SIZE
    assert len(page_obj.object_list) == DEFAULT_PAGE_SIZE


@pytest.mark.parametrize(
    "size",
    [size for size in PAGE_SIZE_OPTIONS if size != DEFAULT_PAGE_SIZE],
)
def test_page_size_query_parameter(admin_client, tasks, size):
    response = admin_client.get(reverse("upkeep:task-list"), {"page_size": size})
    page_obj = response.context["page_obj"]

    assert page_obj.paginator.per_page == size
    assert len(page_obj.object_list) == min(size, len(tasks))


@pytest.mark.parametrize("size", ["0", "-5", "7", "lots", "10.5"])
def test_invalid_page_size_falls_back_to_default(admin_client, tasks, size):
    response = admin_client.get(reverse("upkeep:task-list"), {"page_size": size})

    assert response.context["page_obj"].paginator.per_page == DEFAULT_PAGE_SIZE


@pytest.mark.parametrize(
    "name",
    ["upkeep:home", "upkeep:task-list", "upkeep:area-list", "stuff:item-list"],
)
def test_page_size_applies_to_each_paginated_list(admin_client, name):
    response = admin_client.get(reverse(name), {"page_size": 25})

    assert response.status_code == 200
    assert response.context["page_obj"].paginator.per_page == 25


@pytest.mark.parametrize(
    ("name", "owner_factory"),
    [("stuff:bookmark-select", ItemFactory), ("upkeep:bookmark-select", AreaFactory)],
)
def test_page_size_applies_to_bookmark_pickers(admin_client, name, owner_factory):
    owner = owner_factory.create()
    response = admin_client.get(reverse(name, args=[owner.pk]), {"page_size": 25})

    assert response.status_code == 200
    assert response.context["page_obj"].paginator.per_page == 25
