# Generated by Django 5.0.2 on 2024-02-26 13:00
from __future__ import annotations

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("bookmarks", "0004_bookmark_active"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="bookmark",
            index=models.Index(fields=["-created"], name="bookmarks_b_created_9a00a6_idx"),
        ),
    ]