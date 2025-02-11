{
  flake,
  inputs,
  pkgs,
  system,
  ...
}:
inputs.pre-commit-hooks.lib.${system}.run {
  src = ../../.;
  hooks =
    let
      pythonSet = flake.lib.pythonSets pkgs;
      venv = pythonSet.mkVirtualEnv "pre-commit-env" {
        puka = [ "pre-commit" ];
      };
    in
    {
      nixfmt-rfc-style.enable = true;
      ruff.enable = true;
      ruff-format.enable = true;
      ruff-format.after = [ "ruff" ];
      trim-trailing-whitespace.enable = true;
      end-of-file-fixer.enable = true;
      check-yaml.enable = true;
      check-added-large-files.enable = true;
      pyupgrade.enable = true;
      djade = {
        enable = true;
        name = "djade";
        description = "A Django template formatter.";
        entry = "${venv}/bin/djade";
        types = [ "html" ];
      };
    };
}
