---
series: cloud-computing-101
episode: 9
title: "Cloud Computing 101 (9/10): Cost Management"
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
  - FinOps
  - Cost
  - AWS
  - Architecture
seo_description: Tags, budgets, Savings Plans, and rightsizing — the FinOps fundamentals every cloud engineer needs, taught with boto3 examples.
last_reviewed: '2026-05-14'
---

# Cloud Computing 101 (9/10): Cost Management

Cloud lets you create infrastructure quickly, which also means you can create cost quickly. Surprise invoices are common not because the cloud is mysterious, but because visibility, ownership, and cleanup policies were weak from the start.

Cloud cost is not a single number; it is a sum of on-demand rates, reserved discounts, spot prices, storage tiers, data transfer charges, and managed service premiums. Without tagging and analysis, you cannot answer 'who spent what and why.' Without budgets, costs surprise you.

This is the 9th post in the Cloud Computing 101 series.

In this post, we'll use tags, budgets, Savings Plans, and rightsizing as a practical framework for engineering-led cost control.

> FinOps starts with visibility, not discounts. Make cost attributable first, then automate alerts, commitments, and cleanup around real usage patterns.


![cloud computing 101 chapter 9 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/cloud-computing-101/09/09-01-concept-at-a-glance.en.png)
*cloud computing 101 chapter 9 flow overview*
> Cost control is not about spending less. It is about spending intentionally and knowing where your money goes.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Cost Management?
- Which signal should the example or diagram make visible for Cost Management?
- What failure should be prevented first when Cost Management reaches a real system?

## Questions This Chapter Answers

- Cloud cost basics
- Cost allocation through tags
- Budget alerts
- Savings Plans and Reserved Instances
- Five common pitfalls

## Why It Matters

A surprise on the first invoice is a rite of passage. FinOps is part of engineering, not a finance team chore.

## Key Terms

- **Tag**: a key-value label attached to a resource.
- **Budget**: a monthly cap with alerting.
- **Savings Plans**: a term commitment in exchange for a discount.
- **Reserved Instance**: a commitment tied to a specific instance shape.
- **Rightsizing**: shrinking resources to actual usage.

## Before/After

**Before**: every instance is `m5.xlarge` and runs around the clock.

**After**: non-prod stops at night, prod runs on Savings Plans.

## Hands-on: Create a Budget

### Step 1 — Client

```python
import boto3
budgets = boto3.client("budgets")
account_id = boto3.client("sts").get_caller_identity()["Account"]
```

### Step 2 — Budget definition

```python
budget = {
    "BudgetName": "monthly-cap",
    "BudgetLimit": {"Amount": "500", "Unit": "USD"},
    "TimeUnit": "MONTHLY",
    "BudgetType": "COST",
}
```

### Step 3 — Notifications

```python
notif = [{
    "Notification": {
        "NotificationType": "ACTUAL",
        "ComparisonOperator": "GREATER_THAN",
        "Threshold": 80.0,
        "ThresholdType": "PERCENTAGE",
    },
    "Subscribers": [{"SubscriptionType": "EMAIL", "Address": "ops@example.com"}],
}]
```

### Step 4 — Create

```python
def create_budget():
    budgets.create_budget(
        AccountId=account_id,
        Budget=budget,
        NotificationsWithSubscribers=notif,
    )
```

### Step 5 — Enforce tags (illustrative policy)

```python
require_tags = {
    "Effect": "Deny",
    "Action": "ec2:RunInstances",
    "Resource": "*",
    "Condition": {"Null": {"aws:RequestTag/Project": "true"}},
}
```

## What to Notice in This Code

- An 80% alert gives you reaction time.
- A tag-enforcement policy is a precondition for cost tracking.
- Budgets can be scoped per team.

## How to Verify This Example

Budgets and tag enforcement are easy to declare and easy to forget. Verify that the budget exists with the right threshold and remember that alerts are only useful when ownership for the response is also clear.

```bash
aws budgets describe-budget --account-id "$ACCOUNT_ID" --budget-name monthly-cap
```

**Expected output:**

