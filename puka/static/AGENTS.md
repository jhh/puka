# Static asset conventions

Sources under `puka/static/`. Repo-wide setup and commands are in the root
`AGENTS.md`.

- `puka/static/puka/base.{css,js}` are the sources; `main.{css,js}` are
  generated (gitignored) with `just update-css`/`just update-js` (or
  `just watch` while developing) and by Nix in production. Never edit the
  generated files.
