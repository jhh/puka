from django.core.management import BaseCommand
from django.db import transaction

from puka.stuff.models import Location


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, **_options):
        studio = Location.objects.add_root({"name": "Studio", "code": "S"})

        c1 = Location.objects.add_child(studio, {"name": "C01", "code": "S-C01"})
        for i in range(1, 21):
            Location.objects.add_child(
                c1,
                {"name": f"C01-{i:02}", "code": f"S-C01-{i:02}"},
            )

        d1 = Location.objects.add_child(studio, {"name": "D01", "code": "S-D01"})
        for i in range(1, 9):
            Location.objects.add_child(
                d1,
                {"name": f"D01-{i:02}", "code": f"S-D01-{i:02}"},
            )
