{ pkgs }:
final: prev: {
  psycopg-c = prev.psycopg-c.overrideAttrs (old: {
    nativeBuildInputs =
      old.nativeBuildInputs or [ ]
      ++ (final.resolveBuildSystem {
        setuptools = [ ];
      });
    postPatch = ''
      substituteInPlace build_backend/psycopg_build_ext.py \
        --replace-fail 'pg_config = "pg_config"' 'pg_config = "${pkgs.postgresql.pg_config}/bin/pg_config"'
    '';
  });
}
