# hybrid-d77 :: Utumno, the user's own minimal Quickshell desktop shell
# (github.com/dani-77/utumno), as the niri variant's bar/launcher/lock
# screen. Same install layout as its own Void xbps-src template (void/
# srcpkgs/utumno in that repo): the whole tree under /usr/share/
# quickshell/utumno. NOT found by a plain `qs -c utumno` (qs only
# searches $XDG_CONFIG_DIRS/quickshell, default /etc/xdg) -- launch it
# through `qsd77 run -c utumno`, which prepends /usr/share to
# XDG_CONFIG_DIRS first (confirmed on the first real niri boot).
#
# Installed by hand here instead of through its own Makefile: that
# Makefile is just an `rsync -a --delete` with a few excludes, and
# install_files() does the same copy without pulling rsync into the
# build root.
#
# depends: quickshell-h77 (this project's own Quickshell build, WITH
# the Hyprland QML module its bar needs -- see that template). Runtime
# deps besides that: the commands its
# QML actually shells out to -- amixer (alsa-utils), brightnessctl,
# curl, powerprofilesctl (power-profiles-daemon), checked against the
# source, not copied blindly from the Void template (whose
# wireless_tools/alsa-tools are never called). Listed in
# mklive-image.sh's niri package set rather than as depends=, same
# convention as h77-dots' bash -- that convention came from a cbuild
# "cannot be resolved" error whose real cause (hybrid/ had no .parent
# link, see container/cbuild-entrypoint.sh) is fixed since 2026-09-25,
# so declaring them here would now work too.
#
# eww + atop (0.4.0 on): clicking CPU or RAM on the bar opens an eww
# system monitor (monitor/d77-monitor, with its eww.yuck/eww.scss next to
# it, so no eww config needs installing). Its data comes from dgop, which
# isn't in cports, or else from atop, which d77-monitor parses itself.
# Both are in cports' user tier and are declared here, not only in the
# ISO package set, so h77-update pulls them in on installed systems too.
pkgname = "utumno"
pkgver = "0.4.1"
pkgrel = 0
depends = ["quickshell-h77", "eww", "atop"]
pkgdesc = "Minimal Quickshell desktop shell for Wayland compositors"
license = "MIT"
url = "https://github.com/dani-77/utumno"
source = f"{url}/archive/refs/tags/{pkgver}.tar.gz"
sha256 = "6196f6bd080c04f3b646a87f6b882a15c0144352c25a6549586e8be4a1bbb555"


def install(self):
    self.install_dir("usr/share/quickshell/utumno")
    for f in self.cwd.iterdir():
        if f.name in [".git", ".gitignore", ".claude", "Makefile", "void"]:
            continue
        if f.is_dir():
            self.install_files(f, "usr/share/quickshell/utumno")
        else:
            self.install_file(f, "usr/share/quickshell/utumno")
    self.install_license("LICENSE")
