# Plan: idiomatic flake-parts

## Goal and scope

The Blueprint to flake-parts migration (`docs/flake-parts-migration.md`)
is done. It ported outputs one-to-one, so `nix/flake-module.nix` uses
flake-parts as a thin wrapper around `callPackage`. This plan refactors the
flake to use the flake-parts module system idiomatically:

1. Use the treefmt-nix and git-hooks.nix flake-parts modules.
2. Wire the NixOS module through `importApply` and `withSystem`.
3. Drop the unused Blueprint-style `modules.nixos.puka` output.
4. Pass `pythonSet` and `workspace` as module arguments, not via `self.lib`.
5. Split `nix/flake-module.nix` into one module per concern.
6. Apply small cleanups.

Do not change package implementations, dependency revisions or
`flake.lock` inputs.

## Constraints

- Run every command inside the Nix devshell.
- Use Jujutsu (`jj` skill) for VCS work; never raw `git`.
- Run `jj st` immediately before `nix build`, `nix flake check` and
  `pre-commit run`, so the colocated Git tree includes new files.
- Look up treefmt-nix, git-hooks.nix and flake-parts APIs with Context7
  before implementing; option names below may have changed.
- Keep Markdown lines at 80 characters or fewer; lint with
  `markdownlint-cli2`.
- Format Nix with `nixfmt`.

## Intended output changes

These are the only public output changes. Everything else must stay the
same.

| Before                         | After                                 |
| ------------------------------ | ------------------------------------- |
| `packages.<sys>.formatter`     | removed (`formatter.<sys>` remains)   |
| `checks.<sys>.pkgs-formatter`  | replaced by `checks.<sys>.treefmt`    |
| `modules.nixos.puka`           | removed (`nixosModules.puka` remains) |

`modules.nixos.puka` has no known consumers. The production host
(`cosmos/modules/hosts/eris/services/puka.nix`) imports
`inputs.puka.nixosModules.puka`, and nothing in this repository reads
`modules.nixos.puka`. Do not import `inputs.flake-parts.flakeModules.modules`.

Kept unchanged: `lib`, `nixosModules.puka`, `packages.<sys>.{heroicons,
manage,static,venv}`, `devShells.<sys>.default`, and the checks
`pre-commit`, `puka-integration-tests`, `pkgs-heroicons`, `pkgs-manage`,
`pkgs-static`, `pkgs-venv`, `pkgs-venv-ty-check`, `pkgs-venv-pytest`
(Linux only) and `devshell-default`.

## Step 1: baseline

```sh
jj st
nix flake show --all-systems --json > /tmp/flake-before.json
nix flake check -L --keep-going
```

Save the output tree for comparison in Step 9. Start a new change with
`jj new` and describe it.

## Step 2: target layout

```text
flake.nix                      imports ./nix
nix/default.nix                systems, imports, perSystem module args
nix/lib/default.nix            unchanged (public flake.lib)
nix/packages/default.nix       perSystem.packages
nix/devshell.nix               perSystem.devShells.default
nix/formatter.nix              perSystem.treefmt
nix/checks/default.nix         perSystem.checks (builds, tests)
nix/checks/pre-commit.nix      perSystem.pre-commit
nix/modules/default.nix        flake.nixosModules
nix/modules/nixos/puka.nix     NixOS module (importApply)
```

Delete `nix/flake-module.nix` once everything has moved. Keep
`nix/checks/puka-integration-tests.nix`, `nix/checks/tests.py`,
`nix/packages/*.nix` and `nix/lib/overrides/*` as they are.

In `flake.nix`, replace `./nix/flake-module.nix` with `./nix`.

## Step 3: `nix/default.nix` and module arguments

Create `nix/default.nix`:

```nix
{ inputs, ... }:
let
  pukaLib = import ./lib { inherit inputs; };
in
{
  imports = [
    inputs.treefmt-nix.flakeModule
    inputs.pre-commit-hooks.flakeModule
    ./checks
    ./checks/pre-commit.nix
    ./devshell.nix
    ./formatter.nix
    ./modules
    ./packages
  ];

  systems = [
    "aarch64-darwin"
    "aarch64-linux"
    "x86_64-darwin"
    "x86_64-linux"
  ];

  flake.lib = pukaLib;

  perSystem =
    { pkgs, ... }:
    {
      _module.args = {
        pythonSet = pukaLib.pythonSets pkgs;
        inherit (pukaLib) workspace;
      };
    };
}
```

Every `perSystem` module can then take `{ pythonSet, workspace, ... }`.
No `perSystem` code may read `self.lib` after this step.

## Step 4: packages

Create `nix/packages/default.nix`:

```nix
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
        venv = pkgs.callPackage ./venv.nix { inherit pythonSet workspace; };
      };
    };
}
```

Do not add `formatter` to `packages`.

## Step 5: formatter (treefmt flake module)

Rewrite `nix/formatter.nix` as a flake-parts module. Move the existing
`mkWrapper` settings verbatim under `perSystem.treefmt`:

```nix
{
  perSystem.treefmt = {
    projectRootFile = "flake.nix";
    programs = {
      mdformat.enable = true;
      mdformat.settings.number = true;
      nixfmt.enable = true;
      ruff-format.enable = true;
      yamlfmt.enable = true;
      just.enable = true;
      jsonfmt.enable = true;
    };
    settings.global.excludes = [
      # copy the existing list unchanged
    ];
  };
}
```

