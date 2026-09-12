# hybrid-d77 :: general app dotfiles (not sway-specific), as a cports
# package. Installed to /etc/skel like d77alpine's d77-sway-skel, but
# split apart here per the user's own plan (2026-09-12): app dotfiles
# with no WM-specific content live here, sway's own config lives in the
# sibling h77-sway-dots package instead.
#
# Sources (all read-only references, copied in on 2026-09-12):
#   - alacritty, kitty, qt5ct, qt6ct, Kvantum: ~/d77void/common/config/
#   - foot: ~/d77devuan/pkg/d77-sway-skel/skel/.config/foot
#     (d77void has no foot config of its own; Devuan's was the closest
#     match, foot being the sway-family terminal of choice there too)
#   - backgrounds/d77.png (the wallpaper): ~/d77devuan/pkg/d77-sway-skel/
#     skel/.config/backgrounds -- referenced by h77-sway-dots' sway
#     config via `output * bg ~/.config/backgrounds/d77.png fill`, so it
#     lives in the always-installed h77-dots rather than the sway-only
#     package -- any future non-sway variant gets the same wallpaper too.
#   - files/50-udisks.rules: ~/d77void/common/50-udisks.rules (the same
#     rule ported to obarun/arch/devuan/alpine earlier this project --
#     grants org.freedesktop.udisks(2).* to the `storage` group. Needed
#     even though Chimera DOES have real udiskie (confirmed 2026-09-12,
#     under the `user` repo tier -- an earlier pass here wrongly said it
#     didn't exist, only checked `main`) -- `udiskie -a`'s non-interactive
#     auto-mount fails NotAuthorized without this rule, same as every
#     other d77 variant.
#   - files/motd: shown at login, documents the anon/chimera and
#     root/chimera credentials -- no greeter needed (see h77-sway-dots'
#     .profile for the reasoning: Void's and Chimera's own convention,
#     the user's own call, even though greetd IS packaged here too).
#
# TODO not done yet:
#   - `storage` group: needs creating + the installing user added to it,
#     same as every other distro in this family -- belongs in the
#     mklive-image.sh sway variant's own setup, not here (this package
#     doesn't run anything at install time, `build_style = "meta"`).
#   - whether the `anon` user (and root's `chimera` password) need
#     explicit creation by this project, or already exist by Chimera's
#     own convention on official images -- not yet verified against
#     an actual boot, taking the user's word for it for now.

pkgname = "h77-dots"
pkgver = "0.1.0"
pkgrel = 0
build_style = "meta"
pkgdesc = "General app dotfiles for hybrid-d77"
license = "custom:meta"
url = "https://github.com/dani-77/hybrid-d77"
# We genuinely install straight into /etc (skel content + motd), which
# cbuild's own lint flags by default ("'/etc' exists, verify if this
# is necessary and then set the 'etcfiles' option") -- confirmed the
# real syntax against real templates (main/zsh, main/mc, ...), it's a
# list of option names, not a dict/bool.
options = ["etcfiles"]


def install(self):
    # install_files(path, dest) copies path (a dir) to destdir/dest/<path's
    # own basename> -- since "skel" lives next to template.py (not under
    # any fetched source= tree, there is none here), pass an ABSOLUTE path
    # via template_path: pathlib's `/` operator ignores self.cwd entirely
    # once the right-hand side is already absolute, so this reliably
    # resolves to this package's own skel/ dir regardless of what self.cwd
    # would otherwise be for a source-less "meta" package. Verified
    # against cbuild's real source (src/cbuild/core/template.py), not
    # guessed -- see docs/NOTES.md.
    self.install_files(self.template_path / "skel", "etc")

    # cports' lint insists vendor-shipped polkit rules go under
    # /usr/share, not /etc (/etc/polkit-1/rules.d is meant for local
    # admin overrides) -- polkit itself reads both dirs, so this is a
    # pure packaging-convention fix, not a behavior change. Confirmed
    # against the real lint hook's own message, not guessed.
    self.install_file(
        self.files_path / "50-udisks.rules", "usr/share/polkit-1/rules.d"
    )
    self.install_file(self.files_path / "motd", "etc")
