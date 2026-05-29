---
series: observability-101
episode: 7
title: "Observability 101 (7/10): Alerts and On-Call"
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
  - Alerting
  - SRE
  - OnCall
  - Monitoring
seo_description: What makes an alert worth a 3am page, how to avoid alert fatigue, and the first steps of running on-call sustainably.
last_reviewed: '2026-05-15'
---

# Observability 101 (7/10): Alerts and On-Call

More alerts do not make a system safer by default. Once the team stops trusting the pager, even the alert that matters most arrives already discounted.

That is why alerting design is partly a technical problem and partly a human one. It spends sleep, focus, and trust, so it must be tied to user impact and clear action.

This is the 7th post in the Observability 101 series.


![observability 101 chapter 7 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/observability-101/07/07-01-concept-at-a-glance.en.png)
*observability 101 chapter 7 flow overview*
> Alerts and On-Call is about the boundary decision, not the tool choice.

## Questions to Keep in Mind

- What conditions should an alert meet to justify waking someone at night?
- Why does alert fatigue develop and how can it be reduced?
- How do symptom-based and cause-based alerts differ?

## Why It Matters

Too many alerts *bury* the real signal. On-call *buys sleep* and *spends willpower*. Design is cost.

> *Alerts have a wake-up cost. If you do not know it, you go bankrupt.*

Observability is the ability to understand a system's internal state from external signals. In a distributed system, you cannot instrument every line of code. You rely on *metrics* (what happened), *logs* (why it happened), and *traces* (where it happened).

## Severity Criteria

Not all alerts deserve the same treatment. Separating what needs immediate response from what can wait until morning is what makes on-call sustainable.

| Severity | Response Time | Escalation | Example |
| --- | --- | --- | --- |
| P1 (Critical) | Within 15 min | Team lead at 30 min, exec at 1 hr | Payment service down, data breach |
| P2 (High) | Within 30 min | Team lead at 1 hr | Specific API 5xx > 5% |
| P3 (Medium) | Within 4 hrs | None | Disk usage 80% |
| P4 (Low) | Business hours | None | Log volume growth trend |

Only P1 and P2 wake someone at night. P3 goes to a Slack channel. P4 becomes a daily ticket. The exact thresholds vary by team, but the baseline is always user impact and business loss.

## Key Terms

- **Alert rule**: a condition plus a *duration*.
- **Severity**: *page* vs *ticket*.
- **Routing**: who receives it.
- **Silence**: temporary *suppression*.
- **Runbook**: an *action manual* for the alert.

## Before/After

**Before**: 50 alerts/day, all ignored. Most are brief spikes that disappear or known cause signals. The real outage *gets missed* in the noise.

**After**: 3 alerts/week, *all actionable*. Only symptom alerts with user impact remain as pages; the rest become tickets or chat messages. Alert count drops but trust rises.

## Hands-on: Alerts in 5 Steps

### Step 1 — Prometheus alert rule

```yaml
groups:
  - name: api
    rules:
      - alert: HighErrorRate
        expr: sum(rate(http_requests_total{status=~"5.."}[5m]))
              / sum(rate(http_requests_total[5m])) > 0.05
        for: 10m
        labels: { severity: page }
        annotations:
          summary: "5xx > 5% for 10m"
          runbook: "https://wiki/runbook/api-error"
```

A good first alert is a symptom alert tied to user impact. Error rate — immediately felt by users — is especially appropriate.

### Step 2 — `for` clause to prevent flap

```yaml
for: 10m   # too short and noise explodes
```

Without a duration, every brief spike fires an alert. `for` is the first filter that removes flapping and keeps only sustained problems.

### Step 3 — Split severity

```yaml
labels:
  severity: page    # wakes you up
  # severity: ticket # business hours
```

If every alert wakes someone, the system breaks quickly. Separating immediate response from business-hours handling is what keeps on-call viable.

### Step 4 — Alertmanager routing

```yaml
route:
  receiver: default
  routes:
    - match: { severity: page }
      receiver: pagerduty
    - match: { severity: ticket }
      receiver: slack-ops
```

An alert must have a clear recipient. When the receiver is ambiguous, nobody takes responsibility.

### Step 5 — Runbook link

```text
Every alert MUST have a runbook URL.
The runbook covers: meaning, first 3 actions, escalation, related dashboards.
```

If you do not write down the first three actions after the alert fires, the responder has to think from scratch every time. An alert without a runbook is more dangerous than a runbook without an alert.

### Alert Rule Pseudocode

Expressing alert rules as code makes the logic clearer.

