#!/bin/sh
# hybrid-d77 :: our own "sway" image variant, via chimera-live's own
# mklive-image.sh -b flag mechanism (see vendor/chimera-live/
# mklive-image.sh's "sway" case, added 2026-09-12).
#
# NOT YET FULLY WORKING: h77-dots and h77-sway-dots (our own cports
# packages, pkg/h77-dots and pkg/h77-sway-dots) don't exist as built
# .apk files yet -- that needs a real cports/cbuild checkout + toolchain
# bootstrap, not done yet (see docs/NOTES.md). Every other package name
# in the "sway" case IS verified against the real repo already.
#
# Once a local cports build exists, pass it here via -r/-k, e.g.:
#   ./mklive-d77.sh -r /path/to/cports/packages/main -k /path/to/cports/etc/keys
set -e
cd "$(dirname "$0")/../vendor/chimera-live"
# -r main is passed explicitly: mklive.sh's own default repo only kicks
# in when NO -r is given at all, so once we add -r for the `user` tier
# (needed for greetd/udiskie/seatd), main has to be listed too or it's
# silently dropped. These have to come BEFORE the `build` positional
# arg: mklive-image.sh forwards its own "$@" verbatim onto the end of
# `mklive.sh -p ... -f ...`, and mklive.sh's getopts stops at the first
# non-flag word -- so anything meant to be a real -r/-k/etc option has
# to precede `build` in THIS invocation too, or it lands as a stray
# positional arg on mklive.sh's side instead of being parsed.
exec ./mklive-image.sh -b sway -- \
    -r https://repo.chimera-linux.org/current/main \
    -r https://repo.chimera-linux.org/current/user \
    build "$@"
