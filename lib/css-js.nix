{ pkgs }:
pkgs.buildNpmPackage {
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
}
