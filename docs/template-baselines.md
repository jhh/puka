# Template regression and query baselines

Recorded for Step 1 of `PLAN.md` on 2026-10-04. Production views, models
and templates are unchanged. The starting suite had 516 passing tests.

## Response inventory

`tests/core/views_smoke_test.py` covers every named application URL.
Action-only routes remain covered by the existing mutation tests.

| Request / view | Current response |
| --- | --- |
| Full GET, every page route | Document with head/title and app shell |
| Login GET | Document without the authenticated app shell |
| Ordinary htmx, fragment-capable routes | Fragment without head/html |
| Ordinary htmx, page-only routes | Complete document |
| Boosted bookmarks list/filter and item detail | Complete document |
| Boosted other fragment-capable routes | Fragment: incorrect for body swap |
| Detail navigation into `#content` | No breadcrumb or title update |
| Invalid stuff/upkeep create or update | HTTP 200, card containing a form |

Bookmark-specific response shapes are covered in
`tests/bookmarks/views_test.py`:

- List search, `HX-Target: ul#id_bookmarks`: rows and OOB breadcrumbs;
  no toolbar or list wrapper.
- Infinite scroll, `HX-Target: li`: rows appended with `afterend`;
  no toolbar or list wrapper. The last page has no further trigger.
- List navigation, `HX-Target: div#content`: toolbar, list wrapper and
  OOB breadcrumbs.
- Filter navigation without a page parameter: filter form and list wrapper.
- Filter paging: rows only.
- Filter fragments reuse the list's OOB breadcrumbs, losing the Filter crumb.

At Step 1, known defects had strict expected-failure tests, limited to
assertion failures. Step 2 removes these markers after fixing the response
contract, form targets and navigation metadata; the tests now pass normally.

## Browser reproduction: invalid forms

Checked with headless Google Chrome and Playwright using the rebuilt
`puka/static/puka/main.js`. Browser requests were routed to Django's test
client against an isolated test database; no development data was edited.
The optional browser tooling was installed outside project dependencies.

Routes checked:

- `stuff:item-new` and `stuff:item-edit`
- `upkeep:area-new` and `upkeep:area-edit`

Reproduction steps for each route:

1. Open the full page and locate its `form[hx-post]`.
2. Set that form's `noValidate` property to `true` in developer tools so
   browser required-field validation does not prevent the server request.
3. Clear Name, enter `keep browser notes` in Notes, and submit.
4. Inspect the request, response and resulting DOM.

All four routes produced the same structural failure:

| Observation | Result |
| --- | --- |
| Explicit form `hx-target` before submission | Missing |
| Request headers | `HX-Request: true`, `HX-Target: form` |
| Response | HTTP 200, one card/form with field errors |
| `form[hx-post]` elements after the swap | Two, up from one |
| Nested `form form` elements | One |
| Nested `.card .card` elements | One |
| Submitted notes | Preserved |
| JavaScript errors with freshly built assets | None |

The missing target causes the default innerHTML swap to insert the
returned card/form inside the original form. Server-side regression tests
cover invalid submissions for all 14 stuff/upkeep create/update forms,
including unchanged database rows, errors, CSRF and submitted notes.
Target assertions are strict expected failures pending Step 2.

The browser check covered these four representative routes, not every
form. No persistent browser-test dependency was added.

## Query dataset and measurement

`tests/core/rendering_queries_test.py` creates datasets of size 1 and 3:

- N items, N locations, and inventory at every item/location pair.
- Each item has two tags; inventory quantity is 10 at each location.
- N bookmarks with two tags each, attached to every item and area.
- N areas and N tasks; all tasks belong to the first area. Other areas
  are empty, exercising both populated and empty area-list rows.
- Each task consumes all N items, with required quantity 1 per item.
- Each task has one incomplete and one completed schedule.

All rows fit on the first page. These fixtures demonstrate query growth
within a page, not large-dataset pagination or elapsed-time performance.

Setup, authentication and fixture creation occur outside captured blocks:

1. Direct RequestFactory view dispatch measures context preparation.
2. Deferred `TemplateResponse.render()` measures template-time queries,
   including lazy evaluation of primary and related querysets.
3. A test-client GET measures the complete authenticated request.
4. Two session/user reads account for the request overhead; tests inspect
   their SQL separately from the view and rendering queries.

Counts were measured on macOS with Python 3.13.12, Django 6.1.1 and local
PostgreSQL. Full-page and ordinary htmx requests are tested separately.

