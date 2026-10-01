"""The page layout in base.html: drawer, navbar, sidebar nav and the htmx target ids."""

from __future__ import annotations

import pytest
from django.urls import reverse

from tests.utils import Page, parse_html

pytestmark = pytest.mark.django_db


def _get(client, url: str, **headers) -> Page:
    response = client.get(url, headers=headers)
    assert response.status_code == 200
    return parse_html(response.content)


def _sidebar_links(page: Page) -> dict[str, list[str]]:
    """Sidebar nav-item label -> the link's classes. The label is the link's last <span>."""
    (sidebar,) = page.find("ul", id="sidebar")
    links: dict[str, list[str]] = {}
    current = None
    for el in page.elements[page.elements.index(sidebar) :]:
        if el.tag == "a":
            current = el
        elif el.tag == "span" and el.text and current is not None:
            links[el.text] = current.attrs.get("class", "").split()
            current = None
    return links


def test_layout_ids(admin_client):
    page = _get(admin_client, reverse("stuff:item-list"))

    (toggle,) = page.find("input", id="app-drawer")
    assert toggle.attrs["type"] == "checkbox"
    assert {el.attrs["for"] for el in page.find("label") if "for" in el.attrs} >= {"app-drawer"}
    assert page.find("div", id="breadcrumbs")
    assert page.find("div", id="content")
    assert page.find("header")


def test_root_keeps_stylesheet_and_script_order(admin_client):
    """nix/checks/tests.py reads the second stylesheet and the deferred script."""
    page = _get(admin_client, reverse("home"))
    stylesheets = [el.attrs["href"] for el in page.find("link", rel="stylesheet")]
    assert stylesheets[1].endswith("puka/main.css")
    (script,) = page.find("script")
    assert "defer" in script.attrs
    assert script.attrs["src"].endswith("puka/main.js")


@pytest.mark.parametrize(
    ("url", "active"),
    [
        ("/", {"Overview"}),
        ("/bookmarks/", {"Bookmarks"}),
        ("/bookmarks/filter/", {"Filter"}),
        ("/bookmarks/tags/", {"Tags"}),
        ("/stuff/", {"Inventory"}),
        ("/stuff/location/0/", {"Locations"}),
        ("/upkeep/task/", {"Tasks"}),
        ("/upkeep/area/", {"Areas"}),
    ],
)
def test_sidebar_active_item(admin_client, url, active):
    links = _sidebar_links(_get(admin_client, url))
    assert set(links) == {
        "Overview",
        "Bookmarks",
        "Filter",
        "Inventory",
        "Locations",
        "Tasks",
        "Areas",
        "Tags",
        "Admin",
    }
    assert {label for label, cls in links.items() if "menu-active" in cls} == active


def test_sidebar_hrefs(admin_client):
    page = _get(admin_client, reverse("home"))
    hrefs = {el.attrs["href"] for el in page.find("a")}
    assert {
        "/",
        "/bookmarks/",
        "/bookmarks/filter/",
        "/bookmarks/tags/",
        "/stuff/",
        "/stuff/location/0/",
        "/upkeep/task/",
        "/upkeep/area/",
        "/admin/",
    } <= hrefs
    assert "#" not in {
        el.attrs["href"] for el in page.find("a") if "gap-3" in el.attrs.get("class", "")
    }


def test_navbar_shows_user_and_logout(admin_client, admin_user):
    page = _get(admin_client, reverse("home"))
    content = " ".join(el.text for el in page.elements)
    assert admin_user.email in content
    assert "Register" not in content
    assert "Log in" not in content
    (logout,) = (f for f in page.forms if f.attrs.get("action") == reverse("logout"))
    assert logout.attrs["method"] == "post"


@pytest.mark.parametrize("url", ["/", "/stuff/", "/upkeep/area/", "/bookmarks/"])
def test_no_stale_drawer_refs(admin_client, url):
    content = admin_client.get(url).content.decode()
    assert "sidebarDrawer" not in content
    assert "id_extra_menu" not in content


def test_htmx_fragment_has_no_layout(admin_client):
    page = _get(admin_client, reverse("stuff:item-list"), **{"HX-Request": "true"})
    assert not page.find("ul", id="sidebar")
    assert not page.find("input", id="app-drawer")
