#!/bin/sh
# hybrid-d77 :: fetch the latest h77-dots/h77-sway-dots/h77-installer
# build from the "h77-pkgs" GitHub Release (built by
# .github/workflows/build-h77-pkgs.yml) instead of running
# container/cbuild.Containerfile locally every time. Same pattern as
# d77crux-live's own scripts/fetch-kernel.sh.
#
# Populates exactly what iso/mklive-d77.sh already expects:
#   cbuild-out/hybrid/x86_64/{*.apk,APKINDEX.tar.gz}
#   cbuild-out/*.rsa.pub
#
#   iso/fetch-pkgs.sh              # latest "h77-pkgs" release
#   iso/fetch-pkgs.sh <tag>        # a specific release tag
set -eu

repo=${HYBRID_D77_REPO:-dani-77/hybrid-d77}
project=$(cd -- "$(dirname -- "$0")/.." && pwd)
out="$project/cbuild-out"
tag=${1:-h77-pkgs}

command -v gh >/dev/null || { echo "gh (GitHub CLI) is required." >&2; exit 1; }

echo ">> fetching release '$tag' from $repo"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
gh release download "$tag" --repo "$repo" --dir "$tmp" --clobber

[ -f "$tmp/SHA256SUMS" ] || { echo "!! release is missing SHA256SUMS" >&2; exit 1; }
( cd "$tmp" && sha256sum -c SHA256SUMS )

rm -rf "$out/hybrid"
mkdir -p "$out/hybrid/x86_64"
mv "$tmp"/*.apk "$tmp"/APKINDEX.tar.gz "$out/hybrid/x86_64/"
mv "$tmp"/*.pub "$out/"

echo ">> done -- $out/hybrid now holds the published .apk packages"
ls -la "$out/hybrid/x86_64"
