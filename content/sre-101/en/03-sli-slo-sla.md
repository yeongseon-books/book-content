---
series: sre-101
episode: 3
title: "SRE 101 (3/10): SLI, SLO, SLA"
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
  - SLI
  - SLO
  - SLA
  - Reliability
seo_description: A beginner-friendly guide to SLI, SLO, and SLA covering their definitions, the agreement process, and what makes a good objective
last_reviewed: '2026-05-14'
---

# SRE 101 (3/10): SLI, SLO, SLA

The moment a reliability conversation becomes serious, three acronyms show up: SLI, SLO, and SLA. Because they all involve numbers, teams often compress them into one vague statement like "we promise 99.9%," which is exactly where confusion starts.

What matters operationally is the separation. You need one layer that defines what you measure, another that defines the target you run the system against, and a final layer that defines what you are willing to promise outside the team.

This is the 3rd post in the SRE 101 series. Here we separate measurement, internal objective, and external agreement so later error-budget and alerting decisions have a clean contract underneath them.


![sre 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/sre-101/03/03-01-concept-at-a-glance.en.png)
*sre 101 chapter 3 flow overview*

## Questions to Keep in Mind

- Where exactly is the line between an indicator, an objective, and an external agreement?
- Why should internal targets and customer-facing promises almost never be the same document?
- What information makes an SLO operational instead of decorative?

## Why this topic matters

If you mix the three terms, every decision gets wobbly. Operations may think the team is talking about an internal goal while sales repeats the same number as a public promise.

Separating them makes ownership and consequences clearer. The indicator tells you what changed, the objective tells you when to act, and the agreement tells you what happens if you miss the promise.

> SLI is the indicator, SLO is the internal goal, and SLA is the external promise.

## Why collapsing the three layers is dangerous

When someone says "our service guarantees 99.9%," at least four blanks are hidden: 99.9% of *what*? Measured over *what period*? Who *owns* the target? What *happens* if it is missed?

SLI, SLO, and SLA divide responsibility for filling those blanks. The SLI clarifies the measurement formula. The SLO specifies the target and owner. The SLA adds remedies and exclusions for external promises. Without this separation, numbers exist but operations remain vague.

## Key Terms

| Term | Meaning | Problem if missing |
| --- | --- | --- |
| SLI | Service-level indicator — what you measure | Unclear what is being tracked |
| SLO | Service-level objective — internal target | No basis for release/stability decisions |
| SLA | Service-level agreement — external promise | Liability scope is ambiguous when violated |
| window | Evaluation period for the metric | Same number gets interpreted differently |
| threshold | Target value or allowed limit | Violation judgment becomes unstable |

## SLI / SLO / SLA comparison table

| Aspect | SLI | SLO | SLA |
| --- | --- | --- | --- |
| **Definition** | Metric measuring service level | Internal operational target | External customer promise |
| **Owner** | Platform / operations team | Product / SRE team | Legal / sales team |
| **Example** | `http_2xx / http_total` | 99.9% availability over 30 days | 10% credit if below 99.5% |
| **Consequence of violation** | Dashboard turns orange | Deploy freeze, review strengthened | Compensation paid, contract risk |

SLO is an internal standard; SLA is an external contract. Confusing the two either creates unnecessary pressure or exposes the company to legal risk.

## Error budget connection

The error budget is the failure headroom implied by the SLO. For example, if the 30-day target is 99.9% availability, 0.1% failure is tolerable:

```python
def error_budget(total_requests, target_availability):
    allowed_errors = total_requests * (1 - target_availability)
    return allowed_errors

# 1M requests over 30 days, 99.9% target
print(error_budget(1_000_000, 0.999))  # 1000 errors allowed
```

While budget remains, the team can deploy new features or run refactors. When budget is consumed, deploys halt and stability work takes priority. The detailed mechanics are covered in the next post.

## What makes a good SLO

A good SLO is not simply a high target number. It must state which SLI it tracks, over what window, and who owns it. Only then does a violation lead to action. An SLO missing any of these three elements sits in a dashboard but influences nobody.

Especially: an SLO without an owner is effectively non-existent. The number is written down but nobody reads it with accountability.

## SLO-to-downtime conversion

Abstract percentages become concrete when you express them as allowed downtime:

