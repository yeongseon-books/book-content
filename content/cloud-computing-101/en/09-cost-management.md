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

This is post 9 in the Cloud Computing 101 series.

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

- **What boundary should you inspect first when applying Cost Management?**
  - The article treats Cost Management as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Cost Management?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Cost Management reaches a real system?**
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
