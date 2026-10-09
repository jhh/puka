# AGENTS.md

Django 6 app (Python 3.13 via Nix; Tailwind 4/daisyUI 5/htmx 4/Alpine),
Nix devshell, `just` task runner. Run every command inside the devshell.

## VCS: Jujutsu

- Use the `jj` skill for all VCS work (status, diff, describe, new, squash,
  bookmarks, push). Never run raw `git` even though `.git/` exists
  (colocated repo). Trunk bookmark is `main`; CI runs on PRs and `main`.

## Environment

- Devshell comes from `flake.nix` via direnv (`use flake`). `uv`, `just`,
  `node`, and Postgres are only on `PATH` inside it.
- `UV_NO_SYNC=1` is set: `uv run` never installs deps. After editing
  `pyproject.toml` run `uv lock` then `uv sync`. Nix builds resolve from
  `uv.lock` (uv2nix), so `nix flake check` fails if the lock is stale.
- `.env` only sets `DEBUG=true`. `DJANGO_DATABASE_URL` and `PG*` come from
  the devshell `shellHook`; local Postgres data dir is `.db/`.
- `just init`: npm install + build CSS/JS + write `.env`.
- `just up` / `just down`: development services (Postgres, migrate,
  Django runserver, Tailwind watcher, Mailpit) via process-compose
  (`nix/process-compose.nix`). `just db-start` starts Postgres + migrations
  only. `just attach` opens the process-compose TUI; `just pc ...` passes
  through other process-compose commands. Socket and logs are in `.run/`.
- `just db-load` pulls production data over `ssh eris`; needs prod access.

## Commands

- Dev server: `just run` (`puka.settings.local`).
- manage.py: `just manage "cmd"`, `just migrate`, `just makemigrations`,
  or `uv run puka/manage.py ...`.
- Tests: `just test` or `uv run pytest tests`. Postgres must be running
  (`just db-start`); pytest-django creates `test_puka`.
  - `just up` runs the dev server, Tailwind watcher and Mailpit in the
    background; don't run `just run` alongside it (both use port 8000).
  - Bare `uv run pytest` collects nothing: `testpaths = ["puka"]` in
    `pyproject.toml`, but tests live in `tests/` (`*_test.py`).
  - Single: `uv run pytest tests/stuff/item_model_test.py::test_name`.
  - Coverage: `just coverage`.
- Lint/format: `uv run ruff format .` then `uv run ruff check .`. On NixOS
  the ruff and ty wheels in `.venv` can't run; use the devshell `ruff`
  and `ty` with `--python .venv` instead.
- Types: `just ty`. CI runs `ty check --error-on-warning`, so use
  `uv run ty check --error-on-warning` to match; `ty` over pyright/mypy.
- Templates: `just djangofmt` (format + lint) and `just djade`.
- Assets: `just update-css`, `just update-js`, `just watch`. Rebuild after
  editing `base.css`/`base.js` or Tailwind classes in templates.
- Pre-commit hooks: there is no `pre-commit` CLI on PATH; run the hook
  suite with `nix build .#checks.aarch64-darwin.pre-commit -L` (see
  Verification / CI). The config is a Nix-store symlink generated from
  the git-hooks flake-parts module in `nix/checks/pre-commit.nix`; edit
  that, not the yaml. Hooks rewrite code: ruff, pyupgrade `--py312-plus`,
  django-upgrade `--target-version=5.2`, add-trailing-comma, djangofmt
  (then djade, then `djangofmt check`), nixfmt; files >25 KB are
  rejected.

## Verification / CI

- CI is only `nix flake check -L --keep-going`. Reproduce locally before
  pushing. It builds the `checks` output: pre-commit, treefmt, `ty`
  (warnings fatal), a check per package and devShell (`pkgs-*`,
  `devshell-default`), NixOS integration tests, and pytest (Linux-only,
  so skipped on macOS — run `just test`).
- Run `jj st` right before `nix flake check` (or `nix build`). Nix reads
  the source from the git tree, which jj only updates when it snapshots
  the working copy; without it, new or edited files may be missing from
  the build (e.g. `TemplateDoesNotExist` in the Nix pytest check).
