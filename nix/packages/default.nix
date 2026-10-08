{
  perSystem =
    {
      config,
      pkgs,
      pythonSet,
      workspace,
      ...
    }:
    {
      packages = {
        heroicons = pkgs.callPackage ./heroicons.nix { };

        manage = pkgs.callPackage ./manage.nix {
          inherit (config.packages) venv;
        };

        static = pkgs.callPackage ./static.nix {
          inherit (config.packages) heroicons venv;
          inherit pythonSet;
        };

        venv = pkgs.callPackage ./venv.nix {
          inherit pythonSet workspace;
        };
      };
    };
}
