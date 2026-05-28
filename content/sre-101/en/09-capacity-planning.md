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

This is the 9th post in the SRE 101 series. Here we connect demand forecasting, headroom, load testing, scaling units, and cost so growth does not turn into a preventable outage.


![sre 101 chapter 9 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/sre-101/09/09-01-concept-at-a-glance.en.png)
*sre 101 chapter 9 flow overview*

## Questions to Keep in Mind

- Why is capacity planning a future-demand problem instead of a past-usage replay?
- Why is headroom closer to insurance than to waste?
- How should load tests be used to correct a forecast model?

## Why this topic matters

Without a forecast, the next traffic spike usually gets handled too late. By the time the team is discussing more instances or more budget, users may already be feeling the impact. Services with predictable peaks—Black Friday, semester start, major promotions—need plans months in advance.

At the same time, excess capacity is not free. Good planning explains how much uncertainty the team wants to absorb and what that protection costs. The core of capacity planning is reading safety and cost together.

> Capacity planning is the work of aligning supply with demand using numbers.

## Key Terms

| Term | Meaning | Role in operations |
| --- | --- | --- |
| demand forecast | Predicted future traffic/load | Determines how much to prepare |
| headroom | Spare capacity above predicted peak | Absorbs spikes and forecast errors |
| load test | A controlled experiment under load | Validates actual system limits |
| scaling unit | The minimum unit of expansion (node, pod, instance) | Makes cost calculations concrete |
| lead time | Time from decision to resource availability | Dictates how early decisions must happen |

## Why performance testing alone is insufficient

Load tests show where the current system breaks. But they cannot tell you how much traffic next quarter will bring, how large a marketing event will be, or what patterns a new feature will create. That is why forecasting is needed alongside testing.

Conversely, forecasts without validation against actual limits can drift from reality. Strong teams read both: demand through models, supply through load tests.

## Why headroom must be viewed alongside cost

Headroom looks like waste because it is unused capacity. But from an operations standpoint, it is variability insurance. Without slack to absorb spikes, failover traffic, and forecast errors, small variations immediately become incidents.

Good plans do not argue for headroom abstractly. They explain: "We are spending X% more to cover Y% of expected variation." Cost and capacity belong in the same sentence.

## Capacity planning input data

| Data item | Collection method | Example value | Notes |
| --- | --- | --- | --- |
| Current traffic | Prometheus `rate(http_requests_total[5m])` | 1500 RPS | Use weekday average, exclude peak hours |
| Resource utilization | Node exporter CPU/memory metrics | CPU 45 %, Memory 60 % | Check p95 utilization, not just averages |
| Weekly growth rate | Regression over last 4–8 weeks | +10 % per month | Apply seasonality correction |
| Peak multiplier | Daily max / daily average ratio | 2.5x | Factor in promotions and events |
| Per-node throughput | Load test results | 350 RPS/node | Under latency constraint (p99 < 500 ms) |
| Lead time | Vendor provisioning timeline | 2–4 weeks | Cloud is instant; on-prem can be months |

With all six inputs collected, you can build and validate a forecast. Missing any one reduces confidence significantly.

## Hands-on: Modeling Capacity

### Step 1 — Trend line

```python
def linear_forecast(history, weeks_ahead):
    base = history[-1]
    growth = (history[-1] - history[0]) / max(len(history) - 1, 1)
    return base + growth * weeks_ahead
```

The simplest forecast extends the recent trend. It is not perfect, but it treats future demand explicitly instead of implicitly assuming "same as last quarter."

### Step 2 — Headroom

```python
def headroom(target_util, current_util):
    return max(0, target_util - current_util)
```

Headroom is the gap between current utilization and target utilization. Too tight means any spike becomes an incident. Too wide means unnecessary cost. The team needs a documented target—typically 70–80 % peak utilization.

### Step 3 — Load-test result

```python
def max_rps(samples):
    return max(samples)
```

