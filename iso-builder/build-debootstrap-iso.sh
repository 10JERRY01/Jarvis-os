#!/usr/bin/env bash
# ==============================================================================
# Jarvis OS: Standalone debootstrap Live ISO Builder
# Builds a minimal, fully transparent, bootable hybrid Debian 12 ISO
# with Liquorix gaming kernel, 32-bit multiarch, and Jarvis Ambient AI.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
BUILD_DIR="/tmp/jarvis-debootstrap"
CHROOT_DIR="${BUILD_DIR}/chroot"
ISO_DIR="${BUILD_DIR}/iso"
OUT_DIR="${SCRIPT_DIR}/out"

DEBIAN_MIRROR="http://deb.debian.org/debian/"
DEBIAN_RELEASE="bookworm"
ISO_NAME="jarvis-os-debootstrap-amd64.hybrid.iso"

echo "=========================================================="
echo "    JARVIS OS: DEBOOTSTRAP HYBRID LIVE ISO BUILDER        "
echo "=========================================================="

if [[ $EUID -ne 0 ]]; then
   echo "[ERROR] This builder requires root privileges. Please run with sudo."
   exit 1
fi

cleanup() {
    echo "[INFO] Cleaning up mount points..."
    for m in /dev/pts /dev /proc /sys; do
        if mountpoint -q "${CHROOT_DIR}${m}" 2>/dev/null; then
            umount -l "${CHROOT_DIR}${m}" || true
        fi
    done
}
trap cleanup EXIT

# 1. Dependency Verification
REQUIRED_TOOLS=("debootstrap" "mksquashfs" "xorriso" "grub-mkrescue" "mtools")
for tool in "${REQUIRED_TOOLS[@]}"; do
    command -v "${tool}" >/dev/null 2>&1 || {
        echo "[ERROR] Required tool '${tool}' is missing."
        echo "[INFO] Run: apt-get update && apt-get install -y debootstrap squashfs-tools xorriso grub-pc-bin grub-efi-amd64-bin mtools dosfstools"
        exit 1
    }
done

mkdir -p "${CHROOT_DIR}" "${ISO_DIR}/live" "${ISO_DIR}/boot/grub" "${OUT_DIR}"

# 2. Debootstrap Base System
if [[ ! -f "${CHROOT_DIR}/bin/bash" ]]; then
    echo "[INFO] Bootstrapping Debian 12 (${DEBIAN_RELEASE}) minimal base..."
    debootstrap --arch=amd64 \
        --variant=minbase \
        --components=main,contrib,non-free,non-free-firmware \
        "${DEBIAN_RELEASE}" "${CHROOT_DIR}" "${DEBIAN_MIRROR}"
else
    echo "[INFO] Existing chroot base detected. Skipping initial debootstrap."
fi

# 3. Mount Virtual Filesystems
echo "[INFO] Binding host filesystems into target chroot..."
mount --bind /dev "${CHROOT_DIR}/dev"
mount --bind /dev/pts "${CHROOT_DIR}/dev/pts"
mount -t proc proc "${CHROOT_DIR}/proc"
mount -t sysfs sys "${CHROOT_DIR}/sys"

# Copy DNS config
cp /etc/resolv.conf "${CHROOT_DIR}/etc/resolv.conf"

# 4. Configure Repositories & Install Packages inside Chroot
cat << EOF > "${CHROOT_DIR}/etc/apt/sources.list"
deb ${DEBIAN_MIRROR} ${DEBIAN_RELEASE} main contrib non-free non-free-firmware
deb ${DEBIAN_MIRROR} ${DEBIAN_RELEASE}-updates main contrib non-free non-free-firmware
deb http://security.debian.org/debian-security ${DEBIAN_RELEASE}-security main contrib non-free non-free-firmware
deb ${DEBIAN_MIRROR} ${DEBIAN_RELEASE}-backports main contrib non-free non-free-firmware
EOF

# Add Liquorix Gaming Kernel Repository
cat << 'EOF' > "${CHROOT_DIR}/etc/apt/sources.list.d/liquorix.list"
deb [trusted=yes] http://liquorix.net/debian bookworm main
EOF