```python
def monthly_downtime(availability):
    total_minutes = 30 * 24 * 60  # 43,200 minutes
    downtime = (1 - availability) * total_minutes
    return downtime

print(f"99.9%:  {monthly_downtime(0.999):.1f} min")   # 43.2 min
print(f"99.95%: {monthly_downtime(0.9995):.1f} min")  # 21.6 min
print(f"99.99%: {monthly_downtime(0.9999):.1f} min")  # 4.3 min
```

99.9% availability allows 43 minutes of downtime per month. This makes it easy to judge whether the target is realistic and what investment is needed.

## Choosing good SLIs

When selecting SLIs, these criteria make the metric operationally useful:

**Reflects user experience directly.** HTTP success rate is closer to what users feel than CPU utilization.

**Simple to measure.** Metrics that require complex formulas or joining multiple sources create arguments.

**Enables threshold analysis.** When the metric degrades, you should be able to trace back which segment caused the problem.

**Leads to action.** When the metric violates the target, it should be clear what to do next.

## Writing the spec step by step

### Step 1 — Define the SLI

```python
sli = {
    "name": "http_success_ratio",
    "formula": "http_2xx / http_total",
    "source": "ingress logs",
}
```

The SLI is the starting point for measurement. Name and formula alone are not enough — the data source must also be recorded. Without it, nobody can explain why the metric value changed.

### Step 2 — Define the SLO

```python
slo = {
    "sli": sli["name"],
    "target": 0.999,
    "window_days": 30,
    "owner": "payments-team",
}
```

An SLO needs target, measurement window, and owner together. A target without an owner does not come alive as an operating standard.

### Step 3 — Define the SLA

```python
sla = {
    "slo": slo,
    "remedy": "service credit 10%",
    "exclusions": ["scheduled maintenance"],
}
```

An SLA is an external promise, so it needs remedies and exclusion clauses. Exporting an aggressive internal SLO directly as an external contract creates either an impossibly strong commitment or a meaningless document.

### Step 4 — Detect a violation

```python
def violated(success, total, target):
    return (success / total) < target
```

A good target allows immediate violation detection. If the judgment rule is vague, operational decisions revert to gut feeling.

### Step 5 — Report

```python
def report(success, total, target):
    return {
        "value": success / total,
        "violated": (success / total) < target,
    }
```

Value and violation status shown together support weekly reviews, incident retros, and customer communication.

### Step 6 — Calculate the remaining budget in the same report

```python
def budget_summary(success, total, target):
    errors = total - success
    allowed = (1 - target) * total
    remaining = allowed - errors
    return {
        "availability": success / total,
        "allowed_errors": allowed,
        "remaining_errors": remaining,
    }
```

This is where the three layers start to feel operational. The SLI value tells you what happened, the SLO target tells you whether the result is acceptable, and the remaining-error view tells the team how much room is left before release policy should tighten.

### Step 7 — Resolve metric disputes before they turn into policy disputes

When two dashboards disagree, do not start by arguing about the target. Start by checking whether both dashboards use the same traffic boundary, the same success definition, and the same time window. Many "SLO debates" are really data-source debates in disguise.

| First check | Why it matters |
| --- | --- |
| Are both teams looking at the same request population? | Edge traffic and app-only traffic often produce different availability numbers. |
| Is a redirect or client error counted as success or failure? | The formula can drift even when the chart title stays the same. |
| Is the window rolling 30 days or calendar month? | The same percentage can mean different risk depending on the window. |
| Is maintenance excluded in one report but not the other? | Agreement language often differs from internal measurement language. |

## SLI definitions by service type

SLIs differ by service. The same formula can mean entirely different things depending on what counts as success and which requests are included.

### API service

```python
sli_api = {
    "name": "api_availability",
    "formula": "http_2xx / (http_total - http_4xx)",
    "source": "ingress controller logs",
    "note": "Client errors (4xx) excluded — not a service reliability issue",
}
```

Excluding 4xx matters because a client sending malformed requests is not a service reliability problem. Making this boundary explicit in the SLI formula reduces inter-team arguments.

### Data pipeline

```python
sli_pipeline = {
    "name": "pipeline_freshness",
    "formula": "current_time - last_successful_run_time < threshold",
    "source": "Airflow metadata DB",
    "threshold": "15 minutes",
    "note": "Data older than 15 min is considered stale",
}
```

