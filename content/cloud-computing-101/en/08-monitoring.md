---
series: cloud-computing-101
episode: 8
title: "Cloud Computing 101 (8/10): Monitoring"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Cloud
  - Monitoring
  - CloudWatch
  - AWS
  - Observability
seo_description: CloudWatch metrics, logs, and alarms — the foundation of cloud monitoring explained step by step with boto3 examples for beginners.
last_reviewed: '2026-05-14'
---

# Cloud Computing 101 (8/10): Monitoring

If you cannot see a system clearly, your customers end up doing the detection for you. A well-chosen alarm can turn a weekend outage into a short investigation, while a noisy dashboard can waste the same weekend in alert fatigue.

Metrics tell you what is happening (CPU, memory, requests). Logs tell you why (application events, errors). Traces show you how a request flowed through your system. Dashboards make patterns visible. Alerts wake you up. Together, they form the feedback loop that lets you operate a system.

This is the 8th post in the Cloud Computing 101 series.

In this post, we'll connect metrics, logs, traces, CloudWatch, and alert routing into one practical observability baseline.

> Monitoring works when numbers, events, and request flow answer different questions but reinforce one another during diagnosis.


![cloud computing 101 chapter 8 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/cloud-computing-101/08/08-01-concept-at-a-glance.en.png)
*cloud computing 101 chapter 8 flow overview*
> Good monitoring answers 'what is broken and where is the break' faster than the alternative: downtime without clues.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Monitoring?
- Which signal should the example or diagram make visible for Monitoring?
- What failure should be prevented first when Monitoring reaches a real system?

## Questions This Chapter Answers

- Metrics vs logs vs traces
- CloudWatch basics
- Alarms and notifications via SNS
- Building a dashboard
- Five common pitfalls

## Why It Matters

Without monitoring, your *customers* tell you about outages first. A single well-tuned alarm protects entire weekends.

## Key Terms

- **Metric**: a numeric time series (CPU, latency).
- **Log**: a text event (request, error).
- **Trace**: a distributed call flow (X-Ray).
- **Alarm**: notifies you when a threshold is crossed.
- **SLO**: a target, for example 99.9%.

## Before/After

**Before**: errors are discovered through customer complaints.

**After**: 5xx ratio above threshold pages Slack within minutes.

## Hands-on: CloudWatch Alarm

### Step 1 — Client

```python
import boto3
cw = boto3.client("cloudwatch")
sns = boto3.client("sns")
```

### Step 2 — Topic

```python
def create_topic(name):
    res = sns.create_topic(Name=name)
    return res["TopicArn"]
```

### Step 3 — Subscribe by email

```python
def subscribe(topic_arn, email):
    sns.subscribe(
        TopicArn=topic_arn, Protocol="email", Endpoint=email,
    )
```

### Step 4 — CPU alarm

```python
def cpu_alarm(name, instance_id, topic_arn):
    cw.put_metric_alarm(
        AlarmName=name,
        Namespace="AWS/EC2",
        MetricName="CPUUtilization",
        Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
        Statistic="Average",
        Period=60, EvaluationPeriods=5,
        Threshold=80.0, ComparisonOperator="GreaterThanThreshold",
        AlarmActions=[topic_arn],
    )
```

### Step 5 — Custom metric

```python
def emit(value):
    cw.put_metric_data(
        Namespace="MyApp",
        MetricData=[{"MetricName": "OrdersPerMin", "Value": value}],
    )
```

## What to Notice in This Code

- `Period` and `EvaluationPeriods` together set sensitivity.
- Custom metrics let you alert on business signals.
- Topics decouple alarms from recipients.

## How to Verify This Example

The interesting part of an alarm is not that it exists. It is whether you can explain exactly when it fires. Reading `Period`, `EvaluationPeriods`, and `Threshold` together is what separates a useful alarm from either noise or silence.

```bash
aws cloudwatch describe-alarms --alarm-names high-cpu-demo
```

**Expected output:**

- `MetricName` should be `CPUUtilization`.
- You should see `Period=60`, `EvaluationPeriods=5`, and `Threshold=80`.
- If the SNS email subscription was never confirmed, the alarm may exist while notifications still never reach a human.

### Where teams usually get stuck

