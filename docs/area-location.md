# Area to location assignment

Status: implemented and verified locally on 2026-10-13. Production
deploy is the remaining step (see "Deploy" below).

## Goal

Give every `upkeep.Area` a required foreign key to `stuff.Location`.
Existing areas, and new areas created without an explicit choice, use the
"None" location (code `N`).

## Current state

- `Area` (`puka/upkeep/models.py`) has `name`, `notes`, `location` and
  `bookmarks`.
- `Location` (`puka/stuff/models.py`) is a treebeard `MP_Node` with a
  unique `code`. `__str__` returns the code.
- `upkeep` already depends on `stuff` (`TaskItem.item`), so a foreign key
  from `Area` to `Location` adds no new app dependency or import cycle.
- The NixOS service runs `puka-manage migrate --no-input` in
  `ExecStartPre` (`nix/modules/nixos/puka.nix`). A failing migration stops
  the service from starting.
- **Production did not have a "None" location.** Pre-flight on
  2026-10-13 found 81 locations (7 roots: BR, LR, MB, OF, S, TV, UR) and
  14 areas, none called "None". The migration creates the root when it
  has to backfill (see "Decisions").
- The local development database has "None" (`N`, id 94) and had 14
  areas; the migration backfilled them onto `N`.
- The test database starts empty, so the migration is a no-op there and
  tests create `N` themselves through `NoneLocationFactory`.

## Decisions

1. **Field:** `Area.location` is a required (`null=False`) foreign key
   to `stuff.Location` with `related_name="areas"`,
   `on_delete=SET_DEFAULT` and `default=default_area_location`.
   - `SET_DEFAULT` means deleting a location moves its areas to "None"
     instead of blocking the delete or cascading to tasks/schedules.
   - `Area.location_id: int` is annotated for the type checker, like
     `Inventory.item_id`.
2. **Default:** a module-level callable, `default_area_location()`, in
   `puka/upkeep/models.py`, returning the pk of
   `Location.objects.get(code=NONE_LOCATION_CODE)`.
   - `NONE_LOCATION_CODE = "N"` lives in `puka/stuff/models.py`.
   - Primary keys differ between databases, so the pk cannot be
     hard-coded and `db_default` is not usable.
   - `Location.DoesNotExist` propagates. A missing `N` is a data error.
   - Migrations refer to the callable by import path, so it must never be
     renamed or removed.
3. **The migration creates "None" when needed.** Production has no `N`
   row, and the service migrates unattended. When the backfill finds
   unassigned areas and no `N`, the migration creates the root. The
   historical (treebeard) model has no `add_root`, so this one insert uses
   the current model to get a valid `path`/`depth`; hand-building the path
   would risk corrupting the tree. Fresh and test databases have no areas,
   so the migration returns early and does not seed `N`.
4. **The final `AlterField` is state-only.** Django evaluates a callable
   field default at the schema level when changing nullability
   (`effective_default`), and calls it while building the four-step
   default alteration. On a fresh database that raises
   `Location.DoesNotExist`; on production it would have baked `N`'s pk
   into a column default. The migration instead runs
   `ALTER TABLE ... SET NOT NULL` inside `SeparateDatabaseAndState`, with
   the `AlterField` as a state operation.
5. **Deleting "None" is blocked.** `LocationDeleteView` returns HTTP 400
   when the target is `N` or an ancestor whose subtree contains `N` (a
   location can be moved under another node, and `SET_DEFAULT` would then
   resolve to the row being deleted). The location page shows a disabled
   delete button with an explanation instead of the form.

## Implementation

01. `puka/stuff/models.py`: `NONE_LOCATION_CODE`, `Location.areas`
    annotation, `TYPE_CHECKING` import of `Area`.
02. `puka/upkeep/models.py`: `default_area_location()`, `Area.location`,
    `Area.location_id`.
03. `puka/upkeep/migrations/0003_area_location.py`:
    - `AddField` `location`, `null=True`, no default.
    - `RunPython(assign_none_location)`: skip when no area has a null
      location; otherwise reuse code `"N"` or create the root, then
      `update(location=none.pk)`.
    - `SeparateDatabaseAndState`: `RunSQL` `SET NOT NULL` (reverse:
      `DROP NOT NULL`) plus a state-only `AlterField` with
      `default=puka.upkeep.models.default_area_location`.
04. `tests/factories.py`: `NoneLocationFactory` (get-or-create root,
    `name="None"`, `code="N"`) and `AreaFactory.location`. `conftest.py`
    registers a `none_location` fixture; the shared `area` fixture creates
    `N` first, so the model default is exercised by many tests.
