# hybrid-d77 :: general app dotfiles (not sway-specific), as a cports
# package. Installed to /etc/skel like an equivalent Alpine
# d77-sway-skel, but split apart here per the user's own plan
# (2026-09-12): app dotfiles
# with no WM-specific content live here, sway's own config lives in the
# sibling h77-sway-dots package instead.
#
# Sources (all read-only references, copied in on 2026-09-12):
#   - alacritty, qt6ct, Kvantum, gtk-2.0/3.0/4.0, cmus, fastfetch, htop,
#     mimeapps.list, pavucontrol.ini: ~/d77void/common/config/. qt5ct
#     and kitty dropped entirely -- confirmed neither package exists in
#     cports (qt5ct at all; kitty was never in this project's own list,
#     foot is the terminal), shipping their config would just be dead
#     weight. gtk-3.0/4.0 settings.ini: gtk-theme-name Arc-Dark ->
#     Breeze-Dark (arc-theme doesn't exist either, breeze-gtk does,
#     under KDE's own standard Breeze/Breeze-Dark naming, user-confirmed);
#     gtk-cursor-theme-name (Void's own "whiteglass") dropped entirely,
#     confirmed genuinely absent from cports (no cursor-theme package
#     at all). Kvantum/kvantum.kvconfig's theme= was "KvArcDark" -- a
#     real bug INHERITED from d77void's own source (their own
#     Kvantum/ dir only ever shipped catppuccin-mocha-blue too, same
#     as here, "KvArcDark" never existed on either side) -- fixed to
#     theme=catppuccin-mocha-blue, the only Kvantum theme this project
#     actually ships. qt6ct.conf's color_scheme_path still points at
#     the stock airy.conf rather than the shipped catppuccin-mocha-blue
#     colors file -- left as is, matches d77void's own real config
#     exactly (not a mismatch introduced here), not touched unless
#     asked.
#   - foot: an existing sway skel's own .config/foot (font
#     switched to Hack, matching fuzzel.ini's own font=hack below)
#   - fuzzel: ~/d77void/common/fuzzel_c/fuzzel/fuzzel.ini (terminal=
#     fixed from kitty to foot -- kitty was never actually in this
#     project's own package list to begin with)
#   - files/fuzzel-power-menu: ~/d77void/common/fuzzel_c/fuzzel-power-menu,
#     installed to /usr/bin -- a real #!/usr/bin/env bash script (see
#     depends= below), used by h77-sway-dots' sway config (`bindsym
#     $mod+x exec fuzzel-power-menu`, unmodified from d77void's own).
#   - backgrounds/d77.png (the wallpaper): an existing sway skel's own
#     .config/backgrounds -- referenced by h77-sway-dots' sway
#     config via `output * bg ~/.config/backgrounds/d77.png fill`, so it
#     lives in the always-installed h77-dots rather than the sway-only
#     package -- any future non-sway variant gets the same wallpaper too.
#   - files/50-udisks.rules: ~/d77void/common/50-udisks.rules (the same
#     rule ported to several earlier projects of this author's own --
#     grants org.freedesktop.udisks(2).* to the `storage` group.
#   - files/motd: shown at login, documents the anon/chimera and
#     root/chimera credentials -- no greeter needed (see h77-sway-dots'
#     .profile for the reasoning: Void's and Chimera's own convention,
#     the user's own call, even though greetd IS packaged here too).
#
# `storage` group: Chimera's base install does NOT create one (its own
# default groups -- adm, wheel, audio, video, network, ... -- confirmed
# against a real build log -- have no "storage"), so this package
# creates it via install_sysusers (runs as an apk install trigger, at
# ISO-build time, well before the live-boot's own user creation runs).
# `network` group DOES already exist by default -- no sysusers entry
# needed for that one.
#
# CORRECTED 2026-09-12 late, the actual root cause of "anon has no
# network permissions": chimera-live's own vendored live-boot script,
# initramfs-tools/lib/live/boot/9990-chimera-user.sh, creates the live
# user with a bare `useradd -m -c ... -s ... "$USERNAME"` -- NO -G at
# all, so `anon` gets no supplementary groups whatsoever, not even
# "network" (which NetworkManager's own shipped polkit rule grants
# wholesale to anyone in that group -- main/networkmanager/files/
# 50-org.freedesktop.NetworkManager.rules, confirmed by reading it).
# Same story for `storage` and udiskie's auto-mount. Patched directly
# in the vendored script (`-G network,storage`) rather than worked
# around here -- there's no package-install-time hook that fires again
# at every future boot to fix this after the fact, and the vendored
# script is already precedented as a patch point (mklive-image.sh's
# own "sway" case).
#
# 2026-09-13, after a full real-hardware install: user had to hand-run
# nwg-look to get GTK2 apps themed at all -- there was no skel/.gtkrc-2.0
# (GTK2's own real config file, confirmed via GTK 2.24's real gtkrc.c
# source: read from $HOME root, NOT .config, auto-added as a default rc
# file by gtk_rc_init) to begin with, only .config/gtk-2.0/
# gtkfilechooser.ini (unrelated -- file-chooser recent-dirs state, not
# theming). Added skel/.gtkrc-2.0, same values as gtk-3.0/4.0's own
# settings.ini (Breeze-Dark, Papirus-Dark, Hack 10) for consistency
# across all three GTK versions. The `include` line points at
# ".gtkrc-2.0.mine" (relative, no leading "~" or hardcoded username) --
# checked GTK 2.24's real parse_include_file() in gtkrc.c: it does NOT
# expand "~" at all (only checks g_path_is_absolute(), so a leading "~"
# would be treated as a literal path component and never resolve); a
# plain relative filename, on the other hand, is looked up relative to
# the currently-parsing rc file's own directory (here, wherever this
# very skel/.gtkrc-2.0 file ends up per-user), which correctly resolves
# under ANY username -- unlike d77void's own real .gtkrc-2.0, which
# hardcodes "/home/anon/.gtkrc-2.0.mine" and would silently point at
# the wrong home dir for any other username.
#
# Same round: h77-dots' own files/motd trimmed -- the ESP/BIOS-MBR
# partitioning explanation was redundant once Partition/Filesystems
# were restored as real interactive, guided steps inside the installer
# itself (h77-installer's own pre-flight dialog already covers this) --
# user's own call: "isso é feito sozinho e bem feito," no need to
# pre-explain it in the motd too.
#
# 2026-09-13, later: files/h77-update (new) -- pulls the latest h77-*
# packages from this project's own GitHub Release (h77-pkgs) and apk
# upgrades against them on an ALREADY-INSTALLED system, mirroring
# iso/fetch-pkgs.sh's own real, working pattern but talking to
# GitHub's REST API directly via curl+jq instead of needing the `gh`
# CLI (a dev tool, not something to require on an end-user install).
# Real nuance the script's own header explains in full: cbuild's own
# signing key is regenerated on every single build (confirmed in
# container/cbuild-entrypoint.sh -- keygen runs unconditionally
# whenever etc/keys/*.rsa doesn't exist, and the cbuild container
# reclones cports from scratch every run, so that's always true) --
# so the key an ISO trusted at build time won't verify a LATER
# release's packages. Fixed by always fetching and trusting each
# release's own *.rsa.pub fresh at update time, same as how
# iso/mklive-d77.sh already does for a fresh ISO build. jq (`main`
# tier, confirmed real) added to mklive-image.sh's sway PKGS for this;
# curl was already there (wittr.sh). Also mentioned in
# files/motd-installed ("doas h77-update"), not the live motd -- makes
# no sense to update an ephemeral live session. User's own request,
# 2026-09-13.
#
# 2026-09-16: skel/.config/nvim (new) -- the LazyVim starter
# (github.com/LazyVim/starter), copied from a real installed system
# as-is, no local customization yet (lua/plugins/ only has the
# starter's own example.lua). Needs `neovim` (already in
# mklive-image.sh's sway PKGS, `user` tier) plus `git`, `clang`,
# `gmake` (added same day) to actually be usable -- lazy.nvim clones
# every plugin via git, and native-build plugins (treesitter parsers,
# telescope-fzf-native) need a C compiler + `make`.
#
# 2026-09-16, also: skel/.config/mimeapps.list -- a real, silent gap,
# same story as h77-sway-dots' own swaync miss: mimeapps.list was
# already named above as one of the files sourced from
# ~/d77void/common/config/ on 2026-09-12, but never actually got
# copied into skel/. Added now, but trimmed to just the one entry that
# is a genuine project default (text/plain -> mousepad, matching
# h77-dots' own mousepad package) -- the real file on the source
# machine also had `x-scheme-handler/claude-cli=claude-code-url-
# handler.desktop`, a per-machine artifact of that one install's own
# Claude Code setup, not something every fresh install should get.
#
# 2026-09-16, fastfetch: config.jsonc and its logo re-synced from a
# real installed system -- the committed version was still the
# inherited "D77 Void" branding (kitty-protocol logo at
# images/original.png); the real machine had already moved on to
# "Hybrid D77" branding, a sixel-protocol logo (skel/.config/fastfetch/
# logo.png, replacing the old images/original.png entirely, now
# removed as dead weight), and the D77 Void icon glyph swapped for a
# "chi" character in the module icons (Chimera-appropriate).