- The budget should show a `500 USD` monthly limit.
- The 80% notification threshold should be visible in the response.
- Without a tag-enforcement policy, the report may still tell you what cost happened without telling you who created it.

### Where teams usually get stuck

- Budgets warn; they do not automatically block spend.
- Savings Plans are safest after you have observed stable demand instead of guessed it.
- NAT and data-transfer charges often grow outside the application code path, so architecture review has to surface them deliberately.

## Five Common Mistakes

1. **Untagged resources.**
2. **No budget alerts.**
3. **Over-committing on Savings Plans.**
4. **Leaving expensive instances idle.**
5. **Ignoring NAT and data-transfer costs.**

## How This Shows Up in Production

A `Project=acme` tag separates team costs. A scheduled Lambda stops non-prod at night. A 1-year Savings Plan covers steady-state load. A quarterly rightsizing review trims drift.

## How a Senior Engineer Thinks

- Cost is an architectural metric.
- Tags are the entry point of FinOps.
- Commit only after you have seen real volatility.
- Data transfer costs hide where you cannot see them.
- Hold cost reviews on a regular cadence.

## Checklist

- [ ] Every resource carries a `Project` tag.
- [ ] Monthly budget alert is enabled.
- [ ] Idle resources are reviewed periodically.
- [ ] SPs/RIs reviewed at least once a quarter.

## Practice Problems

1. Explain the difference between on-demand and Savings Plans in one line.
2. List three minimum tags for cost tracking.
3. Give one strategy to reduce NAT Gateway costs.

## Wrap-up and Next Steps

Operations, security, and cost are all in. Time to stitch the picture together. The next post covers Cloud Architecture Basics.

## Answering the Opening Questions

- **Why do cloud bills so often come in higher than expected?**
  - Lack of visibility. Without tags you cannot tell who is spending on what; without budget alerts you discover anomalies only after the fact. Idle resources silently accumulate charges.
- **What role do tags play in cost allocation?**
  - Tags are the only mechanism to categorize costs by team, service, and environment. Combined with Cost Allocation Reports, they enable tracking who spends how much and establish clear accountability.
- **When should budget alerts be created?**
  - At the same moment you create the first resource. Setting them when costs are small builds the habit, and when costs grow the detection system is already operational.

## AWS Cost Explorer CLI Queries

Calling Cost Explorer API via CLI lets you check cost trends without logging into the console.

### Daily Cost Query

```bash
aws ce get-cost-and-usage \
    --time-period Start=2026-05-01,End=2026-05-15 \
    --granularity DAILY \
    --metrics "UnblendedCost" \
    --group-by Type=DIMENSION,Key=SERVICE
```

### Monthly Per-Service Summary

```bash
aws ce get-cost-and-usage \
    --time-period Start=2026-01-01,End=2026-06-01 \
    --granularity MONTHLY \
    --metrics "UnblendedCost" "UsageQuantity" \
    --group-by Type=DIMENSION,Key=SERVICE \
    --filter '{"Not":{"Dimensions":{"Key":"RECORD_TYPE","Values":["Credit","Refund"]}}}'
```

### Cost by Tag

```bash
aws ce get-cost-and-usage \
    --time-period Start=2026-05-01,End=2026-06-01 \
    --granularity MONTHLY \
    --metrics "UnblendedCost" \
    --group-by Type=TAG,Key=team
```

Pipe these results into a weekly Slack notification or scheduled report to automate cost reviews.

## Idle Resource Detection Script

Unused resources are the most common source of waste. The script below finds unattached EBS volumes, idle EC2 instances, and unused Elastic IPs.

