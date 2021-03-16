import csv
from datetime import datetime, timezone
import requests

from bookmarks.models import Bookmark
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Load bookmarks exported from Pocket"
    output_transaction = True

    def add_arguments(self, parser):
        parser.add_argument("csv_url")

    def handle(self, *args, **options):
        csv_url = options["csv_url"]
        r = requests.get(csv_url)

        pocket_reader = csv.DictReader(
            r.iter_lines(decode_unicode=True), dialect="excel"
        )

        for row in pocket_reader:
            raw_title = row["resolved_title"]
            title = (raw_title[:118] + "…") if len(raw_title) > 75 else raw_title
            description = row["excerpt"]
            url = row["resolved_url"]
            tags = row["tags"].split(",")
            tags += ["pocket"]
            created_at = datetime.fromtimestamp(int(row["time_added"]), timezone.utc)

            if title == "" or url == "" or len(url) > 200:
                continue

            bookmark = Bookmark.objects.create(
                title=title,
                description=description,
                url=url,
                tags=tags,
                created_at=created_at,
            )
            bookmark.save()
