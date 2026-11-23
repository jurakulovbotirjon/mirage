# Mirage

Mirage is a personal AI assistant project being developed in small, testable stages. The initial engineering milestone is a trustworthy, source-grounded knowledge pipeline: ingest approved documents, preserve provenance, retrieve relevant passages, and clearly report when the available sources do not contain an answer.

## Project principles

- **Source-grounded:** answers based on the knowledge base must be traceable to retrieved source material.
- **Honest uncertainty:** Mirage must distinguish supported answers from missing or conflicting evidence.
- **Modular by responsibility:** domain rules, application workflows, infrastructure adapters, and interfaces stay separate.
- **Reproducible:** derived knowledge data can be rebuilt from approved source files and recorded pipeline versions.
- **Privacy-conscious:** secrets and personal runtime data do not belong in Git.
- **Incremental engineering:** each milestone has tests and reviewable changes.

## Current status

The repository currently contains:
- A 300-word animal-classification test source in `data/test_sources/`.
- Documentation for candidate botanical sources and their licensing/provenance review.
- A canonical repository-structure proposal in `docs/01-architecture/REPOSITORY_STRUCTURE.md`.

The application runtime and knowledge ingestion/retrieval pipeline have **not yet been implemented**. The animal text is a controlled test input, not an indexed knowledge base.

## Requirements

- Python 3.11 or newer
- Git

Python 3.13 is supported by the declared project range. No runtime third-party dependencies are required at this initial baseline.

## Development setup

Clone the repository and enter it:

```bash
git clone https://github.com/jurakulovbotirjon/mirage.git
cd mirage
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the project with development tools:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Run quality checks:

```bash
pytest
ruff check .
ruff format --check .
```

## Planned first milestone: source-grounded knowledge

The first implementation will progress through independently testable stages:

1. Define source, document, chunk, and retrieval-result contracts.
2. Read the existing test source without modifying the original.
3. Normalize text while retaining source identity and location metadata.
4. Split text into deterministic, traceable chunks.
5. Persist and rebuild a small local index.
6. Retrieve relevant chunks for a query.
7. Test supported questions, unsupported questions, and source traceability.

The first milestone does not require a hosted vector database, model fine-tuning, or runtime internet access. We will add infrastructure only when a demonstrated requirement calls for it.

## Repository map

See [Repository Structure](docs/01-architecture/REPOSITORY_STRUCTURE.md) for folder responsibilities, dependency boundaries, naming conventions, and the intended project layout.

## Knowledge-source policy

Read [Botanical Knowledge Sources](docs/knowledge-sources/botany/README.md) before acquiring or processing external textbooks. Source licenses and page-level exceptions must be reviewed; source files are not automatically approved for AI ingestion merely because they are publicly accessible.

## Security

Never commit API keys, passwords, access tokens, private user data, or local environment files. Keep real secrets in local environment variables or an appropriately secured secret manager. Only safe examples may be committed.
