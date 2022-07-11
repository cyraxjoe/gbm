let
  gbm = import ./. {};
  inherit(gbm) pkgs python;
  extraPackages = [
    python.pkgs.bpython
    python.pkgs.pyflakes
    python.pkgs.flake8
    pkgs.geckodriver
  ];
in
pkgs.mkShell {
  buildInputs = [ gbm.env python ] ++ extraPackages;
}
