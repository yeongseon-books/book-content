# Editorial Debt Resolution Plan

## Current State (as of 2026-05-11, post-blog-transformation)

**Warning counts depend on scope flag** — `check_article_structure.py` runs in two modes:

| Mode | Command | Posts checked | Warnings | What it covers |
| --- | --- | --- | --- | --- |
| Strict (default) | `python3 scripts/check_article_structure.py` | 386 | **121** | Only `status: publish-ready` posts. This is what `make check` runs. |
| Warn-all | `python3 scripts/check_article_structure.py --warn-all` | 1,673 (all) | **228** | All posts including `content-ready`, `needs-update`, `draft`. Used for backlog visibility. |

**Both numbers are correct and refer to the same underlying issue (missing questions / mental-model blocks). They differ only in scope.** The strict count (121) is the CI gate; the warn-all count (228) is the long-tail backlog including not-yet-publishable posts.

### Warning Types (strict mode, 121 total)

| Type | Count | Description |
| --- | --- | --- |
| Missing questions block | ~80 | Article lacks `## 자주 묻는 질문` / FAQ block |
| Missing mental model blockquote | ~41 | Article lacks opening `> mental model` line |

### Warning Distribution by Series (top contributors, strict mode)

| Series | Warnings | Tier |
| --- | --- | --- |
| llm-from-scratch-101 | 9 | core |
| ai-agent-101 | 9 | core |
| azure-app-service-101 | 7 | supported |
| vector-search-101 | 6 | core |
| rag-deep-dive | 6 | core |
| python-dbapi-101 | 6 | supported |
| llm-finetuning-101 | 6 | core |
| llm-apps-ops-101 | 6 | core |
| llm-api-production-101 | 6 | core |
| korean-ai-stack-101 | 6 | supported |
| document-ingestion-101 | 6 | core |
| ai-app-patterns-101 | 6 | core |
| azure-* deep-dive (3) | 18 total | supported |

> Note: 2026-05-10 baseline (106 warnings on 6 series) is superseded. Blog transformation (commit `57f24bd6` + `4725a968`) reset structure across all 840 ko posts; post-transformation re-baseline is **121 warnings (strict) / 228 warnings (--warn-all), missing questions+mental-model blocks** instead of checklists.

## Resolution Strategy

### Principles

1. **Non-blocking**: Warnings are advisory, not CI blockers
2. **Tier-based priority**: Core tier series before supported tier
3. **Incremental resolution**: Fix series-by-series, not article-by-article
4. **Quality over speed**: Ensure added sections provide real value

### Priority Order

#### Phase 1: Core Tier AI Series (High Priority)
- [ ] **ai-evaluation-101** — Evaluation checklists are mission-critical
- [ ] **ai-data-preparation-101** — Data quality checks essential
- [ ] **ai-safety-guardrails-101** — Safety checklists required

**Target**: Q2 2026

#### Phase 2: Core Tier Practical Series (Medium Priority)
- [ ] **ai-web-dev-101** — Production deployment checklists

**Target**: Q3 2026

#### Phase 3: Supported Tier (Low Priority)
- [ ] **harness-engineering-101** — Engineering best practices
- [ ] **multimodal-ai-101** — Emerging topic, lower urgency

**Target**: Q4 2026

## Execution Workflow

For each series:

1. **Audit current state**
   ```bash
   python3 scripts/check_article_structure.py --warn-all content/<series>/ko
   ```

2. **Design section templates**
   - Checklist: Production-ready validation points
   - Question block: Real misconceptions from practitioners

3. **Add to articles** (delegate to writing agent with series context)

4. **Verify improvement**
   ```bash
   python3 scripts/check_article_structure.py --warn-all content/<series>/ko
   # Expect reduced warning count
   ```

5. **Update this plan** (mark phase checkbox as complete)

## Monitoring

Run quarterly:

```bash
python3 scripts/check_article_structure.py --warn-all > /tmp/editorial-debt-report.txt
wc -l /tmp/editorial-debt-report.txt
```

Track trend: warnings should decrease over time.

## Success Criteria

- Core tier series: 0 warnings
- Supported tier series: < 20 warnings total
- Archive tier: No remediation required

---

*Last updated: 2026-05-11 (post-blog-transformation re-baseline)*
*Created for issue #215*
