# hybrid-d77 :: qsd77, the user's own short CLI wrapper around
# `qs ipc call ...` for quickshell-d77 and Utumno
# (github.com/dani-77/qsd77). The niri variant's keybinds call it as
# `qsd77 <cmd> -c utumno` -- it targets quickshell-d77 by default,
# which this project doesn't ship. Needs `qs` at runtime: depends on
# quickshell-h77, this project's own Quickshell build (see there).
pkgname = "qsd77"
pkgver = "1.3.3"
pkgrel = 0
build_style = "go"
hostmakedepends = ["go"]
depends = ["quickshell-h77"]
pkgdesc = "Short CLI for controlling quickshell-d77 and Utumno"
license = "MIT"
url = "https://github.com/dani-77/qsd77"
source = f"{url}/archive/refs/tags/{pkgver}.tar.gz"
sha256 = "507508dfd0fd33aaf095ad75d454340dfec4db0a9824197345dfe08a8fd4c0d8"


def post_install(self):
    self.install_license("LICENSE")
