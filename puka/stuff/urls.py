from __future__ import annotations

from django.urls import URLPattern, URLResolver, path

from puka.stuff.views import (
    LocationCreateView,
    LocationDeleteView,
    LocationListView,
    LocationUpdateView,
    ProductCreateView,
    ProductDeleteView,
    ProductDetailView,
    ProductListView,
    ProductUpdateView,
)

app_name = "stuff"
urlpatterns: list[URLPattern | URLResolver] = [
    path("", ProductListView.as_view(), name="product-list"),
    path("<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
    path("product/new/", ProductCreateView.as_view(), name="product-new"),
    path("product/<int:pk>/edit/", ProductUpdateView.as_view(), name="product-edit"),
    path("product/<int:pk>/delete/", ProductDeleteView.as_view(), name="product-delete"),
    # Location
    path("location/", LocationListView.as_view(), name="location-list-root"),
    path("location/<int:pk>/", LocationListView.as_view(), name="location-list-children"),
    path("location/new/", LocationCreateView.as_view(), name="location-new"),
    path("location/<int:pk>/edit/", LocationUpdateView.as_view(), name="location-edit"),
    path("location/<int:pk>/delete/", LocationDeleteView.as_view(), name="location-delete"),
]