The forecast tells you what demand to expect. The load test tells you what the system can actually deliver. When forecast exceeds tested capacity, you know scaling is needed before the gap arrives.

### Step 4 — Node count

```python
def nodes(predicted_rps, rps_per_node):
    return -(-predicted_rps // rps_per_node)
```

Ceiling division ensures you never provision *just barely enough*—which is the same as *not enough* the moment traffic fluctuates.

### Step 5 — Cost

```python
def cost(nodes, monthly_per_node):
    return nodes * monthly_per_node
```

Capacity planning is also cost planning. When scaling units increase, monthly spend changes. Performance numbers and budget numbers must appear in the same review.

### Step 6 — Turn a forecast into a promotion-week plan

```python
history = [1200, 1350, 1500, 1650]
forecast = linear_forecast(history, weeks_ahead=4)
promotion_peak = int(forecast * 1.3)
required_nodes = nodes(predicted_rps=promotion_peak, rps_per_node=350)
monthly_cost = cost(required_nodes, monthly_per_node=180)
```

This calculation matters because it converts a trend graph into an operating decision. Expected traffic gets peak-adjusted, connected to per-node throughput, and expressed as both an instance count and a monthly cost—all in the same context.

### Step 7 — Ask the load test questions that forecasts cannot answer

Forecasts tell you how much demand might arrive. Load tests tell you where the system bends first when that demand actually hits.

| Question | Why it matters |
| --- | --- |
| Does latency rise smoothly or collapse after a threshold? | A cliff usually means a queue, pool, or dependency limit is being crossed. |
| Which dependency saturates first? | The app tier may look healthy while the database or cache is already near failure. |
| How long does recovery take after the peak passes? | Slow recovery can create user impact even when raw capacity looks adequate. |
| Does autoscaling react before or after the service degrades? | Scaling policy and workload shape have to be tested together, not separately. |

## Full capacity forecast with numpy

```python
import numpy as np

def linear_regression_forecast(historical_data, weeks_ahead):
    """
    Linear regression forecast for future capacity needs.
    
    Args:
        historical_data: List of (week, rps) tuples
        weeks_ahead: How many weeks to forecast
    
    Returns:
        Predicted RPS for each future week
    """
    weeks = np.array([w for w, _ in historical_data])
    rps = np.array([r for _, r in historical_data])
    
    # Fit: rps = slope * week + intercept
    coefficients = np.polyfit(weeks, rps, 1)
    slope, intercept = coefficients
    
    future_weeks = np.arange(weeks[-1] + 1, weeks[-1] + weeks_ahead + 1)
    predictions = slope * future_weeks + intercept
    
    return {
        "slope": slope,
        "intercept": intercept,
        "predictions": list(zip(future_weeks, predictions)),
        "growth_per_week": slope
    }

# Example: 8 weeks of data, forecast 12 weeks out
historical_data = [
    (1, 1200), (2, 1280), (3, 1350), (4, 1420),
    (5, 1500), (6, 1580), (7, 1650), (8, 1720)
]

result = linear_regression_forecast(historical_data, weeks_ahead=12)

print("=== Capacity Forecast ===")
print(f"Growth rate: {result['growth_per_week']:.1f} RPS/week")
print(f"\nPredicted traffic for next 12 weeks:")

for week, rps in result["predictions"]:
    print(f"  Week {week}: {rps:.0f} RPS")

# Apply peak multiplier and headroom
peak_multiplier = 2.5
headroom_pct = 0.20

final_week, final_rps = result["predictions"][-1]
peak_rps = final_rps * peak_multiplier
target_capacity = peak_rps * (1 + headroom_pct)

print(f"\n=== With Peak ({peak_multiplier}x) + Headroom ({headroom_pct*100}%) ===")
print(f"Week {final_week} forecast: {final_rps:.0f} RPS")
print(f"Peak capacity needed: {peak_rps:.0f} RPS")
print(f"Target capacity: {target_capacity:.0f} RPS")

# Infrastructure calculation
rps_per_node = 350
nodes_needed = int(np.ceil(target_capacity / rps_per_node))
monthly_cost_per_node = 180
total_monthly_cost = nodes_needed * monthly_cost_per_node

print(f"\n=== Infrastructure ===")
print(f"Nodes required: {nodes_needed}")
print(f"Monthly cost: ${total_monthly_cost}")
```

