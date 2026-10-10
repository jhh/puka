import csv
from io import StringIO

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from pytest_django.asserts import assertContains

from puka.stuff.importer import (
    COLUMNS,
    ImportFormatError,
    failed_rows_csv,
    import_rows,
    parse_csv,
    template_csv,
)
from puka.stuff.models import Item

ITEM_URL = reverse("stuff:item-import")
TEMPLATE_URL = reverse("stuff:item-import-template")
ERRORS_URL = reverse("stuff:item-import-errors")


def csv_document(*rows: dict[str, str], header=COLUMNS) -> str:
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(header)
    for row in rows:
        writer.writerow([row.get(column, "") for column in COLUMNS])
    return output.getvalue()


def upload(text: str, name: str = "items.csv") -> SimpleUploadedFile:
    return SimpleUploadedFile(name, text.encode(), content_type="text/csv")


@pytest.mark.django_db
class TestParseCsv:
    def test_missing_columns(self):
        with pytest.raises(ImportFormatError, match="Missing columns: Quantity, Location Code"):
            parse_csv("Name,Reorder Level\nWidget,1\n")

    def test_ignores_unknown_columns(self):
        text = csv_document(
            {"Name": "Widget", "Reorder Level": "1", "Tags": "home", "Error": "old error"},
            header=[*COLUMNS, "Error"],
        )
        assert parse_csv(text) == [
            {
                "Name": "Widget",
                "Quantity": "",
                "Reorder Level": "1",
                "Location Code": "",
                "Tags": "home",
                "Bookmark URL": "",
                "Notes": "",
            },
        ]

    def test_skips_blank_rows(self):
        text = csv_document(
            {"Name": "Widget", "Reorder Level": "1", "Tags": "home"},
            {},
            {"Name": "Gadget", "Reorder Level": "2", "Tags": "home"},
        )
        assert [row["Name"] for row in parse_csv(text)] == ["Widget", "Gadget"]


@pytest.mark.django_db
class TestImportRows:
    def test_creates_item_with_inventory_tags_and_bookmark(self, location):
        text = csv_document(
            {
                "Name": "Shelf bracket",
                "Quantity": "4",
                "Reorder Level": "2",
                "Location Code": location.code,
                "Tags": "hardware, shelf",
                "Bookmark URL": "https://example.com/brackets",
                "Notes": "Left wall",
            },
        )
        result = import_rows(parse_csv(text))

        assert result.imported == 1
        assert result.failed == []

        item = Item.objects.get(name="Shelf bracket")
        assert item.reorder_level == 2
        assert item.notes == "Left wall"
        assert set(item.tags.names()) == {"hardware", "shelf"}

        inventory = item.inventories.get()
        assert inventory.location == location
        assert inventory.quantity == 4

        bookmark = item.bookmarks.get()
        assert bookmark.url == "https://example.com/brackets"
        assert bookmark.title == "Shelf bracket"
        assert not bookmark.active
        assert list(bookmark.tags.names()) == ["stuff"]

    @pytest.mark.usefixtures("location")
    def test_creates_child_location(self):
        # The A01 root location exists through the location fixture.
        text = csv_document(
            {
                "Name": "Ladder",
                "Quantity": "1",
                "Reorder Level": "0",
                "Location Code": "A01-05",
                "Tags": "tools",
            },
        )
        result = import_rows(parse_csv(text))

        assert result.imported == 1
        assert Item.objects.get(name="Ladder").inventories.get().location.code == "A01-05"

    def test_keeps_valid_rows_when_another_fails(self, item_factory):
        item_factory(name="Water filter")
        text = csv_document(
            {"Name": "Water filter", "Reorder Level": "1", "Tags": "hvac"},
            {"Name": "New hose", "Reorder Level": "0", "Tags": "garden"},
        )
        result = import_rows(parse_csv(text))

        assert result.imported == 1
        assert result.total == 2
        assert [failure.row["Name"] for failure in result.failed] == ["Water filter"]
        assert result.failed[0].errors == "Name: This item already exists."
        assert Item.objects.filter(name="New hose").exists()

    def test_missing_parent_location(self):
        text = csv_document(
            {"Name": "Widget", "Reorder Level": "0", "Tags": "home", "Location Code": "B99-01"},
        )
        result = import_rows(parse_csv(text))

        assert result.imported == 0
        assert result.failed[0].errors == (
            "Location Code: Enter a location code with a valid parent location code "
            "(B99 not found)."
        )

    def test_zero_quantity_with_location(self, location):
        text = csv_document(
            {
                "Name": "Widget",
                "Quantity": "0",
                "Reorder Level": "0",
                "Location Code": location.code,
                "Tags": "home",
            },
        )
        result = import_rows(parse_csv(text))

        assert result.imported == 0
        assert result.failed[0].errors == (
            "Quantity: Quantity must be greater than zero if location provided."
        )

    def test_invalid_bookmark_url(self):
        text = csv_document(
            {"Name": "Widget", "Reorder Level": "0", "Tags": "home", "Bookmark URL": "not-a-url"},
        )
        result = import_rows(parse_csv(text))

        assert result.imported == 0
        assert result.failed[0].errors == "Bookmark URL: Enter a valid URL."


