---
series: observability-101
episode: 7
title: "Observability 101 (7/10): Alerts and On-Call"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Observability
  - Alerting
  - SRE
  - OnCall
  - Monitoring
seo_description: What makes an alert worth a 3am page, how to avoid alert fatigue, and the first steps of running on-call sustainably.
last_reviewed: '2026-05-15'
---

# Observability 101 (7/10): Alerts and On-Call

More alerts do not make a system safer by default. Once the team stops trusting the pager, even the alert that matters most arrives already discounted.

That is why alerting design is partly a technical problem and partly a human one. It spends sleep, focus, and trust, so it must be tied to user impact and clear action.

This is post 7 in the Observability 101 series.


![observability 101 chapter 7 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/observability-101/07/07-01-concept-at-a-glance.en.png)
*observability 101 chapter 7 flow overview*
> Alerts and On-Call is about the boundary decision, not the tool choice.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Alerts and On-Call?
- Which signal should the example or diagram make visible for Alerts and On-Call?
- What failure should be prevented first when Alerts and On-Call reaches a real system?

## Questions this article answers

- What makes an alert worth waking someone up at 3 a.m.?
- Why does alert fatigue happen, and how do you reduce it?
- What is the difference between symptom alerts and cause alerts?
- Why does severity separation matter?
- What role should a runbook play in on-call operations?

## Why It Matters

Too many alerts *bury* the real signal. On-call *buys sleep* and *spends willpower*. Design is cost.

> *Alerts have a *wake-up cost*. If you do not know it, you go *bankrupt*.*

Observability is the ability to understand a system's internal state from external signals. In a distributed system, you cannot instrument every line of code. You rely on *metrics* (what happened), *logs* (why it happened), and *traces* (where it happened).

## Key Terms

- **Alert rule**: a condition plus a *duration*.
- **Severity**: *page* vs *ticket*.
- **Routing**: who receives it.
- **Silence**: temporary *suppression*.
- **Runbook**: an *action manual* for the alert.

## Before/After

**Before**: 50 alerts/day, all ignored. The real outage *gets missed*.

**After**: 3 alerts/week, *all actionable*.

## Hands-on: Alerts in 5 Steps

### Step 1 — Prometheus alert rule

```yaml
groups:
  - name: api
    rules:
      - alert: HighErrorRate
        expr: sum(rate(http_requests_total{status=~"5.."}[5m]))
              / sum(rate(http_requests_total[5m])) > 0.05
        for: 10m
        labels: { severity: page }
        annotations:
          summary: "5xx > 5% for 10m"
          runbook: "https://wiki/runbook/api-error"
```

### Step 2 — `for` clause to prevent *flap*

```yaml
for: 10m   # too short and noise explodes
```

### Step 3 — Split severity

```yaml
labels:
  severity: page    # wakes you up
  # severity: ticket # business hours
```

### Step 4 — Alertmanager routing

```yaml
route:
  receiver: default
  routes:
    - match: { severity: page }
      receiver: pagerduty
    - match: { severity: ticket }
      receiver: slack-ops
```

### Step 5 — Runbook link

```text
Every alert MUST have a runbook URL.
The runbook covers: meaning, first 3 actions, escalation, related dashboards.
```

## How to Check Alert Quality

Before adding a new page-level alert, replay it against recent data and verify that a human should actually receive it.

```text
1) Replay the rule against the last 30 days.
2) Confirm that the `for` clause filters short spikes.
3) Verify every `severity=page` rule has a runbook and owner.
4) Trigger a test event and confirm routing to PagerDuty or chat.
```

```text
Expected output:
- Page-level alerts stay rare enough that responders still trust them.
- Ticket-level alerts land in business-hours channels only.
- Every alert message includes summary, owner, and runbook context.
```

## What to Notice in This Code

- `for: 10m` enforces a *duration condition*.
- The `severity` label decides *behavior*.
- An alert without a *runbook* is *half-built*.

## Five Common Mistakes

1. **Every alert is a *page*.** Nights become *hell*.
2. **Alerting only on *cause*.** Disconnected from *user impact*.
3. **No `for` clause.** *Flapping* explodes noise.
4. **No *runbook*.** The receiver *freezes*.
5. **No owner.** Everyone's alert = *no one's alert*.

## How This Shows Up in Production

Most teams put *symptom-based alerts (SLO breaches)* first and *cause-based alerts (CPU 95%)* as backup. PagerDuty / Opsgenie / Grafana OnCall are common.

## How a Senior Engineer Thinks

- *Delete alerts that are not *actionable*.*
- *Symptom > cause. SLO is the standard.*
- *The cost of a page is *sleep*.*
- *On-call is *labor* and deserves compensation.*
- *Alerts without a runbook are *retired immediately*.*

## Checklist

- [ ] Each alert has a *runbook link*.
- [ ] Severity splits into *page/ticket*.
- [ ] `for` is set.
- [ ] On-call *rotation* is in place.

## Practice Problems

1. Write one alert for an SLO breach.
2. Identify one *symptom* alert and one *cause* alert.
3. Write a one-page runbook.

## Wrap-up and Next Steps

Good alerts *protect sleep*. Next: *SLI and SLO basics*.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Alerts and On-Call?**
  - The article treats Alerts and On-Call as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Alerts and On-Call?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Alerts and On-Call reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Observability 101 (1/10): What Is Observability?](./01-what-is-observability.md)
- [Observability 101 (2/10): Metrics, Logs, and Traces](./02-metric-log-trace.md)
- [Observability 101 (3/10): Collecting and Visualizing Metrics](./03-metric-collection.md)
- [Observability 101 (4/10): Structured Logging](./04-structured-logging.md)
- [Observability 101 (5/10): Distributed Tracing Basics](./05-distributed-tracing.md)
- [Observability 101 (6/10): Dashboard Design](./06-dashboard-design.md)
- **Alerts and On-Call (current)**
- SLI and SLO Basics (upcoming)
- Cost and Cardinality (upcoming)
- A Production-Ready Observability Stack (upcoming)

<!-- toc:end -->

## References

- [Google SRE — Alerting](https://sre.google/sre-book/practical-alerting/)
- [Prometheus alerting rules](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/)
- [Alertmanager docs](https://prometheus.io/docs/alerting/latest/alertmanager/)
- [On-call principles](https://increment.com/on-call/when-the-pager-goes-off/)

Tags: Observability, Alerting, SRE, OnCall, Monitoring
