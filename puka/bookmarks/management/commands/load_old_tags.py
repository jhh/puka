import json

from django.core.management import BaseCommand

from puka.bookmarks.models import Bookmark


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("file_name", type=str, help="The name of the file to process")

    def handle(self, *args, **options):
        with open(options["file_name"]) as f:
            bookmarks = json.load(f)

        for tags in bookmarks:
            bookmark = Bookmark.objects.get(pk=tags["pk"])
            bookmark.tags.set(tags["tags"])
            bookmark.save()