echo "[INFO] Configuring system packages inside chroot..."
chroot "${CHROOT_DIR}" /bin/bash << 'EOF'
export DEBIAN_FRONTEND=noninteractive

# Add 32-bit Multiarch for Steam & Proton
dpkg --add-architecture i386
apt-get update

# Core Live Boot & Hardware Packages
apt-get install -y --no-install-recommends \
    live-boot \
    live-config \
    systemd-sysv \
    dbus \
    network-manager \
    sudo \
    curl \
    wget \
    pciutils \
    usbutils \
    firmware-linux \
    firmware-linux-nonfree \
    firmware-misc-nonfree \
    pipewire \
    wireplumber \
    pipewire-pulse \
    rtkit

# Gaming & Graphics
apt-get install -y --no-install-recommends \
    mesa-vulkan-drivers \
    mesa-vulkan-drivers:i386 \
    libvulkan1 \
    libvulkan1:i386 \
    vulkan-tools \
    gamemode \
    libgamemode0 \
    mangohud \
    goverlay \
    gamescope \
    lutris \
    wine \
    winetricks \
    flatpak

# Lightweight Fast Desktop (KDE Plasma), Browsers, App Store & Global Menu
apt-get install -y --no-install-recommends \
    kde-plasma-desktop \
    plasma-workspace-wayland \
    sddm \
    konsole \
    dolphin \
    firefox-esr \
    chromium \
    vlc \
    spectacle \
    gparted \
    kcalc \
    synaptic \
    plasma-discover \
    plasma-discover-backend-flatpak \
    papirus-icon-theme \
    breeze-icon-theme \
    breeze-gtk-theme \
    qt6-style-kvantum \
    appmenu-gtk3-module \
    libdbusmenu-gtk3-4 \
    kdeplasma-addons \
    fonts-firacode \
    fonts-jetbrains-mono \
    fonts-inter

# AI Runtime, Software Managers & Must-Have Linux Power Tools
apt-get install -y --no-install-recommends \
    python3-minimal \
    python3-pip \
    python3-venv \
    sqlite3 \
    git \
    build-essential \
    nala \
    aptitude \
    btop \
    htop \
    fastfetch \
    neofetch \
    ripgrep \
    fd-find \
    fzf \
    bat \
    jq \
    tree \
    ncdu \
    micro \
    p7zip-full \
    unzip \
    zip \
    zsh \
    tmux

# Kernel Installation: Liquorix low-latency or fallback to Debian standard
apt-get install -y linux-image-liquorix-amd64 linux-headers-liquorix-amd64 || \
apt-get install -y linux-image-amd64

# Configure Default User
if ! id "jarvis" >/dev/null 2>&1; then
    useradd -m -s /bin/bash -G sudo,audio,video,input,render jarvis
    echo "jarvis:jarvis" | chpasswd
    echo "jarvis ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/jarvis
    chmod 0440 /etc/sudoers.d/jarvis
fi

# Enable SDDM autologin for Live session
mkdir -p /etc/sddm.conf.d
cat << 'AUTOLOGIN' > /etc/sddm.conf.d/autologin.conf
[Autologin]
User=jarvis
Session=plasmawayland
AUTOLOGIN

# Clean apt cache
apt-get clean
rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
EOF

# 5. Overlay Jarvis Ambient AI Core, HUD, Minimalist Themes & Wallpapers
echo "[INFO] Staging Jarvis Core, Knowledge Galaxy HUD, Wallpapers & Calamares installer..."
mkdir -p "${CHROOT_DIR}/opt/jarvis-core" "${CHROOT_DIR}/opt/jarvis-hud" "${CHROOT_DIR}/etc/calamares"

cp -r "${PROJECT_ROOT}/jarvis-core/"* "${CHROOT_DIR}/opt/jarvis-core/"
cp -r "${PROJECT_ROOT}/jarvis-hud/"* "${CHROOT_DIR}/opt/jarvis-hud/"
cp -r "${PROJECT_ROOT}/calamares-config/"* "${CHROOT_DIR}/etc/calamares/"

