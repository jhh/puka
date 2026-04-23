# Puka

This project uses the [just](https://just.systems) command runner for development and [Nix](https://nixos.org) for deployment.

## Running Integration Tests

To run NixOS integration tests:

```sh
nix build .#checks.aarch64-darwin.puka-integration-tests -L
```

To run tests interactively:

```sh
nix build .#checks.aarch64-darwin.puka-integration-tests.driverInteractive
./result/bin/nixos-test-driver
```

See [NixOS manual](./result/bin/nixos-test-driver) for more information about running tests interactively.
