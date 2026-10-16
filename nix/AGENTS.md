# Nix conventions

Nix code under `nix/`. Repo-wide setup, commands, and CI verification are
in the root `AGENTS.md`.

- `nix/` holds the devshell, checks, packages, and the NixOS module
  (`nix/modules/nixos/puka.nix`).
- `nix/checks/pre-commit.nix` configures the git-hooks flake-parts module;
  the pre-commit config is generated from it (a Nix-store symlink), so
  edit that file, not the yaml. Hooks rewrite code: ruff, pyupgrade
  `--py313-plus`, django-upgrade (target auto-detected from
  `pyproject.toml`), add-trailing-comma, djangofmt (then djade, then
  `djangofmt check`), nixfmt; files >25 KB are rejected.
- Format Nix files with `nixfmt`.
- NixOS integration tests (`nix/checks/tests.py`):
  `nix build .#checks.aarch64-darwin.puka-integration-tests -L`
