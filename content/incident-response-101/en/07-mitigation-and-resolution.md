---
series: incident-response-101
episode: 7
title: "Incident Response 101 (7/10): Mitigation and Resolution"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Incident
  - Mitigation
  - Resolution
  - Rollback
  - Operations
seo_description: Learn how to choose mitigation tactics, distinguish them from full resolution, and verify recovery with service metrics.
last_reviewed: '2026-05-15'
---

# Incident Response 101 (7/10): Mitigation and Resolution

Stopping customer pain is not the same as fixing the system. That distinction sounds obvious in calm conversation, but during a live incident teams often announce "resolved" when they have only bought a temporary reduction in impact.

Mitigation and resolution have different goals, different owners, and sometimes different timelines. Confusing them creates both technical and communication risk.

This is the 7th post in the Incident Response 101 series. This post explains how to choose between rollback, scale-out, throttling, and kill switches, and how to prove that the service is truly healthy before you close the incident.


![incident response 101 chapter 7 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/incident-response-101/07/07-01-diagram-at-a-glance.en.png)
*incident response 101 chapter 7 flow overview*
> Mitigation stops the bleeding now. Resolution fixes the cause later. Separate them and you double your speed.

## Questions to Keep in Mind

- What makes rollback such a powerful mitigation tool?
- When should you scale out, throttle, or use a kill switch instead?
- Why is "impact reduced" not enough to declare resolution?

## Why this topic matters

A service can look calmer while the underlying cause is still present. That is why incidents often reopen at night or after traffic shifts if the team stops at temporary containment.

Separating mitigation from resolution keeps the response honest. It improves communication, clarifies ownership, and prevents teams from skipping the verification step.

## Diagram at a glance

The response path moves from impact containment to stability and then to root removal. If those states are not separated, both operations and communication get fuzzy.

## Key Terms

- **mitigation**: stop the damage.
- **resolution**: remove the cause.
- **rollback**: revert to the previous version.
- **kill switch**: turn a feature off immediately.
- **throttle**: limit incoming traffic.

## Before/After

**Before**: announce only after a full fix.

**After**: announce as soon as damage is contained; announce resolution separately.

## Hands-on: A Mini Mitigation Kit

### Step 1 — Rollback

```python
def rollback(version):
    return {"action": "rollback", "to": version}
```

Rollback is the fastest mitigation in most cases. Returning to the last known-good version buys investigation time without requiring you to understand the failure first.

### Step 2 — Scale out

```python
def scale_out(service, replicas):
    return {"service": service, "replicas": replicas}
```

Scaling out adds capacity to absorb unexpected load. It does not fix the root cause, but it keeps the service alive while you investigate.

### Step 3 — Throttle

```python
def throttle(endpoint, rps):
    return {"endpoint": endpoint, "rps": rps}
```

Throttling limits inbound traffic to a rate the system can handle. It trades some user requests for overall service stability—a deliberate, temporary degradation.

### Step 4 — Kill switch

```python
FLAGS = {}

def kill(feature):
    FLAGS[feature] = False
    return FLAGS[feature]
```

A kill switch disables a feature instantly via a flag. If the flag already exists before the incident, mitigation is a one-line change rather than an emergency deployment.

### Step 5 — Verify recovery

```python
def verify(metrics):
    return metrics.get("err_ratio", 1) < 0.01
```

Recovery must be confirmed with numbers, not feelings. Checking that the error ratio dropped below threshold is the quantitative proof that your mitigation worked.

## What to Notice in This Code

- Mitigation is a small action.
- A kill switch is one flag line.
- Verification is quantitative.

## Five Common Mistakes

1. **Only rolling forward, never back.**
2. **No prepared kill switch.**
3. **Announcing mitigation as resolution.**
4. **Closing without verification.**
5. **Forgetting to unthrottle.**

## How This Shows Up in Production

A feature flag system and an autoscaler are wired into a single runbook command, so mitigation takes under two minutes.

## How a Senior Engineer Thinks

- Mitigation first.
- Resolution during business hours.
- A kill switch on every feature.
- Verify with numbers.
- Unthrottling is also an event.

A senior engineer prioritizes mitigation but insists on separate, calm verification for resolution. Post-mitigation state transitions — like unthrottling — are recorded as distinct events because every operational state change matters.

## Example mitigation order

During a live incident, the team should usually scan mitigation options in the order below.

1. Is there a clean rollback to the previous known-good state?
2. Can a feature flag or kill switch disable only the broken path?
3. If the issue is capacity-related, can you scale out immediately?
4. If the problem is traffic amplification, can throttling protect the critical path?
5. After each action, which metric proves that recovery is real?

That order keeps the team focused on the fastest credible reduction in customer impact instead of the most elegant long-term repair.

## Mitigation strategy comparison

Each mitigation tool has different execution speed and risk. Knowing these trade-offs in advance speeds up the live decision.

| Strategy | Execution speed | Risk | Best fit |
| --- | --- | --- | --- |
| Rollback | 1–5 min | Low | Deploy-caused, previous version stable |
| Failover | 1–10 min | Medium | Instance / node failure |
| Traffic block | 30 sec–2 min | High | DDoS, bad traffic, input flood |
| Feature disable | 30 sec–1 min | Low | Specific feature bug, A/B test abort |