```python
def evaluate_alert_rule(metrics, threshold, duration):
    """
    Alert rule evaluation logic.
    metrics: list of time-series data points
    threshold: threshold value
    duration: for clause duration
    """
    breaches = []
    for point in metrics:
        if point.value > threshold:
            breaches.append(point.timestamp)
        else:
            breaches.clear()  # Reset if value drops below threshold

    if len(breaches) > 0:
        first_breach = breaches[0]
        last_breach = breaches[-1]
        if (last_breach - first_breach) >= duration:
            return "FIRING", first_breach
    return "OK", None

# Usage
result, since = evaluate_alert_rule(
    error_rate_samples,
    threshold=0.05,
    duration=timedelta(minutes=10)
)
if result == "FIRING":
    send_alert(severity="page", since=since)
```

This logic mirrors the Prometheus rule engine. Values above threshold accumulate; dropping below resets; once the `for` duration is met, the state becomes FIRING.

## Reducing Alert Fatigue

Alert fatigue is the state where responders no longer trust alerts. Three techniques reduce it:

**Grouping**

Bundle similar alerts into one notification. If three services on the same host fail simultaneously, send one grouped alert instead of three. Alertmanager's `group_by` automates this.

```yaml
route:
  group_by: ["instance", "severity"]
  group_wait: 30s
  group_interval: 5m
```

**Inhibition**

A parent failure suppresses child alerts. When the network is down, every service reports failure — network alert inhibits the rest.

```yaml
inhibit_rules:
  - source_match: { alertname: NetworkDown }
    target_match: { severity: warning }
    equal: ["instance"]
```

**Silencing**

Manually suppress known issues or maintenance windows. PagerDuty and Alertmanager let you specify a time range to stop specific alerts.

```bash
amtool silence add alertname=DiskFull instance=node01 \
  --duration=2h \
  --comment="Disk cleanup in progress"
```

Using all three together drastically reduces the fatigue of receiving the same error repeatedly.

## Alertmanager and PagerDuty Integration

A mature alerting system does not stop at "it fires." Who receives it, how quickly they must respond, and where it escalates on failure must all be defined.

```yaml
route:
  receiver: slack-default
  group_by: ["alertname", "service", "severity"]
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 2h
  routes:
    - matchers:
        - severity="page"
      receiver: pagerduty-critical
    - matchers:
        - severity="ticket"
      receiver: opsgenie-warning

receivers:
  - name: pagerduty-critical
    pagerduty_configs:
      - routing_key: "PD_ROUTING_KEY"
        severity: "critical"
        description: "{{ .CommonAnnotations.summary }}"

  - name: opsgenie-warning
    opsgenie_configs:
      - api_key: "OPS_GENIE_KEY"
        priority: "P3"

  - name: slack-default
    slack_configs:
      - channel: "#ops-alerts"
        send_resolved: true
```

The key insight: the severity label *is* the routing policy. Overusing `severity=page` leaves wake-up cost uncontrolled. Using only `severity=ticket` means critical outages get missed.

## On-Call Rotation and Escalation

| Stage | Response Time | Owner | On Failure |
| --- | --- | --- | --- |
| Primary on-call | 15 min | Weekly primary | Escalate to secondary |
| Secondary on-call | 20 min | Weekly secondary | Escalate to team lead |
| Team lead | 30 min | Service owner | Switch to incident command |
| Incident commander | Immediately | IC | Begin business communication |

Without a standard escalation policy, responsibility boundaries blur when incidents grow. Especially at night, decision-makers join late and recovery time lengthens. Manage escalation stages by *role*, not name, so the policy survives rotation changes.

### Rotation and Compensation

On-call is labor and needs clear rotation and compensation.

**Rotation policy:**
- Primary on-call: weekly half, including weekends (7 days)
- Secondary on-call: escalation if primary does not respond within 30 min
- Handoff: Friday 5 PM after weekly retrospective
- Rest: the week after on-call is rest week

**Compensation:**
- Base: 1 additional day off per on-call week
- Incident response: 0.5 day off for responses exceeding 1 hour
- Night/weekend: 1.5× for incidents after 11 PM or on weekends

Details vary by team, but the shared principle is "on-call is labor." A structure where one person rotates continuously without breaks does not last.

## Multi-Window Burn Rate Alerts

The core of SLO-based alerting is detecting error budget consumption speed. "Error rate > 5%" is less precise than "error budget is being consumed 14× faster than expected."

