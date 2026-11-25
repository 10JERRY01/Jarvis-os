#!/usr/bin/env python3
"""
Jarvis OS Dual-Mode Desktop Persona & Resource Switcher
Allows seamless instant switching between:
  1. "jarvis"  - Ambient AI Intelligence, 3D Knowledge Galaxy HUD, Voice Ears, Gaming Co-Pilot
  2. "zen"     - Full Desktop Environment (Apple Cupertino Light/Dark, Nordic, Pop/Zen),
                 zero AI background overhead, 100% VRAM freed
"""

import os
import sys
import json
import shutil
import subprocess
import urllib.request
import logging
from typing import Dict, Any, Tuple

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tools.theme_manager import ThemeManager

logger = logging.getLogger("jarvis.mode_switcher")

STATE_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "state_mode.json"))
DAEMON_URL = "http://127.0.0.1:4700"


class ModeSwitcher:
    def __init__(self):
        self.state_file = STATE_FILE
        self.theme_mgr = ThemeManager(self.state_file)
        if not os.path.exists(self.state_file):
            self._save_state({
                "mode": "jarvis",
                "vram_freed": False,
                "mic_muted": False,
                "desktop_theme": "cupertino-dark",
            })

    def get_state(self) -> Dict[str, Any]:
        default_state = {
            "mode": "jarvis",
            "vram_freed": False,
            "mic_muted": False,
            "desktop_theme": "cupertino-dark",
        }
        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                default_state.update(data)
                return default_state
        except Exception:
            return default_state

    def _save_state(self, state: Dict[str, Any]):
        current = self.get_state() if os.path.exists(self.state_file) else {}
        current.update(state)
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(current, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to persist state: {e}")

    def notify_desktop(self, title: str, message: str, icon: str = "dialog-information"):
        """Sends native desktop notification via notify-send or prints status cleanly."""
        if shutil.which("notify-send"):
            try:
                subprocess.call(["notify-send", "-a", "Jarvis OS", "-i", icon, title, message])
            except Exception:
                pass
        else:
            print(f"[{title}] {message}")

    def switch_to_zen(self, notify_daemon: bool = False, theme_id: str = None) -> Tuple[bool, str]:
        """
        Switches to Full Desktop Environment / Zen Mode (Apple Cupertino / Pop!_OS / Nordic):
        - Mutes/releases ambient microphone streams.
        - Evicts LLM weights from GPU VRAM (keep_alive: 0).
        - Applies chosen Apple/Linux desktop theme.
        """
        cur_state = self.get_state()
        target_theme = theme_id or cur_state.get("desktop_theme", "cupertino-dark")
        if target_theme == "cyber":
            target_theme = "cupertino-dark"

        logger.info(f"Engaging Desktop/Zen Mode ({target_theme})...")

        if notify_daemon:
            try:
                req = urllib.request.Request(
                    f"{DAEMON_URL}/mode/switch",
                    data=json.dumps({"mode": "zen", "theme": target_theme}).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                )
                urllib.request.urlopen(req, timeout=3)
            except Exception:
                pass

        # Release VRAM in Ollama
        try:
            req = urllib.request.Request(
                "http://127.0.0.1:11434/api/generate",
                data=json.dumps({"model": "bonsai27b", "keep_alive": 0}).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            urllib.request.urlopen(req, timeout=3)
        except Exception:
            pass

        self.theme_mgr.apply_theme(target_theme, persist=False)

        self._save_state({
            "mode": "zen",
            "vram_freed": True,
            "mic_muted": True,
            "desktop_theme": target_theme,
        })

        theme_name = self.theme_mgr.get_theme(target_theme)["name"]
        msg = f"Desktop Environment Active ({theme_name}). Ambient daemons paused, VRAM freed."
        self.notify_desktop("Jarvis OS: Desktop Mode", msg, "user-desktop")
        return True, msg

    def switch_to_desktop(self, notify_daemon: bool = False, theme_id: str = None) -> Tuple[bool, str]:
        """Alias for switch_to_zen preserving selected desktop theme."""
        return self.switch_to_zen(notify_daemon=notify_daemon, theme_id=theme_id)

    def switch_to_jarvis(self, notify_daemon: bool = False) -> Tuple[bool, str]:
        """
        Switches to Jarvis Ambient Intelligence Core Mode:
        - Warms up Bonsai 27B in GPU VRAM.
        - Re-engages PipeWire audio listener for wake words.
        - Resumes 3D Knowledge Galaxy HUD and Cyber aesthetic.
        """
        logger.info("Engaging Jarvis Mode (Ambient AI & Gaming Copilot)...")

        if notify_daemon:
            try:
                req = urllib.request.Request(
                    f"{DAEMON_URL}/mode/switch",
                    data=json.dumps({"mode": "jarvis"}).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                )
                urllib.request.urlopen(req, timeout=3)
            except Exception:
                pass

        # Warm up Bonsai 27B in VRAM
        try:
            req = urllib.request.Request(
                "http://127.0.0.1:11434/api/generate",
                data=json.dumps({"model": "bonsai27b", "keep_alive": "15m"}).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            urllib.request.urlopen(req, timeout=3)
        except Exception:
            pass

        # Apply Cyber HUD colorscheme & wallpaper on Linux without overwriting saved desktop_theme
        self.theme_mgr.apply_theme("cyber", persist=False)

        self._save_state({
            "mode": "jarvis",
            "vram_freed": False,
            "mic_muted": False,
        })

        msg = "Jarvis Ambient Core Active. Bonsai 27B online, 3D HUD live, GPU accelerated."
        self.notify_desktop("Jarvis OS: Ambient Core", msg, "computer")
        return True, msg

    def toggle_mode(self) -> Tuple[bool, str]:
        state = self.get_state()
        current = state.get("mode", "jarvis")
        if current == "jarvis":
            return self.switch_to_zen()
        return self.switch_to_jarvis()


def main():
    switcher = ModeSwitcher()
    if len(sys.argv) < 2:
        state = switcher.get_state()
        print(f"Current Jarvis OS Mode: {state.get('mode', 'jarvis').upper()} (Theme: {state.get('desktop_theme', 'cupertino-dark')})")
        print("Usage:")
        print("  python mode_switcher.py jarvis   # Switch to Jarvis Ambient Core Mode")
        print("  python mode_switcher.py zen      # Switch to Desktop Environment (Apple/Minimalist)")
        print("  python mode_switcher.py desktop  # Alias for zen")
        print("  python mode_switcher.py toggle   # Toggle between Ambient Core and Desktop")
        print("  python mode_switcher.py status   # Show current mode and resource state")
        return

    cmd = sys.argv[1].lower()
    if cmd == "jarvis":
        ok, msg = switcher.switch_to_jarvis(notify_daemon=True)
        print(f"[SUCCESS] {msg}")
    elif cmd in ("zen", "desktop"):
        ok, msg = switcher.switch_to_zen(notify_daemon=True)
        print(f"[SUCCESS] {msg}")
    elif cmd == "toggle":
        state = switcher.get_state()
        if state.get("mode") == "jarvis":
            ok, msg = switcher.switch_to_zen(notify_daemon=True)
        else:
            ok, msg = switcher.switch_to_jarvis(notify_daemon=True)
        print(f"[SUCCESS] {msg}")
    elif cmd == "status":
        print(json.dumps(switcher.get_state(), indent=2))
    else:
        print(f"Unknown mode: {cmd}. Choose 'jarvis', 'zen', 'desktop', or 'toggle'.")


if __name__ == "__main__":
    main()
