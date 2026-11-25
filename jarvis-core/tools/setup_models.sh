#!/usr/bin/env bash
# ==============================================================================
# Jarvis OS: Local Bonsai 27B & Vision Model Setup Script
# Generates clean portable Ollama Modelfiles inside Linux without hardcoded
# Windows host paths and registers `bonsai27b` + `bonsai27b-vision`.
# ==============================================================================

set -euo pipefail

MODEL_DIR="${1:-/opt/jarvis-models/Bonsai-27B-GGUF}"
MAIN_GGUF="${MODEL_DIR}/Bonsai-27B-Q1_0.gguf"
VISION_PROJ="${MODEL_DIR}/mmproj-Bonsai-27B-BF16.gguf"

echo "=========================================================="
echo "      JARVIS OS: BONSAI 27B LOCAL MODEL HYDRATION         "
echo "=========================================================="

if ! command -v ollama >/dev/null 2>&1; then
    echo "[ERROR] Ollama not installed. Install via: curl -fsSL https://ollama.com/install.sh | sh"
    exit 1
fi

if [[ ! -f "${MAIN_GGUF}" ]]; then
    echo "[ERROR] Model weight not found at: ${MAIN_GGUF}"
    echo "Usage: bash setup_models.sh /path/to/Bonsai-27B-GGUF"
    exit 1
fi

TMP_MODELFILE="$(mktemp)"
cat << EOF > "${TMP_MODELFILE}"
FROM "${MAIN_GGUF}"
TEMPLATE """{{- if .System }}<|im_start|>system
{{ .System }}<|im_end|>
{{- end }}
{{- range .Messages }}
{{- if eq .Role "system" }}<|im_start|>system
{{ .Content }}<|im_end|>
{{- else if eq .Role "user" }}<|im_start|>user
{{ .Content }}<|im_end|>
{{- else if eq .Role "assistant" }}<|im_start|>assistant
{{ .Content }}<|im_end|>
{{- end }}
{{- end }}
{{- if .Prompt }}<|im_start|>user
{{ .Prompt }}<|im_end|>
{{- end }}<|im_start|>assistant
"""
PARAMETER stop "<|im_start|>"
PARAMETER stop "<|im_end|>"
PARAMETER stop "<|endoftext|>"
PARAMETER temperature 0.7
PARAMETER top_p 0.95
EOF

echo "[INFO] Registering bonsai27b in local Ollama..."
ollama create bonsai27b -f "${TMP_MODELFILE}"
rm -f "${TMP_MODELFILE}"

if [[ -f "${VISION_PROJ}" ]]; then
    TMP_VISION="$(mktemp)"
    cat << EOF > "${TMP_VISION}"
FROM "${MAIN_GGUF}"
FROM "${VISION_PROJ}"
TEMPLATE """{{- if .System }}<|im_start|>system
{{ .System }}<|im_end|>
{{- end }}
{{- range .Messages }}
{{- if eq .Role "system" }}<|im_start|>system
{{ .Content }}<|im_end|>
{{- else if eq .Role "user" }}<|im_start|>user
{{ .Content }}<|im_end|>
{{- else if eq .Role "assistant" }}<|im_start|>assistant
{{ .Content }}<|im_end|>
{{- end }}
{{- end }}
{{- if .Prompt }}<|im_start|>user
{{ .Prompt }}<|im_end|>
{{- end }}<|im_start|>assistant
"""
PARAMETER stop "<|im_start|>"
PARAMETER stop "<|im_end|>"
PARAMETER stop "<|endoftext|>"
PARAMETER temperature 0.7
PARAMETER top_p 0.95
EOF
    echo "[INFO] Registering bonsai27b-vision in local Ollama..."
    ollama create bonsai27b-vision -f "${TMP_VISION}"
    rm -f "${TMP_VISION}"
fi

echo "[SUCCESS] Local Bonsai 27B brain registered and ready!"