| View | Size | Preparation | Rendering | Auth | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| Item list | 1 | 1 | 5 | 2 | 8 |
| Item list | 3 | 1 | 15 | 2 | 18 |
| Task list | 1 | 1 | 4 | 2 | 7 |
| Task list | 3 | 1 | 22 | 2 | 25 |
| Area list | 1 | 4 | 0 | 2 | 6 |
| Area list | 3 | 6 | 0 | 2 | 8 |
| Item detail | 1 | 4 | 3 | 2 | 9 |
| Item detail | 3 | 4 | 7 | 2 | 13 |
| Location detail, full | 1 | 1 | 3 | 2 | 6 |
| Location detail, full | 3 | 1 | 5 | 2 | 8 |
| Location detail, htmx | 1 | 1 | 2 | 2 | 5 |
| Location detail, htmx | 3 | 1 | 4 | 2 | 7 |
| Task detail | 1 | 3 | 2 | 2 | 7 |
| Task detail | 3 | 3 | 6 | 2 | 11 |
| Area detail | 1 | 2 | 7 | 2 | 11 |
| Area detail | 3 | 2 | 27 | 2 | 31 |

Other than location detail, full and htmx counts match. Its full-page
breadcrumbs evaluate the ancestor queryset, adding one query.

Budgets are upper bounds, not requirements to preserve inefficiency.
Step 3 should reduce these bounds and add constant-query growth guards.
Tests also expose the measured counts through pytest's `record_property`.

## Repeat the checks

Run inside the devshell, with Postgres running:

```sh
uv run pytest tests/core/views_smoke_test.py tests/bookmarks/views_test.py
uv run pytest tests/core/form_rendering_test.py
uv run pytest tests/core/form_components_test.py
uv run pytest tests/core/rendering_queries_test.py
```

See `PLAN.md` for the full verification gate. Large-dataset pagination
still needs its later-step checks.

## Step 2: fragment contract and browser verification

The common helper and bookmark-specific views now use the same contract:

- Full loads, boosted navigation, body-targeted requests and history
  restoration receive complete documents with the application shell.
- Content-navigation fragments include a title and out-of-band breadcrumb
  and sidebar updates. They do not insert another shell into `#content`.
- Full pages and history responses contain no out-of-band updates.
- Bookmark list search retains its own breadcrumb update, but no title or
  sidebar update. Infinite-scroll responses contain rows only.
- Filter tag clicks and paging use a shared rows-only partial. They leave
  the filter form, Filter breadcrumb, document title and sidebar intact.
- Stuff/upkeep forms explicitly target `#content`. `hx-replace-url` uses
  the final redirect URL, without adding history entries for invalid forms.
  Existing HTTP redirects and `HX-Location` mutation responses are retained.

Regression coverage now includes all fragment-capable routes for boosted,
body-targeted and history requests, and compares content-fragment titles,
breadcrumbs and active sidebar links against their full-page equivalents.

Browser verification used headless Chrome, freshly built CSS/JS, an
ephemeral local WSGI server and an isolated test database. Real HTTP
requests exercised redirects and CSRF middleware; no development data was
edited. Desktop checks used 1280 x 800; mobile checks used 375 x 812.

Verified flows:

- Invalid item/area create and update: one form, no nested forms/cards,
  submitted notes retained, unchanged history length.
- Boosted inventory-to-item navigation and targeted item-to-edit navigation:
  correct title, breadcrumbs and Inventory sidebar state, with one shell.
- Cancel, back twice and forward: correct URL, content and navigation state;
  history-restoration responses were full documents.
- Successful item update and area creation: HTTP redirects followed to the
  correct list, with matching URL, title and sidebar state.
- Area deletion: confirmation and `HX-Location` navigation to the area list.
- Item bookmark tag to Filter, then filter tag click: Filter metadata stayed
  intact and the tag response replaced only rows.
- Tags to bookmark list, append the 26th bookmark, then search: no duplicated
  wrapper/shell, and append requests did not alter navigation metadata.
- Mobile area list and drawer navigation to Inventory: no horizontal page
  overflow, and the drawer closed after navigation.

All checked states had exactly one content container, breadcrumb container
and sidebar. No JavaScript errors were observed.

The Step 1 query table remains the historical baseline. Step 2 adds one
ancestor query to location-detail fragments because they now render the
same breadcrumbs as full pages: totals are 6 and 8 for sizes 1 and 3.
Other query budgets are unchanged. Query optimization remains Step 3.

## Step 3: prepared data and constant query budgets