Data pipelines often cannot be measured by HTTP response. Instead, data freshness serves as the SLI. If the gap between the last successful run and now exceeds the threshold, the SLO is violated.

### Storage service

```python
sli_storage = {
    "name": "storage_durability",
    "formula": "verified_objects / total_objects",
    "source": "integrity check batch job",
    "frequency": "daily",
    "note": "Verified via daily integrity batch",
}
```

### PromQL-based SLI calculation

In production, defining SLIs in PromQL enables automated calculation and alerting:

```promql
# API availability SLI (30-day rolling window)
sum(increase(http_requests_total{status=~"2..",service="payments"}[30d]))
/
(
  sum(increase(http_requests_total{service="payments"}[30d]))
  -
  sum(increase(http_requests_total{status=~"4..",service="payments"}[30d]))
)
```

```promql
# Latency SLI: fraction of requests under 300ms
sum(increase(http_request_duration_seconds_bucket{le="0.3",service="search"}[30d]))
/
sum(increase(http_request_duration_seconds_count{service="search"}[30d]))
```

This query calculates the fraction of search requests that responded within 300ms over 30 days. When this value drops below the SLO target (e.g., 99%), the error budget is being consumed.

## SLO document template

To make an SLO operational, it needs more than a target number. Here is a production-ready template:

```yaml
# SLO Document: Payments API
service: payments-api
version: "2026-05-01"
owner: payments-team
approver: platform-lead

slis:
  - name: availability
    formula: "http_2xx / (http_total - http_4xx)"
    source: "ingress controller access logs"

  - name: latency
    formula: "requests_under_300ms / total_requests"
    source: "Prometheus histogram"

slos:
  - sli: availability
    target: 99.9%
    window: 30d (rolling)
    consequence:
      warning: "50% spent → deploy review strengthened"
      critical: "80% spent → deploy freeze"
      violated: "100% spent → full stabilization, postmortem"

  - sli: latency
    target: 99.0%
    window: 30d (rolling)
    threshold: "p99 < 300ms"
    consequence:
      warning: "p99 > 500ms → performance analysis"
      critical: "p99 > 1s → urgent response"

error_budget:
  availability:
    monthly_requests: 10_000_000
    allowed_errors: 10_000

  latency:
    monthly_requests: 10_000_000
    allowed_slow: 100_000

review:
  frequency: weekly
  participants: [sre-lead, payments-lead, product-manager]
  dashboard: "https://grafana.internal/d/payments-slo"
```

The key is not just writing a target number but also documenting consequences (what happens at each threshold) and review cadence. This structure keeps the SLO alive as an operating instrument rather than a static document.

## SLA contract essentials

An SLA is a legally binding external promise. Unlike the internally managed SLO, an SLA is co-authored with legal and sales teams.

| Item | Description | Example |
| --- | --- | --- |
| Service scope | Which service and features the SLA covers | "POST /payments endpoint of the Payments API" |
| Measurement method | How availability is calculated | "5-min success response ratio, monitoring system of record" |
| Target | Guaranteed service level | "99.5% monthly availability" |
| Exclusions | Situations excluded from the SLA | "Scheduled maintenance, customer network issues, force majeure" |
| Remedy | Compensation for violation | "10% monthly fee credit if below 99.5%" |
| Reporting | How often achievement is reported | "Monthly, visible in customer portal" |
| Dispute resolution | Procedure when measurements disagree | "Third-party monitoring benchmark agreed by both parties" |

```python
def calculate_credit(monthly_fee, availability, sla_tiers):
    """
    Calculate SLA violation credit.
    sla_tiers: [(threshold, credit_pct), ...]
    """
    for threshold, credit_pct in sorted(sla_tiers, reverse=True):
        if availability < threshold:
            return monthly_fee * credit_pct
    return 0

sla_tiers = [
    (0.995, 0.10),  # Below 99.5% → 10% credit
    (0.990, 0.25),  # Below 99.0% → 25% credit
    (0.950, 0.50),  # Below 95.0% → 50% credit
]

# This month: 99.3% availability, $10,000 monthly fee
credit = calculate_credit(10_000, 0.993, sla_tiers)
print(f"Credit owed: ${credit:,.0f}")  # $1,000
```

