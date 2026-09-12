#!/bin/sh
# hybrid-d77 :: wrapper around vendor/chimera-live/mklive.sh, same shape
# as their own mklive-image.sh's -b flag (see that file for the base/
# gnome/plasma cases this is modeled on).
#
# NOT YET WORKING -- scaffolding only (2026-09-12). Needs, at minimum:
#   - a local cports checkout + `cbuild` run producing a real repo for
#     -r/-k below (pkg/d77-sway-skel isn't buildable yet, see its
#     template.py TODOs)
#   - confirming the base package set (sway/waybar/foot/... availability
#     in cports) actually matches what's listed there
#
# Intended usage, once real:
#   cd vendor/chimera-live && ../../iso/mklive-d77.sh
set -e
cd "$(dirname "$0")/../vendor/chimera-live"

PKGS="base-full base-live linux-stable d77-sway-skel"

# TODO: -r <path to our cports build output>, -k <our signing key dir>
exec ./mklive.sh -f d77 -p "$PKGS" "$@"
