"""Render each Cotton component from a template string and check the HTML it produces."""

from __future__ import annotations

from urllib.parse import parse_qs, urlsplit

import pytest
from django.template import engines
from django.test import RequestFactory
from django.urls import resolve
from django_cotton.compiler_regex import CottonCompiler

from puka.core.pagination import PageSizePaginator
from tests.utils import Element, Page, parse_html


def render(source: str, request=None, **context) -> str:
    """Compile ``<c-*>`` tags (which only Cotton's loader does) and render the string."""
    template = engines["django"].from_string(CottonCompiler().process(source))
    return template.render(context, request)


def page(source: str, request=None, **context) -> Page:
    return parse_html(render(source, request, **context))


def classes(el: Element) -> list[str]:
    return el.attrs.get("class", "").split()


def only(page: Page, tag: str, **attrs: str) -> Element:
    (el,) = page.find(tag, **attrs)
    return el


# ui/button


def test_button_defaults():
    button = only(page("<c-ui.button>Save</c-ui.button>"), "button")
    assert button.attrs["type"] == "button"
    assert classes(button) == ["btn"]
    assert button.text == "Save"


@pytest.mark.parametrize(
    ("attrs", "expected"),
    [
        ('variant="primary"', ["btn", "btn-primary"]),
        ('variant="error" style="outline"', ["btn", "btn-error", "btn-outline"]),
        ('variant="ghost" size="xs"', ["btn", "btn-ghost", "btn-xs"]),
        ('variant="primary" style="soft" size="sm"', ["btn", "btn-primary", "btn-soft", "btn-sm"]),
        ('variant="link" size="lg" square="1"', ["btn", "btn-link", "btn-lg", "btn-square"]),
        ('class="ml-auto"', ["btn", "ml-auto"]),
    ],
)
def test_button_classes(attrs, expected):
    button = only(page(f"<c-ui.button {attrs}>Go</c-ui.button>"), "button")
    assert classes(button) == expected


def test_button_passes_htmx_and_alpine_attrs():
    source = (
        '<c-ui.button variant="error" type="submit" hx-post="/x/delete/" hx-confirm="Delete?"'
        ' x-bind:disabled="busy" x-on:click="busy = true">Delete</c-ui.button>'
    )
    button = only(page(source), "button")
    assert button.attrs["type"] == "submit"
    assert button.attrs["hx-post"] == "/x/delete/"
    assert button.attrs["hx-confirm"] == "Delete?"
    assert button.attrs["x-bind:disabled"] == "busy"
    assert button.attrs["x-on:click"] == "busy = true"
    for var in ("variant", "style", "size", "icon", "href", "square"):
        assert var not in button.attrs


def test_button_as_link_with_icon():
    source = '<c-ui.button href="/new/" variant="primary" icon="hero-plus" hx-get="/new/">New</c-ui.button>'
    result = page(source)
    assert not result.find("button")
    link = only(result, "a")
    assert link.attrs["href"] == "/new/"
    assert link.attrs["hx-get"] == "/new/"
    assert "type" not in link.attrs
    assert classes(link) == ["btn", "btn-primary"]
    assert classes(only(result, "span")) == ["hero-plus", "size-4"]


# ui/icon


def test_icon():
    icon = only(page('<c-ui.icon name="hero-home" x-show="open" />'), "span")
    assert classes(icon) == ["hero-home", "size-5"]
    assert icon.attrs["aria-hidden"] == "true"
    assert icon.attrs["x-show"] == "open"
    assert "name" not in icon.attrs


def test_icon_class_replaces_default_size():
    icon = only(page('<c-ui.icon name="hero-tag" class="size-3 text-primary" />'), "span")
    assert classes(icon) == ["hero-tag", "size-3", "text-primary"]


# ui/tag_badge


def test_tag_badge():
    source = (
        '<c-ui.tag-badge href="/bookmarks/?tags=ssh" class="mr-1"'
        ' hx-get="?tags=ssh" tabindex="-1">ssh</c-ui.tag-badge>'
    )
    result = page(source)
    link = only(result, "a")
    assert link.attrs["href"] == "/bookmarks/?tags=ssh"
    assert link.attrs["hx-get"] == "?tags=ssh"
    assert link.attrs["tabindex"] == "-1"
    assert classes(link) == ["mr-1"]
    badge = only(result, "span")
    assert classes(badge) == ["badge", "badge-info", "badge-soft", "badge-sm"]
    assert badge.text == "ssh"


