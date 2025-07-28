{
  flake,
  inputs,
  perSystem,
  pkgs,
  system,
}:
let
  pythonSet = flake.lib.pythonSets pkgs;
  inherit (inputs.self.checks.${system}) pre-commit;
in
pkgs.mkShell {
  packages =
    with pkgs;
    [
      pythonSet.python
      just
      mailpit
      nil
      nix-output-monitor
      nixfmt-rfc-style
      nodejs
      postgresql.pg_config
      perSystem.uv2nix.uv-bin
      watchman
      flake.packages.${system}.pg-dev
    ]
    ++ pre-commit.enabledPackages;

  env = {
    UV_PYTHON_DOWNLOADS = "never";
    PGPORT = 5432;
  };

  shellHook = ''
    unset PYTHONPATH
    export PGHOST=$(git rev-parse --show-toplevel)/.db
    export DJANGO_DATABASE_URL=postgres://$(echo $PGHOST | sed -e 's/\//%2f/g')/puka
    ${pre-commit.shellHook}
  '';
}
