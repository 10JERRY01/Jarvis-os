# Jarvis OS (Debian Edition) · Developer & Engineering Guide

Welcome to the internal engineering codebase for **Jarvis OS (Debian Edition)** — engineered specifically for local AI/ML development, coding, learning, and high-FPS low-latency gaming.

---

## 1. System Architecture Overview

```
+-----------------------------------------------------------------------------------+
|                        JARVIS HUD & 3D GALAXY (Port 4700)                         |
|  - WebGL / Canvas Starfield         - Voice Waveform & Hands-Free Interaction     |
|  - Real-Time Node Exploration       - Live Latency & Hybrid Brain Badge           |
+-----------------------------------------------------------------------------------+
                                         | (HTTP / WebSocket)
+-----------------------------------------------------------------------------------+
|                        JARVIS AMBIENT CORE DAEMON                                 |
|  - Brain: Ollama / llama.cpp / Claude / Gemini hybrid dispatcher                  |
|  - Voice: Chunked sentence synthesis (~170 chars) & WAV disk caching              |
|  - Ears: 16kHz audio capture, 700ms silence + 900ms finish window buffering       |
|  - Memory: SQLite FTS5 + Markdown storage for "Total Recall"                      |
+-----------------------------------------------------------------------------------+
                                         |
+-----------------------------------------------------------------------------------+
|                        DEBIAN OS RUNTIMES & KERNEL                                |
|  - Debian 12 (Bookworm) / Testing + Liquorix / XanMod Low-Latency Gaming Kernel   |
|  - Steam (i386 multiarch), Proton GE, GameMode, MangoHud for gaming               |
|  - Docker CE (.deb), Podman, Distrobox, NVIDIA CUDA 12.x / ROCm, uv               |
+-----------------------------------------------------------------------------------+
```

---

## 2. Directory Structure

- `jarvis-core/`: The ambient system daemon.
  - `brain/brain.py`: The LLM dispatcher with stable prompt prefixing and butler persona.
  - `voice/voice.py`: Sentence-packed chunked speech synthesizer (~170 chars) with disk caching.
  - `ears/hear.py`: Wake-word detection and Whisper speech-to-text integration.
  - `memory/memory.py`: Markdown file writer & SQLite FTS5 live search indexer.
  - `daemon.py`: Central service running on `http://127.0.0.1:4700`.
  - `tools/jarvis_cli.py`: The `jarvis` CLI command.
- `jarvis-hud/`: The desktop graphical overlay and 3D Knowledge Galaxy.
  - `viewer/index.html`: The 100% offline, vendored HUD and starfield graph interface.
  - `viewer/graph-data.js`: Live-updated graph data file.
- `preflight/`: Automated validation test suites.
  - `preflight.py`: End-to-end latency budget audit harness.
  - `wifi_off_drill.py`: Network isolation and air-gap verification script.
- `iso-builder/`: Debian `live-build` (lb) harness.
  - `auto/config`: Core live-build bootstrap configuration.
  - `config/package-lists/`: Debian package lists (`base`, `desktop`, `gaming`, `ai-dev`).
  - `config/archives/`: Custom APT repositories (Liquorix gaming kernel, NVIDIA CUDA, Docker).
  - `config/hooks/live/`: Chroot post-bootstrap hooks (multiarch, systemd services, RT priorities).
  - `build-debian-iso.sh`: Automated Debian ISO build script.

---

## 3. Quick Start & Local Testing

### Step 1: Start the Jarvis Core Daemon
```bash
python jarvis-core/daemon.py
```

### Step 2: Open the 3D Knowledge Galaxy HUD
In any browser, navigate to:
```
http://127.0.0.1:4700
```
*(Tip: Add `?mute=1` to the URL for silent testing).*

### Step 3: Run the Preflight Latency Test
```bash
python preflight/preflight.py
```

### Step 4: Run the Wi-Fi-Off Air-Gap Drill
```bash
python preflight/wifi_off_drill.py
```

