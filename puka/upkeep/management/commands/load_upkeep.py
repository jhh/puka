import json
from pathlib import Path

from django.core.exceptions import ObjectDoesNotExist
from django.core.management import BaseCommand
from django.db import transaction

from puka.bookmarks.models import Bookmark
from puka.stuff.models import Inventory, Item, Location
from puka.upkeep.models import Area, Schedule, Task, TaskItem


def create_bookmark(title, description, url):
    bookmark, _ = Bookmark.objects.get_or_create(
        title=title,
        url=url,
        description=description,
        active=False,
    )
    bookmark.tags.add("upkeep", "stuff")
    return bookmark


def create_item(consumable_json, location):
    name = consumable_json["name"]
    notes = consumable_json["notes"]
    url = consumable_json["url"]
    quantity = consumable_json["quantity"]

    item, _ = Item.objects.get_or_create(name=name, reorder_level=0, notes=notes)
    item.tags.add("upkeep")

    if url:
        item.bookmarks.add(create_bookmark(name, notes, url))

    Inventory.objects.get_or_create(item=item, location=location, quantity=quantity)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("file_name", type=str, help="The name of the CSV file to load")

    @transaction.atomic
    def handle(self, **options):
        try:
            location = Location.objects.get(name="Unknown")
        except ObjectDoesNotExist:
            location = Location.add_root(name="Unknown", code="UNK")

        with Path(options["file_name"]).open() as f:
            data = json.load(f)

        for obj in data:
            match obj["model"]:
                case "core.area":
                    Area.objects.update_or_create(**obj["fields"])
                case "core.task":
                    area = Area.objects.get(name=obj["fields"]["area"])
                    area.tasks.get_or_create(**obj["fields"])
                case "core.consumable":
                    create_item(obj["fields"], location)
                case "core.taskconsumable":
                    task = Task.objects.get(
                        name=obj["fields"]["task"][0],
                        area__name=obj["fields"]["task"][1],
                    )
                    item = Item.objects.get(name=obj["fields"]["consumable"])
                    TaskItem.objects.get_or_create(
                        task=task,
                        item=item,
                        quantity=obj["fields"]["quantity"],
                    )
                case "core.schedule":
                    task = Task.objects.get(
                        name=obj["fields"]["task"][0],
                        area__name=obj["fields"]["task"][1],
                    )
                    Schedule.objects.get_or_create(
                        task=task,
                        due_date=obj["fields"]["due_date"],
                        completion_date=obj["fields"]["completion_date"],
                        notes=obj["fields"]["notes"],
                    )
