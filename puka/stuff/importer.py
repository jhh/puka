"""CSV bulk import for inventory items, using the same rules as the item create form."""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from io import StringIO
from typing import TYPE_CHECKING

from django.core.exceptions import NON_FIELD_ERRORS

from puka.stuff.forms import ItemForm
from puka.stuff.services import create_item_from_form

if TYPE_CHECKING:
    from django.core.files.uploadedfile import UploadedFile

COLUMNS = (
    "Name",
    "Quantity",
    "Reorder Level",
    "Location Code",
    "Tags",
    "Bookmark URL",
    "Notes",
)
ERROR_COLUMN = "Error"
FORM_FIELDS = {
    "Name": "name",
    "Quantity": "quantity",
    "Reorder Level": "reorder_level",
    "Location Code": "location_code",
    "Tags": "tags",
    "Bookmark URL": "bookmark_url",
    "Notes": "notes",
}
COLUMN_BY_FIELD = {field: column for column, field in FORM_FIELDS.items()}

IMPORT_SESSION_KEY = "stuff.item-import"
ERRORS_SESSION_KEY = "stuff.item-import-errors"


class ImportFormatError(Exception):
    """The uploaded file is not a readable CSV with the expected columns."""


@dataclass
class FailedRow:
    row: dict[str, str]
    errors: str


@dataclass
class ImportResult:
    imported: int = 0
    failed: list[FailedRow] = field(default_factory=list)

    @property
    def total(self) -> int:
        return self.imported + len(self.failed)


def parse_csv(text: str) -> list[dict[str, str]]:
    """Parse CSV text into rows keyed by the known columns; blank rows are skipped."""
    reader = csv.DictReader(StringIO(text))
    headers = reader.fieldnames or []
    missing = [column for column in COLUMNS if column not in headers]
    if missing:
        msg = f"Missing columns: {', '.join(missing)}. Use the template for the expected columns."
        raise ImportFormatError(msg)

    rows: list[dict[str, str]] = []
    for raw in reader:
        row = {column: (raw.get(column) or "").strip() for column in COLUMNS}
        if any(row.values()):
            rows.append(row)
    return rows


def import_rows(rows: list[dict[str, str]]) -> ImportResult:
    """Validate each row with ItemForm and create the valid ones."""
    result = ImportResult()
    for row in rows:
        form = ItemForm(data={FORM_FIELDS[column]: value for column, value in row.items()})
        if form.is_valid():
            create_item_from_form(form)
            result.imported += 1
        else:
            result.failed.append(FailedRow(row=row, errors=error_text(form)))
    return result


def import_upload(upload: UploadedFile) -> ImportResult:
    try:
        text = upload.read().decode("utf-8-sig")
    except UnicodeDecodeError as error:
        msg = "The file must be UTF-8 encoded CSV."
        raise ImportFormatError(msg) from error
    return import_rows(parse_csv(text))


def error_text(form: ItemForm) -> str:
    """One line of field errors, labelled with the CSV column names."""
    parts: list[str] = []
    for name, messages in form.errors.items():
        if name == NON_FIELD_ERRORS:
            parts.extend(str(message) for message in messages)
        else:
            label = COLUMN_BY_FIELD.get(name, name)
            parts.extend(f"{label}: {message}" for message in messages)
    return "; ".join(parts)


def failed_rows_csv(failed: list[FailedRow]) -> str:
    """Return the failed rows as CSV, with the original columns plus an Error column."""
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow([*COLUMNS, ERROR_COLUMN])
    for failure in failed:
        writer.writerow([failure.row[column] for column in COLUMNS] + [failure.errors])
    return output.getvalue()


def template_csv() -> str:
    """Return a blank template: just the header row."""
    output = StringIO()
    csv.writer(output).writerow(COLUMNS)
    return output.getvalue()
