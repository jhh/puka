{ inputs, pkgs, ... }:
inputs.treefmt-nix.lib.mkWrapper pkgs {
  projectRootFile = "flake.nix";

  programs.mdformat.enable = true;
  programs.mdformat.settings.number = true;

  programs.nixfmt.enable = true;
  programs.ruff-format.enable = true;
  programs.yamlfmt.enable = true;
  programs.just.enable = true;
  programs.jsonfmt.enable = true;
  programs.taplo.enable = true;

  settings = {
    global.excludes = [
      "*.{age,gif,png,svg,env,envrc,gitignore,tmTheme,sublime-syntax,theme,pickle,toml}"
      ".idea/*"
      "puka/static/*"
      "puka/templates/*"
      ".python-version"
    ];
  };
}
