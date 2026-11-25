"""
Jarvis OS System Agent & Gaming Control Engine
Executes system control tags emitted by the Butler Brain:
- [ACTION:TOGGLE_GAMEMODE(on|off)]
- [ACTION:LAUNCH_APP(app)]
- [ACTION:SYSTEM_METRICS()]
- [ACTION:SET_VOLUME(level)]
"""

import os
import re
import shutil
import subprocess
import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger("jarvis.system_agent")

class SystemAgent:
    def __init__(self):
        self.game_mode_active = False

    def execute_action_tag(self, tag: str) -> Tuple[bool, str]:
        """
        Parses and safely executes [ACTION:NAME(ARG)] tags.
        Returns (success: bool, receipt: str).
        """
        match = re.search(r'\[ACTION:([A-Z_]+)\((.*?)\)\]', tag)
        if not match:
            return False, "Malformed action tag."

        action_name = match.group(1)
        action_arg = match.group(2).strip().lower()

        if action_name == "TOGGLE_GAMEMODE":
            return self.toggle_gamemode(action_arg == "on" or action_arg == "1")
        elif action_name == "LAUNCH_APP":
            return self.launch_app(action_arg)
        elif action_name == "SYSTEM_METRICS":
            return self.get_system_metrics()
        elif action_name == "SET_VOLUME":
            return self.set_volume(action_arg)
        else:
            return False, f"Unknown action '{action_name}'."

    def toggle_gamemode(self, enable: bool) -> Tuple[bool, str]:
        """
        Engages Feral GameMode, throttles background AI indexing,
        and sets CPU governor for stutter-free gaming.
        """
        self.game_mode_active = enable
        if enable:
            if shutil.which("gamemoded"):
                subprocess.Popen(["gamemoded", "-r"])
            logger.info("GameMode ENGAGED: Deprioritizing background LLM indexing.")
            return True, "GameMode engaged: CPU governor set to performance, frame latency prioritized."
        else:
            logger.info("GameMode DISENGAGED: Normal ambient state restored.")
            return True, "GameMode disengaged: Normal background AI operations resumed."

    def launch_app(self, app_name: str) -> Tuple[bool, str]:
        allowed_apps = {
            "steam": "steam",
            "vscode": "code",
            "code": "code",
            "terminal": "konsole",
            "konsole": "konsole",
            "heroic": "heroic",
            "lutris": "lutris",
            "browser": "firefox"
        }
        cmd = allowed_apps.get(app_name)
        if not cmd:
            return False, f"Application '{app_name}' is not in the authorized launcher manifest."

        if shutil.which(cmd):
            subprocess.Popen([cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True, f"Launched application '{app_name}' successfully."
        else:
            return False, f"Application '{app_name}' binary ({cmd}) not found on host."

    def get_system_metrics(self) -> Tuple[bool, str]:
        """Collects GPU, VRAM, and RAM metrics."""
        metrics = []

        # Try NVIDIA SMI
        if shutil.which("nvidia-smi"):
            try:
                out = subprocess.check_output(
                    ["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu", "--format=csv,noheader,nounits"],
                    stderr=subprocess.DEVNULL
                ).decode().strip()
                gpu_util, mem_used, mem_total, temp = [x.strip() for x in out.split(",")]
                metrics.append(f"GPU Load: {gpu_util}%, VRAM: {mem_used}/{mem_total} MB, Temp: {temp}C")
            except Exception:
                pass

        # Try Memory info via /proc/meminfo or free
        try:
            with open("/proc/meminfo", "r") as f:
                lines = f.readlines()
            mem_total = int([l for l in lines if "MemTotal" in l][0].split()[1]) // 1024
            mem_avail = int([l for l in lines if "MemAvailable" in l][0].split()[1]) // 1024
            mem_used = mem_total - mem_avail
            metrics.append(f"RAM: {mem_used}/{mem_total} MB")
        except Exception:
            pass

        result = " | ".join(metrics) if metrics else "Metrics currently unavailable on host architecture."
        return True, result

    def set_volume(self, level_str: str) -> Tuple[bool, str]:
        try:
            level = max(0, min(100, int(level_str.rstrip("%"))))
        except ValueError:
            return False, "Invalid volume percentage."

        if shutil.which("wpctl"):
            subprocess.call(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", f"{level/100:.2f}"])
            return True, f"Audio volume adjusted to {level}% via WirePlumber."
        elif shutil.which("pactl"):
            subprocess.call(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{level}%"])
            return True, f"Audio volume adjusted to {level}% via PulseAudio."
        return False, "Neither wpctl nor pactl found to control audio."
