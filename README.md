<p align="center">
  <img src="assets/logo.png" width="128" alt="hybrid-d77 logo">
</p>

<h1 align="center">hybrid-d77</h1>

<p align="center">Chimera Linux · <b>Sway</b> + Waybar · <b>dinit</b> — live ISO + installer.</p>

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
  (`greetd-dinit`, `udiskie-dinit`, `networkmanager-dinit`, ...), and not
  every service self-enables on install (`dbus`, `elogind` do; `polkit`,
  `networkmanager`, `seatd`, `rtkit`, `syslog-ng` don't) — see
  `docs/NOTES.md` for what that means for the installer.
- **Waybar**, ported from this project's own d77devuan config — an
  earlier yambar config was tried first and dropped after real bugs
  showed up on an actual boot (hardcoded battery name, unreliable
  refresh, the wireless display vanishing outright).
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
                               mklive-image.sh (every package name verified
                               against the real repo, main + user tiers)
                               and a live-user group fix in initramfs-tools/
                               .../9990-chimera-user.sh.
pkg/h77-dots/                  general app dotfiles (/etc/skel): foot,
                               alacritty, kitty, qt5ct/qt6ct, Kvantum,
                               fuzzel + fuzzel-power-menu, the wallpaper,
                               50-udisks.rules, motd
pkg/h77-sway-dots/             sway/swaylock/swaync/waybar dotfiles
                               (/etc/skel), depends = ["h77-dots"]
pkg/h77-installer/             thin wrapper around Chimera's own real
                               chimera-installer, pre-loaded with this
                               project's defaults, plus a post-install
                               fix-up for groups/services chimera-installer
                               itself doesn't handle (see docs/NOTES.md)
iso/mklive-d77.sh              wrapper around vendor/chimera-live/mklive.sh,
                               builds the "sway" variant (main + user repos,
                               plus this project's own local package repo)
container/                     Containerfile + entrypoint (builds the ISO)
                               and cbuild.Containerfile + cbuild-entrypoint.sh
                               (builds pkg/h77-* into real .apk files via
                               cports/cbuild) -- both via sudo podman, FROM
                               Chimera's own official container images
docs/NOTES.md                  field notes -- read before touching the build
```

## Status

Confirmed working end to end, live boot through a real disk install: the
live ISO boots (tested on real hardware, not just QEMU), `doas
h77-installer` installs to disk using Chimera's own real
`chimera-installer`, and the installed system boots with Sway/Waybar
running. See `docs/NOTES.md` for the full field notes, what's still
rough (network-source installs, a couple of services worth double
-checking), and the reasoning behind each design call.

## Reference / inspiration (not vendored, just studied)

- [chimera-install-scripts](https://github.com/chimera-linux/chimera-install-scripts) —
  `chimera-installer`/`chimera-bootstrap`, which `pkg/h77-installer`
  wraps rather than replaces.
- [cports](https://github.com/chimera-linux/cports) — the package
  collection itself; every package name referenced here has been
  verified against it (both the `main` and `user` repo tiers).
- [void-mklive](https://github.com/void-linux/void-mklive) — `void-installer`'s
  own groups/services checklists were the reference point for figuring
  out what `chimera-installer` doesn't do.

## Not affiliated with the Chimera Linux project.
