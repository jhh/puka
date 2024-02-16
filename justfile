# just manual: https://github.com/casey/just#readme

_default:
  @just --list

# bootstrap the development environment
bootstrap: venv node pre-commit

# run the development server
run check="none": update
    python {{ if check != "none" { "-X dev" } else { "" } }} manage.py runserver

# update CSS and download all JS dependencies
update: venv update-css

# update CSS
update-css mode="development":
    env NODE_ENV={{ mode }} npm run build

# checks poetry.lock against the version of pyproject.toml and locks if neccessary
poetry-check:
    poetry check --lock --quiet || (just poetry-lock)

# locks the python packages in pyproject.toml without updating the poetry env
poetry-lock:
    poetry lock --no-update

# install NPM CSS & JS dependencies
node:
    npm install

# install pre-commit hooks
pre-commit:
    pre-commit install --install-hooks

# refresh the python packages in the dev env
venv: poetry-check
    nix build .#devEnv -o .venv
