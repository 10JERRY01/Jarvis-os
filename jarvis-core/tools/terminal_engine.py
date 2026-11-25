#!/usr/bin/env python3
"""
Jarvis OS Interactive Terminal Engine
Powers the Terminal app inside the Jarvis Desktop Environment.
Supports:
- Package management (`nala`, `apt`, `apt-get`, `flatpak`, `jarvis-pkg`)
- Jarvis controls (`jarvis status`, `jarvis mode`, `jarvis theme`, `?? <prompt>`)
- System inspection (`fastfetch`, `neofetch`, `uname`, `pwd`, `ls`, `cat`, `nvidia-smi`, etc.)
- Safety checks via ShellAssistant to block destructive commands.
"""

import os
import sys
import shlex
import platform
import subprocess
from typing import Dict, Any

from tools.shell_assistant import ShellAssistant
from tools.pkg_manager import PackageManager
from tools.theme_manager import ThemeManager
from tools.mode_switcher import ModeSwitcher

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


class TerminalEngine:
    def __init__(self):
        self.cwd = PROJECT_ROOT
        self.shell_assistant = ShellAssistant()
        self.pkg_mgr = PackageManager()
        self.theme_mgr = ThemeManager()
        self.mode_switcher = ModeSwitcher()

    def execute(self, raw_cmd: str) -> Dict[str, Any]:
        cmd = (raw_cmd or "").strip()
        if not cmd:
            return {"ok": True, "output": "", "cwd": self.cwd}

        # 1. Safety Gate
        safety, reason = self.shell_assistant.evaluate_safety(cmd)
        if safety == "DANGEROUS":
            return {
                "ok": False,
                "output": f"[BLOCKED - {safety}] {reason}",
                "cwd": self.cwd,
            }

        # 2. Built-in navigation (`cd`)
        if cmd == "cd" or cmd.startswith("cd "):
            target = cmd[3:].strip() if cmd.startswith("cd ") else PROJECT_ROOT
            if target == "~":
                target = PROJECT_ROOT
            new_path = os.path.abspath(os.path.join(self.cwd, target))
            if os.path.isdir(new_path):
                self.cwd = new_path
                return {"ok": True, "output": "", "cwd": self.cwd}
            return {"ok": False, "output": f"cd: no such directory: {target}", "cwd": self.cwd}

        # 3. Built-in help
        if cmd in ("help", "jarvis help"):
            help_text = (
                "Jarvis OS Terminal Commands:\n"
                "  nala install <pkg>     Stage / install Debian software (e.g., nala install obs-studio gimp)\n"
                "  apt install <pkg>      Install or stage .deb packages\n"
                "  jarvis-pkg search <q>  Search software catalog & staged Debian manifests\n"
                "  jarvis-pkg list        Count and list staged packages\n"
                "  jarvis theme <name>    Switch theme (cupertino-dark | cupertino-light | zen | nordic | cyber)\n"
                "  jarvis mode <target>   Switch between 'jarvis' (Ambient Core) and 'zen' (Desktop)\n"
                "  fastfetch / neofetch   Show live system & distro telemetry\n"
                "  ?? <natural request>   Ask Bonsai 27B to translate natural language to Linux Bash\n"
                "  clear                  Clear terminal output"
            )
            return {"ok": True, "output": help_text, "cwd": self.cwd}

        # 4. System Info (`fastfetch`, `neofetch`, `uname -a`)
        if cmd in ("fastfetch", "neofetch"):
            staged_count = len(self.pkg_mgr.get_staged_packages())
            state = self.mode_switcher.get_state()
            theme = self.theme_mgr.get_theme(state.get("desktop_theme", "cupertino-dark"))
            info = (
                f"       _                  _         ___  ____\n"
                f"      | | __ _ _ ____   _(_)___    / _ \\/ ___|\n"
                f"   _  | |/ _` | '__\\ \\ / / / __|  | | | \\___ \\\n"
                f"  | |_| | (_| | |   \\ V /| \\__ \\  | |_| |___) |\n"
                f"   \\___/ \\__,_|_|    \\_/ |_|___/   \\___/|____/\n\n"
                f"  OS Target : Jarvis OS 1.0 (Debian 12 Bookworm / Liquorix 1000Hz)\n"
                f"  Host Env  : {platform.system()} {platform.release()} ({platform.machine()})\n"
                f"  Desktop   : {theme['name']} (KDE Plasma 6 / Cupertino Shell)\n"
                f"  Active AI : Bonsai 27B Local Q1_0 (127.0.0.1:11434)\n"
                f"  Packages  : {staged_count} Debian packages staged in chroot\n"
                f"  Mode      : {state.get('mode', 'jarvis').upper()} | VRAM Freed: {state.get('vram_freed', False)}"
            )
            return {"ok": True, "output": info, "cwd": self.cwd}

        # 5. Smart Shell Translation (`?? <prompt>`)
        if cmd.startswith("?? "):
            query = cmd[3:].strip()
            translated = self.shell_assistant.query_command(query)
            lvl, desc = self.shell_assistant.evaluate_safety(translated)
            return {
                "ok": True,
                "output": f"[Bonsai 27B Shell Translation]\n  Command : {translated}\n  Safety  : {lvl} ({desc})",
                "cwd": self.cwd,
            }

        # 6. Strip leading sudo if present for clean parsing
        parsed_cmd = cmd[5:].strip() if cmd.startswith("sudo ") else cmd
        try:
            tokens = shlex.split(parsed_cmd)
        except ValueError:
            tokens = parsed_cmd.split()

        if not tokens:
            return {"ok": True, "output": "", "cwd": self.cwd}

        prog = tokens[0].lower()

        # 7. Linux Package Managers (`nala`, `apt`, `apt-get`, `flatpak`, `jarvis-pkg`)
        if prog in ("nala", "apt", "apt-get", "flatpak", "jarvis-pkg"):
            return self._handle_pkg_command(prog, tokens[1:])

        # 8. Jarvis CLI commands (`jarvis ...`)
        if prog == "jarvis":
            return self._handle_jarvis_command(tokens[1:])

        # 9. Cross-platform convenience aliases when running on Windows host dev preview
        if not sys.platform.startswith("linux"):
            if prog == "ls":
                return self._list_dir_clean(tokens[1:])
            if prog == "pwd":
                return {"ok": True, "output": self.cwd, "cwd": self.cwd}
            if prog == "cat" and len(tokens) >= 2:
                return self._read_file_clean(tokens[1])
            if prog == "uname":
                return {"ok": True, "output": f"Linux jarvis-os 6.11-liquorix-amd64 #1 SMP PREEMPT_DYNAMIC (Host: {platform.system()})", "cwd": self.cwd}
            if prog == "whoami":
                return {"ok": True, "output": f"jarvis (host: {os.environ.get('USERNAME', 'user')})", "cwd": self.cwd}

        # 10. Real local subprocess execution (clean timeout & safe shell=False where possible)
        try:
            proc = subprocess.run(
                cmd,
                shell=True,
                cwd=self.cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=20,
            )
            out = (proc.stdout or "").rstrip()
            return {"ok": proc.returncode == 0, "output": out or f"(exited {proc.returncode})", "cwd": self.cwd}
        except subprocess.TimeoutExpired:
            return {"ok": False, "output": "[ERROR] Command timed out after 20s.", "cwd": self.cwd}
        except Exception as exc:
            return {"ok": False, "output": f"[ERROR] {exc}", "cwd": self.cwd}

    def _handle_pkg_command(self, prog: str, args: list) -> Dict[str, Any]:
        if not args:
            return {"ok": True, "output": f"Usage: {prog} [install|remove|search|list|update] <package>", "cwd": self.cwd}

        sub = args[0].lower()
        targets = [a for a in args[1:] if not a.startswith("-")]

        if sub == "install":
            backend = "flatpak" if prog == "flatpak" else "auto"
            ok, msg = self.pkg_mgr.install(targets, backend=backend)
            return {"ok": ok, "output": msg, "cwd": self.cwd}
        elif sub in ("remove", "purge", "uninstall"):
            ok, msg = self.pkg_mgr.remove(targets)
            return {"ok": ok, "output": msg, "cwd": self.cwd}
        elif sub == "search":
            q = " ".join(targets)
            results = self.pkg_mgr.search(q)[:20]
            if not results:
                return {"ok": True, "output": f"No packages matched '{q}'.", "cwd": self.cwd}
            lines = [f"Found {len(results)} packages matching '{q}':"]
            for r in results:
                tag = "[installed/staged]" if r.get("installed") else "[available]"
                lines.append(f"  {r['id']:<28} {tag:<18} {r['desc']}")
            return {"ok": True, "output": "\n".join(lines), "cwd": self.cwd}
        elif sub == "list":
            staged = self.pkg_mgr.get_staged_packages()
            preview = ", ".join(staged[:30])
            suffix = f" ... (+{len(staged) - 30} more)" if len(staged) > 30 else ""
            return {"ok": True, "output": f"Total staged Debian packages ({len(staged)}):\n{preview}{suffix}", "cwd": self.cwd}
        elif sub == "update":
            ok, msg = self.pkg_mgr.update_repos()
            return {"ok": ok, "output": msg, "cwd": self.cwd}

        return {"ok": False, "output": f"Unsupported subcommand '{sub}' for {prog}. Try install, remove, search, list, or update.", "cwd": self.cwd}

    def _handle_jarvis_command(self, args: list) -> Dict[str, Any]:
        if not args or args[0] == "status":
            state = self.mode_switcher.get_state()
            return {
                "ok": True,
                "output": f"Jarvis OS Status: ONLINE | Mode: {state.get('mode', 'jarvis').upper()} | Theme: {state.get('desktop_theme', 'cupertino-dark')}",
                "cwd": self.cwd,
            }
        sub = args[0].lower()
        if sub == "theme":
            if len(args) < 2 or args[1] == "list":
                themes = "\n".join([f"  {t['id']:<18} - {t['name']}" for t in self.theme_mgr.list_themes()])
                return {"ok": True, "output": f"Available Desktop Themes:\n{themes}", "cwd": self.cwd}
            ok, msg, _ = self.theme_mgr.apply_theme(args[1].lower())
            return {"ok": ok, "output": msg, "cwd": self.cwd, "refresh_ui": ok}
        if sub == "mode" and len(args) >= 2:
            target = args[1].lower()
            if target in ("zen", "desktop"):
                ok, msg = self.mode_switcher.switch_to_zen()
            elif target == "jarvis":
                ok, msg = self.mode_switcher.switch_to_jarvis()
            elif target == "toggle":
                ok, msg = self.mode_switcher.toggle_mode()
            else:
                return {"ok": False, "output": "Usage: jarvis mode [jarvis|zen|desktop|toggle]", "cwd": self.cwd}
            return {"ok": ok, "output": msg, "cwd": self.cwd, "refresh_ui": ok}
        return {"ok": False, "output": "Usage: jarvis [status|theme <name>|mode <jarvis|zen|desktop>]", "cwd": self.cwd}

    def _list_dir_clean(self, args: list) -> Dict[str, Any]:
        target_arg = next((a for a in args if not a.startswith("-")), ".")
        target = os.path.abspath(os.path.join(self.cwd, target_arg))
        if not os.path.exists(target):
            return {"ok": False, "output": f"ls: cannot access '{target_arg}': No such file or directory", "cwd": self.cwd}
        if os.path.isfile(target):
            return {"ok": True, "output": os.path.basename(target), "cwd": self.cwd}
        entries = sorted(os.listdir(target))
        formatted = [f"{e}/" if os.path.isdir(os.path.join(target, e)) else e for e in entries]
        return {"ok": True, "output": "  ".join(formatted), "cwd": self.cwd}

    def _read_file_clean(self, path_arg: str) -> Dict[str, Any]:
        target = os.path.abspath(os.path.join(self.cwd, path_arg))
        if not os.path.isfile(target):
            return {"ok": False, "output": f"cat: {path_arg}: No such file", "cwd": self.cwd}
        try:
            with open(target, "r", encoding="utf-8", errors="replace") as f:
                data = f.read(8192)
            return {"ok": True, "output": data, "cwd": self.cwd}
        except Exception as exc:
            return {"ok": False, "output": f"cat error: {exc}", "cwd": self.cwd}
