# Plan: move puka's UI to Cotton, htmx, Alpine and daisyUI

Decisions already made:

- Roll out incrementally, in place.
- Replace crispy-forms with Cotton form-field components.
- Keep the current look; clean up with daisyUI.
- Delete `next/` in a new jj change.
- Add view tests before refactoring.

## What exists today

- **Page layout.** Pages extend `root.html` → `base.html` (a daisyUI
  drawer) → an app base → the page. `sidebar.html` is an older layout that
  nothing uses any more.
- **htmx fragments.** Views call
  `get_template(request, "x.html", "#partial")`. There are about 25
  `{% partialdef %}` blocks, and every fragment swaps into `#content`.
- **Forms.**
  - Seven crispy `FormHelper`/`Layout` forms in `stuff/forms.py` and
    `upkeep/forms.py`.
  - Hand-built buttons in `puka/core/forms.py`, styled with plain
    indigo/gray Tailwind rather than daisyUI.
  - One crispy override template, `tailwind/layout/select.html`.
  - `BookmarkForm` and the login form are written by hand.
- **Alpine.** The same search box (Cmd-K to focus, Esc to clear) is copied
  into four templates. `stuff/item_detail.html` has tabs, and there's one
  copy-to-clipboard button.
- **View tests** exist only for bookmarks and stuff items.

### Bugs to fix along the way

- `bookmarks/tags.html` extends `bookmarks/base.html`, which doesn't exist,
  so a full-page load of that page should fail.
- The menus in `stuff/base.html` and `upkeep/base.html` never show up,
  because `base.html` has no `{% block menu %}`.
- Some links use `$refs.sidebarDrawer`, which only exists in the unused
  `sidebar.html`.
- `clearSearch()` is a global inline script, and nothing listens for the
  `clearSearch` event the server sends.
- Templates use `[x-cloak]`, but there's no CSS rule for it.
- The `htmx` context processor duplicates django-htmx's `request.htmx`.
- AGENTS.md says `just start`/`stop`/`load`, but the justfile recipes are
  `db-start`, `db-stop` and `db-load`.

## Design rules for the new stack

1. **Cotton components are reusable presentation; `partialdef`s are htmx
   swap targets.**
   - Views and `get_template` stay as they are. Pages keep
     `{% partialdef %}` blocks for fragments and build their markup from
     `<c-*>` components.
   - Components only get data passed in. They never query the database or
     read the request, except for a nav-item component that needs the
     current path.
     `COTTON_ENABLE_CONTEXT_ISOLATION` enforces this: a component sees its
     attributes plus the context processors, not the parent context.
2. **Component layout** under `puka/templates/cotton/`:
   - `ui/`: button, icon, card, badge, alert, table, pagination,
     breadcrumbs, tabs, empty state, search box → `<c-ui.button>`
   - `form/`: form, field, errors, actions →
     `<c-form.field :field="form.name" />`
   - `layout/`: page header, nav item, drawer, navbar
   - Files are snake_case: `<c-ui.search-box>` is `ui/search_box.html`.
   - Declare `class` in `<c-vars>` (bare, `class`, since djangofmt rejects
     `class=""`) and merge it into the root element, or a caller's `class`
     becomes a second `class` attribute via `{{ attrs }}`.
3. **htmx and Alpine attributes pass through** `{{ attrs }}`, so
   `<c-ui.button hx-post="…" hx-confirm="…">` works.
   - Anything that isn't meant to become an HTML attribute (for example
     `variant`, `icon`, `size`) must be declared in `<c-vars>`.
   - Alpine's shorthand `:class` has to be written `::class` on `<c-*>`
     tags. Use full `x-bind:` on component tags to avoid confusion.
4. **Write out full class names.** Map variants to complete daisyUI classes
   (`{% if variant == "primary" %}btn-primary{% endif %}`) rather than
   building `btn-{{ variant }}`. Tailwind can't find classes that are
   assembled at render time.
5. **Alpine only for client-side state:** the search box, tabs, clipboard
   and drawer close. Anything repeated moves into `Alpine.data(...)` in
   `base.js`. No inline `<script>` blocks.
6. **Explicit Cotton setup.** Use `django_cotton.apps.SimpleAppConfig` with
   loaders and builtins listed in `TEMPLATES`, rather than letting Cotton
   patch settings automatically, so the cached loader and Django 6 partials
   stay under our control.

## Phases

Each phase is its own jj change and has to pass `just test`,
`uv run ty check --error-on-warning`, `pre-commit run --all-files` and
`nix flake check` before moving on.

### Phase 0: Housekeeping

1. Delete `puka/templates/next/` and line 12 of `puka/urls.py`. The
   `TemplateView` import stays because the next line still uses it.
2. Delete the unused `sidebar.html`.
3. Fix `bookmarks/tags.html` so it extends `base.html`.

### Phase 1: Tests first

1. Add `tests/core/views_smoke_test.py`, parametrized over every named URL.
   For each, check a full-page GET returns 200 and contains `<head>`. With
   `HX-Request` set, check it returns the fragment without `<head>`.
2. Add create/update/delete POST tests for stuff (locations, inventory) and
   upkeep (areas, tasks, schedules, task items). Check redirects and
   `HX-Location` headers.
3. Add form-rendering tests: each form shows its fields, errors and
   `hx-post` action. These protect the crispy removal in Phase 4.
