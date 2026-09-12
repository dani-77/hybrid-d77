# hybrid-d77

The d77 desktop (Sway + Waybar) on [Chimera Linux](https://chimera-linux.org/)
-- BSD userland (FreeBSD's), Linux kernel, `apk` package manager, `dinit`
init. The "hybrid" in the name is that: a genuine hybrid of the BSD and
Linux worlds, not just a marketing word.

Named deliberately without "chimera" in it -- unlike the rest of the d77
family (`d77void`, `d77arch`, ...), this one is meant to reach people
outside personal/internal use, and staying clear of the base distro's own
name in the product name avoids a repeat of `d77void` being permanently
tied to Void's name.

**Status: early scaffolding, not buildable yet.** See `docs/NOTES.md` for
what's actually been figured out so far and `docs/TODO.md` (once it
exists) for the concrete next steps.

## Layout

- `vendor/chimera-live/` -- vendored fork of
  [chimera-linux/chimera-live](https://github.com/chimera-linux/chimera-live)
  (image-creation tooling, the `mklive.sh`/`mklive-image.sh` equivalent
  of Alpine's `mkimage.sh`). GPLv3 as a whole (see its own `COPYING.md`).
- `pkg/d77-sway-skel/` -- the d77 desktop config as a
  [cports](https://github.com/chimera-linux/cports) package
  (`template.py`), same role as d77alpine's `pkg/d77-sway-skel/APKBUILD`.
- `iso/mklive-d77.sh` -- wrapper around `vendor/chimera-live/mklive.sh`,
  modeled on their own `mklive-image.sh`.
- `docs/NOTES.md` -- field notes, read before touching the build.

## Reference / inspiration (not vendored, just studied)

- [chimera-install-scripts](https://github.com/chimera-linux/chimera-install-scripts) --
  `chimera-installer`/`chimera-chroot`, for whenever the installer side
  of this gets built.
- [cports](https://github.com/chimera-linux/cports) -- the package
  collection itself; also where `pkg/d77-sway-skel`'s real dependency
  names need verifying against.
