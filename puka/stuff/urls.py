from __future__ import annotations

from django.urls import URLPattern, URLResolver, path

from puka.stuff.views import (
    CategoryCreateView,
    CategoryDeleteView,
    CategoryListView,
    CategoryUpdateView,
    HomeView,
    LocationCreateView,
    LocationDeleteView,
    LocationListView,
    LocationUpdateView,
)

app_name = "stuff"
urlpatterns: list[URLPattern | URLResolver] = [
    path("", HomeView.as_view(), name="home"),
    # Category
    path("category/", CategoryListView.as_view(), name="category-list"),
    path("category/new/", CategoryCreateView.as_view(), name="category-new"),
    path("category/<int:pk>/edit/", CategoryUpdateView.as_view(), name="category-edit"),
    path("category/<int:pk>/delete/", CategoryDeleteView.as_view(), name="category-delete"),
    # Location
    path("location/", LocationListView.as_view(), name="location-list-root"),
    path("location/<int:pk>/", LocationListView.as_view(), name="location-list-children"),
    path("location/new/", LocationCreateView.as_view(), name="location-new"),
    path("location/<int:pk>/edit/", LocationUpdateView.as_view(), name="location-edit"),
    path("location/<int:pk>/delete/", LocationDeleteView.as_view(), name="location-delete"),
]
