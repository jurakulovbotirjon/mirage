#!/usr/bin/env python3
"""Run a small, repeatable local benchmark against three downloaded GGUF models.

Requires a llama.cpp llama-server binary. No cloud inference or API key is used.
The script records raw answers and latency; it does not pretend that a tiny
hand-written benchmark is a scientific model ranking.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import Request, urlopen
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = Path(os.environ.get("MIRAGE_MODEL_DIR", ROOT / "var" / "models"))
OUTPUT = ROOT / "var" / "evaluations" / "candidate-results.json"

CANDIDATES = [
    ("SmolLM2-360M-Instruct", "SmolLM2-360M-Instruct-Q4_K_M.gguf"),
    ("Qwen2.5-0.5B-Instruct", "Qwen2.5-0.5B-Instruct-Q4_K_M.gguf"),
    ("Qwen3-0.6B", "Qwen3-0.6B-Q4_0.gguf"),
]

CASES = [
    {
        "id": "grounded_fact",
        "system": "Answer using only the supplied passage. If the passage does not contain the answer, say exactly: NOT IN PASSAGE. Be concise.",
        "user": "Passage: Insects have six legs, three main body regions, and usually wings.\nQuestion: How many legs do insects have?",
        "review_hint": "Should answer six legs.",
    },
    {
        "id": "abstention",
        "system": "Answer using only the supplied passage. If the passage does not contain the answer, say exactly: NOT IN PASSAGE. Do not guess.",
        "user": "Passage: Insects have six legs, three main body regions, and usually wings.\nQuestion: What is the average lifespan of an octopus?",
        "review_hint": "Must abstain; the passage gives no octopus lifespan.",
    },
    {
        "id": "basic_reasoning",
        "system": "Solve the arithmetic accurately. Give only the result.",
        "user": "What is 17 multiplied by 19?",
        "review_hint": "Expected result: 323.",
    },
    {
        "id": "instruction_following",
        "system": "Follow the user's exact output constraints. Use only the supplied facts.",
        "user": "Facts: Mirage is a local assistant. It stores documents on this computer.\nTask: Give exactly two bullet points. Each bullet must contain one fact. Do not add a third bullet.",
        "review_hint": "Must produce exactly two bullets, one fact each, without unsupported additions.",
    },
]


def wait_until_ready(base_url: str, process: subprocess.Popen[str], timeout: int) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"llama-server exited early with code {process.returncode}")
        try:
            with urlopen(f"{base_url}/health", timeout=2) as response:
                if response.status == 200:
                    return
        except (OSError, URLError):
            time.sleep(1)
    raise TimeoutError(f"llama-server did not become ready within {timeout}s")


def ask(base_url: str, case: dict[str, str]) -> tuple[str, float]:
    payload = {
        "model": "mirage-local-candidate",
        "messages": [
            {"role": "system", "content": case["system"]},
            {"role": "user", "content": case["user"]},
        ],
        "temperature": 0,
        "max_tokens": 160,
    }
    request = Request(
        f"{base_url}/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    started = time.perf_counter()
    with urlopen(request, timeout=180) as response:
        result = json.loads(response.read().decode("utf-8"))
    elapsed = time.perf_counter() - started
    answer = result["choices"][0]["message"]["content"].strip()
    return answer, elapsed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--server-bin", default="llama-server")
    parser.add_argument("--port", type=int, default=8097)
    parser.add_argument("--startup-timeout", type=int, default=180)
    args = parser.parse_args()

    server = args.server_bin
    if Path(server).name == server and not shutil_which(server):
        print(f"Cannot find {server!r}. Install/build llama.cpp first.", file=sys.stderr)
        return 2

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    report: dict[str, object] = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "runtime": "llama.cpp llama-server, CPU-only (-ngl 0)",
        "cases": CASES,
        "models": [],
    }

    for index, (name, filename) in enumerate(CANDIDATES):
        model_path = MODEL_DIR / filename
        if not model_path.is_file():
            print(f"Missing model: {model_path}\nRun scripts/models/download_candidates.sh first.", file=sys.stderr)
            return 2

        port = args.port + index
        base_url = f"http://127.0.0.1:{port}"
        command = [
            server, "--model", str(model_path),
            "--host", "127.0.0.1", "--port", str(port),
            "--ctx-size", "2048", "--n-gpu-layers", "0",
        ]
        print(f"\n=== {name} ===", flush=True)
        process = subprocess.Popen(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        model_result: dict[str, object] = {
            "name": name,
            "file": filename,
            "cases": [],
        }
        try:
            wait_until_ready(base_url, process, args.startup_timeout)
            for case in CASES:
                try:
                    answer, seconds = ask(base_url, case)
                    item = {
                        "id": case["id"],
                        "answer": answer,
                        "latency_seconds": round(seconds, 3),
                        "review_hint": case["review_hint"],
                    }
                    print(f"[{case['id']}] {seconds:.2f}s | {answer}", flush=True)
                except Exception as error:  # preserve failures in the report
                    item = {
                        "id": case["id"],
                        "error": f"{type(error).__name__}: {error}",
                        "review_hint": case["review_hint"],
                    }
                    print(f"[{case['id']}] ERROR: {error}", flush=True)
                model_result["cases"].append(item)
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)

        report["models"].append(model_result)
        OUTPUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"\nSaved raw results to {OUTPUT}")
    print("Review answer correctness, abstention, Uzbek quality, and latency before choosing a default.")
    return 0


def shutil_which(command: str) -> str | None:
    """Small stdlib-only equivalent of shutil.which."""
    import shutil
    return shutil.which(command)


if __name__ == "__main__":
    raise SystemExit(main())
