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
- Don't run `just run` alongside `just up` (both use port 8000).
- `just db-load` pulls production data over `ssh eris`; needs prod access.
- Postgres and process-compose use Unix sockets under the repo (`.db/`,
  `.run/`); the ~103-byte macOS socket limit means very deep worktree
  paths can break them.

## Commands

- Dev server: `just run` (`puka.settings.local`).
- manage.py: `just manage "cmd"`, `just migrate`, `just makemigrations`,
  or `uv run puka/manage.py ...`.
- Tests: `just test`; see `tests/AGENTS.md` for pytest details.
- Lint/format: `uv run ruff format .` then `uv run ruff check .`. On NixOS
  the ruff and ty wheels in `.venv` can't run; use the devshell `ruff`
  and `ty` with `--python .venv` instead.
- Types: `just ty`. CI runs `ty check --error-on-warning`, so use
  `uv run ty check --error-on-warning` to match; `ty` over pyright/mypy.
- Templates: `just djangofmt` (format + lint) and `just djade`.
- Assets: `just update-css`, `just update-js`, `just watch`. Rebuild after
  editing `base.css`/`base.js` or Tailwind classes in templates (see
  `puka/static/AGENTS.md`).

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
- Pre-commit: the `pre-commit` CLI is not on PATH, and jj does not run
  git hooks. Run the hook suite as a check instead:
  `nix build .#checks.aarch64-darwin.pre-commit -L` — it fails when a
  hook would rewrite a file. Formatter check only:
  `nix build .#checks.aarch64-darwin.treefmt -L`. `ruff`, `nixfmt` and
  `pyupgrade` are on PATH for quick local fixes. Hook config lives in
  `nix/AGENTS.md`.
- Browser QA: the `playwright` MCP server in `opencode.json` runs
  headless Chromium (`nix run nixpkgs/nixos-26.05#playwright-mcp`,
  intentionally outside the flake outputs to keep `nix flake check`
  lean). Run `just up` first and keep screenshots in `.playwright-mcp/`
  (gitignored). `just browser-auth` writes `.playwright-mcp/auth.json`,
  which the server loads via `--storage-state` to sign the browser in as
  a local `qa` user; rerun it after the session expires or the database
  is rebuilt.

## Layout

- `puka/` Django project; apps `bookmarks`, `core`, `stuff`, `upkeep`,
  `users`. Settings in `puka/settings/{base,local,test,production}.py`.
- `tests/` mirrors the apps (see `tests/AGENTS.md`).
- `puka/static/puka/base.{css,js}` are sources; `main.{css,js}` are
  generated (gitignored) and built by Nix in production. Never edit them.
- `nix/` holds devshell, checks, packages, and the NixOS module
  (`nix/modules/nixos/puka.nix`); `justfile` is the canonical task list.

## Conventions

- Ruff: `line-length = 99`, `select = ["ALL"]` with repo ignores. Ruff
  and `ty` both exclude `*/migrations/`.
- `from __future__ import annotations`; PEP 604 unions; built-in generics;
  trailing commas in multi-line literals/calls.

## Area guides

More specific rules live next to the code; OpenCode loads them when the
agent reads files in that area. Read them directly when working there.

- `puka/AGENTS.md` — Django views, forms, and settings conventions.
- `puka/templates/AGENTS.md` — template hierarchy, partials, htmx 4.
- `puka/templates/cotton/AGENTS.md` — Cotton component authoring rules.
- `puka/static/AGENTS.md` — CSS/JS sources and generated bundles.
- `tests/AGENTS.md` — pytest setup and test conventions.
- `nix/AGENTS.md` — devshell, checks, pre-commit config, NixOS module.
