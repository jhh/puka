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
          pkgs = nixpkgs.legacyPackages.${system};
          poetry2nixPkg = poetry2nix.lib.mkPoetry2Nix { inherit pkgs; };
          inherit (poetry2nixPkg) mkPoetryEnv mkPoetryApplication;

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
              postInstall = ''
                mkdir -p $out/bin/
                cp -vf manage.py $out/bin/
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
            packages = with pkgs; [ just nodejs poetry pre-commit ];
          };

        }) // {
      nixosModules.puka = import ./nix/module.nix self;
      nixosModules.default = self.nixosModules.puka;
    };
}
