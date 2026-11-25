#!/usr/bin/env bash
# ==============================================================================
# Jarvis OS: Automated ISO Build Script
# Creates a bootable, live installation media with CachyOS kernel optimizations,
# pre-configured gaming runtimes, and the Jarvis Ambient AI Core.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="/tmp/jarvis-iso-work"
OUT_DIR="${SCRIPT_DIR}/out"

echo "=========================================================="
echo "          BUILDING JARVIS OS BOOTABLE ISO IMAGE           "
echo "=========================================================="

if [[ $EUID -ne 0 ]]; then
   echo "[ERROR] This script must be run as root (or via sudo)." 
   exit 1
fi

command -v mkarchiso >/dev/null 2>&1 || {
    echo "[ERROR] 'mkarchiso' not found. Please install 'archiso' package."
    exit 1
}

# Clean previous build artifacts
rm -rf "${WORK_DIR}"
mkdir -p "${WORK_DIR}" "${OUT_DIR}"

# Stage Jarvis Core into the live rootfs overlay
echo "[INFO] Staging Jarvis Ambient Core into /opt/jarvis-core..."
mkdir -p "${SCRIPT_DIR}/airootfs/opt/jarvis-core"
cp -r "${SCRIPT_DIR}/../jarvis-core/"* "${SCRIPT_DIR}/airootfs/opt/jarvis-core/"

echo "[INFO] Staging Jarvis HUD Viewer into /opt/jarvis-hud..."
mkdir -p "${SCRIPT_DIR}/airootfs/opt/jarvis-hud"
cp -r "${SCRIPT_DIR}/../jarvis-hud/"* "${SCRIPT_DIR}/airootfs/opt/jarvis-hud/"

# Set permissions
chmod 755 "${SCRIPT_DIR}/airootfs/opt/jarvis-core/daemon.py"

echo "[INFO] Invoking mkarchiso..."
mkarchiso -v \
    -w "${WORK_DIR}" \
    -o "${OUT_DIR}" \
    "${SCRIPT_DIR}"

echo "=========================================================="
echo " [SUCCESS] Jarvis OS ISO generated successfully!"
echo " Output path: ${OUT_DIR}"
echo "=========================================================="
