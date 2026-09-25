#!/bin/sh
#
# Convenience script for generating different kinds of live images

# all extra arguments are passed to mklive.sh as is
#
# Copyright 2022 q66 <q66@chimera-linux.org>
#
# License: BSD-2-Clause
#

IMAGE=
EXTRA_PKGS=
KERNEL_PKGS=

while getopts "b:k:p:" opt; do
    case "$opt" in
        b) IMAGE="$OPTARG";;
        k) KERNEL_PKGS="$OPTARG";;
        p) EXTRA_PKGS="$OPTARG";;
        *) ;;
    esac
done

shift $((OPTIND - 1))

if [ -z "$KERNEL_PKGS" ]; then
    KERNEL_PKGS="linux-stable"
    if [ "$IMAGE" != "minimal" ]; then
        KERNEL_PKGS="$KERNEL_PKGS linux-stable-zfs-bin"
    fi
fi

readonly BASE_PKGS="base-full base-live ${KERNEL_PKGS} ${EXTRA_PKGS}"

# hybrid-d77: everything both of our own variants (sway, niri) share --
# split out of the sway list 2026-09-25 when the niri variant was
# added, so the two can't silently drift apart. The per-package
# reasoning still lives in the sway case's own comment block below.
readonly H77_COMMON_PKGS="foot brightnessctl grim slurp wl-clipboard \
fuzzel fonts-hack-ttf fonts-nerd-hack fonts-font-awesome-otf bash \
curl wget2 jq firefox thunderbird \
elogind libseat-seatd libseat-seatd-dinit mate-polkit \
dbus dbus-dinit polkit polkit-dinit \
networkmanager networkmanager-dinit power-profiles-daemon \
pipewire wireplumber pavucontrol alsa-utils \
xdg-desktop-portal xdg-desktop-portal-gtk \
xdg-user-dirs xdg-user-dirs-gtk xdg-utils \
udisks udiskie udiskie-dinit \
qt6ct kvantum breeze-gtk nwg-look papirus-icon-theme \
thunar file-roller \
acpi bash-completion bc-gh cmus cups system-config-printer \
fastfetch feh gettext htop inxi imagemagick mousepad mpv \
musl-locales nano smartmontools transmission ufw unzip usbutils \
neovim yt-dlp zathura zathura-pdf-poppler gnome-calculator \
git clang gmake tree-sitter-cli \
chimera-repo-user \
dialog \
h77-dots h77-installer h77-install-scripts h77-welcome"

