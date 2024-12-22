{
  lib,
  nixosModule,
  pkgs,
  workspace,
}:
let
  inherit (pkgs.stdenv) isLinux mkDerivation;
in
final: prev: {

  # puka is the name of our example package
  puka = prev.puka.overrideAttrs (old: {

    passthru = old.passthru // {
      tests =
        let
          venv = final.mkVirtualEnv "puka-check-env" {
            puka = [ "dev" ];
          };
        in
        (old.tests or { })
        // {

          mypy = mkDerivation {
            name = "${final.puka.name}-mypy";
            inherit (final.puka) src;

            nativeBuildInputs = [ venv ];

            dontConfigure = true;
            dontInstall = true;
            buildPhase = ''
              export MYPYPATH=apps
              mypy . --junit-xml $out/junit.xml
            '';
          };
        }
        // lib.optionalAttrs isLinux {
          #
          nixos =
            let
              venv = final.mkVirtualEnv "puka-nixos-test-env" workspace.deps.default;
              secrets = pkgs.writeText "puka-test-secrets" ''
                DJANGO_DATABASE_URL="postgres:///puka"
                DJANGO_ALLOWED_HOSTS="localhost,127.0.0.1"
                SECRET_KEY="test-secret-key"
              '';
            in
            pkgs.nixosTest {
              name = "puka-nixos-test";

              nodes.machine =
                { ... }:
                {
                  imports = [
                    nixosModule
                  ];

                  services.puka = {
                    enable = true;
                    inherit venv;
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

              testScript = ''
                with subtest("Check puka app comes up"):
                  machine.wait_for_unit("puka.service")
                  machine.wait_for_open_port(8001)

                with subtest("Staticfiles are generated"):
                  machine.succeed("curl -sf http://localhost:8001/static/puka/main.css")

                with subtest("Home page is live"):
                  machine.succeed("curl -sLf http://localhost:8001/ | grep 'New Bookmark'")
              '';
            };
        };
    };
  });

}
