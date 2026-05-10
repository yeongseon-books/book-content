# Editorial Debt Resolution Plan

## Current State (as of 2026-05-10)

**Total warnings from `check_article_structure.py --warn-all`: 106**

### Warning Distribution by Series (6 series affected)

1. **ai-data-preparation-101** (core tier)
2. **ai-evaluation-101** (core tier)
3. **ai-safety-guardrails-101** (core tier)
4. **ai-web-dev-101** (core tier)
5. **harness-engineering-101** (supported tier)
6. **multimodal-ai-101** (supported tier)

### Warning Types

| Type | Count | Description |
| --- | --- | --- |
| Missing checklist | 105 | Article lacks production checklist section |
| Missing question block | 49 | Article lacks common misconceptions / FAQ section |

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

*Last updated: 2026-05-10*
*Created for issue #215*
