{ pkgs }:
pkgs.mkShell {
  packages = with pkgs; [
    beam28Packages.elixir_1_19
    nil
  ];

  env = { };

  shellHook = ''

  '';
}
