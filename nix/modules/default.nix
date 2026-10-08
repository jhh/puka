{ flake-parts-lib, withSystem, ... }:
{
  flake.nixosModules.puka = flake-parts-lib.importApply ./nixos/puka.nix {
    inherit withSystem;
  };
}
