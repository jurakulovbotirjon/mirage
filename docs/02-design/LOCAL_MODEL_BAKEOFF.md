# Local model bake-off

This directory contains a reproducible way to fetch and compare three small, openly licensed instruction models. The model weights are **not committed to Git**. They are downloaded into `var/models/`, which is local, backed up separately, and excluded from version control.

## Candidates

| Candidate | Parameters | Quantization | Approx. file size | License | Why test it |
|---|---:|---|---:|---|---|
| SmolLM2 360M Instruct | 0.36B | Q4_K_M | 271 MB | Apache-2.0 | Smallest candidate; likely fastest, but its model card emphasizes English |
| Qwen2.5 0.5B Instruct | 0.49B | Q4_K_M | 491 MB | Apache-2.0 | Small multilingual model; its card lists Korean among supported languages |
| Qwen3 0.6B | 0.6B | Q4_0 | 429 MB | Apache-2.0 | Newer small model; tests whether the extra parameters improve instruction following |

Sizes are approximate and can change with repository revisions. The SmolLM2 GGUF is a community quantization; Qwen2.5 is from the Qwen publisher; Qwen3's GGUF is distributed by ggml-org. Keep each model's license and origin with local backups. The candidate pages and files are mirrored on ModelScope so the download workflow does not rely on Hugging Face.

## Download

The downloader uses ModelScope only as a file source. Mirage does not call an online inference API. After download, inference can run offline. The ModelScope CLI is only a transfer utility; it is not the model runtime.

```bash
chmod +x scripts/models/download_candidates.sh
./scripts/models/download_candidates.sh
```

The script uses the ModelScope CLI to fetch only the selected GGUF files. Total download is roughly 1.2 GB. It does not install an inference service or send prompts to a hosted model. Install the CLI in an isolated virtual environment as shown by the script.

## Runtime and benchmark

Build or install the `llama.cpp` runtime separately and make `llama-server` available on PATH. It runs each GGUF locally, bound only to `127.0.0.1`, with GPU offload disabled for a comparable CPU baseline.

```bash
python scripts/models/benchmark_candidates.py
```

The benchmark records four raw tests per model:
- answer a fact that appears in a supplied passage;
- abstain when the passage does not contain the answer;
- solve a small arithmetic problem;
- answer a short Uzbek question in Latin script.

Results are written to `var/evaluations/candidate-results.json`. This is a screening benchmark, not a scientific leaderboard. We should manually inspect the outputs and measure actual speed on the target laptop before choosing a default. Tiny models may be poor at multi-step reasoning, long context, tool use, and nuanced conversation.

## Important repository boundary

The Git repository stores the manifest, downloader, benchmark, and documentation—not multi-hundred-megabyte binary weights. This avoids bloating Git history and keeps model binaries separate from our code. Back up `var/models/` to storage we control; do not assume a remote model page will remain available forever.
