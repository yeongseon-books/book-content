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

This is post 7 in the DevOps 101 series. In this chapter, we build the operational view around Prometheus, Grafana, RED metrics, and alerts that actually deserve to wake someone up.


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

Mature teams use *SLO-based alerting*. They define an *error budget* and only alert when the *budget burn rate* is fast.

## How a Senior Engineer Thinks

- *Alerts demand action*. Informational signals belong on *dashboards*.
- *Dashboards must answer in one minute*.
- *Cardinality* is cost. Label carefully.
- *SLOs* are an *agreement between team and business*.
- *Monitoring is also a code-review subject*.

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

- **What boundary should you inspect first when applying Monitoring and Alerting?**
  - The article treats Monitoring and Alerting as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Monitoring and Alerting?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Monitoring and Alerting reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

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