case "$IMAGE" in
    minimal)
        PKGS="base-minimal base-full-kernel ${KERNEL_PKGS} ${EXTRA_PKGS}"
        ;;
    base)
        PKGS="${BASE_PKGS}"
        ;;
    gnome)
        PKGS="${BASE_PKGS} gnome"
        ;;
    plasma)
        PKGS="${BASE_PKGS} plasma-desktop"
        ;;
    sway)
        # hybrid-d77's own variant. No single "sway" metapackage exists
        # in cports (unlike gnome/plasma-desktop), so every piece is
        # listed by hand here -- names verified against the real repo
        # 2026-09-12 (see docs/NOTES.md), not guessed.
        #
        # CORRECTED same day: the first pass here searched only the
        # `main` repo and concluded greetd/udiskie don't exist in
        # cports at all -- wrong, both exist, just under the separate
        # `user` repo tier (community-maintained, cports' equivalent of
        # Alpine's community/AUR). greetd IS real (greetd, greetd-dinit,
        # greetd-man) but deliberately not used here -- the user's own
        # call: Void and Chimera's own convention is a plain getty
        # login: prompt, with /etc/motd documenting the anon/chimera and
        # root/chimera credentials, no greeter needed. udiskie IS used
        # (real: udiskie, udiskie-dinit) -- `udiskie -a` non-interactive
        # auto-mount, same as every other d77 variant, needs h77-dots'
        # 50-udisks.rules + the `storage` group (h77-dots creates that
        # group itself via sysusers; the `network` group NetworkManager
        # needs already exists by Chimera's own default -- and the live
        # user is now added to both, patched directly into vendor/
        # chimera-live's own live-boot script, see docs/NOTES.md). Both
        # -r flags below are REQUIRED, not optional -- main alone
        # doesn't have udiskie. seatd's real package name is
        # libseat-seatd (+ -dinit for the service subpackage), also
        # `user` tier.
        #
        # chimera-repo-user is included so the BOOTED live's own apk
        # also has the `user` repo configured (not just the build
        # host's) -- otherwise `apk add` on a running live can only
        # reach `main` (chimera-repo-main comes in transitively via
        # base-full -> base-full-core -> base-bootstrap, confirmed
        # against real templates; chimera-repo-user does not, nothing
        # else pulls it in).
        PKGS="${BASE_PKGS} ${H77_COMMON_PKGS} \
sway swaybg swaylock swayidle swayimg waybar \
swaync wmenu cliphist wlsunset xwayland-satellite \
playerctl python-gobject xdg-desktop-portal-wlr \
h77-sway-dots"
        # waybar (`user` tier -- real, confirmed 2026-09-12, corrects
        # this project's own earlier "doesn't exist" mistake) replaces
        # yambar: real bugs found on real hardware (hardcoded BAT0,
        # unreliable refresh, the wireless display vanishing outright),
        # see docs/NOTES.md. fonts-nerd-hack (`user`) is a SEPARATE
        # package from fonts-hack-ttf (`main`, used by foot) -- it's
        # the nerd-fonts-patched variant with the icon glyphs waybar's
        # config actually uses; plain Hack has no icon codepoints.
        # playerctl + python-gobject: h77-sway-dots' waybar
        # custom/media module (mediaplayer.py) needs both (MPRIS +
        # the `gi` Python module it imports). curl: wittr.sh (the
        # custom/weather module). firefox: user request.
        # fuzzel is `user` tier too (fine, we already need -r user for
        # udiskie/greetd/seatd). fonts-hack-ttf is `main`. bash is
        # needed for fuzzel-power-menu (h77-dots), a real
        # #!/usr/bin/env bash script -- Chimera's default shell is
        # plain /bin/sh (dash-like chimerautils sh), confirmed against
        # /etc/passwd earlier this session. Listed explicitly here
        # rather than as h77-dots' own depends=["bash"]: cbuild itself
        # can't resolve that (see the template.py comment), so this is
        # the reliable equivalent.
        #
        # h77-installer + h77-install-scripts: the disk-installer side,
        # 2026-09-12 -- a thin wrapper (h77-installer) around this
        # project's own patched fork of chimera-installer/
        # chimera-bootstrap (h77-install-scripts, replaces the real
        # `chimera-install-scripts` package entirely), which adds real
        # interactive groups/services checklists -- see both packages'
        # own template.py. `dialog` is listed explicitly here since it
        # was previously pulled in transitively via the real
        # chimera-install-scripts package's own depends=.
        #
        # 2026-09-12 night: full cross-check against d77void's own real
        # sway package list (mkd77.sh's D77_CORE + sway-specific PKGS,
        # via COMMON/FUZZEL) -- every name below verified against a
        # full listing of the real cports main+user trees (git trees
        # API, not guessed), user's own explicit corrections included:
        #   - swaync: WAS configured (skel + `exec swaync` in
        #     sway/config) but the package itself was never added here
        #     -- a real, silent gap, `user` tier.
        #   - mate-polkit (`main`): a polkit AUTHENTICATION AGENT --
        #     without one, no GUI app can ever prompt for a password,
        #     regardless of polkitd running. Also missing until now.
        #   - arc-theme, pcmanfm, geary, qt5ct: confirmed genuinely
        #     absent from cports (checked, not assumed) -- breeze-gtk,
        #     thunar, thunderbird, and qt6ct+kvantum alone used instead
        #     (user's own correction).
        #   - xarchiver, ranger, uget, plymouth, pulseaudio-utils,
        #     qt5-wayland/qt6-wayland, nerd-fonts-symbols-ttf: also
        #     confirmed absent, no direct substitute added (file-roller
        #     covers xarchiver's role; qt5-base/qt6-base already bundle
        #     their own Wayland platform plugin, nothing separate to
        #     add; pipewire's own pulse compat covers pulseaudio-utils).
        #   - wget -> wget2 (the real package name); ImageMagick ->
        #     imagemagick (lowercase, case-sensitive filesystem).
        #
        # 2026-09-13: vim -> neovim (`user` tier, confirmed real,
        # user's own request), and a theming pass fixed two real
        # bugs found while double-checking gtk-2.0/3.0/4.0 -- see
        # pkg/h77-dots/template.py's own header comment for the
        # Kvantum "KvArcDark" and gtk-cursor-theme-name fixes.
        #
        # 2026-09-13, later: jq (`main` tier, confirmed real) added
        # for h77-dots' new h77-update script -- reliable JSON parsing
        # of the GitHub Releases API without depending on the `gh` CLI
        # (a dev tool, not something an end-user install should need).
        #
        # 2026-09-16: git, clang, gmake (all `main` tier, confirmed via
        # `apk policy`) added after neovim/LazyVim came up short on a
        # real installed system -- lazy.nvim (LazyVim's own plugin
        # manager) shells out to `git` to clone every plugin, so neovim
        # is non-functional without it regardless of anything else here.
        # clang covers the "no C compiler" healthcheck warning (this
        # variant intentionally has no `gcc` -- Chimera's own base is
        # LLVM-only, so clang is the native choice, and nvim-treesitter
        # accepts it from its own compiler list). gmake is the one that
        # actually matters for the name `make`: confirmed via `apk
        # manifest` that the `gmake` package installs the real binary
        # at `usr/bin/make` (not just `usr/bin/gmake`), while `bmake`
        # installs only `usr/bin/bmake` and provides no generic `make`
        # at all -- needed for plugins with a native build step, e.g.
        # telescope-fzf-native.nvim.
        #
        # 2026-09-16, same day, real gap found on a real install:
        # tree-sitter-cli (`user` tier) -- the shipped nvim-treesitter
        # is on its "main" branch (the v1.0 rewrite, see lazy-lock.json),
        # which no longer compiles parsers by invoking cc/clang
        # directly -- it shells out to the `tree-sitter` CLI's own
        # `tree-sitter build` instead, which THEN invokes the C
        # compiler. Without this package, every parser install failed
        # with "Error during \"tree-sitter build\": ... ENOENT" even
        # with clang+gmake both present and working. Confirmed by
        # reproducing headless, then fixed and re-verified the same
        # way (TSInstall no longer errors, .so files land in
        # nvim-treesitter/parser/).
        #
        # 2026-09-24: h77-welcome (new) -- a dialog(1) TUI welcome/
        # installer helper, this project's own equivalent of d77void's
        # GTK d77-welcome. No new packages needed for it: `dialog` is
        # already above (h77-installer's own "Before you start"
        # notice), and it only shells out to h77-installer/h77-update,
        # both already here too. See pkg/h77-welcome/template.py for
        # the full reasoning.
        ;;
    niri)
        # hybrid-d77's second variant (2026-09-25): niri as the
        # compositor, the user's own Utumno (Quickshell) as the whole
        # shell -- bar, launcher, lock screen, power menu, wallpaper
        # picker, OSD -- driven by keybinds through qsd77. All three
        # built by this project (pkg/utumno, pkg/qsd77, pkg/
        # h77-niri-dots). niri + quickshell are `user` tier (confirmed
        # against the real cports tree, niri 26.04, quickshell 0.3.1).
        #
        # quickshell is listed here, not as utumno/qsd77's own
        # depends=: same cbuild "template cannot be resolved"
        # limitation as h77-dots' bash (see the sway case below).
        # Utumno's other runtime commands (amixer, brightnessctl, curl,
        # powerprofilesctl) are already in H77_COMMON_PKGS.
        # swaybg: Utumno's wallpaper script has no niri-specific
        # backend, it falls through to its generic swww -> swaybg
        # chain, and swww isn't in cports. xwayland-satellite is
        # niri's own depends= already, listed anyway for clarity.
        # xdg-desktop-portal-gnome: niri's own niri-portals.conf
        # (installed by the niri package) prefers it for screencasting.
        PKGS="${BASE_PKGS} ${H77_COMMON_PKGS} \
niri xwayland-satellite swaybg xdg-desktop-portal-gnome \
quickshell utumno qsd77 \
h77-niri-dots"
        ;;
    *)
        echo "unknown image type: $IMAGE"
        echo
        echo "supported image types: base gnome plasma sway niri"
        exit 1
        ;;
esac

./mklive.sh -p "$PKGS" -f "$IMAGE" "$@"
