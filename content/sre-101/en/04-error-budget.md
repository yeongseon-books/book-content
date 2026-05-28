---
series: sre-101
episode: 4
title: "SRE 101 (4/10): Error Budget"
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
  - ErrorBudget
  - Reliability
  - Release
  - Risk
seo_description: A beginner-friendly guide to error budgets covering the definition, calculation, burn-rate alerting, release decisions, and operational policy
last_reviewed: '2026-05-14'
---

# SRE 101 (4/10): Error Budget

As soon as a team writes down an SLO, the next practical question shows up: how much failure are we willing to tolerate while we keep shipping changes? Without a clear answer, every incident becomes a fresh argument between "move faster" and "slow everything down."

The error budget is useful because it turns that argument into policy. It gives the team a shared number for how much reliability risk remains, and that number should change release behavior before emotions do.

This is the 4th post in the SRE 101 series. Here we connect SLO math to release policy, burn-rate alerting, and the day-to-day trade-off between stability work and product change.


![sre 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/sre-101/04/04-01-concept-at-a-glance.en.png)
*sre 101 chapter 4 flow overview*

## Questions to Keep in Mind

- Why does an error budget become the common language between speed and stability?
- How do you calculate the allowed failure from an SLO target?
- Why do total budget spend and burn rate answer different operating questions?

## Why this topic matters

Speed and stability are not enemies, but they do need a shared decision rule. Otherwise every outage triggers a different reaction depending on who is loudest in the room.

With a budget, the discussion becomes more precise. If the service still has room, the team can take measured risk. If the budget is burning too fast, stability work moves to the front of the queue.

The real strength of an error budget is not that it permits failure. It is that the team agrees in advance on how much failure is acceptable, which removes unnecessary debate. Within the budget, the team moves fast. When the budget is threatened, stability work takes priority automatically.

That makes the error budget both an operational metric and a cultural device. A team that asks "how much budget remains and what policy applies?" is calmer under pressure than one that asks "whose fault is this?"

## Mental model in one sentence

> An error budget is the allowed distance between the reliability goal and actual behavior — and it only matters if it changes release behavior.

## Key Terms

| Term | Meaning | Role in operations |
| --- | --- | --- |
| error budget | The amount of failure the target allows | Makes risk tolerance visible as a number |
| burn rate | The speed at which the budget is consumed | Acts as an early-warning signal |
| freeze | A halt on new releases or risky changes | Forces stability work when budget is near zero |
| window | The evaluation period for the budget | Anchors how spending is interpreted |
| policy | The action rules tied to budget state | Turns the number into behavior |

## Error budget scenarios

| Budget state | Spend ratio | Team behavior | Example |
| --- | --- | --- | --- |
| **Plenty** | < 50% | Ship aggressively, run experiments | 3 deploys/week, new API experiments |
| **Caution** | 50–80% | Extra review, stronger testing | Canary deploys, log audits |
| **Critical** | 80–100% | Freeze new features, prioritize stability | Hotfixes only, tech-debt reduction |
| **Exhausted** | ≥ 100% (SLO violated) | All deploys halted, postmortem required | Incident mode, exec escalation |

Like portfolio investing: when headroom is large you take risks; when you approach the limit you manage tightly. If the whole team agrees on these thresholds in the next retrospective, decision cost drops dramatically.

## Why cumulative spend alone is not enough

Monthly budget may look healthy overall, yet the last hour might be burning at 10x normal rate. Cumulative spend shows how much has been used; burn rate shows how fast things are getting worse right now. One is a gauge, the other is a warning light. You need both.

## Operating the budget step by step

### Step 1 — Compute the budget

```python
def budget(target, total):
    return (1 - target) * total
```

If the SLO is 99.9%, then 0.1% of requests are allowed to fail. The moment you can calculate this, reliability stops being aspirational and becomes an operational number.

### Step 2 — Spend ratio

```python
def spent(errors, allowed):
    return errors / allowed
```

Shows what fraction of the budget has been consumed so far. More useful than single-incident severity because it reveals the cumulative trend direction.

### Step 3 — Burn rate

```python
def burn_rate(errors_in_h, allowed_per_h):
    return errors_in_h / allowed_per_h
```

Burn rate reveals how fast the budget is melting in a short window. Even if cumulative spend is low, a high current rate may signal an emerging major incident.

### Step 4 — Policy branch

```python
def policy(spent_ratio):
    if spent_ratio > 1.0:
        return "freeze"
    if spent_ratio > 0.5:
        return "review"
    return "ship"
```

Numbers alone do not change behavior. You need pre-agreed thresholds for when to review and when to freeze. That way the team does not re-debate from scratch during every incident.

