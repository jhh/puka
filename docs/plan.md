# Plan: simplify and optimize template rendering

## Goal and scope

Improve correctness, rendering cost and maintainability without changing
the current look or replacing the existing template architecture.

Execute in this order:

1. Fix fragment targeting and navigation metadata.
2. Optimize database work triggered during rendering.
3. Extract clearly repeated presentation components.
4. Finish targeted URL, search and asset cleanups.

The review was static. Confirm suspected browser issues and measure query
counts before choosing implementations. Do not assume every repeated
related-manager access causes a query: prefetch caches may already cover it.

## Constraints

- Keep Django 6 partials as response fragments and Cotton components as
  presentation only. Pass prepared data into components.
- Preserve existing routes, appearance, CSRF protection and mutations.
- Retain Cotton context isolation, the custom form renderer and explicit
  Tailwind class mappings. Do not generate classes such as `btn-{{ variant }}`.
- Keep Alpine behavior in `puka/static/puka/base.js`; use `x-on:` and
  `x-bind:` on component tags.
- Use htmx 4 APIs, including explicit `:inherited` attributes where needed.
- Consult Context7 for library behavior and the required daisyUI Blueprint
  workflow before non-trivial UI component changes.
- Run every command inside the Nix devshell. Use jj for any VCS work.
- Make small, independently verified changes; do not introduce a universal
  detail-page, table or navigation framework.

## Step 1: establish regression coverage and baselines

1. Extend existing tests rather than duplicating the smoke-test suite:
   - `tests/core/views_smoke_test.py`
   - `tests/core/form_components_test.py`
   - `tests/core/form_rendering_test.py`
   - The existing bookmark, stuff and upkeep view tests.
2. Inventory response shapes for full-page, boosted and ordinary htmx
   requests, including the bookmark list's different targets.
3. Reproduce invalid create/update submissions for stuff and upkeep in the
   browser. Record the response, target and resulting DOM.
4. Record query counts for item lists, task lists, area lists and the item,
   location, task and area detail views with representative related data.
5. Add small and larger fixture sets so tests can expose query growth as
   rows, consumables and bookmarks increase. Create fixtures outside the
   measured request or rendering block.

Acceptance: existing tests pass; reproduced failures have regression tests;
query baselines distinguish request overhead from relationship queries.

## Step 2: fix fragment targeting and navigation metadata

1. Make `puka/core/views.py` and view-specific template selection agree on
   the response contract:
   - Full-page requests return the document and application shell.
   - Default boosted navigation receives a complete page.
   - Targeted requests return markup suitable for the requested target.
   - Bookmark searches and infinite scrolling retain their row responses.
2. Add explicit targets to the htmx forms in
   `puka/templates/stuff/form.html` and
   `puka/templates/upkeep/form.html`, matching their returned fragments.
3. Verify invalid submissions replace the intended content without nested
   forms or cards. Verify successful submissions and delete responses
   navigate correctly without changing data or redirect semantics.
4. Provide breadcrumbs and document titles for content-navigation
   fragments. Keep row-only searches and append responses from overwriting
   unrelated page metadata. Check sidebar active state after navigation.
5. Separate reusable bookmark rows from page-specific breadcrumbs:
   `bookmarks/filter.html` must not receive the bookmark-list breadcrumb
   trail merely because it reuses the list-items partial.
6. Extend boosted-response tests beyond bookmarks and item detail before
   simplifying any repeated htmx navigation attributes.

Acceptance: full loads, boosted links, targeted navigation, invalid forms,
cancel/delete actions and browser back/forward preserve the correct shell,
content, title and breadcrumbs.

## Step 3: optimize queries used by templates

1. Prepare task stock status outside template rendering. Start with
   `Task.are_consumables_stocked()` and its consumers in task lists, area
   detail and notification emails.
   - Batch consumables and their items, or use suitable annotations.
   - Prepare inventory totals without an aggregate per consumable.
   - Preserve the existing semantics for tasks without consumables,
     insufficient stock, multiple locations and shared items.
2. Prepare task-detail consumables with their items and stock quantities in
   `puka/upkeep/views/task.py`. Display prepared quantities instead of
   calling `Item.quantity()` for each row.
3. Match item list/detail prefetches to the actual template access paths in
   `puka/stuff/views/item.py`:
   - Prefetch inventories with their locations selected.
   - Prefetch item tags and attached bookmarks' tags where displayed.
   - Remove unused location prefetches only after checking all consumers.
