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

This is post 8 in the Cloud Computing 101 series.

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

- **What boundary should you inspect first when applying Monitoring?**
  - The article treats Monitoring as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Monitoring?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Monitoring reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

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
