{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
      in with pkgs; {
        devShells.default = mkShell {
          packages = [
            python311
            sqlite
            python311Packages.fastapi
            python311Packages.streamlit

            ruff
            python311Packages.pytest
            python311Packages.bandit
            nodePackages.pyright
          ];
        };
      }
    );
}
