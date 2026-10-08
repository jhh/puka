# Plan: refactor nix packages to idiomatic nixpkgs style

## Goal and scope

Refactor the package definitions in `nix/packages/` so that each
function declares the individual nixpkgs dependencies it uses
(`lib`, `stdenv`, `fetchFromGitHub`, ...) instead of receiving a
`pkgs` set. The functions stay instantiated with `pkgs.callPackage`
in `nix/flake-module.nix`, which supplies the declared arguments
from nixpkgs.

Project-specific inputs (`pythonSet`, `workspace`, `venv`,
`heroicons`) remain explicit `callPackage` overrides.

Preserve package behavior, versions, hashes, output names and tests.
This document is a plan; the refactor has not been implemented.

## Constraints

- Run every command inside the Nix devshell, including lint and
  verification.
- Use Jujutsu for VCS work, not raw Git commands.
- Do not change dependency versions or hashes.
- Do not touch `nix/checks/`, `nix/devshell.nix` or
  `nix/formatter.nix`; this refactor covers `nix/packages/` only.
- Keep `pythonSet` and `workspace` as project-specific arguments.
- Run `jj st` immediately before Nix builds, flake checks and
  pre-commit so the colocated Git tree includes new and edited files.

## Current state

All four files take `pkgs` and reach into it:

- `heroicons.nix`: `pkgs` → `stdenvNoCC`, `fetchFromGitHub`, `lib`.
- `manage.nix`: `pkgs`, `venv` → `writeShellApplication`.
- `static.nix`: `heroicons`, `pkgs`, `pythonSet`, `venv` →
  `buildNpmPackage`, `stdenv`.
- `venv.nix`: `pkgs`, `pythonSet`, `workspace` → `stdenvNoCC`,
  `postgresql`, `postgresqlTestHook`, `lib`.

`venv.nix` also attaches its tests with a raw attrset merge
(`mkVirtualEnv ... // { passthru.tests = ...; }`), which replaces
any passthru the virtualenv defines.

## Target argument surface

- `heroicons.nix`: `fetchFromGitHub`, `lib`, `stdenvNoCC`.
- `manage.nix`: `venv`, `writeShellApplication`.
- `static.nix`: `buildNpmPackage`, `heroicons`, `pythonSet`,
  `stdenv`, `venv`.
- `venv.nix`: `lib`, `postgresql`, `postgresqlTestHook`,
  `pythonSet`, `stdenvNoCC`, `workspace`.

`callPackage` auto-supplies arguments that exist in the pkgs set
(`lib`, `stdenv`, `stdenvNoCC`, `fetchFromGitHub`,
`writeShellApplication`, `buildNpmPackage`, `postgresql`,
`postgresqlTestHook`). `venv`, `heroicons`, `pythonSet` and
`workspace` remain explicit overrides in `nix/flake-module.nix`.

Keep `heroicons` explicit so `callPackage` cannot silently
substitute a same-named nixpkgs package if one appears.

## Step 1: heroicons.nix

```nix
{
  fetchFromGitHub,
  lib,
  stdenvNoCC,
}:
let
  version = "2.2.0";
in
stdenvNoCC.mkDerivation {
  pname = "heroicons";
  inherit version;

  src = fetchFromGitHub {
    owner = "tailwindlabs";
    repo = "heroicons";
    rev = "v${version}";
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
}
```

Replace `with pkgs.lib;` with explicit `lib.` references. This
derivation is source-independent, so its `drvPath` must stay
identical to the pre-refactor value.

## Step 2: manage.nix

```nix
{ venv, writeShellApplication }:
writeShellApplication {
  name = "puka-manage";
  text = ''
    # Existing script text unchanged.
  '';
}
```

Replace `pkgs.writeShellApplication` with `writeShellApplication`
and drop the `pkgs` argument. The script text is untouched.

## Step 3: static.nix

```nix
{
  buildNpmPackage,
  heroicons,
  pythonSet,
  stdenv,
  venv,
}:
let
  baseCss = "puka/static/puka/base.css";

  pukaCssJs = buildNpmPackage {
    # Existing attributes unchanged.
  };
  inherit (stdenv) mkDerivation;
in
mkDerivation {
  # Existing attributes unchanged.
}
```

