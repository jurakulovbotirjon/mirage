"""Load approved UTF-8 Markdown sources with checksum-backed provenance."""

from __future__ import annotations

import hashlib
from pathlib import Path

from mirage.knowledge.models import Document, SourceReference


def load_markdown_source(
    repository_root: str | Path,
    relative_path: str,
    *,
    expected_sha256: str | None = None,
) -> Document:
    """Load a repository-relative Markdown fixture without modifying its source.

    The first heading becomes the title. Leading bold metadata lines are
    excluded from the knowledge text; the remaining Markdown body is retained.
    """
    root = Path(repository_root).resolve()
    candidate = (root / relative_path).resolve()
    if not candidate.is_relative_to(root):
        raise ValueError("source path must remain inside the repository root")
    if not candidate.is_file():
        raise FileNotFoundError(candidate)

    raw = candidate.read_bytes()
    checksum = hashlib.sha256(raw).hexdigest()
    if expected_sha256 is not None and checksum != expected_sha256:
        raise ValueError("source checksum does not match the expected SHA-256")

    decoded = raw.decode("utf-8")
    lines = decoded.splitlines()
    title = candidate.stem.replace("_", " ").title()
    body_start = 0
    for index, line in enumerate(lines):
        if line.startswith("# "):
            title = line[2:].strip()
            body_start = index + 1
            break

    while body_start < len(lines):
        line = lines[body_start].strip()
        if not line or (line.startswith("**") and line.endswith("**")):
            body_start += 1
            continue
        break

    body = "\n".join(lines[body_start:]).strip()
    source_id = candidate.stem.replace("_", "-")
    source = SourceReference(
        source_id=source_id,
        title=title,
        locator=candidate.relative_to(root).as_posix(),
        sha256=checksum,
    )
    return Document(document_id=f"{source_id}:{checksum[:12]}", text=body, source=source)