Rollback is fastest and safest, but only if the rollback procedure is pre-built. Traffic blocking is fast but can hit legitimate users — use with caution. In practice, teams try feature disable or rollback first, then move to failover or traffic block when those are unavailable.

## Canary rollback pattern

Rollback is the most powerful mitigation tool, but rolling back 100% at once hides normal features that shipped alongside the broken one. In practice, teams often use a canary rollback — reverting a small traffic slice first.

```python
def canary_rollback(service, old_version, canary_ratio=0.1):
    """
    Route a fraction of traffic back to the previous version.
    """
    return {
        "service": service,
        "old_version": old_version,
        "canary_ratio": canary_ratio,
        "status": "rollback_started",
        "watch_metrics": ["error_rate", "latency_p99"],
    }

def expand_rollback(service, canary_ratio, target_ratio):
    """
    Gradually increase the rollback ratio.
    """
    if canary_ratio >= target_ratio:
        return {"status": "complete", "ratio": canary_ratio}

    new_ratio = min(canary_ratio + 0.1, target_ratio)
    return {
        "service": service,
        "new_ratio": new_ratio,
        "status": "expanding",
    }

# Usage
initial = canary_rollback("payment-api", "v2.4.1", canary_ratio=0.1)
print(f"10% traffic rolled back to {initial['old_version']}")

# After monitoring confirms metrics are healthy, expand
step1 = expand_rollback("payment-api", 0.1, 0.5)
print(f"Error rate normal, expanding to 50%: {step1['new_ratio']}")

step2 = expand_rollback("payment-api", 0.5, 1.0)
print(f"Full rollback complete: {step2['status']}")
```

The advantage: if the rollback itself causes unexpected issues, you can stop at 10% and try a forward fix for the remaining 90%.

In production, teams integrate these staged ratios with Argo Rollouts, Flagger, or custom deploy tools for metric-driven automatic expansion.

## Temporary measures vs. permanent fixes

The mitigation/resolution distinction can also be framed by change duration. Temporary measures are applied during the incident but must be reverted later. Permanent fixes stay in place.

Examples:

- **Temporary**: cut API rate limit from 50 to 25 RPS → restore later.
- **Permanent**: change default timeout from 3 s to 5 s → keep.
- **Temporary**: redirect traffic away from one region → redistribute later.
- **Permanent**: delete the code path that caused the failure → keep.

Every temporary measure must have a recorded "undo" schedule. Otherwise it hardens into unintended permanent state. Good practice: include a "rollback plan" section in the mitigation doc.

Good format:

- mitigation: rate limit 50 → 25 RPS, rollback: staged restore after 24 h, owner: @platform
- resolution: timeout default 3 s → 5 s, deploy after tests pass, rollback plan: N/A

## Runbook structure for mitigation and resolution

Separating mitigation from resolution speeds up decision-making. Mixing "stop harm now" and "remove cause later" in the same queue tangles priorities. A runbook with explicit phases fixes this.

| Phase | Purpose | Typical actions | Exit criteria |
| --- | --- | --- | --- |
| Detect | Confirm anomaly | Alert verification, impact estimate | Incident declared or dismissed |
| Mitigate | Reduce customer harm | Rollback, kill switch, throttle | Error rate / failure rate drops |
| Stabilize | Maintain safe state | Scale adjustment, cache/queue check | Metrics stable for sustained window |
| Resolve | Apply permanent fix | Code fix, config correction | Regression test passes |
| Verify | Confirm recovery | SLI recovery check, customer notice | Closure approved |

When this structure is team-wide vocabulary, sharing "we are in Stabilize" in the incident channel is enough to align everyone on what happens next.

### Automation script

```python
def mitigation_plan(can_rollback: bool, has_flag: bool, traffic_spike: bool) -> list[str]:
    actions = []
    if can_rollback:
        actions.append("rollback")
    if has_flag:
        actions.append("disable_feature_flag")
    if traffic_spike:
        actions.append("apply_throttle")
    if not actions:
        actions.append("scale_out")
    return actions

def resolution_ready(test_pass: bool, config_reviewed: bool, peer_approved: bool) -> bool:
    return test_pass and config_reviewed and peer_approved
```

This script is not sophisticated automation — it is explicit decision criteria. Encoding conditions in code ensures that a 3 AM responder applies the same rules as the daytime team.

### Phase transition criteria

- Mitigate → Stabilize: error rate below threshold and sustained for 10+ min.
- Stabilize → Resolve: no further spread signals, root cause candidates converging.
- Resolve → Verify: fix deployed, regression tests pass.
- Verify → Close: external notice sent, postmortem ticket linked.

Documenting transition criteria prevents "mood-based closure" — declaring the incident over because things feel calm rather than because gates were satisfied.

## Operational tips

- Keep a rollback-ready state at all times.
- Kill switches must be executable in 1–2 clicks.
- Define unthrottle conditions during the incident, not after.
- Track the resolution task separately even after mitigation succeeds.

