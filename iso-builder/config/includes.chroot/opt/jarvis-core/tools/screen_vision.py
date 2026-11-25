"""
Jarvis OS Screen Vision Engine
Captures Wayland/X11 screen regions (grim/slurp) and feeds images
into local multimodal models (Qwen2-VL / MiniCPM-V) for UI debugging and OCR.
"""

import os
import sys
import json
import base64
import shutil
import subprocess
import logging
import urllib.request
from typing import Dict, Any, Optional

logger = logging.getLogger("jarvis.vision")

BASE_URL = "http://127.0.0.1:4700"
TEMP_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "..", "temp_capture.png")

class ScreenVision:
    def __init__(self, model_name: str = "bonsai27b-vision"):
        self.model_name = model_name

    def capture_screen(self, region: bool = True) -> Optional[str]:
        """Captures region or fullscreen using Wayland grim/slurp or fallback."""
        temp_path = os.path.abspath(TEMP_IMAGE_PATH)

        # Wayland capture
        if shutil.which("grim"):
            if region and shutil.which("slurp"):
                try:
                    area = subprocess.check_output(["slurp"], stderr=subprocess.DEVNULL).decode().strip()
                    if area:
                        subprocess.call(["grim", "-g", area, temp_path])
                        return temp_path
                except Exception:
                    pass
            subprocess.call(["grim", temp_path])
            return temp_path

        # Fallback to ImageGrab (Pillow)
        try:
            from PIL import ImageGrab
            img = ImageGrab.grab()
            img.save(temp_path, "PNG")
            return temp_path
        except Exception as e:
            logger.warning(f"Screen capture fallback failed: {e}")
            return None

    def encode_image_base64(self, image_path: str) -> str:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def inspect_screen(self, user_prompt: str = "Analyze this screen capture and explain any visible code, errors, or diagrams.") -> str:
        """Captures screen and sends base64 image to local vision LLM."""
        img_path = self.capture_screen(region=False)
        if not img_path or not os.path.exists(img_path):
            return "Unable to capture screen display."

        b64_data = self.encode_image_base64(img_path)
        
        # Try native Ollama /api/chat first (supports images array directly with think: false)
        try:
            ollama_url = "http://127.0.0.1:11434/api/chat"
            ollama_payload = {
                "model": self.model_name,
                "messages": [
                    {"role": "user", "content": user_prompt, "images": [b64_data]}
                ],
                "stream": False,
                "think": False
            }
            ollama_req = urllib.request.Request(
                ollama_url,
                data=json.dumps(ollama_payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(ollama_req, timeout=35) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                content = data.get("message", {}).get("content", "").strip()
                if content:
                    return content
        except Exception as e:
            logger.debug(f"Native Ollama /api/chat vision failed, trying fallback: {e}")

        payload = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64_data}"}}
                    ]
                }
            ],
            "max_tokens": 800
        }

        endpoints = [
            "http://127.0.0.1:11434/v1/chat/completions",
            "http://127.0.0.1:1234/v1/chat/completions"
        ]

        last_err = None
        for endpoint in endpoints:
            try:
                req = urllib.request.Request(
                    endpoint,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json", "Authorization": "Bearer ollama"}
                )
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    return data["choices"][0]["message"]["content"].strip()
            except Exception as e:
                last_err = e
                continue

        return f"Vision model ({self.model_name}) offline or busy: {last_err}"

def main():
    vision = ScreenVision()
    prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Explain what is visible on this screen."
    print("[JARVIS VISION] Capturing screen for analysis...")
    analysis = vision.inspect_screen(prompt)
    print("\n[JARVIS VISION ANALYSIS]:\n" + "=" * 50)
    print(analysis)
    print("=" * 50)

if __name__ == "__main__":
    main()
