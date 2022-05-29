from __future__ import annotations

import pytest
from django.urls import reverse
from pytest_django.asserts import assertContains
from pytest_django.asserts import assertTemplateUsed


@pytest.mark.django_db
def test_bookmarks(client, hipsum_bookmark):
    url = reverse("bookmarks")
    response = client.get(url)
    assertTemplateUsed(response, "bookmarks.html")
    assertContains(response, hipsum_bookmark.title)
    assertContains(response, hipsum_bookmark.description)
    assertContains(response, hipsum_bookmark.url)
    for tag in hipsum_bookmark.tags:
        assertContains(response, tag)


def test_edit_form_new(client):
    url = reverse("bookmark-new")
    response = client.get(url)
    assertTemplateUsed(response, "partials/edit_form.html")
    assertContains(response, "remove translate-x-full")


def test_edit_form_cancel(client):
    url = reverse("bookmark-cancel")
    response = client.get(url)
    assertTemplateUsed(response, "partials/edit_form.html")
    assertContains(response, "add translate-x-full")
