from __future__ import annotations

from django.urls import reverse
from pytest_django.asserts import assertContains
from pytest_django.asserts import assertNotContains
from pytest_django.asserts import assertTemplateUsed


def test_bookmarks(admin_client, succulents_bookmark):
    url = reverse("bookmarks")
    response = admin_client.get(url)
    assertTemplateUsed(response, "partials/bookmarks.html")
    assertContains(response, succulents_bookmark.title)
    assertContains(response, succulents_bookmark.description)
    assertContains(response, succulents_bookmark.url)
    assertContains(response, succulents_bookmark.created.strftime("%B %Y").lower())
    print(succulents_bookmark.created)
    for tag in succulents_bookmark.tags:
        assertContains(response, tag)


def test_bookmarks_with_tag(admin_client, succulents_bookmark, typewriter_bookmark):
    url = reverse("bookmarks")
    response = admin_client.get(f"{url}?t=humblebrag")
    assertContains(response, succulents_bookmark.title)
    assertNotContains(response, typewriter_bookmark.title)


def test_edit_form_new(admin_client):
    url = reverse("bookmark-create")
    response = admin_client.get(url)
    assertTemplateUsed(response, "partials/edit_form.html")
    assertContains(response, "remove translate-x-full")


def test_edit_form_cancel(admin_client):
    url = reverse("bookmark-cancel")
    response = admin_client.get(url)
    assertTemplateUsed(response, "partials/edit_form.html")
    assertContains(response, "add translate-x-full")
