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

      ty-check = mkDerivation {
        name = "puka-ty";
        inherit (pythonSet.puka) src;

        nativeBuildInputs = [ venv ];

        dontConfigure = true;
        dontInstall = true;
        buildPhase = ''
          runHook preBuild
          ty check  --output-format=github --exit-zero | tee $out 2>&1
          runHook postBuild
        '';
      };

      pytest = mkDerivation {
        name = "puka-pytest";
        inherit (pythonSet.puka) src;

        nativeBuildInputs = [ venv ];
        nativeCheckInputs = with pkgs; [
          postgresql
          postgresqlTestHook
        ];
        dontConfigure = true;
        dontBuild = true;
        dontInstall = true;

        doCheck = true;
        postgresqlTestUserOptions = "LOGIN SUPERUSER";
        checkPhase = ''
          runHook preCheck
          mkdir -p $out
          export DJANGO_SETTINGS_MODULE=puka.settings.test
          pytest tests --junit-xml=$out/junit.xml
          runHook postCheck
        '';

        meta.platforms = pkgs.lib.platforms.linux;
      };
    };
}
