# Oracle Content Review — azure-app-service-101

- **Session**: `ses_228fe9cb1ffe0204UJNj8LoQmO`
- **Date**: 2026-04-29
- **Verdict**: **needs-rework**
- **Effort**: Medium (1–2d)

## Rubric summary

| Area | Score | Take |
|---|---:|---|
| Technical accuracy | 3/5 | ko mostly solid; en has multiple stale/wrong platform claims |
| Code examples | 3/5 | Most ko snippets usable; several en snippets are not |
| Korean prose | 4/5 | Natural 입니다 voice, minor residue only |
| English prose | 2/5 | Too compressed, list-heavy, below Medium quality |
| Narrative flow | 4/5 | Strong sequence; series scaffolding works |
| Structural consistency | 3/5 | Duplicate tag surface and duplicate nav are systemic |
| AI-slop indicators | 3/5 | Low cliché, medium templated structure |
| Series-specific risk | 3/5 | Wrong English operational guidance is load-bearing |

## Per-article scores

- `ko/01-what-is-app-service.md` — 5/5 — Strong opener
- `en/01-what-is-app-service.md` — 3/5 — Too thin/generic
- `ko/02-request-lifecycle.md` — 5/5 — Best chapter
- `en/02-request-lifecycle.md` — 3/5 — Nuance stripped
- `ko/03-hosting-models.md` — 4/5 — Good decision guide
- `en/03-hosting-models.md` — 3/5 — Tier matrix has stale guidance
- `ko/04-first-deploy.md` — 4/5 — Strong walkthrough
- `en/04-first-deploy.md` — 4/5 — Mostly runnable
- `ko/05-configuration.md` — 4/5 — Good config discipline
- `en/05-configuration.md` — **2/5** — Outdated Flask + invalid CLI
- `ko/06-logging-monitoring.md` — 4/5 — Strong observability
- `en/06-logging-monitoring.md` — **2/5** — Multiple technical errors
- `ko/07-scaling-101.md` — 4/5 — Solid close
- `en/07-scaling-101.md` — 3/5 — Central stateless example broken

## Top 5 specific issues

1. **Outdated Flask guidance** — `en/05-configuration.md:57-60,74-76,141-145`. Treats `FLASK_ENV` as live; removed in Flask 2.3/3.x.
2. **Invalid `--slot-settings` CLI** — `en/05-configuration.md:213-218`. `az webapp config appsettings set --slot-settings APP_ENV` is invalid; CLI expects `KEY=VALUE`.
3. **Logging chapter wrong defaults + brittle code** — `en/06-logging-monitoring.md:55-66,71-75,208-214,431`. False stdout/stderr default, invalid `az webapp log config show`, `CorrelationFilter` accesses `g` without request-context guard.
4. **Broken stateless/Redis example** — `en/07-scaling-101.md:128-133`. Missing `os`/`json` imports; `user_id`/`session_data` undefined.
5. **Outdated VNet Integration tier matrix** — `en/03-hosting-models.md:84-93`. Says Standard required; current guidance allows Basic+ for dedicated tiers.

## Cross-cutting concerns

- English set is not a faithful counterpart of Korean set (English regresses to thinner/older guidance)
- Korean prose is mostly good — minor residue: `요약하면:` (`ko/04-first-deploy.md:243`), `민감 정보번호` (`ko/05-configuration.md:86,162,251`)
- Narrative sequencing strong
- All 14 source posts carry an extra bolded tag line before required final `Tags:` line (e.g. `ko/01-what-is-app-service.md:278-280`, `en/01-what-is-app-service.md:327-329`)
- English posts add `## Series Index` duplicating canonical TOC

## Verdict: needs-rework

## Action list

1. **P0** Fix `en/05` completely: `FLASK_ENV` removal, Flask 3.x env vars, slot-setting CLI syntax
2. **P0** Fix `en/06` completely: logging defaults, valid CLI commands, request-context filter
3. **P0** Fix `en/07` Redis/stateless example to actually run
4. **P0** Re-verify every Azure tier/CLI claim in `en/03`–`en/07` against current Microsoft Learn
5. **P1** Rewrite English prose to match Korean depth
6. **P1** Bilingual drift pass (en→ko comparison)
7. **P1** Remove extra `**Tags:** ...` bolded line from all 14 posts
8. **P2** Decide on `## Series Index` retention
9. **P2** Clean Korean residue (`요약하면:`, `민감 정보번호`)
10. **P2** Regenerate `medium/` only after corrections
