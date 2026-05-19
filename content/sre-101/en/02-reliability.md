---
series: sre-101
episode: 2
title: Reliability
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
  - Reliability
  - Availability
  - Latency
  - Quality
seo_description: A beginner-friendly guide to reliability covering availability, latency, correctness, durability, and the design principles behind each
last_reviewed: '2026-05-14'
---

# Reliability

Many teams say a service feels stable until an outage or a slow release proves otherwise. That kind of language works in hallway conversation, but it does not help product, platform, and support teams make the same decision from the same evidence.

Reliability gets clearer when you stop treating it like mood and start treating it like a bundle of measurable promises. A service can be up and still feel broken if it is too slow, returns wrong results, or loses data.

This is post 2 in the SRE 101 series. Here we break reliability into measurable dimensions so later topics like SLOs, error budgets, and monitoring rest on something more concrete than “it seems okay.”

## Questions this chapter answers

- What does it mean to describe reliability as a measurable property instead of a general sense of stability?
- Why are availability and latency related but not interchangeable?
- When do correctness and durability matter more than raw uptime?
- Why do teams rely on p95 and p99 more than on average latency?
- How should different systems choose different reliability dimensions?

## Why this topic matters

Without numbers, every conversation and decision becomes subjective. One team thinks the service is fine, another thinks it is risky, and neither side can show where the disagreement comes from.

Once the dimensions are explicit, reliability becomes easier to discuss as product quality. A payment flow, search API, and analytics pipeline can all be reliable, but they rarely need the same emphasis.

> Reliability is the work of proving a customer promise with numbers.

## Concept at a glance

![Concept at a glance](https://yeongseon-books.github.io/book-public-assets/assets/sre-101/02/02-01-concept-at-a-glance.en.png)

*Reliability only becomes visible when availability, latency, correctness, and durability are read together.*
## Key Terms

- **availability**: the *fraction of time* the system works.
- **latency**: the *response time*.
- **correctness**: the *accuracy* of results.
- **durability**: how well data is *retained*.
- **MTTR**: *mean time to recover*.

## Before/After

**Before**: vague phrases like "it *works fine*".

**After**: numbers like "*99.9%*, *p95 200ms*".

## Hands-on: Measuring Four Dimensions

### Step 1 — Availability

```python
def availability(uptime_s, total_s):
    return uptime_s / total_s
```

### Step 2 — Latency p95

```python
def p95(samples):
    s = sorted(samples)
    return s[int(0.95 * len(s)) - 1]
```

### Step 3 — Correctness

```python
def correctness(correct, total):
    return correct / total
```

### Step 4 — Durability

```python
def lost_ratio(lost, stored):
    return lost / stored
```

### Step 5 — Combined SLOs

```python
slos = {
    "availability": 0.999,
    "p95_ms": 200,
    "correctness": 0.9999,
    "lost_ratio": 1e-9,
}
```

## What to Notice in This Code

- Each *dimension* has a different *indicator*.
- *Quantiles* like *p95* are more useful than averages.
- *Correctness* and *durability* matter most in *data systems*.

## Five Common Mistakes

1. **Looking only at *average latency*.**
2. **Assuming *availability* is the *whole* story.**
3. **Ignoring *correctness*.**
4. **Treating *durability* as just *backups*.**
5. **Confusing *server metrics* with *customer experience*.**

## How This Shows Up in Production

A *payment service* prioritizes *correctness*. A *streaming service* prioritizes *latency*.

## How a Senior Engineer Thinks

- *Reliability* needs *numbers* and *definitions*.
- *p95/p99* are closer to the *customer* than averages.
- *Trade-offs* must be made *explicit*.
- *MTTR* is a *learning* outcome.
- *Correctness* is part of the *feature*.

## Checklist

- [ ] Four-dimension *SLOs* defined.
- [ ] *p95/p99* monitored.
- [ ] *Correctness* verified automatically.
- [ ] *Durability* policy documented.

## Practice Problems

1. Define *availability* in one line.
2. Define *p95 latency* in one line.
3. Define *durability* in one line.

## Wrap-up and Next Steps

Next, we cover the difference between *SLI*, *SLO*, and *SLA*.

<!-- toc:begin -->
- [What is SRE?](./01-what-is-sre.md)
- **Reliability (current)**
- SLI, SLO, SLA (upcoming)
- Error Budget (upcoming)
- Monitoring (upcoming)
- Incident Response (upcoming)
- Postmortem (upcoming)
- Reducing Toil (upcoming)
- Capacity Planning (upcoming)
- Building Operable Systems (upcoming)
<!-- toc:end -->

## References

- [Reliability - Google SRE Book](https://sre.google/sre-book/embracing-risk/)
- [Tail at Scale](https://research.google/pubs/pub40801/)
- [The Four Golden Signals](https://sre.google/sre-book/monitoring-distributed-systems/)
- [Availability vs Durability - AWS](https://aws.amazon.com/s3/storage-classes/)

Tags: SRE, Reliability, Availability, Latency, Quality
