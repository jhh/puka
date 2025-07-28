{
  pkgs ? import <nixpkgs> { },
}:
pkgs.writeShellApplication {
  name = "pg-dev";

  runtimeInputs = with pkgs; [ postgresql ];

  bashOptions = [
    "errexit"
    "pipefail"
  ];

  text = ''
    if [ -z "$PGHOST" ]; then
      echo "Error: PGHOST environment variable not set"
      exit 1
    fi

    if [ -z "$PGPORT" ]; then
      echo "Error: PGPORT environment variable not set"
      exit 1
    fi

    case "$1" in
      start)
        if [ ! -d "$PGHOST" ]; then
          echo "Initializing database at $PGHOST"
          initdb -D "$PGHOST" --auth-local=trust --auth-host=md5
          touch "$PGHOST/.first_startup"
        fi

        if pg_ctl -D "$PGHOST" status > /dev/null 2>&1; then
          echo "PostgreSQL is already running"
        else
          echo "Starting PostgreSQL server"
          pg_ctl -D "$PGHOST" -o "-k $PGHOST" -o "-p $PGPORT" -l "$PGHOST/postgres.log" start
          echo "PostgreSQL started successfully"
          if [[ -e "$PGHOST/.first_startup" ]]; then
            rm -f "$PGHOST/.first_startup"
            createdb -h "$PGHOST" -p "$PGPORT"  jeff && echo Created db jeff
            createdb -h "$PGHOST" -p "$PGPORT"  puka && echo Created db puka
            psql -p "$PGPORT" -tAc "ALTER USER $USER WITH SUPERUSER"
            echo "Superuser $USER created"
            psql -p "$PGPORT" -d puka -tA << END_INPUT
              ALTER DATABASE puka SET client_encoding TO 'UTF8';
              ALTER DATABASE puka SET default_transaction_isolation TO 'read committed';
              ALTER DATABASE puka SET timezone TO 'UTC';
    END_INPUT
            echo "Database puka created"
          fi
        fi
        ;;

      stop)
        if pg_ctl -D "$PGHOST" -o "-k $PGHOST" -o "-p $PGPORT" status > /dev/null 2>&1; then
          echo "Stopping PostgreSQL server"
          pg_ctl -D "$PGHOST" -o "-k $PGHOST" -o "-p $PGPORT" stop -m fast
          echo "PostgreSQL stopped successfully"
        else
          echo "PostgreSQL is not running"
        fi
        ;;

      status)
        if pg_ctl -D "$PGHOST" -o "-k $PGHOST" -o "-p $PGPORT" status > /dev/null 2>&1; then
          echo "PostgreSQL is running"
          pg_ctl -D "$PGHOST" -o "-k $PGHOST" -o "-p $PGPORT" status
        else
          echo "PostgreSQL is not running"
          exit 1
        fi
        ;;

      *)
        echo "Usage: $0 {start|stop|status}"
        echo "  start  - Initialize (if needed) and start PostgreSQL server"
        echo "  stop   - Stop PostgreSQL server"
        echo "  status - Check PostgreSQL server status"
        exit 1
        ;;
    esac
  '';
}