### Step 5: Test the CLI Tool, Themes & Package Manager
```bash
python jarvis-core/tools/jarvis_cli.py status
python jarvis-core/tools/jarvis_cli.py ask "What are the core capabilities of Jarvis OS?"
python jarvis-core/tools/jarvis_cli.py remember "Jarvis OS uses a Debian base with Liquorix low-latency kernel for gaming and ML."
python jarvis-core/tools/jarvis_cli.py mode desktop   # Switch to Apple/Multi-Theme Desktop Environment & free VRAM
python jarvis-core/tools/jarvis_cli.py theme list     # List Apple Cupertino Dark/Light, Zen, Nordic, Cyber themes
python jarvis-core/tools/jarvis_cli.py theme cupertino-dark
python jarvis-core/tools/jarvis_cli.py install obs-studio gimp
python jarvis-core/tools/jarvis_cli.py mode jarvis    # Switch back to Ambient AI HUD & warm up VRAM
```

---

## 4. Apple Cupertino, Minimalist Themes, Dock & Software Center

Jarvis OS ships with a dual-environment desktop system allowing instant transitions between the **3D Jarvis Ambient Core** and a **Full-Fledged Desktop Environment** (`http://127.0.0.1:4700` & KDE Plasma 6 Wayland):
- **Apple Cupertino Dark & Light (`JarvisCupertinoDark` / `JarvisCupertinoLight`)**: Frosted glass top global menu bar (`appmenu`), left-side macOS traffic-light window controls (`ButtonsOnLeft=XIA`), floating dock, and fluid 4K mesh wallpapers.
- **Minimalist Zen (`JarvisZen`)**: Clean Pop!_OS / Ubuntu aesthetic using `Papirus-Dark` icons, `Inter` typography, and slate geometry.
- **Nordic Arctic (`JarvisNordic`)**: Polar frost night theme with aurora backdrop.
- **Jarvis Cyber HUD (`JarvisCyber`)**: Obsidian cyan holographic mode with 3D Knowledge Galaxy.
- **Terminal & Linux Software Management**: Pre-configured with `nala`, `aptitude`, `synaptic`, `plasma-discover` (Flatpak + APT App Store), and `jarvis-pkg` CLI/API.
- **Panel & Dock**: Slim macOS-style top menu bar (height 28) with global app menu, clock, Control Center, Spotlight search (`Ctrl+K`), and bottom floating dock (`plasma-org.kde.plasma.desktop-appletsrc`) pinning Firefox ESR, Konsole, Dolphin, Discover Store, Lutris, Mode Switcher, HUD, Spectacle, and Settings.
- **Pre-installed Software Suites**:
  - **Web Browsers**: Firefox ESR, Chromium
  - **Gaming Runtimes**: Steam, Lutris, Feral GameMode, MangoHud, GOverlay, Gamescope, Wine, Winetricks, Flatpak
  - **Power-User CLI & GUI Tools**: `btop`, `fastfetch`, `ripgrep`, `fd-find`, `fzf`, `jq`, `bat`, `micro`, `ncdu`, `vlc`, `spectacle`, `gparted`, `kcalc`, `kolourpaint`
- **Keyboard Shortcuts**:
  - `Super + Space`: Launch Jarvis HUD & 3D Knowledge Galaxy
  - `Meta + Shift + M`: Toggle between Jarvis Ambient Mode and Zen Minimalist Mode
  - `Meta + Shift + S`: Screen Vision Inspector with Bonsai 27B Vision

---

## 5. Building the Bootable Debian ISO Image (Tri-Engine Pipeline)

Jarvis OS supports three complementary Debian build engines:

### Engine 1: Declarative Debian live-build (Production Releases)
Standard Debian declarative build tree using `lb config` and `lb build`.
```bash
cd iso-builder
sudo ./build-debian-iso.sh
```
*On Windows via Docker:*
```powershell
powershell -File iso-builder/docker-build-iso.ps1 -Engine live-build
```

### Engine 2: Standalone debootstrap Pipeline (Minimal & Granular)
Direct `debootstrap` chroot, installing the Liquorix gaming kernel, custom systemd units, and packaging SquashFS with Zstandard level 19 compression.
```bash
cd iso-builder
sudo ./build-debootstrap-iso.sh
```
*On Windows via Docker:*
```powershell
powershell -File iso-builder/docker-build-iso.ps1 -Engine debootstrap
```

### Engine 3: Rapid ISO Repacker (Sub-2-Minute Prototyping)
Unpacks existing SquashFS and repacks with updated Jarvis Core, HUD, and configuration files without re-downloading Debian packages.
```bash
cd iso-builder
sudo ./repack-iso.sh out/jarvis-os-debian-amd64.hybrid.iso
```
*On Windows via Docker:*
```powershell
powershell -File iso-builder/docker-build-iso.ps1 -Engine repack
```
