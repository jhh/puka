# Agent Guide

## Overview
- Django app in `puka/` with app modules in `puka/*/`.
- Tests live in `tests/` and use pytest + pytest-django.
- Frontend uses Tailwind + daisyUI + htmx + Alpine + esbuild.
- Python commands are run via `uv run ...`; tasks via `just`.
- Nix is used for deployment; local dev uses just + uv.

## Key Paths
- `puka/`: Django project, apps, settings, templates.
- `puka/static/puka/`: base.css/base.js inputs; main.css/main.js outputs.
- `tests/`: pytest tests, fixtures, factories.
- `justfile`: canonical dev commands.

## Bootstrap
- `just init`: npm install + build CSS/JS + write `.env`.
- `.env` created with `DEBUG=true`; adjust as needed.

## Run
- `just run`: dev server (uses `puka.settings.local`).
- `just manage "cmd"`: run Django manage.py commands.
- `just shell`: Django shell (IPython if installed).
- `just makemigrations` / `just migrate`: schema changes.

## Build Assets
- `just update-css`: build `puka/static/puka/main.css`.
- `just update-js`: build `puka/static/puka/main.js`.
- `just watch`: watch + rebuild CSS (also builds JS once).
- Do not hand-edit `puka/static/puka/main.css` or `puka/static/puka/main.js`;
  edit the base files.

## Lint / Format / Types
- `uv run ruff format .`: format Python.
- `uv run ruff check .`: lint Python (rules = ALL w/
  repo ignores).
- `just ty`: run `uv run ty check` type checks.
- `pre-commit run --all-files`: run hooks if installed.
- Hooks include add-trailing-comma, django-upgrade, pyupgrade, ruff check --fix,
  ruff format, djade.

## Django Template Formatting
- Use 4-space indentation for HTML elements and align Django template tags
  with their corresponding HTML structure.
- Tags with more than one attributes can have one indented attribute per line.
  example:

      <a
          href="?tags={{ tag }}"
          hx-get="?tags={{ tag }}"
      >


- `just djade`: lint Django templates

## Tests
- `just test`: run pytest with test settings.
- `uv run pytest tests`: same as above.
- Single file:
  `uv run pytest tests/bookmarks/views_test.py`.
- Single test:
  `uv run pytest tests/bookmarks/views_test.py::test_bookmarks`.
- Name filter:
  `uv run pytest tests/bookmarks -k "tags"`.
- Coverage: `just coverage` (opens `htmlcov/index.html`).

## Python Style
- Keep lines <= 99 chars (ruff config).
- Prefer `from __future__ import annotations` in new modules.
- Use PEP 604 unions (`A | B`) and built-in generics
  (`list[str]`, `dict[str, int]`).
- Type annotate public functions, model methods, and managers.
- Add `objects: ModelManager` and typed `models.Manager[...]`
  on models when custom managers are used.
- Use ruff format; do not hand-align or custom wrap.
- Prefer trailing commas in multi-line literals/calls.

## Imports
- Order: `__future__`, stdlib, third-party, local.
- Use absolute imports within the project (e.g.
  `from puka.core.views import get_template`).
- Keep imports at top-level; avoid inside functions unless
  required (see manage.py for the rare exception).

## Django Conventions
- Use `get_template(request, "...", "#partial")` for htmx
  partial rendering; see `puka/core/views.py`.
- For FBVs, use `@require_http_methods` and return
  `HttpResponseLocation` for htmx redirects.
- For CBVs, override `get_template_names()` and use the
  htmx-aware template helper.
- Use `get_object_or_404` for lookup by id; avoid raw
  `Model.objects.get` in views.
- Use `select_related` / `prefetch_related` for list/detail
  queries to avoid N+1.
- Prefer `natural_key` methods where natural keys exist.

## Error Handling
- Raise explicit exceptions with clear messages (see
  `Task.next_date`).
- Do not swallow exceptions; avoid bare `except`.
- Validate user input via forms; re-render form on errors.

## Logging
- Use `logger = logging.getLogger(__name__)`.
- Use lazy formatting: `logger.debug("msg %s", value)`.
- Keep log volume low in hot paths.

## Templates
- Templates live under `puka/templates/`.
- htmx partials use `#fragment` syntax and `{% partialdef %}`.
- Preserve existing layout structure (root -> sidebar -> app).
- Use Tailwind + daisyUI classes; keep class names inline.
- Use `hx-target="#id_content"` for main content swaps.

## Frontend JS/CSS
- Edit `puka/static/puka/base.css` and `base.js` only.
- JS uses ES modules, Alpine, and htmx globals.
- Build outputs are `main.css` and `main.js`.
- Keep imports sorted and minimal in JS (see `base.js`).
- Use daisyui-blueprint MCP for component design input.

## Tests and Fixtures
- Tests use pytest + pytest-django; files end with
  `*_test.py`.
- Shared fixtures live in `tests/conftest.py`.
- Factories live in `tests/factories.py` (factory_boy).
- Prefer fixtures and factories over ad hoc object creation.
- Use pytest-django asserts (assertTemplateUsed, etc.).

## Naming
- Classes: `PascalCase`; views end with `View`.
- Functions/vars: `snake_case`.
- URLs: `app_name` + named paths (e.g. `name="list"`).
- Constants: `UPPER_SNAKE` when needed.

## Type Checking
- `ty` is the preferred checker; config in `pyproject.toml`.
- Django stubs are enabled; keep models and forms typed.

## Cursor / Copilot Rules
- No `.cursor/rules`, `.cursorrules`, or
  `.github/copilot-instructions.md` found.

## Gotchas
- Tests use `puka.settings.test`; dev server uses
  `puka.settings.local` (see `puka/manage.py`).
- Search features rely on Postgres search types; be careful
  when changing search fields or indexes.
- Django admin URLs live at `/admin/`.

## When Adding New Code
- Mirror existing patterns in the relevant app module.
- Keep htmx partial behavior consistent with existing pages.
- Update tests or add new ones alongside feature changes.
- Run format + lint + tests for touched areas.

## Notes
- This file is for agentic coding tools working in this repo.
- Prefer minimal, focused changes; avoid unrelated refactors.
- Keep Markdown lines <= 80 chars.
- use context7 MCP to search documentation.

## End
- If instructions conflict, follow repository conventions first.
