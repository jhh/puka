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

            postInstall = ''
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

        in
        {

          devShell = pkgs.mkShell {
            nativeBuildInputs = with pkgs; [
              python3
              poetry
              nodejs-16_x
              postgresql
              pre-commit
              watchman
            ] ++ pkgs.lib.optional pkgs.stdenv.isLinux pkgs.httpie;

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

              preStart =
                let pkg = self.packages.${pkgs.system}.default;
                in
                ''
                  ${pkg}/bin/manage.py migrate --no-input
                  ${pkg}/bin/manage.py collectstatic --no-input

                '';

              serviceConfig =
                let pkg = self.packages.${pkgs.system}.default;
                in
                {
                  # agenix secret in github:jhh/nixos-configs
                  EnvironmentFile = "/run/agenix/puka_secrets";
                  ExecStart = "${pkg}/bin/gunicorn config.wsgi --log-file -";

                  DynamicUser = true;
                  StateDirectory = "puka";
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
              authentication = ''
                local puka puka md5
              '';
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
