#!/bin/sh
# Runs inside the hybrid-d77 build container (rootful, --privileged).
# Builds hybrid-d77's own "sway" variant (see iso/mklive-d77.sh and
# vendor/chimera-live/mklive-image.sh's "sway" case), with the real
# h77-dots/h77-sway-dots packages baked in -- run
# container/cbuild.Containerfile first (separately, needs its own
# --privileged run for a different reason: bwrap's nested mount()
# calls) to produce cbuild-out/hybrid/, which iso/mklive-d77.sh
# requires and refuses to run without.
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
