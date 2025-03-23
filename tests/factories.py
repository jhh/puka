from factory.declarations import RelatedFactory, SubFactory
from factory.django import DjangoModelFactory
from factory.faker import Faker

from puka.bookmarks.models import Bookmark
from puka.stuff.models import Inventory, Item, Location


class BookmarkFactory(DjangoModelFactory):
    class Meta:  # type: ignore[override]
        model = Bookmark

    title = Faker("sentence")
    description = Faker("sentence")
    url = Faker("url")
    active = Faker("boolean")


class LocationFactory(DjangoModelFactory):
    class Meta:  # type: ignore[override]
        model = Location
        django_get_or_create = ("code",)

    name = "A01-02"
    code = "A01-02"

    @classmethod
    def _create(cls, model_class, *_args, **kwargs):
        qs = model_class.objects.filter(code="A01")
        if not qs:
            model_class.add_root(name="A01", code="A01")
        return model_class.objects.get(pk=qs.get().pk).add_child(**kwargs)


class ItemFactory(DjangoModelFactory):
    class Meta:  # type: ignore[override]
        model = Item

    name = "Test Item"
    reorder_level = 1
    notes = Faker("sentence")


class InventoryFactory(DjangoModelFactory):
    class Meta:  # type: ignore[override]
        model = Inventory

    item = SubFactory(ItemFactory)
    location = SubFactory(LocationFactory)
    quantity = 10


class ItemWithInventoryFactory(ItemFactory):
    class Meta:  # type: ignore[override]
        skip_postgeneration_save = True

    inventory = RelatedFactory(InventoryFactory, factory_related_name="item")
