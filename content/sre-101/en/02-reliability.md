---
series: sre-101
episode: 2
title: "SRE 101 (2/10): Reliability"
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

# SRE 101 (2/10): Reliability

Many teams say a service feels stable until an outage or a slow release proves otherwise. That kind of language works in hallway conversation, but it does not help product, platform, and support teams make the same decision from the same evidence.

Reliability gets clearer when you stop treating it like mood and start treating it like a bundle of measurable promises. A service can be up and still feel broken if it is too slow, returns wrong results, or loses data.

This is the 2nd post in the SRE 101 series. Here we break reliability into measurable dimensions so later topics like SLOs, error budgets, and monitoring rest on something more concrete than "it seems okay."


![sre 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/sre-101/02/02-01-concept-at-a-glance.en.png)
*sre 101 chapter 2 flow overview*

## Questions to Keep in Mind

- What does it mean to describe reliability as a measurable property instead of a general sense of stability?
- Why are availability and latency related but not interchangeable?
- When do correctness and durability matter more than raw uptime?

## Why this topic matters

Without numbers, every conversation and decision becomes subjective. One team thinks the service is fine, another thinks it is risky, and neither side can show where the disagreement comes from.

Each service also weights dimensions differently. A payment system cares most about correctness and durability; a search service is far more sensitive to latency. Treating reliability as a single score hides these differences.

> Reliability is the work of proving a customer promise with numbers.

## Why reliability needs multiple dimensions

Looking at availability alone can make a service appear healthy. But if responses take 10 seconds, results are wrong, or stored data disappears, users are already experiencing failure. Reliability is closer to a bundle of indicators that catch different failure modes than a single number.

This distinction matters in practice. A payment API that maintains 99.99% availability but miscalculates amounts has low reliability. Conversely, a recommendation engine that returns slightly imprecise results may be fine if it responds quickly. Which dimension to prioritize depends on the business meaning of the service.

## What happens without numbers

When reliability is not defined numerically, meetings drift into abstraction. "It feels slow," "less stable than before," "user complaints are up slightly" — these point in a direction but cannot anchor design or investment decisions.

With per-dimension numbers, judgment speeds up. Is the problem latency, error rate, or data loss risk? Strong teams treat reliability as a decomposable quality attribute, not a feeling.

## Key Terms

| Term | Meaning | What to watch in production |
| --- | --- | --- |
| availability | Fraction of time the service was usable | Whether the service could accept requests |
| latency | Time to process a request | Reveals slow user experiences |
| correctness | Degree to which results match expectations | Catches systems that are fast but wrong |
| durability | Degree to which stored data is retained | Reveals data-loss risk |
| MTTR | Mean time to recover after failure | Shows recovery capability |

## Reliability dimensions and business impact

Each dimension, when violated, affects users and the business differently:

| Dimension | Problem scenario | User perception | Business impact |
| --- | --- | --- | --- |
| **Availability** | Service unreachable | Immediate frustration, seeks alternatives | Revenue loss, trust decline |
| **Latency** | Slow response (p95 > 1s) | Annoyance, considers leaving | Conversion drop, bounce rate up |
| **Correctness** | Wrong result (payment amount error) | Trust shattered, demands refund | Legal disputes, compensation costs |
| **Durability** | Data loss (order records gone) | Critical distrust, account closure | Unrecoverable, regulatory issues |

This table helps decide which dimension deserves the tightest SLO for each service.

## Choosing good SLIs

To measure reliability you first need good SLIs (Service Level Indicators). A good SLI meets these criteria:

**Connects directly to user experience.** CPU utilization or memory usage show server state but are distant from what users actually feel. HTTP success rate and response time directly reflect perceived quality.

**Simple to measure and reproduce.** Metrics that require complex formulas or joining data from multiple systems invite debate. A good SLI can be measured clearly in one place.

**Leads to action.** When the metric degrades, it should be obvious what to do. A metric you can only observe but not act on has low operational value.

**Reflects business importance.** Do not treat all APIs equally. Critical user paths (payment, login) need stricter targets than internal admin endpoints.

## SLO-to-downtime conversion

Abstract "99.9% availability" becomes concrete when you translate it to allowed downtime:

```python
def slo_to_downtime(availability, window_days):
    downtime_ratio = 1 - availability
    total_minutes = window_days * 24 * 60
    allowed_downtime_min = total_minutes * downtime_ratio
    return allowed_downtime_min

# Examples
print(f"99.9%  (monthly): {slo_to_downtime(0.999, 30):.1f} min")   # 43.2 min
print(f"99.95% (monthly): {slo_to_downtime(0.9995, 30):.1f} min")  # 21.6 min
print(f"99.99% (monthly): {slo_to_downtime(0.9999, 30):.1f} min")  # 4.3 min
```

99.99% availability allows only 4.3 minutes of downtime per month. That number makes it clear whether the target is realistic and what investment is required to achieve it.

## Measuring the four dimensions step by step

### Step 1 — Availability

```python
def availability(uptime_s, total_s):
    return uptime_s / total_s
```

Availability is the most familiar starting point — was the service alive, could it accept requests? But a high value does not automatically guarantee a good user experience.