- Pre-commit check: the `pre-commit` CLI is not on PATH, and jj does not
  run git hooks. Run the hook suite as a check instead:
  `nix build .#checks.aarch64-darwin.pre-commit -L` — it fails when a
  hook would rewrite a file. Formatter check only:
  `nix build .#checks.aarch64-darwin.treefmt -L`. `ruff`, `nixfmt` and
  `pyupgrade` are on PATH for quick local fixes.
- NixOS integration tests (`nix/checks/tests.py`):
  `nix build .#checks.aarch64-darwin.puka-integration-tests -L`
- Browser QA: the `playwright` MCP server in `opencode.json` runs
  headless Chromium (`nix run nixpkgs/nixos-26.05#playwright-mcp`,
  intentionally outside the flake outputs to keep `nix flake check`
  lean). Run `just up` first and keep screenshots in `.playwright-mcp/`
  (gitignored).
- Postgres and process-compose use Unix sockets under the repo (`.db/`,
  `.run/`); the ~103-byte macOS socket limit means very deep worktree
  paths can break them.

## Layout

- `puka/` Django project; apps `bookmarks`, `core`, `stuff`, `upkeep`,
  `users`. Settings in `puka/settings/{base,local,test,production}.py`.
- `tests/` mirrors the apps; `tests/conftest.py` fixtures and
  `tests/factories.py` (factory_boy, registered via pytest-factoryboy).
  DB tests need `@pytest.mark.django_db` or the `db` fixture.
- `puka/static/puka/base.{css,js}` are sources; `main.{css,js}` are
  generated (gitignored) and built by Nix in production. Never edit them.
- `nix/` holds devshell, checks, packages, and the NixOS module
  (`nix/modules/nixos/puka.nix`); `justfile` is the canonical task list.
- Ruff and `ty` both exclude `*/migrations/`.

## Conventions

- Ruff: `line-length = 99`, `select = ["ALL"]` with repo ignores.
- `from __future__ import annotations`; PEP 604 unions; built-in generics;
  trailing commas in multi-line literals/calls.
- htmx: views return `get_template(request, "path.html", "#partial")` from
  `puka/core/views.py`; templates define `{% partialdef name %}` (Django 6
  built-in partials). Templates extend `root.html` -> `base.html` (drawer,
  navbar, sidebar) -> optional app `base.html` -> page. In templates, test
  `request.htmx` (django-htmx) for htmx requests.
- `htmx.org` is pinned to `4.0.0` in `just update-npm`; use htmx 4 APIs
  (no `hx-params`; the `HX-Trigger` events bubble to `window`).
- Forms: each form sets `template_name` to a template of `<c-form.field>`s
  and `<c-form.actions>`; pages wrap `{{ form }}` in `<c-form.form>`.
  `FORM_RENDERER` (`puka/core/forms.py`) adds daisyUI classes to widgets.

## Cotton components

- Components live in `puka/templates/cotton/{ui,form,layout}/`; filenames
  are snake_case (`<c-ui.search-box>` is `ui/search_box.html`). Each starts
  with a `{% comment %}` describing its variables. Explicit setup:
  `django_cotton.apps.SimpleAppConfig`, loaders and builtins in `TEMPLATES`.
- Components are presentation only; `partialdef`s are htmx swap targets.
  `COTTON_ENABLE_CONTEXT_ISOLATION` means a component sees its attributes
  plus context processors, not the parent context: pass data in. Only
  `layout/nav-item` and `ui/pagination` read the request.
- Attributes not declared in `<c-vars>` pass through `{{ attrs }}`, so put
  `hx-*` and `x-*` on component tags. Declare anything that isn't an HTML
  attribute (`variant`, `size`, `icon`, ...). Declare `class` bare
  (`class`, since djangofmt rejects `class=""`) and merge it into the root
  element, or the caller's class becomes a duplicate attribute.
- On component tags use `x-on:`/`x-bind:`, not `@`/`:` (Cotton treats
  `:attr` as a Python expression).
- Map variants to full daisyUI class names (`{% if variant == "primary" %} btn-primary{% endif %}`); never build `btn-{{ variant }}`, Tailwind can't
  see it. Icons take the full heroicons class (`icon="hero-plus"`).
- Alpine is only for client state (`searchBox`, `tabs`, `drawer` in
  `Alpine.data` in `base.js`); no inline `<script>` blocks.
- Rendering a component from a string in tests needs
  `CottonCompiler().process(source)` first; see
  `tests/core/components_test.py`.
