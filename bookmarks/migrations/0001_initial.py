# Generated by Django 3.1.6 on 2021-02-04 16:15

import django.contrib.postgres.fields
import django.contrib.postgres.indexes
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bookmark',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120)),
                ('description', models.TextField(blank=True)),
                ('url', models.URLField()),
                ('tags', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=50), blank=True, size=None)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.AddIndex(
            model_name='bookmark',
            index=django.contrib.postgres.indexes.GinIndex(fields=['tags'], name='bookmarks_b_tags_65d16c_gin'),
        ),
    ]