### Step 2 — Latency (p95)

```python
def p95(samples):
    s = sorted(samples)
    return s[int(0.95 * len(s)) - 1]
```

Averages often look reassuring. But users remember the slow moments, not the average. That is why production teams watch p95 and p99. When the tail gets long, perceived quality degrades rapidly.

### Step 3 — Correctness

```python
def correctness(correct, total):
    return correct / total
```

Correctness often gets deprioritized in operational dashboards. But in systems where a wrong result is immediately a business problem — payments, permissions, settlements, order processing — it is the first dimension to check.

### Step 4 — Durability

```python
def lost_ratio(lost, stored):
    return lost / stored
```

Durability shows how well stored data is preserved. Having backups is not enough. You also need to know how much you can lose and how much you can recover.

### Step 5 — Bundle into a single SLO set

```python
slos = {
    "availability": 0.999,
    "p95_ms": 200,
    "correctness": 0.9999,
    "lost_ratio": 1e-9,
}
```

Now reliability is not one sentence but an operable target bundle. Which dimension to tighten depends on service characteristics, but at minimum the team is explicit about what matters.

### Step 6 — Evaluate multiple dimensions at once

In practice, a function that checks all dimensions simultaneously is useful:

```python
def evaluate_slos(metrics, slos):
    results = {}
    results["availability"] = metrics["uptime"] / metrics["total_time"] >= slos["availability"]
    results["latency"] = metrics["p95_ms"] <= slos["p95_ms"]
    results["correctness"] = metrics["correct"] / metrics["total"] >= slos["correctness"]
    results["durability"] = metrics["lost"] / metrics["stored"] <= slos["lost_ratio"]
    results["overall"] = all(results.values())
    return results
```

This returns `overall = True` only when every dimension is met. If even one fails, reliability is considered degraded.

## MTTR vs MTBF

Two metrics that always come up in reliability discussions:

**MTTR (Mean Time To Repair)** shows recovery speed — the average time from failure to normal state. Shorter MTTR means smaller blast radius per incident.

**MTBF (Mean Time Between Failures)** shows stability — the average time between incidents. Longer MTBF means fewer failures.

Together they tell the full reliability story. High MTBF + low MTTR = high availability.

## Measuring with PromQL

Once you split reliability into four dimensions, you need concrete queries. Here are Prometheus examples for each:

### Availability

```promql
# 5-minute window availability (success / total)
sum(rate(http_requests_total{status=~"2.."}[5m]))
/
sum(rate(http_requests_total[5m]))
```

This calculates the HTTP 2xx ratio. Add service labels to track per-service availability. When availability drops below the SLO target, the error budget starts burning.

### Latency percentiles

```promql
# Compare p50, p95, p99 simultaneously
histogram_quantile(0.50,
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
)

histogram_quantile(0.95,
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
)

histogram_quantile(0.99,
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
)
```

The wider the gap between p50 and p99, the worse the tail-latency problem. If p50 is 50ms but p99 is 3 seconds, 1 in 100 users gets a terrible experience. This often comes from database locks, cache misses, or external API timeouts.

### Correctness

Correctness often cannot be measured from HTTP status alone — a 200 OK response can still contain wrong data. Business-logic validation metrics are needed:

```promql
# Payment correctness: reconciliation match ratio
sum(rate(payment_reconciliation_total{result="match"}[1h]))
/
sum(rate(payment_reconciliation_total[1h]))
```

```python
def correctness_check(actual_amount, expected_amount, tolerance=0.01):
    """Amount correctness check (1% tolerance)"""
    if expected_amount == 0:
        return actual_amount == 0
    diff_ratio = abs(actual_amount - expected_amount) / expected_amount
    return diff_ratio <= tolerance

# Reconciliation batch
results = [
    correctness_check(10000, 10000),   # True
    correctness_check(9950, 10000),    # True (0.5% diff)
    correctness_check(9800, 10000),    # False (2% diff)
]
accuracy = sum(results) / len(results)
print(f"Correctness: {accuracy*100:.1f}%")  # 66.7%
```

### Durability

```promql
# Data sync failure ratio
sum(rate(data_sync_failures_total[1h]))
/
sum(rate(data_sync_attempts_total[1h]))
```

```python
def durability_score(objects_stored, objects_verified):
    """Durability score: verified objects / stored objects"""
    if objects_stored == 0:
        return 1.0
    return objects_verified / objects_stored

score = durability_score(1_000_000, 999_998)
print(f"Durability: {score*100:.6f}%")  # 99.999800%
```

## Reliability priority by service type

Not every service manages all four dimensions with equal weight:

| Service type | Priority 1 | Priority 2 | Rationale |
| --- | --- | --- | --- |
| Payment/settlement | Correctness | Durability | Wrong amounts → legal issues; data loss → unrecoverable |
| Real-time search | Latency | Availability | 0.5s delay → bounce rate spikes |
| File storage | Durability | Availability | Lost data → unrecoverable; brief unavailability → tolerable |
| Social feed | Availability | Latency | Cannot access → churn; slightly slow → low impact |
| IoT sensor ingestion | Availability | Durability | Preventing data gaps is key; seconds of delay is acceptable |

