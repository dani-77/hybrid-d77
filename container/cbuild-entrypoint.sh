#!/bin/sh
# Runs inside the hybrid-d77-cbuild container, as the non-root "builder"
# user (cbuild refuses root outright). Bootstraps a local cports
# checkout + build root, drops our own pkg/h77-dots and
# pkg/h77-sway-dots into it as a new "hybrid" category (cbuild
# discovers categories by scanning top-level dirs for template.py --
# confirmed against its real src/runner.py _collect_tmpls, nothing is
# hardcoded to main/user/cross), and builds both into real .apk files.
set -eu

CPORTS=/home/builder/cports

if [ ! -d "$CPORTS/.git" ]; then
	echo ">> shallow-cloning chimera-linux/cports (this is a real, fairly"
	echo "   large checkout -- source templates for the whole distro)"
	git clone --depth 1 https://github.com/chimera-linux/cports "$CPORTS"
fi

echo ">> syncing pkg/h77-dots + pkg/h77-sway-dots into cports as 'hybrid/'"
mkdir -p "$CPORTS/hybrid"
rm -rf "$CPORTS/hybrid/h77-dots" "$CPORTS/hybrid/h77-sway-dots"
cp -a /src/pkg/h77-dots "$CPORTS/hybrid/h77-dots"
cp -a /src/pkg/h77-sway-dots "$CPORTS/hybrid/h77-sway-dots"

cd "$CPORTS"

if ! ls etc/keys/*.rsa >/dev/null 2>&1; then
	echo ">> generating a signing key (etc/keys/*.rsa)"
	./cbuild keygen
fi

if [ ! -d bldroot ]; then
	echo ">> bootstrapping the build root (binary bootstrap, not"
	echo "   source-bootstrap -- we don't need to rebuild the whole"
	echo "   toolchain from scratch just to build two meta packages)"
	./cbuild bootstrap
fi

echo ">> building hybrid/h77-dots"
./cbuild pkg hybrid/h77-dots

echo ">> building hybrid/h77-sway-dots"
./cbuild pkg hybrid/h77-sway-dots

echo ">> copying the built repo out to /src/cbuild-out"
mkdir -p /src/cbuild-out
cp -a packages/hybrid /src/cbuild-out/
cp etc/keys/*.pub /src/cbuild-out/ 2>/dev/null || true

echo ">> done -- /src/cbuild-out/hybrid now holds real .apk packages"
ls -la /src/cbuild-out/hybrid