```python
import boto3
from datetime import datetime, timedelta, timezone

ec2 = boto3.client("ec2")
cloudwatch = boto3.client("cloudwatch")


def find_unattached_ebs() -> list[dict]:
    """Return EBS volumes not attached to any instance."""
    volumes = ec2.describe_volumes(
        Filters=[{"Name": "status", "Values": ["available"]}]
    )["Volumes"]
    results = []
    for vol in volumes:
        results.append({
            "VolumeId": vol["VolumeId"],
            "Size_GB": vol["Size"],
            "CreateTime": vol["CreateTime"].isoformat(),
        })
    return results


def find_idle_ec2(cpu_threshold: float = 5.0, days: int = 7) -> list[dict]:
    """Return instances with average CPU below threshold."""
    instances = ec2.describe_instances(
        Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
    )
    idle = []
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days)

    for reservation in instances["Reservations"]:
        for inst in reservation["Instances"]:
            instance_id = inst["InstanceId"]
            stats = cloudwatch.get_metric_statistics(
                Namespace="AWS/EC2",
                MetricName="CPUUtilization",
                Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
                StartTime=start,
                EndTime=end,
                Period=86400,
                Statistics=["Average"],
            )
            if stats["Datapoints"]:
                avg_cpu = sum(d["Average"] for d in stats["Datapoints"]) / len(
                    stats["Datapoints"]
                )
                if avg_cpu < cpu_threshold:
                    idle.append({
                        "InstanceId": instance_id,
                        "InstanceType": inst["InstanceType"],
                        "AvgCPU": round(avg_cpu, 2),
                    })
    return idle


def find_unused_eips() -> list[dict]:
    """Return Elastic IPs not associated with any instance."""
    addresses = ec2.describe_addresses()["Addresses"]
    return [
        {"PublicIp": addr["PublicIp"], "AllocationId": addr["AllocationId"]}
        for addr in addresses
        if "AssociationId" not in addr
    ]


if __name__ == "__main__":
    print("=== Unattached EBS Volumes ===")
    for vol in find_unattached_ebs():
        print(f"  {vol['VolumeId']}  {vol['Size_GB']} GB")

    print("\n=== Idle EC2 Instances (CPU < 5%) ===")
    for inst in find_idle_ec2():
        print(f"  {inst['InstanceId']}  {inst['InstanceType']}  avg {inst['AvgCPU']}%")

    print("\n=== Unused Elastic IPs ===")
    for eip in find_unused_eips():
        print(f"  {eip['PublicIp']}  {eip['AllocationId']}")
```

Run this weekly via CI or cron, posting results to a Slack channel to prevent idle resources from accumulating.

## Budget Alert CLI Setup

Using CLI instead of the console lets you apply identical budget policies across multiple accounts.

```bash
# Create per-team budget (JSON-based)
aws budgets create-budget \
    --account-id "$ACCOUNT_ID" \
    --budget file://budget-definition.json \
    --notifications-with-subscribers file://budget-notifications.json
```

`budget-definition.json` example:

```json
{
  "BudgetName": "team-platform-monthly",
  "BudgetLimit": {"Amount": "2000", "Unit": "USD"},
  "TimeUnit": "MONTHLY",
  "BudgetType": "COST",
  "CostFilters": {
    "TagKeyValue": ["user:team$platform"]
  }
}
```

`budget-notifications.json` example:

```json
[
  {
    "Notification": {
      "NotificationType": "ACTUAL",
      "ComparisonOperator": "GREATER_THAN",
      "Threshold": 50.0,
      "ThresholdType": "PERCENTAGE"
    },
    "Subscribers": [
      {"SubscriptionType": "EMAIL", "Address": "platform-leads@example.com"}
    ]
  },
  {
    "Notification": {
      "NotificationType": "FORECASTED",
      "ComparisonOperator": "GREATER_THAN",
      "Threshold": 100.0,
      "ThresholdType": "PERCENTAGE"
    },
    "Subscribers": [
      {"SubscriptionType": "SNS", "Address": "arn:aws:sns:ap-northeast-2:123456789012:cost-alerts"}
    ]
  }
]
```

Separating 50% actual spend from 100% forecast breach gives you staged response time.

## Reserved Instances vs Savings Plans

