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

- What boundary should you inspect first when applying Collecting and Visualizing Metrics?
- Which signal should the example or diagram make visible for Collecting and Visualizing Metrics?
- What failure should be prevented first when Collecting and Visualizing Metrics reaches a real system?

## Questions this article answers

- How does a metric get collected and turned into a graph?
- What is the difference between pull and push collection models?
- What role does the `/metrics` endpoint play?
- How does PromQL turn raw metrics into operational questions?
- What should a good first dashboard show?

## Why It Matters

A metric pipeline is the *starting line* of all observability. The moment the first byte flows, the system *starts talking*.

> *What you do not measure *does not exist*.*

Observability is the ability to understand a system's internal state from external signals. In a distributed system, you cannot instrument every line of code. You rely on *metrics* (what happened), *logs* (why it happened), and *traces* (where it happened).

## Key Terms

- **Exporter**: a component that *exposes metrics over HTTP*.
- **Scrape interval**: *how often* to pull.
- **Time series**: a sequence of *(label set, value, time)*.
- **PromQL**: the Prometheus *query language*.
- **Dashboard panel**: a single graph.

## Before/After

**Before**: You read logs and *guess the trend*.

**After**: A second-level graph shows the *trend immediately*.

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

### Step 2 — Prometheus config

```yaml
scrape_configs:
  - job_name: app
    scrape_interval: 5s
    static_configs:
      - targets: ["app:8000"]
```

### Step 3 — Run Prometheus (Docker)

```bash
docker run -d --name prom -p 9090:9090 \
  -v $(pwd)/prom.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus
```

### Step 4 — First PromQL queries

```promql
rate(http_requests_total[1m])
sum by (path) (rate(http_requests_total[5m]))
```

### Step 5 — Grafana panel

```bash
docker run -d --name graf -p 3000:3000 grafana/grafana
# Browser: http://localhost:3000
# Datasource: Prometheus → http://prom:9090
# Panel: rate(http_requests_total[1m])
```

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

Most companies start with *Prometheus + Grafana* and grow into *Thanos / Mimir* for scale.

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

## Practice Problems

1. Expose both a `Counter` and a `Gauge`.
2. Explain the difference between `rate()` and `increase()`.
3. Build a 5-minute average throughput dashboard.

## Wrap-up and Next Steps

Once metrics flow, *the system speaks in graphs*. Next: *structured logging*.

## Answering the Opening Questions

- **How are metrics collected and turned into graphs?**
  - Applications accumulate counter, gauge, and histogram values in memory; a collection agent or time-series DB pulls those values on a fixed interval, storing them with timestamps and labels. Querying stored timestamp-value-label tuples with PromQL produces dashboard graphs.
- **How do pull and push approaches differ?**
  - Pull has Prometheus periodically scraping `/metrics` endpoints—the collector controls scrape interval and service discovery. Push has the application sending values to StatsD, OTel Collector, or Pushgateway—suited for short-lived jobs or workloads beyond the network perimeter. The choice follows workload character: long-lived services vs short-lived tasks.
- **What role does the `/metrics` endpoint play?**
  - `/metrics` is the standard touchpoint where the application exposes current counter and gauge values in Prometheus exposition format. This endpoint lets collectors fetch metrics with a single HTTP GET without additional SDK integration—whether implemented as a sidecar or library, the same collection pipeline works.
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

Tags: Observability, Metrics, Prometheus, Grafana, Monitoring
