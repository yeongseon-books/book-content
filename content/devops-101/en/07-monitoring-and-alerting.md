---
series: devops-101
episode: 7
title: "DevOps 101 (7/10): Monitoring and Alerting"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - DevOps
  - Monitoring
  - Prometheus
  - Alerting
  - SRE
seo_description: A practical guide to Prometheus metrics, Grafana dashboards, and meaningful alert design.
last_reviewed: '2026-05-15'
---

# DevOps 101 (7/10): Monitoring and Alerting

The most painful monitoring failure is not a missing dashboard. It is learning about an outage from a customer before your team sees the signal. At that point, your observability stack is not helping you operate the system.

Good monitoring shortens two loops at once: how quickly you notice trouble and how quickly you narrow it down. Metrics, dashboards, and alerts matter because they help the team answer "what changed?" and "where do we look first?" under pressure.

This is the 7th post in the DevOps 101 series. In this chapter, we build the operational view around Prometheus, Grafana, RED metrics, and alerts that actually deserve to wake someone up.


![devops 101 chapter 7 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/devops-101/07/07-01-concept-at-a-glance.en.png)
*devops 101 chapter 7 flow overview*
> Effective monitoring *doesn't show everything*—it surfaces *the few signals* that let the team *act decisively*.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Monitoring and Alerting?
- Which signal should the example or diagram make visible for Monitoring and Alerting?
- What failure should be prevented first when Monitoring and Alerting reaches a real system?

## Questions this article answers

- How do *logs*, *metrics*, and *traces* play different roles as the *three signals* of monitoring?
- How do *Prometheus* and *Grafana* work together in practice?
- Why do patterns like *RED* and *USE* come up so often in operations?
- How do you design alerts that really deserve action?
- What traps do teams keep falling into even after they add monitoring?

## Why It Matters

Incidents *always come*. The difference is *how fast you know* and *how fast you can localize*.

> Operating without monitoring is *driving with eyes closed*.

Monitoring collects metrics over time. Alerting triggers *when those metrics cross a boundary*. Together they answer: *Is it running? Is it healthy? What should I do right now?*

## Key Terms

- **Metric**: a *number over time* (request count, latency, etc.).
- **Counter**: a metric that *only goes up*.
- **Gauge**: a metric that *can go up and down*.
- **Histogram**: records a *distribution* (p50, p95, p99).
- **SLO**: the *service level objective* you commit to.

## Before/After

**Before (logs only)**

```text
- During an incident, you *grep -i error*
- No trends, no idea *why it slowed down*
- Alerts arrive as *customer emails*
```

**After (metrics + alerts)**

```python
from prometheus_client import Counter, Histogram

requests = Counter("http_requests_total", "Total", ["path", "status"])
latency = Histogram("http_latency_seconds", "Latency", ["path"])
```

## Hands-on: Five Steps for Monitoring

### Step 1 - Expose /metrics in the app

```python
from prometheus_client import make_asgi_app
app.mount("/metrics", make_asgi_app())
```

### Step 2 - Configure Prometheus

```yaml
scrape_configs:
  - job_name: myapp
    static_configs:
      - targets: ['myapp:8000']
```

### Step 3 - Track RED metrics

```text
- Rate (request rate)
- Errors (error ratio)
- Duration (response time p95)
```

### Step 4 - Build a Grafana dashboard

```text
- Panel 1: rate(http_requests_total[5m])
- Panel 2: rate(http_requests_total{status=~"5.."}[5m])
- Panel 3: p95 latency
```

### Step 5 - Meaningful alerts

```yaml
- alert: HighErrorRate
  expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.01
  for: 5m
  annotations:
    summary: "5xx error rate above 1%"
```

## What to Notice in This Code

- *Sustained 5 minutes* before alert — ignore *momentary spikes*.
- *Error rate* must be a *ratio*. Absolutes shift with traffic.
- *p95* is more meaningful than *the average*.

## Five Common Mistakes

1. **Too many alerts.** *Alert fatigue* makes you ignore *real ones*.
2. **Watching only *average latency*.** The *tail (p99)* is the real problem.
3. **Metric *cardinality explosion*.** Never label by *high-cardinality* values like user_id.
4. **Alerts with *no response guide*.** What do you do at *3 AM*?
5. **Monitoring is *not monitored*.** Watch for *Prometheus down* from outside.

## How This Shows Up in Production

Mature teams use *SLO-based alerting*. They define an *error budget* and only alert when the *budget burn rate* is fast. But the monitoring system itself requires careful design.

### Core Metric Classification