| Aspect | Reserved Instance (RI) | Savings Plans (SP) |
| --- | --- | --- |
| Discount scope | Specific instance family/region | Compute SP covers any family/region/OS |
| Flexibility | Low (exchange required for changes) | High (auto-applied based on usage) |
| Commitment | 1 or 3 years | 1 or 3 years |
| Max discount | Up to 72% (3-year all upfront) | Up to 66% (Compute SP 3-year) |
| Best fit | Stable workloads with fixed instance type | Workloads that may change families |
| Payment options | All/partial/no upfront | All/partial/no upfront |
| Application order | RI applied first, SP covers remainder | Applied after RI |

In practice: start with Compute Savings Plans, then add RIs only for workloads whose instance type hasn't changed in 6+ months.

## FinOps Maturity Model

The FinOps Foundation defines three maturity stages: Crawl, Walk, Run. Knowing where your team stands clarifies what to do next.

| Stage | Visibility | Optimization | Operations |
| --- | --- | --- | --- |
| **Crawl** | Define tag standards, grant Cost Explorer access | Manual idle resource cleanup | Monthly cost review |
| **Walk** | Enforce tagging policy, per-team dashboards | Apply rightsizing recommendations, adopt SP | Weekly review, anomaly alerts |
| **Run** | Real-time cost feedback, unit economics tracking | Automated scheduling, reservation coverage optimization | Cost in design reviews, quarterly FinOps retro |

Most teams start at Crawl. The most important Crawl action: define and enforce tag standards. Without tags, Walk-stage dashboards produce meaningless groupings.

## Cost Allocation Report Interpretation

AWS Cost and Usage Report (CUR) provides the most granular cost data. It lands in S3 as CSV or Parquet, queryable via Athena.

### Key Columns

| Column | Meaning | Usage |
| --- | --- | --- |
| `lineItem/UsageType` | Billing unit (e.g., `BoxUsage:m5.xlarge`) | Per-instance-type cost breakdown |
| `lineItem/UnblendedCost` | Actual cost at individual account level | Per-team cost tracking |
| `resourceTags/user:team` | User-defined tag | Map to responsible org |
| `reservation/EffectiveCost` | Cost after RI/SP applied | Measure commitment effectiveness |
| `savingsPlan/SavingsPlanRate` | SP-applied unit rate | Calculate savings vs On-Demand |

### Athena Query Example

```sql
SELECT
    "resourceTags/user:team" AS team,
    "product/servicename" AS service,
    SUM("lineItem/UnblendedCost") AS total_cost
FROM cur_report
WHERE month = '5' AND year = '2026'
GROUP BY 1, 2
ORDER BY total_cost DESC
LIMIT 20;
```

Running this periodically reveals which team's which service drives cost.

## Rightsizing Workflow

Rightsizing is not a one-time event — it's a recurring operational activity.

### Step-by-Step

1. **Collect data** — Gather at least 14 days of CPU, memory, and network metrics from CloudWatch.
2. **Generate recommendations** — Check AWS Compute Optimizer or Cost Explorer rightsizing recommendations.
3. **Impact analysis** — Verify that the target instance's peak usage doesn't exceed 80% of the new size.
4. **Apply change** — Test in non-production first, observe for 1 week, then apply to production.
5. **Verify results** — Compare cost and performance metrics before and after.

### CLI Recommendation Check

```bash
aws ce get-rightsizing-recommendation \
    --service AmazonEC2 \
    --configuration '{
        "RecommendationTarget": "SAME_INSTANCE_FAMILY",
        "BenefitsConsidered": true
    }'
```

Don't blindly follow recommendations. Cross-check with peak-hour metrics — a workload with low average but high peaks will suffer if downsized.

## Cost Anomaly Detection

Budget alerts are threshold-based and miss gradual increases. Anomaly detection catches spending that deviates from normal patterns automatically.

### AWS Cost Anomaly Detection Setup

```bash
# Service-level monitor
aws ce create-anomaly-monitor \
    --anomaly-monitor '{
        "MonitorName": "service-level-monitor",
        "MonitorType": "DIMENSIONAL",
        "MonitorDimension": "SERVICE"
    }'

# Create alert subscription
aws ce create-anomaly-subscription \
    --anomaly-subscription '{
        "SubscriptionName": "cost-anomaly-alert",
        "MonitorArnList": ["arn:aws:ce::123456789012:anomalymonitor/monitor-id"],
        "Subscribers": [
            {"Type": "EMAIL", "Address": "finops@example.com"}
        ],
        "Threshold": 50.0,
        "Frequency": "DAILY"
    }'
```

