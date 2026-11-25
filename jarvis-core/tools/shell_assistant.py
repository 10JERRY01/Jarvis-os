#!/usr/bin/env python3
"""
Jarvis OS Developer Smart Shell (??) & Git Assistant
Provides natural language terminal automation, safety rating,
automated conventional git commit generation, and compiler error diagnostics.
"""

import os
import sys
import re
import json
import subprocess
import urllib.request
import urllib.error
from typing import Dict, Any, Tuple

BASE_URL = "http://127.0.0.1:4700"

DANGEROUS_PATTERNS = [
    r"\brm\s+-r?f\b",
    r"\bmkfs\b",
    r"\bdd\b",
    r">\s*/dev/sd[a-z]",
    r"\bchmod\s+([0-7]{3,4}|-R)\s+/",
    r":\(\)\s*\{\s*:\|:&\s*\};:",
    r"\bkill\s+-9\s+1\b"
]

class ShellAssistant:
    def __init__(self):
        pass

    def evaluate_safety(self, command: str) -> Tuple[str, str]:
        """Classifies safety level: SAFE, CAUTION, or DANGEROUS."""
        for pattern in DANGEROUS_PATTERNS:
            if re.search(pattern, command):
                return "DANGEROUS", "Command contains destructive flags capable of permanent data loss."

        if any(w in command for w in ["rm ", "drop ", "truncate", "kill ", "pkill", "systemctl restart", "docker stop"]):
            return "CAUTION", "Command modifies system or service state."

        return "SAFE", "Read-only or non-destructive operation."

    def query_command(self, natural_language_prompt: str) -> str:
        """Asks the local brain to generate a precise Linux bash command."""
        system_instruction = (
            "You are the Jarvis OS Shell Engine. Convert the user request strictly into a single line of Linux Bash code. "
            "Output ONLY the command. Do not include markdown codeblocks, explanations, or commentary."
        )

        prompt = f"Convert to Linux bash command: {natural_language_prompt}"
        payload = json.dumps({
            "question": prompt,
            "system_override": system_instruction
        }).encode("utf-8")

        try:
            req = urllib.request.Request(f"{BASE_URL}/chat", data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                cmd = data.get("answer", "").strip()
                # Clean any markdown fences if present
                cmd = re.sub(r"^```[a-z]*\n?", "", cmd)
                cmd = re.sub(r"\n?```$", "", cmd)
                return cmd.strip()
        except Exception as e:
            return f"# [Error connecting to Jarvis core: {e}]"

    def smart_shell_cli(self, user_prompt: str):
        print(f"\n[JARVIS SHELL] Translating: '{user_prompt}'...")
        suggested_cmd = self.query_command(user_prompt)

        if suggested_cmd.startswith("# [Error"):
            print(suggested_cmd)
            return

        safety, reason = self.evaluate_safety(suggested_cmd)
        color = "\033[92m" if safety == "SAFE" else ("\033[93m" if safety == "CAUTION" else "\033[91m")
        reset = "\033[0m"

        print(f"\nCommand : \033[1m{suggested_cmd}{reset}")
        print(f"Safety  : {color}{safety}{reset} ({reason})")
        print("\nOptions : [Enter] Execute  |  [e] Edit  |  [c] Cancel")

        try:
            choice = input("Action  : ").strip().lower()
        except KeyboardInterrupt:
            print("\nAborted.")
            return

        if choice == "" or choice == "y":
            if safety == "DANGEROUS":
                confirm = input("⚠️ CRITICAL: Destructive command detected. Type 'EXECUTE' to proceed: ")
                if confirm != "EXECUTE":
                    print("Execution prevented.")
                    return
            print(f"\nExecuting: {suggested_cmd}\n" + "-" * 50)
            subprocess.call(suggested_cmd, shell=True)
        elif choice == "e":
            edited = input("Edit command: ").strip()
            if edited:
                subprocess.call(edited, shell=True)
        else:
            print("Cancelled.")

    def git_commit_assistant(self):
        """Analyzes staged git diff and generates a conventional commit."""
        try:
            diff = subprocess.check_output(["git", "diff", "--staged"], stderr=subprocess.DEVNULL).decode("utf-8")
        except Exception:
            diff = ""

        if not diff.strip():
            print("[JARVIS GIT] No staged changes found. Run 'git add <files>' first.")
            return

        print("[JARVIS GIT] Analyzing staged diff with local brain...")
        truncated_diff = diff[:4000]  # Stay within optimal context
        prompt = (
            "You are an expert Git commit engineer. Analyze this git diff and generate a Conventional Commit message "
            "(feat:, fix:, docs:, style:, refactor:, test:, chore:). "
            "First line: conventional summary under 72 chars. Followed by 2-3 bullet points explaining the changes.\n\n"
            f"GIT DIFF:\n{truncated_diff}"
        )

        payload = json.dumps({"question": prompt}).encode("utf-8")
        try:
            req = urllib.request.Request(f"{BASE_URL}/chat", data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                commit_msg = data.get("answer", "").strip()

            print("\nProposed Commit Message:\n" + "=" * 50)
            print(commit_msg)
            print("=" * 50)

            choice = input("\nCommit with this message? [Y/n/e]: ").strip().lower()
            if choice in ["", "y", "yes"]:
                subprocess.call(["git", "commit", "-m", commit_msg])
                print("[SUCCESS] Changes committed successfully.")
            elif choice == "e":
                custom = input("Enter revised message: ").strip()
                if custom:
                    subprocess.call(["git", "commit", "-m", custom])
                    print("[SUCCESS] Changes committed successfully.")
        except Exception as e:
            print(f"[ERROR] Failed to query local brain: {e}")

def main():
    assistant = ShellAssistant()
    if len(sys.argv) < 2:
        print("Usage:")
        print("  ?? <natural language query>   # Smart Shell Assistant")
        print("  jarvis commit                 # Automated Conventional Commit")
        return

    arg = sys.argv[1]
    if arg == "commit":
        assistant.git_commit_assistant()
    else:
        full_query = " ".join(sys.argv[1:])
        assistant.smart_shell_cli(full_query)

if __name__ == "__main__":
    main()