pkgname = "h77-dots"
pkgver = "0.1.0"
pkgrel = 0
build_style = "meta"
pkgdesc = "General app dotfiles for hybrid-d77"
license = "custom:meta"
url = "https://github.com/dani-77/hybrid-d77"
# fuzzel-power-menu is a real #!/usr/bin/env bash script (confirmed by
# reading it), not sh -- Chimera's default shell is plain /bin/sh.
# NOT declared as depends=["bash"]: cbuild's own dependency resolution
# insists on resolving every `depends` entry via a local TEMPLATE
# (confirmed the hard way: "ERROR: template 'bash' cannot be resolved",
# even though main/bash/template.py genuinely exists in the checkout --
# a cbuild quirk/limitation, not investigated further). "bash" is
# listed directly in mklive-image.sh's sway package set instead, which
# works reliably and is functionally equivalent for our purposes.
# We genuinely install straight into /etc (skel content + motd), which
# cbuild's own lint flags by default ("'/etc' exists, verify if this
# is necessary and then set the 'etcfiles' option") -- confirmed the
# real syntax against real templates (main/zsh, main/mc, ...), it's a
# list of option names, not a dict/bool.
options = ["etcfiles"]


def install(self):
    # install_files(path, dest) copies path (a dir) to destdir/dest/<path's
    # own basename> -- since "skel" lives next to template.py (not under
    # any fetched source= tree, there is none here), pass an ABSOLUTE path
    # via template_path: pathlib's `/` operator ignores self.cwd entirely
    # once the right-hand side is already absolute, so this reliably
    # resolves to this package's own skel/ dir regardless of what self.cwd
    # would otherwise be for a source-less "meta" package. Verified
    # against cbuild's real source (src/cbuild/core/template.py), not
    # guessed -- see docs/NOTES.md.
    self.install_files(self.template_path / "skel", "etc")

    # cports' lint insists vendor-shipped polkit rules go under
    # /usr/share, not /etc (/etc/polkit-1/rules.d is meant for local
    # admin overrides) -- polkit itself reads both dirs, so this is a
    # pure packaging-convention fix, not a behavior change. Confirmed
    # against the real lint hook's own message, not guessed.
    self.install_file(
        self.files_path / "50-udisks.rules", "usr/share/polkit-1/rules.d"
    )
    self.install_file(self.files_path / "motd", "etc")
    # motd-installed: a short, generic welcome with NO login
    # credentials and no live-only install instructions -- the live
    # motd above is wrong once actually installed to disk (stale
    # "password: chimera" after the real install sets a real password;
    # "doas h77-installer" makes no sense on an already-installed
    # system). Installed to usr/share, not etc, so it never becomes
    # the ACTUAL /etc/motd by just being packaged -- h77-install-
    # scripts' own menu_install copies it over $sysroot/etc/motd as
    # the very last step of a real install (see its own patch
    # comment), once $sysroot/usr/share/h77/motd-installed (this same
    # file, now inside the freshly bootstrapped target) actually
    # exists to copy from. User's own request, 2026-09-13.
    self.install_file(self.files_path / "motd-installed", "usr/share/h77")
    # QT_QPA_PLATFORMTHEME=qt6ct: without this, Qt apps ignore
    # qt6ct/Kvantum entirely and fall back to their own default style
    # -- user's own call, real Void convention (d77void's own D77_CORE
    # bundle ships qt5ct+qt6ct+kvantum together for the same reason).
    # /etc/environment is read by PAM's pam_env at login, system-wide,
    # standard Linux convention (not sway/labwc-specific).
    self.install_file(self.files_path / "environment", "etc")
    self.install_bin(self.files_path / "fuzzel-power-menu")
    # h77-update: pulls the latest h77-* packages from this project's
    # own GitHub Release (h77-pkgs) and apk upgrades against them on an
    # ALREADY-INSTALLED system -- see the script's own header comment
    # for the full reasoning, including why it always trusts that
    # release's own signing key fresh rather than one baked in at ISO
    # build time (cbuild's own key is regenerated every single build,
    # confirmed in container/cbuild-entrypoint.sh). Needs curl (already
    # here for wittr.sh) + jq (added to mklive-image.sh's sway PKGS
    # for this). User's own request, 2026-09-13.
    self.install_bin(self.files_path / "h77-update")

    # files/storage.sysusers: "g storage -" (systemd-sysusers syntax,
    # confirmed against a real cports package's own sysusers.conf,
    # user/greetd/files/) creates the group with an auto-assigned GID;
    # install_sysusers is cbuild's own real helper (confirmed against
    # its source and greetd's own template.py, which uses it the same
    # way, same files_path-relative pattern as every other install_*
    # call in this file).
    self.install_sysusers(self.files_path / "storage.sysusers")
