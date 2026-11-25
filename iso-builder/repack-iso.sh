#!/usr/bin/env bash
# ==============================================================================
# Jarvis OS: Rapid ISO Unpack, Patch & Repack Pipeline
# Enables sub-2-minute turnarounds when testing Jarvis Core or HUD changes
# without re-downloading Debian packages or rebuilding the rootfs from scratch.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
WORK_DIR="/tmp/jarvis-repack"
EXTRACT_DIR="${WORK_DIR}/iso-extract"
SQUASH_DIR="${WORK_DIR}/squashfs-root"
OUT_DIR="${SCRIPT_DIR}/out"

INPUT_ISO="${1:-${OUT_DIR}/jarvis-os-debian-amd64.hybrid.iso}"
OUTPUT_ISO="${OUT_DIR}/jarvis-os-fast-repack.iso"

echo "=========================================================="
echo "        JARVIS OS: RAPID ISO UNPACK & REPACK PIPELINE     "
echo "=========================================================="

if [[ $EUID -ne 0 ]]; then
   echo "[ERROR] Root privileges required to preserve squashfs file ownership."
   exit 1
fi

if [[ ! -f "${INPUT_ISO}" ]]; then
    echo "[ERROR] Input ISO not found: ${INPUT_ISO}"
    echo "Usage: sudo ./repack-iso.sh [path-to-base-iso]"
    exit 1
fi

for cmd in xorriso unsquashfs mksquashfs; do
    command -v "${cmd}" >/dev/null 2>&1 || {
        echo "[ERROR] Missing required tool: ${cmd}. Install via: apt install -y xorriso squashfs-tools"
        exit 1
    }
done

# Clean and prepare workspace
rm -rf "${EXTRACT_DIR}" "${SQUASH_DIR}"
mkdir -p "${EXTRACT_DIR}" "${OUT_DIR}"

# 1. Extract ISO image
echo "[INFO] Extracting ISO content from ${INPUT_ISO}..."
xorriso -osirx -indev "${INPUT_ISO}" -extract / "${EXTRACT_DIR}"

SQUASHFS_FILE=$(find "${EXTRACT_DIR}" -name "filesystem.squashfs" | head -n 1)
if [[ -z "${SQUASHFS_FILE}" || ! -f "${SQUASHFS_FILE}" ]]; then
    echo "[ERROR] filesystem.squashfs not found in extracted ISO."
    exit 1
fi

# 2. Extract SquashFS filesystem
echo "[INFO] Unpacking SquashFS root filesystem..."
unsquashfs -d "${SQUASH_DIR}" "${SQUASHFS_FILE}"

# 3. Patch Jarvis Components & Desktop Customizations
echo "[INFO] Injecting updated Jarvis Core, HUD, themes, wallpapers & installer into rootfs..."
mkdir -p "${SQUASH_DIR}/opt/jarvis-core" "${SQUASH_DIR}/opt/jarvis-hud" "${SQUASH_DIR}/etc/calamares"

cp -r "${PROJECT_ROOT}/jarvis-core/"* "${SQUASH_DIR}/opt/jarvis-core/"
cp -r "${PROJECT_ROOT}/jarvis-hud/"* "${SQUASH_DIR}/opt/jarvis-hud/"
cp -r "${PROJECT_ROOT}/calamares-config/"* "${SQUASH_DIR}/etc/calamares/"

# Patch Chroot Overlays (Minimalist Papirus/Slate dotfiles, 4K Wallpapers, Desktop entries)
if [ -d "${PROJECT_ROOT}/iso-builder/config/includes.chroot" ]; then
    cp -r "${PROJECT_ROOT}/iso-builder/config/includes.chroot/"* "${SQUASH_DIR}/"
fi

# Ensure executable permissions
chmod +x "${SQUASH_DIR}/opt/jarvis-core/daemon.py"

# 4. Re-compress SquashFS using Zstandard
echo "[INFO] Re-compressing SquashFS with high-ratio Zstandard..."
rm -f "${SQUASHFS_FILE}"
mksquashfs "${SQUASH_DIR}" "${SQUASHFS_FILE}" \
    -comp zstd \
    -Xcompression-level 19 \
    -b 1048576 \
    -noappend

# 5. Re-generate MD5 sums if present
if [[ -f "${EXTRACT_DIR}/md5sum.txt" ]]; then
    echo "[INFO] Updating md5sum.txt..."
    (cd "${EXTRACT_DIR}" && find . -type f ! -path "./md5sum.txt" -exec md5sum {} + > md5sum.txt)
fi

# 6. Repack Bootable Hybrid ISO
echo "[INFO] Repacking bootable hybrid ISO..."
xorriso -as mkisofs \
    -r -V "JARVIS_OS" \
    -o "${OUTPUT_ISO}" \
    -J -l \
    -b isolinux/isolinux.bin \
    -c isolinux/boot.cat \
    -no-emul-boot -boot-load-size 4 -boot-info-table \
    -eltorito-alt-boot \
    -e boot/grub/efi.img \
    -no-emul-boot -isohybrid-gpt-basdat \
    "${EXTRACT_DIR}" 2>/dev/null || {
        # Fallback to standard xorriso repack if isolinux directory layout differs
        echo "[INFO] Repacking with grub-mkrescue fallback..."
        grub-mkrescue -o "${OUTPUT_ISO}" "${EXTRACT_DIR}" -- -volid "JARVIS_OS"
    }

echo "=========================================================="
echo " [SUCCESS] Rapid ISO Repack Completed!"
echo " Output path: ${OUTPUT_ISO}"
echo "=========================================================="
