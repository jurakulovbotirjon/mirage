#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
MODEL_DIR="${MIRAGE_MODEL_DIR:-$ROOT/var/models}"
mkdir -p "$MODEL_DIR"

DOWNLOAD_ALL=false
if [[ "${1:-}" == "--all" ]]; then
  DOWNLOAD_ALL=true
elif [[ -n "${1:-}" ]]; then
  echo "Usage: $0 [--all]  (default: download SmolLM2 only)" >&2
  exit 2
fi

if ! command -v modelscope >/dev/null 2>&1; then
  cat >&2 <<'EOF'
ModelScope's CLI is required only as a file downloader (not for inference).
Install it in an isolated environment, not system Python:

  python3 -m venv .venv-modelscope
  .venv-modelscope/bin/pip install modelscope
  source .venv-modelscope/bin/activate

Then run this script again.
EOF
  exit 1
fi

download() {
  local name="$1"
  local repository="$2"
  local filename="$3"
  local destination="$MODEL_DIR/$name"
  local staging="$MODEL_DIR/.staging-$name"

  if [[ -s "$destination" ]]; then
    echo "[skip] $name already exists ($(du -h "$destination" | cut -f1))"
    return
  fi

  rm -rf "$staging"
  mkdir -p "$staging"
  echo "[download] $name from ModelScope/$repository"
  modelscope download --model "$repository" "$filename" --local_dir "$staging"

  if [[ ! -s "$staging/$filename" ]]; then
    echo "Expected model file was not found: $staging/$filename" >&2
    exit 1
  fi

  mv "$staging/$filename" "$destination"
  rm -rf "$staging"
  echo "[saved] $destination ($(du -h "$destination" | cut -f1))"
}

download \
  "SmolLM2-360M-Instruct-Q4_K_M.gguf" \
  "QuantFactory/SmolLM2-360M-Instruct-GGUF" \
  "SmolLM2-360M-Instruct-Q4_K_M.gguf"

if [[ "$DOWNLOAD_ALL" == true ]]; then
download \
  "Qwen2.5-0.5B-Instruct-Q4_K_M.gguf" \
  "Qwen/Qwen2.5-0.5B-Instruct-GGUF" \
  "qwen2.5-0.5b-instruct-q4_k_m.gguf"

download \
  "Qwen3-0.6B-Q4_0.gguf" \
  "Qwen/Qwen3-0.6B-GGUF" \
  "Qwen3-0.6B-Q4_0.gguf"

fi

(
  cd "$MODEL_DIR"
  sha256sum ./*.gguf > SHA256SUMS
)

echo
if [[ "$DOWNLOAD_ALL" == true ]]; then
  echo "All three candidate files are stored locally in: $MODEL_DIR"
else
  echo "SmolLM2 is stored locally in: $MODEL_DIR"
  echo "Use --all later to fetch the other two candidates."
fi
echo "Local integrity hashes saved to: $MODEL_DIR/SHA256SUMS"
echo "They are intentionally excluded from Git. Back them up separately."
