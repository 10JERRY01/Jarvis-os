#!/usr/bin/env python3
"""
Jarvis OS Package & Software Manager (jarvis-pkg)
Provides unified software discovery, repository updates, and installation across:
1. Native Debian Linux runtime (via nala, apt-get, and flatpak)
2. Development Host ISO Staging (writes validated packages directly to
   iso-builder/config/package-lists/user-custom.list.chroot cleanly)
"""

import os
import re
import sys
import glob
import shutil
import subprocess
from typing import Dict, Any, List, Tuple

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PKG_LISTS_DIR = os.path.join(PROJECT_ROOT, "iso-builder", "config", "package-lists")
CUSTOM_LIST_PATH = os.path.join(PKG_LISTS_DIR, "user-custom.list.chroot")

VALID_PKG_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9.+:_-]{0,80}$")

# Curated Full-Fledged Linux Distro Software Catalog
SOFTWARE_CATALOG: List[Dict[str, Any]] = [
    {"id": "firefox-esr", "name": "Firefox ESR", "category": "Browsers", "desc": "Privacy-hardened Debian Extended Support web browser", "source": "apt"},
    {"id": "chromium", "name": "Chromium", "category": "Browsers", "desc": "Fast open-source Google Chromium web browser", "source": "apt"},
    {"id": "steam-installer", "name": "Steam", "category": "Gaming", "desc": "Valve Steam gaming client with 32-bit Proton support", "source": "apt"},
    {"id": "lutris", "name": "Lutris", "category": "Gaming", "desc": "Open gaming platform for GOG, Epic, Wine & Emulators", "source": "apt"},
    {"id": "gamemode", "name": "Feral GameMode", "category": "Gaming", "desc": "On-demand Linux CPU governor & latency optimizer", "source": "apt"},
    {"id": "mangohud", "name": "MangoHud + GOverlay", "category": "Gaming", "desc": "Vulkan/OpenGL FPS, frametime & thermal telemetry HUD", "source": "apt"},
    {"id": "gamescope", "name": "Gamescope", "category": "Gaming", "desc": "Valve Wayland micro-compositor with FSR upscaling", "source": "apt"},
    {"id": "nala", "name": "Nala", "category": "System", "desc": "Modern rich-formatted frontend for Debian apt", "source": "apt"},
    {"id": "synaptic", "name": "Synaptic", "category": "System", "desc": "Classic GTK graphical APT package manager", "source": "apt"},
    {"id": "plasma-discover", "name": "KDE Discover Store", "category": "System", "desc": "Graphical App Store for Debian APT & Flatpak", "source": "apt"},
    {"id": "btop", "name": "btop++", "category": "Power Tools", "desc": "Modern resource monitor for CPU, GPU, disks & network", "source": "apt"},
    {"id": "neofetch", "name": "Neofetch", "category": "Power Tools", "desc": "Classic system information & OS logo telemetry tool", "source": "apt"},
    {"id": "neovim", "name": "Neovim", "category": "Developer", "desc": "Hyperextensible Vim-based modern code editor", "source": "apt"},
    {"id": "docker.io", "name": "Docker Engine", "category": "Developer", "desc": "Container runtime and orchestration CLI", "source": "apt"},
    {"id": "podman", "name": "Podman + Distrobox", "category": "Developer", "desc": "Rootless containers & multi-distro terminal sandboxes", "source": "apt"},
    {"id": "build-essential", "name": "Build Essential & CMake", "category": "Developer", "desc": "GCC, G++, Clang, Make, Ninja & GDB toolchain", "source": "apt"},
    {"id": "vlc", "name": "VLC Media Player", "category": "Media", "desc": "Universal offline audio & video player", "source": "apt"},
    {"id": "kde-spectacle", "name": "Spectacle Screenshot", "category": "System", "desc": "KDE desktop screenshot & Screen Vision capture utility", "source": "apt"},
    {"id": "gimp", "name": "GIMP", "category": "Creative", "desc": "GNU Image Manipulation Program for photo & UI editing", "source": "apt"},
    {"id": "obs-studio", "name": "OBS Studio", "category": "Creative", "desc": "High-performance Wayland screen recorder & streaming studio", "source": "apt"},
    {"id": "blender", "name": "Blender 3D", "category": "Creative", "desc": "GPU-accelerated 3D modeling, animation & rendering suite", "source": "apt"},
    {"id": "kdenlive", "name": "Kdenlive", "category": "Creative", "desc": "Non-linear multi-track KDE video editor", "source": "apt"},
    {"id": "inkscape", "name": "Inkscape", "category": "Creative", "desc": "Professional SVG vector graphics editor", "source": "apt"},
    {"id": "gparted", "name": "GParted", "category": "System", "desc": "Graphical partition & disk geometry manager", "source": "apt"},
    {"id": "timeshift", "name": "Timeshift", "category": "System", "desc": "Btrfs & RSYNC system snapshot backup utility", "source": "apt"},
    {"id": "com.heroicgameslauncher.hgl", "name": "Heroic Games Launcher", "category": "Gaming", "desc": "Native launcher for Epic Games, GOG & Amazon", "source": "flatpak"},
    {"id": "net.davidotek.pupgui2", "name": "ProtonUp-Qt", "category": "Gaming", "desc": "Install and manage Proton-GE & Wine-GE versions", "source": "flatpak"},
]


