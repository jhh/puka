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
test $DJANGO_SETTINGS_MODULE="puka.settings.test":
    uv run pytest tests

# run tests and create coverage report
coverage:
    uv run pytest --cov --cov-report=html tests
    [[ -x /usr/bin/open ]] && /usr/bin/open htmlcov/index.html

# run manage.py with command
manage command:
    uv run puka/manage.py {{ command }}

# run the development server
run: (manage "runserver")

# create database migrations if needed
makemigrations: (manage "makemigrations")

# migrate the database
migrate: (manage "migrate")

# run the ipython repl
shell: (manage "shell")

# start a new app in puka module
startapp appname:
    uv run puka/manage.py startapp {{ appname }}
    mv {{ appname }} puka/

# install pre-commit hooks
pre-commit:
    pre-commit install --install-hooks

# install npm deppendencies
npm-install:
    npm install

# update npm deppendencies to latest versions
npm-update:
    npm install tailwindcss@latest @tailwindcss/cli@latest @tailwindcss/forms@latest htmx.org@next alpinejs@latest @alpinejs/focus@latest esbuild@latest

# update CSS
update-css:
    rm -f .venv/.gitignore
    npx @tailwindcss/cli --input=puka/static/puka/base.css --output=puka/static/puka/main.css

# update JS
update-js:
    npx esbuild --bundle --outfile=puka/static/puka/main.js puka/static/puka/base.js

watch: update-css update-js
    npx @tailwindcss/cli --watch --input=puka/static/puka/base.css --output=puka/static/puka/main.css
