# hybrid-d77 :: niri session dotfiles, the niri variant's counterpart to
# h77-sway-dots. niri itself is only the compositor here: bar,
# launcher, lock screen, power menu, wallpaper picker and OSD all come
# from Utumno (the user's own Quickshell shell, pkg/utumno), driven by
# keybinds through qsd77 (pkg/qsd77).
#
# config.kdl + d77/*.kdl adapted from the user's own working niri +
# quickshell-d77 setup (2026-09-25): qsd77 calls retargeted at Utumno
# (`-c utumno`), the dashboard bind dropped (Utumno has none),
# volume/brightness keys routed through Utumno's OSD IPC instead of
# bare amixer/brightnessctl, terminal alacritty -> foot (the terminal
# both variants actually ship), dms-only includes dropped.
# swaync (config copied verbatim from h77-sway-dots -- nothing in it
# is sway-specific) added 2026-09-25 as the notification daemon, since
# Utumno has none; Mod+N toggles its panel (no bar button for it here).
# swayidle added the same day: auto-lock on idle/before sleep through
# Utumno's own lock screen (`qsd77 locker -c utumno`), same timings as
# the sway variant's swayidle+swaylock.
#
# Ships its own /etc/skel/.profile and README.md, same paths as
# h77-sway-dots -- the two are alternative sessions, one per ISO, never
# meant to be installed together.
pkgname = "h77-niri-dots"
pkgver = "0.1.0"
pkgrel = 0
build_style = "meta"
depends = ["h77-dots", "h77-welcome", "qsd77", "utumno"]
pkgdesc = "Niri session dotfiles for hybrid-d77"
license = "custom:meta"
url = "https://github.com/dani-77/hybrid-d77"
# Same reasoning as h77-dots: we genuinely install straight into
# /etc/skel, cbuild's lint needs that acknowledged explicitly.
options = ["etcfiles"]


def install(self):
    self.install_files(self.template_path / "skel", "etc")
