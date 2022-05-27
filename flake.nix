{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    poetry2nix.url = "github:nix-community/poetry2nix";
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix }:
    let
      # Nixpkgs overlay providing the application
      overlay = nixpkgs.lib.composeManyExtensions [
        poetry2nix.overlay
        (final: prev: {
          # The application
          puka = prev.poetry2nix.mkPoetryApplication {
            projectDir = ./.;
          };
        })
      ];

      out = system:
        let pkgs = import nixpkgs {
          inherit system;
          overlays = [ overlay ];
        };
        in
        {

          devShell = pkgs.mkShell {

            nativeBuildInputs = with pkgs; [
              nodejs-16_x
              postgresql
              pre-commit
              python3Packages.ipython
              python3Packages.poetry
              watchman
            ];

            buildInputs = pkgs.lib.optional pkgs.stdenv.isDarwin pkgs.openssl;
          };

          packages.default = pkgs.puka.dependencyEnv;

        };
    in
    with flake-utils.lib; eachSystem defaultSystems out // {

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
                    # agenix secret in github:jhh/nixos-configs
                    EnvironmentFile = "/run/agenix/puka_secrets";
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
