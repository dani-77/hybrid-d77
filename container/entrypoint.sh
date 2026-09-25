#!/bin/sh
# Runs inside the hybrid-d77 build container (rootful, --privileged).
# Builds one of hybrid-d77's own variants (VARIANT env var: sway, the
# default, or niri -- see iso/mklive-d77.sh and vendor/chimera-live/
# mklive-image.sh's "sway"/"niri" cases), with the real h77-* packages
# baked in -- run container/cbuild.Containerfile first (separately,
# needs its own --privileged run for a different reason: bwrap's
# nested mount() calls) to produce cbuild-out/hybrid/, which
# iso/mklive-d77.sh requires and refuses to run without.
#
# iso/mklive-d77.sh itself moves the finished ISO into /src/iso and
# writes its .sha256 (since 2026-09-24). This script used to also `cp
# vendor/chimera-live/*.iso` afterwards, from before that change --
# by then the ISO was already gone from there, so that cp failed and
# every container build ended in "no ISO produced". Removed.
set -eu
cd /src

VARIANT="${VARIANT:-sway}"
echo ">> iso/mklive-d77.sh $VARIANT"
./iso/mklive-d77.sh "$VARIANT"
