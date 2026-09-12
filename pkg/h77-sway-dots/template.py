# hybrid-d77 :: sway-specific dotfiles, as a cports package.
#
# Sway/swaylock/swaync dotfiles: ~/d77void/sway/skel/.config/{sway,
# swaylock,swaync} (d77void already has its own "sway" variant -- this
# is the closest, most direct match in the family). yambar/config.yml is
# NEW, written from scratch for hybrid-d77 on 2026-09-12 -- yambar over
# waybar is the user's own choice on its own merits, NOT because waybar
# is unavailable: waybar exists in cports too (`user/waybar`, same tier
# as udiskie/greetd), confirmed 2026-09-12 late after an earlier pass
# here wrongly claimed it wasn't packaged at all -- corrects the exact
# main-vs-user mistake already made once this session, see docs/NOTES.md.
# Catppuccin-mocha palette kept in sync BY HAND
# between sway/catppuccin-mocha (sway's native `set $var` colors) and
# yambar/config.yml (plain hex, yambar can't read sway's variables).
#
# sway/config's own `bar { }` block (swaybar + status.sh) was replaced
# with a plain `exec yambar` -- see that file's own comment. status.sh
# is kept only as a reference for which values yambar's modules needed
# to cover.
#
# TODO not done yet:
#   - yambar's exact module fields were checked against dnkl/yambar's
#     own doc/*.scd (real, cloned from Codeberg -- GitHub doesn't
#     mirror this repo), not guessed -- confirmed working on a real
#     boot (2026-09-12 evening).
#
# 2026-09-12 evening, user request: the bar's `network`/`removables`
# modules (visual ethernet/udisk display) swapped for `cpu`/`mem`
# instead -- real auto-mount (`udiskie -a`, exec'd from sway/config,
# unmodified from d77void) and real networking (NetworkManager) are
# UNCHANGED, this only touches what the bar itself shows. `cpu`'s
# `id < 0` condition is the module's own convention for "total across
# all cores" (confirmed against yambar-modules-cpu.5.scd); `mem`'s
# `percent_used` is a native tag, no computation needed.

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
