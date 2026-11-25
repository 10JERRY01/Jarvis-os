# Jarvis OS (v1.0 Genesis · Debian Edition)

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Debian Base](https://img.shields.io/badge/Base-Debian%2012%20Bookworm-A81D33.svg)](https://www.debian.org/)
[![Project Website](https://img.shields.io/badge/Website-GitHub%20Pages-0A84FF.svg)](https://10JERRY01.github.io/Jarvis-os/)

**Enterprise Debian Stability. Apple-Grade Minimalist Craft. Offline 27B Intelligence.**

Jarvis OS is an open-source Debian 12 (*Bookworm*) Linux distribution engineered for AI developers, power users, and gamers. It pairs a **Liquorix 1000Hz low-latency kernel** and **KDE Plasma 6 (Wayland)** desktop with a dual-environment architecture—allowing instant switching between the **3D Jarvis Ambient Core** and an **Apple macOS / Minimalist Linux Desktop Environment** that frees 100% of GPU VRAM on demand.

---

## Core Architecture

- **Dual-Environment & Multi-Theme Desktop**:
  - **Jarvis Ambient Core (`http://127.0.0.1:4700`)**: 100% offline 3D Knowledge Galaxy, local Bonsai 27B LLM chat, Total Recall FTS5 memory, AST Code RAG, Kokoro TTS, and Screen Vision (`Meta+Shift+S`).
  - **Desktop Environment (`Meta+Shift+M`)**: Unloads LLM weights from VRAM (`keep_alive: 0`), pauses audio capture, and engages curated visual presets: **Apple Cupertino Dark/Light** (global menu bar, left traffic-light controls, floating glass dock), **Minimalist Zen (Pop!_OS / Ubuntu)**, **Nordic Arctic**, and **Jarvis Cyber**.
- **Built-in Terminal & Package Manager**:
  - Pre-configured with `nala`, `apt`, `synaptic`, `plasma-discover` (Flatpak + APT Store), and `jarvis-pkg`.
  - AI Smart Shell (`?? <natural language>`) converts plain requests into safety-checked Linux commands.
- **High-FPS Gaming & Developer Stack**:
  - Steam (`i386` multiarch), Lutris, Proton compatibility, Feral GameMode, MangoHud, GOverlay, Gamescope, Wine, Docker, Podman, Distrobox, `btop`, `neofetch`, `ripgrep`, `fzf`, and `uv`.
- **The Wi-Fi-Off Law**: Zero outbound telemetry and 100% vendored local UI assets.

---

## Downloads & Website

- **Official Website (GitHub Pages)**: [`https://10JERRY01.github.io/Jarvis-os/`](https://10JERRY01.github.io/Jarvis-os/)
- **Releases & Checksums**: [`https://github.com/10JERRY01/Jarvis-os/releases`](https://github.com/10JERRY01/Jarvis-os/releases)
- **ISO Hosting Mirror**: Designed for **Internet Archive (`archive.org`)** / **Cloudflare R2** direct `.iso` distribution configured in [`website/config.js`](website/config.js).

---

## Quick Start

### 1. Build the Bootable Hybrid ISO (`v1.0.0`)

#### Option A: Cloud Build via GitHub Actions (Recommended from Windows / macOS)
Push a release tag (`git tag v1.0.0 && git push origin v1.0.0`) or run **Actions → Build & Publish Jarvis OS v1.0 Hybrid ISO** directly inside GitHub to build `jarvis-os-debootstrap-amd64.hybrid.iso` on Ubuntu Linux cloud runners.

#### Option B: Local Windows / macOS / Linux via Docker Desktop
```powershell
# Start Docker Desktop first, then execute:
powershell -File iso-builder/docker-build-iso.ps1 -Engine debootstrap
# Output: iso-builder/out/jarvis-os-debootstrap-amd64.hybrid.iso
```

#### Option C: Native Debian / Ubuntu Linux
```bash
cd iso-builder
sudo ./build-debootstrap-iso.sh
```

### 2. Hydrate Local Bonsai 27B Weights
Multi-gigabyte `.gguf` weights are excluded from Git. On Linux after installing or booting Jarvis OS, run:
```bash
bash jarvis-core/tools/setup_models.sh /path/to/Bonsai-27B-GGUF
```

### 3. Run Local Verification
```bash
python preflight/wifi_off_drill.py
python preflight/preflight.py
python showcase.py
```

---

## Support the Project

If Jarvis OS powers your workstation or inspires your setup, please consider supporting ongoing open-source development:

- **Buy Me a Coffee**: [`https://buymeacoffee.com/jerrymice45`](https://buymeacoffee.com/jerrymice45)
- **Patreon**: [`https://www.patreon.com/c/Jerry42`](https://www.patreon.com/c/Jerry42)

---

## License

Released under the [GNU General Public License v3.0](LICENSE).
