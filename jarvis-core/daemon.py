"""
Jarvis OS Ambient Daemon (Core Service)
Coordinates local STT (hearing), TTS (voice), LLM (brain), RAG (memory),
Desktop Theme Engine, Package Manager, and Interactive Terminal on 127.0.0.1:4700.
"""

import os
import sys
import json
import time
import platform
import mimetypes
import logging
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Import Jarvis modules
sys.path.insert(0, os.path.dirname(__file__))
from brain.brain import BrainManager
from voice.voice import VoiceEngine
from ears.hear import HearingEngine
from memory.memory import MemoryEngine
from memory.code_rag import CodeRAG
from tools.system_agent import SystemAgent
from tools.screen_vision import ScreenVision
from tools.mode_switcher import ModeSwitcher
from tools.theme_manager import ThemeManager
from tools.pkg_manager import PackageManager
from tools.terminal_engine import TerminalEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("jarvis.daemon")

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VIEWER_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, "jarvis-hud", "viewer"))

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

# Initialize engines
brain_mgr = BrainManager(CONFIG_PATH)
voice_eng = VoiceEngine(CONFIG)
hear_eng = HearingEngine(CONFIG)
mem_eng = MemoryEngine(CONFIG)
code_rag = CodeRAG(os.path.join(os.path.dirname(__file__), "memory", "code_index.db"))
sys_agent = SystemAgent()
vision_eng = ScreenVision()
mode_switcher = ModeSwitcher()
theme_mgr = ThemeManager()
pkg_mgr = PackageManager()
term_eng = TerminalEngine()

# Audit log for the Wi-Fi-Off Drill
OUTBOUND_AUDIT_LOG = []

MIME_FALLBACKS = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".svg": "image/svg+xml",
    ".png": "image/png",
}


class JarvisHTTPHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        sys.stderr.write("%s - - [%s] %s\n" % (self.address_string(), self.log_date_time_string(), format % args))

    def _send_json(self, data: dict, status: int = 200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)

        # Security check: Never serve config.json or traverse parent paths
        if "config.json" in path or ".." in path:
            self.send_error(403, "Access denied.")
            return

        if path == "/status":
            state = mode_switcher.get_state()
            self._send_json({
                "status": "online",
                "active_brain": brain_mgr.active_brain_name,
                "voice_profile": voice_eng.profile,
                "current_mode": state.get("mode", "jarvis"),
                "desktop_theme": state.get("desktop_theme", "cupertino-dark"),
                "notes_indexed": 3,
                "local_only": True,
                "host_os": platform.system(),
            })
            return

        if path == "/mode/status":
            self._send_json(mode_switcher.get_state())
            return

        if path == "/themes":
            state = mode_switcher.get_state()
            self._send_json({
                "active_theme": state.get("desktop_theme", "cupertino-dark"),
                "themes": theme_mgr.list_themes(),
            })
            return

        if path == "/packages/catalog":
            query = (qs.get("q") or [""])[0]
            items = pkg_mgr.search(query) if query else pkg_mgr.get_catalog_with_status()
            self._send_json({
                "host_os": platform.system(),
                "staged_total": len(pkg_mgr.get_staged_packages()),
                "packages": items,
            })
            return

        if path == "/metrics":
            ok, summary = sys_agent.get_system_metrics()
            state = mode_switcher.get_state()
            self._send_json({
                "ok": ok,
                "summary": summary,
                "mode": state.get("mode", "jarvis"),
                "vram_freed": state.get("vram_freed", False),
                "desktop_theme": state.get("desktop_theme", "cupertino-dark"),
                "host_os": f"{platform.system()} {platform.release()}",
            })
            return

        if path == "/fs/list":
            rel = (qs.get("path") or [""])[0].strip("/\\")
            target_dir = os.path.abspath(os.path.join(PROJECT_ROOT, rel))
            if not target_dir.startswith(PROJECT_ROOT) or not os.path.isdir(target_dir):
                self._send_json({"error": "Invalid directory path."}, 400)
                return
            items = []
            for entry in sorted(os.listdir(target_dir)):
                if entry in ("__pycache__", ".git", "Bonsai-27B-Q1_0.gguf", "mmproj-Bonsai-27B-BF16.gguf"):
                    continue
                full = os.path.join(target_dir, entry)
                rel_item = os.path.relpath(full, PROJECT_ROOT).replace("\\", "/")
                is_dir = os.path.isdir(full)
                size = 0 if is_dir else os.path.getsize(full)
                items.append({"name": entry, "path": rel_item, "is_dir": is_dir, "size": size})
            self._send_json({"cwd": rel or "/", "items": items})
            return

        if path == "/fs/read":
            rel = (qs.get("path") or [""])[0].strip("/\\")
            if "config.json" in rel or not rel:
                self._send_json({"error": "Access denied or empty path."}, 403)
                return
            target_file = os.path.abspath(os.path.join(PROJECT_ROOT, rel))
            if not target_file.startswith(PROJECT_ROOT) or not os.path.isfile(target_file):
                self._send_json({"error": "File not found."}, 404)
                return
            try:
                with open(target_file, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read(16384)
                self._send_json({"path": rel, "content": content})
            except Exception as exc:
                self._send_json({"error": str(exc)}, 500)
            return

        if path == "/drill/connections":
            self._send_json({
                "outbound_connections": OUTBOUND_AUDIT_LOG,
                "is_clean": len(OUTBOUND_AUDIT_LOG) == 0,
            })
            return

        # Serve wallpaper assets cleanly under /wallpapers/<slug>.png for Desktop Shell
        if path.startswith("/wallpapers/") and path.endswith(".png"):
            slug = path[len("/wallpapers/"):-4].replace("..", "")
            wp_file = os.path.join(
                PROJECT_ROOT, "iso-builder", "config", "includes.chroot", "usr", "share", "wallpapers", slug, "contents", "images", "3840x2160.png"
            )
            if os.path.isfile(wp_file):
                with open(wp_file, "rb") as f:
                    data = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return

        # Serve viewer static files safely
        rel_file = "index.html" if (path == "/" or path == "") else path.lstrip("/")
        file_path = os.path.abspath(os.path.join(VIEWER_DIR, rel_file))
        if file_path.startswith(VIEWER_DIR) and os.path.isfile(file_path):
            ext = os.path.splitext(file_path)[1].lower()
            mime_type = MIME_FALLBACKS.get(ext) or mimetypes.guess_type(file_path)[0] or "application/octet-stream"
            self.send_response(200)
            self.send_header("Content-Type", mime_type)
            with open(file_path, "rb") as f:
                content = f.read()
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_error(404, "File not found.")

    def do_POST(self):
        content_len = int(self.headers.get("Content-Length", 0))
        body_bytes = self.rfile.read(content_len) if content_len > 0 else b""

        try:
            body_json = json.loads(body_bytes.decode("utf-8")) if body_bytes and "application/json" in (self.headers.get("Content-Type") or "") else {}
        except Exception:
            body_json = {}

        if self.path == "/chat":
            question = body_json.get("question", "").strip()
            if not question:
                self._send_json({"error": "Empty question."}, 400)
                return

            start_t = time.time()
            context_text, node_indexes = mem_eng.search_notes(question)

            try:
                code_chunks = code_rag.search_code(question, top_k=2)
                if code_chunks:
                    code_context = "\n\nRELEVANT LOCAL CODE SNIPPETS:\n" + "\n\n".join([
                        f"File: {c['file_path']} (Symbol: {c['symbol_name']}, Lines {c['start_line']}-{c['end_line']}):\n{c['content'][:500]}"
                        for c in code_chunks
                    ])
                    context_text = (context_text or "") + code_context
            except Exception as e:
                logger.debug(f"Code RAG lookup skipped: {e}")

            system_override = body_json.get("system_override")
            res = brain_mgr.ask(question, context_text, system_override=system_override)
            elapsed = time.time() - start_t

            answer = res.get("answer", "")
            import re
            action_match = re.search(r'\[ACTION:[A-Z_]+\(.*?\)?\]', answer)
            if action_match:
                tag = action_match.group(0)
                ok, receipt = sys_agent.execute_action_tag(tag)
                clean_answer = answer.replace(tag, "").strip()
                res["answer"] = f"{clean_answer} [Receipt: {receipt}]".strip() if clean_answer else f"[Receipt: {receipt}]"
                res["action_executed"] = tag
                res["action_success"] = ok

            res["nodes"] = node_indexes
            res["elapsed_seconds"] = round(elapsed, 2)
            self._send_json(res)
            return

        elif self.path == "/tts":
            text = body_json.get("text", "")
            if not text:
                self._send_json({"error": "Empty text for speech synthesis."}, 400)
                return

            audio_data = voice_eng.synthesize_chunk(text)
            if audio_data:
                self.send_response(200)
                self.send_header("Content-Type", "audio/wav")
                self.send_header("Content-Length", str(len(audio_data)))
                self.send_header("X-Jarvis-Voice", f"local:{voice_eng.profile}")
                self.end_headers()
                self.wfile.write(audio_data)
            else:
                self._send_json({"fallback": "browser", "profile": voice_eng.profile, "text": text}, 200)
            return

        elif self.path == "/remember":
            phrase = body_json.get("phrase", "")
            result = mem_eng.remember(phrase)
            if result.get("success"):
                result["voice_confirm"] = "Recorded to your memory galaxy, sir."
                self._send_json(result)
            else:
                self._send_json(result, 500)
            return

        elif self.path == "/brain/switch":
            target_brain = body_json.get("brain", "")
            success, msg = brain_mgr.switch_brain(target_brain)
            status_code = 200 if success else 400
            self._send_json({"success": success, "message": msg, "active_brain": brain_mgr.active_brain_name}, status_code)
            return

        elif self.path == "/hear":
            text, dur = hear_eng.transcribe_audio_bytes(body_bytes)
            self._send_json({"text": text, "seconds": round(dur, 2)})
            return

        elif self.path == "/vision":
            prompt = body_json.get("prompt", "Analyze what is visible on this screen.")
            analysis = vision_eng.inspect_screen(prompt)
            self._send_json({"analysis": analysis, "model": vision_eng.model_name})
            return

        elif self.path == "/code/search":
            query = body_json.get("query", "")
            top_k = body_json.get("top_k", 5)
            matches = code_rag.search_code(query, top_k=top_k)
            self._send_json({"query": query, "matches": matches, "count": len(matches)})
            return

        elif self.path == "/code/index":
            target_dir = body_json.get("directory", ".")
            count = code_rag.index_directory(target_dir)
            self._send_json({"directory": target_dir, "indexed_chunks": count})
            return

        elif self.path == "/mode/switch":
            target_mode = body_json.get("mode", "").lower()
            theme_id = body_json.get("theme")
            if target_mode in ("zen", "desktop"):
                ok, msg = mode_switcher.switch_to_zen(theme_id=theme_id)
            elif target_mode == "jarvis":
                ok, msg = mode_switcher.switch_to_jarvis()
            elif target_mode == "toggle":
                ok, msg = mode_switcher.toggle_mode()
            else:
                self._send_json({"error": f"Unknown mode '{target_mode}'. Use 'jarvis', 'zen', 'desktop', or 'toggle'."}, 400)
                return
            state = mode_switcher.get_state()
            self._send_json({"success": ok, "message": msg, "mode": state.get("mode"), "desktop_theme": state.get("desktop_theme")})
            return

        elif self.path == "/themes/apply":
            theme_id = body_json.get("theme", "cupertino-dark")
            ok, msg, theme_obj = theme_mgr.apply_theme(theme_id, persist=True)
            self._send_json({"success": ok, "message": msg, "theme": theme_obj}, 200 if ok else 400)
            return

        elif self.path == "/packages/install":
            pkgs = body_json.get("packages") or ([body_json["package"]] if body_json.get("package") else [])
            backend = body_json.get("backend", "auto")
            ok, output = pkg_mgr.install(pkgs, backend=backend)
            self._send_json({"success": ok, "output": output}, 200 if ok else 400)
            return

        elif self.path == "/packages/remove":
            pkgs = body_json.get("packages") or ([body_json["package"]] if body_json.get("package") else [])
            ok, output = pkg_mgr.remove(pkgs)
            self._send_json({"success": ok, "output": output}, 200 if ok else 400)
            return

        elif self.path == "/terminal/exec":
            cmd = body_json.get("command", "")
            res = term_eng.execute(cmd)
            self._send_json(res, 200)
            return

        self.send_error(404, "Endpoint not found.")


def run_server():
    host = CONFIG.get("system", {}).get("host", "127.0.0.1")
    port = CONFIG.get("system", {}).get("port", 4700)
    server = ThreadingHTTPServer((host, port), JarvisHTTPHandler)
    logger.info(f"Jarvis Ambient Core running on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down Jarvis Ambient Core...")
        server.server_close()


if __name__ == "__main__":
    run_server()
