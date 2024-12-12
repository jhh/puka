# just manual: https://github.com/casey/just#readme
_default:
    @just --list

# bootstrap the development environment
init: pre-commit npm-install
    echo DEBUG=true > .env

# run mypy type checks
mypy:
    uv run mypy --check-untyped-defs .

# run tests
test:
    uv run pytest

# run tests and create coverage report
coverage:
    uv run pytest --cov --cov-report=html
    [[ -x /usr/bin/open ]] && /usr/bin/open htmlcov/index.html

# run manage.py with command
manage command:
    uv run --no-sync puka/manage.py {{ command }}

# run the development server
run: (manage "runserver")

# create database migrations if needed
makemigrations: (manage "makemigrations")

# migrate the database
migrate: (manage "migrate")

# run the ipython repl
shell: (manage "shell")

# start a new app in upkeep module
startapp appname:
    uv run config/manage.py startapp {{ appname }}
    mv {{ appname }} upkeep/

# install pre-commit hooks
pre-commit:
    pre-commit install --install-hooks

npm-install:
    npm install

static-watch:
    node static-build.mjs --watch

static-build:
    node static-build.mjs

# temporarily update CSS
update-css:
    tailwindcss -i puka/static/css/base.css -o puka/static/css/main.css
