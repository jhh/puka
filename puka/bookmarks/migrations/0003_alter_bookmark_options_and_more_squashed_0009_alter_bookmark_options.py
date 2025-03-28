# Generated by Django 5.1.4 on 2024-12-25 16:05

import django.contrib.postgres.search
import taggit.managers
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bookmarks", "0002_title_description_search_trigger"),
        ("taggit", "0006_rename_taggeditem_content_type_object_id_taggit_tagg_content_8fc721_idx"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="bookmark",
            options={"ordering": ["-created"]},
        ),
        migrations.AlterField(
            model_name="bookmark",
            name="title_description_search",
            field=django.contrib.postgres.search.SearchVectorField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name="bookmark",
            name="active",
            field=models.BooleanField(default=True),
        ),
        migrations.AddIndex(
            model_name="bookmark",
            index=models.Index(fields=["-created"], name="bookmarks_b_created_9a00a6_idx"),
        ),
        migrations.AlterField(
            model_name="bookmark",
            name="url",
            field=models.URLField(max_length=500, unique=True),
        ),
        migrations.RemoveIndex(
            model_name="bookmark",
            name="bookmarks_b_tags_65d16c_gin",
        ),
        migrations.RemoveField(
            model_name="bookmark",
            name="tags",
        ),
        migrations.AddField(
            model_name="bookmark",
            name="tags",
            field=taggit.managers.TaggableManager(
                help_text="A comma-separated list of tags.",
                through="taggit.TaggedItem",
                to="taggit.Tag",
                verbose_name="Tags",
            ),
        ),
        migrations.AlterModelOptions(
            name="bookmark",
            options={"ordering": ("-created",)},
        ),
    ]
