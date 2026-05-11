# Historical Issues Log (review-57f24bd6)

All findings below are **RESOLVED**. Retained for audit trail; do not treat as current state.
For current backlog see `.sisyphus/editorial-debt-plan.md`.

- 2026-05-11: Round 4 regressions: 33 transformed posts lost one image each, six `content/rag-deep-dive/ko/*.md` dropped `<!-- a-grade-example:begin -->` leaving dangling `<!-- a-grade-example:end -->`, and `content/testing-101/ko/05-test-double.md` kept `## 핵심 용어 정리 (Meszaros 5종)`.
  - **Resolved**: marker pairs restored in `c326c845`; forbidden testing-101 heading removed; image audit completed (see `image-removal-decision.md`).
- 2026-05-11: Re-review after `4725a968` / `adcfb547` found three merge blockers: missing `<!-- a-grade-example:begin -->` wrappers in `rag-deep-dive/ko/*.md`, image removal approval not recorded, and 153 article-structure warnings.
  - **Resolved**: markers restored; image removal explicitly approved in `image-removal-decision.md` (Cat A/B/C decomposition, rag-benchmark-101 mid-article diagram restored); structure warnings re-baselined to 121 strict / 228 --warn-all and documented as Q2 2026 backlog in `editorial-debt-plan.md`.
- 2026-05-11: rag-deep-dive ko/01 `seo_description` overflowed at 90 NFC code-points.
  - **Resolved** in commit `8be1d283`: shortened to 77 NFC; marker leakage in seo_description across 12 posts also cleaned.
- 2026-05-11: Stub series (`ax-practical-guide`, `technical-writing`) carried planned-only status with empty content directories.
  - **Resolved** in commit `00746a68`: removed from `series.yaml` (94 → 92 series), deleted empty directories, regenerated SERIES.md.