# ui/card


def test_card():
    source = """
        <c-ui.card title="Details" id="details" class="mt-4">
            <p>Body</p>
            <c-slot name="actions"><c-ui.button>Edit</c-ui.button></c-slot>
        </c-ui.card>
    """
    result = page(source)
    card = result.elements[0]
    assert card.attrs["id"] == "details"
    assert classes(card) == ["card", "card-border", "border-base-300", "bg-base-100", "mt-4"]
    assert only(result, "h2").text == "Details"
    assert only(result, "p").text == "Body"
    actions = only(result, "div", **{"class": "card-actions justify-end"})
    assert actions is not None
    assert only(result, "button").text == "Edit"


def test_card_without_title_or_actions():
    result = page("<c-ui.card>Body</c-ui.card>")
    assert not result.find("h2")
    assert not [el for el in result.elements if "card-actions" in classes(el)]


def test_card_title_slot():
    source = '<c-ui.card><c-slot name="title"><a href="/x/">Linked</a></c-slot>Body</c-ui.card>'
    result = page(source)
    assert only(result, "a").text == "Linked"
    assert result.find("a")[0] is result.elements[result.elements.index(only(result, "h2")) + 1]


def test_card_header_actions():
    source = """
        <c-ui.card title="Inventory">
            <c-slot name="header_actions"><c-ui.button>Add</c-ui.button></c-slot>
            <p>Body</p>
        </c-ui.card>
    """
    result = page(source)
    assert only(result, "h2").text == "Inventory"
    assert only(result, "button").text == "Add"
    header = only(
        result,
        "div",
        **{"class": "flex flex-wrap items-center justify-between gap-2"},
    )
    assert header is not None


# ui/badge


@pytest.mark.parametrize(
    ("attrs", "expected"),
    [
        ("", ["badge", "badge-soft"]),
        ('variant="primary" style="soft"', ["badge", "badge-primary", "badge-soft"]),
        (
            'variant="warning" size="sm"',
            ["badge", "badge-warning", "badge-soft", "badge-sm"],
        ),
        (
            'variant="neutral" style="outline" size="lg"',
            ["badge", "badge-neutral", "badge-outline", "badge-lg"],
        ),
    ],
)
def test_badge(attrs, expected):
    badge = only(page(f"<c-ui.badge {attrs}>tag 3</c-ui.badge>"), "span")
    assert classes(badge) == expected
    assert badge.text == "tag 3"


# ui/alert


@pytest.mark.parametrize(
    ("variant", "icon"),
    [
        ("info", "hero-information-circle"),
        ("success", "hero-check-circle"),
        ("warning", "hero-exclamation-triangle"),
        ("error", "hero-x-circle"),
    ],
)
def test_alert(variant, icon):
    result = page(f'<c-ui.alert variant="{variant}" style="soft">Heads up</c-ui.alert>')
    alert = result.elements[0]
    assert alert.attrs["role"] == "alert"
    assert classes(alert) == ["alert", f"alert-{variant}", "alert-soft"]
    assert classes(only(result, "span"))[0] == icon
    assert result.elements[-1].text == "Heads up"


def test_alert_custom_and_no_icon():
    custom = page('<c-ui.alert icon="hero-bell">Ding</c-ui.alert>')
    assert classes(only(custom, "span"))[0] == "hero-bell"
    assert not page('<c-ui.alert icon="">Plain</c-ui.alert>').find("span")


# ui/table


def test_table():
    source = """
        <c-ui.table size="sm" zebra="1" pin_rows="1" id="items">
            <thead><tr><th>Name</th></tr></thead>
            <tbody><tr><td>Salt</td></tr></tbody>
        </c-ui.table>
    """
    result = page(source)
    wrapper = result.elements[0]
    assert wrapper.attrs["id"] == "items"
    assert "overflow-x-auto" in classes(wrapper)
    assert classes(only(result, "table")) == ["table", "table-sm", "table-zebra", "table-pin-rows"]
    assert only(result, "td").text == "Salt"


def test_table_defaults():
    assert classes(only(page("<c-ui.table><tbody></tbody></c-ui.table>"), "table")) == ["table"]


# ui/pagination


@pytest.fixture
def rf_get():
    return RequestFactory().get