- More alarms do not automatically create better observability. Unactionable alerts train teams to ignore the system.
- Log retention defaults can quietly turn into a cost problem.
- Infrastructure metrics alone can miss a business outage that is obvious in application signals.

## Five Common Mistakes

1. **Alarming on everything — alarm fatigue.**
2. **Logs without metrics.**
3. **Thresholds that are too sensitive or too dull.**
4. **Infinite log retention — costs grow forever.**
5. **Dashboards too cluttered to read at 3 a.m.**

## How This Shows Up in Production

ALB 5xx rate, RDS connections, Lambda error rate, and orders-per-minute all flow into a dashboard plus alarms plus Slack/PagerDuty.

## How a Senior Engineer Thinks

- Every alarm must be actionable.
- SLOs decide alarm thresholds.
- Logs are a question-answering tool, not a backup.
- Keep dashboards minimal.
- Run game days to verify alarms work.

## Checklist

- [ ] Alarms exist for core metrics.
- [ ] Log retention is configured.
- [ ] At least one operational dashboard.
- [ ] On-call notification path tested.

## Practice Problems

1. Explain the difference between a metric and a log in one line.
2. Write the `Period`/`EvaluationPeriods` for a "CPU 80% for 5 minutes" alarm.
3. Give one strategy to reduce alarm fatigue.

## Wrap-up and Next Steps

Once visibility is in place, you have to control the bill. The next post covers Cost Management.

## Answering the Opening Questions

- **What questions do metrics, logs, and traces each answer?**
  - Metrics answer "is the current state abnormal," logs answer "what exactly happened," and traces answer "where did it slow down." Combining all three covers both detection and root-cause analysis.
- **What baseline capabilities does CloudWatch provide?**
  - Metric collection and time-series storage, log groups and Insights queries, alarms with SNS integration, and dashboard visualization. Custom metrics extend coverage to business KPIs.
- **How are alarms connected to SNS notifications?**
  - Specifying an SNS Topic ARN in the alarm's `AlarmActions` publishes a message to the topic on threshold violation, which then fans out to subscribed email, Lambda, Slack, or other endpoints.

## Structured Logging

Unstructured logs are human-readable but machine-hostile. JSON structured logs enable per-field search and aggregation.

```json
{
  "timestamp": "2026-05-21T09:15:32.456Z",
  "level": "ERROR",
  "service": "order-api",
  "correlation_id": "req-abc-12345",
  "user_id": "u-98765",
  "message": "Payment gateway timeout",
  "duration_ms": 30012,
  "error_code": "PAYMENT_TIMEOUT",
  "upstream": "payment-service",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736"
}
```

Key fields explained:

- **correlation_id**: Propagated across services for a single request. Search by this ID to trace the full request journey.
- **trace_id**: Links to distributed tracing systems. Find this in logs, then open the trace in X-Ray or Jaeger directly.
- **duration_ms**: Numeric latency enables p50/p95/p99 percentile aggregation.
- **error_code**: Codified error types (vs. free-text messages) enable aggregation and alarm conditions.

Compare with the unstructured equivalent:

```text
2026-05-21 09:15:32 ERROR Payment gateway timeout for user u-98765 (took 30012ms)
```

Extracting `duration_ms > 5000` from the above requires regex parsing. With JSON logs, it's a single field query.

## Setting Up Alarms via CLI

Beyond the Python SDK, AWS CLI creates the same alarms — useful for quick validation before codifying infrastructure.

```bash
# Create SNS topic
aws sns create-topic --name high-cpu-alert

# Subscribe email (confirmation email required)
aws sns subscribe \
  --topic-arn arn:aws:sns:ap-northeast-2:123456789012:high-cpu-alert \
  --protocol email \
  --notification-endpoint ops-team@example.com

# Create CPU alarm
aws cloudwatch put-metric-alarm \
  --alarm-name high-cpu-demo \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --dimensions Name=InstanceId,Value=i-0abc123def456 \
  --statistic Average \
  --period 60 \
  --evaluation-periods 5 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --alarm-actions arn:aws:sns:ap-northeast-2:123456789012:high-cpu-alert
```

## Metric Query and Threshold Check Script

