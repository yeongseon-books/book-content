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

Stopping customer pain is not the same as fixing the system. That distinction sounds obvious in calm conversation, but during a live incident teams often announce “resolved” when they have only bought a temporary reduction in impact.

Mitigation and resolution have different goals, different owners, and sometimes different timelines. Confusing them creates both technical and communication risk.

This is the 7th post in the Incident Response 101 series. This post explains how to choose between rollback, scale-out, throttling, and kill switches, and how to prove that the service is truly healthy before you close the incident.


![incident response 101 chapter 7 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/incident-response-101/07/07-01-diagram-at-a-glance.en.png)
*incident response 101 chapter 7 flow overview*
> Mitigation stops the bleeding now. Resolution fixes the cause later. Separate them and you double your speed.

## Questions to Keep in Mind

- What makes rollback such a powerful mitigation tool?
- When should you scale out, throttle, or use a kill switch instead?
- Why is “impact reduced” not enough to declare resolution?

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

### Step 2 — Scale out

```python
def scale_out(service, replicas):
    return {"service": service, "replicas": replicas}
```

### Step 3 — Throttle

```python
def throttle(endpoint, rps):
    return {"endpoint": endpoint, "rps": rps}
```

### Step 4 — Kill switch

```python
FLAGS = {}

def kill(feature):
    FLAGS[feature] = False
    return FLAGS[feature]
```

### Step 5 — Verify recovery

```python
def verify(metrics):
    return metrics.get("err_ratio", 1) < 0.01
```

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

## Example mitigation order

During a live incident, the team should usually scan mitigation options in the order below.

1. Is there a clean rollback to the previous known-good state?
2. Can a feature flag or kill switch disable only the broken path?
3. If the issue is capacity-related, can you scale out immediately?
4. If the problem is traffic amplification, can throttling protect the critical path?
5. After each action, which metric proves that recovery is real?

That order keeps the team focused on the fastest credible reduction in customer impact instead of the most elegant long-term repair.

## Checklist

- [ ] Rollback procedure.
- [ ] Kill switch inventory.
- [ ] Throttling policy.
- [ ] Recovery verification metric.

## Practice Problems

1. Define mitigation in one line.
2. Define resolution in one line.
3. Define kill switch in one line.

## Wrap-up and Next Steps

Next, we cover the postmortem.

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
