#!/usr/bin/env python3
"""
Jarvis OS Command Line Interface (jarvis-cli)
Allows developers to interact with the ambient core, switch brains & themes,
install Linux packages, store memories, and toggle game mode or desktop environment.
"""

import sys
import json
import urllib.request
import urllib.error
import argparse

BASE_URL = "http://127.0.0.1:4700"


def cmd_status():
    try:
        with urllib.request.urlopen(f"{BASE_URL}/status", timeout=3) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print("==================================================")
            print("            JARVIS OS AMBIENT STATUS              ")
            print("==================================================")
            print(f" Status        : {data.get('status').upper()}")
            print(f" Current Mode  : {data.get('current_mode', 'jarvis').upper()}")
            print(f" Desktop Theme : {data.get('desktop_theme', 'cupertino-dark')}")
            print(f" Active Brain  : {data.get('active_brain')}")
            print(f" Voice Profile : {data.get('voice_profile')}")
            print(f" Air-Gapped    : {data.get('local_only')}")
            print("==================================================")
    except Exception as e:
        print(f"[ERROR] Could not reach Jarvis daemon: {e}")


def cmd_brain(name: str):
    try:
        payload = json.dumps({"brain": name}).encode("utf-8")
        req = urllib.request.Request(f"{BASE_URL}/brain/switch", data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print(f"[JARVIS] {data.get('message')}")
    except Exception as e:
        print(f"[ERROR] Failed to switch brain: {e}")


def cmd_ask(question: str):
    try:
        payload = json.dumps({"question": question}).encode("utf-8")
        req = urllib.request.Request(f"{BASE_URL}/chat", data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print(f"\n[JARVIS ({data.get('brain')})]: {data.get('answer')}\n")
    except Exception as e:
        print(f"[ERROR] Failed to query Jarvis: {e}")


def cmd_remember(phrase: str):
    try:
        payload = json.dumps({"phrase": phrase}).encode("utf-8")
        req = urllib.request.Request(f"{BASE_URL}/remember", data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("success"):
                print(f"[JARVIS MEMORY] Stored: {data.get('title')} -> {data.get('path')}")
            else:
                print(f"[ERROR] Memory write failed: {data.get('error')}")
    except Exception as e:
        print(f"[ERROR] Failed to communicate with memory core: {e}")


def cmd_mode(target: str):
    try:
        if target == "status":
            with urllib.request.urlopen(f"{BASE_URL}/mode/status", timeout=3) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                print(f"[JARVIS MODE] Current: {data.get('mode', 'jarvis').upper()} | Theme: {data.get('desktop_theme', 'cupertino-dark')} (VRAM Freed: {data.get('vram_freed')}, Muted: {data.get('mic_muted')})")
        else:
            payload = json.dumps({"mode": target}).encode("utf-8")
            req = urllib.request.Request(f"{BASE_URL}/mode/switch", data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                print(f"[JARVIS MODE] {data.get('message')}")
    except Exception as e:
        print(f"[ERROR] Failed to switch mode: {e}")


def cmd_theme(target: str):
    try:
        if target == "list":
            with urllib.request.urlopen(f"{BASE_URL}/themes", timeout=3) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                print(f"Active Desktop Theme: {data.get('active_theme')}")
                for t in data.get("themes", []):
                    mark = "*" if t["id"] == data.get("active_theme") else " "
                    print(f" {mark} {t['id']:<18} {t['name']} ({t['subtitle']})")
        else:
            payload = json.dumps({"theme": target}).encode("utf-8")
            req = urllib.request.Request(f"{BASE_URL}/themes/apply", data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                print(f"[JARVIS THEME] {data.get('message')}")
    except Exception as e:
        print(f"[ERROR] Failed to configure theme: {e}")


def cmd_install(packages: list):
    try:
        payload = json.dumps({"packages": packages}).encode("utf-8")
        req = urllib.request.Request(f"{BASE_URL}/packages/install", data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print(data.get("output", ""))
    except Exception as e:
        print(f"[ERROR] Package installation failed: {e}")


def cmd_gamemode(state: str):
    cmd_ask(f"Set game mode to {state}")


def cmd_metrics():
    cmd_ask("What are the current system metrics?")


def main():
    parser = argparse.ArgumentParser(description="Jarvis OS CLI Utility")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("status", help="Check ambient core status")

    brain_parser = subparsers.add_parser("brain", help="Switch LLM brain")
    brain_parser.add_argument("name", choices=["local", "claude", "gemini"], help="Brain target")

    ask_parser = subparsers.add_parser("ask", help="Query Jarvis")
    ask_parser.add_argument("question", help="The question or prompt")

    rem_parser = subparsers.add_parser("remember", help="Save a memory into the Knowledge Galaxy")
    rem_parser.add_argument("phrase", help="Memory text")

    game_parser = subparsers.add_parser("gamemode", help="Toggle gaming performance mode")
    game_parser.add_argument("state", choices=["on", "off"], help="GameMode state")

    mode_parser = subparsers.add_parser("mode", help="Switch between Jarvis Ambient Core and Desktop Environment")
    mode_parser.add_argument("target", choices=["jarvis", "zen", "desktop", "toggle", "status"], help="Target mode")

    theme_parser = subparsers.add_parser("theme", help="List or apply Apple/Minimalist/Cyber desktop themes")
    theme_parser.add_argument("target", help="Theme ID (list | cupertino-dark | cupertino-light | zen | nordic | cyber)")

    inst_parser = subparsers.add_parser("install", help="Install Debian/Flatpak software on Jarvis OS")
    inst_parser.add_argument("packages", nargs="+", help="Package name(s)")

    subparsers.add_parser("metrics", help="Query GPU/VRAM/RAM hardware metrics")

    args = parser.parse_args()

    if args.command == "status":
        cmd_status()
    elif args.command == "mode":
        cmd_mode(args.target)
    elif args.command == "theme":
        cmd_theme(args.target)
    elif args.command == "install":
        cmd_install(args.packages)
    elif args.command == "brain":
        cmd_brain(args.name)
    elif args.command == "ask":
        cmd_ask(args.question)
    elif args.command == "remember":
        cmd_remember(args.phrase)
    elif args.command == "gamemode":
        cmd_gamemode(args.state)
    elif args.command == "metrics":
        cmd_metrics()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
