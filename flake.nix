{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix }:
    flake-utils.lib.eachDefaultSystem
      (system:
        let
          version = "2.0.6"; # also set this version in pyproject.toml
          pkgs = nixpkgs.legacyPackages.${system};
          poetry2nixPkg = poetry2nix.lib.mkPoetry2Nix { inherit pkgs; };
          inherit (poetry2nixPkg) mkPoetryEnv mkPoetryApplication;
          inherit (pkgs.stdenv) mkDerivation;

          overrides = poetry2nixPkg.overrides.withDefaults (self: super: {
            uwsgi = super.uwsgi.overridePythonAttrs (old: {
              buildInputs = (old.buildInputs or [ ]) ++ [ super.setuptools pkgs.expat pkgs.zlib ];
            });
          });
        in
        {
          packages = {
            main = mkPoetryApplication {
              projectDir = self;
              inherit overrides;
              groups = [ "main" ];

              patchPhase = ''
                ${pkgs.tailwindcss}/bin/tailwindcss -i puka/static/css/base.css -o puka/static/css/main.css --minify
              '';

              postInstall = ''
                mkdir -p $out/bin/
                cp -vf manage.py $out/bin/
              '';
            };

            static = mkDerivation {
              pname = "puka-static";
              inherit version;
              src = self;
              phases = "unpackPhase installPhase";
              installPhase = ''
                export DJANGO_SETTINGS_MODULE=puka.settings.production
                export SECRET_KEY=
                export STATIC_ROOT=$out
                mkdir -p $out
                ${self.packages.${system}.main}/bin/manage.py collectstatic --no-input
              '';
            };

            devEnv = mkPoetryEnv {
              inherit overrides;
              projectDir = self;
              groups = [ "main" "dev" ];
            };

            default = self.packages.${system}.main;
          };

          devShells.default = pkgs.mkShell {
            buildInputs = [ self.packages.${system}.devEnv ];
            packages = with pkgs; [ just poetry pre-commit tailwindcss ];
          };

        }) // {
      nixosModules.puka = import ./nix/module.nix self;
      nixosModules.default = self.nixosModules.puka;
    };
}
