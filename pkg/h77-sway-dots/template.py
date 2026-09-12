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
#     own example-config.yml/test/full-conf-good.yml/laptop.conf
#     (cloned fresh 2026-09-12), not guessed -- but never actually run
#     through yambar itself (not installed on the dev host). Validate on
#     first real boot.
#   - `udiskie` IS real in cports (`user` repo tier, confirmed
#     2026-09-12 -- corrects an earlier wrong "doesn't exist" note) and
#     is what's actually used for auto-mount (`exec udiskie -a` in
#     sway/config, already present from the d77void source config
#     unmodified). yambar's `removables` module here is a secondary,
#     manual `udisksctl mount/unmount`-on-click display -- redundant
#     with udiskie for the common case, kept anyway as a visible/
#     clickable fallback. Both need h77-dots' 50-udisks.rules plus the
#     installing user in the `storage` group.

pkgname = "h77-sway-dots"
pkgver = "0.1.0"
pkgrel = 0
build_style = "meta"
pkgdesc = "hybrid-d77 sway session dotfiles (/etc/skel): sway, swaylock, swaync, yambar"
license = "MIT"
url = "https://github.com/dani-77/hybrid-d77"
depends = ["h77-dots"]


def install(self):
    self.install_files(self.template_path / "skel", "etc")
