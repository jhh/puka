# Plan: development services with process-compose-flake

## Goal and scope

Replace the hand-written Postgres scripts in `nix/devshell.nix` (`pg-start`,
`pg-stop`, `pg-status`, `puka-db-init` and the `initdb` block in
`shellHook`) and the `db-start`/`db-stop` recipes in `justfile` with a
declarative [process-compose-flake][pcf] configuration. Postgres comes from
the [services-flake][sf] `services.postgres` module, which is built on
process-compose-flake.

The process-compose project, named `puka-dev`, runs:

| Process | What it does |
| --- | --- |
| `postgres-init` | services-flake one-shot: `initdb`, create `puka` |
| `postgres` | services-flake Postgres 17 server, health-checked |
| `migrate` | one-shot `just migrate` once Postgres is healthy |
| `runserver` | `just run` (Django dev server) after `migrate` |
| `watch` | `just watch` (Tailwind CSS watcher) |
| `mailpit` | Mailpit SMTP on `127.0.0.1:1025`, UI on `:8025` |

Day to day it runs detached over a Unix socket. `just` recipes start, stop,
attach to and inspect it.

Do not change production packages, the NixOS module, the integration tests,
Django settings or `DJANGO_DATABASE_URL` semantics.

[pcf]: https://github.com/Platonic-Systems/process-compose-flake
[sf]: https://github.com/juspay/services-flake

## Constraints

- Run every command inside the Nix devshell (`direnv` / `nix develop`).
- Use Jujutsu (`jj` skill) for VCS work; never raw `git` commands for VCS.
  (Calling `git rev-parse` from scripts, as `shellHook` already does, is
  fine.)
- Run `jj st` immediately before `nix build`, `nix flake check` and
  `pre-commit run`, so the colocated Git tree includes new files.
- Context7 has no entries for process-compose-flake or services-flake.
  Read upstream sources on GitHub (`nix/process-compose/*.nix` in
  process-compose-flake, `nix/services/postgres/*.nix` in services-flake).
  For the process-compose CLI, use Context7 library
  `/websites/f1bonacc1_github_io_process-compose`. Option names below were
  correct when this plan was written; confirm them before relying on them.
- **`.db/` holds the developer's local data, loaded from production.** Never
  delete it. Back it up before any test that recreates it (Step 6).
- Do not name any process `test`. process-compose-flake turns a `test`
  process into a flake check, and that check would run in CI.
- Format Nix with `nixfmt`; keep Markdown lines at 80 characters or fewer
  and lint with `markdownlint-cli2`.

## Current behaviour to preserve

- Data directory and socket directory: `<repo root>/.db`. `PGHOST` is that
  directory, and `DJANGO_DATABASE_URL` is
  `postgres://<url-encoded .db path>/puka`.
- Postgres 17 (`pkgs.postgresql_17`), superuser `postgres`, trust auth,
  `--encoding=UTF8 --locale=C`, port 5432. Postgres also listens on TCP
  localhost.
- Database `puka`, configured with:

  ```sql
  ALTER DATABASE puka SET client_encoding TO 'UTF8';
  ALTER DATABASE puka SET default_transaction_isolation TO 'read committed';
  ALTER DATABASE puka SET timezone TO 'UTC';
  ```

- `just db-start` blocks until Postgres is up, `puka` exists and migrations
  have been applied. Afterwards `just test` and `just db-load` work.
- `PGUSER=postgres`, `PGDATABASE=puka` and `PGPORT=5432` stay in the
  devshell, so plain `psql` keeps working.
- Existing `.db` directories, initialized by the old `shellHook`, must keep
  working with no manual migration.

## Design notes

### Working directory

services-flake treats `dataDir` and `socketDir` as paths relative to the
current directory. The wrapper's `cli.preHook` must therefore `cd` to the
repository root, as `shellHook` does:

```sh
cd "$(git rev-parse --show-toplevel)"
```

Use `${lib.getExe pkgs.git}`, not a bare `git`. Child processes inherit
this working directory, so the `just` commands run from the repo root.

### Existing `.db` directories

