# Consolidated Oracle Content Review — All 10 Series

- **Date**: 2026-04-29
- **Reviewer**: Oracle (8 parallel sessions)
- **Total articles**: 129 across 10 series
- **HEAD**: `36eac34` (infrastructure complete)

## Verdict matrix

| Series | Verdict | Effort | Ship-ready order |
|---|---|---|---|
| azure-aks-101 | minor-fixes | Short | 🥇 closest to ship |
| azure-app-service-deep-dive | needs-rework | Medium | |
| azure-app-service-101 | needs-rework | Medium | |
| azure-aks-deep-dive | needs-rework | Medium | |
| ai-web-dev-101 | NEEDS-FIXES | Medium | |
| azure-functions-101 (eBook!) | needs-rework | Medium | 🚨 first ebook candidate |
| llm-from-scratch-101 | **NOT-SHIPPABLE** | Medium | 🔴 math bugs |
| azure-functions-deep-dive | **NOT-SHIPPABLE** | Large | 🔴 hallucinated APIs |
| azure-aca-deep-dive | conditional fail | Medium | 🔴 high hallucination risk |
| azure-aca-101 | **FAIL** | Large (3d+) | 🔴 corrupted (duplicated filler) |

## Cross-series P0 (publication blockers)

### Code that crashes / cannot run
1. **llm-from-scratch-101** — Attention block code crashes (tensor + tuple); ep5 inherits bug
   - `ko|en/03-attention.md:136-149` returns tuple, `ko|en/04-transformer-block.md:86-88` adds it to tensor
2. **llm-from-scratch-101** — ep8 SFT trains wrong target (unshifted labels = token copying, not next-token)
3. **llm-from-scratch-101** — Korean ep8 fine-tune dataset uses Hangul; tokenizer is English-char-only → KeyError
4. **llm-from-scratch-101** — Chatbot ep9 has no OOV handling; Korean examples impossible with English vocab
5. **ai-web-dev-101** — `03-ai-chatbot.md` Vercel AI SDK example broken on fresh install (wrong package, wrong API)
6. **ai-web-dev-101** — `06-deploy.md` FastAPI on Azure App Service incomplete (missing startup command)
7. **azure-app-service-101** — `en/05-configuration.md` invalid CLI `az webapp config appsettings set --slot-settings APP_ENV` (expects KEY=VALUE)
8. **azure-app-service-101** — `en/06-logging-monitoring.md` invalid `az webapp log config show`
9. **azure-app-service-101** — `en/07-scaling-101.md:128-133` Redis stateless example missing imports + undefined vars
10. **azure-functions-101** — `en|ko/07-monitoring-and-ops.md:175` invalid `az monitor app-insights events show --start-time -7d`
11. **azure-aks-101** — `en|ko/06-scaling-hpa-ca-keda.md:194-210` KEDA example missing auth wiring
12. **azure-aca-101** — Duplicated checklist filler corrupts ALL 14 ko/en files (starts at line 116/117 of each)
13. **azure-aca-101** — `en/05-scaling-with-keda.md:39-50` wrong 2026 taxonomy (omits TCP, elevates CPU/memory)