def _page(number: int):
    return PageSizePaginator(list(range(25)), 10).page(number)


def test_pagination_middle_page(rf_get):
    request = rf_get("/stuff/", {"query": "salt", "page": "2"})
    result = page('<c-ui.pagination :page_obj="page_obj" />', request, page_obj=_page(2))

    assert only(result, "nav").attrs["aria-label"] == "Pagination"
    prev, nxt = (link for link in result.find("a") if link.text in {"Previous", "Next"})
    assert prev.text == "Previous"
    assert prev.attrs["href"] == "?query=salt&page=1"
    assert prev.attrs["hx-get"] == prev.attrs["href"]
    assert prev.attrs["hx-target"] == "#content"
    assert prev.attrs["hx-push-url"] == "true"
    assert nxt.attrs["href"] == "?query=salt&page=3"
    summary = [el.text for el in result.find("span")]
    assert summary == ["11", "20", "25"]

    (sizer,) = result.find("button")
    assert sizer.text == "10 / page"
    assert sizer.attrs["popovertarget"] == "page-size-menu"
    (size_state,) = (
        element for element in result.find("div") if "pageSize(" in element.attrs.get("x-data", "")
    )
    assert size_state.attrs["x-data"] == "pageSize('page-size:/stuff/', '10', '10,25,50,100')"
    assert size_state.attrs["x-init"] == "restore()"

    menu = [link for link in result.find("a") if link.text.endswith(" / page")]
    assert [link.text for link in menu] == ["10 / page", "25 / page", "50 / page", "100 / page"]
    assert [link.attrs.get("aria-current") for link in menu] == ["true", None, None, None]
    for size, link in zip(("10", "25", "50", "100"), menu, strict=True):
        assert link.attrs["hx-get"] == link.attrs["href"]
        assert link.attrs["hx-target"] == "#content"
        assert link.attrs["hx-push-url"] == "true"
        assert link.attrs["data-page-size"] == size
        assert link.attrs["x-on:click"] == f"remember('{size}')"
    assert parse_qs(urlsplit(menu[1].attrs["href"]).query) == {
        "query": ["salt"],
        "page": ["1"],
        "page_size": ["25"],
    }


def test_pagination_page_size_key_uses_view_name(rf_get):
    request = rf_get("/stuff/")
    request.resolver_match = resolve("/stuff/")
    result = page('<c-ui.pagination :page_obj="page_obj" />', request, page_obj=_page(1))

    (size_state,) = (
        element for element in result.find("div") if "pageSize(" in element.attrs.get("x-data", "")
    )
    assert size_state.attrs["x-data"].startswith("pageSize('page-size:stuff:item-list'")


def test_pagination_first_and_last_pages_disable_buttons(rf_get):
    first = page(
        '<c-ui.pagination :page_obj="page_obj" target="#list" />',
        rf_get("/"),
        page_obj=_page(1),
    )
    (disabled,) = (button for button in first.find("button") if button.text == "Previous")
    assert "disabled" in disabled.attrs
    (next_link,) = (link for link in first.find("a") if link.text == "Next")
    assert next_link.attrs["hx-target"] == "#list"

    last = page('<c-ui.pagination :page_obj="page_obj" />', rf_get("/"), page_obj=_page(3))
    (disabled,) = (button for button in last.find("button") if button.text == "Next")
    assert "disabled" in disabled.attrs


def test_pagination_single_page_keeps_the_size_menu(rf_get):
    single = PageSizePaginator([1, 2], 10).page(1)
    result = page('<c-ui.pagination :page_obj="page_obj" />', rf_get("/"), page_obj=single)

    assert result.find("nav")
    assert not [button for button in result.find("button") if button.text in {"Previous", "Next"}]


# ui/breadcrumbs and ui/crumb


def test_breadcrumbs():
    source = """
        <c-ui.breadcrumbs id="breadcrumbs" hx-swap-oob="true">
            <c-ui.crumb href="/">Overview</c-ui.crumb>
            <c-ui.crumb href="/bookmarks/" hx-boost="true">Bookmarks</c-ui.crumb>
            <c-ui.crumb icon="hero-hashtag-mini">django</c-ui.crumb>
        </c-ui.breadcrumbs>
    """
    result = page(source)
    trail = result.elements[0]
    assert trail.attrs["id"] == "breadcrumbs"
    assert trail.attrs["hx-swap-oob"] == "true"
    assert classes(trail) == ["breadcrumbs", "text-sm", "font-semibold"]
    assert len(result.find("li")) == 3
    overview, bookmarks = result.find("a")
    assert (overview.attrs["href"], overview.text) == ("/", "Overview")
    assert bookmarks.attrs["hx-boost"] == "true"
    last = result.find("span")[0]
    assert "href" not in last.attrs
    assert classes(result.find("span")[1])[0] == "hero-hashtag-mini"