The module sets `formatter.<sys>` and adds `checks.<sys>.treefmt`. Run
`nix fmt` and inspect the diff:

- If it is small and correct, keep it in this change and leave the check
  enabled.
- If it is large or conflicts with `markdownlint-cli2` (80-column
  Markdown), set `treefmt.flakeCheck = false;` and note the reason in the
  change description. Do not commit large unrelated reformatting.

## Step 6: pre-commit (git-hooks flake module)

Rewrite `nix/checks/pre-commit.nix` as a flake-parts module:

```nix
{
  perSystem =
    { pythonSet, ... }:
    let
      venv = pythonSet.mkVirtualEnv "pre-commit-env" {
        puka = [ "pre-commit" ];
      };
    in
    {
      pre-commit.settings.hooks = {
        # copy every existing hook unchanged, including `after`, `args`
        # and the `${venv}/bin/...` entries
      };
    };
}
```

- Drop `src = ../../.`; the module defaults to the flake source.
- Drop the `inputs`, `system` and `pythonSet` function arguments and the
  `inputs.pre-commit-hooks.lib.${system}.run` call.
- The module provides `checks.<sys>.pre-commit`; do not define it again.

## Step 7: devshell and checks

### `nix/devshell.nix`

Wrap the existing file in a module. Keep the `pg-*` scripts, `env` and
`shellHook` content unchanged.

```nix
{
  perSystem =
    {
      config,
      inputs',
      pkgs,
      pythonSet,
      ...
    }:
    {
      devShells.default = pkgs.mkShell {
        packages = [
          # existing packages; take uv from inputs'.uv2nix.packages.uv-bin
        ]
        ++ config.pre-commit.settings.enabledPackages;
        env = {
          HEROICONS_DIR = "${config.packages.heroicons}/share/heroicons/optimized/";
          # remaining env unchanged
        };
        shellHook = ''
          # existing hook body unchanged
          ${config.pre-commit.installationScript}
        '';
      };
    };
}
```

`config.pre-commit.installationScript` replaces the old
`pre-commit.shellHook`. Check with Context7 that both option names are
current.

### `nix/checks/default.nix`

```nix
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
          puka-integration-tests =
            pkgs.callPackage ./puka-integration-tests.nix {
              pukaModule = self.nixosModules.puka;
            };
          pkgs-venv-ty-check = config.packages.venv.passthru.tests.ty-check;
          devshell-default = config.devShells.default;
        }
        // lib.optionalAttrs pkgs.stdenv.hostPlatform.isLinux {
          pkgs-venv-pytest = config.packages.venv.passthru.tests.pytest;
        };
    };
}
```

The generated `pkgs-*` entries reproduce `pkgs-heroicons`, `pkgs-manage`,
`pkgs-static` and `pkgs-venv`. Since `packages.formatter` is gone, there is
no `pkgs-formatter`.

## Step 8: NixOS module via `importApply`

Create `nix/modules/default.nix`:

```nix
{ flake-parts-lib, withSystem, ... }:
{
  flake.nixosModules.puka = flake-parts-lib.importApply ./nixos/puka.nix {
    inherit withSystem;
  };
}
```

Change the header of `nix/modules/nixos/puka.nix`:

```nix
{ withSystem }:
{
  config,
  lib,
  pkgs,
  ...
}:
let
  cfg = config.services.puka;
  inherit (withSystem pkgs.stdenv.hostPlatform.system ({ config, ... }: config.packages))
    manage
    static
    venv
    ;
  # rest unchanged
```

Remove the `flake` argument and the `inherit (pkgs.stdenv.hostPlatform)
system` line.

## Step 9: verify

```sh
nixfmt nix flake.nix
jj st
nix flake show --all-systems --json > /tmp/flake-after.json
```

Compare `/tmp/flake-before.json` with `/tmp/flake-after.json`. The only
differences must be the ones in "Intended output changes".

```sh
jj st
nix flake check -L --keep-going
nix build .#checks.aarch64-darwin.puka-integration-tests -L
nix develop -c pre-commit run --all-files
nix develop -c just test
nix fmt
```

- `.pre-commit-config.yaml` must still be generated in the devshell.
- `nix flake check` must not warn about an unknown `modules` output.
- `grep -rn 'self.lib\|lib.${system}.run\|mkWrapper' nix` must find
  nothing.

## Step 10: documentation

- `AGENTS.md`: the pre-commit config is generated from
  `nix/checks/pre-commit.nix` (unchanged path, now a module). Update any
  wording that implies a standalone `run` call.
- `docs/flake-parts-migration.md`: add a short note pointing to this
  document.
- Lint changed Markdown with `markdownlint-cli2`.

## Acceptance checklist

- [ ] `nix/flake-module.nix` is deleted; `flake.nix` imports `./nix`.
- [ ] treefmt and pre-commit use their flake-parts modules.
- [ ] `packages.<sys>.formatter` and `checks.<sys>.pkgs-formatter` are
      gone; `formatter.<sys>` and `checks.<sys>.treefmt` exist.
- [ ] The NixOS module uses `importApply` and `withSystem`.
- [ ] `modules.nixos.puka` is gone; `nixosModules.puka` remains.
- [ ] No `perSystem` code reads `self.lib`.
- [ ] All other outputs match the baseline.
- [ ] `nix flake check`, the integration test, pre-commit and `just test`
      pass.
