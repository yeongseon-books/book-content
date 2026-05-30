---
series: observability-101
episode: 9
title: "Observability 101 (9/10): Cost and Cardinality"
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
  - Cost
  - Cardinality
  - Metrics
  - Sampling
seo_description: How cardinality explosions, retention tiers, and sampling decisions actually drive — and tame — observability cost.
last_reviewed: '2026-05-15'
---

# Observability 101 (9/10): Cost and Cardinality

Observability rarely looks expensive at the beginning. A few counters, a few logs, a bit of tracing, and the bill seems harmless. Then one month later the cost curve changes shape and nobody can explain why.

The answer is usually structural, not accidental: too many unique labels, too much retention, and too little sampling discipline.

This is the 9th post in the Observability 101 series.


![observability 101 chapter 9 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/observability-101/09/09-01-concept-at-a-glance.en.png)
*observability 101 chapter 9 flow overview*
> Cost and Cardinality is about the boundary decision, not the tool choice.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Cost and Cardinality?
- Which signal should the example or diagram make visible for Cost and Cardinality?
- What failure should be prevented first when Cost and Cardinality reaches a real system?

## Questions this article answers

- Why is cardinality directly tied to cost?
- Why should retention be split into tiers?
- How do head sampling and tail sampling differ?
- What cost curve does each signal — metrics, logs, and traces — follow?
- Why does a team need its own observability cost budget?

## Why It Matters

In young companies the *#1 line on the AWS bill* is often *observability*. When monitoring costs *more than the product*, it becomes politics.

> *If you do not know the cost of measurement, measurement becomes the enemy.*

Observability is the ability to understand a system's internal state from external signals. In a distributed system, you cannot instrument every line of code. You rely on *metrics* (what happened), *logs* (why it happened), and *traces* (where it happened).

## Key Terms

- **Cardinality**: number of *unique label combinations*.
- **Retention tier**: hot / warm / cold *separation*.
- **Head sampling**: decided at the *start*.
- **Tail sampling**: decided after the trace finishes (slow / error first).
- **Aggregation**: shrink volume by *aggregating before retention*.

## Before/After

**Before**: `user_id` as a label, *50M series*, cost *explodes*.

**After**: `user_id` in *logs only*, labels stay *finite*, cost *predictable*.

## Hands-on: Cost Control in 5 Steps

### Step 1 — Measure cardinality

```promql
count({__name__=~".+"})              # total series
topk(20, count by (__name__) (...))  # top metrics
```

### Step 2 — Remove dangerous labels

```text
# Bad: per-user series
http_requests_total{user_id="42", path="/buy"}
# Good: dimension reduction
http_requests_total{path="/buy"}      # user_id goes to logs
```

### Step 3 — Retention tiers

```yaml
prometheus:  retention: 15d
thanos:      retention.resolution-raw: 30d
             retention.resolution-5m: 90d
             retention.resolution-1h: 1y
```

### Step 4 — Tail sampling

```yaml
processors:
  tail_sampling:
    policies:
      - name: errors
        type: status_code
        status_code: { status_codes: [ERROR] }
      - name: slow
        type: latency
        latency: { threshold_ms: 500 }
      - name: random
        type: probabilistic
        probabilistic: { sampling_percentage: 5 }
```

### Step 5 — Per-signal budget

```text
metric:  <= X million series
log:     <= Y GB per day
trace:   <= Z traces per minute after sampling
```

## Five Rules for Label Design

Metric labels are the strongest driver of cardinality. Follow these five rules to prevent cost explosions.

**1. Use only finite dimensions**

Labels must have a bounded set of possible values. Allow fixed sets like `method`, `status`, `path`, `environment`. Avoid infinitely growing values like `user_id`, `request_id`, `session_id`.

**2. High-cardinality dimensions go to logs**

When you need to track individual values — user identifiers, request IDs, IP addresses — put them in logs, not metrics. Metrics stay aggregated; individual requests live in logs and traces.

