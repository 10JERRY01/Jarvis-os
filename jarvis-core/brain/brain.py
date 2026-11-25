"""
Jarvis Brain Dispatcher & Persona Core
Implements stable-prefix prompt caching, lean butler persona (<300 words),
and seamless local/cloud switching (Ollama, llama.cpp, Claude, Gemini).
"""

import json
import logging
import re
import urllib.request
import urllib.error
from typing import Dict, Any, List, Tuple, Optional

logger = logging.getLogger("jarvis.brain")

# STABLE PREFIX: Must be identical on every turn to maximize KV cache reuse in local LLMs.
# Keep under 300 words. Concrete, razor-sharp instructions.
BUTLER_PERSONA = """You are Jarvis, an impeccably polite, dry British butler with razor wit, serving as the central operating system intelligence.
Rules:
1. Address the user as "sir", occasionally and naturally, not in every sentence.
2. Answer in ONE concise, witty sentence followed strictly by the factual answer. Never recite notes verbatim; summarize cleanly.
3. If the provided notes or system context do not cover the question, state so plainly with dignified honesty. Never fabricate citations or sources.
4. When asked what you cost to run, state the honest truth: zero dollars, you reside entirely on this local machine.
5. If an action requires OS execution, emit a single control tag in square brackets: [ACTION:command(arg)].
6. Never say an action is completed unless the system handed you verification proof.
"""

