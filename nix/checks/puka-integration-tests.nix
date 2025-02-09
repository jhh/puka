{
  inputs,
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
      inputs.srvos.nixosModules.server
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
    ''
      # wait for service
      machine.wait_for_unit("strykeforce-website.service")
      machine.wait_until_succeeds("curl -sLf http://localhost:8000/static/2767/main.css")
      machine.succeed("curl -sLf http://localhost:8000/static/2767/main.js")
      html = machine.succeed("curl -sLf http://localhost:8000/admin/")
      assert "<title>Sign in - Wagtail</title>" in html
    '';
}
