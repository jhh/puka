{
  perSystem.treefmt = {
    projectRootFile = "flake.nix";

    flakeCheck = true;

    programs = {
      mdformat.enable = true;
      mdformat.settings.number = true;
      nixfmt.enable = true;
      ruff-format.enable = true;
      yamlfmt.enable = true;
      just.enable = true;
      jsonfmt.enable = true;
    };

    settings.excludes = [
      "*.{age,gif,png,svg,env,envrc,gitignore,pickle}"
      ".idea/*"
      ".vscode/*"
      "puka/static/*"
      "puka/templates/*"
      ".python-version"
    ];
  };
}
