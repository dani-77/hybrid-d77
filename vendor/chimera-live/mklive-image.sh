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
        PKGS="${BASE_PKGS} sway swaybg swaylock swayidle swayimg waybar \
swaync wmenu cliphist wlsunset xwayland-satellite \
foot brightnessctl grim slurp wl-clipboard \
fuzzel fonts-hack-ttf fonts-nerd-hack fonts-font-awesome-otf bash \
playerctl python-gobject curl wget2 firefox thunderbird \
elogind libseat-seatd libseat-seatd-dinit mate-polkit \
dbus dbus-dinit polkit polkit-dinit \
networkmanager networkmanager-dinit power-profiles-daemon \
pipewire wireplumber pavucontrol alsa-utils \
xdg-desktop-portal xdg-desktop-portal-wlr xdg-desktop-portal-gtk \
xdg-user-dirs xdg-user-dirs-gtk xdg-utils \
udisks udiskie udiskie-dinit \
qt6ct kvantum breeze-gtk nwg-look papirus-icon-theme \
thunar file-roller \
acpi bash-completion bc-gh cmus cups system-config-printer \
fastfetch feh gettext htop inxi imagemagick mousepad mpv \
musl-locales nano smartmontools transmission ufw unzip usbutils \
vim yt-dlp zathura zathura-pdf-poppler gnome-calculator \
chimera-repo-user \
chimera-install-scripts \
h77-dots h77-sway-dots h77-installer"
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
        # chimera-install-scripts (`main`) + h77-installer: the start
        # of the disk-installer side, 2026-09-12 -- a thin wrapper
        # around the real chimera-installer/chimera-bootstrap, not a
        # custom installer. See pkg/h77-installer/template.py.
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
        ;;
    *)
        echo "unknown image type: $IMAGE"
        echo
        echo "supported image types: base gnome plasma sway"
        exit 1
        ;;
esac

./mklive.sh -p "$PKGS" -f "$IMAGE" "$@"
