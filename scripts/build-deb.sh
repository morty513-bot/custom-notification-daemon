#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
package_name="custom-notification-daemon"
artifact_dir="$repo_root/build-artifacts"
main_version="$(grep -E '^VERSION: Final\[str\] = "' "$repo_root/main.py" | sed -E 's/^VERSION: Final\[str\] = "([^"]+)"$/\1/')"
debian_version="$(sed -n '1s/^custom-notification-daemon (\([^)]*\)).*/\1/p' "$repo_root/debian/changelog")"

if [[ -z "$main_version" || -z "$debian_version" ]]; then
    echo "Could not parse versions from main.py or debian/changelog" >&2
    exit 1
fi

if [[ "$main_version" != "$debian_version" ]]; then
    echo "Version mismatch:" >&2
    echo "  main.py VERSION:        $main_version" >&2
    echo "  debian/changelog:       $debian_version" >&2
    echo "Please keep versions in sync before building." >&2
    exit 1
fi

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
