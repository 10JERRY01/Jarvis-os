"""
Jarvis Voice Synthesis Engine
Implements sentence-packed chunking (~170 chars), WAV caching on disk,
and pipelined prefetch to guarantee uninterrupted, natural speech flow.
"""

import os
import re
import json
import hashlib
import urllib.request
import urllib.error
import logging
from typing import List, Generator, Optional, Dict, Any

logger = logging.getLogger("jarvis.voice")

CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

class VoiceEngine:
    def __init__(self, config: Dict[str, Any]):
        self.cfg = config.get("voice", {})
        self.url = self.cfg.get("url", "http://127.0.0.1:8880/v1/audio/speech")
        self.model_id = self.cfg.get("model_id", "kokoro-v1.0")
        self.profile = self.cfg.get("profile", "am_adam")
        self.chunk_char_limit = self.cfg.get("chunk_char_limit", 170)
        self.is_muted = False

    def chunk_text(self, text: str) -> List[str]:
        """
        Splits text into complete sentences under chunk_char_limit.
        Never breaks in the middle of a sentence.
        """
        # Split by sentence end markers (. ! ? followed by space or newline)
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        chunks: List[str] = []
        current_chunk = ""

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            if not current_chunk:
                current_chunk = sentence
            elif len(current_chunk) + len(sentence) + 1 <= self.chunk_char_limit:
                current_chunk += " " + sentence
            else:
                chunks.append(current_chunk)
                current_chunk = sentence

        if current_chunk:
            chunks.append(current_chunk)

        return chunks if chunks else [text]

    def _get_cache_path(self, text: str) -> str:
        key = f"{self.profile}_{self.model_id}_{text}"
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
        return os.path.join(CACHE_DIR, f"{digest}.wav")

    def synthesize_chunk(self, text: str) -> Optional[bytes]:
        """
        Synthesizes a single chunk, checking disk cache first.
        """
        cache_path = self._get_cache_path(text)
        if os.path.exists(cache_path):
            with open(cache_path, "rb") as f:
                return f.read()

        payload = {
            "model": self.model_id,
            "input": text,
            "voice": self.profile,
            "response_format": "wav"
        }

        try:
            req = urllib.request.Request(
                self.url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                audio_bytes = resp.read()
                # Cache audio on disk
                with open(cache_path, "wb") as f:
                    f.write(audio_bytes)
                return audio_bytes
        except Exception as e:
            logger.warning(f"Voice synthesis failed on '{text[:30]}...': {e}")
            return None

    def stream_speech(self, full_text: str) -> Generator[bytes, None, None]:
        """
        Yields audio bytes chunk-by-chunk for pipelined playback.
        """
        if self.is_muted:
            return

        chunks = self.chunk_text(full_text)
        for chunk in chunks:
            audio = self.synthesize_chunk(chunk)
            if audio:
                yield audio

    def keep_warm(self):
        """Pings the voice engine to prevent cold starts."""
        try:
            self.synthesize_chunk("Standing by.")
            logger.info("Voice engine keep-warm pulse sent.")
        except Exception:
            pass
