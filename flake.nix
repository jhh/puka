{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    utils.url = "github:numtide/flake-utils";
    poetry2nix.url = "github:nix-community/poetry2nix";
  };

  outputs = { self, nixpkgs, utils, poetry2nix }:
    let
      localOverlay = nixpkgs.lib.composeManyExtensions [
        poetry2nix.overlay
        (final: prev: {
          puka = prev.poetry2nix.mkPoetryApplication {
            projectDir = ./.;

            fixupPhase = ''
              export SECRET_KEY=dummy
              export DB_HOST=$SECRET_KEY
              export DB_PASSWORD=$SECRET_KEY
              export DJANGO_SETTINGS_MODULE=config.settings.production
              python manage.py collectstatic --no-input
              cp -vfr staticfiles $out/lib/python3.9/site-packages/
              mkdir -p $out/bin/
              cp -vf manage.py $out/bin/
            '';
          };
        })
      ];

      out = system:
        let
          pkgs = import nixpkgs {
            inherit system;
            overlays = [ localOverlay ];
          };

          localPython = pkgs.python39.withPackages (p: with p; [
            ipython
            poetry
          ]);

        in
        {

          devShell = pkgs.mkShell {
            nativeBuildInputs = with pkgs; [
              httpie
              localPython
              nodejs-16_x
              postgresql
              pre-commit
              watchman
            ];

            buildInputs = pkgs.lib.optional pkgs.stdenv.isDarwin pkgs.openssl;
          };

          packages.default = pkgs.puka.dependencyEnv;

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

          config = mkIf cfg.enable {
            systemd.services.puka = {
              description = "Puka Bookmarks";

              wantedBy = [ "multi-user.target" ];
              requires = [ "postgresql.service" ];
              after = [ "postgresql.service" ];

              environment = {
                DJANGO_SETTINGS_MODULE = "config.settings.production";
              };

              preStart = ''
                echo DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
              '';

              serviceConfig =
                let pkg = self.packages.${pkgs.system}.default;
                in
                {
                  # agenix secret in github:jhh/nixos-configs
                  EnvironmentFile = "/run/agenix/puka_secrets";
                  ExecStart = "${pkg}/bin/gunicorn config.wsgi --log-file -";

                  DynamicUser = true;
                  NoNewPrivileges = true;
                  ProtectSystem = "strict";
                };
            };

            services.postgresql = {
              ensureDatabases = [ "puka" ];
              ensureUsers = [
                {
                  name = "puka";
                  ensurePermissions."DATABASE puka" = "ALL PRIVILEGES";
                }
              ];
            };

            services.nginx.virtualHosts."puka.j3ff.io" = {
              forceSSL = true;
              enableACME = true;
              acmeRoot = null;

              locations = {
                "/" = {
                  proxyPass = "http://127.0.0.1:8000";
                };
              };
            };
          };
        };
    };

}
