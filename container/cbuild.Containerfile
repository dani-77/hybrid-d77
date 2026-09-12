# hybrid-d77 :: build container for cports/cbuild -- bootstraps a real
# build root and builds pkg/h77-dots + pkg/h77-sway-dots into actual
# .apk packages (they only exist as template.py + skel content until
# this runs, see docs/NOTES.md).
#
# Separate from container/Containerfile (the mklive.sh/ISO one) on
# purpose: cbuild explicitly REFUSES to run as root ("Please don't run
# cbuild as root", confirmed against its own src/early.py), unlike
# mklive.sh which needs root for mount(8). The process itself runs as
# a plain non-root user throughout (cbuild's own sandboxing is
# bwrap/user-namespaces, not host root) -- but the OUTER container
# still needs --privileged --security-opt label=disable, confirmed the
# hard way: without it, bwrap's own nested mount() calls (even inside
# its own freshly-created mount+user namespace) fail with "Can't mount
# proc on /newroot/proc: Operation not permitted", blocked by podman's
# default capability/seccomp set, not by anything cbuild does.
#
#   sudo podman build -t hybrid-d77-cbuild -f container/cbuild.Containerfile .
#   sudo podman run --rm --privileged --security-opt label=disable \
#       -v "$PWD:/src" -w /src hybrid-d77-cbuild

FROM docker.io/chimeralinux/chimera:latest

# cbuild's real userland deps, confirmed against cports' own Usage.md
# (not guessed): python 3.12+ (cports' own package is just "python",
# 3.14.6 -- the base image does NOT ship it, confirmed the hard way:
# "env: python3: No such file or directory" when ./cbuild's own
# shebang tried to run), git, openssl (keygen only), bwrap
# (bubblewrap). shadow is added just to get useradd, since the base
# image relies on sd-tools (sysusers-style) for its own users and may
# not ship it otherwise.
RUN apk add --no-cache --no-interactive \
        --repository https://repo.chimera-linux.org/current/main \
        python git openssl bubblewrap shadow

# Fixed uid 1000 to match the host user the /src bind mount is owned
# by (avoids permission mismatches without needing --userns tricks).
RUN useradd -m -u 1000 -s /bin/sh builder

USER builder
WORKDIR /home/builder
ENTRYPOINT ["/src/container/cbuild-entrypoint.sh"]
