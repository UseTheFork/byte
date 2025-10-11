{
  inputs = {
    systems.url = "github:nix-systems/default-linux";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";

    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    uv2nix = {
      url = "github:pyproject-nix/uv2nix";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.uv2nix.follows = "uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    inputs@{
      flake-parts,
      nixpkgs,
      pyproject-nix,
      uv2nix,
      pyproject-build-systems,
      ...
    }:
    flake-parts.lib.mkFlake
      {
        inherit inputs;
      }
      (
        {
          withSystem,
          flake-parts-lib,
          inputs,
          self,
          ...
        }:
        let

          # Load the uv workspace from the project root
          workspace = uv2nix.lib.workspace.loadWorkspace { workspaceRoot = ./.; };

          # Create overlay for building Python packages from the workspace
          overlay = workspace.mkPyprojectOverlay {
            sourcePreference = "wheel"; # Prefer wheels for faster builds
          };

        in
        {
          systems = import inputs.systems;
          perSystem =
            { pkgs, lib, ... }:
            let
              python = pkgs.python312;

              # Create Python package set with uv2nix overlays
              pythonSet =
                (pkgs.callPackage pyproject-nix.build.packages {
                  inherit python;
                }).overrideScope
                  (
                    lib.composeManyExtensions [
                      pyproject-build-systems.overlays.default
                      overlay
                    ]
                  );

              # Create production virtual environment with only runtime dependencies
              prodVirtualenv = pythonSet.mkVirtualEnv "byte" workspace.deps.default;
            in

            {
              devShells.default = pkgs.mkShellNoCC {
                name = "nix";

                # Tell Direnv to shut up.
                DIRENV_LOG_FORMAT = "";

                packages = [

                  pkgs.just # Command Runner
                  pkgs.pre-commit

                  pkgs.uv
                  pkgs.nodejs
                  pkgs.prettier

                  # Tools / Formaters Linters etc
                  pkgs.alejandra # Nix
                  pkgs.yamlfmt # YAML
                  pkgs.keep-sorted # General Sorting tool

                ];
              };
              packages = {
                default = prodVirtualenv;
                byte = prodVirtualenv;
              };
            };
        }
      );
}
