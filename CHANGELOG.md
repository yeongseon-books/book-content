# Changelog

## [Unreleased]

### Fixed
- `scripts/export_medium.py`: artifact extension corrected from `.md` to `.html`

### Changed
- `PUBLISHING.md`: Medium policy updated to reflect `.html` browser-paste workflow and public asset URLs (default); migration-complete state noted
- `README.md`: simplified landing page; series catalog delegated to `SERIES.md`; Medium column shows `.html` artifact
- `SERIES.md`: all Medium links corrected from `medium/<NN>.md` to `medium/<NN>.html`
- `series.yaml`: `ax-practical-guide` and `technical-writing` paths normalized to `content/` prefix
- `mkdocs.yml`: removed stale scaffold-phase comment

### Added
- `.github/workflows/content-pipeline.yml`: CI workflow (finalize idempotency, ko style, catalog validation)
- `scripts/check_catalog.py`: validates `series.yaml` paths, language dirs, and medium target constraints
- `scripts/check_exports.py`: verifies medium `.html` artifacts exist for each `en/` post
- `Makefile`: `make check`, `make finalize`, `make medium SERIES=<id>`, `make docs`
- `finalize-posts.py --check`: dry-run mode for CI; exits 1 if any file would change

---

## [2026-04-30] — langgraph-101 + llm-finetuning-101 complete

- Added `langgraph-101`: 6-part series (graph basics → multi-agent systems), ko/en/medium
- Added `llm-finetuning-101`: 6-part series (intro → LoRA → training → eval → serving), ko/en/medium
- All 9 remaining series from issue #1 complete: vector-search-101, langchain-101, ai-app-patterns-101, korean-ai-stack-101, document-ingestion-101, llm-apps-ops-101, rag-benchmark-101, langgraph-101, llm-finetuning-101
