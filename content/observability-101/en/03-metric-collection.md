---
series: observability-101
episode: 3
title: "Observability 101 (3/10): Collecting and Visualizing Metrics"
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
  - Metrics
  - Prometheus
  - Grafana
  - Monitoring
seo_description: Build your first metric pipeline with the Prometheus pull model, exporters, and Grafana dashboards from one Python service.
last_reviewed: '2026-05-15'
---

# Observability 101 (3/10): Collecting and Visualizing Metrics

It is easy to say metrics matter and still have no reliable path from application code to a graph an engineer can trust. A number in memory is not observability yet. Someone has to expose it, scrape it, store it, and query it correctly.

Once you understand that path, Prometheus and Grafana stop looking like tools you install and start looking like parts of one measurement pipeline.

This is the 3rd post in the Observability 101 series.


![observability 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/observability-101/03/03-01-concept-at-a-glance.en.png)
*observability 101 chapter 3 flow overview*
> Collecting and Visualizing Metrics is about the boundary decision, not the tool choice.

## Questions to Keep in Mind

- How does a metric get collected and turned into a graph?
- What is the difference between pull and push collection models?
- What role does the `/metrics` endpoint play?

## Why It Matters

A metric pipeline is the *starting line* of all observability. The moment the first byte flows, the system *starts talking*.

> *What you do not measure does not exist.*

Observability is the ability to understand a system's internal state from external signals. In a distributed system, you cannot instrument every line of code. You rely on *metrics* (what happened), *logs* (why it happened), and *traces* (where it happened).

## Metric Type Comparison

Metrics come in four main types. Knowing the definition, example, and use case of each makes it easy to choose.

| Type | Definition | Example | When to Use |
| --- | --- | --- | --- |
| Counter | Ever-increasing value | Total requests, error count | Recording cumulative quantities |
| Gauge | Fluctuating value | CPU usage, queue length, memory | Representing current state |
| Histogram | Distribution stored in buckets | Response time distribution (p50, p95, p99) | Observing tail latency |
| Summary | Quantiles computed client-side | p95, p99 (client-computed) | Reducing server load |

Prometheus recommends Histogram over Summary. Summary computes quantiles client-side, making it impossible to aggregate across instances. Histogram lets the server compute arbitrary quantiles later.

## Key Terms

- **Exporter**: a component that *exposes metrics over HTTP*.
- **Scrape interval**: *how often* to pull.
- **Time series**: a sequence of *(label set, value, time)*.
- **PromQL**: the Prometheus *query language*.
- **Dashboard panel**: a single graph.

## Pull vs Push Collection

There are two main approaches to collecting metrics.

| Aspect | Pull | Push |
| --- | --- | --- |
| Representative Tools | Prometheus | Datadog, CloudWatch |
| Mechanism | Collector periodically calls endpoint | Application sends to collector |
| Strengths | Easy to control scrape interval and discovery | Works behind firewalls, collects short-lived jobs |
| Weaknesses | Fails if collector cannot reach endpoint | Requires collector address config in app |
| Use Case | Kubernetes, microservices | Serverless, batch jobs |

Prometheus chose the pull model. Because the collector holds the initiative, it is easy to control which targets to read and when. Target discovery integrates with service discovery for automation.

## Before/After

**Before**: You read logs and *guess the trend*. Comparing the last 10 minutes to now is slow and unreliable.

**After**: A second-level graph shows the *trend immediately*. Whether requests are rising, which route is spiking, when latency started wobbling — all visible in one line.

## Exposing Metrics with prometheus_client

The Python `prometheus_client` library makes metric instrumentation straightforward.

```python
from prometheus_client import Counter, Gauge, Histogram, start_http_server
import time
import random

# Define metrics
request_count = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

active_connections = Gauge(
    "active_connections",
    "Number of active connections"
)

request_duration = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0)
)

# Usage
def handle_request(method: str, endpoint: str):
    active_connections.inc()

    start = time.time()
    status = 200 if random.random() > 0.1 else 500

    # Simulate request processing
    time.sleep(random.uniform(0.1, 1.0))

    duration = time.time() - start

    request_count.labels(method=method, endpoint=endpoint, status=status).inc()
    request_duration.labels(method=method, endpoint=endpoint).observe(duration)

    active_connections.dec()
    return status

# Start metrics server (expose /metrics on port 8000)
if __name__ == "__main__":
    start_http_server(8000)
    print("Metrics server running on :8000/metrics")

    while True:
        handle_request("GET", "/api/users")
        time.sleep(1)
```

