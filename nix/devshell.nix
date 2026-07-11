{
  flake,
  inputs,
  perSystem,
  pkgs,
  system,
}:
let
  pythonSet = flake.lib.pythonSets pkgs;
  inherit (inputs.self.checks.${system}) pre-commit;

  pg-stop = pkgs.writeShellScriptBin "pg-stop" ''
    pg_ctl stop -D "$PGDATA" -m fast
  '';

  pg-start = pkgs.writeShellScriptBin "pg-start" ''
    if ! pg_ctl status > /dev/null 2>&1; then
      echo "starting PostgreSQL..."
      : > "$PGDATA/postgres.log"
      pg_ctl start --wait --log="$PGDATA/postgres.log" --options="-k $PGHOST -p $PGPORT"
    fi
  '';

  pg-status = pkgs.writeShellScriptBin "pg-status" ''
    if pg_isready -h "$PGHOST" -p "$PGPORT" -q; then
      echo "PostgreSQL is ready."
    else
      echo "PostgreSQL is not ready."
    fi
  '';

  puka-db-init = pkgs.writeShellScriptBin "puka-db-init" ''
    if ! psql -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='puka'" | grep -q 1; then
      psql -d postgres -tA << END_INPUT
      CREATE DATABASE puka;
      ALTER DATABASE puka SET client_encoding TO 'UTF8';
      ALTER DATABASE puka SET default_transaction_isolation TO 'read committed';
      ALTER DATABASE puka SET timezone TO 'UTC';
    END_INPUT
    fi
  '';
in
pkgs.mkShell {
  packages =
    with pkgs;
    [
      pythonSet.python
      just
      mailpit
      nil
      nix-output-monitor
      nixfmt-rfc-style
      nodejs
      postgresql_17
      postgresql_17.pg_config
      perSystem.uv2nix.uv-bin
      watchman
      pg-stop
      pg-start
      pg-status
      puka-db-init
    ]
    ++ pre-commit.enabledPackages;

  env = {
    HEROICONS_DIR = "${flake.packages.${system}.heroicons}/share/heroicons/optimized/";
    UV_NO_SYNC = "1";
    UV_PYTHON = pythonSet.python.interpreter;
    UV_PYTHON_DOWNLOADS = "never";
    PGPORT = 5432;
    PGUSER = "postgres";
    PGDATABASE = "puka";
  };

  shellHook = ''
    unset PYTHONPATH
    export PGDATA=$(git rev-parse --show-toplevel)/.db
    export PGHOST=$PGDATA
    export DJANGO_DATABASE_URL=postgres://$(echo $PGHOST | sed -e 's/\//%2f/g')/puka

    # Initialize if needed
    if [ ! -d "$PGDATA" ]; then
      echo "initializing puka database..."
      initdb \
        --auth-host=trust \
        --auth-local=trust \
        --encoding=UTF8 \
        --locale=C \
        --username=postgres

    fi

    if ! pg_isready -h "$PGHOST" -p "$PGPORT" -q 2>/dev/null; then
      echo ""
      echo "╔══════════════════════════════════════════════╗"
      echo "║  WARNING: PostgreSQL is not running.         ║"
      echo "║  Run 'just start' to start the database.     ║"
      echo "╚══════════════════════════════════════════════╝"
      echo ""
    fi

    ${pre-commit.shellHook}
  '';
}
