from __future__ import annotations

import pytest
from django.urls import reverse
from pytest_django.asserts import assertContains
from pytest_django.asserts import assertTemplateUsed


@pytest.mark.django_db
def test_bookmarks(client, succulents_bookmark):
    url = reverse("bookmarks")
    response = client.get(url)
    assertTemplateUsed(response, "bookmarks.html")
    assertContains(response, succulents_bookmark.title)
    assertContains(response, succulents_bookmark.description)
    assertContains(response, succulents_bookmark.url)
    assertContains(response, succulents_bookmark.created.strftime("%B %Y").lower())
    print(succulents_bookmark.created)
    for tag in succulents_bookmark.tags:
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
