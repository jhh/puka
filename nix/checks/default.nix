{ self, ... }:
{
  perSystem =
    {
      config,
      lib,
      pkgs,
      ...
    }:
    {
      checks =
        lib.mapAttrs' (name: lib.nameValuePair "pkgs-${name}") config.packages
        // {
          puka-integration-tests = pkgs.callPackage ./puka-integration-tests.nix {
            pukaModule = self.nixosModules.puka;
          };

          # Preserve passthru-test discovery.
          pkgs-venv-ty-check = config.packages.venv.passthru.tests.ty-check;

          devshell-default = config.devShells.default;
        }
        // lib.optionalAttrs pkgs.stdenv.hostPlatform.isLinux {
          pkgs-venv-pytest = config.packages.venv.passthru.tests.pytest;
        };
    };
}
