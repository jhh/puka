# Generated by Django 3.1.7 on 2021-03-17 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookmarks', '0003_auto_20210205_1342'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookmark',
            name='url',
            field=models.URLField(max_length=500),
        ),
    ]