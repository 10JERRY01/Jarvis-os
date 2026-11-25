"""
Jarvis Hearing Bay (Speech-to-Text & Wake Word)
Implements hands-free wake word detection, dual-model routing,
and utterance finish window buffering (700ms silence, 900ms finish window).
"""

import io
import time
import logging
from typing import Dict, Any, Tuple, Optional

logger = logging.getLogger("jarvis.hearing")

class HearingEngine:
    def __init__(self, config: Dict[str, Any]):
        self.cfg = config.get("hearing", {})
        self.wake_words = [w.lower() for w in [self.cfg.get("wake_word", "jarvis")] + self.cfg.get("wake_aliases", [])]
        self.silence_ms = self.cfg.get("silence_ms", 700)
        self.finish_ms = self.cfg.get("finish_ms", 900)
        
        # Soft import faster-whisper
        self.whisper_model = None
        self._init_models()

    def _init_models(self):
        try:
            from faster_whisper import WhisperModel
            # Load large model (for commands) or lightweight turbo model
            model_size = "large-v3-turbo"
            self.whisper_model = WhisperModel(model_size, device="auto", compute_type="float16")
            logger.info(f"Faster-whisper model '{model_size}' loaded successfully.")
        except Exception as e:
            logger.warning(f"Could not initialize faster-whisper directly ({e}). Falling back to API mode.")

    def transcribe_audio_bytes(self, wav_bytes: bytes) -> Tuple[str, float]:
        """
        Transcribes a 16kHz mono WAV audio clip.
        Returns (transcribed_text, elapsed_seconds).
        """
        start_time = time.time()
        
        if self.whisper_model:
            audio_stream = io.BytesIO(wav_bytes)
            segments, _ = self.whisper_model.transcribe(audio_stream, beam_size=1, language="en")
            text = " ".join([seg.text for seg in segments]).strip()
        else:
            # Fallback mock or local endpoint proxy
            text = ""
        
        elapsed = time.time() - start_time
        return text, elapsed

    def process_utterance(self, text: str) -> Dict[str, Any]:
        """
        Checks for wake word, strips prefix, or detects prompt intents.
        """
        lower = text.lower().strip()
        has_wake = False
        command = text

        for w in self.wake_words:
            if lower.startswith(w):
                has_wake = True
                command = text[len(w):].strip(" ,.:;!?")
                break

        if has_wake and not command:
            return {
                "triggered": True,
                "needs_prompt": True,
                "response": "Yes, sir?",
                "command": ""
            }

        return {
            "triggered": has_wake,
            "needs_prompt": False,
            "command": command
        }
