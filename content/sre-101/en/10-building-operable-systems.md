---
series: sre-101
episode: 10
title: "SRE 101 (10/10): Building Operable Systems"
status: content-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - SRE
  - Operability
  - Architecture
  - Reliability
  - Engineering
seo_description: A capstone guide to building operable systems covering observability, automation, safe change, resilience, and integrated operational design
last_reviewed: '2026-05-14'
---

# SRE 101 (10/10): Building Operable Systems

Many systems treat operability as something to bolt on after the first incidents arrive. Logs are added later, rollback gets documented later, and automation only appears after people have already repeated the same painful task enough times to feel forced into it.

That delay is expensive because operability compounds. Systems that are easy to observe, change safely, recover, and automate become easier to improve; systems that are not become progressively harder to trust.

This is the final post in the SRE 101 series. It gathers the earlier ideas into one design lens: observability, safe change, resilience, and automation should be built into the system the same way functional behavior is.

## Questions to Keep in Mind

- Why is operability a design property instead of a post-launch enhancement?
- Why do observability, automation, safe change, and resilience need to be judged together?
- What should a team ask first when auditing whether a system is truly operable?

## Big Picture

![sre 101 chapter 10 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/sre-101/10/10-01-concept-at-a-glance.en.png)

*sre 101 chapter 10 flow overview*

This picture places Building Operable Systems inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.



## Why this topic matters

A feature without operability returns as debt. It may ship successfully once, but every later change, incident, and debugging session becomes more expensive than it needed to be.

Strong teams therefore design the operational path on purpose. They ask not only “does this feature work?” but also “can we understand it, roll it back, recover it, and automate it?”

> Operability should be designed in like a feature, not bolted on later.

## Concept at a glance

## Key Terms

- **operability**: how *easy* it is to *operate* the system.
- **observability**: ability to *infer internal state* from *outside*.
- **safe change**: *canary* and *rollback*-friendly change.
- **resilience**: ability to *recover* from *partial failure*.
- **runbook-as-code**: a *procedure* expressed as *code*.

## Before/After

**Before**: build the *feature*; defer *operations*.

**After**: build the *feature* and its *operability* together.

## Hands-on: An Operability Audit

### Step 1 — Observability check

```python
def has_obs(metrics, logs, traces):
    return all([metrics, logs, traces])
```

### Step 2 — Safe deploy

```python
def safe_deploy(canary_pct, rollback_ready):
    return canary_pct <= 5 and rollback_ready
```

### Step 3 — Resilience patterns

```python
def has_resilience(retry, timeout, breaker):
    return all([retry, timeout, breaker])
```

### Step 4 — Automation ratio

```python
def auto_ratio(auto_min, total_min):
    return auto_min / total_min
```

### Step 5 — Operability score

```python
def score(obs, deploy, resil, auto):
    return sum([obs, deploy, resil, auto >= 0.7]) / 4
```

## What to Notice in This Code

- We check *four dimensions*.
- We *prove* it with *code*.
- A *score* sets the *priority*.

## Five Common Mistakes

1. **Treating *operability* as a *later* concern.**
2. **Missing *observability*.**
3. **Full rollouts without *canaries*.**
4. **No *resilience* patterns.**
5. **Insufficient *automation*.**

## How This Shows Up in Production

A *platform team* ships a *common operability* template; *product teams* focus on the *business*.

## How a Senior Engineer Thinks

- *Operability* is part of the *feature*.
- *Observability* is the *baseline* of debugging.
- Make *changes* *small* and *reversible*.
- Stop *partial failure* from becoming *total failure*.
- *Learning* is *amplified* in *operations*.

## Checklist

- [ ] Four-dimension *checklist*.
- [ ] *Canary/rollback* standard.
- [ ] *Common library*.
- [ ] *Operability KPI*.

## Practice Problems

1. Define *operability* in one line.
2. Define *safe change* in one line.
3. Define *resilience* in one line.

## Wrap-up and Next Steps

Congrats on finishing the series. Next, head into *Incident Response 101* and dive deeper into the *operations floor*.

## Answering the Opening Questions

- **Why is operability a design property instead of a post-launch enhancement?**
  - The article treats Building Operable Systems as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Why do observability, automation, safe change, and resilience need to be judged together?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What should a team ask first when auditing whether a system is truly operable?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [SRE 101 (1/10): What is SRE?](./01-what-is-sre.md)
- [SRE 101 (2/10): Reliability](./02-reliability.md)
- [SRE 101 (3/10): SLI, SLO, SLA](./03-sli-slo-sla.md)
- [SRE 101 (4/10): Error Budget](./04-error-budget.md)
- [SRE 101 (5/10): Monitoring](./05-monitoring.md)
- [SRE 101 (6/10): Incident Response](./06-incident-response.md)
- [SRE 101 (7/10): Postmortem](./07-postmortem.md)
- [SRE 101 (8/10): Reducing Toil](./08-reducing-toil.md)
- [SRE 101 (9/10): Capacity Planning](./09-capacity-planning.md)
- **Building Operable Systems (current)**

<!-- toc:end -->

## References

- [Building Secure and Reliable Systems - Google](https://sre.google/books/building-secure-reliable-systems/)
- [Release It! - Michael Nygard](https://pragprog.com/titles/mnee2/release-it-second-edition/)
- [Resilience Engineering - Wikipedia](https://en.wikipedia.org/wiki/Resilience_engineering)
- [Observability Engineering - O'Reilly](https://www.oreilly.com/library/view/observability-engineering/9781492076438/)

Tags: SRE, Operability, Architecture, Reliability, Engineering
