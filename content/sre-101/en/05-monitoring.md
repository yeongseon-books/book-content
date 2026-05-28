---
series: sre-101
episode: 5
title: "SRE 101 (5/10): Monitoring"
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
  - Monitoring
  - Metrics
  - Alerting
  - Observability
seo_description: A beginner-friendly guide to monitoring covering the four golden signals, metrics, logs, alerting design, and dashboard principles
last_reviewed: '2026-05-14'
---

# SRE 101 (5/10): Monitoring

Early in an operations journey, teams often feel safer when they collect everything. CPU, memory, queue depth, request counts, logs, traces, and every possible warning all look useful because maybe one of them will matter later.

But monitoring gets better when it becomes more selective, not more crowded. A metric is valuable when it helps someone decide what to do next, and an alert is valuable when it changes behavior quickly enough to reduce user impact.

This is the 5th post in the SRE 101 series. Here we treat monitoring as action-oriented measurement, then connect the four golden signals to alert rules, dashboard design, and incident response.


![sre 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/sre-101/05/05-01-concept-at-a-glance.en.png)
*sre 101 chapter 5 flow overview*

## Questions to Keep in Mind

- How is monitoring different from simply collecting a large amount of telemetry?
- Why do latency, traffic, errors, and saturation have to be read together?
- What questions do metrics answer better than logs, and where does that boundary flip?

## Why this topic matters

A flood of alerts drowns the real problem. When every threshold pages someone, the urgent signal and the background noise start to sound the same.

Good monitoring reduces decision time. It tells the team whether there is user impact, whether the system is recovering, and what to check first before a broad incident turns into a longer one.

> Monitoring is measurement that leads to action.

## Key Terms

| Term | Meaning | How it helps in practice |
| --- | --- | --- |
| golden signals | latency, traffic, errors, saturation | A shared language for triage across teams |
| alert | an action-required signal | Tells someone to change behavior now |
| threshold | a limit value that triggers a response | Separates noise from actionable signal |
| dashboard | a curated status display | Answers a question instead of showing everything |
| paging | a call-out notification | Interrupts a human only when user impact is likely |

## Monitoring types

Before diving into signals, it helps to distinguish how monitoring data gets collected and what it reveals.

| Type | Direction | What it tells you | Example |
| --- | --- | --- | --- |
| Blackbox | External probe → system | Whether users can reach the service | HTTP health-check from an outside region |
| Whitebox | System internals → metric store | Why something is broken | Prometheus scraping `/metrics` for queue depth |
| Push-based | Application pushes events | Precise timing of specific events | StatsD counter incremented on each payment |
| Pull-based | Collector scrapes endpoints | Consistent collection schedule, easy discovery | Prometheus pull model with service discovery |

A common production setup combines blackbox probes (can users reach us?) with whitebox metrics (what is happening inside?). Neither alone gives the full picture.

## The four golden signals in depth

Google's SRE book names four signals—latency, traffic, errors, saturation—as the minimum set worth monitoring for any user-facing system.

### Why four and not one?

Each signal answers a different question:

| Signal | Question it answers | Danger of ignoring it |
| --- | --- | --- |
| Latency | Is it slow? | Silent degradation that users feel before metrics catch |
| Traffic | Is demand normal? | Missing traffic may look like "no errors" when the real problem is upstream |
| Errors | Are failures rising? | Gradual error growth hides behind averages |
| Saturation | Are resources at limits? | Crossing the knee of a resource curve often triggers sudden collapse |

Reading them together prevents misinterpretation. A latency spike with flat traffic points to resource pressure or a dependency. A traffic drop with zero errors points to routing or DNS.

## Hands-on: Measuring the Four Signals

### Step 1 — Latency

```python
def latency_p95(samples):
    s = sorted(samples)
    return s[int(0.95 * len(s)) - 1]
```

Averages hide outliers. A p95 of 800 ms means 5 % of users experience at least that much delay. Always check percentiles—p50 for the common case, p95 and p99 for the tail that drives complaints.

### Step 2 — Traffic

```python
def rps(reqs, seconds):
    return reqs / seconds
```

