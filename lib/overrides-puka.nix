{ lib
, nixosModule
, pkgs
, workspace
,
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

              testScript =
                { nodes, ... }:
                let
                  inherit (nodes.machine.services.puka) port venv;
                in
                ''
                  base_url = "http://localhost:${toString port}"
                  login_path = "/admin/login/"
                  login_url = f"{base_url}{login_path}"
                  cookie_jar_path = "/tmp/cookies.txt"
                  curl = f"curl --cookie {cookie_jar_path} --cookie-jar {cookie_jar_path} --fail --header 'Origin: {base_url}' --show-error --silent"

                  with subtest("Check puka app comes up"):
                    machine.wait_for_unit("puka.service")
                    machine.wait_until_succeeds(f"{curl} -sLf {login_url}")

                  username = "username"
                  password = "password"

                  print("Create superuser account")
                  machine.succeed(
                    f"""
                    sudo -u puka env \
                    DJANGO_SETTINGS_MODULE=puka.settings.production SECRET_KEY=test DJANGO_SUPERUSER_PASSWORD='{password}' \
                    ${venv}/bin/puka-manage createsuperuser --no-input --username='{username}' --email=nobody@j3ff.io
                    """
                  )

                  print("Log in as superuser")
                  csrf_token = machine.succeed(f"grep csrftoken {cookie_jar_path} | cut --fields=7").rstrip()
                  machine.succeed(
                    f"{curl} --data 'csrfmiddlewaretoken={csrf_token}' --data 'username={username}' --data 'password={password}' {login_url}"
                  )

                  print("Get the contents of the logged in main page")
                  machine.succeed(f"{curl} --location {base_url} | grep -q 'New Bookmark'")

                  print("Create a new bookmark")
                  csrf_token = machine.succeed(f"grep csrftoken {cookie_jar_path} | cut --fields=7").rstrip()
                  machine.succeed(
                    f""" {curl} -X POST \
                    --data 'csrfmiddlewaretoken={csrf_token}' \
                    --data 'title=Michigan' \
                    --data 'description=USA' \
                    --data-urlencode 'url=http://example.com' \
                    --data 'tags=foobar' \
                    --data 'active=on' \
                    {base_url}/bookmarks/new/
                    """
                  )

                  print("Check for new bookmark on main page")
                  machine.succeed(f"{curl} --location {base_url} | grep -q 'Michigan'")
                '';
            };
        };
    };
  });

}