After setting alarms, periodically verify how close actual metrics are to thresholds. The script below queries the last hour of CPU utilization and classifies each data point.

```python
from datetime import datetime, timedelta, timezone
import boto3

cw = boto3.client("cloudwatch")


def get_cpu_stats(instance_id, hours=1):
    """Query CPU average/max at 5-min intervals for the last N hours."""
    end = datetime.now(timezone.utc)
    start = end - timedelta(hours=hours)

    response = cw.get_metric_statistics(
        Namespace="AWS/EC2",
        MetricName="CPUUtilization",
        Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
        StartTime=start,
        EndTime=end,
        Period=300,
        Statistics=["Average", "Maximum"],
    )
    return sorted(response["Datapoints"], key=lambda d: d["Timestamp"])


def check_threshold(datapoints, warn=60.0, critical=80.0):
    """Compare each data point's average against thresholds."""
    results = []
    for dp in datapoints:
        avg = dp["Average"]
        if avg >= critical:
            level = "CRITICAL"
        elif avg >= warn:
            level = "WARNING"
        else:
            level = "OK"
        results.append({
            "time": dp["Timestamp"].isoformat(),
            "avg": round(avg, 2),
            "max": round(dp["Maximum"], 2),
            "level": level,
        })
    return results


if __name__ == "__main__":
    instance_id = "i-0abc123def456"
    stats = get_cpu_stats(instance_id)
    for r in check_threshold(stats):
        print(f"[{r['level']:>8}] {r['time']}  avg={r['avg']}%  max={r['max']}%")
```

The key insight: `Period=300` (5-min aggregation) combined with warn/critical thresholds. In production, move this logic to Lambda and route results to Slack.

## Alert Fatigue Prevention

When alarms fire too frequently, teams start ignoring them. This is alert fatigue. To prevent real incidents from being buried, you need severity classification and routing rules.

### Severity Classification

| Severity | Definition | Response Time | Notification Channel | Example |
| --- | --- | --- | --- | --- |
| P1 (Critical) | Full service outage or data loss risk | Within 5 min | Phone + Slack + PagerDuty | 5xx rate exceeds 50% |
| P2 (High) | Partial functionality broken, users affected | Within 15 min | Slack + email | Payment failure rate > 5% |
| P3 (Medium) | Performance degradation, not immediate outage | Business hours | Slack channel | p95 latency > 2s |
| P4 (Low) | Informational, trend monitoring | Next business day | Dashboard only | Disk usage reaches 70% |

### Routing Rules

```yaml
alert_routing:
  p1_critical:
    channels: [pagerduty, slack-oncall, phone]
    escalation_after_min: 5
    auto_create_incident: true
  p2_high:
    channels: [slack-oncall, email]
    escalation_after_min: 15
    auto_create_incident: true
  p3_medium:
    channels: [slack-alerts]
    escalation_after_min: null
    auto_create_incident: false
  p4_low:
    channels: [dashboard-only]
    escalation_after_min: null
    auto_create_incident: false
```

### Practical Principles to Reduce Alert Fatigue

1. **Keep only actionable alarms.** If there's no clear action when an alarm fires, demote it to a dashboard metric.
2. **Run weekly alarm reviews.** Measure what percentage of alarms in the last 7 days led to actual action. Below 50% → adjust thresholds or delete.
3. **Apply grouping and deduplication.** If 10 alarms fire simultaneously from the same root cause, deliver one summary notification.
4. **Restrict off-hours alarms to P1/P2.** A P4 alarm at 3 AM only disrupts the on-call engineer's sleep.

## Dashboard Design Principles

A dashboard must let you assess service health within 30 seconds on one screen. Structure around Google SRE's Golden Signals to avoid missing essentials.

| Golden Signal | Measures | Dashboard Widget Example | Why It Matters |
| --- | --- | --- | --- |
| Latency | Request processing time | p50/p95/p99 time-series graph | Direct user-experience indicator |
| Traffic | Requests per second (RPS) | Real-time RPS counter | Load level and capacity headroom |
| Errors | Failed request rate | 5xx rate gauge + trend line | First signal of service health |
| Saturation | Resource utilization | CPU/memory/disk/connection pool | Trigger scale-up before hitting limits |

Common dashboard mistakes:

- Packing 20+ widgets so nothing is readable at a glance. 6–8 core widgets suffice.
- Showing only absolute values without trends. "CPU 45% now" is less useful than "rose from 30% to 45% over the last hour."
- Mixing business and infrastructure metrics on one board. Separate by audience: ops dashboard / business dashboard / capacity dashboard.

## Monitoring Cost Management

Monitoring is not free. As collected metrics and logs grow, so does the bill. "What to collect" matters as much as "what NOT to collect."

| Item | Collect | Caution / Skip |
| --- | --- | --- |
| Application error logs | Always | — |
| Business-critical metrics (orders, payments) | Always | — |
| Infrastructure basics (CPU, memory, network) | Always | — |
| DEBUG-level logs | Dev/staging only | Cost explosion risk in prod |
| Full HTTP request bodies | Only with special audit requirements | Storage cost + PII risk |
| Sub-second resolution metrics | Rare (real-time trading) | 60s resolution is enough for most |
| Health-check success logs | Skip | High volume, zero information value |

CloudWatch cost optimization tips:

- Set explicit retention per log group. Default is "never expire" — costs accumulate silently.
- Custom metrics are billed per `put_metric_data` call. Batch submissions reduce cost.
- Log filter metrics extract occurrence counts of specific patterns without storing full logs.

## Operational Alarm Design — Extended Example

Alarm quality matters more than quantity. The example below combines infrastructure and service signals into an actionable alerting system.

```bash
# AWS: check alarm/dashboard state
aws cloudwatch describe-alarms --state-value ALARM
aws cloudwatch get-dashboard --dashboard-name core-service-dashboard

# Azure Monitor: list metric alert rules
az monitor metrics alert list --resource-group rg-core-prod

# Google Cloud Monitoring: list alerting policies
gcloud alpha monitoring policies list --format="table(displayName,enabled)"
```

```hcl
resource "aws_cloudwatch_metric_alarm" "http_5xx_rate" {
  alarm_name          = "prod-http-5xx-rate-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "HTTPCode_Target_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  statistic           = "Sum"
  threshold           = 20
  alarm_description   = "5xx burst detection"
  treat_missing_data  = "notBreaching"
}
```

| Alarm Target | Example Metric | Recommended Threshold Approach |
| --- | --- | --- |
| Availability | 5xx rate | Dynamic baseline per traffic tier |
| Performance | p95 latency | SLO-based threshold |
| Capacity | CPU/memory | Factor in scale-up lead time |
| Business | Order failure rate | Cross-check with infra signals |

Text architecture diagram:
`App Metric/Log/Trace -> CloudWatch/Azure Monitor/Cloud Monitoring -> Alert Policy -> SNS/Email/ChatOps -> On-call Runbook`

Wiring this into your operations routine shifts from "investigate after failure" to "respond at the symptom stage." Maintain alarm rules, notification routes, and runbook links as a single unit.

<!-- toc:begin -->
## In this series

- [Cloud Computing 101 (1/10): What is Cloud Computing?](./01-what-is-cloud-computing.md)
- [Cloud Computing 101 (2/10): IaaS, PaaS, SaaS](./02-iaas-paas-saas.md)
- [Cloud Computing 101 (3/10): Region and Availability Zone](./03-region-and-availability-zone.md)
- [Cloud Computing 101 (4/10): Compute](./04-compute.md)
- [Cloud Computing 101 (5/10): Storage](./05-storage.md)
- [Cloud Computing 101 (6/10): Network](./06-network.md)
- [Cloud Computing 101 (7/10): Identity and Security](./07-identity-and-security.md)
- **Monitoring (current)**
- Cost Management (upcoming)
- Cloud Architecture Basics (upcoming)

<!-- toc:end -->

## References

- [AWS CloudWatch user guide](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/WhatIsCloudWatch.html)
- [CloudWatch Logs Insights](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/AnalyzingLogData.html)
- [AWS X-Ray](https://docs.aws.amazon.com/xray/latest/devguide/aws-xray.html)
- [Google SRE Book — Monitoring](https://sre.google/sre-book/monitoring-distributed-systems/)

Tags: Cloud, Monitoring, CloudWatch, AWS, Observability