@pytest.mark.django_db
class TestFailedRowsCsv:
    def test_round_trip_ignores_error_column(self):
        text = csv_document({"Name": "", "Reorder Level": "1", "Tags": "home"})
        result = import_rows(parse_csv(text))
        error_csv = failed_rows_csv(result.failed)

        header = error_csv.splitlines()[0]
        assert header == "Name,Quantity,Reorder Level,Location Code,Tags,Bookmark URL,Notes,Error"
        assert "Name: This field is required." in error_csv

        # Fix the name and resubmit the same file: the Error column is ignored.
        rows = parse_csv(error_csv)
        rows[0]["Name"] = "Fixed widget"
        assert import_rows(rows).imported == 1
        assert Item.objects.filter(name="Fixed widget").exists()


@pytest.mark.django_db
class TestTemplateCsv:
    def test_header_only(self):
        lines = template_csv().strip().splitlines()
        assert lines == ["Name,Quantity,Reorder Level,Location Code,Tags,Bookmark URL,Notes"]


@pytest.mark.django_db
class TestItemImportView:
    def test_page(self, admin_client):
        response = admin_client.get(ITEM_URL)

        assert response.status_code == 200
        assertContains(response, "Download template")
        assertContains(
            response,
            "Name, Quantity, Reorder Level, Location Code, Tags, Bookmark URL, Notes",
        )

    def test_template_download(self, admin_client):
        response = admin_client.get(TEMPLATE_URL)

        assert response.status_code == 200
        assert response["Content-Type"] == "text/csv; charset=utf-8"
        assert "attachment" in response["Content-Disposition"]
        assert response.content.decode().strip() == (
            "Name,Quantity,Reorder Level,Location Code,Tags,Bookmark URL,Notes"
        )

    def test_errors_download_without_import(self, admin_client):
        assert admin_client.get(ERRORS_URL).status_code == 404

    def test_import_success(self, admin_client, location):
        response = admin_client.post(
            ITEM_URL,
            {
                "csv_file": upload(
                    csv_document(
                        {
                            "Name": "Shelf bracket",
                            "Quantity": "4",
                            "Reorder Level": "2",
                            "Location Code": location.code,
                            "Tags": "hardware",
                        },
                    ),
                ),
            },
            follow=True,
        )

        assertContains(response, "Imported 1 item from items.csv.", html=True)
        assert Item.objects.filter(name="Shelf bracket").exists()

    def test_import_with_failures_and_resubmit(self, admin_client, item_factory):
        item_factory(name="Water filter")
        response = admin_client.post(
            ITEM_URL,
            {
                "csv_file": upload(
                    csv_document(
                        {"Name": "Water filter", "Reorder Level": "1", "Tags": "hvac"},
                        {"Name": "New hose", "Reorder Level": "0", "Tags": "garden"},
                    ),
                ),
            },
            follow=True,
        )

        assertContains(response, "Imported 1 of 2 items from items.csv.", html=True)
        assertContains(response, "Download error CSV")
        assert Item.objects.filter(name="New hose").exists()

        errors = admin_client.get(ERRORS_URL)
        assert errors.status_code == 200
        content = errors.content.decode()
        assert content.splitlines()[0].endswith("Error")
        assert "Name: This item already exists." in content

        # Fix the failed row and resubmit; the Error column is ignored.
        rows = parse_csv(content)
        rows[0]["Name"] = "Water filter v2"
        response = admin_client.post(
            ITEM_URL,
            {"csv_file": upload(csv_document(*rows), name="errors-fixed.csv")},
            follow=True,
        )

        assertContains(response, "Imported 1 item from errors-fixed.csv.", html=True)
        assert Item.objects.filter(name="Water filter v2").exists()

    def test_missing_columns(self, admin_client):
        response = admin_client.post(
            ITEM_URL,
            {"csv_file": upload("Name,Reorder Level\nWidget,1\n")},
        )

        assert response.status_code == 200
        assertContains(
            response,
            "Missing columns: Quantity, Location Code, Tags, Bookmark URL, Notes.",
        )

    def test_no_data_rows(self, admin_client):
        response = admin_client.post(
            ITEM_URL,
            {"csv_file": upload(csv_document())},
            follow=True,
        )

        assertContains(response, "No data rows found in items.csv.")

    def test_not_utf8(self, admin_client):
        response = admin_client.post(
            ITEM_URL,
            {"csv_file": SimpleUploadedFile("items.csv", b"Name,\xff\xfe\n")},
        )

        assert response.status_code == 200
        assertContains(response, "The file must be UTF-8 encoded CSV.")

    def test_file_required(self, admin_client):
        response = admin_client.post(ITEM_URL, {})

        assert response.status_code == 200
        assertContains(response, "This field is required.")
