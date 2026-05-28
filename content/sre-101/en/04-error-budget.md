---
series: sre-101
episode: 4
title: "SRE 101 (4/10): Error Budget"
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
  - ErrorBudget
  - Reliability
  - Release
  - Risk
seo_description: A beginner-friendly guide to error budgets covering the definition, calculation, burn-rate alerting, release decisions, and operational policy
last_reviewed: '2026-05-14'
---

# SRE 101 (4/10): Error Budget

As soon as a team writes down an SLO, the next practical question shows up: how much failure are we willing to tolerate while we keep shipping changes? Without a clear answer, every incident becomes a fresh argument between “move faster” and “slow everything down.”

The error budget is useful because it turns that argument into policy. It gives the team a shared number for how much reliability risk remains, and that number should change release behavior before emotions do.

This is the 4th post in the SRE 101 series. Here we connect SLO math to release policy, burn-rate alerting, and the day-to-day trade-off between stability work and product change.


![sre 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/sre-101/04/04-01-concept-at-a-glance.en.png)
*sre 101 chapter 4 flow overview*

## Questions to Keep in Mind

- Why does an error budget become the common language between speed and stability?
- How do you calculate the allowed failure from an SLO target?
- Why do total budget spend and burn rate answer different operating questions?

## Why this topic matters

Speed and stability are not enemies, but they do need a shared decision rule. Otherwise every outage triggers a different reaction depending on who is loudest in the room.

With a budget, the discussion becomes more precise. If the service still has room, the team can take measured risk. If the budget is burning too fast, stability work moves to the front of the queue.

> An error budget is the allowed distance between the reliability goal and actual behavior.

## Key Terms

- **error budget**: the *allowed amount of failure*.
- **burn rate**: the *speed* of consumption.
- **freeze**: a *release halt*.
- **window**: the *measurement period*.
- **policy**: the *action* taken when budget is spent.

## Before/After

**Before**: an outage triggers *blame*.

**After**: as long as the *budget holds*, you *take risks*; when it is *spent*, you *freeze*.

## Hands-on: Operating the Budget

### Step 1 — Compute the budget

```python
def budget(target, total):
    return (1 - target) * total
```

### Step 2 — Spend ratio

```python
def spent(errors, allowed):
    return errors / allowed
```

### Step 3 — Burn rate

```python
def burn_rate(errors_in_h, allowed_per_h):
    return errors_in_h / allowed_per_h
```

### Step 4 — Policy branch

```python
def policy(spent_ratio):
    if spent_ratio > 1.0:
        return "freeze"
    if spent_ratio > 0.5:
        return "review"
    return "ship"
```

### Step 5 — Alert

```python
def alert(burn):
    return burn > 14.4  # 14.4x: fast burn
```

## What to Notice in This Code

- The *budget* is *quantifiable*.
- *Burn rate* is the *early-warning* signal.
- A *policy* turns the budget into *behavior*.

## Five Common Mistakes

1. **Keeping the *budget* only as a *document*.**
2. **Ignoring *burn rate*.**
3. **Having *no freeze* policy.**
4. **Running *SLO* and *budget* in *separate* tools.**
5. **Using the *budget* as a *punishment* tool.**

## How This Shows Up in Production

If the *budget* has room, you *experiment*. Once it is *spent*, you *focus on stability*.

## How a Senior Engineer Thinks

- The *budget* is the *language* of the conversation.
- *Burn rate* tells you about *now*.
- A *freeze* is a *reset*, not a *punishment*.
- The *policy* is *negotiated* with the team.
- The *budget* is part of the *product*.

## Checklist

- [ ] *Budget* computed.
- [ ] *Burn-rate* alert.
- [ ] *Freeze* policy.
- [ ] Named *owner*.

## Practice Problems

1. Define *error budget* in one line.
2. Define *burn rate* in one line.
3. Define *freeze* in one line.

## Wrap-up and Next Steps

Next, we cover the *fundamentals of monitoring*.

## Answering the Opening Questions

- **Why does error budget become a shared language between velocity and stability?**
  Error budget converts the abstract tension between "ship faster" and "don't break things" into a concrete number both sides can reference. When budget remains, teams can ship aggressively; when it's depleted, stability work takes priority—same metric, same decision framework.
- **After setting an SLO, how do you calculate the allowable failure range?**
  If your SLO is 99.9% availability over 30 days, the error budget is 0.1% × 30 days = ~43 minutes of allowed downtime. Dividing budget into time periods shows spending rate and lets you compare planned deployments against remaining headroom.
- **Why do cumulative burn and burn rate answer different questions?**
  Cumulative burn shows total budget consumed so far—useful for monthly reviews. Burn rate shows how fast you're consuming right now—useful for alerting. A high burn rate with plenty of remaining budget triggers a different response than a low burn rate near exhaustion.

<!-- toc:begin -->
## In this series

- [SRE 101 (1/10): What is SRE?](./01-what-is-sre.md)
- [SRE 101 (2/10): Reliability](./02-reliability.md)
- [SRE 101 (3/10): SLI, SLO, SLA](./03-sli-slo-sla.md)
- **Error Budget (current)**
- Monitoring (upcoming)
- Incident Response (upcoming)
- Postmortem (upcoming)
- Reducing Toil (upcoming)
- Capacity Planning (upcoming)
- Building Operable Systems (upcoming)

<!-- toc:end -->

## References

- [Embracing Risk - Google SRE Book](https://sre.google/sre-book/embracing-risk/)
- [Alerting on SLOs - Google SRE Workbook](https://sre.google/workbook/alerting-on-slos/)
- [Error Budgets - Atlassian](https://www.atlassian.com/incident-management/kpis/error-budget)
- [Error Budget Policy - Google](https://sre.google/workbook/error-budget-policy/)

Tags: SRE, ErrorBudget, Reliability, Release, Risk
