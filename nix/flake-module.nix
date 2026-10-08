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
      pythonSet = self.lib.pythonSets pkgs;
      workspace = self.lib.workspace;
    in
    {
      packages = {
        heroicons = pkgs.callPackage ./packages/heroicons.nix { };

        manage = pkgs.callPackage ./packages/manage.nix {
          venv = config.packages.venv;
        };

        static = pkgs.callPackage ./packages/static.nix {
          heroicons = config.packages.heroicons;
          inherit pythonSet;
          venv = config.packages.venv;
        };

        venv = pkgs.callPackage ./packages/venv.nix {
          inherit pythonSet workspace;
        };

        # Preserve Blueprint's formatter package export.
        formatter = pkgs.callPackage ./formatter.nix {
          inherit inputs;
        };
      };

      formatter = config.packages.formatter;

      devShells.default = pkgs.callPackage ./devshell.nix {
        heroicons = config.packages.heroicons;
        pre-commit = config.checks.pre-commit;
        inherit pythonSet;
        uv = inputs'.uv2nix.packages.uv-bin;
      };

      checks = {
        pre-commit = pkgs.callPackage ./checks/pre-commit.nix {
          inherit inputs pythonSet system;
        };

        puka-integration-tests = pkgs.callPackage ./checks/puka-integration-tests.nix {
          pukaModule = self.nixosModules.puka;
        };

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
