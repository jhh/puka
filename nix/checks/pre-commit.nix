{ inputs, system, ... }:
inputs.pre-commit-hooks.lib.${system}.run {
  src = ../../.;
  hooks = {
    nixfmt-rfc-style.enable = true;
    ruff.enable = true;
    ruff-format.enable = true;
    ruff-format.after = [ "ruff" ];
    trim-trailing-whitespace.enable = true;
    end-of-file-fixer.enable = true;
    check-yaml.enable = true;
    check-added-large-files.enable = true;
    pyupgrade.enable = true;
  };
}