Run this code and call `curl localhost:8000/metrics` to see metrics in Prometheus exposition format. Prometheus reads this endpoint periodically and stores the data.

## Preventing Cardinality Explosion

Cardinality is the number of unique time-series created by label combinations. Putting `user_id` in a label means one series per user — Prometheus stores each separately, so memory and disk costs explode.

### Patterns to Avoid

1. **Never put unique identifiers in labels**: user_id, order_id, session_id belong in logs or trace attributes.
2. **Normalize label values**: Use `/api/users/:id` instead of `/api/users/123` as a path label.
3. **Keep only necessary labels**: Only attach dimensions worth aggregating — method, status, endpoint.

### Estimating Cardinality

If each label has N unique values, cardinality is the product. 3 methods × 10 endpoints × 5 statuses = 150 time-series. Before adding a new label, ask whether it is truly needed or whether the information belongs in logs instead.

## Hands-on: Metric Pipeline in 5 Steps

### Step 1 — Python `/metrics`

```python
from prometheus_client import Counter, start_http_server

reqs = Counter("http_requests_total", "Total requests", ["path"])

if __name__ == "__main__":
    start_http_server(8000)
    while True:
        reqs.labels(path="/health").inc()
```

The application must first expose metrics externally. Think of `/metrics` as a standard entry point read by collectors, not humans.

### Step 2 — Prometheus config

```yaml
scrape_configs:
  - job_name: app
    scrape_interval: 5s
    static_configs:
      - targets: ["app:8000"]
```

Prometheus does not wait for pushes — it pulls. Declare which targets to read and how often, and the collector calls `/metrics` on schedule.

### Step 3 — Run Prometheus (Docker)

```bash
docker run -d --name prom -p 9090:9090 \
  -v $(pwd)/prom.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus
```

From this point, metrics become stored time-series rather than ephemeral in-memory numbers. Without a collector attached, exposed metrics are values that flow away.

### Step 4 — First PromQL queries

```promql
rate(http_requests_total[1m])
sum by (path) (rate(http_requests_total[5m]))
```

A counter is cumulative, so graphing it raw is hard to interpret. `rate()` converts it to per-second growth — this is the most frequently used fundamental in metric interpretation.

### Step 5 — Grafana panel

```bash
docker run -d --name graf -p 3000:3000 grafana/grafana
# Browser: http://localhost:3000
# Datasource: Prometheus → http://prom:9090
# Panel: rate(http_requests_total[1m])
```

A dashboard is not a screen that decorates numbers — it is a screen that attaches questions. The first panel should answer exactly one question like "how many requests are coming in right now?"

## Prometheus Scrape Configuration Example

In production, scrape configs grow complex as services multiply. Below is a basic configuration combining static targets with Kubernetes service discovery.

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 30s

scrape_configs:
  - job_name: "app-static"
    scrape_interval: 5s
    static_configs:
      - targets: ["app-1:8000", "app-2:8000"]
        labels:
          team: "checkout"
          env: "prod"

  - job_name: "node-exporter"
    static_configs:
      - targets: ["node-a:9100", "node-b:9100"]

  - job_name: "kubernetes-pods"
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        target_label: __address__
        regex: (.+)
        replacement: ${1}
```

Two configuration principles: First, do not use the same interval for all jobs. Fast-changing APIs get 5s; relatively stable node metrics get 15s+ — this reduces collection cost. Second, attach operational labels like `team` and `env` explicitly to simplify queries and routing.

## Counter, Gauge, Histogram in Practice

Below is how all three metric types work together for the same request.

```python
import random
import time
from prometheus_client import Counter, Gauge, Histogram

REQUEST_TOTAL = Counter(
    "checkout_requests_total",
    "Total checkout requests",
    ["route", "status"],
)

INFLIGHT = Gauge(
    "checkout_inflight_requests",
    "In-flight checkout requests",
)

LATENCY = Histogram(
    "checkout_request_duration_seconds",
    "Checkout request duration",
    ["route"],
    buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0),
)

def handle_checkout(route: str = "/checkout") -> int:
    INFLIGHT.inc()
    started = time.time()
    try:
        time.sleep(random.uniform(0.03, 0.7))
        status = 500 if random.random() < 0.08 else 200
        REQUEST_TOTAL.labels(route=route, status=str(status)).inc()
        return status
    finally:
        LATENCY.labels(route=route).observe(time.time() - started)
        INFLIGHT.dec()
