# just manual: https://github.com/casey/just#readme
_default:
    @just --list

# start development services (all if none given) and wait until ready
[group('dev')]
up *processes:
    #!/usr/bin/env bash
    set -euo pipefail

    # All processes from nix/process-compose.nix, in dependency order.
    all="postgres-init postgres migrate runserver watch mailpit"
    # One-shot processes that must not run again once they have succeeded.
    oneshot="migrate postgres-init"
    requested="{{ processes }}"
    if [[ -z "$requested" ]]; then
      target="$all"
    else
      target="$requested"
    fi

    deps_of() {
      case "$1" in
        postgres) echo "postgres-init" ;;
        migrate) echo "postgres" ;;
        runserver) echo "postgres migrate" ;;
        *) echo "" ;;
      esac
    }

    state_of() {
      puka-dev process list -o json |
        jq -r --arg n "$1" '.[] | select(.name == $n) | "\(.status) \(.exit_code)"'
    }

    wait_for() {
      local deadline=$((SECONDS + 180)) name state status ready probed exit_code pending
      while true; do
        pending=""
        for name in "$@"; do
          state=$(puka-dev process list -o json |
            jq -r --arg n "$name" '.[] | select(.name == $n) | "\(.status) \(.is_ready) \(.has_ready_probe) \(.exit_code)"')
          if [[ -z "$state" ]]; then
            echo "Unknown process: $name" >&2
            return 1
          fi
          read -r status ready probed exit_code <<<"$state"
          case "$status" in
            Running|Foreground|Launched)
              if [[ "$probed" == "true" && "$ready" != "Ready" ]]; then
                pending="$pending $name"
              fi
              ;;
            Completed)
              if [[ "$exit_code" != "0" ]]; then
                echo "Process '$name' failed (exit code $exit_code)." >&2
                puka-dev process logs "$name" >&2 || true
                return 1
              fi
              ;;
            Error|Skipped|Terminating)
              echo "Process '$name' failed (status: $status)." >&2
              puka-dev process logs "$name" >&2 || true
              return 1
              ;;
            *)
              pending="$pending $name"
              ;;
          esac
        done
        if [[ -z "$pending" ]]; then
          return 0
        fi
        if (( SECONDS >= deadline )); then
          echo "Timed out waiting for:$pending" >&2
          return 1
        fi
        sleep 1
      done
    }

    ensure() {
      local name=$1 dep state status exit_code
      for dep in $(deps_of "$name"); do
        ensure "$dep"
      done
      state=$(state_of "$name")
      status=${state%% *}
      exit_code=${state##* }
      if [[ "$status" != "Running" ]]; then
        if [[ " $oneshot " == *" $name "* && "$status" == "Completed" && "$exit_code" == "0" ]]; then
          return 0
        fi
        echo "Starting $name..."
        puka-dev process start "$name" >/dev/null
      fi
      wait_for "$name"
    }

    if ! puka-dev project state >/dev/null 2>&1; then
      # No server running: start the requested processes and their deps.
      # shellcheck disable=SC2086
      puka-dev up --detached $target
    else
      # Server running: start whatever is not running yet.
      for name in $target; do
        ensure "$name"
      done
    fi

    # shellcheck disable=SC2086
    wait_for $target

# stop all development services
[group('dev')]
down:
    #!/usr/bin/env bash
    set -euo pipefail
    if puka-dev project state >/dev/null 2>&1; then
      puka-dev down
    else
      echo "Development services are not running."
    fi

# open the process-compose TUI
[group('dev')]
attach:
    puka-dev attach

# run a process-compose client command, e.g. `just pc process list`
[group('dev')]
pc *args:
    puka-dev {{ args }}

# initialize and start the development database
[group('db')]
db-start: (up "migrate")

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

# format and lint templates using djangofmt
[group('test')]
djangofmt:
    uv run djangofmt puka/templates
    uv run djangofmt check puka/templates

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
manage *command:
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
    npx @tailwindcss/cli --input=puka/static/puka/base.css --output=puka/static/puka/main.css

# rebuild JS
[group('update')]
update-js:
    npx esbuild --bundle --outfile=puka/static/puka/main.js puka/static/puka/base.js

# watch CSS and rebuild
[group('run')]
watch: update-css update-js
    npx @tailwindcss/cli --watch=always --input=puka/static/puka/base.css --output=puka/static/puka/main.css