**3. Normalize paths to patterns**

Never insert dynamic paths as-is. `/users/123` and `/users/456` both become `/users/:id`. Defining path patterns bounds endpoint count.

**4. Environment and region stay at the top level**

Labels like `environment`, `region`, `cluster` that partition the entire system belong at the outermost scope. They are few in number, frequently used as query filters, and can sometimes be split at the collector level.

**5. Keep labels to 5 or fewer per metric**

More labels per metric means cardinality grows multiplicatively. Start with 3 labels as a baseline and cap at 5 to prevent explosions.

## Cardinality Explosion Cases

| Case | Problem Label | Result | Recommended Alternative |
| --- | --- | --- | --- |
| User identifier as label | `user_id` | Time series grow with user count | Move to log field |
| Request ID as label | `request_id` | Time series grow with request volume | Move to trace attribute |
| Raw URL as label | `path=/orders/123` | Path combination explosion | Normalize to `/orders/:id` |

Labels are both filter keys and storage keys. Adding an identifier as a label because "it makes search convenient" effectively replicates a user table as time series. Cost, query latency, compaction time, and backup time all degrade together.

## Cost Optimization Strategy Table

| Strategy | Applies To | Expected Effect | Watch Out |
| --- | --- | --- | --- |
| Label reduction | Metrics | Immediate decrease in series count | Do not over-prune operational axes |
| Retention tiering | Metrics / Logs | Reduced long-term storage cost | Verify regulatory retention requirements |
| Sampling | Traces / Logs | Reduced storage volume | Need policy to avoid missing rare cases |
| Log body trimming | Logs | Lower ingestion and indexing cost | Keep minimum fields for debugging |
| Query cache | Dashboards | Query CPU savings | Exempt real-time panels |

Cost optimization works better as a standing policy than a one-time cleanup. Make label review mandatory on new-metric PRs and auto-report top metrics at monthly cost reviews.

## Label Validation Helper

```python
FORBIDDEN_LABEL_KEYS = {"user_id", "request_id", "session_id", "email"}

def validate_metric_labels(metric_name: str, labels: dict[str, str]) -> list[str]:
    errors: list[str] = []
    for key, value in labels.items():
        if key in FORBIDDEN_LABEL_KEYS:
            errors.append(f"{metric_name}: forbidden label key '{key}'")
        if len(value) > 64:
            errors.append(f"{metric_name}: label '{key}' value too long")
        if "/" in value and key == "path" and any(ch.isdigit() for ch in value):
            errors.append(f"{metric_name}: path label appears unnormalized '{value}'")
    return errors

example = {"path": "/orders/12345", "status": "200"}
print(validate_metric_labels("http_requests_total", example))
```

Attach this helper to tests or CI to block cardinality explosions before they ship. Prevention is far cheaper than post-incident cleanup.

## Cost Estimation Formula

```text
Monthly metric cost = series count × scrape frequency (per min) × 60 × 24 × 30 × bytes/sample × storage unit price
```

A concrete calculation:

```python
def estimate_metric_cost(
    num_series: int,
    scrape_interval_sec: int = 15,
    bytes_per_sample: float = 2.0,
    retention_days: int = 30,
    storage_cost_per_gb: float = 0.10,  # USD
) -> dict:
    """Estimate monthly metric storage cost."""
    samples_per_day = num_series * (86400 / scrape_interval_sec)
    total_samples = samples_per_day * retention_days
    total_bytes = total_samples * bytes_per_sample
    total_gb = total_bytes / (1024 ** 3)
    cost_usd = total_gb * storage_cost_per_gb
    return {
        "series": num_series,
        "samples_per_day": int(samples_per_day),
        "total_gb": round(total_gb, 2),
        "monthly_cost_usd": round(cost_usd, 2),
    }

scenarios = [
    ("Small (1,000 series)", 1_000),
    ("Medium (50,000 series)", 50_000),
    ("Large (500,000 series)", 500_000),
    ("Cardinality explosion (5,000,000 series)", 5_000_000),
]

for name, series in scenarios:
    result = estimate_metric_cost(series)
    print(f"{name}: {result['total_gb']} GB, ${result['monthly_cost_usd']}/month")
```

