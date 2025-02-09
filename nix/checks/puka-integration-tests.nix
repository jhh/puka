{
  flake,
  pkgs,
  system,
  ...
}:
let
  inherit (pkgs) lib;
  secrets = pkgs.writeText "puka-test-secrets" ''
    DJANGO_DATABASE_URL="postgres:///puka"
    DJANGO_ALLOWED_HOSTS="localhost,127.0.0.1"
    SECRET_KEY="test-secret-key"
  '';
in
pkgs.nixosTest {
  name = "puka-integration-tests";
  meta.platforms = lib.platforms.linux;

  nodes.machine = {
    imports = [
      flake.modules.nixos.puka
    ];

    services.puka = {
      enable = true;
      inherit (flake.packages.${system}) venv;
      secrets = [ secrets ];
      port = 8001;
    };

    services.postgresql = {
      enable = true;
      package = pkgs.postgresql_16;
      ensureDatabases = [ "puka" ];
      ensureUsers = [
        {
          name = "puka";
          ensureDBOwnership = true;
        }
      ];
    };

    system.stateVersion = "24.11";
  };

  testScript =
    { nodes, ... }:
    let
      inherit (nodes.machine.services.puka) port venv;
    in
    ''
      import uuid

      base_url = "http://localhost:${toString port}"
      login_url = f"{base_url}/admin/login/"
      cookie_jar_path = "/tmp/cookies.txt"
      curl = f"curl --cookie {cookie_jar_path} --cookie-jar {cookie_jar_path} --fail --show-error --silent"

      # wait for service
      machine.wait_for_unit("puka.service")
      machine.wait_until_succeeds(f"{curl} -sLf {login_url}")

      # create a superuser
      username = "username"
      password = "password"

      machine.succeed(f"""
        sudo -u puka env \
        DJANGO_SETTINGS_MODULE=puka.settings.production \
        SECRET_KEY=test \
        DJANGO_SUPERUSER_PASSWORD='{password}' \
        ${venv}/bin/puka-manage createsuperuser --no-input --username='{username}' --email=nobody@j3ff.io
        """
      )

      # log in as superuser
      csrf_token = machine.succeed(f"grep csrftoken {cookie_jar_path} | cut --fields=7").rstrip()
      machine.succeed(f"""
        {curl} \
        --data 'csrfmiddlewaretoken={csrf_token}' \
        --data 'username={username}' \
        --data 'password={password}' \
        {login_url}
        """
      )

      # test that main bookmarks list is available
      assert "New Bookmark" in machine.succeed(f"{curl} --location {base_url}"), "T001"

      # create a new bookmark

      title = str(uuid.uuid1())
      csrf_token = machine.succeed(f"grep csrftoken {cookie_jar_path} | cut --fields=7").rstrip()
      machine.succeed(f"""
        {curl} -X POST \
        --data 'csrfmiddlewaretoken={csrf_token}' \
        --data 'title={title}' \
        --data 'description=' \
        --data-urlencode 'url=http://example.com' \
        --data 'tags=foobar' \
        --data 'active=on' \
        {base_url}/bookmarks/new/
        """
      )

      # check for this new bookmark in main bookmark list
      output = machine.succeed(f"{curl} --location {base_url}")
      assert title in output, "T002"
      assert "http://example.com" in output, "T003"
      assert "foobar" in output, "T004"
    '';
}