Adjust the $50 threshold to team size. Small teams may find $10 meaningful; large services may need $500+ to reduce noise.

## Unit Economics Calculation

Total cost alone can't distinguish healthy growth from growing inefficiency. Unit Economics divides cost by business units to track efficiency.

### Key Metrics

| Metric | Calculation | Meaning |
| --- | --- | --- |
| Cost per Request | Monthly total / Monthly requests | API efficiency |
| Cost per Active User | Monthly total / MAU | Per-user service cost |
| Cost per Transaction | Payment infra cost / Transaction count | Transaction efficiency |
| Cost per GB Processed | Pipeline cost / Data volume | Data processing efficiency |

### Calculation Script

```python
from dataclasses import dataclass


@dataclass
class UnitEconomics:
    total_cost_usd: float
    total_requests: int
    active_users: int
    transactions: int

    @property
    def cost_per_request(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return self.total_cost_usd / self.total_requests

    @property
    def cost_per_user(self) -> float:
        if self.active_users == 0:
            return 0.0
        return self.total_cost_usd / self.active_users

    @property
    def cost_per_transaction(self) -> float:
        if self.transactions == 0:
            return 0.0
        return self.total_cost_usd / self.transactions

    def report(self) -> str:
        return (
            f"Cost/Request:     ${self.cost_per_request:.6f}\n"
            f"Cost/User:        ${self.cost_per_user:.4f}\n"
            f"Cost/Transaction: ${self.cost_per_transaction:.4f}"
        )


# Usage example
may = UnitEconomics(
    total_cost_usd=3200.0,
    total_requests=12_000_000,
    active_users=45_000,
    transactions=180_000,
)
print(may.report())
```

Tracking Unit Economics monthly distinguishes healthy growth (cost rises but efficiency holds) from cost leakage (efficiency degrades).

## Cost Optimization Strategy Matrix

| Strategy | When to Apply | Expected Effect | Watch Out |
| --- | --- | --- | --- |
| Tag standardization | Immediately | Enables cost accountability | Ineffective without enforcement |
| Budget alerts | Immediately | Early anomaly detection | Warning only, not a blocker |
| Idle resource cleanup | Weekly | Immediate savings | Recurs without automation |
| Rightsizing | Monthly | Sustained savings | Validate performance impact |
| Savings Plans | After stable patterns | Discount on steady load | Over-commitment risk |
| Spot instances | Batch/retryable workloads | Large unit-price reduction | Must handle interruptions |
| Scheduling | Non-production immediately | Eliminate nights/weekends cost | Manual start for urgent work |

<!-- toc:begin -->
## In this series

- [Cloud Computing 101 (1/10): What is Cloud Computing?](./01-what-is-cloud-computing.md)
- [Cloud Computing 101 (2/10): IaaS, PaaS, SaaS](./02-iaas-paas-saas.md)
- [Cloud Computing 101 (3/10): Region and Availability Zone](./03-region-and-availability-zone.md)
- [Cloud Computing 101 (4/10): Compute](./04-compute.md)
- [Cloud Computing 101 (5/10): Storage](./05-storage.md)
- [Cloud Computing 101 (6/10): Network](./06-network.md)
- [Cloud Computing 101 (7/10): Identity and Security](./07-identity-and-security.md)
- [Cloud Computing 101 (8/10): Monitoring](./08-monitoring.md)
- **Cost Management (current)**
- Cloud Architecture Basics (upcoming)

<!-- toc:end -->

## References

- [AWS Billing user guide](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/billing-what-is.html)
- [AWS Budgets](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html)
- [Savings Plans](https://docs.aws.amazon.com/savingsplans/latest/userguide/what-is-savings-plans.html)
- [FinOps Foundation](https://www.finops.org/framework/)

Tags: Cloud, FinOps, Cost, AWS, Architecture
