# hybrid-d77 :: welcome/installer helper, as a cports package.
#
# 2026-09-24: this project's own equivalent of d77void's d77-welcome
# (~/d77void/common/x86_64/d77-welcome, a GTK3/python-gi app) -- same
# job (present a README.md, offer post-install actions from a menu),
# but shipped here as a plain dialog(1) TUI script instead of a GTK
# app. Reasons, not guessed:
#   - No greeter/display-manager in this project at all (see
#     h77-sway-dots' own .profile) -- a heavyweight GTK app is a much
#     bigger stretch from "plain getty login" than a TUI is.
#   - `dialog` is ALREADY a hard package dependency of the sway image
#     (vendor/chimera-live/mklive-image.sh's sway PKGS), specifically
#     so h77-installer's own "Before you start" notice can use it --
#     reusing it here needs zero new packages. gtk+3/python3-gobject
#     bindings are NOT already present (python-gobject IS in that same
#     PKGS list, but only the bare `gi` module for waybar's
#     mediaplayer.py -- no GTK typelib/widget bindings come with it).
#   - The actions this menu offers (`doas h77-installer`, `doas
#     h77-update`) are themselves plain terminal programs (chimera-
#     installer is an ncurses/dialog TUI, h77-update is a plain shell
#     script) -- launching them from inside a GTK window would need a
#     PrivilegedRunner-style askpass shim (see d77void's own
#     PrivilegedRunner class) just to bridge two toolkits; running them
#     straight in the same terminal window this menu already owns
#     needs none of that.
#
# Ships only files/h77-welcome -> /usr/bin. The README.md it displays
# (`About`) comes from h77-sway-dots' own skel/README.md (installed to
# ~/README.md, same as every d77void variant's own skel/README.md) --
# not shipped by this package, since its content is sway-specific
# (keybinds) and this package itself is meant to stay WM-agnostic for
# any future non-sway variant. The autostart wiring -- a drop-in
# ~/.config/sway/autostart.d/h77-welcome.conf, `include`d from
# sway/config, that this binary's own "Don't show this again" deletes
# outright (mirroring d77void's own trick of deleting ~/.auto.sh) --
# also lives in h77-sway-dots for the same reason: see that package's
# skel/.config/sway/{config,autostart.d/h77-welcome.conf}.

pkgname = "h77-welcome"
pkgver = "0.1.0"
pkgrel = 0
build_style = "meta"
pkgdesc = "Welcome/installer helper for hybrid-d77"
license = "custom:meta"
url = "https://github.com/dani-77/hybrid-d77"
# doas (opendoas, part of base-full-misc) and dialog (mklive-image.sh's
# sway PKGS) are both already hard requirements of the image itself --
# not re-declared here as depends=: same cbuild template-resolution
# limitation noted in h77-dots' own template.py (bash) and
# h77-installer's own (chimera-install-scripts), confirmed to apply to
# real `main`-category packages, not just guessed to apply here too.


def install(self):
    self.install_bin(self.files_path / "h77-welcome")
