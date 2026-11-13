# hybrid-d77 :: matugen, Material You colour palettes from an image.
# Utumno (0.2.0 on) runs it from wallpaper/set-wallpaper.sh to make its
# theme follow the wallpaper; without it Utumno just keeps its built-in
# palette. Not in cports (neither main nor user, checked 2026-11-13), so
# packaged here, after d77void-pkgs' own srcpkgs/matugen (same version,
# same upstream tarball and checksum), in cports' cargo style (user/eza).
pkgname = "matugen"
pkgver = "4.2.0"
pkgrel = 0
build_style = "cargo"
hostmakedepends = ["cargo-auditable"]
makedepends = ["rust-std"]
pkgdesc = "Material You color generation tool"
license = "GPL-2.0-only"
url = "https://github.com/InioX/matugen"
source = f"{url}/archive/refs/tags/v{pkgver}.tar.gz"
sha256 = "82044ab8ac3e793b2b94f8f75917b348b4038585133a77c07f5de59c88d65244"