The SLA target must always be set *lower* than the internal SLO. If you operate internally toward 99.9% but promise externally at 99.5%, you have a buffer. Without this buffer, slightly missing the SLO immediately triggers SLA compensation.

## Common mistakes when introducing SLI/SLO

| Mistake | Why it's a problem | Mitigation |
| --- | --- | --- |
| Same SLO for all APIs | Manages services of different criticality identically | Separate critical paths from auxiliary paths with tiered targets |
| SLO created but never reviewed | Document exists but does not influence operations | Mandatory weekly SLO review meeting |
| SLA target = SLO target | Internal miss immediately triggers compensation | SLA < SLO to maintain buffer |
| No measurement window specified | Same number interpreted differently | State "30d rolling window" explicitly |
| SLI definition missing data source | Numbers not reproducible, inter-team disputes | Record the query and data source together |

## SLO review meeting practice

An SLO document that nobody reads is already dead. Keeping SLOs alive requires regular review.

**Weekly SLO review checklist:**

- [ ] Checked actual achievement of each SLI over the past 7 days?
- [ ] Checked error budget burn rate?
- [ ] If any SLO was violated, identified root cause?
- [ ] Estimated impact of next week's planned deploys on budget?
- [ ] If action items exist, assigned owner and deadline?

A review meeting takes 15–20 minutes. Walk through the dashboard together: "Are we okay?" → "If not, why?" → "What do we do?" This habit turns the SLO from document to operating tool.

## Checklist

- [ ] SLI name, formula, and data source documented.
- [ ] SLO includes target, measurement window, and owner.
- [ ] SLA specifies remedy and exclusion clauses.
- [ ] Violation can be detected automatically.
- [ ] Internal targets and external promises are not confused.

## Practice Problems

1. Your team runs a search API and a payment API. Design different SLIs for each, explaining why the formulas differ.
2. Write a complete SLO document (using the YAML template format) for a service you operate. Include consequences at 50%, 80%, and 100% budget spend.
3. Your SLA guarantees 99.5% but your internal SLO is 99.9%. Calculate the buffer in minutes per month. Then explain what happens operationally when you enter the buffer zone (SLO violated but SLA still met).

## Wrap-up and Next Steps

Next, we cover the error budget — how much failure is tolerable after setting an SLO, and how that number governs release velocity.

## Answering the Opening Questions

- **What role does each of SLI, SLO, and SLA play, and where do their boundaries lie?**
  SLI defines metrics at the measurement layer, SLO sets targets at the operational layer, and SLA establishes compensation at the contractual layer. They form three tiers: start with measurement, pass through operational targets, and finish with external promises.
- **Why should internal targets and external promises not live in the same document?**
  SLOs are operational criteria with explicit owners that let internal teams judge quickly and experiment. SLAs are contract documents specifying compensation liability to external customers. Different owners, different risks.
- **What information must a good SLO contain beyond the target number?**
  Numbers alone don't enable operational judgment. Measurement window, owner, and data source must all be present so that when the target is violated, someone knows what to look at and what action to take. These three make an SLO actionable rather than aspirational.

<!-- toc:begin -->
## In this series

- [SRE 101 (1/10): What is SRE?](./01-what-is-sre.md)
- [SRE 101 (2/10): Reliability](./02-reliability.md)
- **SLI, SLO, SLA (current)**
- Error Budget (upcoming)
- Monitoring (upcoming)
- Incident Response (upcoming)
- Postmortem (upcoming)
- Reducing Toil (upcoming)
- Capacity Planning (upcoming)
- Building Operable Systems (upcoming)

<!-- toc:end -->

## References

- [Service Level Objectives - Google SRE Book](https://sre.google/sre-book/service-level-objectives/)
- [Implementing SLOs - Google SRE Workbook](https://sre.google/workbook/implementing-slos/)
- [SLI vs SLO vs SLA - Atlassian](https://www.atlassian.com/incident-management/kpis/sla-vs-slo-vs-sli)
- [SLA, SLO, SLI - DigitalOcean](https://www.digitalocean.com/community/tutorials/what-is-sla-slo-sli)

Tags: SRE, SLI, SLO, SLA, Reliability