# Copy Chroot Overlays (Minimalist Papirus/Slate dotfiles, 4K Wallpapers, Desktop entries)
if [ -d "${PROJECT_ROOT}/iso-builder/config/includes.chroot" ]; then
    cp -r "${PROJECT_ROOT}/iso-builder/config/includes.chroot/"* "${CHROOT_DIR}/"
    if [ -d "${CHROOT_DIR}/home/jarvis" ]; then
        cp -r "${CHROOT_DIR}/etc/skel/." "${CHROOT_DIR}/home/jarvis/" 2>/dev/null || true
        chroot "${CHROOT_DIR}" chown -R jarvis:jarvis /home/jarvis || true
    fi
fi

# Optional user-added custom packages staged via Terminal / Software Center
if [ -f "${PROJECT_ROOT}/iso-builder/config/package-lists/user-custom.list.chroot" ]; then
    cp "${PROJECT_ROOT}/iso-builder/config/package-lists/user-custom.list.chroot" "${CHROOT_DIR}/tmp/user-custom.pkgs"
    chroot "${CHROOT_DIR}" /bin/bash -c '
        CUSTOM=$(grep -vE "^\s*(#|$)" /tmp/user-custom.pkgs | tr "\n" " ")
        if [ -n "$CUSTOM" ]; then
            apt-get update && apt-get install -y --no-install-recommends $CUSTOM || true
        fi
        rm -f /tmp/user-custom.pkgs
    '
fi

# Copy systemd unit and enable
mkdir -p "${CHROOT_DIR}/etc/systemd/system"
cp "${PROJECT_ROOT}/iso-builder/airootfs/etc/systemd/system/jarvis-core.service" \
   "${CHROOT_DIR}/etc/systemd/system/jarvis-core.service"

chroot "${CHROOT_DIR}" /bin/bash << 'EOF'
chmod +x /opt/jarvis-core/daemon.py /opt/jarvis-core/tools/*.py || true
chmod +x /usr/local/bin/jarvis-pkg /usr/local/bin/jarvis-theme 2>/dev/null || true
systemctl enable jarvis-core.service
systemctl enable NetworkManager.service
systemctl enable sddm.service
EOF

# 6. Extract Kernel & Initramfs for Live Boot
echo "[INFO] Extracting live kernel and initramfs..."
VMLINUZ=$(ls -1 "${CHROOT_DIR}/boot"/vmlinuz-* | sort -V | tail -n 1)
INITRD=$(ls -1 "${CHROOT_DIR}/boot"/initrd.img-* | sort -V | tail -n 1)

cp "${VMLINUZ}" "${ISO_DIR}/live/vmlinuz"
cp "${INITRD}" "${ISO_DIR}/live/initrd.img"

# 7. Unmount virtual filesystems prior to squashfs
cleanup

# 8. Compress Rootfs into Squashfs with Zstandard
echo "[INFO] Creating Zstandard compressed SquashFS (this takes a few minutes)..."
rm -f "${ISO_DIR}/live/filesystem.squashfs"
mksquashfs "${CHROOT_DIR}" "${ISO_DIR}/live/filesystem.squashfs" \
    -comp zstd \
    -Xcompression-level 19 \
    -b 1048576 \
    -noappend \
    -e boot/vmlinuz* -e boot/initrd.img*

# 9. Configure GRUB for BIOS & UEFI Hybrid Boot
cat << 'EOF' > "${ISO_DIR}/boot/grub/grub.cfg"
set default="0"
set timeout=5

menuentry "Jarvis OS (Debian 12 Bookworm - Low Latency Gaming & Local AI)" {
    linux /live/vmlinuz boot=live quiet splash components username=jarvis
    initrd /live/initrd.img
}

menuentry "Jarvis OS (Safe Graphics Mode - Nomodeset)" {
    linux /live/vmlinuz boot=live nomodeset components username=jarvis
    initrd /live/initrd.img
}
EOF

# 10. Generate Hybrid Bootable ISO
echo "[INFO] Packaging hybrid ISO via grub-mkrescue & xorriso..."
grub-mkrescue -o "${OUT_DIR}/${ISO_NAME}" "${ISO_DIR}" \
    -- -volid "JARVIS_OS" \
    -iso-level 3

echo "=========================================================="
echo " [SUCCESS] Debootstrap Live ISO Built Successfully!"
echo " Location: ${OUT_DIR}/${ISO_NAME}"
echo "=========================================================="
