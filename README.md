# hybrid-d77

The d77 desktop (Sway + [yambar](https://codeberg.org/dnkl/yambar)) on
[Chimera Linux](https://chimera-linux.org/) -- BSD userland (FreeBSD's),
Linux kernel, `apk` package manager, `dinit` init. The "hybrid" in the
name is that: a genuine hybrid of the BSD and Linux worlds, not just a
marketing word.

yambar over waybar is a deliberate choice, not because waybar is
unavailable -- it exists in cports too (`user/waybar`). yambar was
picked on its own merits.

Named deliberately without "chimera" in it -- unlike the rest of the d77
family (`d77void`, `d77arch`, ...), this one is meant to reach people
outside personal/internal use, and staying clear of the base distro's own
name in the product name avoids a repeat of `d77void` being permanently
tied to Void's name.

**Status: live ISO pipeline works end to end.** An official, unmodified
upstream GNOME ISO and a sway-variant test ISO (see below) have both been
built and booted from a USB. The remaining piece is building `h77-dots`/
`h77-sway-dots` as real `.apk` packages via a `cports`/`cbuild`
toolchain bootstrap, so a sway ISO can ship the real d77 skel instead of
upstream defaults. See `docs/NOTES.md` for the full field notes, and the
Layout section below for what's here.

## Layout

- `vendor/chimera-live/` -- vendored fork of
  [chimera-linux/chimera-live](https://github.com/chimera-linux/chimera-live)
  (image-creation tooling, the `mklive.sh`/`mklive-image.sh` equivalent
  of Alpine's `mkimage.sh`). GPLv3 as a whole (see its own `COPYING.md`).
  Patched with a new `sway` case in `mklive-image.sh` (every package name
  individually verified against the real cports repo).
- `pkg/h77-dots/` -- general app dotfiles (foot, alacritty, kitty,
  qt5ct/qt6ct, Kvantum), `50-udisks.rules`, `motd`, and the wallpaper --
  as a [cports](https://github.com/chimera-linux/cports) package
  (`template.py`), installed to `/etc/skel`.
- `pkg/h77-sway-dots/` -- sway/swaylock/swaync/yambar dotfiles, also
  installed to `/etc/skel`, `depends = ["h77-dots"]`.
- `iso/mklive-d77.sh` -- wrapper around `vendor/chimera-live/mklive.sh`,
  builds the `sway` variant with both the `main` and `user` cports repos
  enabled (the latter needed for udiskie/greetd/libseat-seatd).
- `container/` -- Containerfile + entrypoint for building an ISO via
  `sudo podman`, FROM Chimera's own official container image (Alpine's
  own apk-tools can't read Chimera's package format at all).
- `docs/NOTES.md` -- field notes, read before touching the build.

## Reference / inspiration (not vendored, just studied)

- [chimera-install-scripts](https://github.com/chimera-linux/chimera-install-scripts) --
  `chimera-installer`/`chimera-chroot`, for whenever the installer side
  of this gets built (explicitly deferred for now).
- [cports](https://github.com/chimera-linux/cports) -- the package
  collection itself; also where every package name referenced here has
  been verified against (both the `main` and `user` repo tiers).
