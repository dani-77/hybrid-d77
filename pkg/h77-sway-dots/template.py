# hybrid-d77 :: sway-specific dotfiles, as a cports package.
#
# Sway/swaylock/swaync dotfiles: ~/d77void/sway/skel/.config/{sway,
# swaylock,swaync} (d77void already has its own "sway" variant -- this
# is the closest, most direct match in the family). swaylock/config's
# own `image=~/Wallpaper/background2_locked.png` was broken as ported
# -- d77void keeps that image in a top-level ~/Wallpaper/ this project
# never creates. Fixed the way an existing, real sway config does it
# instead: the lock image lives IN .config/swaylock/ itself
# (background2_locked.png, copied in from that same source),
# `image=~/.config/swaylock/background2_locked.png`.
#
# waybar/*: an existing, real, working waybar config (itself
# originally ported from d77void), unmodified apart from the font
# (style.css: Hack Nerd Font, matching this project's own font choice
# -- see h77-dots' foot.ini).
#
# HISTORY, 2026-09-12: this package shipped a from-scratch yambar
# config first (waybar was wrongly believed unpackaged in cports at
# the time -- corrected same day, it's real, `user` tier). yambar
# turned out to have real bugs found on an actual boot: the battery
# module hardcoded BAT0 (breaks on any laptop reporting BAT1), values
# didn't refresh reliably, and the wireless network display vanished
# outright despite being configured -- all three confirmed on real
# hardware, not assumptions. Switched to waybar the same evening,
# which is what this file now describes; the yambar config and its own
# history are gone from this tree (git history has it, if ever needed
# again).
#
# sway/config's own `bar { }` block (swaybar + status.sh) is replaced
# with a plain `exec waybar` -- see that file's own comment. status.sh
# is kept only as a historical reference.

pkgname = "h77-sway-dots"
pkgver = "0.1.0"
pkgrel = 0
build_style = "meta"
pkgdesc = "Sway session dotfiles for hybrid-d77"
license = "custom:meta"
url = "https://github.com/dani-77/hybrid-d77"
depends = ["h77-dots"]
# Same reasoning as h77-dots: we genuinely install straight into
# /etc/skel, cbuild's lint needs that acknowledged explicitly.
options = ["etcfiles"]


def install(self):
    self.install_files(self.template_path / "skel", "etc")
