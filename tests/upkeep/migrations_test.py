from __future__ import annotations

import pytest
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

from puka.stuff.models import Location
from puka.upkeep.models import Area

pytestmark = pytest.mark.django_db(transaction=True)

MIGRATE_FROM = [("upkeep", "0002_area_bookmarks")]
MIGRATE_TO = [("upkeep", "0003_area_location")]
LATEST = [("upkeep", "0004_alter_area_location")]


@pytest.fixture
def executor():
    migration_executor = MigrationExecutor(connection)
    yield migration_executor
    # Restore the latest schema even if a test fails mid-migration.
    migration_executor.loader.build_graph()
    migration_executor.migrate(LATEST)


def test_backfill_creates_none_location(executor):
    executor.migrate(MIGRATE_FROM)
    old_apps = executor.loader.project_state(MIGRATE_FROM).apps
    old_area = old_apps.get_model("upkeep", "Area")
    assert not Location.objects.filter(code="N").exists()
    old_area.objects.create(name="Legacy area")

    executor.loader.build_graph()
    executor.migrate(MIGRATE_TO)

    none = Location.objects.get(code="N")
    assert none.name == "None"
    assert none.is_root()
    assert Area.objects.get().location_id == none.pk


def test_backfill_reuses_existing_none_location(executor):
    none = Location.objects.add_root({"name": "None", "code": "N"})
    executor.migrate(MIGRATE_FROM)
    old_apps = executor.loader.project_state(MIGRATE_FROM).apps
    old_area = old_apps.get_model("upkeep", "Area")
    old_area.objects.create(name="Legacy area")

    executor.loader.build_graph()
    executor.migrate(MIGRATE_TO)

    assert Location.objects.filter(code="N").count() == 1
    assert Area.objects.get().location_id == none.pk
