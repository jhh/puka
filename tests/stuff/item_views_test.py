import pytest
from django.urls import reverse
from faker import Faker
from pytest_django.asserts import assertContains

from puka.bookmarks.models import Bookmark
from puka.stuff.models import Item
from tests.factories import ItemFactory
from tests.utils import parse_html


@pytest.mark.django_db
def test_get_item_list_page(admin_client, salt_item):
    response = admin_client.get(reverse("stuff:item-list"))
    assertContains(response, salt_item.name)


@pytest.mark.django_db
def test_get_item_detail_page(admin_client, salt_item):
    response = admin_client.get(reverse("stuff:item-detail", args=[salt_item.id]))
    assertContains(response, salt_item.name)


@pytest.mark.django_db
class TestItemCreateView:
    def test_happy_path(self, admin_client, item_form_data, location):
        response = admin_client.post(reverse("stuff:item-new"), item_form_data)

        assert response.status_code == 302
        items = list(Item.objects.all())
        assert len(items) == 1

        item = items[0]

        assert item.name == item_form_data["name"]
        assert item.reorder_level == item_form_data["reorder_level"]
        assert item.notes == item_form_data["notes"]

        tags = item.tags.values_list("name", flat=True)
        assert set(tags) == set(item_form_data["tags"].split(","))

        inventories = item.inventories.all()
        assert len(inventories) == 1
        inventory = inventories[0]
        assert inventory.location == location
        assert inventory.quantity == 10

        bookmarks = item.bookmarks.all()
        assert len(bookmarks) == 1
        bookmark = bookmarks[0]
        assert bookmark.title == item.name
        assert not bookmark.active
        assert bookmark.url == item_form_data["bookmark_url"]
        assert list(bookmark.tags.values_list("name", flat=True)) == ["stuff"]

    def test_bookmark_get(self, admin_client, bookmark, item_form_data):
        item_form_data["bookmark_url"] = bookmark.url
        response = admin_client.post(reverse("stuff:item-new"), item_form_data)

        assert response.status_code == 302
        assert Item.objects.all().count() == 1

        assert Bookmark.objects.all().count() == 1

    @pytest.mark.usefixtures("bookmark")
    def test_bookmark_create(self, admin_client, item_form_data):
        item_form_data["bookmark_url"] = Faker().url()
        response = admin_client.post(reverse("stuff:item-new"), item_form_data)

        assert response.status_code == 302
        assert Item.objects.all().count() == 1

        assert Bookmark.objects.all().count() == 2


@pytest.mark.django_db
def test_item_tags_grouped_by_bucket(admin_client):
    for i in range(6):
        ItemFactory.create(name=f"Item {i}").tags.add("common")
    ItemFactory.create(name="Rare item").tags.add("rare")

    response = admin_client.get(reverse("stuff:item-tags"))
    page = parse_html(response.content)

    headings = [el.text for el in page.find("h2")]
    assert headings == ["5—10", "< 5"]
    badges = [el for el in page.find("span") if "badge" in el.attrs.get("class", "")]
    assert [el.text for el in badges] == ["common 6", "rare 1"]
    assert all({"badge-info", "badge-soft"} <= set(el.attrs["class"].split()) for el in badges)

    (common,) = (
        el for el in page.find("a") if el.attrs.get("href", "").endswith("?query=%23common")
    )
    assert common.attrs["href"] == f"{reverse('stuff:item-list')}?query=%23common"
    assert common.attrs["hx-get"] == common.attrs["href"]
    assert common.attrs["hx-target"] == "#content"

    (breadcrumbs,) = page.find("div", id="breadcrumbs")
    crumbs = [
        el.attrs["href"]
        for el in page.elements[page.elements.index(breadcrumbs) :]
        if el.tag == "a"
    ][:3]
    assert crumbs == [
        reverse("home"),
        reverse("stuff:item-list"),
        reverse("stuff:item-tags"),
    ]
