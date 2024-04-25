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

        tests = pkgs.writeShellApplication {
          name = "run-tests";
          runtimeInputs = [ api.dependencyEnv ];
          text = "pytest";
        };
      in {
        packages = {
          inherit api ui tests;
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
