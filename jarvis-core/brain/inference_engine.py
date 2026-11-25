"""
Jarvis OS Local Inference Engine & Hardware-Aware Layer Offloader
Optimizes Bonsai 27B across GPU VRAM (12GB) and System RAM (32GB)
with speculative decoding, GBNF grammars, and dynamic layer budgeting.
"""

import os
import shutil
import subprocess
import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger("jarvis.inference")

class InferenceEngine:
    def __init__(self, config: Dict[str, Any]):
        self.cfg = config.get("inference", {})
        self.target_model = self.cfg.get("target_model", "bonsai:27b")
        self.draft_model = self.cfg.get("draft_model", "bonsai:draft-1.5b")
        self.quantization = self.cfg.get("quantization", "Q4_K_M")
        self.context_length = self.cfg.get("context_length", 8192)
        self.vram_headroom_mb = self.cfg.get("vram_headroom_mb", 2048)
        self.speculative = self.cfg.get("speculative_decoding", True)
        self.model_path = self.cfg.get("model_path", "./Bonsai-27B-GGUF/Bonsai-27B-Q1_0.gguf")
        self.total_layers = 64  # Qwen 3.5 27B architecture block count
        self.vram_mb, self.ram_mb = self._probe_hardware()

    def _probe_hardware(self) -> Tuple[int, int]:
        """Probes GPU VRAM and Host RAM in Megabytes."""
        vram = 0
        ram = 16384  # Default fallback 16GB

        # Probe GPU VRAM via nvidia-smi
        if shutil.which("nvidia-smi"):
            try:
                out = subprocess.check_output(
                    ["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"],
                    stderr=subprocess.DEVNULL
                ).decode().strip()
                vram = int(out.split("\n")[0])
            except Exception:
                pass

        # Probe Host RAM
        try:
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    if line.startswith("MemTotal:"):
                        ram = int(line.split()[1]) // 1024
                        break
        except Exception:
            # Fallback for Windows host
            try:
                import ctypes
                class MEMORYSTATUSEX(ctypes.Structure):
                    _fields_ = [
                        ("dwLength", ctypes.c_ulong),
                        ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong),
                        ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong),
                        ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong),
                        ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
                    ]
                stat = MEMORYSTATUSEX()
                stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
                ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
                ram = int(stat.ullTotalPhys // (1024 * 1024))
            except Exception:
                pass

        return vram, ram

    def calculate_gpu_layers(self) -> int:
        """
        Calculates optimal GPU offload layers for Bonsai 27B.
        Inspects actual GGUF file size if present (e.g. 3.6GB Q1_0).
        """
        if self.vram_mb <= 0:
            return 0  # Pure CPU mode

        usable_vram = max(1024, self.vram_mb - self.vram_headroom_mb)
        
        # Check actual GGUF file size on disk
        actual_path = os.path.abspath(self.model_path)
        if os.path.exists(actual_path):
            total_model_mb = os.path.getsize(actual_path) // (1024 * 1024)
            mb_per_layer = max(1, total_model_mb // self.total_layers)
        else:
            mb_per_layer = 60  # Default ~60MB per layer for Q1_0 / quantized 27B

        kv_cache_mb = (self.context_length / 1024) * 128  # ~1024 MB for 8k ctx
        effective_vram_for_weights = max(0, usable_vram - kv_cache_mb)
        gpu_layers = int(effective_vram_for_weights // mb_per_layer)
        
        # Clamp between 0 and total layers
        return max(0, min(self.total_layers, gpu_layers))

    def get_runtime_parameters(self) -> Dict[str, Any]:
        """Returns optimal runtime arguments for llama.cpp / vLLM / Ollama."""
        gpu_layers = self.calculate_gpu_layers()
        cpu_layers = self.total_layers - gpu_layers
        actual_path = os.path.abspath(self.model_path)
        mb_per_layer = (os.path.getsize(actual_path) // (1024 * 1024 * self.total_layers)) if os.path.exists(actual_path) else 60

        return {
            "model": self.target_model,
            "model_path": self.model_path,
            "draft_model": self.draft_model if self.speculative else None,
            "quantization": self.quantization,
            "context_length": self.context_length,
            "total_layers": self.total_layers,
            "gpu_layers": gpu_layers,
            "cpu_layers": cpu_layers,
            "vram_allocated_mb": gpu_layers * mb_per_layer,
            "system_ram_allocated_mb": cpu_layers * mb_per_layer,
            "hardware": {
                "detected_vram_mb": self.vram_mb,
                "detected_ram_mb": self.ram_mb
            }
        }

    @staticmethod
    def get_action_tag_gbnf() -> str:
        """
        GBNF grammar ensuring that whenever an action is triggered,
        the model strictly emits [ACTION:NAME(ARG)] with zero malformed output.
        """
        return r'''
        root ::= (prose | action)+
        prose ::= [^\[\n]+
        action ::= "[ACTION:" action_name "(" action_arg ")]"
        action_name ::= "TOGGLE_GAMEMODE" | "LAUNCH_APP" | "SYSTEM_METRICS" | "SET_VOLUME"
        action_arg ::= [^)]*
        '''