4. Load location inventories with their items in
   `puka/stuff/views/location.py`.
5. Load area bookmarks and their tags in `puka/upkeep/views/area.py`,
   alongside the existing task preparation.
6. Fix `get_areas_tasks_schedules()` in `puka/upkeep/services.py`:
   - Stop filtering related managers after prefetching all schedules.
   - Prefer database annotations for task count and earliest due task/date
     so pagination happens before materializing every area's relationships.
   - Preserve search ordering and behavior for areas without due schedules.
7. Reuse one prepared bookmarks collection in
   `puka/templates/bookmarks/_detail_page.html` and its callers. Eliminate
   repeated existence checks where a loop's empty branch suffices.
8. Compare against Step 1 baselines and add query-count regression tests
   proving relationship-query counts do not grow per rendered row.

Acceptance: quantities, due dates and stock labels are unchanged; query
growth is bounded for paginated views; unused prefetch work is removed.
Document measured improvements rather than estimated speedups.

## Step 4: extract repeated presentation components

1. Add a small detail-row component under `puka/templates/cotton/ui/` with
   a label and a value slot. Replace the copied field partials in item,
   location, task and area detail templates.
2. Extract inventory quantity controls used by item and location detail.
   Pass inventory ID and prepared quantity explicitly; retain target IDs,
   adjustment values, accessible labels and page-specific edit actions.
3. Extract the Manage dropdown shell used by item, task and area detail.
   Keep each page's routes, confirmation messages and actions in its slot.
4. Share the identical card/form fragment in the stuff and upkeep form
   pages. Preserve app-specific titles, response partial names and the
   explicit targeting fixed in Step 2.
5. Add component rendering tests using Cotton compilation, plus page tests
   for pass-through attributes, class merging and unchanged mutation URLs.
6. Rebuild assets and inspect each changed page at mobile and desktop
   sizes, including keyboard navigation and inventory adjustments.

Acceptance: copied presentation markup is reduced without new database
access, route configuration machinery or behavior changes.

## Step 5: finish targeted cleanups

1. Encode tag parameters in bookmark and inventory URLs. Use `urlencode`
   or Django's `querystring` tag; deliberately choose which filters to keep
   and reset pagination when switching filters.
2. Add tests for tags containing spaces, `&`, `+`, `#` and Unicode. Check
   both ordinary links and htmx requests.
3. Give the item list a results-only search fragment so debounced searches
   do not rebuild the toolbar and Alpine input state.
   - Keep pagination and new-item navigation working.
   - Verify focus, caret, clear-search behavior and rapid typing.
   - Leave other search pages unchanged unless the same need is confirmed.
4. Inspect computed font styles before removing the Inter stylesheet from
   `puka/templates/root.html`. Its configuration in `base.css` is currently
   commented out; remove the request only if the stylesheet is unused.
5. If asset tags change, check the Nix integration test's assumptions about
   their presence and order without weakening functional coverage.

Acceptance: special-character filters round-trip correctly, search retains
input state, and any asset removal leaves typography unchanged.

## Verification gate after each implementation step

1. Run focused tests first, then `just test` with Postgres running
   (`just db-start`). Do not use bare pytest: tests live in `tests/`.
2. Run `uv run ty check --error-on-warning`.
3. For template changes, run `just djangofmt` and `just djade`. Rebuild
   assets with `just update-css` and, when needed, `just update-js`.
4. Run `jj st` immediately before `pre-commit run --all-files`. Inspect
   formatter changes and rerun affected checks.
5. Run `jj st` immediately before `nix flake check -L --keep-going`.
   On macOS, run pytest locally because the Nix pytest check is Linux-only.
6. Inspect the final diff and perform the step's browser acceptance checks.
   Report unavailable checks explicitly; do not mark them as passed.

## Completion checklist

- Fragment targets and page metadata remain correct across navigation.
- Query-count tests cover the optimized list and detail rendering paths.
- Repeated detail rows, inventory controls and dropdown shells are shared.
- Form wrappers retain titles, errors, CSRF protection and correct targets.
- Tag URLs are encoded and item searches preserve input state.
- Browser checks, formatting, types, tests and Nix checks are complete.
- No unrelated redesign, dependency migration or generated-asset edits.
