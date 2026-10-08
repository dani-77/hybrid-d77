# hybrid-d77 :: Mocinha's manifest for this live, as a cports package.
#
# Ships files/mocinha.toml -> /etc/mocinha.toml, the remaster's install
# policy that the Mocinha installer (pkg/mocinha) reads: live copy of
# /run/live/rootfs/filesystem.erofs, the groups and dinit services of
# h77-installer's checklists, KMAP, chpasswd -c SHA512, grub --removable,
# the apk mirror list. Mocinha uninstalls both packages from the installed
# system ([live_only].packages), so neither persists there.
#
# Experimental third install method (branch mocinha), next to h77-installer.

pkgname = "h77-mocinha"
pkgver = "0.1.0"
pkgrel = 0
build_style = "meta"
pkgdesc = "Mocinha installer manifest for hybrid-d77"
license = "custom:meta"
url = "https://github.com/dani-77/hybrid-d77"
# /etc/mocinha.toml is a real, deliberate /etc install.
options = ["etcfiles"]


def install(self):
    self.install_file(self.files_path / "mocinha.toml", "etc")