**Example output:**

```
=== Capacity Forecast ===
Growth rate: 74.3 RPS/week

Predicted traffic for next 12 weeks:
  Week 9: 1789 RPS
  Week 10: 1863 RPS
  ...
  Week 20: 2605 RPS

=== With Peak (2.5x) + Headroom (20%) ===
Week 20 forecast: 2605 RPS
Peak capacity needed: 6513 RPS
Target capacity: 7815 RPS

=== Infrastructure ===
Nodes required: 23
Monthly cost: $4140
```

This takes 8 weeks of historical data, projects 12 weeks forward, applies peak and headroom factors, then calculates node count and cost. The forecast chart makes the decision visual for stakeholders.

## Load test analysis

Forecasts are theoretical. Load tests reveal reality.

```python
def analyze_load_test_results(test_results):
    """
    Analyze load test results to find the breaking point.
    
    test_results: List of (rps, latency_p99, error_rate) tuples
    """
    analysis = {
        "max_safe_rps": 0,
        "breaking_point": None,
        "recommendations": []
    }
    
    for rps, latency_p99, error_rate in test_results:
        # Acceptance criteria: p99 < 1000 ms AND error rate < 1%
        if latency_p99 < 1000 and error_rate < 0.01:
            analysis["max_safe_rps"] = rps
        else:
            if not analysis["breaking_point"]:
                analysis["breaking_point"] = {
                    "rps": rps,
                    "latency_p99": latency_p99,
                    "error_rate": error_rate
                }
                break
    
    # Safe operating capacity = 80% of max tested
    safe_capacity = analysis["max_safe_rps"] * 0.8
    analysis["safe_capacity"] = safe_capacity
    analysis["recommendations"].append(
        f"Max tested: {analysis['max_safe_rps']} RPS, "
        f"safe operating capacity: {safe_capacity:.0f} RPS"
    )
    
    if analysis["breaking_point"]:
        bp = analysis["breaking_point"]
        if bp["latency_p99"] >= 1000:
            analysis["recommendations"].append(
                f"Latency bottleneck at {bp['rps']} RPS "
                f"(p99 = {bp['latency_p99']:.0f} ms)"
            )
        if bp["error_rate"] >= 0.01:
            analysis["recommendations"].append(
                f"Error rate spike at {bp['rps']} RPS "
                f"({bp['error_rate']*100:.1f}%)"
            )
    
    return analysis

# Example test results
test_results = [
    (1000, 250, 0.001),
    (1500, 350, 0.002),
    (2000, 450, 0.003),
    (2500, 650, 0.005),
    (3000, 850, 0.008),
    (3500, 1200, 0.015),  # Breaking point
]

analysis = analyze_load_test_results(test_results)

print("=== Load Test Analysis ===")
print(f"Max safe RPS: {analysis['max_safe_rps']}")
print(f"Safe capacity (80%): {analysis['safe_capacity']:.0f} RPS")

if analysis["breaking_point"]:
    bp = analysis["breaking_point"]
    print(f"\nBreaking point at {bp['rps']} RPS:")
    print(f"  Latency p99: {bp['latency_p99']:.0f} ms")
    print(f"  Error rate: {bp['error_rate']*100:.2f}%")

print("\nRecommendations:")
for rec in analysis["recommendations"]:
    print(f"  - {rec}")
```

The load test calibrates the forecast. If theory says 3000 RPS is achievable but the test shows a breaking point at 2500 RPS, the test wins—that is the real limit.

## Load testing tools

### k6 basic script

