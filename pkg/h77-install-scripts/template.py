# hybrid-d77 :: patched fork of chimera-install-scripts, as a cports
# package. Replaces the real `chimera-install-scripts` (`main` tier)
# in this project's own package set -- same scripts, same license,
# same behavior for anyone who doesn't touch the new bits, plus two
# real gaps closed that upstream simply doesn't have at all (confirmed
# against its actual source, not assumed):
#
#   1. No group selection whatsoever -- the installed user only ever
#      gets added to "wheel", hardcoded.
#   2. No services step at all -- unlike Void's own void-installer,
#      which has a real interactive checklist for both groups AND
#      services (github.com/void-linux/void-mklive, installer.sh).
#
# User's own call, after using h77-installer's earlier post-install
# fix-up hook (pkg/h77-installer/files/post-install) successfully on a
# real disk install and then asking for this instead: patch
# chimera-installer directly, the same way vendor/chimera-live's own
# 9990-chimera-user.sh was already patched, rather than bolting
# something on afterward. Both additions are deliberately ADDITIVE and
# fail safe -- cancel either new dialog and the exact original
# upstream behavior applies unchanged (wheel-only groups; no services
# step ran). See the patches' own header comments in
# files/chimera-installer for the full reasoning, including why the
# services checklist sticks to a small, individually-verified-real
# candidate list instead of scanning every file under
# usr/lib/dinit.d/ (that directory also holds internal/dependency-only
# entries with no reliable way to tell them apart from real standalone
# services).
#
# 2026-09-13: three more real gaps closed, same "check against
# void-installer's real source, delegate to a real tool instead of
# reimplementing" principle -- disk partitioning (menu_hybrid_partition,
# pure cfdisk delegation, no custom partition-table code, same as
# void-installer's own menu_partitions), a filesystem/mountpoint
# assignment + format/mount step (menu_hybrid_filesystems, a close
# port of void-installer's own menu_filesystems + create_filesystems
# -- DESTRUCTIVE, every format is behind its own explicit
# per-partition confirmation naming the device), network configuration
# (menu_hybrid_network, delegates to NetworkManager's own real nmtui),
# and console keymap selection (menu_hybrid_keymap, confirmed Chimera's
# own patched console-setup uses the exact same KMAP= convention
# void-installer already assumes, no translation needed). Caught one
# real bashism this way, not guessed: `done < <(sort ...)` (process
# substitution) doesn't parse under chimerautils' own /bin/sh --
# confirmed by running `sh -n` with /bin/sh being real dash on the dev
# host, same POSIX-strict class of shell -- fixed to a real temp file.
#
# Same day, user report ("não é só nesse menu... é em todos"): EVERY
# screen in the installer, not just package-install progress, showed
# visual artifacts making it look frozen. Root cause, confirmed
# against dialog's own real upstream source/CHANGES: ui_dialog(), the
# universal wrapper every single menu goes through, hardcoded
# --keep-tite on every call -- which disables dialog's normal
# alternate-screen redraw (the same mechanism vim/htop/less use), so
# nothing ever got cleared between screens. Removed from ui_dialog(),
# kept only on ui_programbox (its real, deliberate purpose there: keep
# the install log in the terminal's own scrollback).
#
# Real ISO test (Toshiba), user report: Keymap immediately errored
# "no keymaps found ... is kbd installed?". kbd WAS installed
# (confirmed: base-full-console -> console-setup -> kbd, all real
# deps), the path was wrong -- menu_hybrid_keymap ported Void's own
# /usr/share/kbd/keymaps without checking it against Chimera's real
# kbd package layout first. Re-read kbd's actual template.py: its own
# post_install uninstalls unwanted keymap sets from
# "usr/share/keymaps/{sun,amiga,...}" -- Chimera's real path is
# /usr/share/keymaps, no "kbd/" component. Fixed.
#
# Same test round, two more real bugs (screenshots): the Filesystems
# partition picker showed a literal "?" for every single entry, and
# separately SystemRoot failed right after ("the system root is
# invalid") even though Filesystems had just formatted+mounted /mnt/
# root. Root-caused for real (not guessed) by running lsblk locally
# with the exact same flags: `lsblk -pno NAME,TYPE` on a disk with
# more than one partition prefixes the NAME column with tree-drawing
# glyphs by default (e.g. "└─/dev/sda1", confirmed via a real `lsblk
# -pno NAME,TYPE` run on a multi-partition disk) -- that corrupted
# string is what menu_hybrid_filesystems's loop was storing as
# $_hd77_part. Two real consequences from the ONE root cause: (1)
# `lsblk -no SIZE "└─/dev/sda1"` fails outright ("não é um
# dispositivo de bloco" / not a block device), so $_hd77_size came
# back empty every time -> the "?" fallback; (2) the corrupted path
# is what got written into HD77_FS_FILE and later handed to mkfs/
# mount, so those failed silently against a nonexistent device name
# too, meaning /mnt/root was never actually mounted by the time
# SystemRoot's own `mountpoint -q` check ran. Fixed by adding `-l`
# (list mode, confirmed via a real side-by-side lsblk run: disables
# the tree formatting, plain "/dev/sda1") to that one lsblk call --
# menu_hybrid_partition's own disk-level `lsblk -dno NAME,TYPE` needed
# no change, confirmed disks never get a tree prefix (nothing above
# them to draw a branch from). Also dropped --no-tags from the
# partition-picker ui_dialog call itself: with it, dialog only ever
# shows the item column (the size, or now-fixed "?"), never the tag
# (the actual device path) -- so even with the size bug fixed, the
# user would still have had no way to tell partitions apart by
# device. User's own real-hardware report: "Assim não dá para
# perceber."
#
# Same round, cosmetic per user request: every dialog's --backtitle/
# --title said "Chimera Linux installer" (upstream's own string,
# never changed by any patch so far) -- renamed throughout to "Hybrid
# D77 installer".
#
# 2026-09-13, later the same day: real hardware re-test (Toshiba,
# after the lsblk -l fix above) still failed -- Filesystems reported
# "no partition was assigned to /" even after the user completed the
# full cycle correctly (ext4, "/", Yes to format, confirmed directly
# by the user, not assumed). Added heavier diagnostics first (an
# explicit "Recorded: ..." confirmation dialog after each partition
# entry, reading back from HD77_FS_FILE itself rather than trusting
# the in-memory variables, plus dumping the file's raw content into
# the final error dialog) to try to catch the real cause. Verified via
# a real chroot into this project's own built ISO (mounting its erofs
# live filesystem directly, bind-mounting a writable dir in for /tmp)
# that Chimera's actual grep (BSD grep, GNU-compatible) and actual
# /bin/sh both run the exact write-and-check sequence correctly --
# ruled out as the cause, not guessed.
#
# User's own call at that point, invoking the explicit fallback agreed
# earlier ("se não perceberes como fazer no chimera retrocede e deixa
# só a rede que está a funcionar correta"): REVERTED
# menu_hybrid_partition and menu_hybrid_filesystems entirely -- the
# custom cfdisk-delegation + format/mount checklist never worked
# reliably on real hardware despite passing every offline/chroot
# simulation, and destructive disk operations aren't something to
# leave half-understood. Partition and Filesystems removed from the
# top-level menu and the MENU_DEFAULT_ITEM chain (UserAccount now
# leads straight to SystemRoot again, matching pristine upstream's own
# order exactly -- confirmed against the real upstream source at the
# pinned commit). SystemRoot itself was NEVER modified by either
# patch (it's pure unmodified upstream, manual path entry + its own
# `mountpoint -q` validation) so no changes were needed there -- the
# expectation going forward is the same as plain upstream
# chimera-installer: partition and format the disk by hand (cfdisk +
# mkfs + mount, e.g. from a second TTY) before running the installer,
# exactly like the real, official Chimera installation docs describe.
# Network (menu_hybrid_network, real NetworkManager nmtui) and Keymap
# (menu_hybrid_keymap, the /usr/share/keymaps fix) both tested working
# on the same real hardware and were kept, per the user's own explicit
# confirmation ("a rede ficou bem").
#
# Same day, user report: Groups/Services checklists (untouched by any
# of the above -- confirmed via `git diff`, not guessed) appeared
# "desligados" (turned off) on a later test. Root cause, found by the
# user directly: upstream chimera-installer's own very first screen
# asks to fetch-and-run the latest version from
# raw.githubusercontent.com/chimera-linux/chimera-install-scripts --
# answering yes re-execs into that PRISTINE, unpatched copy for the
# rest of the run, silently discarding every patch here (Groups,
# Services, the reminder, the title, all of it). This script itself
# was never touched for that -- upstream already gates the whole
# prompt behind $SKIP_UPDATE_CHECK (skipped if non-empty, confirmed in
# its own source). Fixed in the one place that actually needed it:
# h77-installer's own wrapper now `export SKIP_UPDATE_CHECK=1` before
# exec'ing chimera-installer, so our own patches can never be silently
# replaced by vanilla upstream mid-run.
#
# Same day, user request: h77-dots' live /etc/motd (login credentials
# + "doas h77-installer" instructions) makes no sense once actually
# installed to disk. menu_install now copies h77-dots' own
# usr/share/h77/motd-installed (a short, generic, credential-free
# welcome -- see h77-dots' own template.py) over $sysroot/etc/motd as
# the last real step, right after the services checklist (packages are
# already on $sysroot by then, so the source file exists to copy);
# falls back to just deleting the live motd if that file isn't there
# for any reason.
#
# Same day, later: Partition and Filesystems RESTORED, rewritten to
# actually mirror void-installer's own real architecture this time
# instead of approximating it. Re-read void's real source side by
# side with ours (github.com/void-linux/void-mklive, installer.sh):
# its own menu_filesystems does ZERO disk I/O -- only records the plan
# into a config file, pure planning; the actual mkfs/mount only
# happens in a separate function, create_filesystems, called once,
# non-interactively, immediately before the real install begins (no
# gap between formatting/mounting and using that mount). void's
# TARGETDIR is also a fixed constant (/mnt/target) with no equivalent
# of chimera's own separate, validated SystemRoot step.
#
# menu_hybrid_filesystems now keeps that same split: the interactive
# loop only records into HD77_FS_FILE (plus a "Recorded: ..."
# diagnostic confirmation per entry, and a raw-file dump on the final
# validation error -- kept from the diagnostic pass added right before
# the original revert, since real proof beats guessing if this ever
# breaks again). Once "Done" is picked, ONE consolidated confirmation
# shows the whole plan (replacing the earlier per-partition yes/no,
# closer to void's own single "are you sure" framing), then mkfs/mount
# runs as one non-interactive pass mirroring create_filesystems
# exactly -- no more dialogs mid-execution.
#
# Target path changed from /mnt/root to plain /mnt -- user's own real,
# proven manual install convention (mount root directly at /mnt,
# strip that prefix by hand when needed), raised as a concern before
# implementing this. Checked genfstab's own real source first: it
# strips whatever ROOT_PATH actually is via a generic
# `${target#$ROOT_PATH}`, no "/mnt" hardcoded anywhere, so either path
# works identically as far as this project's tooling goes -- matching
# the user's own convention removes any doubt rather than leaving it
# untested. Upstream menu_sysroot's own "/mnt/root" fallback default
# text is untouched (real upstream default, confirmed against the
# pristine source at the pinned commit) -- it only matters if SYSROOT
# was never set, i.e. Partition/Filesystems were skipped entirely and
# SystemRoot is being filled in by hand instead.
#
# Source: github.com/chimera-linux/chimera-install-scripts, commit
# 43b0a7d2c86fa51c85a3fdc532ac5ebf9ece83b1 (the exact commit
# chimera-install-scripts-0.6.1 in cports itself builds from --
# confirmed against its real template.py), BSD-2-Clause, COPYING.md
# carried over unmodified.
#
# NOT depends=["cmd:apk!apk-tools", ...] the way upstream's own
# template.py declares its runtime deps: same cbuild limitation hit
# for h77-dots' bash and h77-installer's own chimera-install-scripts
# dependency (cbuild's `depends=` resolution needs a local template,
# not just a real remote binary). Every one of upstream's real
# dependencies (apk-tools, chimerautils, util-linux-mount,
# libarchive-progs) is already present in this project's own package
# set except `dialog`, which is listed directly in mklive-image.sh's
# sway PKGS instead.

pkgname = "h77-install-scripts"
pkgver = "0.6.1"
pkgrel = 0
build_style = "meta"
pkgdesc = "Patched chimera-install-scripts for hybrid-d77"
license = "BSD-2-Clause"
url = "https://github.com/dani-77/hybrid-d77"


def install(self):
    for f in (
        "chimera-installer",
        "chimera-bootstrap",
        "chimera-chroot",
        "genfstab",
    ):
        self.install_bin(self.files_path / f)
    self.install_license(self.files_path / "COPYING.md")
