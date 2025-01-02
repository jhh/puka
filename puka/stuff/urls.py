from __future__ import annotations

from django.urls import URLPattern, URLResolver, path

from puka.stuff.views import (
    CategoryCreateView,
    CategoryDeleteView,
    CategoryListView,
    CategoryUpdateView,
    HomeView,
)

app_name = "stuff"
urlpatterns: list[URLPattern | URLResolver] = [
    path("", HomeView.as_view(), name="home"),
    path("category/", CategoryListView.as_view(), name="category-list"),
    path("category/new/", CategoryCreateView.as_view(), name="category-new"),
    path("category/<int:pk>/edit/", CategoryUpdateView.as_view(), name="category-edit"),
    path("category/<int:pk>/delete/", CategoryDeleteView.as_view(), name="category-delete"),
]
