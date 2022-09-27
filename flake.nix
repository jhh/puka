{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
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

            overrides = prev.poetry2nix.overrides.withDefaults
              (self: super: {
                uwsgi = super.uwsgi.overridePythonAttrs
                  (old:
                    {
                      buildInputs = (old.buildInputs or [ ]) ++ [ prev.expat prev.zlib ];
                    });
              });

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
              poetry
              nodejs-16_x
              postgresql
              pre-commit
              # watchman
            ] ++ pkgs.lib.optional pkgs.stdenv.isLinux pkgs.httpie;

            buildInputs = [ pkgs.expat pkgs.zlib ] ++ pkgs.lib.optional pkgs.stdenv.isDarwin pkgs.openssl;
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
                  echo Copying static files to $STATE_DIRECTORY.
                  ${pkg}/bin/manage.py collectstatic --no-input --clear --verbosity=0

                '';

              serviceConfig =
                let pkg = self.packages.${pkgs.system}.default;
                in
                {
                  # agenix secret in github:jhh/nixos-configs
                  EnvironmentFile = "/run/agenix/puka_secrets";
                  ExecStart = "${pkg}/bin/uwsgi  --http-socket 127.0.0.1:8000 --master --processes 2 --disable-logging --module config.wsgi";

                  Type = "notify";
                  NotifyAccess = "all";
                  KillSignal = "SIGQUIT";
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
              # security.acme is configured for eris globally in nginx.nix
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