# ui/empty-state


def test_empty_state():
    result = page(
        '<c-ui.empty-state title="No schedules"><a href="/new/">Add one</a></c-ui.empty-state>',
    )
    assert classes(only(result, "span"))[0] == "hero-inbox"
    assert only(result, "p").text == "No schedules"
    assert only(result, "a").attrs["href"] == "/new/"


def test_empty_state_without_icon():
    assert not page('<c-ui.empty-state title="Nothing" icon="" />').find("span")


# ui/search-box


def test_search_box_defaults():
    result = page('<c-ui.search-box hx-get="/bookmarks/" hx-target="#id_bookmarks" />')
    root = result.elements[0]
    assert root.attrs["x-data"] == "searchBox"
    assert classes(root) == ["w-80"]
    assert "hx-get" not in root.attrs

    search = result.field("q")
    assert search.attrs["type"] == "search"
    assert search.attrs["id"] == "search"
    assert search.attrs["value"] == ""
    assert search.attrs["placeholder"] == "Search"
    assert search.attrs["x-ref"] == "input"
    assert search.attrs["hx-get"] == "/bookmarks/"
    assert search.attrs["hx-target"] == "#id_bookmarks"
    assert search.attrs["x-on:keydown.meta.k.window.prevent"] == "focus()"
    assert search.attrs["x-on:keydown.ctrl.k.window.prevent"] == "focus()"
    assert search.attrs["x-on:keyup.esc.prevent.stop"] == "reset()"
    assert search.attrs["x-on:clear-search.camel.window"] == "clear()"
    assert [el.text for el in result.find("kbd")] == ["⌘", "K"]


def test_search_box_options():
    source = (
        '<c-ui.search-box name="query" value="{{ query }}" class="w-64"'
        ' hx-get="/upkeep/task/" hx-trigger="change" hx-target="#content" />'
    )
    result = page(source, query='salt "fine"')
    assert classes(result.elements[0]) == ["w-64"]
    search = result.field("query")
    assert search.attrs["value"] == 'salt "fine"'
    assert search.attrs["hx-trigger"] == "change"
    for var in ("name", "value", "placeholder", "id"):
        assert var not in result.elements[0].attrs


# layout/page-header


def test_page_header():
    source = """
        <c-layout.page-header title="Locations">
            <c-slot name="actions"><c-ui.button variant="primary">Add</c-ui.button></c-slot>
        </c-layout.page-header>
    """
    result = page(source)
    assert only(result, "h1").text == "Locations"
    assert only(result, "button").text == "Add"


def test_page_header_title_slot_without_actions():
    result = page(
        '<c-layout.page-header><c-slot name="title"><a href="/">Home</a> :: Shelf</c-slot>'
        "</c-layout.page-header>",
    )
    assert only(result, "a").text == "Home"
    assert len(result.find("div")) == 1


# layout/nav-item


def test_page_meta(rf_get):
    result = page(
        '<c-layout.page-meta title="{{ title }}"><c-ui.crumb>Current page</c-ui.crumb>'
        "</c-layout.page-meta>",
        rf_get("/upkeep/area/"),
        title='Area "quotes" & notes',
    )
    assert only(result, "title").text == 'Area "quotes" & notes'
    crumbs = only(result, "div", id="breadcrumbs")
    sidebar = only(result, "ul", id="sidebar")
    assert crumbs.attrs["hx-swap-oob"] == sidebar.attrs["hx-swap-oob"] == "true"
    assert not result.find("header")
    assert not result.find("input", id="app-drawer")
    active = {link.attrs["href"] for link in result.find("a") if "menu-active" in classes(link)}
    # Areas is a Manage item, so its parent Tasks stays highlighted too.
    assert active == {"/upkeep/task/", "/upkeep/area/"}


