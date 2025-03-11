import csv
from pathlib import Path

from django.core.management import BaseCommand
from django.db import transaction

from puka.bookmarks.models import Bookmark
from puka.stuff.models import Inventory, Item, Location


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("file_name", type=str, help="The name of the CSV file to load")

    @transaction.atomic
    def handle(self, *_args, **options):
        Bookmark.objects.filter(tags__name__in=["stuff"]).delete()
        Item.objects.all().delete()

        with Path(options["file_name"]).open() as f:
            csv_reader = csv.reader(f)
            for row in csv_reader:
                bookmark = None
                if row[5]:
                    bookmark = Bookmark.objects.create(
                        title=row[0],
                        url=row[5],
                        description=row[3],
                        active=False,
                    )
                    bookmark.tags.add("stuff", row[4].lower())

                loc = Location.objects.get(name=row[2])

                item = Item.objects.create(
                    name=row[0],
                    reorder_level=0,
                    notes=row[3],
                )

                tags = row[4].strip().lower()
                if tags:
                    item.tags.add(tags)

                Inventory.objects.create(
                    item=item,
                    location=loc,
                    quantity=row[1],
                )

                if bookmark:
                    item.bookmarks.add(bookmark)
