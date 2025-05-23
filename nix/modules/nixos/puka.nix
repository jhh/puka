{ flake, ... }:
{
  config,
  lib,
  pkgs,
  ...
}:
let
  cfg = config.services.puka;
  inherit (pkgs) system;
  inherit (flake.packages.${system}) manage static venv;

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

    settingsModule = mkOption {
      type = lib.types.str;
      default = "puka.settings.production";
      description = "Django settings module for Puka";
    };

    venv = mkOption {
      type = lib.types.package;
      default = venv;
      description = "Puka virtual environment package";
    };

    staticRoot = mkOption {
      type = lib.types.package;
      default = static;
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

    taskWithin = mkOption {
      type = lib.types.str;
      default = "1d";
      description = "Notification threshold for upcoming tasks";
    };

    suppliesWithin = mkOption {
      type = lib.types.str;
      default = "2w";
      description = "Notification threshold for out-of-stock task supplies";
    };

  };

  config = mkIf cfg.enable {
    environment.systemPackages = [ manage ];

    systemd.services.puka = {
      description = "Puka server";

      environment = {
        DJANGO_SETTINGS_MODULE = cfg.settingsModule;
        DJANGO_STATIC_ROOT = cfg.staticRoot;
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

    systemd.services."puka-notify" = {
      environment = {
        DJANGO_SETTINGS_MODULE = cfg.settingsModule;
        DJANGO_STATIC_ROOT = cfg.staticRoot;
        PUKA_TASK_WITHIN = cfg.taskWithin;
        PUKA_SUPPLIES_WITHIN = cfg.suppliesWithin;
      };

      script = ''
        ${cfg.venv}/bin/puka-manage notify
      '';
      serviceConfig = {
        EnvironmentFile = cfg.secrets;
        Type = "oneshot";
        User = "puka";
      };
      startAt = "daily";
    };

    networking.firewall.allowedTCPPorts = [
      443
      80
    ];
  };
}
