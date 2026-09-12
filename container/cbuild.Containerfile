# hybrid-d77 :: build container for cports/cbuild -- bootstraps a real
# build root and builds pkg/h77-dots + pkg/h77-sway-dots into actual
# .apk packages (they only exist as template.py + skel content until
# this runs, see docs/NOTES.md).
#
# Separate from container/Containerfile (the mklive.sh/ISO one) on
# purpose: cbuild explicitly REFUSES to run as root ("Please don't run
# cbuild as root", confirmed against its own src/early.py), unlike
# mklive.sh which needs root for mount(8). This container therefore
# runs as a plain non-root user throughout, no --privileged needed for
# the run itself (cbuild's own sandboxing is bwrap/user-namespaces,
# which don't need host root).
#
#   sudo podman build -t hybrid-d77-cbuild -f container/cbuild.Containerfile .
#   sudo podman run --rm -v "$PWD:/src" -w /src hybrid-d77-cbuild

FROM docker.io/chimeralinux/chimera:latest

# cbuild's real userland deps, confirmed against cports' own Usage.md
# (not guessed): python3.12+ (base image already has a new enough
# python3), git, openssl (keygen only), bwrap (bubblewrap). shadow is
# added just to get useradd, since the base image relies on sd-tools
# (sysusers-style) for its own users and may not ship it otherwise.
RUN apk add --no-cache --no-interactive \
        --repository https://repo.chimera-linux.org/current/main \
        git openssl bubblewrap shadow

# Fixed uid 1000 to match the host user the /src bind mount is owned
# by (avoids permission mismatches without needing --userns tricks).
RUN useradd -m -u 1000 -s /bin/sh builder

USER builder
WORKDIR /home/builder
ENTRYPOINT ["/src/container/cbuild-entrypoint.sh"]
