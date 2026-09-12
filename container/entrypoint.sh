#!/bin/sh
# Runs inside the hybrid-d77 build container (rootful, --privileged).
# Builds hybrid-d77's own "sway" variant (see iso/mklive-d77.sh and
# vendor/chimera-live/mklive-image.sh's "sway" case).
#
# EXPECTED TO FAIL as of 2026-09-12: h77-dots/h77-sway-dots (pkg/) are
# not built as real .apk files yet -- that needs a real cports/cbuild
# checkout + toolchain bootstrap, not done. This run's real purpose is
# to confirm every OTHER package name resolves (sway, yambar, udiskie,
# etc, all verified individually already -- this is the first time
# they're all requested together in one transaction) and see exactly
# where it stops.
set -eu
cd /src

echo ">> iso/mklive-d77.sh (hybrid-d77's own sway variant)"
./iso/mklive-d77.sh

echo ">> copying the ISO out to /src/iso"
mkdir -p /src/iso
# mklive.sh writes the .iso to CWD (vendor/chimera-live/ here), NOT into
# the build dir passed as an argument -- confirmed 2026-09-12 the hard
# way (this used to look in build/*.iso and silently produced nothing).
cp vendor/chimera-live/*.iso /src/iso/ 2>/dev/null || { echo "!! no ISO produced" >&2; exit 1; }
( cd /src/iso && for f in *.iso; do sha256sum "$f" > "$f.sha256"; done )
ls -lh /src/iso/*.iso
