# Django app conventions

Conventions for the Django apps under `puka/`. Repo-wide setup, commands,
and layout are in the root `AGENTS.md`.

## Views

- htmx: views return `get_template(request, "path.html", "#partial")` from
  `puka/core/views.py`.

## Forms

- Each form sets `template_name` to a template of `<c-form.field>`s and
  `<c-form.actions>`; pages wrap `{{ form }}` in `<c-form.form>`.
  `FORM_RENDERER` (`puka/core/forms.py`) adds daisyUI classes to widgets.
