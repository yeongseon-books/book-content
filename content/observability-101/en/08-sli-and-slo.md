---
series: observability-101
episode: 8
title: "Observability 101 (8/10): SLI and SLO Basics"
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
  - SLO
  - SLI
  - SRE
  - Reliability
seo_description: Define SLIs, set SLO targets, and use the error budget to make reliability a number instead of a feeling.
last_reviewed: '2026-05-15'
---

# Observability 101 (8/10): SLI and SLO Basics

Reliability conversations often go in circles because each side is speaking from instinct. One team says the service is fine, another says it is already risky, and nobody has a shared threshold for when feature work should slow down.

SLIs and SLOs solve that by turning service quality into a number, a target, and a budget the team can spend or protect.

This is the 8th post in the Observability 101 series.


![observability 101 chapter 8 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/observability-101/08/08-01-concept-at-a-glance.en.png)
*observability 101 chapter 8 flow overview*
> SLI and SLO Basics is about the boundary decision, not the tool choice.

## Questions to Keep in Mind

- What boundary should you inspect first when applying SLI and SLO Basics?
- Which signal should the example or diagram make visible for SLI and SLO Basics?
- What failure should be prevented first when SLI and SLO Basics reaches a real system?

## Questions this article answers

- What does an SLI measure, and how should you measure it?
- What kind of promise does an SLO create?
- Why does the error budget become the balance point between feature delivery and reliability work?
- What kinds of conditions do burn-rate alerts catch early?
- Why should you separate internal metrics from user-facing metrics?

## Why It Matters

"Stable" is *subjective*. 99.9% is *agreement*. With SLOs, the *features vs reliability* fight is settled *with data*.

> *An SLO is *the shared language between engineers and the business*.*

Observability is the ability to understand a system's internal state from external signals. In a distributed system, you cannot instrument every line of code. You rely on *metrics* (what happened), *logs* (why it happened), and *traces* (where it happened).

## Key Terms

- **SLI**: a *measurable ratio* (e.g., success rate).
- **SLO**: a *target value* (e.g., 99.9%).
- **SLA**: a *contract*, breach has *penalty*.
- **Error budget**: the allowed *amount of failure*.
- **Burn rate**: how *fast* the budget is consumed.

## Before/After

**Before**: "It's slow" vs "it's fine" — a *word fight*.

**After**: "This month availability is *99.87%*, below the *99.9%* SLO" — *debate over*.

## Hands-on: SLOs in 5 Steps

### Step 1 — Define an SLI

```promql
# Availability SLI = good / total
sli_good = sum(rate(http_requests_total{status!~"5.."}[5m]))
sli_total = sum(rate(http_requests_total[5m]))
sli = sli_good / sli_total
```

### Step 2 — Pick an SLO target

```text
SLO: 99.9% availability over 30 days
That allows 30 * 24 * 60 * 0.001 = 43.2 minutes/month
```

### Step 3 — Error budget

```promql
1 - (sli_good / sli_total)         # current failure rate
# remaining 30-day budget = 0.001 * total - errors
```

### Step 4 — Burn-rate alert (multi-window)

```yaml
- alert: FastBurn
  expr: error_rate_5m > 14.4 * 0.001
        and error_rate_1h > 14.4 * 0.001
  for: 2m
  labels: { severity: page }
```

### Step 5 — Monthly SLO report

```text
- Availability: 99.92% (target 99.9% PASS)
- Latency: p95 320ms (target <= 500ms PASS)
- Budget burned: 38%
```

## How to Operate an Error Budget

An SLO matters only if it changes release behavior and incident response.

```text
30-day SLO target: 99.9%
allowed downtime: 43.2m
this month burned: 31.4m (72.7%)
current burn rate: 2.1x
decision: keep routine deploys, hold risky changes
```

```text
Expected output:
- The team shares one number for the target, one for remaining budget, and one for burn rate.
- Burn-rate alerts catch both fast incidents and slow degradation.
- Monthly reviews use budget consumption to decide whether feature velocity should slow down.
```

### Error Budget Policy

An error budget is just a number. To operationalize it, you need a policy that maps consumption levels to concrete actions.

**Policy 1: Budget consumed ≤ 70% (green zone)**

- Maintain normal deploy velocity.
- Continue new feature development.
- Report budget consumption at the weekly review.

**Policy 2: Budget consumed 70–90% (yellow zone)**

