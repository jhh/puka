{ inputs, self, ... }:
{
  systems = [
    "aarch64-darwin"
    "aarch64-linux"
    "x86_64-darwin"
    "x86_64-linux"
  ];

  flake = {
    lib = import ./lib {
      inherit inputs;
    };

    nixosModules.puka = import ./modules/nixos/puka.nix {
      flake = self;
    };

    modules.nixos.puka = self.nixosModules.puka;
  };

  perSystem =
    {
      config,
      inputs',
      pkgs,
      system,
      ...
    }:
    let
      # Supply arguments expected by the existing Nix functions.
      call = pkgs.lib.callPackageWith (
        pkgs
        // {
          inherit inputs pkgs system;
          flake = self;

          perSystem = {
            self = config.packages;
            uv2nix = inputs'.uv2nix.packages;
          };
        }
      );
    in
    {
      packages = {
        heroicons = call ./packages/heroicons.nix { };
        manage = call ./packages/manage.nix { };
        static = call ./packages/static.nix { };
        venv = call ./packages/venv.nix { };

        # Preserve Blueprint's formatter package export.
        formatter = call ./formatter.nix { };
      };

      formatter = config.packages.formatter;

      devShells.default = call ./devshell.nix { };

      checks = {
        pre-commit = call ./checks/pre-commit.nix { };

        puka-integration-tests = call ./checks/puka-integration-tests.nix { };

        # Preserve automatic package-build checks.
        pkgs-heroicons = config.packages.heroicons;
        pkgs-manage = config.packages.manage;
        pkgs-static = config.packages.static;
        pkgs-venv = config.packages.venv;
        pkgs-formatter = config.packages.formatter;

        # Preserve passthru-test discovery.
        pkgs-venv-ty-check = config.packages.venv.passthru.tests.ty-check;

        devshell-default = config.devShells.default;
      }
      // pkgs.lib.optionalAttrs pkgs.stdenv.hostPlatform.isLinux {
        pkgs-venv-pytest = config.packages.venv.passthru.tests.pytest;
      };
    };
}
