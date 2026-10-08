{ inputs, ... }:
{
  imports = [ inputs.process-compose-flake.flakeModule ];

  perSystem =
    { lib, pkgs, ... }:
    {
      # `puka-dev` runs the development services; see docs/process-compose-dev-services.md.
      process-compose.puka-dev =
        { ... }:
        {
          imports = [ inputs.services-flake.processComposeModules.default ];

          cli = {
            # Services use paths relative to the repository root.
            preHook = ''
              cd "$(${lib.getExe pkgs.git} rev-parse --show-toplevel)"
              mkdir -p .run
            '';
            # services-flake defaults to --no-server; detached mode needs it.
            options.no-server = lib.mkForce false;
            environment = {
              PC_SOCKET_PATH = ".run/process-compose.sock";
              PC_LOG_FILE = ".run/process-compose.log";
              PC_ORDERED_SHUTDOWN = true;
            };
          };

          services.postgres.postgres = {
            enable = true;
            package = pkgs.postgresql_17;
            dataDir = ".db";
            socketDir = ".db";
            superuser = "postgres";
            port = 5432;
            initialDatabases = [ { name = "puka"; } ];
            # Only applied on a fresh initdb; existing data directories
            # already carry these settings.
            initialScript.after = pkgs.writeText "puka-db.sql" ''
              ALTER DATABASE puka SET client_encoding TO 'UTF8';
              ALTER DATABASE puka SET default_transaction_isolation TO 'read committed';
              ALTER DATABASE puka SET timezone TO 'UTC';
            '';
          };

          settings.processes = {
            migrate = {
              command = "just migrate";
              depends_on.postgres.condition = "process_healthy";
            };

            runserver = {
              command = "just run";
              depends_on.migrate.condition = "process_completed_successfully";
              availability.restart = "on_failure";
              readiness_probe = {
                http_get = {
                  host = "127.0.0.1";
                  port = 8000;
                  path = "/";
                };
                initial_delay_seconds = 2;
                period_seconds = 10;
                timeout_seconds = 4;
                success_threshold = 1;
                failure_threshold = 5;
              };
            };

            watch = {
              command = "just watch";
              availability.restart = "on_failure";
            };

            mailpit = {
              command = lib.concatStringsSep " " [
                (lib.getExe pkgs.mailpit)
                "--smtp 127.0.0.1:1025"
                "--listen 127.0.0.1:8025"
              ];
              readiness_probe = {
                http_get = {
                  host = "127.0.0.1";
                  port = 8025;
                  path = "/";
                };
                initial_delay_seconds = 1;
                period_seconds = 10;
                timeout_seconds = 4;
                success_threshold = 1;
                failure_threshold = 5;
              };
            };
          };
        };
    };
}