| Category | Examples | Purpose |
| --- | --- | --- |
| Traffic | requests/sec | Load trend |
| Errors | 5xx ratio | Quality degradation detection |
| Latency | p95 latency | User-perceived performance |
| Resources | CPU, memory, saturation | Capacity / bottleneck |
| Business | checkout success rate | Service value observation |

### Grafana Dashboard Layout

| Panel Order | Content | Reason |
| --- | --- | --- |
| 1 | Request rate, error rate, latency | Service status in under 1 minute |
| 2 | Infrastructure resource utilization | Bottleneck hypothesis evidence |
| 3 | Recent deploy events | Correlate changes with anomalies |
| 4 | Alert history | Noise pattern review |

### Why RED + USE Together

- RED shows user-request-perspective quality fast.
- USE explains system-resource-perspective bottlenecks.
- Together they connect *"there is a problem"* with *"why it is slow"* in one conversation.

### Alertmanager Best Practices

```yaml
groups:
  - name: api-alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.01
        for: 5m
        labels:
          severity: page
        annotations:
          summary: "API 5xx ratio > 1% for 5m"
          runbook: "https://internal/wiki/runbook-api-errors"
```

Every alert includes a `runbook` link. An alert without a response guide is just noise.

### Operational Rules

1. Every alert *must* include a runbook link.
2. Use `for` conditions to filter momentary spikes.
3. Limit label cardinality to control storage cost and query speed.
4. Monitor the monitoring system itself (scrape failures, disk usage).
5. Meaningful signals only—actionable alerts only. That's how on-call quality is maintained.

## How a Senior Engineer Thinks

- *Alerts demand action*. Informational signals belong on dashboards, not pagers.
- *Dashboards must answer in one minute*. If it takes longer, restructure the panels.
- *Cardinality is cost*. Label with care; never by user_id or request_id.
- *SLOs* are an agreement between team and business—not just a number.
- *Monitoring is also a code-review subject*. Alert rules get PRs.
- *Start with RED + p95 + runbook links*. These three change response speed more than any tool migration.
- *Design questions before metrics*. "What degrades → who acts → what action" defines the alert.
## Checklist

- [ ] *RED metrics* exist for every service.
- [ ] *p95 latency* lives on the dashboard.
- [ ] *Alerts include a runbook link*.
- [ ] *Alert noise* is measured.

## Practice Problems

1. Add a */metrics* endpoint to your app.
2. Build a *RED dashboard* in Grafana.
3. Create an alert for *5xx > 1% sustained 5 minutes*.

## Wrap-up and Next Steps

Monitoring is the *eyes*. In the next post we cover *logs*, the *ears*.

## Answering the Opening Questions

- **How do the three monitoring signals—logs, metrics, traces—differ in role?**
  - Metrics like `http_requests_total` and p95 latency detect anomalies quickly as numbers; logs narrow causes with error messages and context; traces show how a single request traversed multiple services. All three together are needed to connect symptoms and causes on the same timeline.
- **How do Prometheus and Grafana work together?**
  - The flow: FastAPI exposes `/metrics`, Prometheus scrapes according to `scrape_configs`, and Grafana visualizes with request rate, error rate, and p95 panels. Adding Alertmanager rules with `for: 5m` conditions ensures dashboard anomalies translate into actual response alerts.
- **Why are metric patterns like RED and USE frequently mentioned in operations?**
  - RED (Rate, Errors, Duration) gives a quick user-perspective service health read; USE (Utilization, Saturation, Errors) explains system bottlenecks. The article recommends viewing both together because they connect "there is a problem" with "why it is slow" within the same conversation.
<!-- toc:begin -->
## In this series

- [DevOps 101 (1/10): What Is DevOps?](./01-what-is-devops.md)
- [DevOps 101 (2/10): CI Pipeline](./02-ci-pipeline.md)
- [DevOps 101 (3/10): CD and Deployment Strategies](./03-cd-and-deployment.md)
- [DevOps 101 (4/10): Environments and Configuration](./04-environments-and-config.md)
- [DevOps 101 (5/10): Infrastructure as Code](./05-infrastructure-as-code.md)
- [DevOps 101 (6/10): Containers and Build](./06-containers-and-build.md)
- **Monitoring and Alerting (current)**
- Logging and Analysis (upcoming)
- Incident Response and On-Call (upcoming)
- An Operable DevOps Flow (upcoming)

<!-- toc:end -->

## References

- [Prometheus docs](https://prometheus.io/docs/)
- [Grafana docs](https://grafana.com/docs/)
- [Google SRE — Monitoring](https://sre.google/sre-book/monitoring-distributed-systems/)
- [The RED Method (Tom Wilkie)](https://www.weave.works/blog/the-red-method-key-metrics-for-microservices-architecture/)

Tags: DevOps, Monitoring, Prometheus, Alerting, SRE
