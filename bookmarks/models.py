from django.contrib.postgres import indexes
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django.utils import timezone

# Create your models here.


class Bookmark(models.Model):
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    url = models.URLField(max_length=500)
    tags = ArrayField(models.CharField(max_length=50), blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    title_description_search = SearchVectorField(null=True)

    class Meta:
        indexes = [
            GinIndex(fields=["tags"]),
            GinIndex(fields=["title_description_search"]),
        ]

    def __str__(self) -> str:
        return self.title