### Step 5 — Early warning alert

```python
def alert(burn):
    return burn > 14.4  # 14.4x: fast burn
```

A speed-based alert catches problems early. The exact threshold varies by organization, but without one, large incidents announce themselves only after significant budget is already gone.

## Full budget calculation example

When you have the SLO and request count, you can compute budget, current state, and remaining headroom in one function:

```python
def calculate_error_budget(total_requests, target_availability, current_errors):
    """
    Compute error budget and analyze current state.
    """
    allowed_errors = total_requests * (1 - target_availability)
    remaining_errors = allowed_errors - current_errors
    spent_ratio = current_errors / allowed_errors if allowed_errors > 0 else 0

    return {
        "allowed_errors": allowed_errors,
        "current_errors": current_errors,
        "remaining_errors": remaining_errors,
        "spent_ratio": spent_ratio,
        "status": get_status(spent_ratio),
    }

def get_status(spent_ratio):
    if spent_ratio >= 1.0:
        return "EXHAUSTED"
    elif spent_ratio >= 0.8:
        return "CRITICAL"
    elif spent_ratio >= 0.5:
        return "WARNING"
    else:
        return "HEALTHY"

# 30-day window: 1M requests, 99.9% target, 800 errors so far
result = calculate_error_budget(1_000_000, 0.999, 800)
print(f"Allowed errors : {result['allowed_errors']}")
print(f"Current errors : {result['current_errors']}")
print(f"Remaining      : {result['remaining_errors']}")
print(f"Spent ratio    : {result['spent_ratio']*100:.1f}%")
print(f"Status         : {result['status']}")
```

Output:

```
Allowed errors : 1000.0
Current errors : 800
Remaining      : 200.0
Spent ratio    : 80.0%
Status         : CRITICAL
```

One function summarizes the budget state: allowed, consumed, remaining, and status. Operational decisions speed up when this view is always one query away.

## Burn-rate alerting design

Simple error-rate thresholds fire too late or too early. Burn-rate alerts ask a better question: at the current pace, will we exhaust the budget before the window ends?

### Burn rate values

- burn rate = 1: consuming exactly on pace (budget empties on the last day of the window)
- burn rate = 2: twice the pace (empties at day 15)
- burn rate = 14.4: very fast (empties in ~2 days)

### PromQL multi-window alerts (Google SRE Workbook pattern)

```promql
# Fast burn: 14.4x over 1-hour window
(
  sum(rate(http_requests_total{status=~"5..",service="payments"}[1h]))
  /
  sum(rate(http_requests_total{service="payments"}[1h]))
) > (14.4 * 0.001)

# Slow burn: 6x over 6-hour window
(
  sum(rate(http_requests_total{status=~"5..",service="payments"}[6h]))
  /
  sum(rate(http_requests_total{service="payments"}[6h]))
) > (6 * 0.001)
```

### Alert hierarchy in Prometheus

```yaml
groups:
  - name: error_budget_burn
    rules:
      - alert: ErrorBudgetFastBurn
        expr: |
          (
            sum(rate(http_requests_total{status=~"5.."}[1h]))
            / sum(rate(http_requests_total[1h]))
          ) > (14.4 * 0.001)
        for: 2m
        labels:
          severity: page
        annotations:
          summary: "Error budget burning at 14.4x (exhausts in ~2 days)"
          runbook: "https://wiki.internal/runbooks/error-budget-fast-burn"

      - alert: ErrorBudgetSlowBurn
        expr: |
          (
            sum(rate(http_requests_total{status=~"5.."}[6h]))
            / sum(rate(http_requests_total[6h]))
          ) > (6 * 0.001)
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "Error budget burning at 6x (exhausts in ~5 days)"
```

Fast burn catches sudden large incidents; slow burn catches gradual quality degradation. Using both means neither sharp spikes nor slow drifts go unnoticed.

## Budget burn simulation

Seeing how the budget behaves day-by-day makes burn rate concrete:

```python
def simulate_budget_burn(
    total_requests_per_day,
    target_availability,
    window_days,
    daily_error_rates,
):
    """
    Simulate error budget consumption over time.
    daily_error_rates: list of per-day error ratios.
    """
    total_requests = total_requests_per_day * window_days
    total_budget = total_requests * (1 - target_availability)

    cumulative_errors = 0
    daily_report = []

    for day, error_rate in enumerate(daily_error_rates, 1):
        daily_errors = total_requests_per_day * error_rate
        cumulative_errors += daily_errors
        spent_ratio = cumulative_errors / total_budget

        daily_report.append({
            "day": day,
            "daily_error_rate": f"{error_rate*100:.3f}%",
            "cumulative_errors": int(cumulative_errors),
            "budget_spent": f"{spent_ratio*100:.1f}%",
            "status": get_status(spent_ratio),
        })

    return daily_report

# Scenario: 1M requests/day, 99.9% target, 30-day window
# First 5 days normal, day 6 incident, then elevated errors
daily_rates = [0.0005] * 5 + [0.005] + [0.001] * 4 + [0.0005] * 20

report = simulate_budget_burn(
    total_requests_per_day=1_000_000,
    target_availability=0.999,
    window_days=30,
    daily_error_rates=daily_rates,
)

print(f"{'Day':<5} {'Error Rate':<12} {'Cumul Errors':<14} {'Budget':<10} {'Status'}")
print("-" * 55)
for r in report[:10]:
    print(f"{r['day']:<5} {r['daily_error_rate']:<12} {r['cumulative_errors']:<14} {r['budget_spent']:<10} {r['status']}")
```

Output:

```
Day   Error Rate   Cumul Errors   Budget     Status
-------------------------------------------------------
1     0.050%       500            1.7%       HEALTHY
2     0.050%       1000           3.3%       HEALTHY
3     0.050%       1500           5.0%       HEALTHY
4     0.050%       2000           6.7%       HEALTHY
5     0.050%       2500           8.3%       HEALTHY
6     0.500%       7500           25.0%      HEALTHY
7     0.100%       8500           28.3%      HEALTHY
8     0.100%       9500           31.7%      HEALTHY
9     0.100%       10500          35.0%      HEALTHY
10    0.100%       11500          38.3%      HEALTHY
```

Day 6's incident (0.5% error rate) burns 16.7% of the budget in a single day — that is 10 normal days' worth of budget consumed in 24 hours. This is why burn rate alerting catches things that cumulative dashboards miss.

## Release decision function

Connecting budget state to release gates removes the "should we deploy?" argument:

```python
def release_decision(budget_spent_pct, burn_rate, change_risk):
    """
    Release gate based on budget state.
    change_risk: 'low', 'medium', 'high'
    """
    # Budget exhausted: block everything except rollbacks
    if budget_spent_pct >= 100:
        return {
            "decision": "BLOCK",
            "reason": "Budget exhausted — stability work only",
            "allowed": ["hotfix", "rollback"],
        }

    # Budget critical: block high-risk changes
    if budget_spent_pct >= 80:
        if change_risk == "high":
            return {
                "decision": "BLOCK",
                "reason": "Critical budget zone — high-risk blocked",
                "allowed": ["hotfix", "low-risk config"],
            }
        return {
            "decision": "REVIEW",
            "reason": "Critical budget zone — extra review required",
            "required": ["SRE approval", "canary at 1%"],
        }

    # Budget warning: strengthen review
    if budget_spent_pct >= 50:
        return {
            "decision": "REVIEW",
            "reason": "Half budget consumed — review strengthened",
            "required": ["peer review", "canary at 5%"],
        }

    # Budget healthy: ship normally
    return {
        "decision": "APPROVE",
        "reason": "Budget healthy — normal deployment",
        "required": ["standard review"],
    }

# Examples
print(release_decision(45, 1.2, "medium"))
print(release_decision(82, 3.0, "high"))
print(release_decision(100, 14.4, "low"))
```

The function is simple but shows the key principle: if the error budget is not connected to decision rules, it is just an observation metric. The team needs budget state to automatically change what deployments are allowed.

## Dashboard design

An effective error budget dashboard answers one question: "Can we deploy right now?"

| Panel | Content | Format |
| --- | --- | --- |
| Budget remaining | Error budget left (%) | Gauge (green → yellow → red) |
| Spend trend | 30-day cumulative spend graph | Time series + target line |
| Burn rate | Current consumption speed (1h, 6h windows) | Stat (1x, 2x, 14.4x) |
| Policy state | Currently active release policy | Text (SHIP / REVIEW / FREEZE) |
| Recent deploys | Deploy timestamps with post-deploy error change | Annotations + overlay |

```promql
# Budget remaining calculation (Grafana variable)
1 - (
  sum(increase(http_requests_total{status=~"5..",service="$service"}[30d]))
  /
  (sum(increase(http_requests_total{service="$service"}[30d])) * (1 - $target))
)
```

More graphs does not mean a better dashboard. A good dashboard shows only what is needed to make a deployment decision.

## Team collaboration around the budget

The error budget is not an SRE-only metric. It reaches full effectiveness when product, engineering, and leadership all look at the same number.

