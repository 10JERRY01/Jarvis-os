# Jarvis OS (v1.0 Genesis · Debian Edition)

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
  - Steam (`i386` multiarch), Lutris, Proton compatibility, Feral GameMode, MangoHud, GOverlay, Gamescope, Wine, Docker, Podman, Distrobox, `btop`, `fastfetch`, `ripgrep`, `fzf`, and `uv`.
- **The Wi-Fi-Off Law**: Zero outbound telemetry and 100% vendored local UI assets.

---

## Repository Structure

```text
Jarvis-os/
├── .github/workflows/      # Cloud ISO builder (R2 + Releases) & GitHub Pages CI
├── calamares-config/       # Branded GUI installer + GPU hardware detection
├── docs/                   # Developer & operations documentation
├── iso-builder/            # Tri-Engine Debian ISO builder (live-build, debootstrap, repack)
├── jarvis-core/            # Local AI daemon, Brain/Voice/Hearing, Terminal & Pkg APIs
├── jarvis-hud/             # 100% offline Knowledge Galaxy & Apple-inspired Desktop Shell
├── preflight/              # 12-point integrity, latency & air-gap verification harness
├── website/                # Minimalist GitHub Pages website (Download Hub & Monetization)
└── showcase.py             # End-to-end subsystem demonstration script
```

---

## Quick Start

### 1. Build the Bootable Hybrid ISO

#### Option A: Windows / macOS / Linux via Docker Desktop
```powershell
# Ensure Docker Desktop is running
powershell -File iso-builder/docker-build-iso.ps1 -Engine debootstrap
```

#### Option B: Native Debian / Ubuntu Linux
```bash
cd iso-builder
sudo ./build-debootstrap-iso.sh
# Output: iso-builder/out/jarvis-os-debootstrap-amd64.hybrid.iso
```

#### Option C: Cloud Build via GitHub Actions
Push a version tag (e.g., `git tag v1.0.0 && git push origin v1.0.0`) or trigger `.github/workflows/build-v1-iso.yml` manually to compile the ISO in the cloud, upload to Cloudflare R2 (when secrets are set), and publish to GitHub Releases.

### 2. Hydrate Local Bonsai 27B Weights
Large `.gguf` weights are excluded from Git. On Linux after installing/booting Jarvis OS, run:
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

## License

Released under the [GNU General Public License v3.0](LICENSE).