```yaml
groups:
  - name: slo-burn-rate
    rules:
      # Fast burn (1h window): burn rate 14x → immediate page
      - alert: SLOBurnRateFast
        expr: |
          (
            sum(rate(http_requests_total{status=~"5..",service="checkout"}[1h]))
            / sum(rate(http_requests_total{service="checkout"}[1h]))
          ) > (14 * 0.001)
        for: 2m
        labels:
          severity: page
        annotations:
          summary: "checkout SLO burn rate 14x (1h window)"
          runbook: "https://wiki/runbook/slo-burn"

      # Slow burn (6h window): burn rate 6x → ticket
      - alert: SLOBurnRateSlow
        expr: |
          (
            sum(rate(http_requests_total{status=~"5..",service="checkout"}[6h]))
            / sum(rate(http_requests_total{service="checkout"}[6h]))
          ) > (6 * 0.001)
        for: 30m
        labels:
          severity: ticket
        annotations:
          summary: "checkout SLO burn rate 6x (6h window)"
```

Multi-window approach explained:

| Window | Burn Rate Threshold | Meaning | Response |
| --- | --- | --- | --- |
| 1 hour | 14× | 30-day budget exhausted in 2 days | Immediate page |
| 6 hours | 6× | 30-day budget exhausted in 5 days | Business-hours ticket |
| 3 days | 1× | Consumption speed normal | Monitoring only |

This approach beats simple thresholds because it connects directly to SLOs, letting you explain "why this alert matters" in business language.

## Runbook Writing Guide

A runbook documents the first actions within 3 minutes of receiving an alert. A good runbook structure:

```markdown
# [P1] Payment API 5xx > 5%

## Meaning
Payment API 5xx responses exceeded 5% of total requests over 5 minutes.
Users are experiencing payment failures.

## First 3 Things to Check
1. Check error rate pattern on Grafana payment API dashboard
2. Query Loki: `{app="payment"} |= "error" | json | status >= 500`
3. Check for recent deploys in Slack #deploy channel (last 10 min)

## First Actions
- If 5xx concentrates on specific endpoint → drill down logs for that endpoint
- If timing overlaps with recent deploy → consider rollback
- If DB connection pool exhaustion → temporarily increase connection limit

## Escalation
If not resolved within 30 min, escalate to payment team lead (Slack @payment-lead)

## Related Links
- Dashboard: https://grafana/d/payment
- Logs: https://grafana/explore?loki
- Postmortem template: https://wiki/postmortem
```

Every alert must have a runbook, and it must be concrete enough for a first-time responder to execute immediately.

## Incident Response Timeline Example

```text
T+0m   PagerDuty alert received (SLOBurnRateFast)
T+2m   Primary on-call acknowledges, opens Grafana dashboard
T+5m   Payment API /checkout endpoint 5xx concentration confirmed
T+7m   Loki logs show "connection pool exhausted"
T+10m  DB connection limit increased 50 → 100 (temporary mitigation)
T+12m  Error rate returns to normal
T+15m  Situation summary shared in Slack #incidents
T+30m  Root cause investigation begins (suspected connection leak)
T+2h   Fix deployed, connection pool restored to original value
T+24h  Postmortem completed
```

Three key points in this timeline:

1. **Acknowledged within T+2m**: MTTA under 2 minutes means the escalation policy is working.
2. **Mitigation at T+10m**: Stop user impact first, even if the root cause is not yet found.
3. **Postmortem at T+24h**: Document root cause and prevention to avoid repeat incidents.

## Alert Rule Test Automation

Alert rules, like code, can be tested. Prometheus supports rule testing via `promtool`.

```yaml
# tests/alert_rules_test.yaml
rule_files:
  - ../rules/api_alerts.yaml

evaluation_interval: 1m

tests:
  - interval: 1m
    input_series:
      - series: 'http_requests_total{status="500",service="checkout"}'
        values: "0+10x20"  # Increases by 10 every minute for 20 minutes
      - series: 'http_requests_total{status="200",service="checkout"}'
        values: "0+100x20"
    alert_rule_test:
      - eval_time: 15m
        alertname: HighErrorRate
        exp_alerts:
          - exp_labels:
              severity: page
            exp_annotations:
              summary: "5xx > 5% for 10m"
```

```bash
# Run in CI
promtool test rules tests/alert_rules_test.yaml
```

This test verifies "when error rate is 10%, does HighErrorRate fire at the 15-minute mark?" Including this in CI prevents false alarms when rules change.

## Alert Quality Metrics

Alerts themselves need quality measurement to improve. Review these metrics weekly to manage alert fatigue quantitatively.

| Metric | Target | Action When Exceeded |
| --- | --- | --- |
| Weekly page alert count | ≤ 5 | Rule tuning or automation review |
| False alarm ratio | ≤ 20% | Adjust `for`, revisit thresholds |
| Runbook-less alert ratio | 0% | Require runbook before new alert approval |
| MTTA (mean time to acknowledge) | ≤ 5 min | Review routing/escalation |
| MTTR (mean time to resolve) | ≤ 1 hr (P1) | Improve runbooks, consider auto-recovery |

