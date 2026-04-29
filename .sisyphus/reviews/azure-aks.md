# Oracle Content Review — azure-aks-101 + azure-aks-deep-dive

- **Session**: `ses_228fdc42dffei8n4V1PU7yCjkT`
- **Date**: 2026-04-29
- **Verdicts**:
  - `azure-aks-101`: **needs minor-fixes** (publishable after correction pass)
  - `azure-aks-deep-dive`: **needs-rework** (not deep enough yet)
- **Effort**: 101=Short, deep-dive=Medium

## Per-article scores

### azure-aks-101
| Episode | ko | en |
|---|---:|---:|
| 01 what is AKS | 4 | 4 |
| 02 cluster architecture | 4 | 4 |
| 03 first cluster and deploy | 3 | 3 |
| 04 pod / deployment / service | 4 | 4 |
| 05 networking and ingress | 3 | 3 |
| 06 scaling HPA / CA / KEDA | 3 | 3 |
| 07 monitoring and ops | 4 | 4 |

### azure-aks-deep-dive
| Episode | ko | en |
|---|---:|---:|
| 01 control plane anatomy | 3 | 3 |
| 02 kubelet and containerd | 4 | 4 |
| 03 CNI and Azure CNI Overlay | **2** | **2** |
| 04 scheduler and pod placement | 3 | 3 |
| 05 HPA and CA internals | **2** | **2** |
| 06 KEDA internals | 3 | 3 |

## Top 8 issues

1. **2026 ingress framing stale** — `aks-101 en|ko/05-networking-and-ingress.md:144-156`. App Routing presented as recommended NGINX path; omits 2026 reality that upstream ingress-nginx is in retirement, AKS steering toward Gateway API.
2. **KEDA Service Bus example not runnable** — `aks-101 en|ko/06-scaling-hpa-ca-keda.md:194-210`. Lacks auth wiring (`TriggerAuthentication` or `connectionFromEnv`).
3. **Probe guidance too toy-like** — `aks-101 en|ko/03-first-cluster-and-deploy.md:206-223`. Readiness/liveness identical, no startup probe.
4. **Deep-dive CNI collapses flat networking into generic Azure CNI** — `aks-deep-dive en|ko/03-cni-and-azure-cni-overlay.md:24-27,45-51`. Missing 2026 Pod Subnet vs Node Subnet distinction.
5. **Scheduler diagnosis line misleading** — `aks-deep-dive en|ko/04-scheduler-and-pod-placement.md:60-64`. "Has feasible nodes but keeps losing on score" not real Pending root cause; score ranks feasible nodes.
6. **AKS-specific CA placement wrong** — `aks-deep-dive en|ko/05-hpa-and-cluster-autoscaler-internals.md:27-29`. Says CA "runs as separate Deployment"; in AKS, Microsoft manages CA in managed control plane.
7. **Ep5 hand-wavy on internals** — `aks-deep-dive en|ko/05:38-55`. Names HPA 15s sync, CA binpacking; skips CA scan interval/profile defaults, unschedulable-pod timing, scale-down delays, HPA↔CA race windows.
8. **KEDA "internals" never explains scaler interface** — `aks-deep-dive en|ko/06-keda-internals.md:36-50`. No real treatment of scaler contract, auth path, operator vs adapter split.

## Cross-cutting concerns

- 101 stays in bounds; deep-dive often doesn't go far enough beyond it (ep3/5/6)
- Deep-dive missing repo-mandated `## Source Version` / `## Call Path Summary` sections
- Hallucination risk = stale framing/omission, not full fabrication
- `.sisyphus/style/check-ko.sh` returned 0 hits

## Verdicts

- **azure-aks-101**: minor-fixes
- **azure-aks-deep-dive**: needs-rework

## Action list

1. **P0 [Deep Dive]** Rewrite ep5 around AKS reality: HPA in control plane, CA managed by AKS, CA profile defaults, scan interval, scale-down delays, HPA↔CA interaction
2. **P0 [101 + Deep Dive]** Update networking chapters for 2026 ingress posture (managed NGINX usable but Gateway API migration context)
3. **P0 [101]** Replace KEDA example with runnable Azure Service Bus + auth (`TriggerAuthentication`/`connectionFromEnv`)
4. **P0 [Deep Dive]** Split flat networking: Azure CNI Pod Subnet vs Azure CNI Node Subnet (legacy) in ep3
5. **P1 [101]** Improve FastAPI deployment manifest: `startupProbe`, realistic readiness/liveness timing
6. **P1 [Deep Dive]** Add `## Source Version` and `## Call Path Summary` to all 6 deep-dive posts
7. **P1 [Deep Dive]** Fix ep4 scheduler diagnosis language (failed filters, constraints, preemption/backoff, bind/retry)
8. **P1 [Deep Dive]** Expand ep6: scaler interface, operator vs metrics-adapter split
9. **P2 [101]** Add sentence on `CriticalAddonsOnly=true:NoSchedule` for system/user pool separation
10. **P2 [Deep Dive]** Reduce repeated thesis lines; add one worked trace per episode
