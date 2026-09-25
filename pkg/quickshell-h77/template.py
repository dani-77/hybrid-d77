# hybrid-d77 :: Quickshell built WITH its Hyprland QML module. cports'
# own user/quickshell template (0.3.1), copied verbatim except for two
# configure flags: cports builds it with -DHYPRLAND=OFF and
# -DSCREENCOPY_HYPRLAND_TOPLEVEL=OFF (same as Void's package), which
# drops the Quickshell.Hyprland QML module entirely -- and Utumno's
# Bar.qml references WorkspacesHyprland (which imports it) directly in
# an inline Component, so the QML engine needs the module just to LOAD
# the bar, even on niri where that Loader branch never runs. Both flags
# removed here (they default to ON); the module is just IPC over
# Hyprland's socket, it doesn't need Hyprland itself installed.
#
# Its own name, not "quickshell" (user's call): under the same name,
# apk would silently swap it for cports' build on the first `apk
# upgrade` after a cports version bump, Hyprland module gone again. A
# different name is never replaced by apk on its own. It still ships
# the same files as cports' quickshell, so the two can't be installed
# together -- nothing here pulls cports' one in. Re-sync pkgver/sha256
# with cports' template by hand when upgrading.
pkgname = "quickshell-h77"
pkgver = "0.3.1"
pkgrel = 0
build_style = "cmake"
configure_args = [
    "-DDISTRIBUTOR=Chimera Linux",
    "-DINSTALL_QML_PREFIX=lib/qt6/qml",
    "-DUSE_JEMALLOC=OFF",
    "-DBUILD_TESTING=ON",
    # https://github.com/quickshell-mirror/quickshell/issues/491
    "-DNO_PCH=ON",
]
make_check_args = ["-E", "popupwindow"]
make_check_env = {"QT_QPA_PLATFORM": "offscreen"}
hostmakedepends = [
    "cmake",
    "ninja",
    "pkgconf",
    "qt6-qtshadertools",
    "spirv-tools",
    "wayland-progs",
]
makedepends = [
    "cli11",
    "cpptrace-devel",
    "glib-devel",
    "libdrm-devel",
    "libxcb-devel",
    "linux-pam-devel",
    "mesa-gbm-devel",
    "pipewire-devel",
    "polkit-devel",
    "qt6-qtbase-private-devel",
    "qt6-qtdeclarative-devel",
    "vulkan-headers",
    "wayland-devel",
    "wayland-protocols",
]
depends = ["qt6-qtsvg"]
pkgdesc = "QtQuick toolkit for desktop shells, with Hyprland module"
license = "LGPL-3.0-only"
url = "https://quickshell.org"
source = (
    f"https://git.outfoxxed.me/quickshell/quickshell/archive/v{pkgver}.tar.gz"
)
sha256 = "d60592622f1aa1cbb853d4814f605dfde827bc692befbfecffaccf4c90e352d8"
options = ["!cross"]


def post_install(self):
    self.install_license("LICENSE")
