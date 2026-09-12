# hybrid-d77 :: thin installer wrapper, as a cports package.
#
# NOT a custom installer -- reuses Chimera's own real
# chimera-installer/chimera-bootstrap, now via this project's own
# patched fork (pkg/h77-install-scripts, see that template.py) which
# adds real interactive groups/services checklists directly into
# chimera-installer itself -- see that package's own header comment
# for the full reasoning. This package only ships:
#   - files/installer.conf -> /etc/h77/installer.conf: pre-filled
#     INSTALL_CONFIG_* answers (chimera-installer's own real config
#     file format, confirmed against its source's config_load()), so
#     the user isn't re-typing the same safe defaults every run. See
#     that file's own header comment for exactly what's set and why
#     (notably: NOT the package list -- local-source installs get
#     h77-dots/h77-sway-dots for free via chimera-bootstrap's own
#     local tar-copy of the live's rootfs, no apk/network involved).
#   - files/h77-installer -> /usr/bin: `exec chimera-installer -c
#     /etc/h77/installer.conf "$@"`, nothing more -- the groups/
#     services gaps this used to paper over with an always-run
#     post-install fix-up are now handled by the interactive checklists
#     themselves (see h77-install-scripts).
#   - files/post-install -> /usr/lib/h77-installer/post-install: kept
#     as a MANUAL fallback only (not auto-run from h77-installer
#     anymore -- see that file's own header comment for why running it
#     unconditionally would now conflict with an explicit uncheck in
#     the interactive dialogs).
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
