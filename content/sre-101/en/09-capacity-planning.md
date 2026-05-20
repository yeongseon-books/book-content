---
series: sre-101
episode: 9
title: "SRE 101 (9/10): Capacity Planning"
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
  - CapacityPlanning
  - Forecasting
  - Performance
  - Operations
seo_description: A beginner-friendly guide to capacity planning covering demand forecasting, headroom, load testing, scaling units, and cost trade-offs
last_reviewed: '2026-05-14'
---

# SRE 101 (9/10): Capacity Planning

Capacity conversations often start with the last traffic graph because it is the easiest artifact to reach for. But planning is not about copying the past. It is about estimating future demand, checking what the system can really sustain, and leaving enough room for mistakes, spikes, and lead times.

That is why capacity planning belongs with reliability, not just cost control. If you wait until traffic has already risen, the most important decision has already been made for you by production behavior.

This is post 9 in the SRE 101 series. Here we connect demand forecasting, headroom, load testing, scaling units, and cost so growth does not turn into a preventable outage.

## Questions to Keep in Mind

- Why is capacity planning a future-demand problem instead of a past-usage replay?
- Why is headroom closer to insurance than to waste?
- How should load tests be used to correct a forecast model?

## Big Picture

![sre 101 chapter 9 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/sre-101/09/09-01-concept-at-a-glance.en.png)

*sre 101 chapter 9 flow overview*

This picture places Capacity Planning inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.



## Why this topic matters

Without a forecast, the next traffic spike usually gets handled too late. By the time the team is discussing more instances or more budget, users may already be feeling the impact.

At the same time, excess capacity is not free. Good planning explains how much uncertainty the team wants to absorb and what that protection costs.

> Capacity planning is the work of aligning supply with demand using numbers.

## Concept at a glance

## Key Terms

- **demand forecast**: predicted *future demand*.
- **headroom**: *spare* capacity.
- **load test**: a *load experiment*.
- **scaling unit**: a unit of *expansion*.
- **lead time**: how long *procurement* takes.

## Before/After

**Before**: scale up based on *last quarter's* traffic.

**After**: scale up using a *forecast* and a *load test*.

## Hands-on: Modeling Capacity

### Step 1 — Trend line

```python
def linear_forecast(history, weeks_ahead):
    base = history[-1]
    growth = (history[-1] - history[0]) / max(len(history) - 1, 1)
    return base + growth * weeks_ahead
```

### Step 2 — Headroom

```python
def headroom(target_util, current_util):
    return max(0, target_util - current_util)
```

### Step 3 — Load-test result

```python
def max_rps(samples):
    return max(samples)
```

### Step 4 — Node count

```python
def nodes(predicted_rps, rps_per_node):
    return -(-predicted_rps // rps_per_node)
```

### Step 5 — Cost

```python
def cost(nodes, monthly_per_node):
    return nodes * monthly_per_node
```

### Step 6 — Turn a forecast into a promotion-week plan

```python
history = [1200, 1350, 1500, 1650]
forecast = linear_forecast(history, weeks_ahead=4)
promotion_peak = int(forecast * 1.3)
required_nodes = nodes(predicted_rps=promotion_peak, rps_per_node=350)
monthly_cost = cost(required_nodes, monthly_per_node=180)
```

This kind of calculation turns an abstract growth trend into an operating decision. Once the team translates the forecast into expected peak traffic, it can add headroom, pick an instance count, and explain the cost of that decision in the same review.

### Step 7 — Ask the load test questions that forecasts cannot answer

Forecasts tell you how much demand might arrive. Load tests tell you where the system bends first when that demand actually hits.

| Question | Why it matters |
| --- | --- |
| Does latency rise smoothly or collapse after a threshold? | A cliff usually means a queue, pool, or dependency limit is being crossed. |
| Which dependency saturates first? | The app tier may look healthy while the database or cache is already near failure. |
| How long does recovery take after the peak passes? | Slow recovery can create user impact even when raw capacity looks adequate. |
| Does autoscaling react before or after the service degrades? | Scaling policy and workload shape have to be tested together, not separately. |

## What to Notice in This Code

- The *forecast* is *data-driven*.
- *Headroom* absorbs *variability*.
- *Cost* is read *together* with capacity.

## Five Common Mistakes

1. **Replicating the *past* with no *forecast*.**
2. **Zero *headroom* leaves you exposed.**
3. **Skipping *load tests*.**
4. **Ignoring *lead time*.**
5. **Treating *cost* as a separate problem.**

## How This Shows Up in Production

A peak event like *Black Friday* is *modeled* months ahead.

## How a Senior Engineer Thinks

- *Forecasts* improve with *iteration*.
- *Headroom* is *insurance*.
- *Load tests* belong on a *schedule*.
- *Lead time* shapes the *strategy*.
- *Cost* is part of *capacity*.

## Checklist

- [ ] *Forecast model*.
- [ ] *Headroom policy*.
- [ ] *Load-test schedule*.
- [ ] *Cost analysis*.

## Practice Problems

1. Define *headroom* in one line.
2. Define *load test* in one line.
3. Define *lead time* in one line.

## Wrap-up and Next Steps

The final episode is *Building Operable Systems*.

## Answering the Opening Questions

- **Why is capacity planning a future-demand problem instead of a past-usage replay?**
  - The article treats Capacity Planning as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Why is headroom closer to insurance than to waste?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **How should load tests be used to correct a forecast model?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [SRE 101 (1/10): What is SRE?](./01-what-is-sre.md)
- [SRE 101 (2/10): Reliability](./02-reliability.md)
- [SRE 101 (3/10): SLI, SLO, SLA](./03-sli-slo-sla.md)
- [SRE 101 (4/10): Error Budget](./04-error-budget.md)
- [SRE 101 (5/10): Monitoring](./05-monitoring.md)
- [SRE 101 (6/10): Incident Response](./06-incident-response.md)
- [SRE 101 (7/10): Postmortem](./07-postmortem.md)
- [SRE 101 (8/10): Reducing Toil](./08-reducing-toil.md)
- **Capacity Planning (current)**
- Building Operable Systems (upcoming)

<!-- toc:end -->

## References

- [Software Engineering in SRE - Google SRE Book](https://sre.google/sre-book/software-engineering-in-sre/)
- [Capacity Planning - High Scalability](http://highscalability.com/blog/category/capacity-planning)
- [The Art of Capacity Planning - O'Reilly](https://www.oreilly.com/library/view/the-art-of/9780596518578/)
- [Load Testing - Grafana k6](https://grafana.com/docs/k6/latest/)

Tags: SRE, CapacityPlanning, Forecasting, Performance, Operations
