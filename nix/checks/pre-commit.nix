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
      check-added-large-files.args = [ "--maxkb=25" ];
      check-case-conflicts.enable = true;
      check-json.enable = true;
      check-toml.enable = true;
      pyupgrade.enable = true;
      pyupgrade.args = [ "--py312-plus" ];
      add-trailing-comma = {
        enable = true;
        name = "add-trailing-comma";
        description = "Automatically add trailing commas to calls and literals.";
        entry = "${venv}/bin/add-trailing-comma";
        types = [ "python" ];
      };
      djade = {
        enable = true;
        name = "djade";
        description = "A Django template formatter.";
        entry = "${venv}/bin/djade";
        types = [ "html" ];
      };
      django-upgrade = {
        enable = true;
        name = "django-upgrade";
        description = "Automatically upgrade your Django project code.";
        entry = "${venv}/bin/django-upgrade --target-version=5.2";
        types = [ "python" ];
      };
    };
}