Traffic volume sets the baseline against which other signals are read. If traffic is 50 % lower than expected, low error rates might just mean requests never arrived.

### Step 3 — Errors

```python
def error_ratio(err, total):
    return err / total
```

Error ratio is more useful than error count because a service at 10,000 RPS with 100 errors is very different from one at 200 RPS with 100 errors.

### Step 4 — Saturation

```python
def saturation(used, capacity):
    return used / capacity
```

Saturation above 80–90 % usually means the next spike will cause visible degradation. Memory, CPU, disk I/O, connection pools, and thread pools each have their own saturation curves.

### Step 5 — Prometheus metric types in practice

```python
from prometheus_client import Counter, Gauge, Histogram

# Counter — monotonically increasing (errors, requests)
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'status']
)

# Gauge — goes up and down (temperature, active connections)
active_connections = Gauge(
    'active_connections',
    'Currently active DB connections'
)

# Histogram — distribution (latency buckets)
request_duration = Histogram(
    'http_request_duration_seconds',
    'Request latency in seconds',
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)
```

Choosing the right metric type matters. A Counter suits things that only go up (total requests). A Gauge suits values that fluctuate (queue depth). A Histogram captures distributions (latency percentiles).

### Step 6 — Alert rule

```python
def should_page(err_ratio, p95_ms, sat):
    return err_ratio > 0.01 or p95_ms > 500 or sat > 0.9
```

### Step 7 — Decide what to check first during a latency spike

Golden signals are most useful when they shorten triage. A latency alert should not force the responder to guess where to begin; it should narrow the first few questions.

| Symptom | First check | Why this is first |
| --- | --- | --- |
| p95 latency climbs, traffic stays flat | Saturation and dependency latency | Slowdowns with steady demand often point to resource pressure or a downstream dependency. |
| Traffic drops suddenly | Ingress, CDN, or upstream routing health | Missing traffic can mean the app is healthy but requests never arrive. |
| Errors rise with saturation | Queue depth and timeouts | A service often fails at the edge of capacity before it fully falls over. |
| Errors rise without latency movement | Deployment diff or bad response path | Fast failures often mean logic, config, or auth problems rather than capacity exhaustion. |

### Step 8 — Tie structured events to alert decisions

```python
def classify_event(status_code, latency_ms, cache_hit):
    page = status_code >= 500 or latency_ms > 800
    investigate = latency_ms > 300 and not cache_hit
    return {"page": page, "investigate": investigate}
```

This is a small example, but it shows an important monitoring habit: alerts become stronger when they are linked to operational context. A spike in latency means more when the cache is missing or a dependency is timing out than when the workload is simply busier than normal.

## Dashboard design principles

A dashboard that shows everything helps no one. Good dashboards answer a specific question for a specific audience.

| Row | Panel | Why it belongs |
| --- | --- | --- |
| 1 | Error budget burn rate | Shows how fast the team is spending its reliability budget |
| 2 | Latency p50, p95, p99 | Separates the common experience from the painful tail |
| 3 | Traffic RPS + error ratio overlay | Correlates demand changes with failure rate |
| 4 | Saturation (CPU, memory, connections) | Predicts when the next spike will hurt |

### Dashboard anti-patterns

| Anti-pattern | Problem | Fix |
| --- | --- | --- |
| Graph graveyard (50+ panels) | Nobody reads it, nobody maintains it | Limit to 8–12 panels per dashboard |
| Average-only latency | Hides the tail that users feel | Always show p95/p99 alongside p50 |
| No time alignment | Graphs with different time ranges confuse correlation | Lock all panels to same time window |
| Missing annotations | Deploys, config changes invisible | Add deployment markers as vertical annotations |

### PromQL dashboard queries

```promql
# Error ratio over 5 minutes
sum(rate(http_requests_total{status=~"5.."}[5m]))
/
sum(rate(http_requests_total[5m]))

# Latency p99
histogram_quantile(0.99,
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
)

# Saturation — active connections vs pool size
active_connections / max_db_connections
```

## Observability beyond metrics: the three pillars

