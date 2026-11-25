#!/usr/bin/env python3
"""
Jarvis OS HUD Launcher
Ensures the local daemon is active and launches the 3D Knowledge Galaxy
in an isolated app window with Super+Space.
"""

import sys
import os
import time
import subprocess
import urllib.request

BASE_URL = "http://127.0.0.1:4700"

def is_daemon_alive():
    try:
        with urllib.request.urlopen(f"{BASE_URL}/status", timeout=1) as resp:
            return resp.status == 200
    except Exception:
        return False

def ensure_daemon():
    if not is_daemon_alive():
        daemon_script = os.path.join(os.path.dirname(__file__), "..", "daemon.py")
        subprocess.Popen([sys.executable, daemon_script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(20):
            time.sleep(0.15)
            if is_daemon_alive():
                break

def launch_browser_app():
    # Try Chrome/Chromium app-mode for seamless frameless HUD window
    candidates = ["google-chrome", "chromium", "brave-browser", "firefox", "xdg-open"]
    for c in candidates:
        if subprocess.call(["which", c], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
            if c in ["google-chrome", "chromium", "brave-browser"]:
                subprocess.Popen([c, f"--app={BASE_URL}", "--window-size=1200,800"])
            else:
                subprocess.Popen([c, BASE_URL])
            return

def main():
    ensure_daemon()
    launch_browser_app()

if __name__ == "__main__":
    main()
