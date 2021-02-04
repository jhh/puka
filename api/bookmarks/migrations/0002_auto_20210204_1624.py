# Generated by Django 3.1.6 on 2021-02-04 16:24

from django.db import migrations
from django.core.management import call_command


def forwards_func(apps, schema_editor):
    call_command("loaddata", "legacy")


class Migration(migrations.Migration):

    dependencies = [
        ("bookmarks", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(forwards_func),
    ]