```javascript
// load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 100 },  // ramp-up
    { duration: '5m', target: 100 },  // steady state
    { duration: '2m', target: 200 },  // spike
    { duration: '5m', target: 200 },
    { duration: '2m', target: 0 },    // ramp-down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'],
    http_req_failed: ['rate<0.01'],
  },
};

export default function () {
  let response = http.get('https://api.example.com/health');
  check(response, {
    'status is 200': (r) => r.status === 200,
    'latency < 500ms': (r) => r.timings.duration < 500,
  });
  sleep(1);
}
```

```bash
k6 run --vus 200 --duration 10m load-test.js
```

### Locust basic script

```python
# locustfile.py
from locust import HttpUser, task, between

class APIUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def get_home(self):
        self.client.get("/")

    @task(1)
    def get_api(self):
        self.client.get("/api/data")
```

```bash
locust -f locustfile.py --host=https://api.example.com --users 200 --spawn-rate 10
```

Load tests should check not just peak throughput but also latency distribution, error rates, bottleneck locations, and recovery time after the peak subsides.

## What to Notice in This Code

- Forecasting and validation must work together—neither alone produces a reliable plan.
- Headroom is a variability absorber, not waste.
- Scaling units and cost belong in the same decision frame.
- Lead time determines how far ahead decisions must be made.
- Load test results override theoretical calculations when they disagree.

## Five Common Mistakes

1. **Replicating the past with no forecast.** Last quarter's peak is not next quarter's peak if the service is growing.
2. **Zero headroom.** Tight provisioning means every spike is an incident.
3. **Skipping load tests.** Paper throughput and real throughput often differ significantly.
4. **Ignoring lead time.** On-prem hardware can take weeks; the decision must happen that far ahead.
5. **Treating cost as a separate conversation.** If capacity reviews and budget reviews happen in different meetings, trade-offs cannot be made coherently.

## How This Shows Up in Production

A peak event like Black Friday is modeled months ahead: historical growth extrapolated, peak multiplier applied, load tested at projected peak, infrastructure pre-provisioned with headroom. The same model is reviewed quarterly to catch drift between forecast and reality.

## How a Senior Engineer Thinks

- Forecasts improve with iteration. Being wrong is normal; not feeding that error back into the next forecast is not.
- Headroom is insurance, and like all insurance it has a premium. The premium should be stated explicitly.
- Load tests belong on a schedule, not just before launch.
- Lead time shapes strategy: if hardware takes 4 weeks to arrive, the decision must happen 4+ weeks before the need.
- Cost is part of capacity, not a separate conversation. The team that says "we need 30 % more capacity" must also say what it costs.

## Checklist

- [ ] Demand forecast model exists and is reviewed monthly.
- [ ] Headroom policy and target utilization are defined.
- [ ] Load tests run on a regular schedule (not just pre-launch).
- [ ] Scaling unit and cost are reviewed together.
- [ ] Lead time factored into decision timing.

## Practice Problems

1. Explain why peak multiplier and headroom serve different purposes.
2. Given 1500 RPS today growing 10 %/month, calculate the target capacity in 3 months with 2.5x peak and 20 % headroom.
3. Describe a scenario where a load test result contradicts the capacity forecast, and explain which one should be trusted.

## Wrap-up and Next Steps

The final episode is *Building Operable Systems*—tying reliability, monitoring, automation, and response into a single design lens.

## Answering the Opening Questions

- **Why is capacity planning future demand forecasting, not past replication?**
  Capacity planning looks at current utilization and future growth rate together, predicting when limits will be reached—not simply provisioning what was used last quarter.
- **Why is headroom more like insurance than waste?**
  Headroom absorbs unexpected spikes, failover traffic, and forecast errors that would otherwise cause incidents. The cost is the premium; the protection is the value.
- **How does load testing calibrate prediction models?**
  Load tests reveal actual breaking points that may differ from theoretical calculations. When the test shows a bottleneck at 2500 RPS but the model assumed 3000 RPS, the test result corrects the model downward.

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
