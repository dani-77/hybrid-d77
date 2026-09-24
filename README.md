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
pkg/h77-welcome/               dialog(1) TUI welcome/installer helper,
                               autostarted by h77-sway-dots' sway config
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
  build-h77-pkgs.yml            builds every pkg/h77-* via cbuild in CI and
                               publishes them as .apk files on a GitHub
                               Release (tag h77-pkgs) -- build once,
                               fetch/pin the release asset instead of
                               rebuilding from source every time
iso/mklive-d77.sh              wrapper around vendor/chimera-live/mklive.sh,
                               builds the "sway" variant (main + user repos,
                               plus this project's own local package repo)
iso/fetch-pkgs.sh              downloads the latest h77-pkgs release
                               instead of rebuilding locally every time
container/                     Containerfile + entrypoint (builds the ISO)
                               and cbuild.Containerfile + cbuild-entrypoint.sh
                               (builds pkg/h77-* into real .apk files via
                               cports/cbuild) -- both via sudo podman, FROM
                               Chimera's own official container images
build.sh                       one command, whole pipeline (see Build below)
docs/NOTES.md                  field notes -- read before touching the build
```

## Build

Two containers, in order: `cbuild` builds `pkg/h77-*` into real `.apk`
files (cbuild itself refuses to run as root); the ISO container then
consumes those and runs `mklive.sh` (needs root, for `mount(8)`).

### On a Chimera/hybrid-d77 host

`iso/mklive-d77.sh` is real Chimera's own `mklive.sh`, meant to run ON
Chimera -- no container needed at all when the host already is one. It
just needs a local apk repo at `cbuild-out/hybrid/` to pull `h77-*`
from, populated either way:

- **build it yourself**, via cports/`cbuild` (Chimera's own normal
  package build system, same role xbps-src plays for Void) --
  `container/cbuild-entrypoint.sh` is the exact, real recipe (clone
  cports, sync `pkg/h77-*` in as a "hybrid" category, `cbuild
  bootstrap` + `cbuild pkg` per package); run those same commands
  directly instead of through the container.
- **or fetch CI's already-built packages**: `./iso/fetch-pkgs.sh`.

Either way, then:

```sh
doas ./iso/mklive-d77.sh   # needs root, for mount(8)
```

### From any host (rootful container)

```
./build.sh          # both containers, in order -> iso/*.iso
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
    -v "$PWD:/src" -w /src hybrid-d77-build
```

Or skip the `cbuild` step entirely and pull the latest `h77-*`
packages already built by CI instead: `iso/fetch-pkgs.sh`, then just
the ISO half above.

### Writing the result to a USB drive

```
lsblk                                                   # confirm the device
sudo umount /run/media/$USER/* 2>/dev/null               # if auto-mounted
sudo dd if=iso/chimera-linux-x86_64-LIVE-*.iso of=/dev/sdX \
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
desktop. See `docs/NOTES.md` for the full field notes, what's still open
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
- [void-mklive](https://github.com/void-linux/void-mklive) — `void-installer`'s
  own real architecture was the reference point for several patches: its
  Groups/Services checklists (things upstream chimera-installer doesn't
  have at all), and its `menu_filesystems`/`create_filesystems` split
  (planning is interactive, execution is one non-interactive pass) —
  re-read side by side with this project's own first attempt after that
  one didn't hold up on real hardware.

## License

This project's own original work (`pkg/h77-*`, `container/`, `iso/`,
docs) is [MIT](LICENSE). The vendored subtrees under `vendor/` keep
their own upstream licenses in full — GPLv3 for `chimera-live`,
BSD-2-Clause for `chimera-install-scripts` — see each one's own
`COPYING.md`.

## Not affiliated with the Chimera Linux project.
