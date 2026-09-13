#!/bin/sh
# Builds ONLY the ISO half of the pipeline (via container/Containerfile),
# rootful (chroot/mount work needs it). Needs cbuild-out/hybrid/ to
# already exist (either from container/cbuild.Containerfile, or from
# iso/fetch-pkgs.sh) -- iso/mklive-d77.sh refuses to run without it.
#
# For the whole pipeline in one command (cbuild + this), use the repo
# root's own ./build.sh instead -- this script is what it calls for
# the ISO half; kept standalone too for anyone who wants to run just
# this step by hand (e.g. after fetch-pkgs.sh instead of cbuild).
#
#   container/build.sh                 # wrapper: builds image + runs rootful
#   REBUILD=1 container/build.sh       # rebuild the image first
set -eu

cd "$(dirname "$0")/.."
IMAGE=${IMAGE:-hybrid-d77-build}

if [ -n "${ENGINE:-}" ]; then :
elif command -v docker >/dev/null 2>&1; then
	if docker info >/dev/null 2>&1; then ENGINE="docker"; else ENGINE="sudo docker"; fi
elif command -v podman >/dev/null 2>&1; then
	if [ "$(id -u)" = 0 ]; then ENGINE="podman"; else ENGINE="sudo podman"; fi
else echo "need docker or podman" >&2; exit 1; fi
echo ">> engine: $ENGINE"

if [ "${REBUILD:-0}" = 1 ] || ! $ENGINE image inspect "$IMAGE" >/dev/null 2>&1; then
	$ENGINE build -t "$IMAGE" -f container/Containerfile .
fi

chmod +x container/entrypoint.sh iso/*.sh 2>/dev/null || true

exec $ENGINE run --rm --privileged \
	--security-opt label=disable \
	-v "$PWD:/src" -w /src \
	"$IMAGE" "$@"
