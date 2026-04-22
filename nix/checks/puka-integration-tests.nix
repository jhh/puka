{
  flake,
  pkgs,
  ...
}:
let
  secrets = pkgs.writeText "puka-test-secrets" ''
    DJANGO_DATABASE_URL="postgres:///puka"
    DJANGO_ALLOWED_HOSTS="localhost,127.0.0.1"
    SECRET_KEY="test-secret-key"
  '';
in
pkgs.testers.nixosTest {
  name = "puka-integration-tests";

  nodes.machine =
    { pkgs, ... }:
    {
      imports = [
        flake.modules.nixos.puka
      ];

      environment.systemPackages = with pkgs; [
        wget
      ];

      services.puka = {
        enable = true;
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

  skipTypeCheck = true;

  testScript =
    { nodes, ... }:
    let
      inherit (nodes.machine.services.puka) port venv;
    in
    builtins.replaceStrings
      [
        "\${port}"
        "\${venv}"
      ]
      [
        "${toString port}"
        "${venv}"
      ]
      (pkgs.lib.readFile ./tests.py);
}
