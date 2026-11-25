#!/usr/bin/env python3
"""
Jarvis OS Multi-Theme & Appearance Engine
Supports instant switching between Apple macOS-inspired Cupertino themes and
curated Linux themes across KDE Plasma 6 Wayland and the interactive web Desktop Shell.
"""

import os
import json
import shutil
import subprocess
import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger("jarvis.theme_manager")

THEMES: Dict[str, Dict[str, Any]] = {
    "cupertino-dark": {
        "id": "cupertino-dark",
        "name": "Apple Cupertino Dark",
        "subtitle": "macOS-inspired frosted dark glass, left traffic lights, mesh curve",
        "color_scheme": "JarvisCupertinoDark",
        "wallpaper": "jarvis-cupertino-dark",
        "button_layout": "left",
        "is_dark": True,
        "accent": "#0A84FF",
        "preview_gradient": "linear-gradient(135deg, #0d162c 0%, #0a84ff 45%, #30d158 100%)",
    },
    "cupertino-light": {
        "id": "cupertino-light",
        "name": "Apple Cupertino Light",
        "subtitle": "macOS-inspired bright pearl aluminum, soft azure gradient glass",
        "color_scheme": "JarvisCupertinoLight",
        "wallpaper": "jarvis-cupertino-light",
        "button_layout": "left",
        "is_dark": False,
        "accent": "#007AFF",
        "preview_gradient": "linear-gradient(135deg, #f5f5f7 0%, #64d2ff 50%, #a8a2ff 100%)",
    },
    "zen": {
        "id": "zen",
        "name": "Minimalist Slate (Pop!_OS / Ubuntu)",
        "subtitle": "Distraction-free Catppuccin slate with Papirus icons",
        "color_scheme": "JarvisZen",
        "wallpaper": "jarvis-zen",
        "button_layout": "right",
        "is_dark": True,
        "accent": "#89B4FA",
        "preview_gradient": "linear-gradient(135deg, #181926 0%, #303446 50%, #89b4fa 100%)",
    },
    "nordic": {
        "id": "nordic",
        "name": "Nordic Arctic Frost",
        "subtitle": "Polar night slate with calm arctic frost blue & aurora tones",
        "color_scheme": "JarvisNordic",
        "wallpaper": "jarvis-nordic",
        "button_layout": "right",
        "is_dark": True,
        "accent": "#88C0D0",
        "preview_gradient": "linear-gradient(135deg, #2e3440 0%, #4c566a 50%, #88c0d0 100%)",
    },
    "cyber": {
        "id": "cyber",
        "name": "Jarvis Cyber HUD",
        "subtitle": "Obsidian tactical interface with neon cyan arc-reactor telemetry",
        "color_scheme": "JarvisCyber",
        "wallpaper": "jarvis-cyber",
        "button_layout": "right",
        "is_dark": True,
        "accent": "#00E5FF",
        "preview_gradient": "linear-gradient(135deg, #07090e 0%, #0f172a 50%, #00e5ff 100%)",
    },
}


class ThemeManager:
    """Manages visual desktop themes across KDE Plasma 6 and Jarvis state persistence."""

    def __init__(self, state_file: str = None):
        self.state_file = state_file or os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "state_mode.json")
        )

    def list_themes(self) -> List[Dict[str, Any]]:
        """Returns all registered desktop theme definitions."""
        return list(THEMES.values())

    def get_theme(self, theme_id: str) -> Dict[str, Any]:
        """Returns a theme definition by ID, defaulting cleanly to cupertino-dark."""
        return THEMES.get(theme_id, THEMES["cupertino-dark"])

    def apply_theme(self, theme_id: str, persist: bool = True) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Applies the selected theme locally.
        On KDE Plasma Linux, updates color scheme, wallpaper, icon theme, and KWin traffic-light buttons.
        """
        if theme_id not in THEMES:
            valid = ", ".join(THEMES.keys())
            return False, f"Unknown theme '{theme_id}'. Available: {valid}", {}

        theme = THEMES[theme_id]
        wp_path = f"/usr/share/wallpapers/{theme['wallpaper']}/contents/images/3840x2160.png"

        # 1. Apply KDE Plasma color scheme if running on Plasma Linux
        if shutil.which("plasma-apply-colorscheme"):
            try:
                subprocess.call(
                    ["plasma-apply-colorscheme", theme["color_scheme"]],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except Exception as exc:
                logger.debug(f"plasma-apply-colorscheme error: {exc}")

        # 2. Apply matching 4K wallpaper
        if shutil.which("plasma-apply-wallpaperimage") and os.path.exists(wp_path):
            try:
                subprocess.call(
                    ["plasma-apply-wallpaperimage", wp_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except Exception as exc:
                logger.debug(f"plasma-apply-wallpaperimage error: {exc}")

        # 3. Configure window button placement (Apple Left Traffic Lights vs Standard Right) + GTK Sync
        kwrite = shutil.which("kwriteconfig6") or shutil.which("kwriteconfig5")
        if kwrite:
            try:
                subprocess.call(
                    [kwrite, "--file", "kdeglobals", "--group", "Icons", "--key", "Theme", "Papirus-Dark"],
                    stderr=subprocess.DEVNULL,
                )
                if theme["button_layout"] == "left":
                    subprocess.call(
                        [kwrite, "--file", "kwinrc", "--group", "org.kde.kdecoration2", "--key", "ButtonsOnLeft", "XIA"],
                        stderr=subprocess.DEVNULL,
                    )
                    subprocess.call(
                        [kwrite, "--file", "kwinrc", "--group", "org.kde.kdecoration2", "--key", "ButtonsOnRight", ""],
                        stderr=subprocess.DEVNULL,
                    )
                else:
                    subprocess.call(
                        [kwrite, "--file", "kwinrc", "--group", "org.kde.kdecoration2", "--key", "ButtonsOnLeft", ""],
                        stderr=subprocess.DEVNULL,
                    )
                    subprocess.call(
                        [kwrite, "--file", "kwinrc", "--group", "org.kde.kdecoration2", "--key", "ButtonsOnRight", "IAX"],
                        stderr=subprocess.DEVNULL,
                    )
                qdbus = shutil.which("qdbus6") or shutil.which("qdbus")
                if qdbus:
                    subprocess.call([qdbus, "org.kde.KWin", "/KWin", "reconfigure"], stderr=subprocess.DEVNULL)
            except Exception as exc:
                logger.debug(f"KWin button update failed: {exc}")

        if persist:
            self._persist_theme_state(theme_id)

        return True, f"Applied desktop theme: {theme['name']}", theme

    def _persist_theme_state(self, theme_id: str):
        state = {"mode": "jarvis", "vram_freed": False, "mic_muted": False, "desktop_theme": theme_id}
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, "r", encoding="utf-8") as f:
                    state.update(json.load(f))
        except Exception:
            pass
        state["desktop_theme"] = theme_id
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2)
        except Exception as exc:
            logger.warning(f"Failed to persist theme state: {exc}")