services-flake's `postgres-init` runs `initdb` only when `dataDir` does not
exist. On every start it copies a generated `postgresql.conf` into the data
directory, overwriting the one `initdb` wrote. It also sets `hba_file` to a
generated trust-only `pg_hba.conf`. Both are acceptable. The
`initialDatabases` and `initialScript` options only take effect on a fresh
`initdb`. Existing `.db` directories already contain `puka` with the
`ALTER DATABASE` settings.

Because `initdb` only runs when `dataDir` is missing, nothing may create
`.db` before `postgres-init` runs. For that reason the process-compose
socket and log go in `.run/`, not `.db/`.

### Socket path length

Unix socket paths are limited to about 103 bytes on macOS. Both
`.db/.s.PGSQL.5432` and the `postgres-init` temporary socket at
`.db/pg-init-XXXXXX/.s.PGSQL.5432` must stay under that limit when they
include the absolute repo path. This is fine for the current checkout. Note
it in the README section if you add one.

### Detached mode and process environment

- process-compose passes its environment to child processes. `just`, `uv`,
  `npx` and the `DJANGO_*` and `PG*` variables therefore come from the
  devshell. The `puka-dev` wrapper is meant to be run inside the devshell,
  like every other command in this repo. Reference Nix-only tools such as
  `mailpit` by store path (`lib.getExe pkgs.mailpit`).
- process-compose reads `.env` from the working directory by default. That
  file only sets `DEBUG=true`, so leave this enabled.
- A detached process has no TTY and no stdin. The Tailwind v4 CLI's plain
  `--watch` exits when stdin closes. Change the `watch` recipe to
  `--watch=always`, after confirming with `npx @tailwindcss/cli --help`
  that the installed version supports it. Interactive `just watch` still
  works and stops with Ctrl-C.
- `pdb`/`breakpoint()` do not work inside process-compose. To debug, stop
  the `runserver` process (`just pc process stop runserver`) and run
  `just run` in a terminal.

### Wrapper options

The process-compose-flake wrapper runs
`process-compose <cli.options> "$@"`. Upstream recommends configuring global
settings through `cli.environment`, so subcommands such as `down`,
`attach` and `process list` still take their own flags. Use:

- `cli.environment.PC_SOCKET_PATH = ".run/process-compose.sock"`. Setting
  this enables Unix-socket mode and avoids the default TCP port 8080.
- `cli.environment.PC_LOG_FILE = ".run/process-compose.log"`
- `cli.environment.PC_ORDERED_SHUTDOWN = true`, so Postgres stops after
  `runserver`.

Before starting, `preHook` must `mkdir -p .run`, because process-compose
requires the socket directory to exist.

## Step 1: baseline

```sh
jj st
jj new -m "dev: manage development services with process-compose-flake"
nix flake show --all-systems --json > /tmp/flake-before.json
just db-start   # confirm the old flow works and note the output
just db-stop
```

Record the outputs of `ls .db`, `psql -c '\l'` and
`psql -c 'SELECT name, setting FROM pg_settings WHERE name IN
(''timezone'', ''default_transaction_isolation'', ''client_encoding'')'`
while the database is running. Step 6 compares against them.

## Step 2: flake inputs

Add the following to `flake.nix`:

```nix
process-compose-flake.url = "github:Platonic-Systems/process-compose-flake";
services-flake.url = "github:juspay/services-flake";
```

Run `nix flake lock`, then `nix flake metadata`. Add
`inputs.nixpkgs.follows = "nixpkgs"` only to inputs that actually declare a
`nixpkgs` input; at the time of writing, neither does.

## Step 3: `nix/process-compose.nix`

Create a flake-parts module and add `./process-compose.nix` to the
`imports` in `nix/default.nix`. Sketch:

