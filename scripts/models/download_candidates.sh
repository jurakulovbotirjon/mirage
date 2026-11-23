#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
MODEL_DIR="${MIRAGE_MODEL_DIR:-$ROOT/var/models}"
mkdir -p "$MODEL_DIR"

if ! command -v curl >/dev/null 2>&1; then
  echo "curl is required. Install it with: sudo apt install curl" >&2
  exit 1
fi

download() {
  local name="$1"
  local url="$2"
  local destination="$MODEL_DIR/$name"
  local partial="$destination.part"

  if [[ -s "$destination" ]]; then
    echo "[skip] $name already exists ($(du -h "$destination" | cut -f1))"
    return
  fi

  echo "[download] $name"
  curl --fail --location --retry 3 --retry-delay 2 --continue-at - \
    --output "$partial" "$url"
  mv "$partial" "$destination"
  echo "[saved] $destination ($(du -h "$destination" | cut -f1))"
}

download \
  "SmolLM2-360M-Instruct-Q4_K_M.gguf" \
  "https://huggingface.co/lmstudio-community/SmolLM2-360M-Instruct-GGUF/resolve/main/SmolLM2-360M-Instruct-Q4_K_M.gguf"

download \
  "Qwen2.5-0.5B-Instruct-Q4_K_M.gguf" \
  "https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/qwen2.5-0.5b-instruct-q4_k_m.gguf"

download \
  "Qwen3-0.6B-Q4_0.gguf" \
  "https://huggingface.co/ggml-org/Qwen3-0.6B-GGUF/resolve/main/Qwen3-0.6B-Q4_0.gguf"

echo
echo "All three candidate files are stored locally in: $MODEL_DIR"
echo "They are intentionally excluded from Git. Keep separate backups of these weights."
