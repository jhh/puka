from __future__ import annotations

from typing import TYPE_CHECKING, cast

from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVectorField
from django.db import models
from django.db.models import Count, F, Q, Sum
from django.urls import reverse
from taggit.managers import TaggableManager
from taggit.models import Tag
from treebeard.mp_tree import MP_Node

from puka.bookmarks.models import Bookmark

if TYPE_CHECKING:
    from puka.upkeep.models import Area


class Location(MP_Node):
    # treebeard's paths are base62: "Z" sorts before "a" in byte order, but
    # not under locales such as en_US.UTF-8. Force the column to C so path
    # ordering, lookups, and the unique index match the path alphabet.
    path = models.CharField(max_length=255, unique=True, db_collation="C")
    name: models.CharField = models.CharField(max_length=100)
    code: models.CharField = models.CharField(max_length=25, unique=True)
    alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    node_order_by = ("name",)
    inventories: models.Manager[Inventory]
    areas: models.Manager[Area]

    def __str__(self):
        return self.code


class CategoryManager(models.Manager["Category"]):
    def get_by_natural_key(self, name: str) -> Category:
        return self.get(name=name)

    def find(self, value: str | int) -> Category | None:
        """Find a category by primary key or slug."""
        lookup = Q(slug=str(value))
        if str(value).isdecimal():
            lookup |= Q(pk=value)
        return self.filter(lookup).first()


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True, null=True)

    objects = CategoryManager()

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.name,)


class ItemQuerySet(models.QuerySet["Item"]):
    def with_category(self, category: Category | int | str) -> ItemQuerySet:
        if isinstance(category, Category):
            return self.filter(category=category)
        if isinstance(category, int):
            return self.filter(category_id=category)
        found = Category.objects.find(category)
        if found is None:
            return self.none()
        return self.filter(category=found)

    def top_tags(self, limit: int) -> models.QuerySet[Tag]:
        """Most-used tags on the items in this queryset, highest count first."""
        relname = self.model.tags.through.tag_relname()
        return (
            Tag.objects.filter(
                **{
                    f"{relname}__content_type": ContentType.objects.get_for_model(self.model),
                    f"{relname}__object_id__in": self.order_by().values("pk"),
                },
            )
            .annotate(num_times=Count(relname))
            .order_by("-num_times", "name")[:limit]
        )


class ItemManager(models.Manager["Item"]):
    def get_queryset(self) -> ItemQuerySet:
        return ItemQuerySet(self.model, using=self._db)

    def with_tag(self, tag: str) -> ItemQuerySet:
        return self.get_queryset().filter(tags__name__iexact=tag).order_by("name")

    def with_text(self, text: str) -> ItemQuerySet:
        query = SearchQuery(text, search_type="websearch", config="english")
        return (
            self.get_queryset()
            .annotate(rank=SearchRank(F("name_notes_search"), query))
            .filter(rank__gte=0.1)
            .order_by("-rank")
        )

    def with_location(self, location: str) -> ItemQuerySet:
        return cast("ItemQuerySet", self.filter(locations__code__istartswith=location))

    def with_category(self, category: Category | int | str) -> ItemQuerySet:
        return self.get_queryset().with_category(category)

    def search(self, text: str) -> ItemQuerySet:
        query = text.strip()
        if query.startswith("#"):
            tag = query[1:]
            return self.with_tag(tag)
        if query.startswith("@"):
            location = query[1:]
            return self.with_location(location).order_by("locations__code")
        if query:
            return self.with_text(query)
        return cast("ItemQuerySet", self.order_by("name").all())

    def get_by_natural_key(self, name):
        return self.get(name=name)


class Item(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(
        Category,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="items",
    )
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

    objects = ItemManager()
    inventories: models.Manager[Inventory]

    class Meta:
        ordering = ("name",)
        indexes = (GinIndex(fields=["name_notes_search"]),)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("stuff:item-detail", kwargs={"pk": self.pk})

    def natural_key(self):
        return (self.name,)

    def quantity(self):
        inventory = Inventory.objects.filter(item=self).aggregate(quantity=Sum("quantity"))
        return inventory["quantity"] or 0


class Inventory(models.Model):
    item_id: int
    location_id: int
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="inventories")
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="inventories")
    quantity = models.PositiveIntegerField()

    class Meta:
        ordering = ("location__name",)
        verbose_name = "Inventory"
        verbose_name_plural = "Inventories"
        constraints = (
            models.UniqueConstraint(fields=["item", "location"], name="unique_item_location"),
        )

    def __str__(self):
        return f"{self.item} {self.quantity}"

    def get_absolute_url(self):
        return reverse("stuff:item-detail", kwargs={"pk": self.item.pk})
