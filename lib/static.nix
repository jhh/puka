{
  pkgs,
  pythonSet,
  workspace,
  venv,
}:
let
  pukaCssJs = pkgs.buildNpmPackage {
    name = "django-static-deps";
    src = ../.;
    npmDepsHash = "sha256-VSYvzgzPYj/mGQ8SvdZB+UtaqgyAjy1fPivk1ioUU6o=";
    dontNpmBuild = true;

    buildPhase = ''
      runHook preBuild
      npx tailwindcss -m -i puka/static/css/base.css -o $out/puka/static/css/main.css
      # node ./static-build.mjs
      runHook postBuild
    '';

    installPhase = ''
      runHook preInstall
      # mkdir -p $out/ui
      # mv upkeep/ui/static/ui/main.* $out/ui
      runHook postInstall
    '';
  };
  inherit (pkgs.stdenv) mkDerivation;
in
mkDerivation {
  pname = "puka-static";
  inherit (pythonSet.puka) version;
  nativeBuildInputs = [ venv ];

  dontUnpack = true;
  dontConfigure = true;
  dontBuild = true;

  installPhase = ''
    export DJANGO_SETTINGS_MODULE=puka.settings.production
    export DJANGO_STATICFILES_DIR="${pukaCssJs}"
    export SECRET_KEY=
    export STATIC_ROOT=$out
    mkdir -p $out
    ${venv}/bin/puka-manage collectstatic --no-input
  '';

}
