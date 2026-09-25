<p align="center">
  <img src="assets/logo.png" width="128" alt="hybrid-d77 logo">
</p>

<h1 align="center">hybrid-d77</h1>

<p align="center">Chimera Linux · <b>Sway</b> + Waybar or <b>niri</b> + Utumno · <b>dinit</b> — live ISO + installer.</p>

---

## Variants

Two ISOs from the same tree, same base (Chimera, dinit, no greeter,
`h77-installer`, `h77-welcome`, `h77-update`, the same app set) --
only the session differs:

| | `sway` (default) | `niri` |
|---|---|---|
| Compositor | Sway | niri (scrollable tiling) |
| Bar | Waybar | [Utumno](https://github.com/dani-77/utumno) (Quickshell) |
| Launcher | wmenu / fuzzel | Utumno |
| Lock / power menu | swaylock / fuzzel-power-menu | Utumno |
| Notifications | swaync | -- |
| Wallpaper | `output * bg` | Utumno's picker (`~/Wallpaper`) + swaybg |
| Session dotfiles | `pkg/h77-sway-dots` | `pkg/h77-niri-dots` |
| ISO | `hybrid-d77-live-x86_64-DATE-sway.iso` | `hybrid-d77-live-x86_64-DATE-niri.iso` |

On niri, Utumno is driven by keybinds through
[qsd77](https://github.com/dani-77/qsd77) (`qsd77 launcher -c utumno`,
...); keybinds are listed in `~/README.md` on either variant, shown
by h77-welcome's "About" item.

## Why this shape

- [Chimera Linux](https://chimera-linux.org/) pairs a Linux kernel with a
  BSD userland (FreeBSD's `chimerautils`) and `apk` (the same package
  *format* as Alpine, a different, incompatible `apk-tools` build and
  build system, **cports**/`cbuild`). The "hybrid" in the name is that: a
  genuine hybrid of the BSD and Linux worlds, not just a marketing word.
- Named deliberately **without** "chimera" in it — unlike `d77void`
  (permanently tied to Void's own name), this one deliberately stays
  clear of the base distro's own name. Not just personal preference —
  there's a real trademark-policy concern too.
- Init is **dinit**, not systemd — per-package dinit service files ship
  as `<pkg>-dinit` subpackages (`greetd-dinit`, `udiskie-dinit`,
  `networkmanager-dinit`, ...), and not every service self-enables on
  install (`dbus`, `elogind` do; `polkit`, `networkmanager`, `seatd`,
  `rtkit`, `syslog-ng` don't) — see `docs/NOTES.md` for what that means
  for the installer.
- **Waybar**, ported from an existing, already-working sway config — an
  earlier yambar config was tried first and dropped after real bugs
  showed up on an actual boot (hardcoded battery name, unreliable
  refresh, the wireless display vanishing outright).
- A second variant, **niri**, uses [Utumno](https://github.com/dani-77/utumno)
  (Quickshell) as the whole shell -- bar, launcher, lock screen, power
  menu, wallpaper picker, OSD -- driven through
  [qsd77](https://github.com/dani-77/qsd77). Both are packaged here too.
- No greeter/display-manager, even though `greetd` is packaged — Void's
  and Chimera's own convention: a plain `getty` `login:` prompt, with
  `/etc/motd` documenting the credentials, straight into Sway (or niri) via
  `.profile` once logged in. `anon`/`chimera` + `root`/`chimera` are left
  as Chimera's own default, same pattern as Void's `anon`/`voidlinux` —
  no custom user-creation logic.

## Layout

```
vendor/chimera-live/          vendored fork of chimera-linux/chimera-live
                               (mklive.sh/mklive-image.sh, the mkimage.sh
                               equivalent) -- GPLv3 as a whole, see its own
                               COPYING.md. Patched with "sway" and "niri"
                               cases (sharing one common package list) in
                               mklive-image.sh (every package name verified
                               against the real repo, main + user tiers)
                               and a live-user group fix in initramfs-tools/
                               .../9990-chimera-user.sh.
vendor/chimera-install-scripts/ vendored fork of chimera-linux/
                               chimera-install-scripts -- chimera-installer/
                               chimera-bootstrap/chimera-chroot/genfstab.
                               chimera-installer itself is real patched (not
                               just wrapped): interactive Groups + Services
                               checklists, Partition + Filesystems (planning
                               and non-interactive execution split, mirrors
                               void-installer's own architecture), Network
                               (nmtui) and Keymap steps upstream doesn't
                               have at all, plus a couple of real upstream
                               bugs fixed (--keep-tite breaking every
                               screen's redraw; the "fetch latest version"
                               prompt silently discarding every patch here
                               -- now gated off via $SKIP_UPDATE_CHECK).
                               Packaged as pkg/h77-install-scripts, which
                               replaces the real chimera-install-scripts in
                               this project's own package set entirely. See
                               that package's own template.py for the full,
                               dated history of every patch.
pkg/h77-dots/                  general app dotfiles (/etc/skel): foot,
                               alacritty, qt6ct, Kvantum, gtk-2.0/3.0/4.0,
                               fuzzel + fuzzel-power-menu, the wallpaper,
                               50-udisks.rules, motd (+ a separate,
                               credential-free motd-installed the installer
                               swaps in after a real disk install),
                               h77-update (updates h77-* on an installed
                               system from the h77-pkgs GitHub Release)
pkg/h77-sway-dots/             sway/swaylock/swaync/waybar dotfiles
                               (/etc/skel), depends = ["h77-dots", "h77-welcome"];
                               also ships skel/README.md (credentials +
                               keybinds, shown by h77-welcome's "About" item)
pkg/h77-niri-dots/             niri config (/etc/skel) for the niri
                               variant: Utumno autostart, qsd77 keybinds,
                               own .profile + README.md; depends =
                               ["h77-dots", "h77-welcome", "qsd77", "utumno"]
pkg/utumno/                    Utumno (Quickshell shell), from its own
                               tagged release, to /usr/share/quickshell/utumno
pkg/qsd77/                     qsd77 (Go CLI for Utumno's IPC), from its
                               own tagged release
pkg/h77-welcome/               dialog(1) TUI welcome/installer helper,
                               autostarted by h77-sway-dots' sway config
                               (or h77-niri-dots' niri config)
                               (until its own "Don't show this again"),
                               offering Install (h77-installer) and Update
                               (h77-update) from one menu -- this project's
                               own equivalent of d77void's GTK d77-welcome,
                               reusing the `dialog` dependency already
                               needed by h77-installer instead of adding a
                               second GUI toolkit
pkg/h77-installer/             thin wrapper around h77-install-scripts' own
                               patched chimera-installer, pre-loaded with
                               this project's defaults (/etc/h77/
                               installer.conf); the old post-install
                               groups/services fix-up is now a manual-only
                               fallback, superseded by the real interactive
                               checklists patched into the installer itself
pkg/h77-install-scripts/       cports package for the patched
                               chimera-installer above (see vendor/
                               chimera-install-scripts/ entry)
.github/workflows/
  build-h77-pkgs.yml            builds every pkg/* via cbuild in CI and
                               publishes them as .apk files on a GitHub
                               Release (tag h77-pkgs) -- build once,
                               fetch/pin the release asset instead of
                               rebuilding from source every time
iso/mklive-d77.sh              wrapper around vendor/chimera-live/mklive.sh,
                               builds the "sway" (default) or "niri" variant
                               (main + user repos, plus this project's own
                               local package repo) as
                               iso/hybrid-d77-live-ARCH-DATE-VARIANT.iso
iso/fetch-pkgs.sh              downloads the latest h77-pkgs release
                               instead of rebuilding locally every time
container/                     Containerfile + entrypoint (builds the ISO)
                               and cbuild.Containerfile + cbuild-entrypoint.sh
                               (builds every pkg/* into real .apk files via
                               cports/cbuild) -- both via sudo podman, FROM
                               Chimera's own official container images
build.sh                       one command, whole pipeline (see Build below)
docs/NOTES.md                  field notes -- read before touching the build
```

## Build

Two containers, in order: `cbuild` builds every `pkg/*` (the `h77-*`
packages, plus `utumno` and `qsd77`) into real `.apk`
files (cbuild itself refuses to run as root); the ISO container then
consumes those and runs `mklive.sh` (needs root, for `mount(8)`).

### On a Chimera/hybrid-d77 host

`iso/mklive-d77.sh` is real Chimera's own `mklive.sh`, meant to run ON
Chimera -- no container needed at all when the host already is one. It
just needs a local apk repo at `cbuild-out/hybrid/` to pull this
project's own packages from, populated either way:

- **build it yourself**, via cports/`cbuild` (Chimera's own normal
  package build system, same role xbps-src plays for Void) --
  `container/cbuild-entrypoint.sh` is the exact, real recipe (clone
  cports, sync `pkg/*` in as a "hybrid" category -- with a
  `hybrid/.parent -> ../user` link, without which cbuild can't resolve
  any dependency outside `hybrid/` -- then `cbuild bootstrap` + `cbuild
  pkg` per package); run those same commands directly instead of
  through the container.
- **or fetch CI's already-built packages**: `./iso/fetch-pkgs.sh`.

Either way, then:

```sh
doas ./iso/mklive-d77.sh        # sway; needs root, for mount(8)
doas ./iso/mklive-d77.sh niri   # niri variant
```

### From any host (rootful container)

```
./build.sh          # both containers, in order -> iso/hybrid-d77-live-*-sway.iso
./build.sh niri     # same, niri variant    -> iso/hybrid-d77-live-*-niri.iso
```

Needs docker or `sudo podman` (rootless podman won't do the `mount(8)`
work the ISO half needs). Each step can also be run by hand instead,
same containers, same images:

```
sudo podman build -t hybrid-d77-cbuild -f container/cbuild.Containerfile .
sudo podman run --rm --privileged --security-opt label=disable \
    -v "$PWD:/src" -w /src hybrid-d77-cbuild

sudo podman build -t hybrid-d77-build -f container/Containerfile .
sudo podman run --rm --privileged --security-opt label=disable \
    -e VARIANT=sway -v "$PWD:/src" -w /src hybrid-d77-build   # or VARIANT=niri
```

Or skip the `cbuild` step entirely and pull the latest packages
already built by CI instead: `iso/fetch-pkgs.sh`, then just
the ISO half above.

### Writing the result to a USB drive

```
lsblk                                                   # confirm the device
sudo umount /run/media/$USER/* 2>/dev/null               # if auto-mounted
sudo dd if=iso/hybrid-d77-live-x86_64-*-sway.iso of=/dev/sdX \
    bs=4M status=progress conv=fsync && sync
```

## Status

Confirmed working end to end on real hardware (not just QEMU), including
the destructive disk-partitioning path: live boot → `doas h77-installer`
→ interactive Partition (cfdisk) + Filesystems (plan, then one
non-interactive format/mount pass, mirroring void-installer's own
`menu_filesystems`/`create_filesystems` split) → SystemRoot → Kernel →
Packages → Bootloader → Install, groups/services checklists applied,
installed-system motd swapped in, reboot into a working Sway/Waybar
desktop -- that's the sway variant. The niri variant (2026-09-25) is
newer: all its packages build and install cleanly, its niri config
passes `niri validate` on the real niri 26.04, and its ISO builds
end to end, but it hasn't been booted on real hardware yet. See
`docs/NOTES.md` for the full field notes, what's still open
(network-source installs, a couple of services worth double-checking),
and the reasoning behind every design call, including a few real bugs
found and fixed via actual hardware testing along the way.

## Reference / inspiration

- [chimera-install-scripts](https://github.com/chimera-linux/chimera-install-scripts) —
  forked and patched directly as `vendor/chimera-install-scripts/` /
  `pkg/h77-install-scripts` (see above), not just studied.
- [cports](https://github.com/chimera-linux/cports) — the package
  collection itself; every package name referenced here has been
  verified against it (both the `main` and `user` repo tiers).
- [niri](https://github.com/niri-wm/niri) and
  [Quickshell](https://quickshell.org) -- both straight from cports'
  `user` tier, not rebuilt here.
- [Utumno](https://github.com/dani-77/utumno) and
  [qsd77](https://github.com/dani-77/qsd77) -- the same author's own
  shell and its CLI, packaged here from their tagged releases
  (`pkg/utumno`, `pkg/qsd77`); their niri config is adapted from a
  working niri + quickshell-d77 setup.
- [void-mklive](https://github.com/void-linux/void-mklive) — `void-installer`'s
  own real architecture was the reference point for several patches: its
  Groups/Services checklists (things upstream chimera-installer doesn't
  have at all), and its `menu_filesystems`/`create_filesystems` split
  (planning is interactive, execution is one non-interactive pass) —
  re-read side by side with this project's own first attempt after that
  one didn't hold up on real hardware.

## License

This project's own original work (`pkg/*`, `container/`, `iso/`,
docs) is [MIT](LICENSE); Utumno and qsd77 themselves (fetched from
their own repos at build time, not vendored) are MIT too. The vendored subtrees under `vendor/` keep
their own upstream licenses in full — GPLv3 for `chimera-live`,
BSD-2-Clause for `chimera-install-scripts` — see each one's own
`COPYING.md`.

## Not affiliated with the Chimera Linux project.
