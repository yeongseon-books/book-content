---
series: observability-101
episode: 6
title: "Observability 101 (6/10): Dashboard Design"
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
  - Dashboard
  - Grafana
  - SRE
  - Monitoring
seo_description: USE and RED patterns and how to choose panels that answer questions instead of decorating the wall.
last_reviewed: '2026-05-15'
---

# Observability 101 (6/10): Dashboard Design

Large dashboards often look impressive right until an incident starts. The screen is full, but the first person on call still does not know where to look, what changed first, or whether the problem is user-facing or internal.

Good dashboard design fixes that. The first screen should compress the system into a small number of questions that lead directly to the next action.

This is the 6th post in the Observability 101 series.


![observability 101 chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/observability-101/06/06-01-concept-at-a-glance.en.png)
*observability 101 chapter 6 flow overview*
> Dashboard Design is about the boundary decision, not the tool choice.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Dashboard Design?
- Which signal should the example or diagram make visible for Dashboard Design?
- What failure should be prevented first when Dashboard Design reaches a real system?

## Questions this article answers

- What separates a good dashboard from one that is just wallpaper?
- What questions do the RED and USE patterns answer?
- Why should you look at distributions instead of averages?
- Which panels belong on the first screen?
- How should you show context such as deploy timestamps alongside the charts?

## Why It Matters

Most dashboards are *decoration*. If you do not know *where to look* during an incident, 30 panels are worth *zero*.

> *A dashboard is a *tool that answers*. If it does not answer, delete it.*

Observability is the ability to understand a system's internal state from external signals. In a distributed system, you cannot instrument every line of code. You rely on *metrics* (what happened), *logs* (why it happened), and *traces* (where it happened).

## Key Terms

- **USE**: the *resource* lens.
- **RED**: the *request* lens.
- **Golden signals**: the four axes of *service health*.
- **Heatmap**: distribution *over time*.
- **Annotation**: a *marker* like a deploy.

## Before/After

**Before**: 30 panels, all *interesting*, none *answering*.

**After**: 6 panels; the first screen *immediately* tells you health.

## Hands-on: Dashboard in 5 Steps

### Step 1 — RED panels (requests)

```promql
# Rate
sum(rate(http_requests_total[1m]))
# Errors
sum(rate(http_requests_total{status=~"5.."}[1m]))
# Duration p95
histogram_quantile(0.95, sum by (le) (rate(http_duration_seconds_bucket[5m])))
```

### Step 2 — USE panels (resources)

```promql
# CPU utilization
avg(rate(node_cpu_seconds_total{mode!="idle"}[1m]))
# Memory saturation
1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes
```

### Step 3 — A Golden-signals row

```text
Row: Service Health
  Panel 1: Latency (p50/p95/p99)
  Panel 2: Traffic (req/s)
  Panel 3: Errors (5xx/min)
  Panel 4: Saturation (queue depth)
```

### Step 4 — Annotation: deploy markers

```yaml
annotations:
  - name: deploy
    datasource: prometheus
    expr: changes(build_info[1m]) > 0
```

### Step 5 — Variables to switch environment

```text
$env = staging | production
$service = api | worker | scheduler
```

## How to Validate the First Screen

The real test is whether the first 30 seconds change your next action. Imagine checkout latency rising right after a deploy.

```text
1) Check latency p95/p99 on the summary row.
2) Check whether 5xx rises at the same time.
3) Check saturation: queue depth, CPU, memory.
4) Align the anomaly with deploy annotations.
```

```text
Expected output:
- The summary row distinguishes latency regression from error spikes.
- Healthy saturation suggests the bottleneck is inside the app or a dependency, not the host.
- A deploy marker overlapping the change makes rollback or config review the next obvious step.
```

## Five Signs of a Bad Dashboard

Good dashboards are hard to define in the abstract. Bad dashboards are obvious. If you spot these patterns, redesign the entire screen.

**1. More than 20 panels.** Nobody knows where to start. Limit the first screen to a health summary and push the rest into role-specific drilldowns.

**2. Averages only.** Averages hide the long tail. If most requests take 100ms but 1% take 5 seconds, the average reads ~150ms while those users suffer 5 seconds. Show p95, p99, and distribution panels together.

