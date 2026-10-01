from __future__ import annotations

from django.urls import reverse
from django.utils import timezone
from django.utils.formats import date_format
from pytest_django.asserts import assertContains, assertNotContains, assertTemplateUsed

from puka.bookmarks.models import Bookmark
from tests.conftest import create_bookmark
from tests.utils import parse_html


def test_bookmarks(admin_client, succulents_bookmark):
    url = reverse("bookmarks:list")
    response = admin_client.get(url)
    assertTemplateUsed(response, "bookmarks/bookmark_list.html")
    assertContains(response, succulents_bookmark.title)
    assertContains(response, succulents_bookmark.description)
    assertContains(response, succulents_bookmark.url)
    assertContains(response, succulents_bookmark.created.strftime("%B %Y").lower())
    for tag in succulents_bookmark.tags.all():
        assertContains(response, tag)


def test_bookmarks_with_tag(admin_client, succulents_bookmark, typewriter_bookmark):
    url = reverse("bookmarks:list")
    response = admin_client.get(f"{url}?tags=humblebrag")
    assertContains(response, succulents_bookmark.title)
    assertNotContains(response, typewriter_bookmark.title)


def test_bookmarks_with_search_tag(
    admin_client,
    succulents_bookmark,
    typewriter_bookmark,
):
    url = reverse("bookmarks:list")
    response = admin_client.get(f"{url}?q=%23humblebrag")
    assertContains(response, succulents_bookmark.title)
    assertNotContains(response, typewriter_bookmark.title)


def test_bookmarks_with_blank_search(
    admin_client,
    succulents_bookmark,
    typewriter_bookmark,
    flannel_bookmark,
):
    url = reverse("bookmarks:list")
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
    url = reverse("bookmarks:list")
    response = admin_client.get(f"{url}?q=aesthetic")
    assertContains(response, flannel_bookmark.title)
    assertContains(response, typewriter_bookmark.title)
    assertNotContains(response, succulents_bookmark)


def test_edit_form_new(admin_client):
    url = reverse("bookmarks:new")
    response = admin_client.get(url)
    assertTemplateUsed(response, "bookmarks/form.html")


def test_bookmarks_htmx_request(admin_client):
    url = reverse("bookmarks:list")
    response = admin_client.get(url, HTTP_HX_REQUEST="true")
    assert "<head>" not in response.content.decode()


def test_create_bookmark(admin_client):
    url = reverse("bookmarks:new")
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
    url = reverse("bookmarks:edit", args=[flannel_bookmark.id])
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
    url = reverse("bookmarks:edit", args=[typewriter_bookmark.id])
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
    assertContains(response, "vaporware pabst")
    assertContains(response, "error")


def test_tags_grouped_by_bucket(admin_client):
    for i in range(6):
        create_bookmark(f"bookmark {i}", url=f"https://example.com/{i}", tags=["common"])
    create_bookmark("rare bookmark", url="https://example.com/rare", tags=["rare"])

    response = admin_client.get(reverse("bookmarks:tags"), headers={"HX-Request": "true"})
    page = parse_html(response.content)

    headings = [el.text for el in page.find("h2")]
    assert headings == ["5—10", "< 5"]
    assert len(page.find("ul")) == 2
    badges = [el.text for el in page.find("span") if "badge" in el.attrs.get("class", "")]
    assert badges == ["common 6", "rare 1"]


def test_bookmark_detail(admin_client, succulents_bookmark):
    response = admin_client.get(reverse("bookmarks:detail", args=[succulents_bookmark.pk]))
    page = parse_html(response.content)

    assert page.find("h1")[0].text == succulents_bookmark.title
    dd = [el.text for el in page.find("dd")]
    assert dd[1] == date_format(
        timezone.localtime(succulents_bookmark.modified),
        "DATETIME_FORMAT",
    )
    assert dd[2] == "Yes"
    badges = {el.text for el in page.find("span") if "badge" in el.attrs.get("class", "")}
    assert badges == {"thundercats", "humblebrag"}


def test_bookmarks_empty_state(admin_client):
    response = admin_client.get(reverse("bookmarks:list") + "?q=nothing-matches")
    assert "No bookmarks found" in response.content.decode()


def test_bookmarks_tag_breadcrumb_oob(admin_client, succulents_bookmark):
    url = reverse("bookmarks:list") + "?tags=humblebrag"
    content = admin_client.get(url, headers={"HX-Request": "true"}).content.decode()
    (crumbs,) = parse_html(content).find("div", id="breadcrumbs")
    assert crumbs.attrs["hx-swap-oob"] == "true"
    trail = content[content.index('id="breadcrumbs"') : content.index("</ul>")]
    assert "hero-hashtag-mini" in trail
    assert "humblebrag" in trail


def test_bookmarks_list_shows_domain(admin_client, succulents_bookmark):
    assertContains(admin_client.get(reverse("bookmarks:list")), "hipsum.co")


def test_bookmarks_oob_breadcrumbs_only_for_htmx(admin_client, succulents_bookmark):
    url = reverse("bookmarks:list")
    full = admin_client.get(url).content.decode()
    assert "hx-swap-oob" not in full
    fragment = admin_client.get(url, headers={"HX-Request": "true"}).content.decode()
    assert 'hx-swap-oob="true"' in fragment
