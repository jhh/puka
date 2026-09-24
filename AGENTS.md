# AGENTS.md

Django app (Python 3.12+, Tailwind/daisyUI/htmx/Alpine), Nix devshell,
`just` task runner. Run every command inside the Nix devshell.

## Environment

- The devshell comes from `flake.nix` via direnv (`use flake`). `uv`, `just`,
  `node`, and Postgres are only on `PATH` inside it; `uv run` outside the
  devshell will not use the pinned interpreter.
- `.env` only sets `DEBUG=true`. `DJANGO_DATABASE_URL` and `PG*` come from the
  devshell `shellHook` (local Postgres data dir is `.db/`).
- `just init`: npm install + build CSS/JS + write `.env`.
- `just start`: start local Postgres, create DB, migrate. `just stop` stops it.

## Commands

- Dev server: `just run` (`puka.settings.local`).
- manage.py: `just manage "cmd"` (e.g. `just migrate`, `just makemigrations`),
  or `uv run puka/manage.py ...`.
- Tests: `just test` or `uv run pytest tests`.
  - Bare `uv run pytest` collects nothing: `testpaths = ["puka"]` in
    `pyproject.toml`, but all tests live in `tests/`.
  - Single: `uv run pytest tests/stuff/item_model_test.py::test_name`.
  - Coverage: `just coverage`.
- Lint/format: `uv run ruff format .` then `uv run ruff check .`.
- Types: `just ty` (`uv run ty check`). `ty` is preferred over pyright/mypy.
- Templates: `just djade`.
- Assets: `just update-css`, `just update-js`, `just watch`.
- `pre-commit run --all-files`; the config is a Nix-store symlink, do not edit.

## Verification / CI

- CI runs `nix flake check` (`spotdemo4/nix-flake-check-action`). Reproduce with
  `nix flake check -L` before pushing; it is broader than ruff/pytest.
- NixOS integration tests (separate from pytest):
  `nix build .#checks.aarch64-darwin.puka-integration-tests -L`.

## Layout

- `puka/` Django project; apps: `bookmarks`, `core`, `stuff`, `upkeep`,
  `users`. Settings in `puka/settings/{base,local,test,production}.py`.
- `tests/` mirrors the apps; `tests/conftest.py` fixtures and
  `tests/factories.py` (factory_boy, registered via pytest-factoryboy).
- `puka/static/puka/base.{css,js}` are the sources; `main.{css,js}` are
  generated (gitignored) and also built by Nix in production — never edit them.
- `nix/` holds the devshell, deployment module, and static build; `justfile`
  is the canonical task list.

## Conventions

- Ruff: `line-length = 99`, `select = ["ALL"]` with repo ignores.
- Use `from __future__ import annotations`; PEP 604 unions and built-in
  generics; trailing commas in multi-line literals/calls.
- htmx: get templates with `get_template(request, "path", "#partial")` from
  `puka/core/views.py`; partials use `{% partialdef %}` and `#fragment`.
  Keep the root -> sidebar -> app template layout.
- VCS is Jujutsu (`jj`), colocated with git; use `jj`, not raw `git`.
