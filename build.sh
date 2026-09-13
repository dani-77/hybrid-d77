#!/bin/sh
# hybrid-d77 :: ONE command, whole pipeline. Runs both containers in
# the right order and produces a ready-to-write ISO under iso/.
#
#   ./build.sh
#
# Why two separate containers (unlike e.g. d77devuan's own single
# container/build.sh): cbuild REFUSES to run as root ("Please don't
# run cbuild as root", confirmed against cports' own src/early.py),
# while mklive.sh (the ISO builder) needs root for mount(8). Each
# container also needs its OWN image (container/cbuild.Containerfile
# vs container/Containerfile) -- different base setup, different
# entrypoint. This script exists so nobody has to remember that split
# or the exact podman invocations by hand; running the two containers
# separately (as documented in each Containerfile's own header
# comment) still works fine too.
set -eu

cd "$(dirname "$0")"

if [ -n "${ENGINE:-}" ]; then :
elif command -v docker > /dev/null 2>&1; then
	if docker info > /dev/null 2>&1; then ENGINE="docker"; else ENGINE="sudo docker"; fi
elif command -v podman > /dev/null 2>&1; then
	if [ "$(id -u)" = 0 ]; then ENGINE="podman"; else ENGINE="sudo podman"; fi
else
	echo "need docker or podman" >&2
	exit 1
fi
echo ">> engine: $ENGINE"

echo ""
echo "== 1/2: building h77-dots / h77-sway-dots / h77-installer / h77-install-scripts =="
$ENGINE build -t hybrid-d77-cbuild -f container/cbuild.Containerfile .
mkdir -p cbuild-out
# The container's own "builder" user is a fixed uid 1000 -- pre-own
# cbuild-out so it can write into it without a permission error, same
# fix this project's own CI workflow needed for the same reason.
[ "$(id -u)" = 0 ] || sudo chown -R 1000:1000 cbuild-out 2> /dev/null || true
$ENGINE run --rm --privileged --security-opt label=disable \
	-v "$PWD:/src" -w /src \
	hybrid-d77-cbuild
# Hand ownership back to the invoking user -- the container wrote as
# uid 1000, this shell (and anything reading cbuild-out/ next) isn't
# necessarily that uid.
[ "$(id -u)" = 0 ] || sudo chown -R "$(id -u):$(id -g)" cbuild-out 2> /dev/null || true

echo ""
echo "== 2/2: building the sway ISO =="
# A previous ISO build's leftover build/ dir is owned by root (the ISO
# container runs rootful) -- a plain rm here fails with "Permissão
# recusada" the very next time this runs as a normal user. Confirmed
# the hard way.
[ "$(id -u)" = 0 ] && rm -rf vendor/chimera-live/build || sudo rm -rf vendor/chimera-live/build
$ENGINE build -t hybrid-d77-build -f container/Containerfile .
$ENGINE run --rm --privileged --security-opt label=disable \
	-v "$PWD:/src" -w /src \
	hybrid-d77-build

iso=$(ls -t iso/chimera-linux-x86_64-LIVE-*-sway.iso 2> /dev/null | head -1)
[ -n "$iso" ] || { echo "!! no ISO produced" >&2; exit 1; }
[ "$(id -u)" = 0 ] || sudo chown "$(id -u):$(id -g)" "$iso" "$iso.sha256" 2> /dev/null || true

echo ""
echo ">> done: $iso"
# The checksum file, written by container/entrypoint.sh itself, holds
# only the bare filename (it's generated with `cd iso && sha256sum
# "$f" > "$f.sha256"`) -- sha256sum -c needs to run from that same
# directory to resolve it, not the repo root. Confirmed the hard way.
( cd iso && sha256sum -c "$(basename "$iso").sha256" )
