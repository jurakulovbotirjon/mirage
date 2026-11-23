# Mirage Repository Structure

**Status:** Proposed baseline  
**Scope:** Repository and folder architecture for the first implementation  
**Decision:** Keep the application modular, the knowledge pipeline isolated, and source material separate from generated data.

This document is the canonical guide for where files belong. Create directories when the first real file for that responsibility is added; do not fill Git with placeholder files merely to make the tree look complete.

## 1. Canonical repository tree

```text
mirage/
├── README.md
├── pyproject.toml
├── .gitignore
├── .env.example
├── LICENSE
│
├── config/
│   ├── README.md
│   └── defaults.yaml
│
├── docs/
│   ├── 00-governance/
│   │   ├── PROJECT_CHARTER.md
│   │   └── DECISIONS.md
│   ├── 01-architecture/
│   │   ├── SYSTEM_OVERVIEW.md
│   │   ├── REPOSITORY_STRUCTURE.md
│   │   └── DATA_FLOW.md
│   ├── 02-design/
│   │   ├── KNOWLEDGE_PIPELINE.md
│   │   └── RETRIEVAL_DESIGN.md
│   ├── 03-quality/
│   │   ├── TEST_STRATEGY.md
│   │   └── SECURITY_MODEL.md
│   └── knowledge-sources/
│       └── ...
│
├── src/
│   └── mirage/
│       ├── __init__.py
│       ├── main.py
│       ├── application/
│       ├── domain/
│       ├── infrastructure/
│       ├── interfaces/
│       └── knowledge/
│           ├── __init__.py
│           ├── ingestion/
│           ├── chunking/
│           ├── indexing/
│           └── retrieval/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── acceptance/
│   └── fixtures/
│
├── data/
│   ├── test_sources/
│   ├── source_materials/
│   │   ├── originals/
│   │   └── manifests/
│   └── runtime/
│       ├── extracted/
│       ├── chunks/
│       └── indexes/
│
├── scripts/
│   ├── README.md
│   └── ...
│
└── .github/
    └── workflows/
```

## 2. Folder responsibilities

| Location | Owns | Must not contain |
|---|---|---|
| `config/` | Safe, non-secret default configuration | Passwords, API keys, user data |
| `docs/00-governance/` | Project scope and recorded decisions | Implementation code |
| `docs/01-architecture/` | System boundaries, structure, data flows | Temporary notes |
| `docs/02-design/` | Component-level technical designs | Runtime data |
| `docs/03-quality/` | Testing and security strategy | Test execution output |
| `docs/knowledge-sources/` | Source approval, provenance, licenses | Unreviewed source claims |
| `src/mirage/application/` | Use cases and orchestration | Database or file-system implementation details |
| `src/mirage/domain/` | Core entities, value objects, domain rules | Framework-specific code |
| `src/mirage/infrastructure/` | File, database, model, and external adapters | Business rules |
| `src/mirage/interfaces/` | CLI/API/voice entry points and input/output schemas | Core domain logic |
| `src/mirage/knowledge/` | Knowledge ingestion and retrieval capabilities | Conversation UI concerns |
| `tests/unit/` | Fast tests of isolated behavior | Network or real external services |
| `tests/integration/` | Tests across real component boundaries | Uncontrolled production data |
| `tests/acceptance/` | End-to-end behavior against requirements | Ad hoc experiments |
| `tests/fixtures/` | Small deterministic test inputs | Production secrets or licensed books |
| `data/test_sources/` | Synthetic or explicitly reusable test documents | Unreviewed copyrighted material |
| `data/source_materials/originals/` | Locally held, unchanged source files | Git-tracked PDFs/EPUBs |
| `data/source_materials/manifests/` | Provenance, version, license, checksum records | Extracted/chunked runtime output |
| `data/runtime/` | Regenerable extracted text, chunks, and indexes | Canonical source documents |
| `scripts/` | Maintainer and development commands | Core application logic |
| `.github/workflows/` | CI automation | Application source code |

## 3. Non-negotiable organization rules

1. **One responsibility per module.** A file should have one clear reason to change.
2. **Dependency direction stays inward.** Domain code must not import infrastructure, interfaces, or frameworks.
3. **No giant catch-all files.** Avoid names such as `utils.py`, `helpers.py`, or `manager.py` unless the responsibility is genuinely precise and documented.
4. **Separate source from derived data.** Originals are immutable; extracted text, chunks, and indexes are generated artifacts.
5. **Make generated data reproducible.** Every derived artifact must be traceable to a source checksum and pipeline version.
6. **Keep secrets out of Git.** Commit `.env.example`, never a real `.env`.
7. **Tests mirror the source structure.** Test names and folders should make the behavior under test obvious.
8. **No premature empty architecture.** Add a folder when its first implementation or document is ready, not just to decorate the tree.
9. **Document decisions once.** Record important architectural choices in `docs/00-governance/DECISIONS.md`; do not scatter conflicting rules across READMEs.
10. **Keep the root clean.** Only project entry points, configuration, and essential repository metadata belong at the root.

## 4. Knowledge pipeline boundaries

The first knowledge capability should follow this sequence:

```text
approved source
    ↓
ingestion reader
    ↓
normalized document + provenance
    ↓
chunker
    ↓
chunk records with source/page metadata
    ↓
indexer
    ↓
retriever
    ↓
answer context with citations
```

Keep each stage independently testable. The ingestion reader must not decide what answer to give; the retriever must not silently rewrite source material; and the answer-generation layer must be able to say that the indexed sources do not contain an answer.

## 5. Naming conventions

- Python packages and modules: `snake_case`.
- Python classes and exceptions: `PascalCase`.
- Constants: `UPPER_SNAKE_CASE`.
- Documentation: descriptive `UPPER_SNAKE_CASE.md` filenames, consistent with existing project documents.
- Tests: `test_<module_or_behavior>.py`.
- Use names that describe responsibility, not implementation fashion.

## 6. Initial implementation order

Do not create the entire tree in one giant commit. Build it in reviewable slices:

1. Repository baseline: README, packaging, lint/test configuration, and ignore rules.
2. Knowledge contracts: document, source reference, chunk, and retrieval result models.
3. Ingestion: read the existing 300-word test source and preserve provenance.
4. Chunking: deterministic chunks with stable identifiers and source offsets.
5. Storage/indexing: persist and rebuild the test corpus predictably.
6. Retrieval: return relevant chunks with traceable source references.
7. Acceptance tests: answer questions supported by the source and reject questions it cannot answer.

Each slice must include tests and a short documented decision when it changes an architectural boundary.

## 7. Current repository state

This is a target structure, not a claim that all folders or components already exist. The current repository contains the 300-word animal test source and knowledge-source documentation. The runtime pipeline is still to be implemented. The existing test source remains the first controlled fixture; it is not yet an indexed knowledge base.
