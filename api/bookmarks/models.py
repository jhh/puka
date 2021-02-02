from django.db import models

# Create your models here.


class Bookmark(models.Model):
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)