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

          pytest = mkDerivation {
            name = "${final.puka.name}-pytest";
            inherit (final.puka) src;

            nativeBuildInputs = [
              venv
            ];

            dontConfigure = true;

            buildPhase = ''
              runHook preBuild
              # pytest --import-mode=importlib --cov tests --cov-report html
              runHook postBuild
            '';

            installPhase = ''
              runHook preInstall
              echo "nothing to see here" > $out
              # mv htmlcov $out
              runHook postInstall
            '';
          };
        }
        // lib.optionalAttrs isLinux {
          #
          nixos =
            let
              venv = final.mkVirtualEnv "puka-nixos-test-env" workspace.deps.default;
              secrets = pkgs.writeText "puka-test-secrets" ''
                DEBUG=false
                DJANGO_DATABASE_URL="sqlite:///tmp/db.sqlite3"
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

                  system.stateVersion = "24.11";
                };

              testScript = ''
                with subtest("Check puka app comes up"):
                  machine.wait_for_unit("puka.service")
                  machine.wait_for_open_port(8001)

                with subtest("Staticfiles are generated"):
                  machine.succeed("curl -sf http://localhost:8001/static/ui/main.css")

                with subtest("Home page is live"):
                  machine.succeed("curl -sLf http://localhost:8001/ | grep 'Upkeep'")
              '';
            };
        };
    };
  });

}