**3. Inconsistent colors.** When the same metric appears in different colors on different screens, confusion follows. Standardize time ranges, color palettes, and unit notation across the organization.

**4. No thresholds.** Without baselines, "is this number good?" repeats endlessly. Showing SLO target lines, capacity warning lines, and historical average lines on each panel accelerates judgment.

**5. Vague dashboard titles.** Titles like "Operations Status" or "System Monitoring" tell you nothing about what question the screen answers. "Checkout API Health" or "Worker Saturation" is far better.

**Resolution**: Refactor or archive bad dashboards. Keeping stale screens around creates confusion about which one is the real operations view. Keep only dashboards people actually use; retire the rest based on access statistics.

## Heatmaps for Distribution Over Time

A heatmap shows how a distribution changes across time. Patterns invisible in averages or even p95 become obvious.

For example, request latency is below 100ms for most traffic, but at 9 AM every day a band of 5-second requests appears. A heatmap renders this as a red stripe at that time slot. Use Grafana's "Histogram over time" panel type or visualize Prometheus histogram buckets directly.

```promql
sum by (le) (rate(http_duration_seconds_bucket[5m]))
```

This query shows how many requests fall into each bucket. Plotted over time, it becomes a heatmap that reveals time-of-day slowdowns far faster than a single percentile line.

## Dashboard Set Composition

For a single service, you typically build three dashboards. Merging all three into one defeats their purpose.

**1. Service Overview**

- Purpose: decide within 30 seconds whether the service is healthy
- Panels: Latency p95/p99, Traffic, Errors 5xx, Saturation (4-6 panels)
- Refresh: 10 seconds or real-time
- Audience: on-call engineer, incident response team

**2. Request Analysis**

- Purpose: analyze performance patterns for specific endpoints
- Panels: per-endpoint latency/throughput, method distribution, status distribution (10-15 panels)
- Refresh: 1 minute
- Audience: backend developers, performance tuning team

**3. Infrastructure Health**

- Purpose: check host, container, and database resource state
- Panels: CPU, Memory, Disk, Network, DB connections (10-20 panels)
- Refresh: 1 minute
- Audience: SRE, infrastructure team

Each dashboard answers a different question, so splitting by role is the correct design choice.

## RED Method Practical Table

| Signal | Question | Representative Query | Common Misconception |
|---|---|---|---|
| Rate | Has request volume changed? | `sum(rate(http_requests_total[1m]))` | Looking only at totals hides per-route variance. |
| Errors | Are failures increasing? | `sum(rate(http_requests_total{status=~"5.."}[5m]))` | Excluding 4xx entirely can miss user-perceived errors. |
| Duration | Is it getting slower? | `histogram_quantile(0.95, ...)` | Averages hide tail latency. |

RED is the "user perspective." CPU, memory, and disk are useful for cause investigation but do not directly represent user quality. First screen RED, second screen USE is the stable production pattern.

## Dashboard Anti-Patterns and Fixes

| Anti-Pattern | Problem | Fix |
|---|---|---|
| 30 panels on one screen | Initial response path disappears | Shrink first screen to 4-6 summary panels |
| Mixed units (ms, s, %) | Interpretation errors increase | Enforce panel units and templatize |
| Different time ranges per panel | Comparison becomes impossible | Unify dashboard default time range |
| Inconsistent color semantics | Risk signal recognition slows | Standardize threshold color policy |
| No annotations | Deploy-impact assessment is delayed | Auto-inject deploy/incident annotations |

An operations dashboard is a decision interface, not a design artifact. When a new panel request arrives, asking "what action does this panel change?" as a team standard prevents dashboards from becoming wallpaper.

## Grafana Panel JSON Example

For GitOps-style management, version-controlling dashboards as JSON is recommended. Below is a minimal latency p95 panel definition.

```json
{
  "title": "Checkout Latency p95",
  "type": "timeseries",
  "datasource": {"type": "prometheus", "uid": "prom-main"},
  "targets": [
    {
      "expr": "histogram_quantile(0.95, sum by (le) (rate(http_request_duration_seconds_bucket{route=\"/checkout\"}[5m])))",
      "legendFormat": "p95"
    }
  ],
  "fieldConfig": {
    "defaults": {
      "unit": "s",
      "thresholds": {
        "mode": "absolute",
        "steps": [
          {"color": "green", "value": null},
          {"color": "yellow", "value": 0.5},
          {"color": "red", "value": 1.0}
        ]
      }
    }
  }
}
```

