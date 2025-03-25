from django.core.management import BaseCommand
from django.db import transaction

from puka.stuff.models import Location


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, **_options):
        studio = Location.add_root(name="Studio", code="S")

        c1 = Location.objects.get(pk=studio.pk).add_child(name="C01", code="S-C01")
        for i in range(1, 21):
            Location.objects.get(pk=c1.pk).add_child(name=f"C01-{i:02}", code=f"S-C01-{i:02}")

        d1 = Location.objects.get(pk=studio.pk).add_child(name="D01", code="S-D01")
        for i in range(1, 9):
            Location.objects.get(pk=d1.pk).add_child(name=f"D01-{i:02}", code=f"S-D01-{i:02}")
