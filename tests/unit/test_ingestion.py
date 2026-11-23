"""Tests for checksum-verified Markdown source ingestion."""

import hashlib

import pytest

from mirage.knowledge.ingestion import load_markdown_source


def test_loader_extracts_body_and_preserves_provenance(tmp_path) -> None:
    source = tmp_path / "sample.md"
    content = "# Sample Title\n\n**Purpose:** fixture  \n**Type:** test\n\nA factual sentence."
    source.write_text(content, encoding="utf-8")

    document = load_markdown_source(tmp_path, "sample.md")

    assert document.text == "A factual sentence."
    assert document.source.title == "Sample Title"
    assert document.source.locator == "sample.md"
    assert document.source.sha256 == hashlib.sha256(source.read_bytes()).hexdigest()


def test_loader_rejects_checksum_mismatch(tmp_path) -> None:
    (tmp_path / "sample.md").write_text("# Title\n\nText.", encoding="utf-8")
    with pytest.raises(ValueError, match="checksum"):
        load_markdown_source(tmp_path, "sample.md", expected_sha256="0" * 64)


def test_loader_rejects_path_traversal(tmp_path) -> None:
    outside = tmp_path.parent / "outside.md"
    outside.write_text("# Outside\n\nText.", encoding="utf-8")
    with pytest.raises(ValueError, match="inside"):
        load_markdown_source(tmp_path, "../outside.md")


def test_loader_reports_missing_source(tmp_path) -> None:
    with pytest.raises(FileNotFoundError):
        load_markdown_source(tmp_path, "missing.md")
