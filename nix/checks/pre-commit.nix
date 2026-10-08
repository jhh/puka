{
  inputs,
  pkgs,
  pythonSet,
  system,
}:
inputs.pre-commit-hooks.lib.${system}.run {
  src = ../../.;
  hooks =
    let
      venv = pythonSet.mkVirtualEnv "pre-commit-env" {
        puka = [ "pre-commit" ];
      };
    in
    {
      nixfmt.enable = true;
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
      check-merge-conflicts.enable = true;
      check-symlinks.enable = true;
      pyupgrade.enable = true;
      pyupgrade.args = [ "--py312-plus" ];
      add-trailing-comma = {
        enable = true;
        name = "add-trailing-comma";
        description = "Automatically add trailing commas to calls and literals.";
        entry = "${venv}/bin/add-trailing-comma";
        types = [ "python" ];
      };
      djangofmt = {
        enable = true;
        name = "djangofmt";
        description = "A fast, HTML-aware Django template formatter.";
        entry = "${venv}/bin/djangofmt";
        types = [ "html" ];
      };
      djangofmt-check = {
        enable = true;
        name = "djangofmt-check";
        description = "Lint Django templates with djangofmt.";
        entry = "${venv}/bin/djangofmt check";
        types = [ "html" ];
        after = [ "djade" ];
      };
      djade = {
        after = [ "djangofmt" ];
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
