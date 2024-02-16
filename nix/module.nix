self: { config, lib, pkgs, ... }:
with lib;
let
  cfg = config.j3ff.puka;
in
{
  options.j3ff.puka = {
    enable = mkEnableOption "Enable the Puka service";
  };

  config = mkIf cfg.enable {
    systemd.services.puka = {
      description = "Puka Bookmarks";

      wantedBy = [ "multi-user.target" ];
      requires = [ "postgresql.service" ];
      after = [ "postgresql.service" ];

      environment = {
        DJANGO_SETTINGS_MODULE = "puka.settings.production";
      };

      preStart =
        let pkg = self.packages.${pkgs.system}.default;
        in
        ''
          ${pkg}/bin/manage.py migrate --no-input
          echo Copying static files to $STATE_DIRECTORY.
          ${pkg}/bin/manage.py collectstatic --no-input --clear --verbosity=0

        '';

      serviceConfig =
        let pkg = self.packages.${pkgs.system}.default.dependencyEnv;
        in
        {
          # agenix secret in github:jhh/nixos-configs
          EnvironmentFile = "/run/agenix/puka_secrets";
          ExecStart = "${pkg}/bin/uwsgi  --http-socket 127.0.0.1:8000 --master --processes 2 --disable-logging --module puka.wsgi";

          Type = "notify";
          NotifyAccess = "all";
          KillSignal = "SIGQUIT";
          DynamicUser = true;
          StateDirectory = "puka";
          NoNewPrivileges = true;
          ProtectSystem = "strict";
        };
    };

    services.postgresql = {
      ensureDatabases = [ "puka" ];
      ensureUsers = [
        {
          name = "puka";
          ensureDBOwnership = true;
        }
      ];
      authentication = ''
        local puka puka md5
      '';
    };

    services.nginx.virtualHosts."puka.j3ff.io" = {
      # security.acme is configured for eris globally in nginx.nix
      forceSSL = true;
      enableACME = true;
      acmeRoot = null;

      locations = {
        "/" = {
          proxyPass = "http://127.0.0.1:8000";
        };
      };
    };
  };
}