Metrics alone cannot explain *why* something failed. The three pillars—metrics, logs, traces—each answer a different scope of question.

| Pillar | Best for | Limitation |
| --- | --- | --- |
| Metrics | Detecting anomaly timing, aggregation, alerting | Cannot show individual request detail |
| Logs | Root-cause analysis, specific error messages, audit trails | High volume, hard to aggregate |
| Traces | Request flow across services, latency attribution | Sampling may miss rare events |

A structured log with a `trace_id` connects the three: you find the anomaly timing in metrics, narrow to the affected trace, then read the logs for that trace to find root cause.

```python
import logging
import json

def structured_log(level, message, **context):
    """Emit structured JSON log with trace context."""
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "level": level,
        "message": message,
        "trace_id": context.get("trace_id", "unknown"),
        "service": "payment-api",
        **context
    }
    logging.log(getattr(logging, level.upper()), json.dumps(entry))

# Usage during request handling
structured_log("error", "Payment gateway timeout",
    trace_id="abc-123-def",
    gateway="stripe",
    latency_ms=5200,
    retry_count=2
)
```

## SLO-based alerting vs. symptom-based alerting

Traditional alerting fires when a metric crosses a static threshold. SLO-based alerting fires when the *error budget burn rate* suggests the SLO will be breached at current pace.

| Approach | Fires when | Advantage | Risk |
| --- | --- | --- | --- |
| Symptom-based (threshold) | `error_rate > 1%` for 5 min | Simple to set up, immediate | Noisy on transient spikes |
| SLO-based (burn rate) | Budget consumed 10x faster than sustainable | Fewer pages, tied to customer impact | Slower to detect sudden step-change |

### Prometheus alerting rules for both approaches

```yaml
# Symptom-based: fires immediately on threshold breach
- alert: HighErrorRate
  expr: |
    sum(rate(http_requests_total{status=~"5.."}[5m]))
    /
    sum(rate(http_requests_total[5m]))
    > 0.01
  for: 5m
  labels:
    severity: page
  annotations:
    summary: "Error rate exceeds 1% for 5 minutes"

# SLO-based: fires when burn rate threatens the monthly budget
- alert: ErrorBudgetBurnRate
  expr: |
    sum(rate(http_requests_total{status=~"5.."}[1h]))
    /
    sum(rate(http_requests_total[1h]))
    > (1 - 0.999) * 14.4
  for: 5m
  labels:
    severity: page
  annotations:
    summary: "Error budget burning 14.4x faster than sustainable (1h window)"
```

The `14.4` factor means: at this rate, the entire monthly error budget would be consumed in roughly 5 days. Teams often set multiple windows (1 h at 14.4x, 6 h at 6x) to catch both fast burns and slow bleeds.

## Alert fatigue: how it forms and how to reduce it

Alert fatigue happens when the on-call engineer sees so many notifications that real signals get lost in noise.

### Common causes

1. Thresholds set too tight (fire on every minor blip)
2. Non-actionable alerts ("disk at 70 %" with no action to take)
3. Duplicates from multiple sources for the same symptom
4. Alerts that auto-resolve before anyone can act

### Reduction principles

| Principle | Implementation |
| --- | --- |
| Every alert must have an action | If no one knows what to do, demote to dashboard |
| Merge correlated alerts | Group by root symptom, not individual metric |
| Use severity tiers | Page for user impact, ticket for non-urgent |
| Review alert volume weekly | Track pages-per-shift as a KPI |

### Alert scoring function

```python
def alert_priority_score(user_impact: bool, actionable: bool,
                         frequency_per_week: int) -> str:
    """
    Score an alert to decide keep / demote / delete.
    
    - High user impact + actionable → keep as page
    - Actionable but low impact → ticket
    - Not actionable or fires > 10x/week → demote or delete
    """
    if not actionable:
        return "delete"
    if frequency_per_week > 10 and not user_impact:
        return "demote_to_dashboard"
    if user_impact:
        return "page"
    return "ticket"
```

Run this assessment quarterly on every active alert. Teams that do this consistently see 40–60 % reduction in page volume within two quarters.

## What to Notice in This Code

