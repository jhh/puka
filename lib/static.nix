{
  pkgs,
  pythonSet,
  venv,
}:
let
  pukaCssJs = pkgs.buildNpmPackage {
    name = "django-static-deps";
    src = ../.;
    npmDepsHash = "sha256-UKwbimfQT6tIbu+2oHi8WdICSE/b7kh9fL+hT7rTbEM=";
    dontNpmBuild = true;

    buildPhase = ''
      runHook preBuild
      npx tailwindcss --minify -i puka/static/css/base.css -o $out/css/main.css
      npx esbuild --bundle --minify --outfile=$out/js/main.js puka/static/js/base.js
      runHook postBuild
    '';

    installPhase = ''
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
    export DJANGO_STATIC_ROOT=$out
    mkdir -p $out
    ${venv}/bin/puka-manage collectstatic --no-input
  '';

}
