#!/bin/sh
# hybrid-d77 :: ONE command, whole pipeline. Runs both containers in
# the right order and produces a ready-to-write ISO under iso/.
#
#   ./build.sh [all|sway|niri]  (default: all)
#   PKGS=auto|fetch|local ./build.sh ...  (default: auto)
#
# "all" builds the packages ONCE, then both ISOs back to back -- the
# packages are identical for both variants, so there's no point in
# building them twice.
#
# PKGS=auto (the default) skips the package build entirely when CI
# already published the same thing: the "h77-pkgs" release notes name
# the commit it was built from, and if nothing CI builds from (pkg/,
# the cbuild container) differs between that commit and this working
# tree, iso/fetch-pkgs.sh just downloads it. Anything else -- local
# changes, commits CI hasn't built yet, no gh, no network -- builds
# locally like before. The cbuild container is --rm and keeps its
# cports checkout/build root inside itself, so a local build always
# starts from scratch (clone, bootstrap, every package): ~an hour on
# this project's own build host, vs. seconds to download.
# PKGS=fetch / PKGS=local force one or the other.
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

case "${1:-all}" in
	all) VARIANTS="sway niri" ;;
	sway|niri) VARIANTS="$1" ;;
	*) echo "usage: $0 [all|sway|niri]" >&2; exit 1 ;;
esac

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

# Same paths as .github/workflows/build-h77-pkgs.yml's own push trigger
# -- the only inputs that change what CI publishes.
PKG_INPUTS="pkg container/cbuild.Containerfile container/cbuild-entrypoint.sh"

# Prints the commit the published "h77-pkgs" release was built from,
# if it matches this working tree's package inputs exactly (committed
# AND uncommitted, untracked files included); prints nothing otherwise.
published_matches() {
	command -v gh > /dev/null 2>&1 || return 0
	sha=$(gh release view h77-pkgs --repo "${HYBRID_D77_REPO:-dani-77/hybrid-d77}" --json body --jq .body 2> /dev/null |
		sed -n 's/.* from \([0-9a-f]\{40\}\)\..*/\1/p')
	[ -n "$sha" ] || return 0
	git cat-file -e "$sha^{commit}" 2> /dev/null || return 0
	# shellcheck disable=SC2086 # PKG_INPUTS is a word list on purpose
	git diff --quiet "$sha" -- $PKG_INPUTS || return 0
	# shellcheck disable=SC2086
	[ -z "$(git ls-files --others --exclude-standard -- $PKG_INPUTS)" ] || return 0
	echo "$sha"
}

case "${PKGS:-auto}" in
	auto)
		sha=$(published_matches)
		if [ -n "$sha" ]; then PKGS=fetch; else PKGS=local; fi
		;;
	fetch|local) ;;
	*) echo "PKGS must be auto, fetch or local" >&2; exit 1 ;;
esac

echo ""
if [ "$PKGS" = fetch ]; then
	echo "== 1/2: fetching the h77-* packages from the h77-pkgs release${sha:+ (built from $sha)} =="
	# A previous local build left cbuild-out owned by uid 1000.
	[ "$(id -u)" = 0 ] || sudo chown -R "$(id -u):$(id -g)" cbuild-out 2> /dev/null || true
	./iso/fetch-pkgs.sh
else
	echo "== 1/2: building the h77-* packages (+ utumno, qsd77) =="
	# install_files() copies each pkg/*/skel tree as-is, so a stray
	# __pycache__ (e.g. from running waybar's mediaplayer.py locally) ends
	# up in the package and cbuild aborts with "leftover unsplit pycache".
	# It's gitignored, so CI never sees it -- only local builds break.
	find pkg -path '*/skel/*' -name __pycache__ -type d -prune -exec rm -rf {} +
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
fi

for VARIANT in $VARIANTS; do
	echo ""
	echo "== 2/2: building the $VARIANT ISO =="
	# A previous ISO build's leftover build/ dir is owned by root (the ISO
	# container runs rootful) -- a plain rm here fails with "Permissão
	# recusada" the very next time this runs as a normal user. Confirmed
	# the hard way.
	[ "$(id -u)" = 0 ] && rm -rf vendor/chimera-live/build || sudo rm -rf vendor/chimera-live/build
	$ENGINE build -t hybrid-d77-build -f container/Containerfile .
	$ENGINE run --rm --privileged --security-opt label=disable \
		-e VARIANT="$VARIANT" \
		-v "$PWD:/src" -w /src \
		hybrid-d77-build

	iso=$(ls -t iso/hybrid-d77-live-*-"$VARIANT".iso 2> /dev/null | head -1)
	[ -n "$iso" ] || { echo "!! no ISO produced" >&2; exit 1; }
	[ "$(id -u)" = 0 ] || sudo chown "$(id -u):$(id -g)" "$iso" "$iso.sha256" 2> /dev/null || true

	echo ""
	echo ">> done: $iso"
	# The checksum file, written by container/entrypoint.sh itself, holds
	# only the bare filename (it's generated with `cd iso && sha256sum
	# "$f" > "$f.sha256"`) -- sha256sum -c needs to run from that same
	# directory to resolve it, not the repo root. Confirmed the hard way.
	( cd iso && sha256sum -c "$(basename "$iso").sha256" )
done