High false alarm ratio means rules are too sensitive. High MTTA means routing or escalation is weak. Managing these as SLOs for the alerting system itself reduces on-call fatigue over time.

Visualize these on a Grafana dashboard to create a meta-dashboard for the health of the alerting system itself. "Alerts that observe the alerting system" are a sign of operational maturity.

## How to Check Alert Quality

Before adding a new page-level alert, replay it against recent data and verify that a human should actually receive it.

```text
1) Replay the rule against the last 30 days.
2) Confirm that the `for` clause filters short spikes.
3) Verify every `severity=page` rule has a runbook and owner.
4) Trigger a test event and confirm routing to PagerDuty or chat.
```

```text
Expected output:
- Page-level alerts stay rare enough that responders still trust them.
- Ticket-level alerts land in business-hours channels only.
- Every alert message includes summary, owner, and runbook context.
```

## What to Notice in This Code

- `for: 10m` enforces a *duration condition*.
- The `severity` label decides *behavior*.
- An alert without a *runbook* is *half-built*.

## Five Common Mistakes

1. **Every alert is a *page*.** Nights become *hell*.
2. **Alerting only on *cause*.** Disconnected from *user impact*.
3. **No `for` clause.** *Flapping* explodes noise.
4. **No *runbook*.** The receiver *freezes*.
5. **No owner.** Everyone's alert = *no one's alert*.

## How This Shows Up in Production

Strong teams establish symptom alerts first. SLO breaches, high error rates, long latency — signals connected to user experience come first. Cause alerts like CPU 95% serve as backup for drill-down.

On-call is treated as labor. Rotation, compensation, handoffs, runbooks, and alert quality reviews must all exist for long-term operation. Alerting design is ultimately about protecting people.

## How a Senior Engineer Thinks

- *Delete alerts that are not actionable.*
- *Symptom > cause. SLO is the standard.*
- *The cost of a page is sleep.*
- *On-call is labor and deserves compensation.*
- *Alerts without a runbook are retired immediately.*

## Checklist

- [ ] Each alert has a *runbook link*.
- [ ] Severity splits into *page/ticket*.
- [ ] `for` is set.
- [ ] On-call *rotation* is in place.

## Practice Problems

1. Write one alert for an SLO breach.
2. Identify one *symptom* alert and one *cause* alert.
3. Write a one-page runbook.

## Wrap-up and Next Steps

Good alerts *protect sleep*. Next: *SLI and SLO basics*.

## Answering the Opening Questions

- **What conditions should an alert meet to justify waking someone at night?**
  - All three must hold: (1) user impact is ongoing, (2) damage grows without immediate action, (3) auto-recovery is impossible. If any one is missing, downgrade to ticket severity.
- **Why does alert fatigue develop and how can it be reduced?**
  - Fatigue starts with low confidence — accumulated false alarms train people to ignore alerts. Solutions: reduce duplicates via grouping, inhibition, and silencing; filter momentary spikes with `for` duration; review weekly false-alarm ratios.
- **How do symptom-based and cause-based alerts differ?**
  - Symptom alerts detect "problems users experience" (5xx spike, latency rise). Cause alerts detect "internal system state" (CPU 95%, disk 90%). Night pages should center on symptom alerts; cause alerts are for drill-down and tickets.
<!-- toc:begin -->
## In this series

- [Observability 101 (1/10): What Is Observability?](./01-what-is-observability.md)
- [Observability 101 (2/10): Metrics, Logs, and Traces](./02-metric-log-trace.md)
- [Observability 101 (3/10): Collecting and Visualizing Metrics](./03-metric-collection.md)
- [Observability 101 (4/10): Structured Logging](./04-structured-logging.md)
- [Observability 101 (5/10): Distributed Tracing Basics](./05-distributed-tracing.md)
- [Observability 101 (6/10): Dashboard Design](./06-dashboard-design.md)
- **Alerts and On-Call (current)**
- SLI and SLO Basics (upcoming)
- Cost and Cardinality (upcoming)
- A Production-Ready Observability Stack (upcoming)

<!-- toc:end -->

## References

- [Google SRE — Alerting](https://sre.google/sre-book/practical-alerting/)
- [Prometheus alerting rules](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/)
- [Alertmanager docs](https://prometheus.io/docs/alerting/latest/alertmanager/)
- [On-call principles](https://increment.com/on-call/when-the-pager-goes-off/)

Tags: Observability, Alerting, SRE, OnCall, Monitoring