```

Counter records cumulative facts. Gauge records current-moment state. Histogram records distribution. Conflating the three into one type leads to misleading alerts and wrong conclusions.

## PromQL Interpretation Patterns

Dashboard quality equals query quality. These three queries are the most frequently used base patterns.

```promql
# Throughput (requests per second)
sum(rate(checkout_requests_total[1m]))

# 5xx error ratio
sum(rate(checkout_requests_total{status=~"5.."}[5m]))
/
sum(rate(checkout_requests_total[5m]))

# p95 latency
histogram_quantile(
  0.95,
  sum by (le) (rate(checkout_request_duration_seconds_bucket[5m]))
)
```

Interpretation order should be consistent: first verify numerator and denominator match, then check whether the aggregation axis (`by`) is too broad or narrow, and finally confirm the window length fits the question. To see 30-second wobbles, a 5-minute window is too slow; for monthly trends, a 1-minute window is too noisy.

## Grafana Dashboard JSON Example

Grafana dashboards can be managed as JSON. Below is a minimal dashboard showing metric collection status at a glance.

```json
{
  "title": "Checkout API Overview",
  "panels": [
    {
      "title": "Request Rate",
      "type": "timeseries",
      "targets": [
        {
          "expr": "sum(rate(checkout_requests_total[5m]))",
          "legendFormat": "req/s"
        }
      ],
      "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
    },
    {
      "title": "Error Rate",
      "type": "timeseries",
      "targets": [
        {
          "expr": "sum(rate(checkout_requests_total{status=~\"5..\"}[5m])) / sum(rate(checkout_requests_total[5m]))",
          "legendFormat": "error ratio"
        }
      ],
      "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
    },
    {
      "title": "p95 Latency",
      "type": "timeseries",
      "targets": [
        {
          "expr": "histogram_quantile(0.95, sum by (le) (rate(checkout_request_duration_seconds_bucket[5m])))",
          "legendFormat": "p95"
        }
      ],
      "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
    },
    {
      "title": "In-Flight Requests",
      "type": "gauge",
      "targets": [
        {
          "expr": "sum(checkout_inflight_requests)",
          "legendFormat": "inflight"
        }
      ],
      "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8}
    }
  ]
}
```

These four panels follow the RED method (Rate, Errors, Duration) plus current concurrency (In-Flight). Each panel answers exactly one question:

1. How many requests are coming in now? (Request Rate)
2. Is the failure ratio rising? (Error Rate)
3. What latency do users experience? (p95 Latency)
4. Are concurrent requests piling up? (In-Flight)

When adding panels, start by writing the question it answers. Panels created without a question end up ignored.

## Recording Rules to Reduce Query Cost

As dashboards grow, the same PromQL gets executed repeatedly across panels. Recording rules pre-compute frequently used queries and store the result as new time-series.

```yaml
groups:
  - name: checkout_rules
    interval: 30s
    rules:
      - record: checkout:request_rate:5m
        expr: sum(rate(checkout_requests_total[5m]))

      - record: checkout:error_ratio:5m
        expr: |
          sum(rate(checkout_requests_total{status=~"5.."}[5m]))
          / sum(rate(checkout_requests_total[5m]))

      - record: checkout:latency_p95:5m
        expr: |
          histogram_quantile(0.95,
            sum by (le) (rate(checkout_request_duration_seconds_bucket[5m]))
          )
```

Three benefits of recording rules:

1. **Faster queries**: Dashboards read pre-computed series instead of evaluating complex expressions on every refresh.
2. **Alert stability**: Using recording rules in alert rules reduces false negatives caused by missing time-series.
3. **Easier long-term retention**: Keep raw high-resolution data for 2 weeks, but retain recording rule results longer.

The naming convention is `<namespace>:<metric>:<window>`. When the entire team follows the same naming standard, query templates become reusable.

## How to Verify the Pipeline End to End

The pipeline fails more often at the seams than in the code itself, so verify each hop explicitly.

```bash
# 1) The application exposes metrics
curl -s http://localhost:8000/metrics | grep http_requests_total

