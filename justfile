# just manual: https://github.com/casey/just#readme

_default:
  @just --list

# bootstrap the development environment
bootstrap: venv pre-commit

# open the project in Pycharm
edit:
  pycharm .

# watch HTML templates and update CSS
watch:
    tailwindcss -i puka/static/css/base.css -o puka/static/css/main.css --watch

# run the development server
run check="none":
    python {{ if check != "none" { "-X dev" } else { "" } }} manage.py runserver

# update CSS and download all JS dependencies
update: venv update-css update-htmx update-alpine
    direnv reload

# update CSS
update-css:
    tailwindcss -i puka/static/css/base.css -o puka/static/css/main.css

CURL := "curl --no-progress-meter --location"
JS_DIR := "puka/static/js"

HTMX_BASE := "https://unpkg.com/htmx.org/dist"
HTMX_EXT_BASE := "https://unpkg.com/htmx.org/dist/ext"
HTMX_JS := "htmx.min.js"
CLASS_TOOLS_JS := "class-tools.js"

# update the HTML library
update-htmx:
    {{ CURL }} {{ HTMX_BASE }}/{{ HTMX_JS }} --output {{ JS_DIR }}/{{ HTMX_JS }}
    {{ CURL }} {{ HTMX_EXT_BASE }}/{{ CLASS_TOOLS_JS }} --output {{ JS_DIR }}/{{ CLASS_TOOLS_JS }}

    # add newline so pre-commit doesn't complain
    echo "" >> {{ JS_DIR }}/{{ HTMX_JS }}
    echo "" >> {{ JS_DIR }}/{{ CLASS_TOOLS_JS }}

# update the Alpine JS library to latest version
update-alpine:
    curl --no-progress-meter --location https://unpkg.com/alpinejs --output {{ JS_DIR }}/alpine.js
    curl --no-progress-meter --location https://unpkg.com/@alpinejs/focus --output {{ JS_DIR }}/alpine-focus.js

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
