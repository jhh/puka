import json
import pathlib

from bookmarks.models import Bookmark
from django.core.management.base import BaseCommand, CommandParser
from django.utils.dateparse import parse_datetime


class Command(BaseCommand):
    help = "Load bookmarks from JSON in legacy Puka format."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "json_file", type=pathlib.Path, help="Path to JSON file to import."
        )

    def handle(self, *args, **kwargs) -> None:
        json_file: pathlib.Path = kwargs["json_file"]
        with json_file.open() as f:
            json_array = json.load(f)

        for bm in json_array:
            title = bm["title"][:120]
            description = bm.get("description", "")
            url = bm["url"][:200]
            tags = bm["tags"]
            created_at = parse_datetime(bm["timestamp"]["$date"])
            print(f"{title} - {created_at}")
            bookmark = Bookmark(
                title=title,
                description=description,
                url=url,
                tags=tags,
                created_at=created_at,
            )
            bookmark.save()