Including thresholds in the panel definition prevents people from interpreting numbers by gut feel. During on-call situations, green/yellow/red baselines directly speed up decisions.

## Grafana Dashboard Provisioning

Grafana supports declaring dashboards in YAML and version-controlling them with Git.

```yaml
# /etc/grafana/provisioning/dashboards/default.yaml
apiVersion: 1
providers:
  - name: "default"
    orgId: 1
    folder: "Operations"
    type: file
    disableDeletion: false
    editable: true
    updateIntervalSeconds: 30
    options:
      path: /var/lib/grafana/dashboards
      foldersFromFilesStructure: true
```

With this config, placing JSON files in `/var/lib/grafana/dashboards/` automatically loads them. Deploy dashboard JSON from a CI/CD pipeline and the entire environment stays synchronized without manual clicks.

## Complete 4-Panel Service Health Dashboard JSON

Below is a full example of the first row (Service Health) composed of 4 panels.

```json
{
  "title": "Service Health",
  "panels": [
    {
      "title": "Request Rate",
      "type": "timeseries",
      "gridPos": {"h": 8, "w": 6, "x": 0, "y": 0},
      "targets": [{"expr": "sum(rate(http_requests_total{service=\"$service\"}[1m]))", "legendFormat": "req/s"}],
      "fieldConfig": {"defaults": {"unit": "reqps"}}
    },
    {
      "title": "Error Rate",
      "type": "timeseries",
      "gridPos": {"h": 8, "w": 6, "x": 6, "y": 0},
      "targets": [{"expr": "sum(rate(http_requests_total{service=\"$service\",status=~\"5..\"}[1m])) / sum(rate(http_requests_total{service=\"$service\"}[1m])) * 100", "legendFormat": "error %"}],
      "fieldConfig": {"defaults": {"unit": "percent", "thresholds": {"steps": [{"color": "green", "value": null}, {"color": "red", "value": 1}]}}}
    },
    {
      "title": "Latency p95",
      "type": "timeseries",
      "gridPos": {"h": 8, "w": 6, "x": 12, "y": 0},
      "targets": [{"expr": "histogram_quantile(0.95, sum by (le) (rate(http_request_duration_seconds_bucket{service=\"$service\"}[5m])))", "legendFormat": "p95"}],
      "fieldConfig": {"defaults": {"unit": "s", "thresholds": {"steps": [{"color": "green", "value": null}, {"color": "yellow", "value": 0.5}, {"color": "red", "value": 1.0}]}}}
    },
    {
      "title": "In-Flight Requests",
      "type": "timeseries",
      "gridPos": {"h": 8, "w": 6, "x": 18, "y": 0},
      "targets": [{"expr": "sum(http_requests_in_flight{service=\"$service\"})", "legendFormat": "in-flight"}],
      "fieldConfig": {"defaults": {"unit": "short", "thresholds": {"steps": [{"color": "green", "value": null}, {"color": "yellow", "value": 100}, {"color": "red", "value": 500}]}}}
    }
  ],
  "templating": {
    "list": [
      {"name": "service", "type": "query", "query": "label_values(http_requests_total, service)"},
      {"name": "env", "type": "custom", "query": "staging,production"}
    ]
  },
  "annotations": {
    "list": [{
      "name": "Deployments",
      "datasource": "prometheus",
      "expr": "changes(build_info{service=\"$service\"}[1m]) > 0",
      "tagKeys": "service",
      "titleFormat": "Deploy"
    }]
  }
}
```

Save this JSON to `/var/lib/grafana/dashboards/service-health.json` and Grafana auto-loads it. The `$service` and `$env` variables allow switching between services and environments without duplicating dashboards, and deploy annotations display automatically.

## Dashboard Review Checklist

When creating or refactoring a dashboard, check these items to prevent wallpaper syndrome.