Replace `pkgs.buildNpmPackage` with `buildNpmPackage` and
`inherit (pkgs.stdenv) mkDerivation` with `inherit (stdenv)`.
`pythonSet.puka.version`, `venv` and `heroicons` keep their current
uses.

## Step 4: venv.nix

New arguments and an `overrideAttrs` passthru:

```nix
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
      # Existing ty-check and pytest derivations unchanged.
    };
  };
})
```

- `overrideAttrs` is confirmed available on the virtualenv
  (`builtins.typeOf` is `lambda`).
- `nativeCheckInputs` becomes `[ postgresql postgresqlTestHook ]`
  instead of `with pkgs; [ ... ]`.
- `meta.platforms = pkgs.lib.platforms.linux` becomes
  `meta.platforms = lib.platforms.linux`.
- Test names, commands and platform restrictions stay unchanged.

## Step 5: flake-module.nix

No wiring changes are expected. The explicit overrides continue to
supply project-specific arguments while `callPackage` fills in the
new nixpkgs-level arguments:

```nix
manage = pkgs.callPackage ./packages/manage.nix {
  venv = config.packages.venv;
};

static = pkgs.callPackage ./packages/static.nix {
  heroicons = config.packages.heroicons;
  inherit pythonSet;
  venv = config.packages.venv;
};

venv = pkgs.callPackage ./packages/venv.nix {
  inherit pythonSet workspace;
};
```

## Step 6: verification

1. Format only the changed files: `nixfmt nix/packages/*.nix`.
2. `jj st`, then confirm output names:
   - `nix eval --json .#packages.aarch64-darwin --apply builtins.attrNames`
   - `nix eval --json .#checks.aarch64-darwin --apply builtins.attrNames`
   - `nix eval --json .#checks.x86_64-linux --apply builtins.attrNames`
3. Confirm the `heroicons` `drvPath` is unchanged.
4. Build without result symlinks:
   - `nix build --no-link .#venv .#static .#heroicons`
   - `nix build --no-link .#checks.aarch64-darwin.pkgs-venv-ty-check`
5. `jj st`, then `nix flake check -L --keep-going`.
6. Verify the Linux-only pytest check on the Linux builder:
   `nix build --no-link .#checks.aarch64-linux.pkgs-venv-pytest -L`
7. `jj st`, then `pre-commit run --all-files`.

Source-dependent `drvPath`s change because the repository source
changes; output names and behavior must not.

Acceptance: no `pkgs` argument or `pkgs.` reference remains under
`nix/packages/`; all four packages still instantiate through
`pkgs.callPackage`; both virtualenv tests stay reachable; builds and
checks pass.

## Keep separate from this refactor

- Converting `nix/devshell.nix` and `nix/checks/` to the same style;
  they take `pkgs` today and are left for a follow-up.
- Adopting a package-directory importer or overlay.
- Changing dependency versions, hashes or the uv2nix integration.

## Completion checklist

- [ ] `nix/packages/*.nix` declare individual nixpkgs dependencies.
- [ ] No `pkgs` argument remains in `nix/packages/`.
- [ ] `venv` attaches tests with `overrideAttrs`, preserving any
  existing passthru.
- [ ] Output names are unchanged.
- [ ] `nix flake check -L --keep-going` passes.
- [ ] No unrelated files or dependency revisions change.

## References

- [callPackage][callpkg]
- [Package parameters (by-name)][by-name]
- [Passthru attributes][passthru]
- [Overriding packages][override]

[by-name]: https://github.com/NixOS/nixpkgs/blob/master/pkgs/by-name/README.md
[callpkg]: https://github.com/NixOS/nixpkgs/blob/master/lib/customisation.nix
[override]: https://nixos.org/manual/nixpkgs/stable/#sec-pkg-override
[passthru]: https://nixos.org/manual/nixpkgs/stable/#chap-passthru
