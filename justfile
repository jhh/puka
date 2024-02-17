# just manual: https://github.com/casey/just#readme

_default:
  @just --list

# bootstrap the development environment
bootstrap: venv pre-commit

# open the project in Pycharm
edit:
  pycharm .

# run the development server
run check="none":
    python {{ if check != "none" { "-X dev" } else { "" } }} manage.py runserver

# update CSS and download all JS dependencies
update: venv update-css update-htmx
    direnv reload

# update CSS
update-css:
    tailwindcss -i puka/static/css/base.css -o puka/static/css/main.css

CURL := "curl --no-progress-meter --location"
JS_DIR := "--output puka/static/js"

HTMX_BASE := "https://unpkg.com/htmx.org/dist"
HTMX_EXT_BASE := "https://unpkg.com/htmx.org/dist/ext"
HTMX_JS := "htmx.min.js"
CLASS_TOOLS_JS := "class-tools.js"

# update the HTML library
update-htmx:
    {{ CURL }} {{ HTMX_BASE }}/{{ HTMX_JS }} {{ JS_DIR }}/{{ HTMX_JS }}
    {{ CURL }} {{ HTMX_EXT_BASE }}/{{ CLASS_TOOLS_JS }} {{ JS_DIR }}/{{ CLASS_TOOLS_JS }}

HYPERSCRIPT_BASE := "https://unpkg.com/hyperscript.org"
HYPERSCRIPT_VERSION := "0.9.12"
HYPERSCRIPT_JS := "_hyperscript.min.js"

update-hyperscript:
    {{ CURL }} {{ HYPERSCRIPT_BASE }}@{{ HYPERSCRIPT_VERSION }} {{ JS_DIR }}/{{ HYPERSCRIPT_JS }}

# checks poetry.lock against the version of pyproject.toml and locks if neccessary
poetry-check:
    poetry check --lock --quiet || (just poetry-lock)

# locks the python packages in pyproject.toml without updating the poetry env
poetry-lock:
    poetry lock --no-update

# install pre-commit hooks
pre-commit:
    pre-commit install --install-hooks

# refresh the python packages in the dev env
venv: poetry-check
    nix build .#devEnv -o .venv