Stock status is now computed with a correlated `Exists` query against
consumables whose required quantity exceeds their inventory total. Missing
inventory is treated as zero. Each task is checked independently, including
tasks sharing the same item; a task without consumables is stocked.

`get_tasks_with_earliest_due_date()` prepares this status for task lists,
area detail and notification emails. The existing stock-status method uses
the annotation when present and otherwise fetches the status in one query.
Notification selection and rendering now use one query for 1, 3 or 15 tasks
in the regression fixtures; mail delivery is mocked in those tests.

Task-detail consumables load their items and annotated `on_hand` totals in
one query. Item and location views prefetch inventories with their related
locations/items selected. Item and area detail also prefetch bookmark tags,
and their templates reuse one prepared bookmarks collection. No styling,
mutation routes or empty-state behavior is changed.

Area summaries are now a lazy annotated values queryset, not a Python list
assembled before pagination. Task counts and earliest incomplete schedules
are computed in SQL. Empty/completed-only areas have no due task or date.
Search retains relevance ordering; unfiltered results use primary-key order
for stable pagination. Equal due dates use task ID and then schedule ID as
deterministic tie-breakers.

Measured authenticated request totals:

| View | Before, size 1 | Before, size 3 | After, sizes 1/3/15 |
| --- | ---: | ---: | ---: |
| Item list | 8 | 18 | 6 |
| Task list | 7 | 25 | 4 |
| Area list | 6 | 8 | 4 |
| Item detail | 9 | 13 | 7 |
| Location detail | 6 | 8 | 5 |
| Task detail | 7 | 11 | 5 |
| Area detail | 11 | 31 | 6 |

The Before columns use full-page counts from Step 1 (also the Step 2
budgets). After counts match for full-page and htmx responses. All totals
include two authentication/session queries.

Current preparation/rendering budgets:

| View | Preparation | Rendering |
| --- | ---: | ---: |
| Item list | 1 | 3 |
| Task list | 1 | 1 |
| Area list | 1 | 1 |
| Item detail | 5 | 0 |
| Location detail | 2 | 1 |
| Task detail | 3 | 0 |
| Area detail | 4 | 0 |

Lists still evaluate their primary querysets and bulk prefetches lazily
during rendering. Location breadcrumbs still load ancestors once. Neither
path issues a relationship query per rendered row.

The query guard fixtures now include size 15, crossing task/area pagination
boundaries. Every size uses the same scalar query ceiling. A separate area
summary test checks lazy construction, a `LIMIT 10` first-page query, and
correct task counts/dates without loading all tasks and schedules in Python.
These are query-count measurements, not elapsed-time performance claims.

Browser checks at 1280 x 800 and 375 x 812 confirmed a two-location total of
5 against a requirement of 6, unchanged bookmark rendering, and no overflow
in the changed regions. After adding one unit, fresh task/area requests
showed total 6 and updated stock labels. Location inventory controls and
bookmark removal/empty states still worked, with no JavaScript errors.

## Step 4: shared presentation

Three small Cotton components replace repeated detail-page markup:

- `ui/detail_row.html`: label and value slot, used for scalar fields on item,
  location, task and area detail. Rich slot content and zero values work.
- `ui/inventory_quantity.html`: explicit inventory ID/prepared quantity,
  unchanged adjustment URLs, target IDs, values and accessible button names.
  The item page keeps its edit action in the slot; the location page omits it.
- `layout/manage_dropdown.html`: a Manage trigger and menu shell. Each page
  supplies its own links, mutation buttons and confirmation messages.

The user chose to migrate Manage menus to the native popover API. Menu IDs
and CSS anchor names are unique per page. Keyboard Enter opens the menu,
Tab reaches its first action, Escape closes it and restores trigger focus,
and outside clicks dismiss it. The account menu is outside this refactor.

`core/form.html` now contains the shared card/form wrapper. Stuff/upkeep
pages retain their titles, metadata and `form-partial` definitions; explicit
`#content` targets and URL replacement behavior are unchanged.

Component tests cover Cotton compilation, context isolation, rich slots,
class merging, attribute pass-through, zero quantities and popover IDs.
Page/form tests protect menu routes, confirmation text, per-page edit
actions, and use of the shared form include. Step 3 query ceilings still hold.

Browser checks at 1280 x 800 and 375 x 812 covered all four detail pages,
item/area invalid forms, inventory adjustment from both item and location
pages, menu keyboard/outside dismissal, and Edit-to-form/Cancel navigation.
Menus stayed inside viewport bounds; changed regions had no horizontal
overflow, duplicated shells or nested forms, and no JavaScript errors.
