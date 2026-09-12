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
        PKGS="${BASE_PKGS} sway swaybg swaylock swayidle yambar \
foot brightnessctl grim slurp wl-clipboard \
fuzzel fonts-hack-ttf bash \
elogind libseat-seatd libseat-seatd-dinit \
dbus dbus-dinit polkit polkit-dinit \
networkmanager networkmanager-dinit \
pipewire wireplumber pavucontrol \
xdg-desktop-portal xdg-desktop-portal-wlr \
udisks udiskie udiskie-dinit \
chimera-repo-user \
chimera-install-scripts \
h77-dots h77-sway-dots h77-installer"
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
        ;;
    *)
        echo "unknown image type: $IMAGE"
        echo
        echo "supported image types: base gnome plasma sway"
        exit 1
        ;;
esac

./mklive.sh -p "$PKGS" -f "$IMAGE" "$@"
