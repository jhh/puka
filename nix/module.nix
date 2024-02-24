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
        STATIC_ROOT = self.packages.${pkgs.system}.static;
      };

      preStart =
        let pkg = self.packages.${pkgs.system}.default;
        in
        ''
          ${pkg}/bin/manage.py migrate --no-input
        '';

      serviceConfig =
        let pkg = self.packages.${pkgs.system}.default.dependencyEnv;
        in
        {
          # agenix secret in github:jhh/nixos-configs
          EnvironmentFile = "/run/agenix/puka_secrets";
          ExecStart = "${pkg}/bin/gunicorn  --workers=2 --bind 127.0.0.1:8000 puka.wsgi";

          Type = "notify";
          NotifyAccess = "all";
          KillSignal = "SIGQUIT";
          DynamicUser = true;
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
    };

    systemd.services.postgresql.postStart = ''
      $PSQL -d puka -tA << END_INPUT
        ALTER ROLE puka SET client_encoding TO 'utf8';
        ALTER ROLE puka SET default_transaction_isolation TO 'read committed';
        ALTER ROLE puka SET timezone TO 'UTC';
      END_INPUT
    '';

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