**With the product team:** When budget is healthy, you can say "experiments are safe right now" with data. When budget is low, you can propose "let's stabilize this week and ship next week" with evidence instead of opinion.

**With the engineering team:** If burn rate climbs after a deploy, that deploy is the likely cause. Engineers can decide quickly to rollback or hotfix, without emotional escalation.

**With leadership:** Executives want to know "is the service reliable enough?" Including budget achievement in monthly reports shows the return on reliability investment quantitatively.

## Error budget policy template

To make the budget operational rather than informational, the team needs a written policy. Here is a starter template:

```yaml
team: payments-api
slo:
  target: 99.9%
  window: 30d
  sli: http_success_ratio

error_budget:
  allowed_errors_per_month: 1000

policy:
  - condition: spent < 50%
    action: SHIP
    description: Normal deployments, experiments allowed
    approval: team lead

  - condition: spent >= 50% and spent < 80%
    action: REVIEW
    description: All deploys require SRE review, canary mandatory
    approval: SRE + team lead

  - condition: spent >= 80%
    action: FREEZE
    description: New features blocked, hotfix and stability only
    approval: VP Engineering

  - condition: slo_violated (spent >= 100%)
    action: INCIDENT
    description: Incident mode, postmortem required, prevention plan
    approval: executive report

alerts:
  - type: burn_rate
    threshold: 14.4
    window: 1h
    description: Page on-call when 14.4x for 1 hour

  - type: cumulative
    threshold: 80%
    description: Notify entire team at 80% cumulative spend

review_schedule:
  - frequency: weekly
    participants: [team-lead, sre, product]
    agenda: [budget status, burn rate trends, 2-week risk forecast]
```

Adapt this to your team's context. The important elements are: per-threshold actions, approval chains, alert criteria, and a regular review cadence. With all four, the budget drives behavior instead of sitting in a document.

## Checklist

- [ ] Error budget is computed from the SLO.
- [ ] Both cumulative spend and burn rate are tracked.
- [ ] Review and freeze policies are documented with thresholds.
- [ ] Budget state is wired into actual release decisions.
- [ ] Budget is used as a decision tool, not a blame tool.

## Practice Problems

1. Your SLO is 99.95% over 30 days with 2M requests/day. Calculate the monthly error budget in request count and minutes of downtime.
2. After a deploy, error rate jumps from 0.02% to 0.8% for 3 hours. How much budget does this consume? Should the next planned deploy proceed?
3. Draft a one-page error budget policy for your team including thresholds, actions, and review cadence.

## Wrap-up and Next Steps

Next, we cover monitoring — how to decide which signals need watching, and how to read system health without drowning in alert noise.

## Answering the Opening Questions

- **Why does error budget become a shared language between velocity and stability?**
  Error budget converts the abstract tension between "ship faster" and "don't break things" into a concrete number both sides can reference. When budget remains, teams can ship aggressively; when it's depleted, stability work takes priority—same metric, same decision framework.
- **How do you calculate the allowed failure from an SLO target?**
  If your SLO is 99.9% availability over 30 days, the error budget is 0.1% × 30 days × daily request volume = the allowed number of failed requests. Dividing budget into time slices gives spending rate and lets you compare planned deployments against remaining headroom.
- **Why do cumulative burn and burn rate answer different questions?**
  Cumulative burn shows total budget consumed so far — useful for monthly reviews and trend analysis. Burn rate shows how fast you're consuming right now — useful for alerting and immediate response. A high burn rate with plenty of remaining budget triggers a different response than a low burn rate near exhaustion.

<!-- toc:begin -->
## In this series

- [SRE 101 (1/10): What is SRE?](./01-what-is-sre.md)
- [SRE 101 (2/10): Reliability](./02-reliability.md)
- [SRE 101 (3/10): SLI, SLO, SLA](./03-sli-slo-sla.md)
- **Error Budget (current)**
- Monitoring (upcoming)
- Incident Response (upcoming)
- Postmortem (upcoming)
- Reducing Toil (upcoming)
- Capacity Planning (upcoming)
- Building Operable Systems (upcoming)

<!-- toc:end -->

## References

- [Embracing Risk - Google SRE Book](https://sre.google/sre-book/embracing-risk/)
- [Alerting on SLOs - Google SRE Workbook](https://sre.google/workbook/alerting-on-slos/)
- [Error Budgets - Atlassian](https://www.atlassian.com/incident-management/kpis/error-budget)
- [Error Budget Policy - Google](https://sre.google/workbook/error-budget-policy/)

Tags: SRE, ErrorBudget, Reliability, Release, Risk