| # | Check Item | Pass Criteria |
|---|---|---|
| 1 | First-screen panel count <= 6 | Excess panels moved to drilldown |
| 2 | Every panel has a unit label | s, ms, %, reqps, etc. explicitly set |
| 3 | Threshold lines present | SLO target or capacity warning lines |
| 4 | Deploy annotations wired | Deploy timestamps auto-displayed |
| 5 | Variables for env/service switching | Dashboard reusable without duplication |
| 6 | Dashboard title reads like a question | "Payment API Health" not "System Monitoring" |
| 7 | Color policy consistency | Green=healthy, Yellow=caution, Red=danger |
| 8 | Default time range unified | All panels show the same time period |

## What to Notice in This Code

- *RED* is the *outside view*; *USE* is the *inside view*.
- p95 reflects *most user experience*; p99 is the *tail*.
- *Annotations* mark the *cause* of changes.

## Five Common Mistakes

1. **30 panels on *one screen*.** No idea *where to look*.
2. **Everything as *averages*.** Distribution disappears.
3. **No unit labels.** Meaning is *ambiguous*.
4. **No thresholds.** You cannot tell *risky* from *normal*.
5. **Treating dashboards as *art*.** They cease to answer.

## How This Shows Up in Production

The most consulted Service Overview dashboard collapses into about six panels. Request rate, error rate, latency, and saturation are all that remain on the first screen; everything else splits into role-specific drilldown views. Trying to solve everything on a single screen means nothing is readable.

Senior engineers write dashboard titles like questions. "API Health," "Checkout Path Latency," "Worker Saturation" — the name alone should reveal what the screen answers.

## How a Senior Engineer Thinks

- *A dashboard's title *is* its question.*
- *Six panels per screen — the rest belongs in *drilldown* dashboards.*
- *p95/p99 is closer to *truth* than the average.*
- *Mark deploys with *annotations*.*
- *Panels that do not answer get *deleted*.*

## Checklist

- [ ] You know the four *RED* queries.
- [ ] You know what *USE* means.
- [ ] The first screen is a *health summary*.
- [ ] Deploy *annotations* are visible.

## Practice Problems

1. Build a *RED* dashboard for one service.
2. Build a *USE* dashboard for host resources.
3. Mark *deploy moments* with annotations.

## Wrap-up and Next Steps

Question-driven dashboards change *decision speed*. Next: *alerts and on-call*.

## Answering the Opening Questions

- **What distinguishes a good dashboard from wallpaper?**
  - A good dashboard answers questions. "Is the service healthy right now?", "If it slowed down, where should I dig?", "Did something break after deploy?"—answerable within 30 seconds makes it good. Wallpaper has many numbers but drives no action.
- **What questions do RED and USE patterns each answer?**
  - RED answers "what quality are users experiencing?"—Rate, Errors, Duration. USE answers "what state are internal system resources in?"—Utilization, Saturation, Errors. First screen RED, second screen USE is the practical standard.
- **Why should you view distributions instead of averages?**
  - If a service averages 100ms but 1% of requests take 5 seconds, the average shows ~150ms while 1% of users suffer 5 seconds. Percentiles (p95/p99) and heatmaps catch these long tails that averages hide.
<!-- toc:begin -->
## In this series

- [Observability 101 (1/10): What Is Observability?](./01-what-is-observability.md)
- [Observability 101 (2/10): Metrics, Logs, and Traces](./02-metric-log-trace.md)
- [Observability 101 (3/10): Collecting and Visualizing Metrics](./03-metric-collection.md)
- [Observability 101 (4/10): Structured Logging](./04-structured-logging.md)
- [Observability 101 (5/10): Distributed Tracing Basics](./05-distributed-tracing.md)
- **Dashboard Design (current)**
- Alerts and On-Call (upcoming)
- SLI and SLO Basics (upcoming)
- Cost and Cardinality (upcoming)
- A Production-Ready Observability Stack (upcoming)

<!-- toc:end -->

## References

- [Brendan Gregg — USE Method](https://www.brendangregg.com/usemethod.html)
- [Tom Wilkie — RED Method](https://www.weave.works/blog/the-red-method-key-metrics-for-microservices-architecture/)
- [Google SRE — Golden Signals](https://sre.google/sre-book/monitoring-distributed-systems/)
- [Grafana dashboard best practices](https://grafana.com/docs/grafana/latest/best-practices/)
- [Grafana panels and visualizations](https://grafana.com/docs/grafana/latest/panels-visualizations/)

Tags: Observability, Dashboard, Grafana, SRE, Monitoring