```nix
{ inputs, ... }:
{
  imports = [ inputs.process-compose-flake.flakeModule ];

  perSystem =
    { lib, pkgs, ... }:
    {
      process-compose.puka-dev =
        { config, ... }:
        {
          imports = [ inputs.services-flake.processComposeModules.default ];

          cli = {
            preHook = ''
              cd "$(${lib.getExe pkgs.git} rev-parse --show-toplevel)"
              mkdir -p .run
            '';
            environment = {
              PC_SOCKET_PATH = ".run/process-compose.sock";
              PC_LOG_FILE = ".run/process-compose.log";
              PC_ORDERED_SHUTDOWN = true;
            };
          };

          services.postgres.postgres = {
            enable = true;
            package = pkgs.postgresql_17;
            dataDir = ".db";
            socketDir = ".db";
            superuser = "postgres";
            port = 5432;
            initialDatabases = [ { name = "puka"; } ];
            initialScript.after = pkgs.writeText "puka-db.sql" ''
              ALTER DATABASE puka SET client_encoding TO 'UTF8';
              ALTER DATABASE puka SET default_transaction_isolation
                TO 'read committed';
              ALTER DATABASE puka SET timezone TO 'UTC';
            '';
          };

          settings.processes = {
            migrate = {
              command = "just migrate";
              depends_on.postgres.condition = "process_healthy";
            };
            runserver = {
              command = "just run";
              depends_on.migrate.condition = "process_completed_successfully";
              availability.restart = "on_failure";
            };
            watch = {
              command = "just watch";
              availability.restart = "on_failure";
            };
            mailpit.command = lib.concatStringsSep " " [
              (lib.getExe pkgs.mailpit)
              "--smtp 127.0.0.1:1025"
              "--listen 127.0.0.1:8025"
            ];
          };
        };
    };
}
```

Notes:

- With service name `postgres`, services-flake creates the processes
  `postgres-init` and `postgres`. The `postgres` process has a
  `pg_isready` readiness probe, so `process_healthy` is meaningful.
- Leave `listen_addresses` at the default (`127.0.0.1`). The old setup also
  listened on localhost over TCP.
- Leave `initdbArgs` at the default (`--locale=C --encoding=UTF8`). Trust
  auth comes from the generated `pg_hba.conf`.
- Optionally add HTTP readiness probes for `runserver` (port 8000) and
  `mailpit` (port 8025), so `just pc process list` reports their health.
- The module generates `packages.<sys>.puka-dev`. `nix/checks/default.nix`
  maps every package to a check, so `checks.<sys>.pkgs-puka-dev` will also
  appear. It only builds a wrapper script and is acceptable. Record it as
  an intended output change.

## Step 4: `nix/devshell.nix`

1. Delete the `let` bindings `pg-stop`, `pg-start`, `pg-status` and
   `puka-db-init`, and remove them from `packages`.
2. Add `config.packages.puka-dev` to `packages`. Keep
   `pkgs.postgresql_17` and `pkgs.postgresql_17.pg_config`, which provide
   `psql` and the psycopg build. Remove `pkgs.mailpit`, since the process
   now uses it by store path.
3. Take the port and directory from the service config, so they are
   defined in one place:

   ```nix
   pg = config.process-compose.puka-dev.services.postgres.postgres;
   ```

   Use `PGPORT = pg.port;` and build `PGDATA`/`PGHOST` from `pg.dataDir`
   (`.db`) in `shellHook`. `pg.dataDir` must remain a relative path for
   this to work.
4. In `shellHook`, delete the `initdb` block (`postgres-init` now handles
   it). Keep the `PGDATA`, `PGHOST` and `DJANGO_DATABASE_URL` exports.
5. Update the "not running" banner to say `just up` (full stack) or
   `just db-start` (database only). The current text names a nonexistent
   `just start`. Keep the `pg_isready` check.
6. Add `watch_file nix/process-compose.nix` to `.envrc`.
7. Add `.run` to `.gitignore`.

## Step 5: `justfile`

Replace the `db-start` and `db-stop` recipes. Pass process names as
recipe arguments. `process-compose up NAME...` starts only the named
processes and their dependencies; verify this with
`process-compose up --help`.

```just
# start development services in the background (all if none given)
[group('dev')]
up *processes:
    ...

# stop all development services
[group('dev')]
down:
    puka-dev down

# open the process-compose TUI
[group('dev')]
attach:
    puka-dev attach

# run a process-compose client command, e.g. `just pc process list`
[group('dev')]
pc *args:
    puka-dev {{ args }}

# start the database and apply migrations
[group('db')]
db-start: (up "migrate")
```

Requirements for `up`:

