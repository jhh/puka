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
    """Sidebar nav-item href -> the link's classes. A nav item labels its link in a <span>."""
    (sidebar,) = page.find("ul", id="sidebar")
    links: dict[str, list[str]] = {}
    current = None
    for el in page.elements[page.elements.index(sidebar) :]:
        if el.tag == "a":
            current = el
        elif el.tag == "span" and el.text and current is not None:
            links[current.attrs.get("href", "")] = current.attrs.get("class", "").split()
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
        ("/", {"/"}),
        ("/bookmarks/", {"/bookmarks/"}),
        ("/bookmarks/filter/", {"/bookmarks/", "/bookmarks/filter/"}),
        ("/bookmarks/tags/", {"/bookmarks/", "/bookmarks/tags/"}),
        ("/stuff/", {"/stuff/"}),
        ("/stuff/item/tags/", {"/stuff/", "/stuff/item/tags/"}),
        ("/stuff/location/0/", {"/stuff/location/0/"}),
        ("/stuff/item/import/", {"/stuff/", "/stuff/item/import/"}),
        ("/upkeep/task/", {"/upkeep/task/"}),
        ("/upkeep/area/", {"/upkeep/task/", "/upkeep/area/"}),
    ],
)
def test_sidebar_active_item(admin_client, url, active):
    links = _sidebar_links(_get(admin_client, url))
    assert set(links) == {
        "/",
        "/bookmarks/",
        "/bookmarks/filter/",
        "/bookmarks/tags/",
        "/stuff/",
        "/stuff/item/tags/",
        "/stuff/location/0/",
        "/stuff/item/import/",
        "/upkeep/task/",
        "/upkeep/area/",
        "/admin/",
    }
    assert {href for href, cls in links.items() if "menu-active" in cls} == active


@pytest.mark.parametrize(
    ("url", "open_"),
    [
        ("/", False),
        ("/bookmarks/", False),
        ("/bookmarks/filter/", True),
        ("/bookmarks/tags/", True),
        ("/stuff/", False),
        ("/stuff/item/new/", False),
        ("/stuff/location/0/", False),
        ("/stuff/item/import/", True),
        ("/stuff/item/tags/", True),
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
    assert "menu-active" in links["/admin/"]
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
        "/stuff/item/tags/",
        "/stuff/item/import/",
        "/upkeep/task/",
        "/upkeep/area/",
        "/admin/",
    } <= hrefs
    assert "#" not in {
        el.attrs["href"] for el in page.find("a") if "gap-3" in el.attrs.get("class", "")
    }


def test_account_menu_closes_on_outside_click(admin_client):
    page = _get(admin_client, reverse("home"))
    assert any(
        el.tag == "details" and el.attrs.get("x-on:click.outside") == "$el.open = false"
        for el in page.elements
    )


def test_account_menu_theme_controller(admin_client):
    page = _get(admin_client, reverse("home"))

    inputs = page.find("input", name="theme")
    assert [el.attrs["value"] for el in inputs] == ["system", "light", "dark"]
    assert [el.attrs["aria-label"] for el in inputs] == [
        "System theme",
        "Light theme",
        "Dark theme",
    ]
    assert all("theme-controller" in el.attrs["class"].split() for el in inputs)
    assert [("checked" in el.attrs) for el in inputs] == [True, False, False]
    (group,) = page.find("div", role="radiogroup", aria_label="Theme")
    assert {"flex", "gap-0", "border", "overflow-hidden", "p-0"} <= set(
        group.attrs["class"].split(),
    )
    labels = [el for el in page.find("label") if "flex-1" in el.attrs.get("class", "").split()]
    assert [el.text for el in labels] == ["", "", ""]
    assert all(
        {"rounded-[var(--radius-field)]", "border-0"} <= set(el.attrs["class"].split())
        for el in labels
    )
    assert any(el.text == "Profile" for el in page.find("span"))
    assert not any(el.text == "Theme" for el in page.find("span"))


@pytest.mark.parametrize(
    ("theme", "data_theme"),
    [("light", "light"), ("dark", "dark"), ("system", None), ("", None)],
)
def test_saved_theme_applies_to_root_and_controller(admin_client, theme, data_theme):
    if theme:
        admin_client.cookies["theme"] = theme

    page = _get(admin_client, reverse("home"))

    (html,) = page.find("html")
    assert html.attrs.get("data-theme") == data_theme
    checked = [
        el.attrs["value"] for el in page.find("input", name="theme") if "checked" in el.attrs
    ]
    expected = theme if theme in {"light", "dark"} else "system"
    assert checked == [expected]


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
    assert "menu-active" in _sidebar_links(page)["/stuff/"]
    assert not page.find("input", id="app-drawer")