This table helps when designing SLOs for the first time — set stricter targets on the priority dimensions, realistic targets on the rest.

## Dashboard design for reliability

An effective layout for viewing all four dimensions at a glance:

### Row 1: Summary

| Panel | Content | Format |
| --- | --- | --- |
| Current availability | Last 5-min success rate | Stat (green/red) |
| SLO achievement | 30-day window | Gauge (with target line) |
| Error budget remaining | Remaining failure allowance | Stat (%) |

### Row 2: Per-dimension detail

| Panel | Content | Format |
| --- | --- | --- |
| Availability trend | 24h availability graph | Time series |
| Latency percentiles | p50, p95, p99 | Time series (3 lines) |
| Error ratio | 5xx ratio trend | Time series |
| Saturation | CPU, memory, connection pool | Time series |

### Row 3: Diagnostics

| Panel | Content | Format |
| --- | --- | --- |
| Recent deploys | Deploy timestamps | Annotations |
| Alert history | Recently fired alerts | Table |
| Service dependencies | External API status | Status map |

The dashboard flows top-to-bottom: "Is there a problem?" → "Which dimension?" → "What is the cause?" Without this order, you end up with many graphs but slow judgment.

## Translating reliability targets to business language

Engineering speaks in 99.9% and p99. Business asks what those numbers actually mean. Translating reliability targets into business impact makes cross-team communication far easier:

```python
def availability_to_business_impact(availability, monthly_revenue, monthly_users):
    """Translate availability to business impact"""
    downtime_minutes = (1 - availability) * 30 * 24 * 60
    revenue_at_risk = monthly_revenue * (1 - availability)
    affected_users = monthly_users * (1 - availability)

    return {
        "availability": f"{availability*100:.3f}%",
        "monthly_downtime_min": f"{downtime_minutes:.1f} min",
        "revenue_at_risk": f"${revenue_at_risk:,.0f}",
        "affected_users": f"{affected_users:,.0f}",
    }

# Example: $1M monthly revenue, 1M monthly users
for avail in [0.99, 0.999, 0.9999]:
    impact = availability_to_business_impact(avail, 1_000_000, 1_000_000)
    print(f"\n{impact['availability']}:")
    print(f"  Monthly downtime: {impact['monthly_downtime_min']}")
    print(f"  Revenue at risk:  {impact['revenue_at_risk']}")
    print(f"  Affected users:   {impact['affected_users']}")
```

Output:

```
99.000%:
  Monthly downtime: 432.0 min
  Revenue at risk:  $10,000
  Affected users:   10,000

99.900%:
  Monthly downtime: 43.2 min
  Revenue at risk:  $1,000
  Affected users:   1,000

99.990%:
  Monthly downtime: 4.3 min
  Revenue at risk:  $100
  Affected users:   100
```

With this translation, business and engineering can discuss SLOs in the same language. Questions like "what does it cost to go from 99.9% to 99.99%?" can be answered with concrete cost-benefit comparisons.

## Common mistakes when setting first reliability targets

**Applying the same target to every dimension.** Demanding 99.99% availability for both an internal admin API and a payment API over-invests in low-criticality paths.

**Looking only at averages.** Average response time of 100ms looks great, but if p99 is 2 seconds, some users are having a terrible experience.

**Ignoring relationships between dimensions.** High saturation worsens latency; high latency causes timeouts that register as errors. View dimensions together to read root causes accurately.

## Checklist

- [ ] Availability, latency, correctness, and durability defined separately.
- [ ] p95/p99 monitored alongside averages.
- [ ] Correctness automatically verified on critical paths.
- [ ] Durability policy documenting loss tolerance and recovery expectations.
- [ ] Team agreement on which dimension takes priority for this service.

## Practice Problems

1. Your service has 99.95% availability over 30 days. Convert that to allowed downtime in minutes. Then explain why p99 latency might still make users unhappy even at that availability level.
2. A payment system processes 500K transactions/day. Design SLIs for all four reliability dimensions, choosing appropriate measurement points for each.
3. Your p50 is 80ms but p99 is 4.5 seconds. List three possible root causes and explain how you would investigate each.

## Wrap-up and Next Steps

Next, we cover the difference between SLI, SLO, and SLA — what to measure, what to target, and what to commit to externally.

## Answering the Opening Questions

- **What's needed to see reliability as a measurable value rather than a vague sense of stability?**
  Splitting reliability into four dimensions (availability, latency, correctness, durability) makes each measurable and enables judging current state by those values. It also helps catch problems missed when only a single metric is watched.
- **Why do availability and latency look similar but represent different problems?**
  Availability shows whether the service is alive; latency measures how long users actually waited. Using percentiles like p95 and p99 reveals perceived quality in the slower tail far better than averages.
- **In which systems do correctness and durability become especially critical?**
  Correctness and durability are the first dimensions to check in data-centric systems (payments, permissions, settlements, messaging). Being fast but wrong, or losing data, directly shakes business trust.

<!-- toc:begin -->
## In this series

- [SRE 101 (1/10): What is SRE?](./01-what-is-sre.md)
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
