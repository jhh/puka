{
  flake,
  perSystem,
  pkgs,
}:
let
  pythonSet = flake.lib.pythonSets pkgs;
in
pkgs.mkShell {
  packages = with pkgs; [
    pythonSet.python
    just
    nil
    nix-output-monitor
    nixfmt-rfc-style
    nodejs
    postgresql.dev
    pre-commit
    perSystem.uv2nix.uv-bin
    watchman
  ];

  env = {
    UV_PYTHON_DOWNLOADS = "never";
  };

  shellHook = ''
    unset PYTHONPATH
  '';
}
