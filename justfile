# just manual: https://github.com/casey/just#readme
_default:
    @just --list

# initialize and start the development database
[group('db')]
db-start:
  pg-start
  puka-db-init
  @just manage migrate

# stop the development database
[group('db')]
db-stop:
  pg-stop

# load data into the development database
[group('db')]
db-load:
  #!/usr/bin/env bash
  set -euo pipefail
  tmpfile=$(mktemp).json
  ssh eris puka-manage dumpdata --natural-foreign -e contenttypes -e auth.permission > $tmpfile
  echo Loading data from $tmpfile...
  uv run puka/manage.py loaddata $tmpfile

# bootstrap the development environment
[group('init')]
init: npm-install update-css update-js
  echo DEBUG=true > .env

# run ty type checks
[group('test')]
ty:
    uv run ty check

# lint templates using djade
[group('test')]
djade:
    uv run djade puka/templates/**/*.html

# run tests
[group('test')]
test $DJANGO_SETTINGS_MODULE="puka.settings.test":
    uv run pytest tests

# run tests and create coverage report
[group('test')]
coverage:
    uv run pytest --cov --cov-report=html tests
    [[ -x /usr/bin/open ]] && /usr/bin/open htmlcov/index.html

# run manage.py with command
[group('run')]
manage command:
    uv run puka/manage.py {{ command }}

# run the development server
[group('run')]
run: (manage "runserver")

# create database migrations if needed
[group('db')]
makemigrations: (manage "makemigrations")

# migrate the database
[group('db')]
migrate: (manage "migrate")

# run the ipython repl
[group('run')]
shell: (manage "shell")

# start a new app in puka module
[group('init')]
startapp appname:
    uv run puka/manage.py startapp {{ appname }}
    mv {{ appname }} puka/

# install npm deppendencies
[group('init')]
npm-install:
    npm install

# update npm deppendencies to latest versions
[group('update')]
update-npm:
    npm install tailwindcss@latest @tailwindcss/cli@latest @tailwindcss/forms@latest daisyui@latest htmx.org@4.0.0 alpinejs@latest @alpinejs/focus@latest esbuild@latest

# rebuild CSS
[group('update')]
update-css:
    rm -f .venv/.gitignore
    npx @tailwindcss/cli --input=puka/static/puka/base.css --output=puka/static/puka/main.css

# rebuild JS
[group('update')]
update-js:
    npx esbuild --bundle --outfile=puka/static/puka/main.js puka/static/puka/base.js

# watch CSS and rebuild
[group('run')]
watch: update-css update-js
    npx @tailwindcss/cli --watch --input=puka/static/puka/base.css --output=puka/static/puka/main.css
