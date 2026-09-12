# hybrid-d77 :: field notes

## 2026-09-12 :: kickoff research

First session. No build attempted yet -- this is what came out of reading
`chimera-live` and `cports` before touching anything.

### The pieces

- **`vendor/chimera-live`** -- vendored fork of
  [chimera-linux/chimera-live](https://github.com/chimera-linux/chimera-live)
  (same pattern as d77obarun's vendored fork of `iso-builder/`). BSD-2-Clause,
  except `initramfs-tools/` which is Debian's live-boot project (GPLv3) --
  per their own `COPYING.md`, that makes the *whole* repo GPLv3 as a
  combined work. Keep `COPYING.md` intact.
- **`pkg/d77-sway-skel`** -- our own package, the equivalent of
  d77alpine's `pkg/d77-sway-skel/APKBUILD`. Chimera uses `apk` too (same
  package *format* as Alpine), but packages are built via **cports**
  ([chimera-linux/cports](https://github.com/chimera-linux/cports)), whose
  templates are **Python** (`template.py`), not abuild's shell
  `APKBUILD`s. Still scaffolding -- see the TODOs in the template itself.
- **`iso/mklive-d77.sh`** -- our wrapper, modeled on `chimera-live`'s own
  `mklive-image.sh` (`-b base|gnome|plasma`). Also scaffolding.

### How `chimera-live` actually works (vs. Alpine's `mkimage.sh`)

- `mklive.sh` is the direct equivalent of Alpine's `mkimage.sh`. Options:
  `-p PACKAGES` (package list), `-r REPO` (extra apk repo, repeatable),
  `-k DIR` (signing keys), `-c CMDLINE` (extra kernel cmdline), `-f FLAVOR`
  (name tag), `-s squashfs|erofs` (erofs is the default, not squashfs).
- `mklive-image.sh` is the high-level wrapper (our `iso/mkimg.d77.sh`
  equivalent): `-b IMAGE` picks a package set (`base`/`gnome`/`plasma`
  today), `-p` adds extra packages on top, everything else passes through
  to `mklive.sh`. Dead simple -- read it, it's ~50 lines.
- **There is no apkovl-equivalent.** Alpine's genapkovl mechanism (a
  separate live-only config overlay: hostname, world file, greetd
  config, live-user creation script, service enablement) has NO
  counterpart here. Whatever a live image needs (default user, autologin,
  session config, extra services) has to come from **packages themselves**
  -- e.g. a `gnome` package presumably ships its own gdm/autologin
  config as part of the package, not as a build-time overlay step. This
  means `d77-sway-skel` (or a sibling package) will likely need to own
  more of the "make it a live-friendly default install" logic than
  `d77-sway-skel` does on Alpine, where `genapkovl-d77.sh` carries a good
  chunk of it (`etc/local.d/d77-live.start`, the live `greetd.toml`'s
  `[initial_session]`, etc).
- **Init system is `dinit`**, not OpenRC or systemd. d77alpine's
  `*-openrc` subpackage pattern (e.g. `greetd-openrc`) has no direct
  translation -- need to find out how dinit service files are packaged
  and enabled in cports before `depends=` can be filled in for real.
- **Base filesystem is `erofs` by default** (not squashfs) -- `-s` flag
  exists if squashfs is ever needed, but no reason to override yet.
- **Live-boot mechanism**: a vendored/adapted copy of Debian's
  `live-boot`, driven via initramfs-tools hooks
  (`initramfs-tools/hooks/live`) reading `/etc/live/boot.conf` +
  `/etc/live/boot/*` -- this is the actual hook point for anything that
  needs to run at live boot (closest thing to genapkovl's
  `etc/local.d/d77-live.start`). Not yet explored in depth.

### `base-live` (the live meta-package) is NOT what it sounds like

`main/base-live/template.py` in cports is just a `build_style = "meta"`
package pulling in **bootloader + storage tooling for offline installs**
(grub variants per-arch, limine, systemd-boot, cryptsetup-scripts, lvm2)
-- nothing about live-session UX, autologin, or the desktop. Don't go
looking for autologin logic in there again.

### Package template shape (from real cports examples, fetched via GitHub)

```python
pkgname = "chimera-repo-user"
pkgver = "0.3"
pkgrel = 0
build_style = "meta"        # meta = no actual build step, just depends= + install()
depends = ["chimera-repo-main"]
pkgdesc = "..."
license = "custom:meta"
url = "https://chimera-linux.org"

def install(self):
    self.install_file(self.files_path / "some-file", "usr/lib/apk/repositories.d")

@subpackage("chimera-repo-user-debug")
def _(self):
    self.subdesc = "debug packages"
    self.depends = [self.parent]
    return ["usr/lib/apk/repositories.d/*-debug.list"]
```

`match self.profile().arch:` is used for arch-conditional `depends +=`
(seen in `base-live`'s real template, for per-arch bootloader packages).

### Not done yet / real next steps

1. Get a working local `cports` checkout + `cbuild` toolchain running at
   all (never done tonight -- unclear yet how heavy this is compared to
   abuild+`podman run`).
2. Confirm real cports package names for the desktop stack (sway, waybar,
   foot, mako, greetd-equivalent-or-not, polkit, seatd, NetworkManager,
   pipewire/wireplumber) -- the placeholder `depends=` in
   `pkg/d77-sway-skel/template.py` is *guessed*, not verified.
3. Work out the dinit service-enablement story (what does a dinit unit
   look like, how does a cports package ship+enable one, is there an
   `*-openrc`-equivalent subpackage convention).
4. Figure out where live-only bits belong: a `live-boot` hook script
   under `/etc/live/boot/` (or `etc/live/boot.conf` config), shipped by
   which package -- possibly `d77-sway-skel` itself, possibly a small
   dedicated `d77-live` package so `d77-sway-skel` stays installable on
   a normal (non-live) target too, same reasoning as d77alpine's own
   skel/apps split.
5. Only after 1-4: actually run `iso/mklive-d77.sh` for a first real ISO
   attempt.

Naming: the public-facing name is **hybrid-d77** deliberately, not
`d77chimera` -- see the memory file for why (Chimera's own name stays
out of the product name this time, learned from `d77void` staying
permanently tied to Void's name).

## 2026-09-12 evening :: official GNOME ISO built + written, real desktop packages scaffolded

### Official, unmodified GNOME live: built and confirmed working

Built via `container/` (Containerfile + entrypoint.sh + build.sh), through
`sudo podman`, using **Chimera's own official container image**
(`docker.io/chimeralinux/chimera:latest`) as the build host -- not a
custom Alpine-based container. Two real bugs found and fixed getting
there:

- Alpine's own `apk-tools` (edge) cannot read Chimera's repo/package
  format at all: `ERROR: ... ADB compression not supported`. Chimera
  ships a newer apk-tools 3.x with a binary "ADB" index/package format
  that's simply incompatible. Fix: don't fight it, build FROM Chimera's
  own container (it ships its own correct apk-tools) -- "usa o
  container deles, não reinventes a roda".
- The official Chimera container doesn't ship `mount(8)`, which
  `mklive.sh` calls directly against the host (not inside a chroot) to
  set up pseudo-filesystems: `./mklive.sh: mount: not found`. Fixed by
  `apk add --repository .../main util-linux-mount` in the Containerfile
  (the specific subpackage that provides `mount`, not a generic
  "util-linux" meta package).
- `mklive.sh` writes its output `.iso` into **the current working
  directory** (`vendor/chimera-live/` itself), *not* into the `build/`
  directory passed as an argument. `entrypoint.sh` originally looked in
  `build/*.iso` and silently produced nothing -- fixed to `cp *.iso`
  from the chimera-live dir.

Result: `chimera-linux-x86_64-LIVE-20260912-gnome.iso` (~1.93 GB),
written to `/dev/sdb` (Kingston DataTraveler USB) via `dd`, confirmed
0 errors. Proves the whole `chimera-live` pipeline works end to end on
this host before adapting anything.

### Real cbuild template API (confirmed against cbuild's own source)

Sparse-cloned `chimera-linux/cports` (`src/cbuild/core/template.py`) to
verify rather than guess:

- `self.install_files(path, dest, symlinks=True, name=None)` -- copies
  a directory `path` into `self.destdir / dest / (name or path.name)`.
  For a source-less `build_style = "meta"` package (no `source=` tree
  fetched, so `self.cwd` isn't meaningful), pass an **absolute** path
  via `self.template_path / "skel"` -- pathlib's `/` operator discards
  the left operand once the right side is already absolute, so this
  reliably resolves to the package's own directory regardless of `cwd`.
- `self.install_file(src, dest, mode=0o644, name=None, glob=False)` --
  single file, `dest` is a directory.
- `self.install_dir(dest, mode=0o755)`.
- `self.files_path = self.template_path / "files"`.
- `pre_install`/`install`/`post_install` are **build-time-only**
  template phases (part of building the `.apk` on the build machine),
  NOT a target-system `apk add`-time hook. The only real install-time
  hook mechanism is `triggers` (directory-path-watch, not unconditional
  like Alpine's `.trigger`) -- not needed here in the end.

### Repo tier correction: `main` vs `user`

First pass wrongly concluded `udiskie`, `greetd`, and `libseat-seatd`
didn't exist in cports at all, based on `apk search` against `main`
only. **User caught this** ("podes ver no cports como trata o
chimera") -- searched the actual GitHub repo directly and found all of
them real, just filed under the separate **`user`** repo tier
(community-maintained, cports' equivalent of Alpine's
community/AUR): `user/greetd/template.py`, `user/udiskie/template.py`,
etc. `mklive.sh`'s own default repo (`--repository .../current/main`)
only applies when **no** `-r` flag is given at all -- passing any `-r`
disables the default entirely, so once `user` is needed, `main` has to
be passed explicitly too, or it's silently dropped.

### Argument-order bug in mklive-image.sh -> mklive.sh forwarding

`mklive-image.sh`'s own `getopts` consumes only its own flags then
forwards its leftover `"$@"` verbatim onto `mklive.sh -p ... -f ...
"$@"`. `mklive.sh`'s own `getopts` stops parsing at the first non-flag
word (the `build` dir argument) -- so any `-r`/`-k` meant for
`mklive.sh` has to be placed **before** `build` in the outer
`mklive-image.sh` invocation, or it lands as a stray positional arg
instead of a real option. Fixed in `iso/mklive-d77.sh`:
`./mklive-image.sh -b sway -- -r <main> -r <user> build "$@"`.

### The real desktop packages: h77-dots / h77-sway-dots / sway variant

Per the user's own 3-part plan, split into:

1. **`pkg/h77-dots`** -- general app dotfiles (foot, alacritty, kitty,
   qt5ct/qt6ct, Kvantum), `50-udisks.rules`, `motd`, and
   `backgrounds/d77.png` (the wallpaper, sourced from d77devuan so any
   future non-sway variant gets it too), installed to `/etc/skel`.
   Sources: `~/d77void/common/config/*` and `~/d77devuan/pkg/
   d77-sway-skel/skel/.config/{foot,backgrounds}` (read-only
   references -- the d77void-exception applies here since this is a
   *different* repo).
2. **`pkg/h77-sway-dots`** -- sway/swaylock/swaync dotfiles (from
   `~/d77void/sway/skel/.config/*`, closest match in the family) plus a
   brand-new `yambar/config.yml`, `depends = ["h77-dots"]`. **Correction
   2026-09-12 late, prompted by the user asking me to re-check**: waybar
   is NOT actually missing from cports -- it exists as `user/waybar`,
   same tier as udiskie/greetd. The original "waybar isn't packaged"
   claim repeated the exact main-vs-user mistake already made once this
   session (see the repo-tier correction below) and was wrong. yambar
   stays -- the user's explicit call once this was pointed out -- but
   for its own merits, not because waybar is unavailable.
   `sway/config`'s `bar {}` block replaced with `exec
   yambar`; wallpaper line fixed to `~/.config/backgrounds/d77.png`.
   `.profile` (not `.bash_profile` -- Chimera's default shell is plain
   `/bin/sh`) execs `sway` on tty1 when no Wayland/X session is active.
3. **`mklive-image.sh`'s new `sway)` case** -- every package name
   individually verified against the real repo (not guessed): sway +
   family (swaybg/swaylock/swayidle), yambar, foot, elogind,
   libseat-seatd(-dinit), dbus(-dinit), polkit(-dinit),
   networkmanager(-dinit), pipewire/wireplumber/pavucontrol,
   xdg-desktop-portal(-wlr), udisks/udiskie(-dinit), plus our own
   `h77-dots h77-sway-dots`.

### Login design: plain TTY, no greeter -- final, user-decided

`greetd` genuinely exists in cports (`user` tier: `greetd`,
`greetd-dinit`, `greetd-man`) but is **deliberately not used**. User's
explicit call, several messages converging on this: Void's and
Chimera's own convention is a plain `getty` `login:` prompt +
`/etc/motd` documenting credentials, autologin into a shell that execs
sway via `.profile`. User/root and passwords are left as **Chimera's
own default** (`anon`/`chimera`, `root`/`chimera`, same pattern as
Void's `anon`/`voidlinux`) -- explicitly: build no custom user-creation
logic, trust that convention. `udiskie -a` (already present, unmodified,
in the inherited sway config) handles real auto-mount; `motd` documents
both credential pairs.

### Still open

- **`h77-dots`/`h77-sway-dots` are template.py + skel content only --
  not built `.apk` files.** Needs a real `cports`/`cbuild` toolchain
  bootstrap, not attempted yet. This is the actual next blocker for a
  fully-our-own live image.
- `storage` group creation (needed for udiskie's polkit rule to grant
  anything) -- not yet wired anywhere; belongs in the sway variant's
  own live-setup, not in either meta-package (neither has an
  install-time hook).
- Whether `anon`/`chimera` truly is Chimera's shipped default (vs.
  something to provision ourselves) -- taking the user's word for it,
  not yet confirmed against an actual boot.
- Disk-installer work is explicitly **deferred** -- "o trabalho de
  instalar deixamos para depois". Current scope is the live ISO only.

## 2026-09-12 late evening :: disk-installer, first slice

Live ISO confirmed working on real hardware (a physical boot photo,
Toshiba laptop) -- wallpaper, yambar bar, fuzzel launcher with
foot/foot-client/foot-server/volume-control/yambar all indexed. That
unblocked starting the installer side.

### chimera-installer/chimera-bootstrap, verified against real source

A ChatGPT suggestion prompted fetching and reading the actual
`chimera-linux/chimera-install-scripts` source (`chimera-installer`,
`chimera-bootstrap`) rather than taking the summary on faith. It
checked out accurate on every specific claim:

- `chimera-installer -c CONF`: real flag. `config_load()` reads any
  `INSTALL_CONFIG_*` line from that file straight into the
  environment; `config_get`/`config_set` auto-prefix with
  `INSTALL_CONFIG_` when reading/writing. So a config file with
  `INSTALL_CONFIG_PACKAGES="..."` is the real, correct mechanism.
- `menu_packages()` stores into `PACKAGES` (via `config_set_answer`),
  read later as `extrapkgs` and `apk add`ed into the target.
- `chimera-bootstrap -l "$sysroot"` (local) vs `chimera-bootstrap
  "$sysroot"` (network) -- exact, `chimera-installer`'s own source at
  the bootstrap-invocation point.
- `useradd -R "$sysroot" -m ...` runs AFTER the extra-packages apk-add
  step, confirming a package's `/etc/skel` content really does reach
  the new user's home with zero manual `cp -r`.

**The one thing worth getting precisely right, missed on a first pass
and corrected after the user pointed back at the local-source part of
the original answer**: `chimera-bootstrap`'s LOCAL mode
(`INSTALL_LOCAL=1`, which is `chimera-installer`'s own DEFAULT unless
the Source menu is changed) does NOT apk-install anything for the base
system. It does a **plain `tar` copy** of
`/run/live/rootfs/filesystem.*` (the live's own mounted erofs/squashfs
root) straight into the target:

```sh
tar -cf - -C "$INSTALL_LOCAL_PATH" . | tar -xpf - -C "$ROOT_DIR"
```

No apk, no network, no repo reachability needed for anything already
part of the live's own package set -- which includes `h77-dots`/
`h77-sway-dots` (and the kernel, and the bootloader packages from
`base-live`, and everything else in `mklive-image.sh`'s sway `PKGS`),
since they're installed on the live itself. This is the exact same
lesson d77alpine learned the hard way (copy the live literally instead
of re-installing via the package manager) -- except here it's already
built into upstream's own installer, natively.

The real, separate "extra packages" step (`menu_install`'s own
`apk add "$@"` via `chimera-chroot`) runs **unconditionally after the
bootstrap step, regardless of local vs network source** -- so
declaring `h77-dots`/`h77-sway-dots` in `INSTALL_CONFIG_PACKAGES`
would be actively wrong for local installs: they're already copied by
the tar step, and listing them again would force an avoidable
apk/network round-trip (which would also just fail outright with no
repo configured for our own local-only packages). `installer.conf`
therefore deliberately does NOT set `PACKAGES` at all.

### What got built

- **`pkg/h77-installer`** -- thin wrapper package. `files/
  installer.conf` (`INSTALL_CONFIG_SOURCE=local`,
  `INSTALL_CONFIG_KERNEL=stable`, `INSTALL_CONFIG_HOSTNAME=hybrid-d77`
  -- deliberately NOT `SystemRoot`/disk layout, that has to stay
  interactive, and deliberately NOT `PACKAGES`, see above) installed
  to `/etc/h77/installer.conf`; `files/h77-installer` (`exec
  chimera-installer -c /etc/h77/installer.conf "$@"`) installed to
  `/usr/bin`. NOT `depends = ["chimera-install-scripts"]` -- hit the
  exact same cbuild limitation as h77-dots' bash ("ERROR: template
  'chimera-install-scripts' cannot be resolved", even though the real
  `main/chimera-install-scripts/template.py` exists) -- listed
  directly in `mklive-image.sh`'s package set instead, same as bash.
- `mklive-image.sh`'s sway case: added `chimera-install-scripts` and
  `h77-dots h77-sway-dots h77-installer` (installer needs root --
  `doas h77-installer`, opendoas being Chimera's own default via
  `base-full-misc`, not `sudo` -- noted in `motd` now too).
- `container/cbuild-entrypoint.sh` generalized from a hardcoded
  two-package list to a loop over `H77_PKGS="h77-dots h77-sway-dots
  h77-installer"` -- adding a future package now only needs a name
  added there and to `mklive-image.sh`'s own list.
- Same `pkgdesc` lint rules bit again on the first pass (must start
  uppercase, <=72 chars, no parenthetical subdescription) -- fixed
  before even trying a build this time, now that the pattern is known.

### Still open

- Network-source installs need someone to fill in `Packages` by hand
  in the menu (nothing pre-fills that path yet) -- out of scope for
  this first slice, local-source (the default, from the live USB
  itself) is what's actually been built for.
- Not yet tested on a real install run (booted + actually walked
  through `doas h77-installer` to a disk) -- the ISO build succeeding
  and the package resolving is as far as this got tonight.
- `SystemRoot`/partitioning remains fully interactive, by design --
  nothing here attempts to guess a target machine's disk layout.

### Implemented later the same night: publish h77-dots/h77-sway-dots/h77-installer as a GitHub Release

Done: `.github/workflows/build-h77-pkgs.yml` (mirrors d77crux-live's
own `build-kernel.yml` almost line for line -- checkout, build the
container, run it `--privileged` since GitHub-hosted runners are full
VMs and allow that, publish to a fixed `h77-pkgs` release tag,
deleting+recreating it if it already exists, same as d77crux-kernel
does per-version) + `iso/fetch-pkgs.sh` (mirrors `scripts/
fetch-kernel.sh`: `gh release download`, verify `SHA256SUMS`, populate
exactly what `iso/mklive-d77.sh` already expects --
`cbuild-out/hybrid/x86_64/` + `cbuild-out/*.rsa.pub`). Triggers on
`workflow_dispatch` or a push touching `pkg/**`.

**Confirmed working end to end** after three real failures, each fixed
by an actual CI run, not guessed:
1. `--privileged` on the container alone wasn't enough --
   `ubuntu-latest` runners are Ubuntu 24.04, which restricts
   unprivileged user namespace creation via an AppArmor policy at the
   HOST kernel level (a property of the runner VM, not something a
   container flag overrides from inside). Fixed with `sudo sysctl -w
   kernel.apparmor_restrict_unprivileged_userns=0` on the runner,
   before building.
2. `mkdir: /src/cbuild-out: Permission denied` -- the container's
   `builder` user is a fixed uid 1000 (chosen to match a local dev
   host's own uid by convention), but the GH Actions runner's own
   checkout is owned by a different uid, so 1000 couldn't create a new
   directory there. Fixed by pre-creating `cbuild-out` and `chown -R
   1000:1000` before running the container.
3. `SHA256SUMS: Permission denied` in the very next step -- the fix
   above left `cbuild-out` owned by 1000, so the runner's own user
   (running the Checksum step) couldn't write into it either. Fixed by
   `chown`ing it back to the runner's own uid right after the
   container exits.

First real run published `h77-pkgs` cleanly: all three `.apk`s,
`APKINDEX.tar.gz`, the signing pubkey, `SHA256SUMS`. `gh release view
h77-pkgs --repo dani-77/hybrid-d77` confirms it.

### Original note (superseded by the above, kept for context)

User's own idea, same pattern already proven in `d77crux-live` for
`d77crux-kernel` -- confirmed by reading `d77crux-live/scripts/
fetch-kernel.sh`: a GitHub Actions workflow in the `d77crux` repo
builds the kernel and publishes it as a release asset (`.pkg.tar.xz` +
`.sha256`); the remaster's own `fetch-kernel.sh` does `gh release
download` before assembling the ISO, instead of compiling locally
every time.

Applied here, this would solve two things at once:
- Skip re-running `container/cbuild.Containerfile` (bootstrap + build,
  ~2-3 min) every session -- a `fetch-pkgs.sh` downloads the latest
  release's `.apk`s + `APKINDEX.tar.gz` into `cbuild-out/hybrid/`
  before `iso/mklive-d77.sh` runs.
- Give network-source `chimera-installer` installs a real repo to
  reach for `h77-dots`/`h77-sway-dots`/`h77-installer` (currently only
  local-source installs get them, via `chimera-bootstrap -l`'s tar
  copy of the live's own rootfs) -- if the release's files are also
  served from a stable URL (e.g. GitHub Pages), that closes the
  network-source gap noted above.

Not started -- explicitly parked ("Anotado para já") while finishing
the current ISO build/test.

## 2026-09-12 night :: real disk install confirmed, then a real gap

`doas h77-installer` on the previous ISO installed cleanly to a real
disk on the first try. Immediately hit the exact gap flagged as open
in the section above: NetworkManager had no permissions (same root
cause as the live's own `anon` user, but chimera-installer's own
target user this time) -- confirmed via `doas dinitctl enable
networkmanager` needing to be run by hand.

### void-installer comparison, verified against its real source

User asked to check how Void's own `void-installer`
(`void-linux/void-mklive`) handles groups/services, since
`chimera-installer` clearly doesn't. It has two things
`chimera-installer` has neither of:

- **Groups** (`menu_useraccount`): an interactive checklist built from
  the LIVE's own `/etc/group` (filtering out gid>=1000 and known
  system groups), pre-checked with a fixed default (`wheel,audio,
  video,floppy,cdrom,optical,kvm,users,xbuilder`), user-adjustable,
  then a single `useradd -m -G "$USERGROUPS" ...` in the target.
- **Services** (`menu_services`): an interactive checklist built from
  the TARGET's own `/etc/sv/*` (whatever packages actually installed),
  pre-checked for whatever's already runit-enabled by package triggers,
  `enable_service()`/`disable_service()` being a plain `ln -sf`/`rm -f`
  into `runsvdir/default` -- runit's version of the same boot.d symlink
  convention dinit uses.

`chimera-installer`, confirmed by re-reading its real source with this
question in mind: `usermod -a -G wheel` is the ONLY group it ever
touches, and there is not one single dinit/service-related line
anywhere in the whole script.

### install_service(enable=True): which dinit services self-enable

Before writing the fix-up, checked which packages in our own list
actually need it, rather than assuming all of them do -- confirmed
against cbuild's own `install_service()` source
(`src/cbuild/core/template.py`): passing `enable=True` bakes a symlink
directly INTO the package itself, at `usr/lib/dinit.d/boot.d/<name>`
-- meaning the service self-enables on ANY system that installs that
package, live or target, no action needed from us. Checked every
relevant package's real template:

- **Self-enabling already** (`enable=True`, confirmed): `dbus`
  (`dbus-daemon` + `dbus-daemon.user`), `elogind` (`elogind`).
- **NOT self-enabling** (confirmed, needs a manual `/etc/dinit.d/
  boot.d/` symlink on the actual system -- the same thing
  `9990-chimera-user.sh` already does for the LIVE user, now needed
  for the INSTALLED target too): `polkit` (service `polkitd`),
  `networkmanager` (service `networkmanager`), `libseat` (subpackage
  `libseat-seatd`, service `seatd`), `rtkit` (service `rtkit`),
  `syslog-ng` (service `syslog-ng`).
- `udiskie`'s service is `udiskie.user` (a PER-USER dinit service, a
  different directory tree, `usr/lib/dinit.d/user/`) -- not relevant
  here, we already start it per-session via sway's own `exec udiskie
  -a`, not as a system service.

**Important, and easy to get wrong**: none of this carries over from
the live via `chimera-bootstrap -l`'s local tar-copy, even for
services `9990-chimera-user.sh` DOES enable on the live (rtkit,
polkitd, syslog-ng, networkmanager-or-dhcpcd). That script's own
symlinks land in the live's writable overlay at boot time, not in the
read-only `/run/live/rootfs/filesystem.*` image that the local
bootstrap actually copies from -- so the installed target starts with
NONE of those enabled, same as a from-scratch chimera-installer run
would. Every one of them has to be enabled again, explicitly, for the
target.

### What got built: files/post-install

`h77-installer` no longer `exec`s `chimera-installer` (that would
replace the whole process, nothing could run afterward) -- it runs it
normally, then calls `files/post-install <sysroot>` (installed to
`/usr/lib/h77-installer/post-install`) if `$SYSROOT` (default
`/mnt/root`, chimera-installer's own suggested default; overridable as
`h77-installer`'s first argument if a different SystemRoot was typed
in the menu) looks like a real completed install (`mountpoint -q` +
`etc/passwd` exists). It:

1. Finds the one user chimera-installer created (the single real
   subdirectory under `$SYSROOT/home` -- confirmed chimera-installer
   only ever creates exactly one), `usermod -aG
   network,storage,audio,video` it in the target chroot.
2. Symlinks `polkitd`/`networkmanager`/`seatd`/`rtkit`/`syslog-ng` into
   `$SYSROOT/etc/dinit.d/boot.d/` -- but only for whichever of those
   are actually present under `$SYSROOT/usr/lib/dinit.d/`, so this
   stays correct even if the package set changes later.

No interactive checklist, unlike Void -- matches this project's own
established taste (hardcode what's already known, don't ask a menu
what the answer already is), and the user's explicit steer this
session ("Post install hook").

### Still open

- Not yet re-tested against a real disk install end to end (only that
  it builds and the logic reads correctly) -- next real boot should
  confirm `networkmanager`/`polkitd`/`seatd` all come up enabled
  without a manual `dinitctl enable`.
- `rtkit` and `syslog-ng` are enabled unconditionally if present, even
  though neither is explicitly in `mklive-image.sh`'s own PKGS list --
  they're pulled in transitively (base-full-misc, elsewhere) and DO
  show up in a real build, but that's incidental, not declared. Worth
  reconsidering once the package list is revisited.
- Network-source installs still don't get `PACKAGES` filled in
  automatically, and the post-install fix-up only helps AFTER
  chimera-installer's own user-creation step, not during it.

## 2026-09-12 night :: back to waybar -- yambar had real bugs

After a successful real disk install and boot, three real problems
surfaced with the yambar config that shipped up to this point (all
observed on actual hardware, not assumed):

1. The `battery` module hardcoded `BAT0`. Any laptop reporting
   `BAT1` instead (not rare) gets nothing.
2. Values didn't refresh reliably.
3. The wireless network display stopped showing anything at all,
   despite the module being configured and previously confirmed
   against yambar's own real docs -- static documentation isn't the
   same as tested runtime behavior, and this was never actually run
   through yambar before shipping it (flagged as an open TODO earlier
   in this file, and it caught up).

User's call: drop yambar, go back to waybar using this project's own
real, already-working d77devuan config (`pkg/d77-sway-skel/skel/
.config/waybar`) instead of hand-writing a new one. Ported as directly
as reasonable:

- `config`/`style.css`/`d77.css`/`mediaplayer.py`/`wittr.sh` copied
  over unmodified except the font (`style.css`: `Hack Nerd Font`,
  matching this project's own choice for foot -- see `fonts-nerd-hack`
  below) and header comments.
- `sway/config`'s `exec yambar` -> `exec waybar`.
- `pkg/h77-sway-dots/skel/.config/yambar/` removed entirely (git
  history has it if ever needed again).

Real cports package names, verified, added to `mklive-image.sh`'s sway
`PKGS`:

- `waybar` (`user` tier, 0.15.0 -- confirmed real via its own real
  template.py, `-Dpulseaudio=enabled -Dmpris=enabled -Dlogind=enabled`
  among its build flags, so the ported config's `pulseaudio`/
  `sway/*`/`battery`/`network` modules all have what they need).
- `fonts-nerd-hack` (`user` tier, a subpackage of `user/fonts-nerd`) --
  a SEPARATE package from `fonts-hack-ttf` (`main`, used by foot):
  plain Hack has no icon glyphs, the nerd-fonts-patched variant is a
  different package entirely. Confirmed the exact subpackage name
  (`fonts-nerd-{package}`, `package="hack"`) by reading the real
  template.
- `playerctl` + `python-gobject` (both `main`) -- `mediaplayer.py`'s
  real runtime deps (MPRIS via playerctl, plus the `gi` Python module
  it imports; the Debian-only `gir1.2-playerctl-2.0`/`python3-gi-cairo`
  split doesn't apply here).
- `curl` (`main`) -- `wittr.sh`'s only dependency.
- `firefox` (`main`) -- user request, added alongside this batch.

Not yet rebuilt/tested against a real boot at the time of writing --
next step.

## 2026-09-12 night, later :: full app-bundle cross-check against d77void

User's framing: the ISO so far is a proof of concept, a lot of a real
desktop app bundle is still missing. Directed to cross-check against
d77void's own real sway variant instead of guessing a list from
scratch -- read `mkd77.sh`'s `sway)` case, `D77_CORE` (the shared app
bundle across all d77void variants), and the functions `COMMON=yes`/
`FUZZEL=yes` actually call (`include_common` -> `_include_base`,
`include_fuzzel`) to get the REAL list, not just the `PKGS=` line.

Verified every candidate against a full, non-truncated listing of
cports' real `main` (2387 dirs) and `user` (851 dirs) trees, fetched
via the git trees API (`gh api .../git/trees/<sha>`, recursion via
each dir's own sha) rather than the paginated contents endpoint (which
silently caps at 1000) or one `gh search code` call per package (hits
GitHub's search rate limit fast).

**User's own examples confirmed exactly right**: `arc-theme` genuinely
absent, `breeze-gtk` (`main`) is the real substitute; `pcmanfm`
absent, `thunar` (`user`) instead; `geary` absent, `thunderbird`
(`main`) instead; `qt5ct` absent, only `qt6ct` (`main`) + `kvantum`
(already had) exist.

**Found independently, real functional gaps**: `swaync` was configured
(skel + `exec swaync` already in sway/config) but the package itself
was NEVER added to `mklive-image.sh`'s `PKGS` -- silently broken.
`mate-polkit` (`main`) -- a polkit AUTHENTICATION AGENT, distinct from
`polkitd` the daemon -- was missing entirely; without one, no GUI app
can ever prompt for a password no matter what else is enabled. Also:
`swaylock/config`'s `image=~/Wallpaper/background2_locked.png` pointed
at a top-level `~/Wallpaper/` dir this project never creates (a
d77void-ism, not ported correctly the first time) -- fixed the way
d77devuan's own real config does it: the lock image lives inside
`.config/swaylock/` itself, copied in from d77devuan's own
`pkg/d77-sway-skel`, `image=~/.config/swaylock/background2_locked.png`.

**Confirmed genuinely absent, no substitute added** (checked, not
assumed): `alsa-tools`, `cups-browsed`, `plymouth` (no boot-splash
pipeline exists here anyway), `pulseaudio-utils` (pipewire's own pulse
compat already covers this), `qt5-wayland`/`qt6-wayland` (Qt's own
Wayland platform plugin is bundled into qt5-base/qt6-base already,
nothing separate to add), `ranger`, `uget`, `nerd-fonts-symbols-ttf`,
`nwg-launchers` (not needed, fuzzel is the launcher). `xarchiver`
absent too -- `file-roller` (`main`) used instead, a better fit
alongside `thunar` anyway (same GTK/GNOME ecosystem). `wget` -> the
real package is `wget2`. `ImageMagick` -> lowercase `imagemagick`
(case-sensitive).

**Everything added to `mklive-image.sh`'s sway `PKGS`, all confirmed
real** (main unless noted): `swayimg`, `swaync` (user), `wmenu`
(sway/config already sets `$menu wmenu-run`), `cliphist` (user),
`wlsunset` (user), `xwayland-satellite` (user), `fonts-font-awesome-otf`,
`playerctl`+`python-gobject` (already had, waybar's mediaplayer.py),
`wget2`, `thunderbird`, `mate-polkit`, `power-profiles-daemon`,
`alsa-utils` (user), `xdg-desktop-portal-gtk`, `xdg-user-dirs`(+`-gtk`),
`xdg-utils`, `qt6ct`, `kvantum` (already had), `breeze-gtk`, `nwg-look`
(user), `papirus-icon-theme`, `thunar` (user), `file-roller`, `acpi`,
`bash-completion`, `bc-gh`, `cmus`, `cups`, `system-config-printer`,
`fastfetch`, `feh` (user), `gettext`, `htop`, `inxi`, `imagemagick`,
`mousepad` (user), `mpv`, `musl-locales`, `nano`, `smartmontools`,
`transmission` (user), `ufw`, `unzip`, `usbutils`, `vim`, `yt-dlp`,
`zathura`+`zathura-pdf-poppler` (user), `gnome-calculator`.

New config dirs ported into `pkg/h77-dots/skel/.config/` from
`~/d77void/common/config/` (the ones `_include_base` actually copies
that are relevant to apps now in our own list): `gtk-2.0`, `gtk-3.0`,
`gtk-4.0` (theme name fixed Arc-Dark -> Breeze-Dark), `cmus`,
`fastfetch`, `htop`, `mimeapps.list`, `pavucontrol.ini`. Dropped
`qt5ct` and `kitty` skel dirs entirely -- dead config for packages
that don't exist/were never installed, the same class of bug `swaync`
turned out to be, just caught proactively this time instead of by
accident.

Not yet rebuilt/tested against a real boot at the time of writing --
this is a large batch, next step is a full rebuild + real-hardware
check.

### Noted for later: repo visibility, and a more integrated groups/services flow

- **Visibility**: `h77-pkgs`-fetching via `gh release download` (both
  `iso/fetch-pkgs.sh` and the CI workflow itself) works fine on a
  PRIVATE repo, since both authenticate (the user's own `gh` login, or
  the Action's own `GITHUB_TOKEN`). It would need to go PUBLIC only
  for consumers that can't authenticate -- someone else's machine
  running `fetch-pkgs.sh` without `gh` logged in, or a network-source
  `chimera-installer` install doing a plain `apk add` against a real
  HTTPS repo URL (closing the network-source gap noted earlier). Given
  this project's own stated goal (reach people beyond personal use,
  unlike the rest of the d77 family), going public makes sense
  eventually -- user's own call on timing, not done yet.
- **Groups/services, a more integrated version**: DONE, same night,
  right after this was written -- user asked directly: "consegues
  fazer o patch do chimera-installer para ter isso sem quebrar?".

## 2026-09-12 night, later still :: chimera-installer patched directly for real groups/services

Vendored `chimera-install-scripts` (`vendor/chimera-install-scripts/`,
same pattern as `chimera-live`: real upstream source, gh api fetch of
`chimera-installer`/`chimera-bootstrap`/`chimera-chroot`/`genfstab`/
`COPYING.md`, pinned to the exact commit cports' own
`chimera-install-scripts-0.6.1` template builds from). Patched
`chimera-installer` itself with two ADDITIVE features, modeled
directly on `void-installer`'s own real structure (verified against
its source, not guessed):

- **Groups**: a checklist appended to the end of `menu_user_account()`
  -- built from the LIVE's own `/etc/group` (system groups filtered by
  gid/name, same filter shape as void-installer's), preset
  `wheel,network,storage,audio,video`, freely adjustable, stored as
  `USERGROUPS`. The actual `useradd`/`usermod` block later in
  `menu_install` uses it if set, falling back to the EXACT original
  upstream `-a -G wheel` behavior if it's unset (dialog cancelled, or
  an old config) -- so this can't regress the existing flow.
- **Services**: a NEW `menu_hybrid_services()`, called from
  `menu_install` right after bootloader install (same placement
  void-installer uses for its own `menu_services`, right after
  `set_bootloader` -- by this point real package/service files exist
  on `$sysroot` to check for). Deliberately NOT a scan of every file
  under `usr/lib/dinit.d/` -- unlike a runit `/etc/sv/<name>/`
  directory, a flat dinit service file doesn't reliably say "this is a
  real standalone service, safe to toggle" vs. an internal/dependency
  -only one. Sticks to the same small, individually-verified-real
  candidate list `h77-installer`'s own post-install script already
  used: `polkitd`, `networkmanager`, `seatd`, `rtkit`, `syslog-ng`
  (only offered if the package is actually on target), all preset ON,
  enabling via the same `/etc/dinit.d/boot.d/` symlink convention used
  everywhere else in this project.

New package **`pkg/h77-install-scripts`** ships the four patched
scripts (`install_bin` each, real `cbuild` API, not guessed) +
`COPYING.md` (`install_license`, BSD-2-Clause carried over unmodified)
-- replaces the real `chimera-install-scripts` package entirely in
`mklive-image.sh`'s PKGS (removed there, `h77-install-scripts` added
instead; `dialog` added explicitly since it was previously pulled in
transitively via the real package's own `depends=`). NOT
`depends=["cmd:apk!apk-tools", ...]` the way upstream's own
template.py declares them -- same `cbuild` "depends= needs a local
template" limitation hit repeatedly this session; every one of those
real deps is already in this project's own package set except
`dialog`.

**`h77-installer` simplified back to a plain `exec`** now that the
interactive checklists exist: the old always-run post-install fix-up
would have silently re-applied its own defaults even over an explicit
uncheck in the new dialogs, a real correctness conflict once both
existed. `files/post-install` stays installed as a manual-only
fallback (network-source installs, or reapplying by hand), header
comment updated to say so plainly.

Not yet tested against a real interactive install run (dialog
checklists behave correctly on paper, verified against real
`ui_dialog`/`config_get`/`config_set` conventions already used
elsewhere in the same file, but never actually clicked through) --
next real disk install should confirm both checklists render and
apply correctly.

## 2026-09-13 :: post-milestone theming cleanup, vim -> neovim

User confirmed the patched installer ISO worked end to end, then
asked for a few small follow-ups:

- **Kvantum**: `kvantum.kvconfig`'s `theme=` was `KvArcDark` -- a real
  bug, but INHERITED from d77void's own source, not introduced here
  (checked: their own `Kvantum/` dir only ever shipped
  `catppuccin-mocha-blue` too, `KvArcDark` never existed on either
  side). Fixed to `theme=catppuccin-mocha-blue`, the only theme this
  project actually ships.
- **gtk-cursor-theme-name**: was `whiteglass` (Void's own choice) --
  confirmed genuinely absent from cports (no cursor-theme package at
  all, `main` or `user`), dropped entirely from `gtk-3.0`/`gtk-4.0`
  rather than left pointing at nothing.
- **gtk-icon-theme-name** (`Papirus-Dark`) and **gtk-theme-name**
  (`Breeze-Dark`, already fixed earlier) both double-checked against
  the real upstream sources cports builds from (papirus-icon-theme's
  own `Makefile`/`install.sh`: `EXTRA_THEMES="Papirus-Dark
  Papirus-Light"` by default; user directly confirmed Breeze-Dark) --
  both correct as shipped.
- **qt6ct.conf's `color_scheme_path`** still points at the stock
  `airy.conf` rather than the shipped `catppuccin-mocha-blue.conf` --
  checked, this exactly matches d77void's own real config (not a
  mismatch introduced here), left alone since it wasn't what was
  asked and isn't a new bug.
- **vim -> neovim**: real package, `user` tier, user's own request.

Not yet rebuilt/tested against a real boot at the time of writing.