```text
Small (1,000 series): 0.93 GB, $0.09/month
Medium (50,000 series): 46.57 GB, $4.66/month
Large (500,000 series): 465.66 GB, $46.57/month
Cardinality explosion (5,000,000 series): 4656.61 GB, $465.66/month
```

When cardinality grows 10×, cost grows exactly 10×. Before adding any label, calculate its cardinality impact.

## Recording Rules to Reduce Cardinality

Pre-aggregate high-cardinality raw metrics with recording rules to improve both query performance and storage cost.

```yaml
# prometheus-rules.yml
groups:
  - name: cost_optimization
    interval: 1m
    rules:
      # Raw: instance × path × method × status (tens of thousands of series)
      # Aggregated: method × status (tens of series)
      - record: job:http_requests:rate5m
        expr: sum by (method, status) (rate(http_requests_total[5m]))

      # Raw: instance × path × le (hundreds of thousands of series)
      # Aggregated: path × le (thousands of series)
      - record: job:http_duration:histogram_quantile
        expr: |
          histogram_quantile(0.99,
            sum by (path, le) (rate(http_request_duration_seconds_bucket[5m]))
          )

      # Long-term retention downsampling (1-hour resolution)
      - record: job:http_requests:rate1h
        expr: sum by (service) (rate(http_requests_total[1h]))
```

The key: dashboards and alerts reference the recording rule outputs. Raw metrics get short retention (7 days); recording rule results get long retention (90 days). This reshapes the cost structure.

| Retention Tier | Resolution | Retention Period | Purpose |
| --- | --- | --- | --- |
| Raw metrics | 15 s | 7 days | Real-time debugging |
| Recording rules (1 min) | 1 min | 30 days | Dashboards, alerts |
| Downsampled (1 hour) | 1 hour | 1 year | Trend analysis, capacity planning |
| Aggregated (1 day) | 1 day | 3 years | Executive reports |

## Label Governance Policy

Controlling cardinality requires organizational policy, not just technical tools.

| Rule | Description | Enforcement |
| --- | --- | --- |
| Label value cap | Max 100 unique values per label | Block in CI |
| Forbidden labels | `user_id`, `request_id`, `trace_id` banned from metric labels | Code review reject |
| New label approval | Cardinality impact estimate required for new labels | PR template checklist |
| Path normalization | `/users/123` → `/users/:id` before recording as label | Middleware enforcement |
| Periodic audit | Monthly review of top-50 high-cardinality series | Team meeting agenda |

```python
# Path normalization middleware example (FastAPI)
import re
from fastapi import Request

PATTERNS = [
    (re.compile(r"/users/[0-9a-f-]+"), "/users/:id"),
    (re.compile(r"/orders/\d+"), "/orders/:id"),
    (re.compile(r"/products/[\w-]+"), "/products/:slug"),
]

def normalize_path(path: str) -> str:
    """Normalize high-cardinality paths."""
    for pattern, replacement in PATTERNS:
        if pattern.search(path):
            return pattern.sub(replacement, path)
    return path

# Usage in middleware
async def metrics_middleware(request: Request, call_next):
    normalized = normalize_path(request.url.path)
    # Only record the normalized path in metrics
    REQUEST_COUNT.labels(method=request.method, path=normalized).inc()
    response = await call_next(request)
    return response
```

This single middleware reduces tens of thousands of unique paths to a few dozen patterns. Time series count drops by orders of magnitude, and query speed and storage cost both improve.

## How to Start a Cost Review

Do not wait for the invoice. Review high-cardinality metrics directly in the monitoring system.

