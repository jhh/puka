{
  flake,
  pkgs,
  perSystem,
  ...
}:
let
  pythonSet = flake.lib.pythonSets pkgs;
  workspace = flake.lib.workspace;
in
pythonSet.mkVirtualEnv "puka-env" workspace.deps.default
// {
  passthru.tests =
    let
      venv = pythonSet.mkVirtualEnv "puka-test-env" {
        puka = [ "test" ];
      };
      inherit (pkgs.stdenvNoCC) mkDerivation;
    in
    {
      # pytests are not included in checks due to requiring postgres

      mypy = mkDerivation {
        name = "puka-mypy";
        inherit (pythonSet.puka) src;

        nativeBuildInputs = [ venv ];

        dontConfigure = true;
        dontInstall = true;
        buildPhase = ''
          runHook preBuild
          export MYPYPATH=apps
          mypy . --junit-xml $out/junit.xml
          runHook postBuild
        '';
      };
    };
}
