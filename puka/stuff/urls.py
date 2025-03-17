from __future__ import annotations

from django.urls import URLPattern, URLResolver, path

from puka.stuff.views.item import (
    InventoryCreateView,
    InventoryDeleteView,
    InventoryUpdateView,
    ItemCreateView,
    ItemDeleteView,
    ItemDetailView,
    ItemListView,
    ItemUpdateView,
    adjust_inventory,
)
from puka.stuff.views.location import (
    LocationCreateView,
    LocationDeleteView,
    LocationDetailView,
    LocationListView,
    LocationUpdateView,
)

app_name = "stuff"
urlpatterns: list[URLPattern | URLResolver] = [
    path("", ItemListView.as_view(), name="item-list"),
    path("<int:pk>/", ItemDetailView.as_view(), name="item-detail"),
    path("item/new/", ItemCreateView.as_view(), name="item-new"),
    path("item/<int:pk>/edit/", ItemUpdateView.as_view(), name="item-edit"),
    path("item/<int:pk>/delete/", ItemDeleteView.as_view(), name="item-delete"),
    # Location
    path("location/", LocationListView.as_view(), name="location"),
    path("location/<int:pk>/", LocationListView.as_view(), name="location-list"),
    path("location/<int:pk>/detail/", LocationDetailView.as_view(), name="location-detail"),
    path("location/new/", LocationCreateView.as_view(), name="location-new"),
    path("location/<int:pk>/edit/", LocationUpdateView.as_view(), name="location-edit"),
    path("location/<int:pk>/delete/", LocationDeleteView.as_view(), name="location-delete"),
    # Inventory
    path("item/<int:pk>/inventory/new/", InventoryCreateView.as_view(), name="inventory-new"),
    path("inventory/<int:pk>/edit/", InventoryUpdateView.as_view(), name="inventory-edit"),
    path("inventory/<int:pk>/delete/", InventoryDeleteView.as_view(), name="inventory-delete"),
    path("inventory/<int:pk>/adjust/", adjust_inventory, name="inventory-adjust"),
]
