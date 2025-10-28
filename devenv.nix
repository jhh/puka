{
  config,
  lib,
  pkgs,
  ...
}:

{
  env.DEBUG = true;
  env.DJANGO_DATABASE_URL = "postgres:///puka?pool=true";

  packages = with pkgs; [
    git
    just
    # nodejs
  ];

  languages.python = {
    enable = true;
    version = "3.13";
    uv.enable = true;
  };

  languages.javascript = {
    enable = true;
    npm.enable = true;
    npm.install.enable = true;
  };

  processes = lib.mkIf (!config.devenv.isTesting) {
    server.exec = "uv run puka/manage.py runserver";
  };

  services.postgres = {
    enable = true;
    initialDatabases = [ { name = "puka"; } ];
  };

  scripts = {

  };

  enterTest = ''
    export DJANGO_SETTINGS_MODULE=puka.settings.test
    uv run pytest tests
  '';

  git-hooks.hooks = {
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
    check-merge-conflicts.enable = true;
    check-symlinks.enable = true;
    pyupgrade.enable = true;
    pyupgrade.args = [ "--py313-plus" ];

    add-trailing-comma = {
      enable = true;
      name = "add-trailing-comma";
      description = "Automatically add trailing commas to calls and literals.";
      entry = "${pkgs.python313Packages.add-trailing-comma}/bin/add-trailing-comma";
      types = [ "python" ];
    };

    django-upgrade = {
      enable = true;
      name = "django-upgrade";
      description = "Automatically upgrade your Django project code.";
      entry = "${pkgs.django-upgrade}/bin/django-upgrade --target-version=5.2";
      types = [ "python" ];
    };
  };

}
