#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
package_name="custom-notification-daemon"
artifact_dir="$repo_root/build-artifacts"

mkdir -p "$artifact_dir"

pushd "$repo_root" >/dev/null

dpkg-buildpackage -us -uc

shopt -s nullglob
for f in ../"$package_name"_*.deb \
         ../"$package_name"_*.ddeb \
         ../"$package_name"_*.dsc \
         ../"$package_name"_*.tar.* \
         ../"$package_name"_*.buildinfo \
         ../"$package_name"_*.changes; do
    mv -f "$f" "$artifact_dir/"
done

popd >/dev/null

echo "Build artifacts moved to: $artifact_dir"
