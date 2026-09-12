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
        # 50-udisks.rules + the `storage` group. Both -r flags below are
        # REQUIRED, not optional -- main alone doesn't have udiskie.
        # seatd's real package name is libseat-seatd (+ -dinit for the
        # service subpackage), also `user` tier.
        PKGS="${BASE_PKGS} sway swaybg swaylock swayidle yambar \
foot brightnessctl grim slurp wl-clipboard \
elogind libseat-seatd libseat-seatd-dinit \
dbus dbus-dinit polkit polkit-dinit \
networkmanager networkmanager-dinit \
pipewire wireplumber pavucontrol \
xdg-desktop-portal xdg-desktop-portal-wlr \
udisks udiskie udiskie-dinit \
h77-dots h77-sway-dots"
        ;;
    *)
        echo "unknown image type: $IMAGE"
        echo
        echo "supported image types: base gnome plasma sway"
        exit 1
        ;;
esac

./mklive.sh -p "$PKGS" -f "$IMAGE" "$@"
