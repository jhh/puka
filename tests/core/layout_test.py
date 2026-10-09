"""The page layout in base.html: drawer, navbar, sidebar nav and the htmx target ids."""

from __future__ import annotations

import pytest
from django.template.loader import render_to_string
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


def test_root_keeps_local_stylesheet_and_deferred_script(admin_client):
    """The root loads only the app CSS; Nix also verifies both assets are served."""
    page = _get(admin_client, reverse("home"))
    stylesheets = [el.attrs["href"] for el in page.find("link", rel="stylesheet")]
    assert stylesheets == ["/static/puka/main.css"]
    (script,) = page.find("script")
    assert "defer" in script.attrs
    assert script.attrs["src"].endswith("puka/main.js")


@pytest.mark.parametrize(
    ("url", "active"),
    [
        ("/", {"Overview"}),
        ("/bookmarks/", {"Bookmarks"}),
        ("/bookmarks/filter/", {"Bookmarks", "Filter"}),
        ("/bookmarks/tags/", {"Bookmarks", "Tags"}),
        ("/stuff/", {"Inventory"}),
        ("/stuff/location/0/", {"Inventory", "Locations"}),
        ("/upkeep/task/", {"Tasks"}),
        ("/upkeep/area/", {"Tasks", "Areas"}),
    ],
)
def test_sidebar_active_item(admin_client, url, active):
    links = _sidebar_links(_get(admin_client, url))
    assert set(links) == {
        "Overview",
        "Bookmarks",
        "Filter",
        "Tags",
        "Inventory",
        "Locations",
        "Tasks",
        "Areas",
        "Admin",
    }
    assert {label for label, cls in links.items() if "menu-active" in cls} == active


@pytest.mark.parametrize(
    ("url", "open_"),
    [
        ("/", False),
        ("/bookmarks/", False),
        ("/bookmarks/filter/", True),
        ("/bookmarks/tags/", True),
        ("/stuff/", False),
        ("/stuff/item/new/", False),
        ("/stuff/location/0/", True),
        ("/upkeep/task/", False),
        ("/upkeep/area/", True),
    ],
)
def test_sidebar_manage_opens_when_active(admin_client, url, open_):
    page = _get(admin_client, url)
    (sidebar,) = page.find("ul", id="sidebar")
    (details,) = (
        el for el in page.elements[page.elements.index(sidebar) :] if el.tag == "details"
    )
    assert ("open" in details.attrs) is open_


def test_sidebar_manage_structure(admin_client):
    """Secondary pages live in a collapsible Manage menu, grouped by section."""
    page = _get(admin_client, reverse("home"))
    (sidebar,) = page.find("ul", id="sidebar")
    elements = page.elements[page.elements.index(sidebar) :]
    (details,) = (el for el in elements if el.tag == "details")
    summary = elements[elements.index(details) + 1]
    assert summary.tag == "summary"
    assert "font-semibold" in summary.attrs.get("class", "").split()
    icon = elements[elements.index(summary) + 1]
    assert icon.tag == "span"
    assert icon.attrs["class"] == "hero-cog-6-tooth size-5"
    assert any(el.tag == "span" and el.text == "Manage" for el in elements)
    titles = [el.text for el in elements if "menu-title" in el.attrs.get("class", "").split()]
    assert titles == ["Bookmarks", "Inventory", "Tasks"]


def test_no_leaked_template_comments(admin_client):
    """Cotton emits multi-line {# #} comments as text; templates use {% comment %}."""
    for url in ("/", "/stuff/", "/upkeep/area/", "/bookmarks/"):
        content = admin_client.get(url).content.decode()
        assert "{#" not in content


def test_sidebar_admin_state(rf):
    """Admin is a Manage item; Django's own admin layout does not render the sidebar."""
    page = parse_html(render_to_string("core/sidebar.html", request=rf.get("/admin/")))
    links = _sidebar_links(page)
    assert "menu-active" in links["Admin"]
    (details,) = page.find("details")
    assert "open" in details.attrs


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


def test_no_stale_drawer_refs(admin_client):
    for url in ("/", "/stuff/", "/upkeep/area/", "/bookmarks/"):
        content = admin_client.get(url).content.decode()
        assert "sidebarDrawer" not in content
        assert "id_extra_menu" not in content


def test_htmx_fragment_has_no_layout(admin_client):
    page = _get(admin_client, reverse("stuff:item-list"), **{"HX-Request": "true"})
    (sidebar,) = page.find("ul", id="sidebar")
    assert sidebar.attrs["hx-swap-oob"] == "true"
    assert "menu-active" in _sidebar_links(page)["Inventory"]
    assert not page.find("input", id="app-drawer")
