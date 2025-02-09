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
    sudo -u puka env \
      DJANGO_SETTINGS_MODULE=puka.settings.production \
      DJANGO_DATABASE_URL=postgres:///puka \
      SECRET_KEY=not-secret \
      ${perSystem.self.venv}/bin/puka-manage "$@"
  '';
}
