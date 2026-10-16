# Template conventions

Templates under `puka/templates/`. Repo-wide setup and commands are in the
root `AGENTS.md`.

- Templates extend `root.html` -> `base.html` (drawer, navbar, sidebar) ->
  optional app `base.html` -> page.
- Templates define `{% partialdef name %}` (Django 6 built-in partials) as
  htmx swap targets; Cotton components (see
  `puka/templates/cotton/AGENTS.md`) are presentation only.
- In templates, test `request.htmx` (django-htmx) for htmx requests.
- `htmx.org` is pinned to `4.0.0` in `just update-npm`; use htmx 4 APIs
  (no `hx-params`; the `HX-Trigger` events bubble to `window`).
- Render forms with the `c-form` components, not hand-written markup (see
  `puka/AGENTS.md`).
