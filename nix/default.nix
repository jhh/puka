{ inputs, ... }:
let
  pukaLib = import ./lib { inherit inputs; };
in
{
  imports = [
    inputs.treefmt-nix.flakeModule
    inputs.pre-commit-hooks.flakeModule
    ./checks
    ./checks/pre-commit.nix
    ./devshell.nix
    ./formatter.nix
    ./modules
    ./packages
  ];

  systems = [
    "aarch64-darwin"
    "aarch64-linux"
    "x86_64-linux"
  ];

  flake.lib = pukaLib;

  perSystem =
    { pkgs, ... }:
    {
      _module.args = {
        pythonSet = pukaLib.pythonSets pkgs;
        inherit (pukaLib) workspace;
      };
    };
}
