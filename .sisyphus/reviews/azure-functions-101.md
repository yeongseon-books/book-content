# Oracle Content Review — azure-functions-101 (FIRST EBOOK CANDIDATE)

- **Session**: `ses_228fe35f3ffeS65grZ3BCI420V`
- **Date**: 2026-04-29
- **Verdict**: **NOT shippable as first ebook without fixes** (needs-rework)
- **Effort**: Medium (1–2d)

## Per-article scores

### ko/
- `01-what-is-azure-functions.md` — 4 — Strong opener; one timeout simplification
- `02-triggers-and-bindings.md` — 4 — Best concept work; sample illustrative not runnable
- `03-host-and-worker.md` — 3 — Python concurrency description misleading
- `04-first-deploy.md` — 4 — Practical; teaches **legacy Consumption** as main path
- `05-choosing-a-plan.md` — 3 — Reads like survey, not decision memo
- `06-scaling-and-cold-start.md` — 3 — Cold start one layer too abstract
- `07-monitoring-and-ops.md` — 3 — Two pieces of guidance not publish-safe

### en/ (same scores, English voice better than expected)

## Top 5 specific issues

1. **Invalid CLI** — `en|ko/07-monitoring-and-ops.md:175`. `az monitor app-insights events show --start-time -7d` is not valid. Use `--offset 7d` or real timestamp.
2. **Brittle admin-endpoint guidance** — `en|ko/07-monitoring-and-ops.md:148`. `/admin/host/scale/status` not current public Learn guidance — internal/diagnostic, not stable operator path.
3. **Python worker model mischaracterized** — `en|ko/03-host-and-worker.md:99`. Treats Python like Node single-threaded event-loop. Reality: sync→threadpool, async→shared event loop, Flex HTTP concurrency default for Python = 1.
4. **"Runnable code" bar not met** — `en|ko/02-triggers-and-bindings.md:83`, `en|ko/06-scaling-and-cold-start.md:110`. `build_invoice(...)`, `create_cosmos_client()` undefined.
5. **Main deploy walkthrough teaches LEGACY path** — `en|ko/04-first-deploy.md:35,181-195`. Says Flex is default for new apps, then makes classic Consumption primary E2E experience. Wrong default for first ebook.

## Cross-cutting concerns

- **Ebook flow structurally OK, editorially not.** Reads like blog: "Coming up next," "This is Part X," repeated forward refs. Should be `blog-only`-fenced or rewritten.
- Chapters 5–7 directionally right but not "decision-grade"
- Korean prose mostly strong; residue: `요약하면`, `정리하면`, `다음 화에서`
- English prose better than expected; main weakness = blog scaffolding
- Scope discipline good (stays mostly 101)

## Re-check confirmed

- Ch1 timeout statement (`en|ko/01-what-is-azure-functions.md:133`) over-compresses: Consumption default 5/max 10; Flex/Premium/Dedicated default 30/effectively unbounded
- No `blog-only`/`ebook-only` markers anywhere — all 14 files contain blog-series scaffolding

## Verdict: not-shippable as first ebook (needs-rework → minor-fixes after P0 land)

## Action list

**P0**
1. Fix ch7 invalid CLI; remove `/admin/host/scale/status` as primary
2. Correct ch3 Python concurrency from current docs (sync/async/Flex semantics)
3. Make ep2/ep6 snippets fully runnable OR label as partial sketches
4. Correct ch1 timeout statement

**P1**
5. Rework ch4 — make Flex Consumption primary; demote classic to note/appendix
6. Tighten ch5 comparison table (sourced + decisive)
7. Add ch6 paragraph on platform-side cold-start mitigation (placeholder/warm capacity)
8. Sweep all 14 files for blog scaffolding; convert/fence with `blog-only`

**P2**
9. Korean style pass for S1-ish closers (`요약하면`, `정리하면`)
10. Add ch7 note on OpenTelemetry as 2026-era direction
