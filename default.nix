{ poetry2nixSrc ? null }:
let
  sources = import ./nix/sources.nix {};
  pkgs = import sources.nixpkgs {};
  poetry2nix = pkgs.callPackage sources.poetry2nix { inherit pkgs; } ;
  python = pkgs.python310;
  projectDir = ./.;
  overrides = poetry2nix.overrides.withDefaults (
    self: super: {
      selenium-requests = super.selenium-requests.overridePythonAttrs (
        old: { buildInputs = (old.buildInputs or [ ]) ++ [ super.poetry ] ;}
      );
    }
  );
in
{
  app = poetry2nix.mkPoetryApplication {
    inherit python projectDir overrides;
  };
  env = poetry2nix.mkPoetryEnv {
    editablePackageSources = { gbm = ./.; };
    inherit python projectDir overrides;
  };
  inherit pkgs python;
}