05. `puka/upkeep/forms.py`: `AreaForm` includes `location`
    (`field_classes` -> `LocationChoiceField`, ordered by `path`,
    `show_hidden_initial = False` because a callable default otherwise
    renders a hidden `initial-location` input).
06. `puka/stuff/forms.py`: `DestinationField` became
    `LocationChoiceField` ("Name (CODE)"), reused by `InventoryMoveForm`.
07. `puka/upkeep/services.py`: `get_areas_tasks_schedules()` includes
    `location__name`; the area list shows a Location column with the
    location's name.
08. `puka/upkeep/views/area.py`: `AreaDetailView` selects
    `location`; the area detail links to `stuff:location-detail`.
09. `puka/stuff/views/location.py`: `LocationDetailView` prefetches
    `areas` (ordered by name); both the location detail and the
    browseable location page (`stuff:location-list` with a pk) show an
    Areas list, the latter with task counts. `LocationDeleteView` blocks
    deletes that contain `N`; `LocationListView` passes
    `none_location_code` to the template and annotates each row with
    `area_count` (alongside `inventory_count`, both `distinct=True`) for
    the location list's Areas column.
10. `puka/upkeep/admin.py`: `AreaAdmin` with
    `list_display = ("name", "location")` and
    `list_select_related = ("location",)`.
11. `puka/stuff/management/commands/seed_locations.py` seeds the "None"
    root too (last, so seeded primary keys do not shift).
    `nix/checks/tests.py` reads the area form's default location and
    submits it when creating its QA area, since the NixOS VM test runs on
    a database that has no areas.

A database with no areas never gets a "None" row from the migration
(decision 3). Production and the dev database have areas, so it is
created there. On a fresh database, run `seed_locations` or create the
`N` root before creating the first area.

## Tests

- Default assignment and the missing-`N` error
  (`tests/upkeep/models_test.py`).
- Migration backfill: creates `N` when absent; reuses an existing `N`
  (`tests/upkeep/migrations_test.py`, uses `MigrationExecutor`).
- Deleting a location (and its parent) moves areas to `N`; deleting `N`
  or an ancestor of `N` is a 400; the `N` page hides the delete form
  (`tests/stuff/location_views_test.py`).
- Form defaults to `N`, option labels, changing an area's location, and
  the location link on list and detail (`area_views_test.py` in
  `tests/upkeep/views`, `form_rendering_test.py` in `tests/core`).
- The location page lists its areas and hides the section when empty;
  the location list shows area counts without double-counting rows
  joined to other relations (`tests/stuff/page_test.py`).

## Verification

- `just test`: 619 passed.
- `uv run ty check --error-on-warning`: clean.
- `uv run ruff format .` / `uv run ruff check .`: clean.
- `just djangofmt` / `just djade`: clean.
- Local database: `just migrate`, then 14/14 areas on code `N`; reverse
  to `upkeep 0002` drops the column, re-apply backfills again.
- Query budgets: `stuff:location-detail` preparation went from 2 to 3
  (the areas prefetch runs when `DetailView.get_object()` evaluates the
  queryset). `docs/template-baselines.md` records the new budget.
- NixOS integration test: seeds the "None" location and submits the
  form's default location when creating an area.
- `nix build .#checks.aarch64-darwin.pre-commit -L` and
  `nix flake check -L --keep-going`: passed on 2026-10-13, including the
  NixOS integration test.
- Browser QA with Playwright (headless Chromium, 1280x800, signed in as
  the local `qa` user):
  - The area list shows the Location column with location names ("None"
    for the backfilled areas).
  - The new-area form defaults to "None (N)".
  - An area created on `N` moved back to `N` after its throwaway
    location was deleted (`SET_DEFAULT`).
  - The `N` location page shows a disabled delete button.
  - The location page lists its areas with task counts; a location
    without areas shows no section. Clicking a listed area swaps
    `#content` and lands on that area's detail.
  - The location list and sublocation lists show an Areas column whose
    counts match the database.
  - QA rows were deleted afterwards; no QA data remains.

## Deploy

1. Re-check production before deploying; the migration creates `N` when
   the backfill needs it, but confirm the area count first:

   ```sql
   SELECT count(*) FROM upkeep_area;
   ```

2. Take a production database backup.

3. Deploy. `ExecStartPre` runs the migration. Watch the service status
   and the migration log output.

4. Check that every area has a location and that a "None" root exists:

   ```sql
   SELECT count(*) FROM upkeep_area a JOIN stuff_location l
     ON l.id = a.location_id WHERE l.code = 'N';
   ```

5. If the migration failed, the service will not have started. Inspect
   the logs, fix the reported problem, then restart.

## Rollback

- `puka-manage migrate upkeep 0002` drops the column. The "None" row and
  all other data stay, since the backfill only wrote the new column.
- Deploy the previous build after reversing the migration.
