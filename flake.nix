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
          default = mkPoetryApplication {
            projectDir = self;
          };
        };
        devShells.default = with pkgs; mkShell {
          inputsFrom = [ self.packages.${system}.default ];
          packages = [
            poetry
            ruff
            nodePackages.pyright
          ];
          shellHook = "source $(poetry env info --path)/bin/activate";
        };
      });
}
