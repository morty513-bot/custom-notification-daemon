# AGENTS.md

This file is a lightweight handoff for future coding-agent sessions.
Keep this file up to date where needed.

## Project Snapshot

- Name: custom-notification-daemon
- Goal: run a custom `org.freedesktop.Notifications` daemon for Wayland/Sway.
- Current UX target: toast-like notifications in the top-right, layered above windows (no layout reservation).

## Core Files

- `main.py`: app entrypoint; wires daemon + renderer.
- `notifications.py`: D-Bus protocol layer and daemon base class.
- `renderer.py`: GTK renderer and layer-shell integration.
- `apt-packages.txt`: required apt dependencies.
- `requirements.txt`: Python dependencies.
- `typings/`: local stubs for GI introspection modules used by type checker.
- `pyrightconfig.json`: points pyright to local stubs.

## Runtime Behavior Notes

- The daemon must own `org.freedesktop.Notifications`.
- If another notification daemon is running (dunst/mako/etc.), startup fails by design.
- On Wayland/Sway, true non-window-overlay behavior requires GtkLayerShell.

## Environment Setup

Install system packages:

sudo xargs -a apt-packages.txt apt install -y

Create venv with system site packages (important for apt-installed GI libs):

/usr/bin/python3 -m venv --system-site-packages .venv
source .venv/bin/activate
pip install -r requirements.txt

Run daemon:

source .venv/bin/activate
python main.py

## Renderer Decisions (Current)

- GTK version is detected dynamically (prefers GTK3, falls back to GTK4).
- GtkLayerShell is optional; if unavailable, renderer falls back to normal GTK windows.
- GtkLayerShell version handling includes `0.1` and `0` for compatibility.
- Toast positioning uses top-right anchors and margins.
- Exclusive zone is set to `0` so compositor does not shrink workspace.
- Keyboard mode is set to `NONE` when supported to avoid focus grab.

## D-Bus / Protocol Notes

- Signal emitters in `notifications.py` must return a list body.
- Returning tuples for dbus-next signals caused `SignatureBodyMismatchError` in earlier iteration.

## Type Checking Notes

- GI imports are dynamic (`gi.repository`) and not fully statically discoverable.
- Local minimal stubs are intentionally partial, only for symbols used here.
- `pyrightconfig.json` uses:
  - `stubPath: typings`
  - `reportMissingModuleSource: none`

## Quick Troubleshooting

If startup says another daemon is running:

pkill -x dunst || true
pkill -x mako || true
systemctl --user stop dunst.service 2>/dev/null || true
systemctl --user stop mako.service 2>/dev/null || true

If renderer warns it is running without GtkLayerShell:

- Verify apt packages from `apt-packages.txt` are installed.
- Recreate venv with `--system-site-packages`.
