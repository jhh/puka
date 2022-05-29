from __future__ import annotations

from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models

from puka.core.models import TimeStampedModel


class BookmarkManager(models.Manager):
    def with_tags(self, tags: list[str]) -> models.QuerySet:
        return super().get_queryset().filter(tags__overlap=tags)


class Bookmark(TimeStampedModel):
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    url = models.URLField(max_length=500)
    tags = ArrayField(models.CharField(max_length=50), blank=True)
    title_description_search = SearchVectorField(null=True, editable=False)

    objects = BookmarkManager()

    class Meta:
        indexes = [
            GinIndex(fields=["tags"]),
            GinIndex(fields=["title_description_search"]),
        ]
        ordering = ["-created"]

    def __str__(self) -> str:
        return self.title
