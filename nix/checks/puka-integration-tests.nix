{
  lib,
  pukaModule,
  testers,
  writeShellScript,
  writeText,
}:
let
  secrets = writeText "puka-test-secrets" ''
    DJANGO_DATABASE_URL="postgres:///puka"
    DJANGO_ALLOWED_HOSTS="localhost,127.0.0.1"
    SECRET_KEY="test-secret-key"
  '';
in
testers.nixosTest {
  name = "puka-integration-tests";

  nodes.machine =
    { config, pkgs, ... }:
    let
      port = 8001;
    in
    {
      imports = [
        pukaModule
      ];

      services.puka = {
        enable = true;
        secrets = [ secrets ];
        inherit port;
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
      networking.firewall.allowedTCPPorts = [ port ];
      virtualisation.forwardPorts = [
        {
          host.port = port;
          guest.port = port;
        }
      ];

      system.stateVersion = "24.11";
    };

  extraPythonPackages = p: [ p.beautifulsoup4 ];
  skipTypeCheck = true;

  testScript =
    { nodes, ... }:
    let
      inherit (nodes.machine.services.puka) port venv;
      username = "alice";
      password = "sekret";
      createSuperUser = writeShellScript "create-puka-superuser" ''
        set -euo pipefail
        export DJANGO_SUPERUSER_PASSWORD="sekret"
        puka-manage createsuperuser --no-input --username="${username}" --email=alice@example.com
      '';
    in
    builtins.replaceStrings
      [
        "\${port}"
        "\${venv}"
        "\${createSuperUser}"
        "\${username}"
        "\${password}"
      ]
      [
        "${toString port}"
        "${venv}"
        "${createSuperUser}"
        "${username}"
        "${password}"
      ]
      (lib.readFile ./tests.py);
}