### Hallucinated/invented technical claims (deep-dive)
14. **azure-functions-deep-dive** — 6+ invented APIs cited as if in `5e59423`:
    - `WorkerConfigFactory` (real: `WorkerConfigurationResolver`)
    - `WorkerProcess.Start()` (real: `StartProcessAsync()`)
    - `SendStartStreamMessage` (doesn't exist)
    - `maxConcurrentRequests` (invented setting)
    - `functions.json` in specialization flow (doesn't exist)
    - Also: false claim about `SendInvocationRequest` wrapping with `request_id = new GUID`
15. **azure-functions-deep-dive** — ep6 misses real specialization path (`WebHostRpcWorkerChannelManager.SpecializeAsync()`/`UsePlaceholderChannel()`)
16. **azure-functions-deep-dive** — ep4 false: `SendInvocationRequest` does NOT wrap with `request_id = new GUID`; correlation = `invocation_id`
17. **azure-functions-deep-dive** — ep3 false: `Server/Startup.cs` maps `FunctionRpc.FunctionRpcBase`, not `MapGrpcService<FunctionRpcService>`
18. **azure-aca-deep-dive** — ep6 (Envoy ingress) "highest hallucination risk in whole review"; full request path stated as fact when only edge proxy/TLS documented
19. **azure-aca-deep-dive** — ep3 Envoy weight ownership stated too strongly
20. **azure-aca-deep-dive** — ep5 Dapr port 3501, Sentry, mTLS plumbing cited from upstream as if ACA-confirmed

### Wrong technical claims (101)
21. **azure-functions-101** — `en|ko/03-host-and-worker.md:99` Python concurrency mischaracterized (treats Python like Node single-threaded)
22. **azure-functions-101** — `en|ko/04-first-deploy.md` teaches LEGACY Consumption as primary while saying Flex is default
23. **azure-aks-deep-dive** — ep5 wrong: claims CA "runs as separate Deployment"; in AKS, Microsoft manages CA in control plane
24. **azure-aks-deep-dive** — ep3 missing 2026 Pod Subnet vs Node Subnet distinction
25. **azure-app-service-101** — `en/05-configuration.md` outdated `FLASK_ENV` guidance (removed in Flask 2.3/3.x)
26. **azure-app-service-101** — `en/06-logging-monitoring.md` `CorrelationFilter` accesses `g` without request-context guard
27. **ai-web-dev-101** — `04-rag-intro.md` description says cosine, code uses raw dot product

### Structural blockers (deep-dive)
28. **azure-functions-deep-dive** — Missing `## Source Version` and `## Call Path Summary` in all 12 files
29. **azure-functions-deep-dive** — Wrong series counters `(2/7)…(5/7)` for 6-part series
30. **azure-aks-deep-dive** — Missing `## Source Version` / `## Call Path Summary` in all 6 files
31. **azure-app-service-deep-dive** — Missing same scaffolding in all 12 files

## Cross-series P1 (important, not blocking)

### Stale 2026 framing
- azure-aks-101 + azure-aks-deep-dive: ingress chapters miss ingress-nginx retirement / Gateway API direction
- azure-functions-101: ch5 plan comparison reads as survey not decision; ch6 missing platform-side cold-start mitigation (placeholder/warm capacity)
- ai-web-dev-101: `gpt-3.5-turbo` is legacy; switch to `gpt-4o-mini` class
- ai-web-dev-101: never mentions Responses API as primary

### Security messaging
- ai-web-dev-101: hardcoded API keys in 1/4, `eval()` in 5, secret-in-CLI in 6
- ai-web-dev-101: RAG chapter missing prompt-injection warnings

### Bilingual drift
- azure-app-service-101: English regresses to thinner/older guidance vs Korean
- azure-functions-101: blog scaffolding ("Coming up next") in all 14 ebook-bound files

### Korean prose residue
- azure-app-service-101: `요약하면:`, `민감 정보번호`
- azure-app-service-deep-dive: mixed-English (`large cache priming`, `expensive startup path`)
- azure-functions-101: `요약하면`, `정리하면`, `다음 화에서`
- azure-functions-deep-dive: `요약하면`, `게다가`

### Reproducibility (LLM)
- llm-from-scratch-101: unpinned TinyShakespeare URL, no seed setting, hardcoded `vocab_size=65`
- llm-from-scratch-101: streaming/non-streaming chat semantics differ (history dropped in streaming)
- llm-from-scratch-101: missing PyTorch 2.x notes (SDPA, `torch.compile`, `inference_mode`, `mps`)

## Cross-series P2 (polish)

- Tag line duplication (extra bolded `**Tags:**` before required final `Tags:`) — azure-app-service-101
- `## Series Index` duplicating canonical TOC — azure-app-service-101 en
- Repeated chapter-template intros across deep-dive series
- AI-slop/promotional phrasing in ai-web-dev-101 (`거대한 두뇌`, `축하드립니다`)
- Emoji in ai-web-dev-101 ep3 code block (`🧑‍🍳`) violates no-emoji rule
- LOC claim in llm-from-scratch-101 (`~720 LOC`) not well supported

## Recommended fix order

### Wave 1 (P0, highest reader-impact bugs)
1. **azure-aca-101** — strip duplicated checklist filler (14 files, mechanical fix)
2. **llm-from-scratch-101** — fix attention/block contract (P0 #1) — affects all downstream chapters
3. **llm-from-scratch-101** — fix ep8 SFT shifted-labels math
4. **llm-from-scratch-101** — fix Korean ep8/ep9 OOV (either remove Hangul or rebuild tokenizer)
5. **ai-web-dev-101** — rewrite `03-ai-chatbot.md` for current Vercel AI SDK
6. **ai-web-dev-101** — fix `06-deploy.md` FastAPI startup command

### Wave 2 (P0, invalid CLI / stale facts)
7. **azure-app-service-101** — `en/05`, `en/06`, `en/07` CLI/code fixes
8. **azure-functions-101** — `ch7` invalid CLI, `ch3` Python concurrency, `ch1` timeout
9. **azure-aca-101** — fix scaling taxonomy

### Wave 3 (P0, deep-dive hallucinations)
10. **azure-functions-deep-dive** — replace 6 invented API names with real `5e59423` types
11. **azure-functions-deep-dive** — fix ep4 invocation path + ep6 specialization path
12. **azure-aca-deep-dive** — rewrite ep6 (Envoy) with documented/inferred labels
13. **azure-aca-deep-dive** — downgrade ep3 Envoy weight + ep5 Dapr ACA mapping certainty
14. **azure-aks-deep-dive** — fix ep5 CA placement, ep3 CNI subnet split

### Wave 4 (P0, structural deep-dive scaffolding)
15. Add `## Source Version` + `## Call Path Summary` to all azure-*-deep-dive files
16. Fix azure-functions-deep-dive series counters `/7` → `/6`

### Wave 5 (P1, ebook prep)
17. azure-functions-101 (first ebook) — Flex-as-primary in ch4, blog scaffolding sweep
18. ai-web-dev-101 — model name updates, security cleanup, Responses API note
19. Bilingual drift pass (azure-app-service-101 en→ko)

### Wave 6 (P1, framing)
20. AKS ingress 2026 framing
21. Korean prose pass (humanize-korean S1)

### Wave 7 (P2, polish)
22. Tag line dedup, Series Index decision, AI-slop phrasing, LOC claim

## Per-series commit strategy (Path C: per-series atomic commits)

Each series gets one or more commits, in this format:
```
fix(<series>): apply oracle review P0/P1 fixes

P0:
- <issue> at <file>:<line>
- ...

P1:
- ...

Ref: .sisyphus/reviews/<series>.md
```

After each per-series commit:
1. Run `python3 .sisyphus/medium/finalize-posts.py`
2. Re-regenerate `medium/<NN>.md` if `en/` changed
3. Update ROADMAP Phase 7 checkbox for that series
4. Update `series.yaml.meta.validated_ref` after final commit