@pytest.mark.parametrize(
    ("path", "active"),
    [("/bookmarks/", True), ("/bookmarks/filter/", False), ("/stuff/", False)],
)
def test_nav_item_exact_match(rf_get, path, active):
    result = page(
        '<c-layout.nav-item url_name="bookmarks:list" icon="hero-bookmark">Bookmarks</c-layout.nav-item>',
        rf_get(path),
    )
    link = only(result, "a")
    assert link.attrs["href"] == "/bookmarks/"
    assert ("menu-active" in classes(link)) is active
    assert ("aria-current" in link.attrs) is active
    assert classes(result.find("span")[0]) == ["hero-bookmark", "size-5"]
    assert result.find("span")[1].text == "Bookmarks"
    assert "hx-get" not in link.attrs
    assert "url_name" not in link.attrs


@pytest.mark.parametrize(
    ("path", "active"),
    [("/stuff/location/0/", True), ("/stuff/location/7/detail/", True), ("/stuff/item/1/", False)],
)
def test_nav_item_match_and_arg(rf_get, path, active):
    source = (
        '<c-layout.nav-item url_name="stuff:location-list" :arg="0" match="/stuff/location/"'
        ' target="#content" x-on:click="close()">Locations</c-layout.nav-item>'
    )
    link = only(page(source, rf_get(path)), "a")
    assert link.attrs["href"] == "/stuff/location/0/"
    assert link.attrs["hx-get"] == "/stuff/location/0/"
    assert link.attrs["hx-target"] == "#content"
    assert link.attrs["hx-push-url"] == "true"
    assert link.attrs["x-on:click"] == "close()"
    assert ("menu-active" in classes(link)) is active
    for var in ("arg", "match", "target"):
        assert var not in link.attrs


def test_nav_item_ignores_parent_context(rf_get):
    """Context isolation: a parent's `match` variable doesn't leak into the component."""
    source = '<c-layout.nav-item url_name="home">Overview</c-layout.nav-item>'
    link = only(page(source, rf_get("/bookmarks/"), match="/"), "a")
    assert "menu-active" not in classes(link)


# layout/drawer and layout/navbar


def test_nav_item_children():
    source = """
        <c-layout.nav-item url_name="bookmarks:list">
            Bookmarks
            <c-slot name="children">
                <c-layout.nav-item url_name="bookmarks:filter">Filter</c-layout.nav-item>
            </c-slot>
        </c-layout.nav-item>
    """
    result = page(source, RequestFactory().get("/bookmarks/filter/"))
    outer, inner = result.find("li")
    assert result.elements.index(only(result, "ul")) > result.elements.index(outer)
    parent, child = result.find("a")
    assert "menu-active" not in classes(parent)
    assert "menu-active" in classes(child)
    assert child.attrs["href"] == "/bookmarks/filter/"
    assert inner is not None


def test_nav_item_without_children_has_no_submenu():
    result = page(
        '<c-layout.nav-item url_name="home">Home</c-layout.nav-item>',
        RequestFactory().get("/"),
    )
    assert not result.find("ul")


def test_drawer():
    source = """
        <c-layout.drawer id="app-drawer">
            <main id="content">Page</main>
            <c-slot name="side"><nav id="sidebar">Menu</nav></c-slot>
        </c-layout.drawer>
    """
    result = page(source)
    root = result.elements[0]
    assert classes(root) == ["drawer", "lg:drawer-open"]
    assert root.attrs["x-data"] == "drawer"
    assert root.attrs["x-on:keydown.escape.window"] == "close()"
    assert only(result, "aside").attrs["x-on:click"] == "closeOnLink($event)"
    toggle = only(result, "input")
    assert toggle.attrs["id"] == "app-drawer"
    assert toggle.attrs["type"] == "checkbox"
    assert classes(toggle) == ["drawer-toggle"]
    assert only(result, "main").text == "Page"
    overlay = only(result, "label")
    assert overlay.attrs["for"] == "app-drawer"
    assert classes(overlay) == ["drawer-overlay"]
    assert only(result, "nav", id="sidebar").text == "Menu"
    side = only(result, "aside")
    assert result.elements.index(side) < result.elements.index(only(result, "nav"))


def test_navbar():
    source = """
        <c-layout.navbar drawer="app-drawer">
            <c-slot name="start"><div id="breadcrumbs">Crumbs</div></c-slot>
            <c-slot name="end"><button type="button">Account</button></c-slot>
        </c-layout.navbar>
    """
    result = page(source)
    assert "navbar" in classes(only(result, "header"))
    toggle = only(result, "label")
    assert toggle.attrs["for"] == "app-drawer"
    assert "lg:hidden" in classes(toggle)
    assert only(result, "div", id="breadcrumbs").text == "Crumbs"
    assert only(result, "button").text == "Account"


