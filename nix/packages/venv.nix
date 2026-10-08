{
  lib,
  postgresql,
  postgresqlTestHook,
  pythonSet,
  stdenvNoCC,
  workspace,
}:
let
  baseVenv = pythonSet.mkVirtualEnv "puka-env" workspace.deps.default;
  venv = pythonSet.mkVirtualEnv "puka-test-env" {
    puka = [ "test" ];
  };
  inherit (stdenvNoCC) mkDerivation;
in
baseVenv.overrideAttrs (old: {
  passthru = (old.passthru or { }) // {
    tests = (old.passthru.tests or { }) // {
      # pytests are not included in checks due to requiring postgres

      ty-check = mkDerivation {
        name = "puka-ty";
        inherit (pythonSet.puka) src;

        nativeBuildInputs = [ venv ];

        dontConfigure = true;
        dontInstall = true;
        buildPhase = ''
          runHook preBuild
          ty check  --output-format=concise --error-on-warning | tee $out 2>&1
          runHook postBuild
        '';
      };

      pytest = mkDerivation {
        name = "puka-pytest";
        inherit (pythonSet.puka) src;

        nativeBuildInputs = [ venv ];
        nativeCheckInputs = [
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

        meta.platforms = lib.platforms.linux;
      };
    };
  };
})
