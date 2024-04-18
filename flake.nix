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
          LD_LIBRARY_PATH = "${stdenv.cc.cc.lib}/lib";
          packages = [
            python311
            sqlite
            poetry
            ruff
            nodePackages.pyright
          ];
          shellHook = "source $(poetry env info --path)/bin/activate";
        };
      }
    );
}