# 2) Prometheus sees the target as healthy
curl -s http://localhost:9090/api/v1/targets | grep '"health":"up"'
```

```text
Expected output:
- `/metrics` contains `http_requests_total`.
- The Prometheus target shows `up`.
- Grafana renders a non-zero `rate(http_requests_total[1m])` line.
```

## What to Notice in This Code

- Prometheus *pulls*; the app *exposes*.
- `/metrics` returns *plain text*.
- `rate()` computes *per-second growth* (counter → rate).

## Five Common Mistakes

1. **Graphing a counter *as is*.** You need `rate()`.
2. **Putting *unique IDs* in labels.** Cardinality explodes.
3. **Setting scrape interval to *1 second*.** You crush the target.
4. **Pull blocked by a *firewall*.** Target reports *down*.
5. **Stuffing *every panel* into Grafana.** Meaningless *wallpaper*.

## How This Shows Up in Production

Most companies start with *Prometheus + Grafana* and grow into *Thanos / Mimir* for scale. But the starting principles are the same: metrics must be well-exposed, reliably collected, and visualized around questions.

Senior engineers look at the pipeline before the dashboard. Is the scrape interval appropriate? Are labels controlled? Do queries confuse cumulative values with rates? More numbers do not mean better observability.

One critical perspective is pipeline reliability itself. If the collector dies, all alerts go silent. Running Prometheus as a single instance is risky even for small teams. At minimum, verify two things:

1. **Collector liveness alert**: If Prometheus's own `up` metric hits 0, an external channel (e.g., health-check-based PagerDuty) must fire.
2. **Scrape gap detection**: If `scrape_samples_scraped == 0` persists beyond a threshold, the target is dead or there is a network issue.

Without these meta-alerts, you can find yourself in an incident where the dashboard is blank and nobody knows. The collector must run stably for everything built on top — alerts and dashboards — to have meaning.

## How a Senior Engineer Thinks

- *Measure what is measurable.*
- *Pull lives or dies by *target discovery*.*
- *Counters always go through *rate()*.*
- *A dashboard is a *question*, not a panel.*
- *Cardinality is the first cost variable.*

## Checklist

- [ ] You expose `/metrics` from your app.
- [ ] Prometheus shows the target as *up*.
- [ ] You write one *PromQL* query.
- [ ] You build the first Grafana panel.
- [ ] You can explain recording rule purpose and naming.
- [ ] You can describe conditions that cause cardinality explosion.

## Practice Problems

1. Expose both a `Counter` and a `Gauge`.
2. Explain the difference between `rate()` and `increase()`.
3. Build a 5-minute average throughput dashboard.

## Wrap-up and Next Steps

Once metrics flow, *the system speaks in graphs*. Recording rules pre-compute expensive queries. Cardinality control keeps the collector alive. Next: *structured logging*.

## Answering the Opening Questions

- **How are metrics collected and turned into graphs?**
  - Applications accumulate counter, gauge, and histogram values in memory; a collection agent or time-series DB pulls those values on a fixed interval, storing them with timestamps and labels. Querying stored timestamp-value-label tuples with PromQL produces dashboard graphs.
- **How do pull and push approaches differ?**
  - Pull has Prometheus periodically scraping `/metrics` endpoints — the collector controls scrape interval and service discovery. Push has the application sending values to StatsD, OTel Collector, or Pushgateway — suited for short-lived jobs or workloads beyond the network perimeter. The choice follows workload character: long-lived services vs short-lived tasks.
- **What role does the `/metrics` endpoint play?**
  - `/metrics` is the standard touchpoint where the application exposes current counter and gauge values in Prometheus exposition format. This endpoint lets collectors fetch metrics with a single HTTP GET without additional SDK integration — whether implemented as a sidecar or library, the same collection pipeline works.
<!-- toc:begin -->
## In this series

- [Observability 101 (1/10): What Is Observability?](./01-what-is-observability.md)
- [Observability 101 (2/10): Metrics, Logs, and Traces](./02-metric-log-trace.md)
- **Collecting and Visualizing Metrics (current)**
- Structured Logging (upcoming)
- Distributed Tracing Basics (upcoming)
- Dashboard Design (upcoming)
- Alerts and On-Call (upcoming)
- SLI and SLO Basics (upcoming)
- Cost and Cardinality (upcoming)
- A Production-Ready Observability Stack (upcoming)

<!-- toc:end -->

## References

- [Prometheus getting started](https://prometheus.io/docs/prometheus/latest/getting_started/)
- [prometheus_client (Python)](https://github.com/prometheus/client_python)
- [PromQL basics](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Grafana docs](https://grafana.com/docs/grafana/latest/)
- [Recording rules](https://prometheus.io/docs/prometheus/latest/configuration/recording_rules/)

Tags: Observability, Metrics, Prometheus, Grafana, Monitoring
