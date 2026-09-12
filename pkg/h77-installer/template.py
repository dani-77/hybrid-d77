# hybrid-d77 :: thin installer wrapper, as a cports package.
#
# NOT a custom installer -- reuses Chimera's own real
# chimera-installer/chimera-bootstrap (chimera-install-scripts,
# `main` tier, confirmed real against the actual repo) for everything
# that matters: partitioning, bootstrap, user creation, bootloader.
# This package only ships:
#   - files/installer.conf -> /etc/h77/installer.conf: pre-filled
#     INSTALL_CONFIG_* answers (chimera-installer's own real config
#     file format, confirmed against its source's config_load()), so
#     the user isn't re-typing the same safe defaults every run. See
#     that file's own header comment for exactly what's set and why
#     (notably: NOT the package list -- local-source installs get
#     h77-dots/h77-sway-dots for free via chimera-bootstrap's own
#     local tar-copy of the live's rootfs, no apk/network involved).
#   - files/h77-installer -> /usr/bin: runs chimera-installer, then a
#     small post-install fix-up (see files/post-install's own header
#     comment for exactly why it's needed -- chimera-installer only
#     ever adds the new user to "wheel" and has no services step at
#     all, confirmed against its real source, unlike Void's own
#     void-installer which has both a groups and a services checklist).
#   - files/post-install -> /usr/lib/h77-installer/post-install: adds
#     network/storage/audio/video to the installed user, enables the
#     dinit services this desktop needs that don't self-enable
#     (polkitd, networkmanager, seatd, rtkit, syslog-ng -- dbus and
#     elogind already self-enable via their own templates'
#     install_service(..., enable=True), confirmed by reading them).
#
# Kickoff of the disk-installer work, 2026-09-12 -- the live-ISO side
# of this project was the priority until now ("o trabalho de instalar
# deixamos para depois"); this is a deliberately small first slice; see
# docs/NOTES.md for what's still open (SystemRoot/disk layout stays
# interactive on purpose, network-source installs need someone to fill
# in Packages by hand for now, nothing automates that yet).

pkgname = "h77-installer"
pkgver = "0.1.0"
pkgrel = 0
build_style = "meta"
pkgdesc = "Installer wrapper for hybrid-d77"
license = "custom:meta"
url = "https://github.com/dani-77/hybrid-d77"
# NOT declared as depends=["chimera-install-scripts"]: cbuild's own
# dependency resolution insists on resolving every `depends` entry via
# a local TEMPLATE, not just a real remote binary -- confirmed the
# hard way here too (same issue as h77-dots' bash, see that
# template.py's comment): "ERROR: template 'chimera-install-scripts'
# cannot be resolved", even though main/chimera-install-scripts/
# template.py genuinely exists. Listed directly in mklive-image.sh's
# package set instead.
#
# /etc/h77/installer.conf is a real, deliberate /etc install.
options = ["etcfiles"]


def install(self):
    self.install_bin(self.files_path / "h77-installer")
    self.install_file(
        self.files_path / "post-install", "usr/lib/h77-installer", mode=0o755
    )
    self.install_file(self.files_path / "installer.conf", "etc/h77")
