from django.db import models
from django.utils import timezone

# Create your models here.


class Bookmark(models.Model):
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    url = models.URLField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return self.title
