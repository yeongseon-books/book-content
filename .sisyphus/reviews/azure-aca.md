# Oracle Content Review — azure-aca-101 + azure-aca-deep-dive

- **Session**: `ses_228f98a73ffekhYkirsLECyGZN`
- **Date**: 2026-04-29
- **Verdicts**:
  - `azure-aca-101`: **FAIL — not publish-ready**
  - `azure-aca-deep-dive`: **conditional fail — promising but unsafe at hallucination standard**
- **Effort**: Large (3d+)

## Per-series synthesis

### azure-aca-101
**Editorial corruption**: "Operations checklist" block is duplicated dozens of times in every post (both ko and en). Series feels machine-generated. Plus 2026 scaling semantics wrong.

### azure-aca-deep-dive
Stronger series. Ep4 (KEDA) is best — distinct from AKS KEDA, good caveat discipline. Eps 3, 5, 6 move from source-grounded to plausible reconstruction without explicit labeling.

## Per-article scores

### azure-aca-101 (all 2/5)
| Ep | Article | Score | Note |
|---|---|---:|---|
| 1 | What is ACA | 2 | Decent intro, ruined by duplicated filler |
| 2 | Environment / App / Revision | 2 | Core model OK, too thin, duplicated filler |
| 3 | First deploy | 2 | CLI mostly current, deployment path incomplete |
| 4 | Ingress / traffic split | 2 | Commands current, runtime explanation too assertive |
| 5 | Scaling with KEDA | 2 | **Real 2026 accuracy issue** |
| 6 | Dapr integration | 2 | Dapr example illustrative, not runnable |
| 7 | Monitoring / ops | 2 | KQL OK, App Insights framing muddled |

### azure-aca-deep-dive
| Ep | Article | Score | Note |
|---|---|---:|---|
| 1 | ACA architecture | 3 | Good map, source boundary too loose |
| 2 | Environment internals | **4** | Best sourced boundary article |
| 3 | Revision / traffic split | 3 | Strong, Envoy-weight overstates certainty |
| 4 | KEDA in ACA | **4** | Distinct from AKS, best caveat discipline |
| 5 | Dapr sidecar internals | 3 | Good upstream Dapr grounding, ACA mapping too strong |
| 6 | Envoy ingress path | **2** | Highest hallucination risk in set |

## Top 8 issues

1. **Wrong 2026 scaling taxonomy** — `aca-101 en/05-scaling-with-keda.md:39-50`. Current ACA: HTTP, TCP, custom. Article omits TCP, elevates CPU/memory to top-level.
2. **Duplicated checklist loops in ALL 14 ACA 101 files** — starts at `aca-101 en|ko/01-what-is-aca.md:116-117`. Same corruption pattern in every post.
3. **Dapr component YAML not runnable** — `aca-101 en/06-dapr-integration.md:68-77`. Lacks auth/secret context.
4. **Monitoring blurs App Insights vs Dapr telemetry** — `aca-101 en/07-monitoring-and-ops.md:72-79`. `--dapr-connection-string` configures Dapr service-to-service telemetry, not general app tracing.
5. **"Enough to explain mechanism accurately" too strong** — `aca-deep-dive en/03-revision-and-traffic-split.md:187-192`. ACA private config translation not exposed; should be best-fit inference.
6. **Upstream Dapr injection used as if it explains ACA** — `aca-deep-dive en/05-dapr-sidecar-internals.md:62-69`. Useful analogy, not proven implementation path.
7. **Full request path stated as fact** — `aca-deep-dive en/06-envoy-ingress-path.md:36-38`. Edge proxy/TLS documented; full Service/Pod hop inferred.
8. **Cold-start "wakes zero-replica" story not sourced** — `aca-deep-dive en/06:182-193`. Plausible but not from ACA internals docs.

## Hallucination candidates (deep-dive)

- "ACA runs on AKS / hidden Kubernetes substrate" — directionally right, needs explicit Microsoft citation or softer wording
- Envoy-weight ownership in ep3 — most defensible inference, still inference
- ACA sidecar injection following upstream admission-webhook (ep5)
- Dapr port `3501` from upstream defaults, not ACA docs (ep5:149-153)
- Control-plane address, Sentry, trust anchors, mTLS plumbing (ep5:229-235,290-296)
- Full first-request path through Envoy (ep6:36-38, 153-163, 182-193, 282) — **highest-risk reconstruction in whole review**

## Verdicts

- **azure-aca-101**: FAIL (duplicated filler alone blocks publication; scaling article has real accuracy problem)
- **azure-aca-deep-dive**: conditional fail until eps 3, 5, 6 rewritten with clearer evidence boundaries

## Action list

### P0
1. Remove duplicated checklist loops from all 14 ACA 101 ko/en files
2. Fix `05-scaling-with-keda` to 2026 ACA taxonomy: HTTP / TCP / custom (CPU/memory under custom)
3. Rewrite deep-dive ep6 — every step tagged **documented** vs **inferred**
4. Rewrite deep-dive ep3 — downgrade "Envoy owns weights" from assertion to inference
5. Rewrite deep-dive ep5 — separate upstream Dapr-on-K8s from likely-ACA behavior
6. Add explicit Microsoft source for "ACA runs on AKS" claim, or soften

### P1
7. Fix monitoring article — separate App Insights instrumentation from Dapr telemetry
8. Replace 101 Dapr YAML with runnable example OR explicit schematic label
9. Expand first-deploy article (build/push/registry prereqs) OR rename "deploy existing image"
10. Add "evidence model" section to each deep-dive post

### P2
11. Remove/source Envoy mentions in 101 (keep internals in deep dive)
12. Smooth 101 English prose
