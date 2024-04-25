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
      in {
        packages = {
          api = mkPoetryApplication {
            projectDir = self;
            groups = [ "api" ];
          };
          ui = let
            app = mkPoetryApplication {
              projectDir = self;
              groups = [ "ui" ];
              preferWheels = true;
            };
          in pkgs.writeShellApplication {
            name = "nix-store-explorer-ui";
            runtimeInputs = [ app.dependencyEnv ];
            text = ''
              streamlit run ${app.dependencyEnv}/lib/python3.11/site-packages/ui/frontend.py
            '';
          };

          default = self.packages.${system}.api;
        };
        devShells.default = with pkgs; mkShell {
          inputsFrom = [
            self.packages.${system}.api
          ];
          packages = [
            poetry
            ruff
            nodePackages.pyright
            self.packages.${system}.ui
          ];
          shellHook = "source $(poetry env info --path)/bin/activate";
        };
      });
}
