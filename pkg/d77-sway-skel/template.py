# hybrid-d77 :: the d77 Sway/Waybar desktop config, as a cports package.
#
# Modeled directly on d77alpine's pkg/d77-sway-skel/APKBUILD (same idea,
# same pkg-manager family -- Chimera uses apk too, just built via cports'
# Python templates instead of abuild's shell APKBUILDs). NOT yet verified
# against a real cbuild run -- this is scaffolding from the 2026-09-12
# research session (see ../../docs/NOTES.md), not a working package.
#
# TODO before this builds:
#   - confirm every package name below actually exists in cports (main/
#     user) -- these are carried over from the Alpine names and WILL be
#     wrong in places (Chimera's naming doesn't always match Alpine's)
#   - figure out the dinit-vs-openrc service story (Chimera uses dinit,
#     not OpenRC -- d77alpine's `*-openrc` subpackage pattern has no
#     direct equivalent here)
#   - `skel/` (dotfiles) and `bin/` (d77-session, fuzzel-power-menu,
#     d77-setup) are still empty -- copy over from d77alpine's skel once
#     the compositor config itself is ported/adapted
#   - no `depends=` list yet; needs a first successful `cbuild` run
#     against a real cports checkout to know what's actually installable

pkgname = "d77-sway-skel"
pkgver = "0.1.0"
pkgrel = 0
build_style = "meta"
pkgdesc = "d77 Sway/Waybar desktop config (/etc/skel) + the desktop it pulls in"
license = "MIT"
url = "https://github.com/dani-77/hybrid-d77"

# placeholder -- see the TODO above, none of this is verified yet
depends = [
    "sway",
    "waybar",
    "foot",
    # ...
]


def install(self):
    # TODO: install skel/ to etc/skel, bin/ to usr/bin, same shape as
    # d77alpine's package() step (cp -a skel/. -> etc/skel/, etc.)
    pass
