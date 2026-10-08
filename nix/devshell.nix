{
  perSystem =
    {
      config,
      inputs',
      pkgs,
      pythonSet,
      ...
    }:
    let
      pg = config.process-compose.puka-dev.services.postgres.postgres;
    in
    {
      devShells.default = pkgs.mkShell {
        packages = [
          pythonSet.python
          pkgs.jq
          pkgs.just
          pkgs.nil
          pkgs.nix-output-monitor
          pkgs.nixfmt
          pkgs.nodejs
          pkgs.postgresql_17
          pkgs.postgresql_17.pg_config
          inputs'.uv2nix.packages.uv-bin
          config.packages.puka-dev
        ]
        ++ config.pre-commit.settings.enabledPackages;

        env = {
          HEROICONS_DIR = "${config.packages.heroicons}/share/heroicons/optimized/";
          UV_NO_SYNC = "1";
          UV_PYTHON = pythonSet.python.interpreter;
          UV_PYTHON_DOWNLOADS = "never";
          PGPORT = toString pg.port;
          PGUSER = pg.superuser;
          PGDATABASE = "puka";
        };

        shellHook = ''
          unset PYTHONPATH
          export PGDATA=$(git rev-parse --show-toplevel)/${pg.dataDir}
          export PGHOST=$PGDATA
          export DJANGO_DATABASE_URL=postgres://$(echo $PGHOST | sed -e 's/\//%2f/g')/puka

          if ! pg_isready -h "$PGHOST" -p "$PGPORT" -q 2>/dev/null; then
            echo ""
            echo "╔══════════════════════════════════════════════╗"
            echo "║  WARNING: PostgreSQL is not running.         ║"
            echo "║  Run 'just db-start' or 'just up' first.     ║"
            echo "╚══════════════════════════════════════════════╝"
            echo ""
          fi

          ${config.pre-commit.installationScript}
        '';
      };
    };
}
