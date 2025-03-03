# Generated by Django 5.1.6 on 2025-03-03 12:46

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
                ('name', models.CharField(max_length=100, unique=True)),
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
                ('current_stock', models.PositiveIntegerField()),
                ('reorder_level', models.PositiveIntegerField()),
                ('notes', models.TextField(blank=True)),
                ('name_notes_search', django.contrib.postgres.search.SearchVectorField(editable=False, null=True)),
                ('bookmarks', models.ManyToManyField(related_name='+', to='bookmarks.bookmark')),
                ('tags', taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='stuff.location')),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='InventoryTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True)),
                ('type', models.CharField(choices=[('IN', 'In'), ('OUT', 'Out')], max_length=4)),
                ('quantity', models.PositiveIntegerField()),
                ('notes', models.TextField(blank=True)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='stuff.item')),
            ],
            options={
                'verbose_name': 'Inventory Transaction',
                'verbose_name_plural': 'Inventory Transactions',
                'ordering': ('-date',),
            },
        ),
    ]
