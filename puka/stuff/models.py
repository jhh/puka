from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVectorField
from django.db import models
from django.db.models import F
from taggit.managers import TaggableManager
from treebeard.mp_tree import MP_Node

from puka.bookmarks.models import Bookmark


class Location(MP_Node):
    name: models.CharField = models.CharField(max_length=100, unique=True)
    alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    node_order_by = ("name",)

    def __str__(self):
        return self.name


class ProductManager(models.Manager):
    def with_tags(self, tags: list[str]) -> models.QuerySet:
        return self.get_queryset().filter(tags__name__in=tags).distinct()

    def with_text(self, text: str) -> models.QuerySet:
        query = SearchQuery(text, search_type="websearch", config="english")
        return (
            self.get_queryset()
            .annotate(rank=SearchRank(F("name_notes_search"), query))
            .filter(rank__gte=0.1)
            .order_by("-rank")
        )


class Product(models.Model):
    name = models.CharField(max_length=100, unique=True)
    current_stock = models.PositiveIntegerField()
    reorder_level = models.PositiveIntegerField()
    location = models.ForeignKey(Location, related_name="products", on_delete=models.CASCADE)
    bookmarks = models.ManyToManyField(Bookmark, related_name="+")
    tags = TaggableManager()
    notes = models.TextField(blank=True)
    name_notes_search = SearchVectorField(null=True, editable=False)

    objects = ProductManager()

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class InventoryTransaction(models.Model):
    product = models.ForeignKey(Product, related_name="transactions", on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    type = models.CharField(max_length=4, choices=(("IN", "In"), ("OUT", "Out")))
    quantity = models.PositiveIntegerField()
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ("-date",)
        verbose_name = "Inventory Transaction"
        verbose_name_plural = "Inventory Transactions"

    def __str__(self):
        return f"{self.product} {self.type} {self.quantity} on {self.date}"
