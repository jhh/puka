from datetime import time

from factory.declarations import RelatedFactory, SubFactory
from factory.django import DjangoModelFactory
from factory.faker import Faker

from puka.bookmarks.models import Bookmark
from puka.stuff.models import Inventory, Item, Location
from puka.upkeep.models import Area, Task


class BookmarkFactory(DjangoModelFactory):
    class Meta:
        model = Bookmark

    title = Faker("sentence")
    description = Faker("sentence")
    url = Faker("url")
    active = Faker("boolean")


class LocationFactory(DjangoModelFactory):
    class Meta:
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
    class Meta:
        model = Item

    name = "Test Item"
    reorder_level = 1
    notes = Faker("sentence")


class InventoryFactory(DjangoModelFactory):
    class Meta:
        model = Inventory

    item = SubFactory(ItemFactory)
    location = SubFactory(LocationFactory)
    quantity = 10


class ItemWithInventoryFactory(ItemFactory):
    class Meta:
        skip_postgeneration_save = True

    inventory = RelatedFactory(InventoryFactory, factory_related_name="item")


class AreaFactory(DjangoModelFactory):
    class Meta:
        model = Area

    name = "Test Area"
    notes = Faker("sentence")


class TaskFactory(DjangoModelFactory):
    class Meta:
        model = Task

    name = "Test Task"
    notes = Faker("sentence")
    duration = time(hour=1, minute=30)
    interval = 6
    frequency = "months"
    area = SubFactory(AreaFactory)