- Hold high-risk deploys (e.g., database schema migrations).
- Prioritize stability improvements for existing features.
- Analyze root causes of recent failures at weekly review.

**Policy 3: Budget consumed > 90% (red zone)**

- Freeze all new-feature deploys.
- Form a stabilization task force and focus exclusively on reliability.
- Escalate to leadership.
- Maintain the policy until budget consumption drops below 70%.

This policy turns numbers into actions. When the rule "no feature deploys if budget is exhausted" is explicit, both engineering and business teams speak from the same reference point.

### Distinguishing SLA from SLO from SLI

In practice, teams often conflate SLI, SLO, and SLA. The three serve clearly different roles.

**SLI (Service Level Indicator)**
A measurable metric. It must be expressible as a precise number—success rate, latency, throughput. Example: `availability = (successful requests / total requests) * 100%`.

**SLO (Service Level Objective)**
An agreed-upon target the team commits to. Example: `maintain availability ≥ 99.9%`. Missing the target carries no legal penalty, but it is the internal operational standard.

**SLA (Service Level Agreement)**
A contract with customers. Example: `refund 10% of service fees if availability falls below 99.9%`. Because breach triggers financial or legal liability, SLAs are set more conservatively than SLOs.

A common pattern: if your SLO is 99.9%, set the SLA at 99.5%. This buffer means you can miss your internal target without immediately breaking customer commitments.

### Multi-SLO Priority

When a service has multiple SLOs, you must define priority explicitly. Treating all SLOs with equal weight leaves the team unable to decide which breach to fix first.

```python
slo_priority = {
    "availability": {
        "target": 0.999,
        "weight": 1.0,  # highest priority
        "action": "freeze all deploys"
    },
    "latency_p95": {
        "target": 500,  # ms
        "weight": 0.8,
        "action": "prioritize performance tuning"
    },
    "latency_p99": {
        "target": 1000,  # ms
        "weight": 0.6,
        "action": "optimize long-tail latency"
    }
}

def check_slo_breach(metrics, slo_priority):
    breached = []
    for name, config in sorted(
        slo_priority.items(),
        key=lambda x: x[1]["weight"],
        reverse=True
    ):
        if metrics[name] < config["target"]:
            breached.append((name, config))

    if breached:
        top = breached[0]
        print(f"Critical SLO breach: {top[0]}")
        print(f"Action required: {top[1]['action']}")
```

With explicit priority, when multiple SLOs breach simultaneously, the team knows which one to restore first.

## SLI Calculation Code

When the indicator definition lives only in a document, interpretation drifts during operations. Expressing calculation logic in code keeps the team aligned.

```python
from dataclasses import dataclass

@dataclass
class SLIResult:
    good: int
    total: int

    @property
    def value(self) -> float:
        return 0.0 if self.total == 0 else self.good / self.total

def availability_sli(status_codes: list[int]) -> SLIResult:
    total = len(status_codes)
    good = sum(1 for code in status_codes if 200 <= code < 500)
    return SLIResult(good=good, total=total)

samples = [200, 200, 201, 502, 503, 200, 429, 200]
result = availability_sli(samples)
print(f"SLI={result.value:.4f} ({result.good}/{result.total})")
```

What counts as "good" depends on service context. An authentication service might treat 401 as a normal response, while a payment API might classify certain 4xx codes as failures. The key is to document the criteria and maintain a change log.

## Error Budget Burn Formula

The two most-used formulas in operations:

```text
allowed_error_rate = 1 - slo_target
burn_rate = actual_error_rate / allowed_error_rate
```

For example, with a 99.9% SLO the allowed error rate is 0.1% (0.001). If the actual error rate is 0.5% (0.005), burn rate is 5.0—meaning you are consuming the budget five times faster than planned. This lets you interpret incident severity as a relative speed rather than an absolute number.

## Multi-Window Alert Template

Using both a short window and a long window catches both sudden spikes and gradual degradation.

```yaml
groups:
  - name: slo-burn
    rules:
      - alert: SLOFastBurn
        expr: (error_rate_5m > 14.4 * 0.001) and (error_rate_1h > 14.4 * 0.001)
        for: 2m
        labels:
          severity: page
        annotations:
          summary: "SLO fast burn detected"

      - alert: SLOSlowBurn
        expr: (error_rate_30m > 6 * 0.001) and (error_rate_6h > 6 * 0.001)
        for: 15m
        labels:
          severity: ticket
        annotations:
          summary: "SLO slow burn detected"
```

