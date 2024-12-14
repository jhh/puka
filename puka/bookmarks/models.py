from __future__ import annotations

import logging

from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVectorField
from django.db import models
from django.db.models import F, Index

from puka.core.models import TimeStampedModel

logger = logging.getLogger(__name__)


class ActiveBookmarkManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(active=True)

    def with_tags(self, tags: list[str]) -> models.QuerySet:
        return self.get_queryset().filter(tags__overlap=tags)

    def with_text(self, text: str) -> models.QuerySet:
        query = SearchQuery(text, search_type="websearch", config="english")
        return (
            self.get_queryset()
            .annotate(rank=SearchRank(F("title_description_search"), query))
            .filter(rank__gte=0.1)
            .order_by("-rank")
        )


class Bookmark(TimeStampedModel):
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    url = models.URLField(max_length=500, unique=True)
    active = models.BooleanField(default=True)
    tags = ArrayField(models.CharField(max_length=50), blank=True)
    title_description_search = SearchVectorField(null=True, editable=False)

    objects = models.Manager()
    active_objects = ActiveBookmarkManager()

    class Meta:
        indexes = [
            Index(fields=["-created"]),
            GinIndex(fields=["tags"]),
            GinIndex(fields=["title_description_search"]),
        ]
        ordering = ["-created"]

    def __str__(self) -> str:
        return self.title
