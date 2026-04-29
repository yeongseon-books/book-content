# Oracle Content Review — azure-app-service-deep-dive

- **Session**: `ses_228fe6500ffeGPcpSePNZi1XyK`
- **Date**: 2026-04-29
- **Verdict**: **needs-rework**
- **Effort**: Medium (1–2d)

## Per-article scores

- `ko/01-platform-architecture.md` — 3/5 — Good map; overstates shared-storage
- `en/01-platform-architecture.md` — 3/5 — Same; not materially deeper than 101
- `ko/02-front-end-and-arr.md` — 3/5 — Slot-routing simplified past accuracy
- `en/02-front-end-and-arr.md` — 3/5 — Weak App Service-specific provenance
- `ko/03-worker-and-sandbox.md` — **4/5** — Strongest chapter
- `en/03-worker-and-sandbox.md` — **4/5** — Same; earns "deep dive"
- `ko/04-deployment-and-kudu.md` — **4/5** — Best-sourced chapter
- `en/04-deployment-and-kudu.md` — **4/5** — Strong; missing source-version framing
- `ko/05-scaling-internals.md` — **2/5** — Mostly Azure Monitor autoscale basics
- `en/05-scaling-internals.md` — **2/5** — "Internals" oversold
- `ko/06-cold-start-and-warmup.md` — 3/5 — Settings-driven, not internals-driven
- `en/06-cold-start-and-warmup.md` — 3/5 — Decent, not deep

## Top 5 specific issues

1. **Missing deep-dive scaffolding across all 12 files** — `ko|en/01-platform-architecture.md:20`. No `## Source Version`, no `## Call Path Summary`.
2. **Misleading slot-routing model + diagram** — `en/02-front-end-and-arr.md:189-196`, `ko/02:187-193`. Diagram shows Front-End → Production/Staging worker sets as if separate; Learn slot-swap doc describes warming + routing-rule switch in same plan.
3. **Episode 1 overgeneralizes shared `/home/site/wwwroot`** — `en|ko/01-platform-architecture.md:87-97`. Linux custom containers change this with `WEBSITES_ENABLE_APP_SERVICE_STORAGE=false` (admitted in ep03).
4. **Episode 5 isn't really "internals"** — `en|ko/05-scaling-internals.md:30-38,106-117,220-228`. Restates autoscale docs; lists Oryx as primary source (category error).
5. **Episode 6 mislabels Oryx as primary source for warm-up** — `en|ko/06-cold-start-and-warmup.md:104-118,230-237`. Real sources: app-settings doc, slot doc, IIS app-init doc.

## Cross-cutting concerns

- Depth uneven (03-04 real deep dive; 01-02-06 careful explainers; 05 thin)
- Source discipline inconsistent
- Korean has mixed-English chunks: `large cache priming`, `expensive startup path`, `organic traffic`
- English chapter-template repetition in intros/wrap sections

## Verdict: needs-rework

## Action list

1. **P0** Fix slot-routing language + diagram in ep02 (ko + en)
2. **P0** Add `Source Version` to all 12 files; add `Call Path Summary` only where real public call path exists
3. **P0** Rework ep05 — real App Service scaling deep dive OR retitle/scope down
4. **P1** Rewrite ep01 shared-storage section with Linux container exception
5. **P1** Clean refs in ep05-06 — remove fake Oryx primary source, add real Learn/IIS sources
6. **P1** Make diagrams explicitly "documented mental model" where inferred
7. **P2** Korean humanization pass for mixed-English leftovers
8. **P2** Reduce English chapter-template repetition
