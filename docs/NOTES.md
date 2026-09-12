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
