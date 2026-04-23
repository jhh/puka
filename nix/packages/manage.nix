{
  pkgs,
  perSystem,
  ...
}:
pkgs.writeShellApplication {
  name = "puka-manage";
  text = ''
    if [ "$UID" -ne 0 ]; then
        echo "error: run this command as root."
        exit 1
    fi

    export DJANGO_SETTINGS_MODULE=''${DJANGO_SETTINGS_MODULE:-puka.settings.production}
    export DJANGO_DATABASE_URL=''${DJANGO_DATABASE_URL:-postgres:///puka}
    export SECRET_KEY=not-secret
    runuser -u puka \
      -w DJANGO_SETTINGS_MODULE,DJANGO_DATABASE_URL,SECRET_KEY,DJANGO_SUPERUSER_PASSWORD \
      -- ${perSystem.self.venv}/bin/puka-manage "$@"
  '';
}
