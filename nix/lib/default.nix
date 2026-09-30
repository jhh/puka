{ inputs, ... }:
let
  workspace = inputs.uv2nix.lib.workspace.loadWorkspace { workspaceRoot = ../../.; };

  overlay = workspace.mkPyprojectOverlay {
    sourcePreference = "wheel";
  };

  pythonSets =
    pkgs:
    let
      baseSet = pkgs.callPackage inputs.pyproject-nix.build.packages {
        python = pkgs.python313;
      };

      psycopgOverrides = import ./overrides/overrides-psycopg.nix { inherit pkgs; };
      rustToolchainOverrides = import ./overrides/overrides-rust-toolchain.nix { };
    in
    baseSet.overrideScope (
      inputs.nixpkgs.lib.composeManyExtensions [
        inputs.pyproject-build-systems.overlays.default
        overlay
        psycopgOverrides
        rustToolchainOverrides
      ]
    );
in
{

  inherit
    overlay
    pythonSets
    workspace
    ;
}
