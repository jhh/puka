import pytest

from puka.stuff.forms import ItemForm

FIELD_REQUIRED = ["This field is required."]
WHOLE_NUMBER = ["Enter a whole number."]
POSITIVE_NUMBER = ["Ensure this value is greater than or equal to 0."]


@pytest.mark.django_db
class TestItemForm:
    def test_happy_path(self, item_form_data):
        form = ItemForm(data=item_form_data)
        assert form.errors == {}

    def test_name_required(self, item_form_data):
        item_form_data["name"] = ""
        form = ItemForm(data=item_form_data)
        assert len(form.errors) == 1
        assert form.errors["name"] == FIELD_REQUIRED

    def test_name_unique(self, item_form_data, item_factory):
        item = item_factory()
        item_form_data["name"] = item.name
        form = ItemForm(data=item_form_data)
        assert len(form.errors) == 1
        assert form.errors["name"] == ["This item already exists."]

    @pytest.mark.parametrize(
        ("reorder_level", "msg"),
        [("", FIELD_REQUIRED), ("  ", WHOLE_NUMBER)],
    )
    def test_reorder_level_required(self, item_form_data, reorder_level, msg):
        item_form_data["reorder_level"] = reorder_level
        form = ItemForm(data=item_form_data)
        assert len(form.errors) == 1
        assert form.errors["reorder_level"] == msg

    def test_reorder_level_postive(self, item_form_data):
        item_form_data["reorder_level"] = "-5"
        form = ItemForm(data=item_form_data)
        assert len(form.errors) == 1
        assert form.errors["reorder_level"] == POSITIVE_NUMBER

    def test_tags_required(self, item_form_data):
        item_form_data["tags"] = ""
        form = ItemForm(data=item_form_data)
        assert len(form.errors) == 1
        assert form.errors["tags"] == FIELD_REQUIRED

    @pytest.mark.parametrize("location_code", ["", " ", "  "])
    def test_location_code_not_required(self, item_form_data, location_code):
        item_form_data["location_code"] = location_code
        form = ItemForm(data=item_form_data)
        assert form.errors == {}
        assert not form.cleaned_data["location_code"]

    def test_location_code_parent_required(self, item_form_data):
        item_form_data["location_code"] = "MISSING-PARENT-CODE"
        form = ItemForm(data=item_form_data)
        assert len(form.errors) == 1
        assert form.errors["location_code"] == [
            "Enter a location code with a valid parent location code (MISSING-PARENT not found).",
        ]

    def test_no_location_or_quantity(self, item_form_data):
        item_form_data["location_code"] = ""
        item_form_data["quantity"] = ""
        form = ItemForm(data=item_form_data)
        assert form.errors == {}
        assert not form.cleaned_data["location_code"]
        assert not form.cleaned_data["quantity"]

    @pytest.mark.usefixtures("location")  # load root "A01" fixture
    def test_location_code_parent_get(self, item_form_data):
        item_form_data["location_code"] = "A01-03"
        form = ItemForm(data=item_form_data)
        assert form.errors == {}
        assert form.cleaned_data["location_code"] == "A01-03"

    def test_quantity_requires_location(self, item_form_data):
        item_form_data["quantity"] = ""
        form = ItemForm(data=item_form_data)
        assert len(form.errors) == 1
        assert form.errors["quantity"] == [
            "Quantity must be greater than zero if location provided.",
        ]
