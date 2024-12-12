{ pkgs, pythonSet, venv }:
pkgs.writeShellApplication {
  name = "puka-manage";
  text = ''
    if [ "$UID" -ne 0 ]; then
        echo "error: run this command as root."
        exit 1
    fi
    sudo -u puka env DJANGO_DATABASE_URL=postgres:///puka ${venv}/bin/puka-manage "$@"
  '';
}
