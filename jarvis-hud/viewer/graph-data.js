const GRAPH = {
  "nodes": [
    {
      "id": 0,
      "label": "Jarvis Operating System",
      "group": "system",
      "excerpt": "Jarvis OS is an engineered Linux distribution tailored for development, local LLMs, agentic AI, ML, learning, and gaming."
    },
    {
      "id": 1,
      "label": "Local LLM Core & Ollama",
      "group": "ai",
      "excerpt": "Local model runtime running on port 11434 with zero internet leakage and low-latency inference."
    },
    {
      "id": 2,
      "label": "Whisper Ears & Kokoro Voice",
      "group": "voice",
      "excerpt": "Audio pipeline capturing voice at 16kHz mono and streaming synthesized speech in 170-character chunks."
    },
    {
      "id": 3,
      "label": "Gaming & BORE Kernel",
      "group": "gaming",
      "excerpt": "High FPS kernel scheduling, Proton GE, GameMode, and low-latency Vulkan graphics for competitive esports."
    },
    {
      "id": 4,
      "label": "Total Recall Memory Bus",
      "group": "memory",
      "excerpt": "Local markdown-backed knowledge galaxy indexed via SQLite FTS5 with live real-time graph insertion."
    }
  ],
  "links": [
    {"source": 0, "target": 1},
    {"source": 0, "target": 2},
    {"source": 0, "target": 3},
    {"source": 0, "target": 4},
    {"source": 1, "target": 4}
  ]
};