- **Idempotent.** If the server is already running (check with
  `puka-dev project state > /dev/null 2>&1` or an equivalent), start the
  requested processes with `puka-dev process start NAME`. For `just up`
  with no names, start every process that is not running. Otherwise run
  `puka-dev up --detached {{ processes }}`.
- **Blocks until ready.** `db-start` callers, including `just test`, expect
  the database to be usable and migrated when it returns. First check
  whether `puka-dev project is-ready --wait` waits for `migrate` to finish
  with exit code 0. If it does not, poll
  `puka-dev process list --output json` (check the exact flag) until
  `postgres` is healthy and `migrate` has completed. Fail with a non-zero
  exit and print `just pc process logs migrate` if `migrate` fails.
- Use a `#!/usr/bin/env bash` shebang recipe with `set -euo pipefail`, like
  `db-load`.

Remove `db-stop`; `down` replaces it. Leave `db-load`, `migrate`,
`makemigrations`, `run` and `manage` unchanged. Change `watch` to pass
`--watch=always` (see Design notes).

## Step 6: verify

Run these with nothing else bound to ports 5432, 8000, 1025 or 8025.

1. **Evaluation and formatting**

   ```sh
   jj st
   nixfmt nix/*.nix flake.nix
   nix flake show --all-systems --json > /tmp/flake-after.json
   ```

   Diff the two JSON files. The only new outputs should be
   `packages.<sys>.puka-dev` and `checks.<sys>.pkgs-puka-dev`.

2. **Existing data directory**: run `direnv reload` (or re-enter the shell)
   and confirm that `which pg-start` finds nothing. Then:

   ```sh
   just db-start          # returns only after migrate succeeds
   just pc process list   # postgres healthy, migrate completed
   psql -c '\l'           # same databases as the baseline
   just test
   just down
   pg_isready             # not ready
   ```

   Compare the `pg_settings` query from Step 1.

3. **Full stack**: run `just up`. Then check that
   `curl -sf http://127.0.0.1:8000/` and
   `curl -sf http://127.0.0.1:8025/` succeed. Edit a Tailwind class in a
   template and confirm `puka/static/puka/main.css` is rebuilt. Run
   `just up` again and confirm it is a no-op. Run `just attach`, quit the
   TUI without stopping the server, then run `just down`.

4. **Fresh initialization** (protect the user's data):

   ```sh
   just down
   mv .db .db.bak
   just db-start
   psql -c "SELECT datname FROM pg_database WHERE datname = 'puka'"
   psql -d puka -c 'SHOW timezone'           # UTC
   just down
   rm -rf .db
   mv .db.bak .db
   just db-start                             # data is back
   just down
   ```

   If any step fails, restore `.db.bak` before debugging. Never delete
   `.db.bak` until `.db` has been restored.

5. **Subdirectory invocation**: run `cd puka && puka-dev up --detached`.
   Confirm it uses `<root>/.db` and `<root>/.run`, then run `just down`.

6. **CI parity**

   ```sh
   jj st
   pre-commit run --all-files
   uv run ty check --error-on-warning
   nix flake check -L --keep-going
   ```

## Step 7: documentation

- `AGENTS.md`, section Environment: replace the
  `just db-start` / `just db-stop` bullet with `just up` / `just down` /
  `just attach` / `just pc ...` and `just db-start` (database and
  migrations only). Mention that the data dir is `.db/` and the
  process-compose socket and log are in `.run/`.
- `AGENTS.md`, section Commands: in the Tests bullet, keep "Postgres must be
  running (`just db-start`)". Add that `just up` runs the dev server,
  Tailwind watcher and Mailpit in the background, and `just run` must not
  run alongside it because both use port 8000.
- `AGENTS.md`, section Verification: add the 103-byte socket path note if
  worktrees live in deep paths.
- Lint changed Markdown with `markdownlint-cli2`.

## Done when

- `nix/devshell.nix` contains no Postgres management scripts and no
  `initdb`.
- `just db-start`, `just up`, `just down`, `just attach` and `just pc` work
  as described, and `just up` is idempotent.
- Both existing and freshly initialized `.db` directories work, and the
  user's original `.db` is intact.
- `nix flake check` passes, and the only new outputs are `puka-dev` and
  `pkgs-puka-dev`.
- The change is described in a single jj change. Do not push.