- The *four signals* are a *shared language* for triage.
- An *alert* must be *actionable*—if no one knows what to do, it is noise.
- A *dashboard* should answer a specific *question*, not display everything.
- *Metrics* show *when* something went wrong; *logs* show *why*.
- SLO-based alerting ties pages to *customer experience*, not raw thresholds.

## Five Common Mistakes

1. **Alerting on *everything*.** Quantity of alerts does not equal quality of coverage.
2. **Monitoring only *averages*.** A healthy average hides a painful tail.
3. **Ignoring *saturation*.** Systems degrade suddenly after crossing resource knees.
4. **Dashboards that are *graph graveyards*.** Unmaintained panels rot into confusion.
5. **Letting *alert fatigue* fester.** Fatigued on-call engineers miss real incidents.

## How This Shows Up in Production

You combine *Prometheus* metrics with *Loki* logs in a single *Grafana* view. Alerts fire into a *PagerDuty* or *Opsgenie* rotation. SLO burn-rate dashboards replace brittle static thresholds. Weekly alert-review meetings trim low-value pages and promote useful warnings.

## How a Senior Engineer Thinks

- An *alert* is a *scheduled phone call*. If you would not call someone for this, do not page.
- A *dashboard* answers a *question*. If you cannot name the question, the dashboard is decoration.
- *Metrics* connect to *customer experience*. Internal metrics matter only if they predict user-visible impact.
- *Alert fatigue* is a *KPI*. Pages-per-shift should be tracked and improved like any other reliability metric.
- *Operations* deserves *design*, too. Monitoring architecture should be reviewed like application architecture.

## Checklist

- [ ] Four golden signals defined and scraped for every user-facing service.
- [ ] Thresholds set with both symptom-based and SLO burn-rate approaches.
- [ ] Dashboards limited to 8–12 panels, each answering a named question.
- [ ] Alert fatigue measured (pages/shift) and reviewed quarterly.
- [ ] Structured logs include trace_id for correlation with metrics and traces.

## Practice Problems

1. Name the four golden signals and state what each answers in one sentence.
2. Explain why p99 latency matters more than average latency for user experience.
3. Describe one scenario where SLO-based alerting would page but symptom-based alerting would not.

## Wrap-up and Next Steps

Next, we cover *incident response*—what happens when monitoring detects a problem and someone needs to act.

## Answering the Opening Questions

- **How does monitoring differ from mere data collection?**
  Monitoring isn't just collecting data—it's a system for deciding whether to act immediately based on collected metrics. If an alert fires but no one knows what to do, that metric is merely a record, not monitoring.
- **Why must latency, traffic, errors, and saturation be viewed together?**
  Each metric answers a different question: latency asks "is it slow?", traffic asks "is demand normal?", errors asks "are failures rising?", saturation asks "are resources hitting limits?" Viewing just one easily leads to misreading the overall situation.
- **What questions do metrics and logs each answer?**
  Metrics show current state numerically and are suited for finding anomaly timing. Logs record specific requests, error messages, and stack traces for root-cause analysis. Use metrics to find *when* something went wrong, logs to find *why*.

<!-- toc:begin -->
## In this series

- [SRE 101 (1/10): What is SRE?](./01-what-is-sre.md)
- [SRE 101 (2/10): Reliability](./02-reliability.md)
- [SRE 101 (3/10): SLI, SLO, SLA](./03-sli-slo-sla.md)
- [SRE 101 (4/10): Error Budget](./04-error-budget.md)
- **Monitoring (current)**
- Incident Response (upcoming)
- Postmortem (upcoming)
- Reducing Toil (upcoming)
- Capacity Planning (upcoming)
- Building Operable Systems (upcoming)

<!-- toc:end -->

## References

- [Monitoring Distributed Systems - Google SRE Book](https://sre.google/sre-book/monitoring-distributed-systems/)
- [Practical Alerting - Google SRE Book](https://sre.google/sre-book/practical-alerting/)
- [USE Method - Brendan Gregg](https://www.brendangregg.com/usemethod.html)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/alerting/)

Tags: SRE, Monitoring, Metrics, Alerting, Observability
