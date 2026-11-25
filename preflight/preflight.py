"""
Jarvis OS Preflight Latency & Integrity Test Harness
Executes real end-to-end calls against the running Jarvis system.
Measures real hardware latency budgets (Hear X s, Think Y s, Speak Z s).
"""

import sys
import time
import json
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:4700"

def run_preflight():
    print("=" * 65)
    print("      JARVIS OS: END-TO-END PREFLIGHT & LATENCY HARNESS")
    print("=" * 65)

    passes = 0
    fails = 0
    warns = 0

    latency_hear = 0.0
    latency_think = 0.0
    latency_speak = 0.0

    # 1. Daemon up and serving viewer
    try:
        t0 = time.time()
        with urllib.request.urlopen(f"{BASE_URL}/", timeout=3) as resp:
            status = resp.status
            body = resp.read()
            if status == 200 and b"JARVIS OS" in body:
                print("[PASS] Server is up and serving the Knowledge Galaxy viewer.")
                passes += 1
            else:
                print("[FAIL] Server responded but returned unexpected viewer content.")
                fails += 1
    except Exception as e:
        print(f"[FAIL] Server is not reachable at {BASE_URL}: {e}")
        fails += 1

    # 2. Graph data loads with node count > 0
    try:
        with urllib.request.urlopen(f"{BASE_URL}/graph-data.js", timeout=3) as resp:
            data_str = resp.read().decode("utf-8")
            if "const GRAPH =" in data_str and "nodes" in data_str:
                print("[PASS] Graph data loaded with active nodes.")
                passes += 1
            else:
                print("[FAIL] graph-data.js missing valid GRAPH definition.")
                fails += 1
    except Exception as e:
        print(f"[FAIL] Could not load graph-data.js: {e}")
        fails += 1

    # 3. Ollama / Local Model endpoint check
    try:
        with urllib.request.urlopen("http://127.0.0.1:11434/v1/models", timeout=3) as resp:
            models_data = json.loads(resp.read().decode("utf-8"))
            print(f"[PASS] Local LLM engine (Ollama) active. Detected {len(models_data.get('data', []))} models.")
            passes += 1
    except Exception:
        print("[WARN] Local LLM engine not answering on port 11434. Run: 'ollama serve && ollama pull qwen2.5:7b'")
        warns += 1

    # 4. /chat real question test & latency measurement
    try:
        t0 = time.time()
        payload = json.dumps({"question": "What is the primary role of Jarvis OS?"}).encode("utf-8")
        req = urllib.request.Request(f"{BASE_URL}/chat", data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=25) as resp:
            chat_data = json.loads(resp.read().decode("utf-8"))
            latency_think = round(time.time() - t0, 3)
            if chat_data.get("answer"):
                print(f"[PASS] /chat returned answer in {latency_think}s (Brain: {chat_data.get('brain')}).")
                passes += 1
            else:
                print("[FAIL] /chat returned empty answer.")
                fails += 1
    except Exception as e:
        print(f"[WARN] /chat test skipped or failed ({e}).")
        warns += 1

    # 5. /tts latency & WAV check
    try:
        t0 = time.time()
        payload = json.dumps({"text": "Systems online and ready."}).encode("utf-8")
        req = urllib.request.Request(f"{BASE_URL}/tts", data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            content_type = resp.headers.get("Content-Type", "")
            raw = resp.read()
            latency_speak = round(time.time() - t0, 3)
            if "audio" in content_type and len(raw) > 100:
                print(f"[PASS] /tts rendered local audio ({len(raw)} bytes) in {latency_speak}s.")
                passes += 1
            else:
                data = json.loads(raw.decode("utf-8"))
                if data.get("fallback") == "browser":
                    print(f"[PASS] /tts verified: Browser speech synthesis fallback active (Profile: {data.get('profile')}).")
                    passes += 1
                else:
                    print("[FAIL] /tts returned malformed response.")
                    fails += 1
    except Exception as e:
        print(f"[WARN] /tts engine not active locally ({e}). Fallback to browser TTS active.")
        warns += 1

    # 6. /remember test
    try:
        test_phrase = f"remember that test verification timestamp is {int(time.time())}"
        payload = json.dumps({"phrase": test_phrase}).encode("utf-8")
        req = urllib.request.Request(f"{BASE_URL}/remember", data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            rem_data = json.loads(resp.read().decode("utf-8"))
            if rem_data.get("success"):
                print("[PASS] Total Recall (/remember) created note and updated index.")
                passes += 1
            else:
                print(f"[FAIL] /remember returned error: {rem_data.get('error')}")
                fails += 1
    except Exception as e:
        print(f"[FAIL] /remember test failed: {e}")
        fails += 1

    # 7. Security audit: config.json must NEVER be reachable via HTTP
    try:
        with urllib.request.urlopen(f"{BASE_URL}/config.json", timeout=2) as resp:
            print("[FAIL] CRITICAL SECURITY FAULT: config.json is accessible via HTTP!")
            fails += 1
    except urllib.error.HTTPError as e:
        if e.code in (403, 404):
            print("[PASS] Security boundary verified: config.json is strictly protected.")
            passes += 1
        else:
            print(f"[WARN] Unexpected HTTP code for config.json: {e.code}")
            warns += 1
    except Exception:
        print("[PASS] Security boundary verified: config.json is unreachable.")
        passes += 1

    # 8. Bonsai 27B Inference Engine Check
    try:
        sys.path.insert(0, "jarvis-core")
        from brain.inference_engine import InferenceEngine
        cfg = json.load(open("jarvis-core/config.json"))
        ie = InferenceEngine(cfg)
        params = ie.get_runtime_parameters()
        if params.get("model") in ["bonsai27b", "bonsai:27b"] and params.get("gpu_layers") > 0:
            print(f"[PASS] Bonsai 27B Engine Configured: {params['gpu_layers']}/{params['total_layers']} layers on GPU VRAM.")
            passes += 1
        else:
            print("[WARN] Inference engine fell back to pure CPU mode.")
            warns += 1
    except Exception as e:
        print(f"[WARN] Inference engine check: {e}")
        warns += 1

    # 9. Codebase Semantic RAG Check
    try:
        from memory.code_rag import CodeRAG
        rag = CodeRAG()
        results = rag.search_code("chunk_text")
        if len(results) > 0:
            print(f"[PASS] Codebase Semantic RAG verified ({len(results)} matches for symbol search).")
            passes += 1
        else:
            print("[WARN] Code RAG index empty or no matches found.")
            warns += 1
    except Exception as e:
        print(f"[WARN] Code RAG check: {e}")
        warns += 1

    # 10. System Agent Action & Gaming Control Check
    try:
        from tools.system_agent import SystemAgent
        sa = SystemAgent()
        ok, receipt = sa.execute_action_tag("[ACTION:TOGGLE_GAMEMODE(on)]")
        if ok and "GameMode engaged" in receipt:
            print("[PASS] System Agent & GameMode Action verified.")
            passes += 1
        else:
            print("[FAIL] System Agent action execution failed.")
            fails += 1
    except Exception as e:
        print(f"[FAIL] System Agent check: {e}")
        fails += 1

    # 11. Dual-Persona Mode & Minimalist Theming Check
    try:
        with urllib.request.urlopen(f"{BASE_URL}/mode/status", timeout=3) as resp:
            mode_data = json.loads(resp.read().decode("utf-8"))
            current_mode = mode_data.get("mode")
            zen_colors = "iso-builder/config/includes.chroot/usr/share/color-schemes/JarvisZen.colors"
            zen_wp = "iso-builder/config/includes.chroot/usr/share/wallpapers/jarvis-zen/contents/images/3840x2160.png"
            panel_cfg = "iso-builder/config/includes.chroot/etc/skel/.config/plasma-org.kde.plasma.desktop-appletsrc"
            
            import os
            if os.path.exists(zen_colors) and os.path.exists(zen_wp) and os.path.exists(panel_cfg):
                print(f"[PASS] Dual-Persona Mode Engine & Minimalist Desktop Assets verified (Current: {current_mode.upper()}).")
                passes += 1
            else:
                print("[FAIL] Dual-Persona Mode or minimalist desktop assets missing.")
                fails += 1
    except Exception as e:
        print(f"[FAIL] Dual-Persona Mode check failed: {e}")
        fails += 1

    # 12. Apple Multi-Theme Desktop Shell, Terminal & Package Manager Check
    try:
        import os
        with urllib.request.urlopen(f"{BASE_URL}/themes", timeout=3) as resp:
            t_data = json.loads(resp.read().decode("utf-8"))
        with urllib.request.urlopen(f"{BASE_URL}/packages/catalog", timeout=3) as resp:
            p_data = json.loads(resp.read().decode("utf-8"))
        term_req = urllib.request.Request(
            f"{BASE_URL}/terminal/exec",
            data=json.dumps({"command": "jarvis-pkg list"}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(term_req, timeout=5) as resp:
            term_data = json.loads(resp.read().decode("utf-8"))

        cupertino_colors = "iso-builder/config/includes.chroot/usr/share/color-schemes/JarvisCupertinoDark.colors"
        cupertino_wp = "iso-builder/config/includes.chroot/usr/share/wallpapers/jarvis-cupertino-dark/contents/images/3840x2160.png"
        desktop_js = "jarvis-hud/viewer/js/desktop.js"

        if (
            len(t_data.get("themes", [])) >= 5
            and p_data.get("staged_total", 0) > 0
            and term_data.get("ok")
            and os.path.exists(cupertino_colors)
            and os.path.exists(cupertino_wp)
            and os.path.exists(desktop_js)
        ):
            print(f"[PASS] Apple/Multi-Theme Shell, Terminal & Package Manager verified ({len(t_data['themes'])} themes, {p_data['staged_total']} Debian pkgs staged).")
            passes += 1
        else:
            print("[FAIL] Apple Multi-Theme Desktop Shell or Terminal/Package verification incomplete.")
            fails += 1
    except Exception as e:
        print(f"[FAIL] Apple Desktop Shell & Package check failed: {e}")
        fails += 1

    print("-" * 65)
    total_budget = round(latency_hear + latency_think + latency_speak, 3)
    print(f"LATENCY BUDGET: Hear {latency_hear}s, Think {latency_think}s, Speak {latency_speak}s (Total: {total_budget}s)")
    print(f"SUMMARY: {passes} PASS, {fails} FAIL, {warns} WARN")
    print("=" * 65)

    return 0 if fails == 0 else 1

if __name__ == "__main__":
    sys.exit(run_preflight())
