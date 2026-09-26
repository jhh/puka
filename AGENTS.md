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
- `just start` / `just stop`: local Postgres (+ create DB + migrate).
- `just load` pulls production data over `ssh eris`; needs prod access.

## Commands

- Dev server: `just run` (`puka.settings.local`).
- manage.py: `just manage "cmd"`, `just migrate`, `just makemigrations`,
  or `uv run puka/manage.py ...`.
- Tests: `just test` or `uv run pytest tests`. Postgres must be running
  (`just start`); pytest-django creates `test_puka`.
  - Bare `uv run pytest` collects nothing: `testpaths = ["puka"]` in
    `pyproject.toml`, but tests live in `tests/` (`*_test.py`).
  - Single: `uv run pytest tests/stuff/item_model_test.py::test_name`.
  - Coverage: `just coverage`.
- Lint/format: `uv run ruff format .` then `uv run ruff check .`.
- Types: `just ty`. CI runs `ty check --error-on-warning`, so use
  `uv run ty check --error-on-warning` to match; `ty` over pyright/mypy.
- Templates: `just djade`.
- Assets: `just update-css`, `just update-js`, `just watch`. Rebuild after
  editing `base.css`/`base.js` or Tailwind classes in templates.
- `pre-commit run --all-files`. The config is a Nix-store symlink generated
  from `nix/checks/pre-commit.nix`; edit that, not the yaml. Hooks rewrite
  code: ruff, pyupgrade `--py312-plus`, django-upgrade `--target-version=5.2`,
  add-trailing-comma, djade, nixfmt; files >25 KB are rejected.

## Verification / CI

- CI is only `nix flake check -L --keep-going`. Reproduce locally before
  pushing. Checks: pre-commit, `ty` (warnings fatal), NixOS integration
  tests, and pytest (Linux-only, so skipped on macOS — run `just test`).
- NixOS integration tests (`nix/checks/tests.py`):
  `nix build .#checks.aarch64-darwin.puka-integration-tests -L`

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
  built-in partials). Keep the root -> sidebar -> app template layout.
- `htmx.org` is pinned to `4.0.0` in `just npm-update`; use htmx 4 APIs.
- Crispy forms use `crispy-tailwind`; overrides live in
  `puka/templates/tailwind/layout/`.
