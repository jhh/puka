{
  flake,
  pkgs,
  perSystem,
  ...
}:
let
  pythonSet = flake.lib.pythonSets pkgs;
  inherit (perSystem.self) venv;

  baseCss = "puka/static/puka/base.css";
  templates = "${pythonSet.python.sitePackages}/crispy_tailwind";

  pukaCssJs = pkgs.buildNpmPackage {
    name = "django-static-deps";
    src = ../../.;
    npmDepsHash = "sha256-Lcv3Dq2Tai+2XGAmJ+iozA2YO+pT/KENQr1XlIIltXs=";
    dontNpmBuild = true;

    patchPhase = ''
      runHook prePatch
      substituteInPlace ${baseCss} --replace-fail "../../../.venv/${templates}" "${venv}/${templates}"
      runHook postPatch
    '';

    buildPhase = ''
      runHook preBuild
      npx @tailwindcss/cli --minify --input=${baseCss} --output=$out/puka/main.css
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
    ${venv}/bin/puka-manage collectstatic --no-input --ignore="puka/base.*"
  '';

}
