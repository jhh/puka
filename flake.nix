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

      pythonSets = forAllSystems (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};

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
      nixosModules.puka = import ./lib/module.nix self;
      nixosModules.default = self.nixosModules.puka;

      packages = forAllSystems (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          pythonSet = pythonSets.${system};
          venv = pythonSet.mkVirtualEnv "puka-env" workspace.deps.default;
          inherit (pkgs.stdenv) mkDerivation;
        in
        {
          css-js =
            let
              pkgs = nixpkgs.legacyPackages.${system};
            in
            pkgs.buildNpmPackage {
              name = "django-static-deps";
              src = ./.;
              npmDepsHash = "sha256-VSYvzgzPYj/mGQ8SvdZB+UtaqgyAjy1fPivk1ioUU6o=";
              dontNpmBuild = true;

              buildPhase = ''
                runHook preBuild
                npx tailwindcss -m -i puka/static/css/base.css -o $out/puka/static/css/main.css
                # node ./static-build.mjs
                runHook postBuild
              '';

              installPhase = ''
                runHook preInstall
                # mkdir -p $out/ui
                # mv upkeep/ui/static/ui/main.* $out/ui
                runHook postInstall
              '';
            };

          static = mkDerivation {
            pname = "puka-static";
            inherit (pythonSet.puka) version;
            nativeBuildInputs = [ venv ];

            dontUnpack = true;
            dontConfigure = true;
            dontBuild = true;

            installPhase = ''
              export DJANGO_SETTINGS_MODULE=puka.settings.production
              export DJANGO_STATICFILES_DIR="${self.packages.${system}.css-js}"
              export SECRET_KEY=
              export STATIC_ROOT=$out
              mkdir -p $out
              ${venv}/bin/puka-manage collectstatic --no-input
            '';

          };
          venv = venv;
        }
      );

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
