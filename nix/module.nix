{
  pythonSets,
  workspace,
  packages,
}:
{
  config,
  lib,
  pkgs,
  ...
}:
let
  cfg = config.services.puka;
  inherit (pkgs) system;

  pythonSet = pythonSets.${system};

  inherit (lib.options) mkOption;
  inherit (lib.modules) mkIf;
in
{
  options.services.puka = {
    enable = mkOption {
      type = lib.types.bool;
      default = false;
      description = "Enable Puka service";
    };

    port = lib.mkOption {
      type = lib.types.port;
      description = "Server listen port";
      default = 8000;
    };

    settings-module = mkOption {
      type = lib.types.str;
      default = "puka.settings.production";
      description = "Django settings module for Puka";
    };

    venv = mkOption {
      type = lib.types.package;
      default = pythonSet.mkVirtualEnv "puka-env" workspace.deps.default;
      description = "Puka virtual environment package";
    };

    static-root = mkOption {
      type = lib.types.package;
      default = packages.${system}.static;
      description = "Puka static root package";
    };

    secrets = lib.mkOption {
      type = with lib.types; listOf path;
      description = ''
        A list of files containing the various secrets. Should be in the format
        expected by systemd's `EnvironmentFile` directory.
      '';
      default = [ ];
    };
  };

  config = mkIf cfg.enable {
    systemd.services.puka = {
      description = "Puka server";

      environment = {
        DJANGO_SETTINGS_MODULE = cfg.settings-module;
        DJANGO_STATIC_ROOT = cfg.static-root;
      };

      serviceConfig = {
        EnvironmentFile = cfg.secrets;
        ExecStartPre = "${cfg.venv}/bin/puka-manage migrate --no-input";
        ExecStart = ''
          ${cfg.venv}/bin/gunicorn --bind 127.0.0.1:${toString cfg.port} puka.wsgi:application
        '';
        Restart = "on-failure";

        User = "puka";
        DynamicUser = true;
        StateDirectory = "puka";
        RuntimeDirectory = "puka";

        BindReadOnlyPaths = [
          "${
            config.environment.etc."ssl/certs/ca-certificates.crt".source
          }:/etc/ssl/certs/ca-certificates.crt"
          builtins.storeDir
          "-/etc/resolv.conf"
          "-/etc/nsswitch.conf"
          "-/etc/hosts"
          "-/etc/localtime"
        ];

        RestrictAddressFamilies = "AF_UNIX AF_INET";
        CapabilityBoundingSet = "";
        SystemCallFilter = [
          "@system-service"
          "~@privileged @setuid @keyring"
        ];
      };

      wantedBy = [ "multi-user.target" ];
      after = [ "postgresql.service" ];
    };
  };
}