4. Fill the empty `tests/upkeep/views/` and add any missing factories in
   `tests/factories.py`.

### Phase 2: Install and check Cotton

1. Add `django-cotton` to `pyproject.toml`, then run `uv lock` and
   `uv sync`, and configure the loaders and builtins in
   `settings/base.py`.
2. Spike these before building anything on top, each with a test:
   - A template that uses `<c-*>` still resolves `template.html#partial`
     through Cotton's loader and the cached loader, both in `render()` and
     `{% include %}`.
   - djade and djangofmt (now a pre-commit hook) leave `<c-vars />` and
     `{{ attrs }}` alone.
   - Tailwind 4 auto-detection picks up `puka/templates/cotton/**`. If
     not, add an explicit `@source` to `base.css`, and check the Nix build
     in `nix/packages/static.nix` sees it.
   - The Nix integration test still passes. It depends on the order of
     `<link>` and `<script>` tags in `root.html`.
3. Add `[x-cloak]{display:none}` to `base.css`.

### Phase 3: Core components

1. Build the `ui/` and `layout/` components using daisyUI 5 syntax, checked
   against the daisyUI Blueprint tools while building.
2. Replace the `get_current_class` template tag with
   `<c-layout.nav-item url_name="…">`, then remove the tag.
3. Build `<c-ui.search-box>`, backed by `Alpine.data("searchBox")`, to
   replace the four copied search boxes and the global `clearSearch()`
   scripts. It either listens for the server's `clearSearch` event or the
   trigger gets removed.
4. Add a component test file that renders each component from a `Template`
   string and checks the output HTML.

### Phase 4: Forms

1. Build the form components:
   - `<c-form.form>`: the `<form>` tag with CSRF token, the `hx-post`
     action and non-field errors.
   - `<c-form.field>`: a daisyUI `fieldset` with label, the widget, help
     text and error styling. It picks the right markup by widget type:
     text/number/date/url, textarea, select, checkbox, file, and taggit.
   - `<c-form.actions>`: submit, cancel (`hx-get` to `#content`) and delete
     (`hx-post` with `hx-confirm`), replacing the three buttons in
     `core/forms.py`.
2. Grid layout moves out of Python `Layout`s and into templates. Each form
   gets a small template of `<c-form.field>`s inside a responsive grid, or
   a generic loop for simple forms.
3. Convert `LocationForm` first as the pilot, then the rest of the stuff
   and upkeep forms, then `BookmarkForm`, the filter forms and login.
4. Remove `crispy_forms` and `crispy_tailwind` from `INSTALLED_APPS`, the
   `CRISPY_*` settings, the dependencies, `FormHelper` code,
   `core/forms.py` and `templates/tailwind/`.
5. Done. `core/forms.py` stays, now holding the `FORM_RENDERER` that puts
   daisyUI classes on widgets (templates can't), and each form sets
   `template_name`. htmx 4 has no `hx-params`, so delete buttons drop it.

### Phase 5: Layout

1. Rebuild `root.html` and `base.html` using the layout components. Keep
   the drawer, `#breadcrumbs` and `#content` ids so the htmx targets don't
   change.
2. Decide what to do with the app sub-menus: add a `{% block menu %}` to
   the sidebar, or fold those links into the main nav.
3. Fix the drawer-close behaviour, using an `x-ref` in `base.html` or a
   small Alpine store.
4. Done. Sub-menus are folded into the main nav (nested
   `<c-layout.nav-item>`s); the app `{% block menu %}` partials are gone.
   `Alpine.data("drawer")` closes the drawer on sidebar link clicks and Esc.

### Phase 6: Convert page by page

Order: bookmarks → stuff → upkeep → overview, 404 and login.

For each page, keep the `partialdef` names, replace raw markup with
components, and swap the remaining ad-hoc Tailwind for daisyUI classes.
Check each converted page in the browser (full load, boosted navigation,
and every htmx action) plus its tests.

Done, one jj change per app. The overview shows real counts from a small
`overview` view. The login page lost its non-working "Remember me",
"Forgot password?" and "Sign up" controls, and the account menu its
"Settings" link. Browser checks are still to do.

### Phase 7: Cleanup

1. Remove the `htmx` context processor and use `request.htmx` in templates.
2. Remove unused `{% load utils %}` lines, and
   `puka/core/templatetags/utils.py` itself once `|domain` is dropped too.
3. Remove the `django_browser_reload` check in `urls.py`, or install it.
4. Update AGENTS.md with the Cotton conventions from above and the correct
   `just` recipe names.
5. Done. `|domain` became `Bookmark.domain`, so `puka/core/templatetags/`
   is gone. `django_browser_reload` was never installed; its URL hook is
   removed.

## Risks

- **Partials and Cotton's loader together** are the one unknown that could
  block the plan. Phase 2 checks it before anything else. If it fails, the
  fallback is to move fragments into their own files and reference them as
  `{% include %}` or Cotton components. Resolved in Phase 2: `#partial`
  names resolve through Cotton and the cached loader
  (`tests/core/cotton_spike_test.py`).
- **Tests in CI.** Pytest runs only on Linux in CI, so on macOS run
  `just test` locally for every change.
- **Large templates.** Pre-commit rejects files over 25 KB. Moving markup
  into components keeps templates small, but watch `item_detail.html`.