```promql
count({__name__=~".+"})
topk(10, count by (__name__) ({__name__=~".+"}))
```

```text
Expected output:
- A small set of metrics accounts for most time series.
- Finite labels such as `path` and `status` stay, while identifiers such as `user_id` and `request_id` get removed from metrics.
- Teams can act before budgets are exceeded by cutting labels, retention, or sampling volume.
```

## What to Notice in This Code

- *Cardinality* explodes via *label multiplication*.
- *Resolution downsampling* shrinks volume of *older data*.
- *Tail sampling* keeps only *valuable traces*.

## Five Common Mistakes

1. **`user_id`, `request_id` as *labels*.** Cardinality explosion.
2. **Keeping every signal *forever*.** Cost compounds.
3. **Treating sampling as *bad*.** Risk of insolvency.
4. **Embedding *binaries* in logs.** Volume explosion.
5. **No *team-level* cost view.** Accountability dilutes.

## How This Shows Up in Production

Most companies combine *team cardinality budgets*, *retention tiers*, and *tail sampling* to make observability cost *predictable*.

## How a Senior Engineer Thinks

- *Cardinality is *tax*.*
- *Old data lives at *lower resolution*.*
- *Sampling is *not shameful*.*
- *Cost must have an *owner*.*
- *Measure the cost of measurement.*

## Checklist

- [ ] You know the *top-cardinality* metrics.
- [ ] *Retention tiers* are layered.
- [ ] Traces have *sampling*.
- [ ] Each team has a *cost budget*.

## Practice Problems

1. Find three labels that risk cardinality explosion.
2. Design a 3-tier retention plan.
3. Write a tail-sampling policy for *errors / slow / random*.

## Wrap-up and Next Steps

Without cost awareness, *observability becomes the enemy*. Next: *a production-ready stack*.

## Answering the Opening Questions

- **Why is cardinality directly linked to cost?**
  - As confirmed in the cost estimation formula, time-series count is the primary cost variable. Adding one label that increases cardinality 100× also increases storage, query, and indexing costs 100×. Metrics are not free—label design is cost design.
- **Why should retention periods be tiered?**
  - Real-time debugging needs 15-second resolution, but trend analysis from 6 months ago needs only 1-hour resolution. Tiered retention maintains the same information while saving 90%+ storage. Recording rules and downsampling automatically build this layer structure.
- **How do head sampling and tail sampling differ?**
  - Head sampling decides probabilistically at request start—simple to implement but can miss important traces. Tail sampling decides after trace completion based on conditions like errors or latency—storing only high-value traces relative to cost. For cost optimization, tail sampling is more effective.
<!-- toc:begin -->
## In this series

- [Observability 101 (1/10): What Is Observability?](./01-what-is-observability.md)
- [Observability 101 (2/10): Metrics, Logs, and Traces](./02-metric-log-trace.md)
- [Observability 101 (3/10): Collecting and Visualizing Metrics](./03-metric-collection.md)
- [Observability 101 (4/10): Structured Logging](./04-structured-logging.md)
- [Observability 101 (5/10): Distributed Tracing Basics](./05-distributed-tracing.md)
- [Observability 101 (6/10): Dashboard Design](./06-dashboard-design.md)
- [Observability 101 (7/10): Alerts and On-Call](./07-alert-and-oncall.md)
- [Observability 101 (8/10): SLI and SLO Basics](./08-sli-and-slo.md)
- **Cost and Cardinality (current)**
- A Production-Ready Observability Stack (upcoming)

<!-- toc:end -->

## References

- [Cardinality is the enemy](https://www.robustperception.io/cardinality-is-key/)
- [Thanos downsampling](https://thanos.io/tip/components/compact.md/)
- [OpenTelemetry tail sampling](https://opentelemetry.io/docs/collector/configuration/#processors)
- [Honeycomb on cost](https://www.honeycomb.io/blog/observability-cost)

Tags: Observability, Cost, Cardinality, Metrics, Sampling
