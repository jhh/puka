# Generated by Django 5.1.7 on 2025-03-11 14:30

import django.contrib.postgres.indexes
import django.contrib.postgres.search
import django.db.models.deletion
import taggit.managers
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('bookmarks', '0003_alter_bookmark_options_and_more_squashed_0009_alter_bookmark_options'),
        ('taggit', '0006_rename_taggeditem_content_type_object_id_taggit_tagg_content_8fc721_idx'),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.CharField(max_length=255, unique=True)),
                ('depth', models.PositiveIntegerField()),
                ('numchild', models.PositiveIntegerField(default=0)),
                ('name', models.CharField(max_length=100)),
                ('code', models.CharField(max_length=25, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('reorder_level', models.PositiveIntegerField()),
                ('notes', models.TextField(blank=True)),
                ('name_notes_search', django.contrib.postgres.search.SearchVectorField(editable=False, null=True)),
                ('bookmarks', models.ManyToManyField(related_name='+', to='bookmarks.bookmark')),
                ('tags', taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags')),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Inventory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inventories', to='stuff.item')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inventories', to='stuff.location')),
            ],
            options={
                'verbose_name': 'Inventory',
                'verbose_name_plural': 'Inventories',
                'ordering': ('item__name',),
            },
        ),
        migrations.AddField(
            model_name='item',
            name='locations',
            field=models.ManyToManyField(related_name='items', through='stuff.Inventory', to='stuff.location'),
        ),
        migrations.AddIndex(
            model_name='item',
            index=django.contrib.postgres.indexes.GinIndex(fields=['name_notes_search'], name='stuff_item_name_no_d1686a_gin'),
        ),
        migrations.AddConstraint(
            model_name='inventory',
            constraint=models.UniqueConstraint(fields=('item', 'location'), name='unique_item_location'),
        ),
    ]