Following these four rules dramatically reduces the pattern where a stabilized incident re-explodes hours later.

## Recovery verification gates

```yaml
recovery_gates:
  error_ratio_below: 0.01
  p95_latency_below_ms: 800
  sustained_minutes: 15
  customer_updates_sent: true
  postmortem_ticket_created: true
```

Recovery declarations should be gate-based, not instinct-based. Gates ensure judgment consistency even across shift handoffs.

## Post-mitigation observation window

Immediately after mitigation, a short observation window is essential. Check error rate, latency, and queue backlog at 5-minute intervals. If any sign of re-escalation appears, revert to the previous phase immediately. Many teams skip this window and prematurely close incidents.

Also check for side effects that the mitigation itself introduced. For example, throttling protects the critical path but intentionally delays some requests — prepare the unthrottle condition and customer notice wording in advance.

## Mitigation-to-resolution transition checkpoints

| Transition | Required condition | Verification metric |
| --- | --- | --- |
| Mitigate → Stabilize | Error rate dropped and held for 10 min | error_ratio, p95 |
| Stabilize → Resolve | Root cause candidates converged, no new spread | timeline, alert noise |
| Resolve → Verify | Permanent fix deployed, regression test passed | test report |
| Verify → Close | Customer notice sent, postmortem link created | comms log |

With transition criteria documented, "mood-based closure" is blocked. The observation window right after mitigation is especially critical because re-escalation probability is highest then.

## On-call command sheet template

```text
[mitigation-command-sheet]
- rollback_command:
- feature_flag_off_command:
- scale_out_command:
- throttle_command:
- verify_query:
- rollback_of_mitigation_plan:
```

During an incident, even the time spent finding a command is cost. Having this sheet prepared per service dramatically improves the first 10 minutes of response quality.

## Post-mitigation observation table

| Window | Metric to check | Criterion |
| --- | --- | --- |
| 0–5 min | error ratio | Downward trend confirmed |
| 5–10 min | p95 latency | Below threshold sustained |
| 10–15 min | new critical alerts | 0 fired |
| 15+ min | customer reports | No increase |

This table prevents premature closure right after mitigation appears to work.

## Checklist

- [ ] Rollback procedure documented and tested.
- [ ] Kill switch inventory maintained.
- [ ] Throttling policy and unthrottle criteria defined.
- [ ] Recovery verification metric specified.
- [ ] Post-mitigation observation window scheduled.
- [ ] Temporary vs permanent fix documented for each action.

## Practice Problems

1. Define mitigation in one line.
2. Define resolution in one line.
3. Define kill switch in one line.

## Wrap-up and Next Steps

Mitigation stops the harm; resolution removes the cause. Separating them enables fast containment, honest communication, and safe follow-up fixes. Use rollback, scale-out, throttle, and kill switches to keep the service alive first, then verify full recovery with numbers before declaring resolution.

Next, we cover the postmortem — turning incident lessons into organizational assets.

## Answering the Opening Questions

- **How is putting out the fire different from removing the cause?**
  - Mitigation targets the short-term goal of "stop user harm right now." Resolution targets the permanent goal of "ensure this cause never recurs." Trying to accomplish both in one sitting delays mitigation and grows the blast radius. Stop the bleeding first, then invest time in the precise fix.
- **Why is rollback the most powerful mitigation tool?**
  - Most incidents start with a recent change (deploy, config, feature flag). Rollback undoes that change wholesale, returning to the known-safe state of "at least yesterday it worked." It can be used before diagnosis is complete—nearly the only first-response action that does not require full understanding of the cause.
- **When should you use scale-out, throttle, or kill switch?**
  - Scale-out: when traffic exceeds capacity and correct code fails only because resources are exhausted. Throttle: when excessive calls from some users/endpoints are collapsing the service for everyone else. Kill switch: when a specific feature is itself the source of the incident and must be turned off immediately. All three are mitigation tools, not resolution—each must be followed by a separate root-cause fix.
<!-- toc:begin -->
## In this series

- [Incident Response 101 (1/10): What is an Incident?](./01-what-is-incident.md)
- [Incident Response 101 (2/10): Severity Classification](./02-severity.md)
- [Incident Response 101 (3/10): Initial Response](./03-initial-response.md)
- [Incident Response 101 (4/10): Communication](./04-communication.md)
- [Incident Response 101 (5/10): Writing the Timeline](./05-timeline.md)
- [Incident Response 101 (6/10): Root Cause Analysis](./06-root-cause-analysis.md)
- **Mitigation and Resolution (current)**
- Postmortem (upcoming)
- Prevention (upcoming)
- Building an Incident Runbook (upcoming)

<!-- toc:end -->

## References

### Official Docs
- [Mitigation during incidents - PagerDuty](https://response.pagerduty.com/during/mitigation/)
- [Release Engineering - Google SRE Book](https://sre.google/sre-book/release-engineering/)
- [Feature Toggles - Martin Fowler](https://martinfowler.com/articles/feature-toggles.html)
- [Incident management guide - Atlassian](https://www.atlassian.com/incident-management)

Tags: Incident, Mitigation, Resolution, Rollback, Operations
