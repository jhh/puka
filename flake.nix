{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, utils }:
    let
      out = system:
        let pkgs = nixpkgs.legacyPackages."${system}";
        in
        {

          devShell = pkgs.mkShell {

            nativeBuildInputs = with pkgs; [
              postgresql
              yarn
              python3Packages.poetry
              nodejs-16_x
            ];

            buildInputs = pkgs.lib.optional pkgs.stdenv.isDarwin pkgs.openssl;
          };

          packages.default = let puka = with pkgs.poetry2nix; mkPoetryApplication {
            projectDir = ./.;
            preferWheels = true;

            fixupPhase = ''
              tar -xzf build.tgz
              export SECRET_KEY=dummy
              export DJANGO_SETTINGS_MODULE=puka.settings.production
              python manage.py collectstatic --no-input
              cp -vfr build $out/lib/python3.9/site-packages/
            '';
          }; in puka.dependencyEnv;

        };
    in
    with utils.lib; eachSystem defaultSystems out // {

      nixosModules.default = { config, lib, pkgs, ... }:
        with lib;
        let
          cfg = config.j3ff.puka;
        in
        {
          options.j3ff.puka = {
            enable = mkEnableOption "Enable the Puka service";
          };

          config = mkIf cfg.enable
            {
              # systemd.timers.dyndns = {
              #   description = "Periodic update of home.j3ff.io DNS record";
              #   wantedBy = [ "multi-user.target" ];

              #   timerConfig = {
              #     OnBootSec = "15min";
              #     OnUnitActiveSec = "4h"
              #   };
              # };

              systemd.services.puka = {
                description = "Puka bookmarks";

                wantedBy = [ "multi-user.target" ];

                environment = {
                  DJANGO_SETTINGS_MODULE = "puka.settings.production";
                };

                serviceConfig =
                  let pkg = self.packages.${pkgs.system}.default;
                  in
                  {
                    # Type = "oneshot";
                    # agenix secret in github:jhh/nixos-configs
                    # LoadCredential = "AWS_SECRET_ACCESS_KEY:/run/agenix/aws_secret";
                    ExecStart = "${pkg}/bin/gunicorn puka.wsgi --log-file -";

                    DynamicUser = true;
                    NoNewPrivileges = true;
                    ProtectSystem = "strict";
                  };
              };
            };
        };



      nixosConfigurations.container = nixpkgs.lib.nixosSystem {
        system = "x86_64-linux";
        modules = [
          self.nixosModules.default
          ({ config, pkgs, ... }: {
            # Only allow this to boot as a container
            boot.isContainer = true;
            networking.hostName = "puka";

            j3ff.puka.enable = true;
          })
        ];
      };
    };

}
