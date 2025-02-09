{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

    pyproject-nix = {
      url = "github:nix-community/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    uv2nix = {
      url = "github:adisbladis/uv2nix";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.uv2nix.follows = "uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    {
      self,
      nixpkgs,
      uv2nix,
      pyproject-nix,
      pyproject-build-systems,
      ...
    }:
    let
      inherit (nixpkgs) lib;
      forAllSystems = lib.genAttrs lib.systems.flakeExposed;

      workspace = uv2nix.lib.workspace.loadWorkspace { workspaceRoot = ./.; };

      overlay = workspace.mkPyprojectOverlay {
        sourcePreference = "wheel";
      };

      # editableOverlay = workspace.mkEditablePyprojectOverlay {
      #   root = "$REPO_ROOT";
      # };
      #            pyprojectOverrides =

      pythonSets = forAllSystems (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};

          baseSet = pkgs.callPackage pyproject-nix.build.packages {
            python = pkgs.python312;
          };

          psycopgOverrides = import ./lib/overrides-psycopg.nix { inherit pkgs; };
          pukaOverrides = import ./lib/overrides-puka.nix {
            inherit lib pkgs workspace;
            nixosModule = self.nixosModules.default;
          };
        in
        baseSet.overrideScope (
          lib.composeManyExtensions [
            pyproject-build-systems.overlays.default
            overlay
            psycopgOverrides
            pukaOverrides
          ]
        )
      );
    in
    {
      nixosModules.default = import ./lib/module.nix {
        inherit pythonSets workspace;
        packages = self.packages;
      };

      checks = forAllSystems (
        system:
        let
          pythonSet = pythonSets.${system};
        in
        # Inherit tests from passthru.tests into flake checks
        pythonSet.puka.passthru.tests
      );

      packages = forAllSystems (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          pythonSet = pythonSets.${system};
          venv = pythonSet.mkVirtualEnv "puka-env" workspace.deps.default;
          static = import ./lib/static.nix {
            inherit pkgs pythonSet venv;
          };
          manage = import ./lib/manage.nix {
            inherit pkgs pythonSet venv;
          };
        in
        {
          inherit manage static venv;
        }
      );

      apps = forAllSystems (system: {
        default = {
          type = "app";
          program = "${self.packages.${system}.manage}/bin/puka-manage";
        };
      });

      formatter = forAllSystems (system: nixpkgs.legacyPackages.${system}.nixfmt-rfc-style);

      devShells = forAllSystems (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          # editablePythonSet = pythonSets.${system}.overrideScope editableOverlay;
          # venv = editablePythonSet.mkVirtualEnv "puka-dev-env" workspace.deps.all;
          uv = uv2nix.packages.${system}.uv-bin;
          packages = [
            pkgs.just
            pkgs.nil
            pkgs.nix-output-monitor
            pkgs.nixfmt-rfc-style
            pkgs.nodejs
            pkgs.postgresql.dev
            pkgs.pre-commit
            uv
            pkgs.watchman
          ];
        in
        {
          default = pkgs.mkShell {
            inherit packages;
            shellHook = ''
              unset PYTHONPATH
              export UV_PYTHON_DOWNLOADS=never
            '';
          };
        }
      );
    };
}
