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

### Noted for later: publish h77-dots/h77-sway-dots/h77-installer as a GitHub Release

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
