#!/usr/bin/env python3
"""
Jarvis OS Calamares Hardware Detection & Driver Auto-Configuration Module
Runs in target chroot during installation to detect GPUs and tune system.
"""

import os
import subprocess
import libcalamares

def run_cmd(cmd, chroot=True):
    root_mount = libcalamares.target_env.root_mount_point if chroot else ""
    if chroot:
        return libcalamares.utils.target_env_call(cmd)
    else:
        return subprocess.call(cmd)

def detect_gpu():
    try:
        output = subprocess.check_output(["lspci", "-nn"], stderr=subprocess.DEVNULL).decode("utf-8")
    except Exception:
        output = ""
    return output

def configure_nvidia(root_path):
    libcalamares.utils.debug("Jarvis HWDetect: NVIDIA GPU identified. Configuring drivers...")
    # Blacklist nouveau
    modprobe_dir = os.path.join(root_path, "etc", "modprobe.d")
    os.makedirs(modprobe_dir, exist_ok=True)
    with open(os.path.join(modprobe_dir, "blacklist-nouveau.conf"), "w") as f:
        f.write("blacklist nouveau\noptions nouveau modeset=0\n")
    
    # Configure early DRM modeset in kernel parameters
    with open(os.path.join(modprobe_dir, "nvidia-modeset.conf"), "w") as f:
        f.write("options nvidia-drm modeset=1\n")

def configure_amd(root_path):
    libcalamares.utils.debug("Jarvis HWDetect: AMD GPU identified. Configuring RADV & ROCm...")
    # Default to RADV for gaming
    env_dir = os.path.join(root_path, "etc", "environment.d")
    os.makedirs(env_dir, exist_ok=True)
    with open(os.path.join(env_dir, "90-vulkan-radv.conf"), "w") as f:
        f.write("AMD_VULKAN_ICD=RADV\n")

def run():
    root_path = libcalamares.target_env.root_mount_point
    pci_info = detect_gpu()

    if "NVIDIA" in pci_info or "10de:" in pci_info:
        configure_nvidia(root_path)
    elif "AMD" in pci_info or "1002:" in pci_info:
        configure_amd(root_path)

    # Check for SSD/NVMe to optimize scheduler
    try:
        sys_block = os.listdir("/sys/block")
        has_nvme = any("nvme" in dev for dev in sys_block)
        if has_nvme:
            sysctl_d = os.path.join(root_path, "etc", "sysctl.d")
            os.makedirs(sysctl_d, exist_ok=True)
            with open(os.path.join(sysctl_d, "99-jarvis-io.conf"), "w") as f:
                f.write("vm.vfs_cache_pressure=50\nvm.swappiness=10\n")
    except Exception:
        pass

    return None
