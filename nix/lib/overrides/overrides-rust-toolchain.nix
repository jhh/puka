# djade and djangofmt wheels both ship a stray site-packages/rust-toolchain.toml,
# which collides when they're installed into the same virtualenv. Drop it.
_:
let
  dropRustToolchain = old: {
    postInstall = (old.postInstall or "") + ''
      rm -f $out/lib/python*/site-packages/rust-toolchain.toml
    '';
  };
in
_final: prev: {
  djade = prev.djade.overrideAttrs dropRustToolchain;
  djangofmt = prev.djangofmt.overrideAttrs dropRustToolchain;
}
