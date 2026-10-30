# Cotton component conventions

Authoring rules for Cotton components under `puka/templates/cotton/`.
Repo-wide setup and commands are in the root `AGENTS.md`; general template
rules are in `puka/templates/AGENTS.md`.

- Components live in `puka/templates/cotton/{ui,form,layout}/`; filenames
  are snake_case (`<c-ui.search-box>` is `ui/search_box.html`). Each starts
  with a `{% comment %}` describing its variables. Explicit setup:
  `django_cotton.apps.SimpleAppConfig`, loaders and builtins in `TEMPLATES`.
- Components are presentation only; `partialdef`s are htmx swap targets.
  `COTTON_ISOLATE_BY_DEFAULT` means a component sees its attributes plus
  context processors, not the parent context: pass data in. Only
  `layout/nav-item` and `ui/pagination` read the request. Isolated
  components get a plain `Context`, so Django's `{% querystring %}` needs
  an explicit mapping (`{% querystring request.GET page=... %}`).
- Attributes not declared in `<c-vars>` pass through `{{ attrs }}`, so put
  `hx-*` and `x-*` on component tags. Declare anything that isn't an HTML
  attribute (`variant`, `size`, `icon`, ...). Declare `class` bare
  (`class`, since djangofmt rejects `class=""`) and merge it into the root
  element, or the caller's class becomes a duplicate attribute.
- On component tags use `x-on:`/`x-bind:`, not `@`/`:` (Cotton treats
  `:attr` as a Python expression).
- Map variants to full daisyUI class names; never build `btn-{{ variant }}`,
  Tailwind can't see it. Example:
  `{% if variant == "primary" %} btn-primary{% endif %}`. Icons take the
  full heroicons class (`icon="hero-plus"`).
- Alpine is only for client state (`searchBox`, `tabs`, `drawer` in
  `Alpine.data` in `base.js`); no inline `<script>` blocks.
- Rendering a component from a string in tests needs
  `CottonCompiler().process(source)` first; see
  `tests/core/components_test.py`.
