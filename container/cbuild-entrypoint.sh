#!/bin/sh
# Runs inside the hybrid-d77-cbuild container, as the non-root "builder"
# user (cbuild refuses root outright). Bootstraps a local cports
# checkout + build root, drops our own pkg/* packages into it as a new
# "hybrid" category (cbuild discovers categories by scanning top-level
# dirs for template.py -- confirmed against its real src/runner.py
# _collect_tmpls, nothing is hardcoded to main/user/cross), and builds
# each into a real .apk file.
set -eu

CPORTS=/home/builder/cports
# Every package under pkg/ that should be built this way. Add new
# ones here (and their name to mklive-image.sh's package list) --
# nothing else needs touching.
# h77-welcome listed before h77-sway-dots: the latter's depends=
# includes the former (see h77-sway-dots' own template.py comment),
# and this loop builds strictly in this order below -- untested
# whether cbuild resolves in-category build order on its own, so this
# doesn't rely on it.
H77_PKGS="h77-dots h77-welcome h77-sway-dots h77-installer h77-install-scripts"

if [ ! -d "$CPORTS/.git" ]; then
	echo ">> shallow-cloning chimera-linux/cports (this is a real, fairly"
	echo "   large checkout -- source templates for the whole distro)"
	git clone --depth 1 https://github.com/chimera-linux/cports "$CPORTS"
fi

echo ">> syncing pkg/{$H77_PKGS} into cports as 'hybrid/'"
mkdir -p "$CPORTS/hybrid"
for p in $H77_PKGS; do
	rm -rf "$CPORTS/hybrid/$p"
	cp -a "/src/pkg/$p" "$CPORTS/hybrid/$p"
done

cd "$CPORTS"

if ! ls etc/keys/*.rsa >/dev/null 2>&1; then
	echo ">> generating a signing key (etc/keys/*.rsa)"
	./cbuild keygen
fi

# cbuild refuses to build from any category outside etc/config.ini's
# [build] categories setting ("main user" by default) -- confirmed the
# hard way: "h77-dots-0.1.0-r0: ERROR: cannot be built, disallowed by
# cbuild (not in main, user)". The example config's own comment says
# "custom categories are not supported! the mechanism though which
# they work is an implementation detail subject to change at any
# time" -- true for upstream contributions, fine for our own local-only
# build. Widen it to include "hybrid" here rather than editing a
# tracked cports file (this whole checkout is throwaway/untracked).
# Also disables the linter/formatter enforcement (flake8+black/ruff):
# neither is installed here and both are "enforced unless set to none"
# per config.ini.example -- confirmed the hard way, "could not
# determine template linter". Fine for our own two trivial meta
# packages; upstream contributions would need the real tools.
#
# Done via Python's configparser, not sed -- chimerautils' sed is BSD
# sed, not GNU sed, and its -i/`a` syntax differ enough (confirmed the
# hard way: "invalid command code e") that a portable edit is simpler
# than chasing BSD-sed quoting. Runs AFTER keygen on purpose: keygen
# itself creates/rewrites etc/config.ini with the [signing] section,
# and this must not race or get clobbered by that.
python3 - <<'PYEOF'
import configparser
cfg = configparser.ConfigParser()
cfg.read("etc/config.ini")
if not cfg.has_section("build"):
    cfg.add_section("build")
cfg.set("build", "categories", "main user hybrid")
cfg.set("build", "linter", "none")
cfg.set("build", "formatter", "none")
with open("etc/config.ini", "w") as f:
    cfg.write(f)
PYEOF

if [ ! -d bldroot ]; then
	echo ">> bootstrapping the build root (binary bootstrap, not"
	echo "   source-bootstrap -- we don't need to rebuild the whole"
	echo "   toolchain from scratch just to build two meta packages)"
	./cbuild bootstrap
fi

for p in $H77_PKGS; do
	echo ">> building hybrid/$p"
	./cbuild pkg "hybrid/$p"
done

echo ">> copying the built repo out to /src/cbuild-out"
mkdir -p /src/cbuild-out
cp -a packages/hybrid /src/cbuild-out/
cp etc/keys/*.pub /src/cbuild-out/ 2>/dev/null || true

echo ">> done -- /src/cbuild-out/hybrid now holds real .apk packages"
ls -la /src/cbuild-out/hybrid