Fast burn triggers immediate response; slow burn triggers planned stabilization. Without this separation, teams either over-respond to everything or consistently respond too late.

### SLO Dashboard — Grafana JSON Example

A dashboard panel configuration that shows SLO status at a glance:

```json
{
  "title": "SLO Status — checkout-service",
  "type": "stat",
  "datasource": "Prometheus",
  "targets": [
    {
      "expr": "1 - (sum(rate(http_requests_total{service=\"checkout\", code=~\"5..\"}[30d])) / sum(rate(http_requests_total{service=\"checkout\"}[30d])))",
      "legendFormat": "Availability (30d)"
    }
  ],
  "fieldConfig": {
    "defaults": {
      "thresholds": {
        "steps": [
          { "value": 0, "color": "red" },
          { "value": 0.995, "color": "yellow" },
          { "value": 0.999, "color": "green" }
        ]
      },
      "unit": "percentunit",
      "decimals": 4
    }
  }
}
```

This panel displays 30-day rolling-window availability as a percentage. The color changes based on threshold, so current SLO status is visible at a glance.

Pair it with an error-budget-remaining gauge:

```json
{
  "title": "Error Budget Remaining",
  "type": "gauge",
  "datasource": "Prometheus",
  "targets": [
    {
      "expr": "1 - (sum(increase(http_requests_total{service=\"checkout\", code=~\"5..\"}[30d])) / (sum(increase(http_requests_total{service=\"checkout\"}[30d])) * 0.001))",
      "legendFormat": "Budget Remaining"
    }
  ],
  "fieldConfig": {
    "defaults": {
      "min": 0,
      "max": 1,
      "thresholds": {
        "steps": [
          { "value": 0, "color": "red" },
          { "value": 0.25, "color": "orange" },
          { "value": 0.5, "color": "green" }
        ]
      },
      "unit": "percentunit"
    }
  }
}
```

When budget drops below 25% the gauge turns orange; at 0% it turns red. At that point, freeze feature deploys and focus on stabilization.

### Error Budget Scenario Analysis

Consider a service handling 10 million monthly requests with a 99.9% SLO:

| Scenario | Monthly Allowed Failures | Single-Incident Consumption | Remaining Budget | Action |
|---------|--------------------------|---------------------------|-----------------|--------|
| Normal operation | 10,000 | 0 | 100% | Allow feature deploys |
| 5-min full outage (100 RPS) | 10,000 | 30,000 | -200% | Immediate freeze + RCA |
| 1-hour partial outage (10% errors) | 10,000 | 3,600 | 64% | Watch closely |
| Day-long intermittent (0.5% errors) | 10,000 | 4,320 | 56.8% | Begin root-cause analysis |
| Week-long slow degradation (0.1% errors) | 10,000 | 6,048 | 39.5% | Prioritize in next sprint |

The key insight: a brief total outage is dramatic, but a day-long 0.5% error rate consumes 43% of the entire budget. Slow burns are often more expensive than fast incidents.

### SLO Rollout Roadmap

When introducing SLOs to an organization, take a phased approach. Applying them to all services at once creates measurement burden and political resistance.

**Phase 1 — Build measurement foundation (2–4 weeks)**

```yaml
actions:
  - Select 3 critical services
  - Build RED metrics collection pipeline
  - Measure actual performance baseline (2 weeks)
  - Write SLI definition doc (1 page per service)
deliverables:
  - SLI definition document
  - Prometheus recording rules
  - Grafana baseline dashboard
```

**Phase 2 — Set SLOs and observe (4–6 weeks)**

```yaml
actions:
  - Set SLO targets based on baseline (realistic levels)
  - Automate error budget calculation
  - Configure burn-rate alerts (silent mode)
  - Start weekly SLO review meetings
deliverables:
  - SLO document (targets + rationale)
  - Burn-rate alert rules (silent observation)
  - Weekly review template
```

**Phase 3 — Operational integration (4–8 weeks)**

```yaml
actions:
  - Connect alerts to actual on-call rotation
  - Formalize error budget policy (freeze criteria, unfreeze criteria)
  - Reflect SLO status in sprint planning
  - Add SLO to leadership reports
deliverables:
  - Error budget policy document
  - On-call runbook SLO section
  - Monthly reliability report
```

