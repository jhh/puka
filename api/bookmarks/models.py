from django.contrib.postgres import indexes
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.db import models
from django.utils import timezone

# Create your models here.


class Bookmark(models.Model):
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    url = models.URLField()
    tags = ArrayField(models.CharField(max_length=50), blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [GinIndex(fields=["tags"])]

    def __str__(self) -> str:
        return self.title