def test_navbar_without_end():
    result = page("<c-layout.navbar>Title</c-layout.navbar>")
    assert not [el for el in result.elements if "navbar-end" in classes(el)]


# Components used in pages


BOOKMARK_SEARCH = ("q", "/bookmarks/", "input changed delay:0.5s", "#id_bookmarks")
ITEM_SEARCH = ("query", "/stuff/", "input changed delay:0.5s", "#item-results")
AREA_SEARCH = ("query", "/upkeep/area/", "change", "#content")
TASK_SEARCH = ("query", "/upkeep/task/", "change", "#content")


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("url", "htmx", "value", "expected"),
    [
        ("/bookmarks/", False, "", BOOKMARK_SEARCH),
        ("/stuff/?query=salt", False, "salt", ITEM_SEARCH),
        ("/stuff/?query=salt", True, "salt", ITEM_SEARCH),
        ("/upkeep/area/?query=roof", False, "roof", AREA_SEARCH),
        ("/upkeep/task/?query=roof", True, "roof", TASK_SEARCH),
        ("/upkeep/", False, "", TASK_SEARCH),
    ],
)
def test_pages_use_search_box(admin_client, url, htmx, value, expected):
    name, hx_get, trigger, target = expected
    response = admin_client.get(url, headers={"HX-Request": "true"} if htmx else {})
    assert response.status_code == 200
    result = parse_html(response.content)

    assert len([el for el in result.elements if el.attrs.get("x-data") == "searchBox"]) == 1
    search = result.field(name)
    assert search.attrs["x-ref"] == "input"
    assert search.attrs["value"] == value
    assert search.attrs["hx-get"] == hx_get
    assert search.attrs["hx-trigger"] == trigger
    assert search.attrs["hx-target"] == target


@pytest.mark.django_db
@pytest.mark.parametrize("url", ["/bookmarks/filter/", "/stuff/item/1/bookmark/"])
def test_no_inline_scripts(admin_client, url):
    from tests.factories import ItemFactory  # noqa: PLC0415

    ItemFactory.create(pk=1)
    for headers in ({}, {"HX-Request": "true"}):
        result = parse_html(admin_client.get(url, headers=headers).content)
        assert all("src" in el.attrs for el in result.find("script"))


@pytest.mark.parametrize(
    "source",
    [
        '<c-ui.button class="x-extra">Go</c-ui.button>',
        '<c-ui.button href="/" class="x-extra">Go</c-ui.button>',
        '<c-ui.icon name="hero-home" class="x-extra" />',
        '<c-ui.card class="x-extra">Body</c-ui.card>',
        '<c-ui.badge class="x-extra">b</c-ui.badge>',
        '<c-ui.alert class="x-extra">a</c-ui.alert>',
        '<c-ui.table class="x-extra"></c-ui.table>',
        '<c-ui.breadcrumbs class="x-extra"></c-ui.breadcrumbs>',
        '<c-ui.crumb class="x-extra">c</c-ui.crumb>',
        '<c-ui.crumb href="/" class="x-extra">c</c-ui.crumb>',
        '<c-layout.nav-item url_name="home" class="x-extra">n</c-layout.nav-item>',
        '<c-form.form class="x-extra">f</c-form.form>',
        '<c-form.actions class="x-extra" />',
        '<c-ui.empty-state title="t" class="x-extra" />',
        '<c-ui.search-box class="x-extra" />',
        '<c-layout.page-header title="t" class="x-extra" />',
        '<c-layout.drawer class="x-extra">p</c-layout.drawer>',
        '<c-layout.navbar class="x-extra">n</c-layout.navbar>',
        '<c-ui.detail-row label="Name" class="x-extra">value</c-ui.detail-row>',
        '<c-ui.inventory-quantity :inventory_id="7" :quantity="0" class="x-extra" />',
        '<c-layout.manage-dropdown id="manage-test" class="x-extra" />',
    ],
)
def test_class_is_merged_not_duplicated(source):
    html = render(source)
    (tag,) = (line for line in html.split("<") if "x-extra" in line)
    assert tag.count("class=") == 1
