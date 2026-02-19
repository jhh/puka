# Puka — NixOS package derivation
#
# Built using nixpkgs' beamPackages.mixRelease.
#
# Key build-time considerations:
#
#   1. Heroicons is a git dep in mix.lock. fetchMixDeps fetches it via
#      `mix deps.get` (network is allowed in FODs). The mixRelease build
#      then links those fetched deps; no separate fetchgit needed.
#
#   2. Assets are vendored (no package.json / npm). The mix alias
#      `assets.deploy` runs esbuild + tailwindcss then phx.digest.
#      Both tools try to download platform binaries at runtime; we
#      satisfy them by symlinking the Nix-provided binaries into the
#      expected _build/ paths before the mix task runs.
#
#   3. Tailwind v4 is used — the nixpkgs `tailwindcss` package ships
#      the standalone CLI which is what the Elixir `tailwind` library
#      looks for.
#
# Usage (from project root):
#
#   nix build .#default       — build the release
#   ./result/bin/server       — run it (env vars required; see below)
#
# Required runtime environment variables:
#
#   SECRET_KEY_BASE   — 64-byte base64 secret (mix phx.gen.secret)
#   DATABASE_URL      — PostgreSQL connection URL
#   PHX_HOST          — public hostname
#
# Optional:
#
#   PORT              — HTTP port (default 4000)
#   POOL_SIZE         — DB pool size (default 10)
#   ECTO_IPV6         — set to "true" to enable IPv6 sockets
#   DNS_CLUSTER_QUERY — Erlang cluster DNS query

{ pkgs, ... }:

let
  # ---------------------------------------------------------------------------
  # BEAM toolchain — match the versions used in devshell.nix
  # ---------------------------------------------------------------------------
  beamPackages = pkgs.beam.packagesWith pkgs.beam.interpreters.erlang_28;
  elixir = beamPackages.elixir_1_19;

  # ---------------------------------------------------------------------------
  # Platform name translation: Nix system → esbuild/tailwindcss release name
  # ---------------------------------------------------------------------------
  translatedPlatform =
    {
      "aarch64-darwin" = "darwin-arm64";
      "aarch64-linux" = "linux-arm64";
      "armv7l-linux" = "linux-arm";
      "x86_64-darwin" = "darwin-x64";
      "x86_64-linux" = "linux-x64";
    }
    .${pkgs.stdenv.system};

  # ---------------------------------------------------------------------------
  # Dependency snapshot — all deps including the heroicons git dep.
  # fetchMixDeps runs `mix deps.get` in a fixed-output derivation where
  # network access is allowed, so git deps are fetched correctly.
  # ---------------------------------------------------------------------------
  mixFodDeps = beamPackages.fetchMixDeps {
    pname = "puka-mix-deps";
    version = "0.1.0";
    src = ../.;
    # Set to "" to get the correct hash on first run; Nix will print it.
    hash = "sha256-S5xvUyZ6tE/pb2f6qYdqiwVmpBud7t1wBm6e9xMx7fI=";
  };
in
beamPackages.mixRelease {
  pname = "puka";
  version = "0.1.0";
  src = ../.;

  inherit mixFodDeps;

  # BEAM / Elixir versions to use inside the build sandbox
  inherit elixir;
  erlang = pkgs.beam.interpreters.erlang_28;

  # -------------------------------------------------------------------------
  # Asset compilation
  #
  # Runs before `mix release` assembles the OTP release bundle.
  # All mix invocations pass --no-deps-check because the heroicons git dep
  # appears out-of-date to mix's lock checker in the offline sandbox.
  # -------------------------------------------------------------------------
  # Remove heroicons from mix.exs and mix.lock before the build.
  # heroicons is app:false, compile:false — it only provides SVG sources
  # for the Heroicons Tailwind plugin at asset-compile time.  The plugin
  # in assets/vendor/heroicons.js is already vendored, so heroicons does
  # not need to be present at all.  Removing it eliminates the git-dep
  # lock check which cannot succeed in the offline Nix sandbox.
  preBuild = ''
    # Strip the multi-line heroicons tuple from mix.exs deps list.
    # The entry spans lines starting with "{:heroicons" through "depth: 1},"
    ${pkgs.gnused}/bin/sed -i \
      '/{:heroicons/,/depth: 1},/d' mix.exs
    # Strip the heroicons entry from mix.lock (single line starting with "heroicons")
    ${pkgs.gnused}/bin/sed -i \
      '/"heroicons"/d' mix.lock
  '';

  preInstall = ''
    # -------------------------------------------------------------------
    # 1. Satisfy the Elixir `tailwind` library: it looks for a binary at
    #    _build/tailwind-<platform>
    # -------------------------------------------------------------------
    ln -sf ${pkgs.tailwindcss}/bin/tailwindcss \
      _build/tailwind-${translatedPlatform}

    # -------------------------------------------------------------------
    # 2. Satisfy the Elixir `esbuild` library: it looks for a binary at
    #    _build/esbuild-<platform>
    # -------------------------------------------------------------------
    ln -sf ${pkgs.esbuild}/bin/esbuild \
      _build/esbuild-${translatedPlatform}

    # -------------------------------------------------------------------
    # 3. Compile and digest assets
    # -------------------------------------------------------------------
    mix phx.digest.clean
    mix tailwind puka --minify
    mix esbuild puka --minify
    mix phx.digest

    # -------------------------------------------------------------------
    # 4. Generate the release helper scripts (bin/server, bin/migrate)
    # -------------------------------------------------------------------
    mix phx.gen.release
  '';

  # -------------------------------------------------------------------------
  # Pass-through metadata / downstream tests hook
  # -------------------------------------------------------------------------
  passthru = {
    # Expose the Elixir and Erlang versions for consumers / NixOS modules.
    inherit elixir;
    inherit (pkgs.beam.interpreters) erlang_28;
  };

  meta = {
    description = "Puka — personal bookmark manager (Phoenix LiveView)";
    homepage = "https://github.com/jhh/puka";
    license = pkgs.lib.licenses.mit; # adjust if/when a license is added
    platforms = pkgs.lib.platforms.linux ++ pkgs.lib.platforms.darwin;
    mainProgram = "puka";
  };
}
