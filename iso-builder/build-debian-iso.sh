#!/usr/bin/env bash
# ==============================================================================
# Jarvis OS: Automated Debian Live-Build ISO Generation Script
# Builds a bootable hybrid Debian ISO with low-latency kernel, gaming runtimes,
# developer tools, and the offline-first Jarvis Ambient AI Daemon.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
WORK_DIR="/tmp/jarvis-debian-live"
OUT_DIR="${SCRIPT_DIR}/out"

echo "=========================================================="
echo "      BUILDING JARVIS OS (DEBIAN EDITION) LIVE ISO        "
echo "=========================================================="

if [[ $EUID -ne 0 ]]; then
   echo "[ERROR] This script must be run as root (or via sudo)."
   exit 1
fi

command -v lb >/dev/null 2>&1 || {
    echo "[ERROR] 'live-build' (lb) not found."
    echo "[INFO] Install via: sudo apt-get install -y live-build debootstrap squashfs-tools xorriso grub-pc-bin grub-efi-amd64-bin"
    exit 1
}

# Clean previous working directories
mkdir -p "${WORK_DIR}" "${OUT_DIR}"
cd "${SCRIPT_DIR}"

echo "[INFO] Cleaning previous live-build state..."
lb clean --purge || true

echo "[INFO] Staging Jarvis Ambient Core into chroot overlay..."
mkdir -p "${SCRIPT_DIR}/config/includes.chroot/opt/jarvis-core"
cp -r "${PROJECT_ROOT}/jarvis-core/"* "${SCRIPT_DIR}/config/includes.chroot/opt/jarvis-core/"

echo "[INFO] Staging Jarvis Knowledge Galaxy HUD into chroot overlay..."
mkdir -p "${SCRIPT_DIR}/config/includes.chroot/opt/jarvis-hud"
cp -r "${PROJECT_ROOT}/jarvis-hud/"* "${SCRIPT_DIR}/config/includes.chroot/opt/jarvis-hud/"

echo "[INFO] Staging Calamares installer configuration..."
mkdir -p "${SCRIPT_DIR}/config/includes.chroot/etc/calamares"
cp -r "${PROJECT_ROOT}/calamares-config/"* "${SCRIPT_DIR}/config/includes.chroot/etc/calamares/"

# Systemd unit installation
mkdir -p "${SCRIPT_DIR}/config/includes.chroot/etc/systemd/system"
cp "${PROJECT_ROOT}/iso-builder/airootfs/etc/systemd/system/jarvis-core.service" \
   "${SCRIPT_DIR}/config/includes.chroot/etc/systemd/system/jarvis-core.service"

# Permissions
chmod +x "${SCRIPT_DIR}/config/includes.chroot/opt/jarvis-core/daemon.py"
chmod +x "${SCRIPT_DIR}/auto/config"

echo "[INFO] Running lb config..."
lb config

echo "[INFO] Executing lb build (this may take 15-30 minutes depending on network and cache)..."
lb build

# Relocate generated ISO
if ls live-image-amd64.hybrid.iso 1> /dev/null 2>&1; then
    mv live-image-amd64.hybrid.iso "${OUT_DIR}/jarvis-os-debian-amd64.hybrid.iso"
    echo "=========================================================="
    echo " [SUCCESS] Jarvis OS (Debian Edition) ISO Generated!"
    echo " Output path: ${OUT_DIR}/jarvis-os-debian-amd64.hybrid.iso"
    echo "=========================================================="
else
    echo "[WARN] Build finished. Check output directory or live-build logs."
fi
