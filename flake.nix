{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, utils }:
    let out = system:
      let pkgs = nixpkgs.legacyPackages."${system}";
      in
      {

        devShell = pkgs.mkShell {

          nativeBuildInputs = with pkgs; [
            postgresql
            yarn
            python3Packages.poetry
            nodejs-16_x
          ];

          buildInputs = pkgs.lib.optional pkgs.stdenv.isDarwin pkgs.openssl;
        };

        defaultPackage = with pkgs.poetry2nix; mkPoetryApplication {
          projectDir = ./.;
          preferWheels = true;
        };

        defaultApp = utils.lib.mkApp {
          drv = self.defaultPackage."${system}";
        };

      }; in with utils.lib; eachSystem defaultSystems out;

}
