from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVectorField
from django.db import models
from django.db.models import F
from taggit.managers import TaggableManager
from treebeard.mp_tree import MP_Node

from puka.bookmarks.models import Bookmark


class Location(MP_Node):
    name: models.CharField = models.CharField(max_length=100)
    code: models.CharField = models.CharField(max_length=25, unique=True)
    alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    node_order_by = ("name",)

    def __str__(self):
        return self.code


class ItemManager(models.Manager["Item"]):
    def with_tag(self, tag: str) -> models.QuerySet["Item"]:
        return self.get_queryset().filter(tags__name__iexact=tag).order_by("name")

    def with_text(self, text: str) -> models.QuerySet["Item"]:
        query = SearchQuery(text, search_type="websearch", config="english")
        return (
            self.get_queryset()
            .annotate(rank=SearchRank(F("name_notes_search"), query))
            .filter(rank__gte=0.1)
            .order_by("-rank")
        )

    def with_location(self, location: str) -> models.QuerySet["Item"]:
        return self.filter(locations__code__istartswith=location)

    def search(self, text: str) -> models.QuerySet["Item"]:
        query = text.strip()
        if query.startswith("#"):
            tag = query[1:]
            return self.with_tag(tag)
        if query.startswith("@"):
            location = query[1:]
            return self.with_location(location).order_by("locations__code")
        if query:
            return self.with_text(query)
        return self.all()


class Item(models.Model):
    name = models.CharField(max_length=100, unique=True)
    reorder_level = models.PositiveIntegerField()
    locations: models.ManyToManyField = models.ManyToManyField(
        Location,
        related_name="items",
        through="Inventory",
    )
    bookmarks = models.ManyToManyField(Bookmark, related_name="+")
    tags = TaggableManager()
    notes = models.TextField(blank=True)
    name_notes_search = SearchVectorField(null=True, editable=False)

    objects: ItemManager = ItemManager()  # type: ignore[override]

    class Meta:
        ordering = ("name",)
        indexes = (GinIndex(fields=["name_notes_search"]),)

    def __str__(self):
        return self.name


class Inventory(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="inventories")
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="inventories")
    quantity = models.PositiveIntegerField()

    class Meta:
        ordering = ("item__name",)
        verbose_name = "Inventory"
        verbose_name_plural = "Inventories"
        constraints = (
            models.UniqueConstraint(fields=["item", "location"], name="unique_item_location"),
        )

    def __str__(self):
        return f"{self.item} {self.quantity}"
