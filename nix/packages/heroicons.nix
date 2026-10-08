{
  fetchFromGitHub,
  lib,
  stdenvNoCC,
}:

stdenvNoCC.mkDerivation (finalAttrs: {
  pname = "heroicons";
  version = "2.2.0";

  src = fetchFromGitHub {
    owner = "tailwindlabs";
    repo = "heroicons";
    rev = "v${finalAttrs.version}";
    sha256 = "sha256-Jcxr1fSbmXO9bZKeg39Z/zVN0YJp17TX3LH5Us4lsZU=";
  };

  dontBuild = true;
  dontConfigure = true;

  installPhase = ''
    runHook preInstall
    mkdir -p $out/share/heroicons
    cp -r $src/optimized $out/share/heroicons/
    runHook postInstall
  '';

  meta = {
    description = "A set of free MIT-licensed high-quality SVG icons";
    homepage = "https://heroicons.com";
    license = lib.licenses.mit;
  };
})