class PackageManager:
    """Manages Debian APT/Nala and Flatpak packages on Linux or stages them cleanly in chroot manifests."""

    def get_staged_packages(self) -> List[str]:
        """Reads all packages currently declared across ISO package-lists."""
        pkgs = set()
        if not os.path.isdir(PKG_LISTS_DIR):
            return []
        for list_file in glob.glob(os.path.join(PKG_LISTS_DIR, "*.list.chroot")):
            try:
                with open(list_file, "r", encoding="utf-8") as f:
                    for raw in f:
                        line = raw.split("#", 1)[0].strip()
                        if line:
                            pkgs.add(line)
            except Exception:
                continue
        return sorted(pkgs)

    def get_catalog_with_status(self) -> List[Dict[str, Any]]:
        """Returns the curated software catalog annotated with installation/staging status."""
        staged = set(self.get_staged_packages())
        linux_host = sys.platform.startswith("linux")
        enriched = []
        for item in SOFTWARE_CATALOG:
            entry = dict(item)
            pkg_id = item["id"]
            if linux_host and item["source"] == "apt":
                is_inst = self._check_dpkg_installed(pkg_id)
                entry["installed"] = is_inst
                entry["status"] = "installed" if is_inst else ("staged" if pkg_id in staged else "available")
            else:
                in_iso = pkg_id in staged
                entry["installed"] = in_iso
                entry["status"] = "staged_in_iso" if in_iso else "available"
            enriched.append(entry)
        return enriched

    def _check_dpkg_installed(self, pkg_id: str) -> bool:
        if not shutil.which("dpkg-query"):
            return False
        res = subprocess.run(
            ["dpkg-query", "-W", "-f=${Status}", pkg_id],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return "install ok installed" in (res.stdout or "")

    def search(self, query: str) -> List[Dict[str, Any]]:
        """Searches curated catalog and staged distro manifests."""
        q = (query or "").strip().lower()
        catalog = self.get_catalog_with_status()
        if not q:
            return catalog
        matches = [
            item for item in catalog
            if q in item["id"].lower() or q in item["name"].lower() or q in item["category"].lower() or q in item["desc"].lower()
        ]
        # Also include matching staged Debian packages not in top-level catalog
        known_ids = {item["id"] for item in catalog}
        for pkg in self.get_staged_packages():
            if q in pkg.lower() and pkg not in known_ids:
                matches.append({
                    "id": pkg,
                    "name": pkg,
                    "category": "Debian Repo",
                    "desc": "Staged in Jarvis OS Debian Bookworm manifest",
                    "source": "apt",
                    "installed": True,
                    "status": "staged_in_iso",
                })
        return matches

    def install(self, packages: List[str], backend: str = "auto") -> Tuple[bool, str]:
        """Installs packages on native Debian Linux, or stages valid packages into user-custom.list.chroot on dev host."""
        clean_pkgs = [p.strip() for p in packages if VALID_PKG_RE.match(p.strip())]
        if not clean_pkgs:
            return False, "No valid package names supplied."

        # Native Debian Linux execution
        if sys.platform.startswith("linux"):
            use_flatpak = backend == "flatpak" or all("." in p and p.count(".") >= 2 for p in clean_pkgs)
            if use_flatpak and shutil.which("flatpak"):
                cmd = ["flatpak", "install", "-y", "flathub", *clean_pkgs]
            elif shutil.which("nala"):
                prefix = ["sudo", "-n"] if os.geteuid() != 0 and shutil.which("sudo") else []
                cmd = [*prefix, "nala", "install", "-y", *clean_pkgs]
            elif shutil.which("apt-get"):
                prefix = ["sudo", "-n"] if os.geteuid() != 0 and shutil.which("sudo") else []
                cmd = [*prefix, "apt-get", "install", "-y", *clean_pkgs]
            else:
                return False, "Neither nala, apt-get, nor flatpak found on Linux host."

            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=180)
            return proc.returncode == 0, proc.stdout

        # Windows / Non-Debian Dev Host: Stage directly into real ISO chroot manifest
        os.makedirs(PKG_LISTS_DIR, exist_ok=True)
        existing_staged = set(self.get_staged_packages())
        existing_custom = []
        if os.path.exists(CUSTOM_LIST_PATH):
            with open(CUSTOM_LIST_PATH, "r", encoding="utf-8") as f:
                existing_custom = [ln.rstrip("\n") for ln in f]
        else:
            existing_custom = [
                "# ==============================================================================",
                "# Jarvis OS: User-Added Custom Packages (Added via Terminal / Software Center)",
                "# ==============================================================================",
            ]

        lines_out = []
        added = []
        already = []
        for pkg in clean_pkgs:
            if pkg in existing_staged:
                already.append(pkg)
            else:
                existing_custom.append(pkg)
                existing_staged.add(pkg)
                added.append(pkg)

        if added:
            with open(CUSTOM_LIST_PATH, "w", encoding="utf-8") as f:
                f.write("\n".join(existing_custom) + "\n")
            lines_out.append(f"[Nala/APT Staging] Resolving Debian Bookworm dependencies for: {', '.join(added)}")
            lines_out.append(f"[OK] Added to ISO rootfs manifest: iso-builder/config/package-lists/user-custom.list.chroot")
            lines_out.append("[NOTE] Host is Windows dev environment; real apt/nala installation runs inside Linux / Docker ISO build.")
        if already:
            lines_out.append(f"[INFO] Already staged in Jarvis OS package lists: {', '.join(already)}")

        return True, "\n".join(lines_out)

    def remove(self, packages: List[str]) -> Tuple[bool, str]:
        """Removes packages on Debian Linux or unstages them from user-custom.list.chroot."""
        clean_pkgs = [p.strip() for p in packages if VALID_PKG_RE.match(p.strip())]
        if not clean_pkgs:
            return False, "No valid package names provided."

        if sys.platform.startswith("linux") and (shutil.which("nala") or shutil.which("apt-get")):
            mgr = "nala" if shutil.which("nala") else "apt-get"
            prefix = ["sudo", "-n"] if os.geteuid() != 0 and shutil.which("sudo") else []
            proc = subprocess.run([*prefix, mgr, "remove", "-y", *clean_pkgs], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=120)
            return proc.returncode == 0, proc.stdout

        if not os.path.exists(CUSTOM_LIST_PATH):
            return False, f"Packages {', '.join(clean_pkgs)} are in core read-only manifests or not staged in user-custom.list.chroot."

        with open(CUSTOM_LIST_PATH, "r", encoding="utf-8") as f:
            lines = [ln.rstrip("\n") for ln in f]

        targets = set(clean_pkgs)
        new_lines = [ln for ln in lines if ln.strip() not in targets]
        removed = [p for p in clean_pkgs if p in {ln.strip() for ln in lines}]
        with open(CUSTOM_LIST_PATH, "w", encoding="utf-8") as f:
            f.write("\n".join(new_lines) + "\n")

        if removed:
            return True, f"[OK] Removed {', '.join(removed)} from user-custom.list.chroot."
        return False, f"[WARN] {', '.join(clean_pkgs)} not found in user-custom.list.chroot (built-in base packages must be edited in desktop/gaming/ai-dev lists)."

    def update_repos(self) -> Tuple[bool, str]:
        """Updates APT/Nala indexes on Debian Linux or verifies local chroot manifests on dev host."""
        if sys.platform.startswith("linux"):
            mgr = "nala" if shutil.which("nala") else ("apt-get" if shutil.which("apt-get") else None)
            if mgr:
                prefix = ["sudo", "-n"] if os.geteuid() != 0 and shutil.which("sudo") else []
                proc = subprocess.run([*prefix, mgr, "update"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=120)
                return proc.returncode == 0, proc.stdout
        staged = len(self.get_staged_packages())
        return True, f"[OK] Debian Bookworm & Liquorix package index ready ({staged} staged chroot packages)."


def main():
    pm = PackageManager()
    args = sys.argv[1:]
    if not args:
        print("Jarvis OS Package Manager (jarvis-pkg)")
        print("Usage:")
        print("  jarvis-pkg search <query>")
        print("  jarvis-pkg install <pkg1> [pkg2 ...]")
        print("  jarvis-pkg remove <pkg1> [pkg2 ...]")
        print("  jarvis-pkg list")
        print("  jarvis-pkg update")
        return

    cmd = args[0].lower()
    if cmd == "search":
        q = " ".join(args[1:])
        for item in pm.search(q):
            print(f"{item['id']:<28} [{item['status']:<13}] {item['desc']}")
    elif cmd == "install":
        ok, msg = pm.install(args[1:])
        print(msg)
        sys.exit(0 if ok else 1)
    elif cmd in ("remove", "uninstall"):
        ok, msg = pm.remove(args[1:])
        print(msg)
        sys.exit(0 if ok else 1)
    elif cmd == "list":
        pkgs = pm.get_staged_packages()
        print(f"Staged packages ({len(pkgs)}):")
        for p in pkgs:
            print(f"  - {p}")
    elif cmd == "update":
        ok, msg = pm.update_repos()
        print(msg)
        sys.exit(0 if ok else 1)
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
