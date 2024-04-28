{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    poetry2nix = {
      url = "github:SnejUgal/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; })
          mkPoetryApplication;

        api = mkPoetryApplication {
          projectDir = self;
          groups = [ "api" ];
          checkGroups = [ ];
        };

        uiEnv = (mkPoetryApplication {
          projectDir = self;
          groups = [ "ui" ];
          preferWheels = true;
        }).dependencyEnv;
        ui = pkgs.writeShellApplication {
          name = "nix-store-explorer-ui";
          runtimeInputs = [ uiEnv ];
          text = ''
            streamlit run ${uiEnv}/lib/python3.11/site-packages/src/frontend.py
          '';
        };

        ci-bandit = pkgs.writeShellApplication {
          name = "ci--bandit";
          runtimeInputs = [
            # cannot build `bandit` from source via `poetry2nix`, so use
            # the nixpkgs version
            pkgs.python311Packages.bandit
          ];
          text = "bandit -r src";
        };

        ci-ruff = pkgs.writeShellApplication {
          name = "ci-ruff";
          runtimeInputs = [ pkgs.ruff ];
          text = ''
            set -x
            ruff format --check
            ruff check
          '';
        };

        ci-pyright = pkgs.writeShellApplication {
          name = "ci-pyright";
          runtimeInputs = with pkgs; [
            poetry
            nodePackages.pyright
          ];
          text = ''
            set -x
            poetry install
            poetry run pyright
          '';
        };

        tests = pkgs.writeShellApplication {
          name = "run-tests";
          runtimeInputs = [ api.dependencyEnv ];
          text = "pytest";
        };
      in {
        packages = {
          inherit api ui tests ci-bandit ci-ruff ci-pyright;
          default = api;
        };
        devShells.default = with pkgs; mkShell {
          inputsFrom = [
            api
          ];
          packages = [
            poetry
            ruff
            nodePackages.pyright

            ui
          ];
          shellHook = "source $(poetry env info --path)/bin/activate";
        };
      });
}
