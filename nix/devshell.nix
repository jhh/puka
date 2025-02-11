{
  flake,
  inputs,
  perSystem,
  pkgs,
  system,
}:
let
  pythonSet = flake.lib.pythonSets pkgs;
in
pkgs.mkShell {
  packages =
    with pkgs;
    [
      pythonSet.python
      just
      nil
      nix-output-monitor
      nixfmt-rfc-style
      nodejs
      postgresql.dev
      perSystem.uv2nix.uv-bin
      watchman
    ]
    ++ inputs.self.checks.${system}.pre-commit.enabledPackages;

  env = {
    UV_PYTHON_DOWNLOADS = "never";
  };

  shellHook = ''
    unset PYTHONPATH
    ${inputs.self.checks.${system}.pre-commit.shellHook}
  '';
}
