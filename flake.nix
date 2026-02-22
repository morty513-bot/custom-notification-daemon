{
  description = "Custom notification daemon";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };

        python = pkgs.python3;
        py = python.pkgs;
      in
      {
        devShells.default = pkgs.mkShell {
          packages = [
            python
            py.dbus-next

            # test client for sending notifications (notify-send)
            pkgs.libnotify

            # debugging/inspection tools (session bus listing, monitor, etc.)
            pkgs.systemd # provides busctl
            pkgs.dbus    # provides dbus-send, dbus-monitor

            # optional quality-of-life tooling
            py.ruff
            py.black
            py.pytest
          ];

          shellHook = ''
            export PYTHONUNBUFFERED=1
          '';
        };
      });
}
