<p align="center">
  <img src="assets/logo.png" width="128" alt="hybrid-d77 logo">
</p>

<h1 align="center">hybrid-d77</h1>

<p align="center">Chimera Linux · <b>Sway</b> + yambar · <b>dinit</b> — live ISO (chimera-live).</p>

---

## Why this shape

- [Chimera Linux](https://chimera-linux.org/) pairs a Linux kernel with a
  BSD userland (FreeBSD's `chimerautils`) and `apk` (the same package
  *format* as Alpine, a different, incompatible `apk-tools` build and
  build system, **cports**/`cbuild`). The "hybrid" in the name is that: a
  genuine hybrid of the BSD and Linux worlds, not just a marketing word.
- Named deliberately **without** "chimera" in it — unlike the rest of the
  d77 family (`d77void`, `d77arch`, ...), this one is meant to reach
  people outside personal/internal use, and staying clear of the base
  distro's own name avoids a repeat of `d77void` staying permanently tied
  to Void's name (also a real trademark-policy concern, not just taste).
- Init is **dinit**, not OpenRC/systemd/s6 like the rest of the family —
  per-package dinit service files ship as `<pkg>-dinit` subpackages
  (`greetd-dinit`, `udiskie-dinit`, `networkmanager-dinit`, ...).
- **yambar**, not waybar — a deliberate choice, not a limitation: waybar
  exists in cports too (`user/waybar`, same repo tier as udiskie/greetd).
- No greeter/display-manager, even though `greetd` is packaged — Void's
  and Chimera's own convention: a plain `getty` `login:` prompt, with
  `/etc/motd` documenting the credentials, straight into Sway via
  `.profile` once logged in. `anon`/`chimera` + `root`/`chimera` are left
  as Chimera's own default, same pattern as Void's `anon`/`voidlinux` —
  no custom user-creation logic.

## Layout

```
vendor/chimera-live/          vendored fork of chimera-linux/chimera-live
                               (mklive.sh/mklive-image.sh, the mkimage.sh
                               equivalent) -- GPLv3 as a whole, see its own
                               COPYING.md. Patched with a "sway" case in
                               mklive-image.sh, every package name verified
                               against the real repo (main + user tiers).
pkg/h77-dots/                  general app dotfiles (/etc/skel): foot,
                               alacritty, kitty, qt5ct/qt6ct, Kvantum,
                               the wallpaper, 50-udisks.rules, motd
pkg/h77-sway-dots/              sway/swaylock/swaync/yambar dotfiles
                               (/etc/skel), depends = ["h77-dots"]
iso/mklive-d77.sh              wrapper around vendor/chimera-live/mklive.sh,
                               builds the "sway" variant (main + user repos)
container/                     Containerfile + entrypoint -- builds an ISO
                               via sudo podman, FROM Chimera's own official
                               container image (Alpine's apk-tools can't
                               read Chimera's package format at all)
docs/NOTES.md                  field notes -- read before touching the build
```

## Status

The live ISO pipeline works end to end: an official, unmodified upstream
GNOME ISO and a sway-variant test ISO have both been built (via
`container/`) and booted from USB. What's left is building `h77-dots`/
`h77-sway-dots` as real `.apk` packages through a `cports`/`cbuild`
toolchain bootstrap, so a sway ISO ships the real d77 skel instead of
upstream defaults — see `docs/NOTES.md` for the full field notes and
current blockers.

The disk-installer side is explicitly **not** in scope yet — the goal
right now is a consistent, working **live** ISO first.

## Reference / inspiration (not vendored, just studied)

- [chimera-install-scripts](https://github.com/chimera-linux/chimera-install-scripts) —
  `chimera-installer`/`chimera-chroot`, for whenever the installer side
  gets built.
- [cports](https://github.com/chimera-linux/cports) — the package
  collection itself; every package name referenced here has been
  verified against it (both the `main` and `user` repo tiers).

## Not affiliated with the Chimera Linux project.
