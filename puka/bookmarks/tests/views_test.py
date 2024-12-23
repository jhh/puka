from __future__ import annotations

from django.urls import reverse
from pytest_django.asserts import assertContains, assertNotContains, assertTemplateUsed

from puka.bookmarks.models import Bookmark


def test_bookmarks(admin_client, succulents_bookmark):
    url = reverse("bookmarks")
    response = admin_client.get(url)
    assertTemplateUsed(response, "bookmarks/list.html")
    assertContains(response, succulents_bookmark.title)
    assertContains(response, succulents_bookmark.description)
    assertContains(response, succulents_bookmark.url)
    assertContains(response, succulents_bookmark.created.strftime("%B %Y").lower())
    print(succulents_bookmark.created)
    for tag in succulents_bookmark.tags.all():
        assertContains(response, tag)


def test_bookmarks_with_tag(admin_client, succulents_bookmark, typewriter_bookmark):
    url = reverse("bookmarks")
    response = admin_client.get(f"{url}?t=humblebrag")
    assertContains(response, succulents_bookmark.title)
    assertNotContains(response, typewriter_bookmark.title)


def test_bookmarks_with_search_tag(
    admin_client,
    succulents_bookmark,
    typewriter_bookmark,
):
    url = reverse("bookmarks")
    response = admin_client.get(f"{url}?q=%23humblebrag")
    assertContains(response, succulents_bookmark.title)
    assertNotContains(response, typewriter_bookmark.title)


def test_bookmarks_with_blank_search(
    admin_client,
    succulents_bookmark,
    typewriter_bookmark,
    flannel_bookmark,
):
    url = reverse("bookmarks")
    response = admin_client.get(f"{url}?q=")
    assertContains(response, succulents_bookmark.title)
    assertContains(response, typewriter_bookmark.title)
    assertContains(response, flannel_bookmark.title)


def test_bookmarks_with_text(
    admin_client,
    succulents_bookmark,
    flannel_bookmark,
    typewriter_bookmark,
):
    url = reverse("bookmarks")
    response = admin_client.get(f"{url}?q=aesthetic")
    assertContains(response, flannel_bookmark.title)
    assertContains(response, typewriter_bookmark.title)
    assertNotContains(response, succulents_bookmark)


def test_edit_form_new(admin_client):
    url = reverse("bookmark-new")
    response = admin_client.get(url)
    assertTemplateUsed(response, "bookmarks/form.html")


def test_bookmarks_htmx_request(admin_client):
    url = reverse("bookmarks")
    response = admin_client.get(url, HTTP_HX_REQUEST="true")
    assertTemplateUsed(response, "bookmarks/_list_li.html")


def test_create_bookmark(admin_client):
    url = reverse("bookmark-new")
    response = admin_client.post(
        url,
        {
            "title": "Glossier portland shaman",
            "description": "Sriracha adaptogen viral waistcoat glossier.",
            "url": "https://example.com/99",
            "tags": "hammock,keytar",
            "active": True,
        },
    )
    assert response.status_code == 302
    qs = Bookmark.active_objects.with_tags(["hammock"])
    assert len(qs) == 1


def test_update_bookmark(admin_client, flannel_bookmark):
    url = reverse("bookmark-edit", args=[flannel_bookmark.id])
    response = admin_client.post(
        url,
        {
            "title": flannel_bookmark.title,
            "description": "copper mug pitchfork",
            "url": flannel_bookmark.url,
            "tags": "food,truck",
            "active": True,
        },
    )
    assert response.status_code == 302
    qs = Bookmark.active_objects.with_tags(["hammock"])
    qs = Bookmark.active_objects.with_text("copper")
    assert len(qs) == 1


def test_invalid_update_bookmark(admin_client, typewriter_bookmark):
    url = reverse("bookmark-edit", args=[typewriter_bookmark.id])
    response = admin_client.post(
        url,
        {
            "title": typewriter_bookmark.title,
            "description": "vaporware pabst",
            "url": "not_a_url",
            "tags": "",
        },
    )
    qs = Bookmark.active_objects.with_text("pabst")
    assert len(qs) == 0
    assertTemplateUsed(response, "tailwind/whole_uni_form.html")
    assertContains(response, "vaporware pabst")
    assertContains(response, "error")
