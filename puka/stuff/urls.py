from __future__ import annotations

from django.urls import URLPattern, URLResolver, path

from puka.stuff.views.bookmark import BookmarkSelectView, bookmark_delete_view
from puka.stuff.views.item import (
    InventoryCreateView,
    InventoryDeleteView,
    InventoryUpdateView,
    ItemCreateView,
    ItemDeleteView,
    ItemDetailView,
    ItemImportView,
    ItemListView,
    ItemUpdateView,
    adjust_inventory,
    item_import_errors,
    item_import_template,
)
from puka.stuff.views.location import (
    LocationCreateView,
    LocationDeleteView,
    LocationDetailView,
    LocationListView,
    LocationUpdateView,
)
from puka.stuff.views.location_inventory import (
    LocationInventoryCreateView,
    LocationInventoryDeleteView,
    LocationInventoryMoveView,
    LocationInventoryUpdateView,
    LocationItemCreateView,
)

app_name = "stuff"
urlpatterns: list[URLPattern | URLResolver] = [
    path("", ItemListView.as_view(), name="item-list"),
    path("item/<int:pk>/", ItemDetailView.as_view(), name="item-detail"),
    path("item/new/", ItemCreateView.as_view(), name="item-new"),
    path("item/<int:pk>/edit/", ItemUpdateView.as_view(), name="item-edit"),
    path("item/<int:pk>/delete/", ItemDeleteView.as_view(), name="item-delete"),
    # Item import
    path("item/import/", ItemImportView.as_view(), name="item-import"),
    path("item/import/template/", item_import_template, name="item-import-template"),
    path("item/import/errors/", item_import_errors, name="item-import-errors"),
    # Location
    path("location/", LocationListView.as_view(), name="location"),
    path("location/<int:pk>/", LocationListView.as_view(), name="location-list"),
    path("location/<int:pk>/detail/", LocationDetailView.as_view(), name="location-detail"),
    path("location/new/", LocationCreateView.as_view(), name="location-new"),
    path("location/<int:pk>/edit/", LocationUpdateView.as_view(), name="location-edit"),
    path("location/<int:pk>/delete/", LocationDeleteView.as_view(), name="location-delete"),
    path(
        "location/<int:location_pk>/item/new/",
        LocationItemCreateView.as_view(),
        name="location-item-new",
    ),
    path(
        "location/<int:location_pk>/inventory/new/",
        LocationInventoryCreateView.as_view(),
        name="location-inventory-new",
    ),
    path(
        "location/<int:location_pk>/inventory/<int:pk>/edit/",
        LocationInventoryUpdateView.as_view(),
        name="location-inventory-edit",
    ),
    path(
        "location/<int:location_pk>/inventory/<int:pk>/move/",
        LocationInventoryMoveView.as_view(),
        name="location-inventory-move",
    ),
    path(
        "location/<int:location_pk>/inventory/<int:pk>/delete/",
        LocationInventoryDeleteView.as_view(),
        name="location-inventory-delete",
    ),
    # Inventory
    path("item/<int:pk>/inventory/new/", InventoryCreateView.as_view(), name="inventory-new"),
    path("inventory/<int:pk>/edit/", InventoryUpdateView.as_view(), name="inventory-edit"),
    path("inventory/<int:pk>/delete/", InventoryDeleteView.as_view(), name="inventory-delete"),
    path("inventory/<int:pk>/adjust/", adjust_inventory, name="inventory-adjust"),
    # Bookmark
    path("item/<int:pk>/bookmark/", BookmarkSelectView.as_view(), name="bookmark-select"),
    path("item/<int:item_pk>/bookmark/delete/", bookmark_delete_view, name="bookmark-delete"),
]
