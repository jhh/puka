# Area to location assignment

Status: rewritten on 2026-10-22. The "None" fallback location was removed;
areas now require an explicit location.

## Goal

Give every `upkeep.Area` a required foreign key to `stuff.Location`. The
user picks the location when creating an area; there is no default
location and no "None" row.

## Current state

- `Area` (`puka/upkeep/models.py`) has `name`, `notes`, `location` and
  `bookmarks`.
- `Location` (`puka/stuff/models.py`) is a treebeard `MP_Node` with a
  unique `code`. `__str__` returns the code.
- `Area.location` is a required (`null=False`) foreign key with
  `related_name="areas"` and `on_delete=PROTECT`. Deleting a location
  that has areas (directly or in its subtree) is blocked.

## History: the "None" location

`upkeep` migration `0003_area_location` originally gave every area a
default "None" location (code `N`):

- `Area.location` used `on_delete=SET_DEFAULT` with a callable default,
  `default_area_location()`, returning the pk of the `N` row.
- The migration backfilled existing areas onto `N` and created the root
  when it had to.
- `LocationDeleteView` blocked deleting `N` or any ancestor of `N`.

That design was removed on 2026-10-22:

1. `Area.location` is now `on_delete=PROTECT` with no default, and
   `default_area_location()` / `NONE_LOCATION_CODE` are deleted.
2. `0003_area_location` no longer references the callable in its
   state-only `AlterField` (it was removed from `puka.upkeep.models`,
   and migrations import it by path). The `RunPython` backfill is
   unchanged: it still creates `N` when it runs on a database that has
   unassigned areas, so a not-yet-migrated database keeps working.
   Migration `0004_alter_area_location` changes `on_delete` to
   `PROTECT`. `on_delete` is a Python-level attribute, so the operation
   has no database effect; it does not evaluate the old callable
   default and needs no `N` row on a fresh database.
3. No migration deletes the `N` row. Areas on it must be reassigned
   first, and a migration cannot guess a replacement location. Once the
   row is empty it is a normal location and can be deleted from its
   location page.

## Decisions

1. **Field:** `Area.location` is a required (`null=False`) foreign key
   to `stuff.Location` with `related_name="areas"` and
   `on_delete=PROTECT`.
   - `PROTECT` blocks deleting a location that still has areas instead
     of reassigning or cascading them.
   - `Area.location_id: int` is annotated for the type checker, like
     `Inventory.item_id`.
2. **No default.** `AreaForm` includes `location`
   (`LocationChoiceField`, ordered by `path`) and requires a choice.
3. **Delete guard.** `LocationDeleteView` returns HTTP 400 when the
   location or any descendant has areas, and the location page shows a
   disabled delete button with an explanation instead of the form.
4. **Seed data.** `seed_locations` no longer creates a "None" root.

## Implementation

01. `puka/upkeep/models.py`: `Area.location` (`PROTECT`, no default);
    `default_area_location()` removed.
02. `puka/stuff/models.py`: `NONE_LOCATION_CODE` removed.
03. `puka/upkeep/migrations/0003_area_location.py`: the state-only
    `AlterField` no longer references
    `puka.upkeep.models.default_area_location`.
04. `puka/upkeep/migrations/0004_alter_area_location.py`: `AlterField`
    `on_delete=PROTECT`.
05. `puka/stuff/views/location.py`: `subtree_has_areas()` guards
    `LocationDeleteView` and drives `location_has_areas` for the
    template; `_contains_none_location()` removed.
06. `puka/templates/stuff/location_list.html`: disabled delete button
    when areas are assigned.
07. `puka/upkeep/forms.py`: the `show_hidden_initial` workaround for
    the callable default was removed.
08. `puka/stuff/management/commands/seed_locations.py`: the "None" root
    was removed.
09. `tests/factories.py`: `NoneLocationFactory` became
    `AreaLocationFactory` (root code `TEST`); `AreaFactory.location`
    points at it. `conftest.py` has an `area_location` fixture; the
    shared `area` fixture passes a location.
10. `nix/checks/tests.py`: the area form check submits an explicit
    location from the options instead of a preselected default.

## Tests

- Creating an area without a location is rejected; the form has no
  preselected option (`tests/upkeep/views/area_views_test.py`).
- `Area.objects.create()` without a location raises `IntegrityError`
  (`tests/upkeep/models_test.py`).
- Deleting a location with areas is a 400, directly or through a
  descendant, and the delete button is disabled with an explanation
  (`tests/stuff/location_views_test.py`).
- The `0003` backfill still creates or reuses `N`
  (`tests/upkeep/migrations_test.py`).

## Verification

- `just test`: 631 passed.
- `uv run ty check --error-on-warning`, `uv run ruff format .`,
  `uv run ruff check .`, `just djangofmt`, and `just djade`: clean.
- `nix flake check -L --keep-going`: passed, including the NixOS
  integration test.
- Local database: `0004` applied; `None` shows the disabled delete
  button while it still has areas, and a location without areas shows
  the delete form.

## Data and deploy

1. Reassign every area on `N` to a real location (edit each area in the
   UI, or run SQL).
2. Deploy; migration `0004` is a state-only change.
3. Delete `N` on its location page. The button is enabled once no areas
   reference it.
4. If `0003` was not applied yet, the deploy runs it first: it
   backfills areas onto a newly created `N`. Reassign them and delete
   `N` as above.

## Rollback

The old code expects a "None" location (`default_area_location()`), so
recreate it before reverting:

```python
from puka.stuff.models import Location

Location.objects.add_root({"name": "None", "code": "N"})
```

Then deploy the previous build. Reverting `0004` only changes migration
state; reverting `0003` drops the column.
