{
  pkgs,
  pythonSet,
  venv,
}:
let
  pukaCssJs = pkgs.buildNpmPackage {
    name = "django-static-deps";
    src = ../.;
    npmDepsHash = "sha256-5betlQyJXp0zB15wdGu4oF5NisajKuH/e54k2n5uSyk=";
    dontNpmBuild = true;

    buildPhase = ''
      runHook preBuild
      npx @tailwindcss/cli --minify --input=puka/static/puka/base.css --output=$out/puka/main.css
      npx esbuild --bundle --minify --outfile=$out/puka/main.js puka/static/puka/base.js
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
    ${venv}/bin/puka-manage collectstatic --no-input --ignore="base.*"
  '';

}
