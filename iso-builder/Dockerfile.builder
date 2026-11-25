# ==============================================================================
# Jarvis OS: Debian Live ISO Container Builder
# Allows building the bootable hybrid ISO from Windows / macOS / Linux via Docker.
# ==============================================================================

FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    live-build \
    debootstrap \
    squashfs-tools \
    xorriso \
    grub-common \
    grub-pc-bin \
    grub-efi-amd64-bin \
    mtools \
    dosfstools \
    rsync \
    curl \
    ca-certificates \
    libarchive-tools \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

CMD ["/bin/bash", "/workspace/iso-builder/build-debian-iso.sh"]
