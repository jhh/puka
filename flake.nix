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
      # self,
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

      editableOverlay = workspace.mkEditablePyprojectOverlay {
        root = "$REPO_ROOT";
      };

      pythonSets = forAllSystems (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          inherit (pkgs) stdenv;

          baseSet = pkgs.callPackage pyproject-nix.build.packages {
            python = pkgs.python312;
          };
        in
        baseSet.overrideScope (
          lib.composeManyExtensions [
            pyproject-build-systems.overlays.default
            overlay
          ]
        )
      );
    in
    {
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
            pkgs.nixfmt-rfc-style
            pkgs.nodejs
            pkgs.pre-commit
            pkgs.tailwindcss
            uv
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