**Phase 4 — Expansion and maturity (ongoing)**

```yaml
actions:
  - Expand to remaining services (3-5 per quarter)
  - Introduce SLO-based capacity planning
  - Link internal SLAs to SLOs
  - Automate budget freeze/unfreeze pipeline
deliverables:
  - SLO status integrated into service catalog
  - Automated freeze/unfreeze workflow
```

At each phase, the most important outcome is the team building the habit of using SLOs as a decision-making tool. Creating numbers matters less than acting on them.

## What to Notice in This Code

- An *SLI* is always a *ratio*.
- *Burn rate* uses a *short window AND a long window*.
- If the budget *remains*, ship faster; if low, *freeze*.

## Five Common Mistakes

1. **Setting SLO to *100%*.** *Unreachable*.
2. **Using an *internal metric* as SLI.** Disconnected from user experience.
3. **Only thresholds, no *burn rate*.** Slow burns *go unnoticed*.
4. **Not using budget for *feature decisions*.** SLO becomes *decoration*.
5. **Multiple SLOs *breaking at once*.** Priority is *unclear*.

## How This Shows Up in Production

Most companies start with *availability + latency* SLOs and use them as the *criterion* for product decisions like deploys and feature additions.

## How a Senior Engineer Thinks

- *100% is *impossible*. 99.9% is a *choice*.*
- *SLI is *user-facing*.*
- *Budget is *budget*. When spent, you *stop*.*
- *Burn rate is *early warning*.*
- *Without an SLO, there is no *priority*.*

## Checklist

- [ ] You have *defined* one SLI.
- [ ] You have *agreed* on one SLO.
- [ ] You can *compute* the error budget.
- [ ] One burn-rate alert exists.

## Practice Problems

1. Write *Availability SLI* for one service in PromQL.
2. Compute the *monthly budget* (minutes) for SLO 99.9%.
3. Write a fast and slow *burn-rate* alert pair.

## Wrap-up and Next Steps

SLOs are a *shared language*. Next: *cost and cardinality*.

## Answering the Opening Questions

- **What does a service level indicator measure and how?**
  - An SLI is user experience quantified. Availability is successful response ratio; latency is p99 response time; correctness is correct result ratio. As shown in the Prometheus recording rule, raw metrics must be aggregated into ratios to become meaningful indicators.
- **What promise does a service level objective create?**
  - An SLO is a measurable internal promise like "availability ≥ 99.9% over a 30-day rolling window." This promise converts to a concrete error budget number, enabling data-driven decisions between feature shipping and stabilization.
- **Why does error budget become the balance point between feature development and stabilization?**
  - As the scenario analysis showed, a 99.9% SLO on 10M monthly requests creates an allowance of 10,000 failures. Deploy while budget remains; freeze when exhausted. Numbers—not gut feeling—make the decision, reducing conflict between dev and ops teams.
<!-- toc:begin -->
## In this series

- [Observability 101 (1/10): What Is Observability?](./01-what-is-observability.md)
- [Observability 101 (2/10): Metrics, Logs, and Traces](./02-metric-log-trace.md)
- [Observability 101 (3/10): Collecting and Visualizing Metrics](./03-metric-collection.md)
- [Observability 101 (4/10): Structured Logging](./04-structured-logging.md)
- [Observability 101 (5/10): Distributed Tracing Basics](./05-distributed-tracing.md)
- [Observability 101 (6/10): Dashboard Design](./06-dashboard-design.md)
- [Observability 101 (7/10): Alerts and On-Call](./07-alert-and-oncall.md)
- **SLI and SLO Basics (current)**
- Cost and Cardinality (upcoming)
- A Production-Ready Observability Stack (upcoming)

<!-- toc:end -->

## References

- [Google SRE — SLO chapter](https://sre.google/sre-book/service-level-objectives/)
- [The SRE Workbook — Implementing SLOs](https://sre.google/workbook/implementing-slos/)
- [Multi-window burn rate](https://sre.google/workbook/alerting-on-slos/)
- [Sloth — SLO generator](https://sloth.dev/)
- [Google Cloud — Service monitoring SLO overview](https://cloud.google.com/stackdriver/docs/solutions/slo-monitoring)

Tags: Observability, SLO, SLI, SRE, Reliability
