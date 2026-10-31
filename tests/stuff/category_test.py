import pytest
from django.db.models.deletion import ProtectedError

from puka.stuff.models import Category

pytestmark = pytest.mark.django_db


class TestCategory:
    def test_ordered_by_name(self, category_factory):
        category_factory(name="Tools")
        category_factory(name="Electronics")
        category_factory(name="Hardware")

        assert list(Category.objects.values_list("name", flat=True)) == [
            "Electronics",
            "Hardware",
            "Tools",
        ]

    def test_natural_key(self, category_factory):
        category = category_factory(name="Tools")

        assert category.natural_key() == ("Tools",)
        assert Category.objects.get_by_natural_key("Tools") == category

    def test_delete_is_protected_while_items_use_it(self, category_factory, item_factory):
        category = category_factory(name="Tools")
        item_factory(category=category)

        with pytest.raises(ProtectedError):
            category.delete()
