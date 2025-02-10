from django.db import models
from treebeard.mp_tree import MP_Node

from puka.bookmarks.models import Bookmark


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class Location(MP_Node):
    name: models.CharField = models.CharField(max_length=100, unique=True)
    alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    node_order_by = ("name",)

    def __str__(self):
        return f"Location: {self.name}"


class Product(models.Model):
    name = models.CharField(max_length=100, unique=True)
    current_stock = models.PositiveIntegerField()
    reorder_level = models.PositiveIntegerField()
    category = models.ForeignKey(Category, related_name="products", on_delete=models.CASCADE)
    location = models.ForeignKey(Location, related_name="products", on_delete=models.CASCADE)
    bookmarks = models.ManyToManyField(Bookmark, related_name="+")
    notes = models.TextField(blank=True)

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