class BrainManager:
    def __init__(self, config_path: str):
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)
        
        self.active_brain_name = self.config.get("system", {}).get("boot_brain", "local")
        self.brains = self.config.get("brains", {})
        self.history: List[Dict[str, str]] = []

    def get_active_brain_config(self) -> Dict[str, Any]:
        return self.brains.get(self.active_brain_name, self.brains.get("local", {}))

    def switch_brain(self, brain_name: str) -> Tuple[bool, str]:
        if brain_name not in self.brains:
            return False, f"Unknown brain '{brain_name}'. Available: {list(self.brains.keys())}"
        
        target = self.brains[brain_name]
        api_key = target.get("api_key", "")
        if "PUT-YOUR-KEY-HERE" in api_key:
            return False, f"Cannot switch to {brain_name}: API key has not been configured in config.json."
        
        self.active_brain_name = brain_name
        return True, f"Switched brain to {brain_name} ({target.get('model', 'default')})."

    def ask(self, question: str, retrieved_context: Optional[str] = None, system_override: Optional[str] = None) -> Dict[str, Any]:
        """
        Sends query to active brain.
        Places stable system prompt FIRST, and dynamic retrieved context + user prompt LAST
        to ensure prompt cache hits on local engines.
        """
        brain_cfg = self.get_active_brain_config()
        brain_type = brain_cfg.get("type", "openai_compatible")

        user_content = question
        if retrieved_context:
            user_content = f"CONTEXT FROM RETRIEVED LOCAL NOTES:\n{retrieved_context}\n\nUSER QUESTION:\n{question}"

        system_prompt = system_override or BUTLER_PERSONA
        messages = [
            {"role": "system", "content": system_prompt},
            *self.history[-4:],  # Keep rolling short server-side history
            {"role": "user", "content": user_content}
        ]

        try:
            if brain_type == "openai_compatible":
                response_text = self._call_openai_compatible(brain_cfg, messages)
            elif brain_type == "anthropic":
                response_text = self._call_anthropic(brain_cfg, messages)
            elif brain_type == "gemini":
                response_text = self._call_gemini(brain_cfg, messages)
            else:
                response_text = "I appear to be configured with an unrecognized brain architecture, sir."
            
            # Update history
            self.history.append({"role": "user", "content": question})
            self.history.append({"role": "assistant", "content": response_text})

            return {
                "success": True,
                "answer": response_text,
                "brain": self.active_brain_name,
                "model": brain_cfg.get("model")
            }

        except Exception as e:
            logger.error(f"Error querying brain {self.active_brain_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "answer": f"My apologies, sir. An issue occurred while consulting the {self.active_brain_name} brain.",
                "brain": self.active_brain_name
            }

    def _resolve_model_name(self, base_url: str, requested_model: str) -> str:
        try:
            req = urllib.request.Request(f"{base_url.rstrip('/')}/models")
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode())
                available = [m.get("id", "") for m in data.get("data", [])]
                if requested_model in available:
                    return requested_model
                # Match prefixes or without colons (e.g. bonsai:27b -> bonsai27b:latest)
                for m in available:
                    req_clean = requested_model.replace(":", "").replace("-", "").lower()
                    m_clean = m.replace(":", "").replace("-", "").lower()
                    if req_clean in m_clean or m_clean in req_clean:
                        return m
                if available:
                    return available[0]
        except Exception:
            pass
        return requested_model

    def _call_openai_compatible(self, cfg: Dict[str, Any], messages: List[Dict[str, str]]) -> str:
        base_urls = [cfg.get("base_url", "http://127.0.0.1:11434/v1")]
        # Also try LM Studio port 1234 if 11434 fails
        if "11434" in base_urls[0]:
            base_urls.append("http://127.0.0.1:1234/v1")
        elif "1234" in base_urls[0]:
            base_urls.append("http://127.0.0.1:11434/v1")

        req_model = cfg.get("model", "bonsai27b")

        last_err = None
        for base_url in base_urls:
            resolved_model = self._resolve_model_name(base_url, req_model)

            # If targeting Ollama (port 11434), try native /api/chat with think: false for ultra-low latency (~2s)
            if "11434" in base_url:
                try:
                    ollama_url = f"{base_url.rstrip('/').replace('/v1', '')}/api/chat"
                    ollama_payload = {
                        "model": resolved_model,
                        "messages": messages,
                        "stream": False,
                        "think": False,
                        "options": {
                            "temperature": cfg.get("temperature", 0.7),
                            "num_predict": cfg.get("max_tokens", 800)
                        }
                    }
                    ollama_req = urllib.request.Request(
                        ollama_url,
                        data=json.dumps(ollama_payload).encode("utf-8"),
                        headers={"Content-Type": "application/json"}
                    )
                    with urllib.request.urlopen(ollama_req, timeout=30) as resp:
                        data = json.loads(resp.read().decode("utf-8"))
                        content = data.get("message", {}).get("content", "").strip()
                        if content:
                            return content
                except Exception as e:
                    logger.debug(f"Ollama /api/chat failed, proceeding to /v1: {e}")

            url = f"{base_url.rstrip('/')}/chat/completions"
            max_toks = cfg.get("max_tokens", 1500)
            payload = {
                "model": resolved_model,
                "messages": messages,
                "max_tokens": max_toks,
                "temperature": cfg.get("temperature", 0.7)
            }
            extra_body = cfg.get("extra_body", {})
            payload.update(extra_body)
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {cfg.get('api_key', 'ollama')}"}
            )

            try:
                with urllib.request.urlopen(req, timeout=60) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    choice = data["choices"][0]
                    content = choice["message"].get("content") or ""
                    
                    # Clean thinking tags (<think>...</think>) if present
                    content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()

                    # Fallback if reasoning budget was spent and content was cut off
                    if not content and choice.get("finish_reason") == "length":
                        logger.warning("Local brain truncated on length, retrying with expanded token budget...")
                        payload["max_tokens"] = max_toks + 600
                        req_retry = urllib.request.Request(
                            url,
                            data=json.dumps(payload).encode("utf-8"),
                            headers={"Content-Type": "application/json", "Authorization": f"Bearer {cfg.get('api_key', 'ollama')}"}
                        )
                        with urllib.request.urlopen(req_retry, timeout=60) as resp_retry:
                            data_retry = json.loads(resp_retry.read().decode("utf-8"))
                            content = data_retry["choices"][0]["message"].get("content") or ""
                            content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()

                    if content:
                        return content.strip()
                    elif choice["message"].get("reasoning"):
                        # Extract final sentence from reasoning if content field is empty
                        reasoning = choice["message"]["reasoning"].strip()
                        lines = [ln.strip() for ln in reasoning.split("\n") if ln.strip()]
                        if lines:
                            return lines[-1].strip()

                    return "I am at your service, sir, though speech momentarily eludes me."
            except Exception as e:
                logger.warning(f"Query attempt on {base_url} failed: {e}")
                last_err = e
                continue

        raise last_err if last_err else RuntimeError("Failed to connect to local brain endpoints.")

    def _call_anthropic(self, cfg: Dict[str, Any], messages: List[Dict[str, str]]) -> str:
        url = f"{cfg['base_url'].rstrip('/')}/messages"
        # Extract system prompt
        system_prompt = next((m["content"] for m in messages if m["role"] == "system"), "")
        chat_messages = [m for m in messages if m["role"] != "system"]

        payload = {
            "model": cfg.get("model", "claude-3-7-sonnet"),
            "system": system_prompt,
            "messages": chat_messages,
            "max_tokens": cfg.get("max_tokens", 1024)
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "x-api-key": cfg["api_key"],
                "anthropic-version": "2023-06-01"
            }
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["content"][0]["text"].strip()

    def _call_gemini(self, cfg: Dict[str, Any], messages: List[Dict[str, str]]) -> str:
        model = cfg.get("model", "gemini-2.5-flash")
        url = f"{cfg['base_url'].rstrip('/')}/models/{model}:generateContent?key={cfg['api_key']}"
        
        contents = []
        for m in messages:
            role = "user" if m["role"] in ["user", "system"] else "model"
            contents.append({"role": role, "parts": [{"text": m["content"]}]})

        payload = {"contents": contents}
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
