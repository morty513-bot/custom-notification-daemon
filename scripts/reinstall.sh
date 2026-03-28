#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
artifact_dir="$repo_root/build-artifacts"

shopt -s nullglob
artifacts=("$artifact_dir"/custom-notification-daemon_*.deb)

if [[ ${#artifacts[@]} -eq 0 ]]; then
	echo "No .deb artifact found in $artifact_dir" >&2
	echo "Run ./scripts/build-deb.sh first." >&2
	exit 1
fi

latest_deb="$(ls -t "${artifacts[@]}" | head -n 1)"
echo "Installing: $latest_deb"
sudo dpkg -i "$latest_deb"


