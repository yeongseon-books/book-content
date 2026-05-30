---
series: cloud-computing-101
episode: 1
title: "Cloud Computing 101 (1/10): What is Cloud Computing?"
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
  - AWS
  - Infrastructure
  - DevOps
  - Networking
seo_description: A practical primer on cloud computing — five core characteristics, on-prem vs cloud, the major providers, and the shared responsibility model.
last_reviewed: '2026-05-14'
---

# Cloud Computing 101 (1/10): What is Cloud Computing?

Buying servers used to be the default. Teams had to order hardware, rack it, wire the network, install the operating system, and only then start building the service itself. Cloud changed that sequence by turning infrastructure into something you can request in minutes.

Cloud provides five key characteristics: on-demand self-service provisioning, broad network access, resource pooling across tenants, elastic scaling, and measured service. Together, they form an operating model that shifts cost structure and responsibility.

This is the first post in the Cloud Computing 101 series.

In this post, we'll build the mental model that makes later topics like service models, regions, networking, security, and cost control easier to reason about.

> Cloud computing is an operating model: rent compute, storage, and network on demand, then manage cost and responsibility as deliberately as performance.


![cloud computing 101 chapter 1 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/cloud-computing-101/01/01-01-concept-at-a-glance.en.png)
*cloud computing 101 chapter 1 flow overview*
> The key insight is that cloud cost and risk depend on what you decide to do inside it, not just signing up for it.

## Questions to Keep in Mind

- What boundary should you inspect first when applying What is Cloud Computing??
- Which signal should the example or diagram make visible for What is Cloud Computing??
- What failure should be prevented first when What is Cloud Computing? reaches a real system?

## Questions This Chapter Answers

- The five essential characteristics of cloud
- On-premises vs cloud
- The three major providers
- The shared responsibility model
- Five common pitfalls

## Why It Matters

You can launch a global service with *zero up-front capital*. The trade-off is that you must understand *cost* and *responsibility boundaries* from day one.

## Key Terms

- **CSP**: Cloud Service Provider (AWS, Azure, GCP).
- **Elasticity**: automatic scale-up and scale-down with demand.
- **On-demand**: provision a resource the moment you need it.
- **Pay-as-you-go**: billed by usage, not by purchase.
- **Shared responsibility**: who secures what — provider vs customer.

## Before/After

**Before**: order servers, install them, wait six weeks.

**After**: click in the console, instance is ready in a minute.

## Hands-on: Your First Cloud Resource — S3 with boto3

### Step 1 — Install

```bash
pip install boto3
```

### Step 2 — Credentials

```bash
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_DEFAULT_REGION="us-east-1"
```

### Step 3 — Client

```python
import boto3

s3 = boto3.client("s3")
```

### Step 4 — Create a bucket

```python
def create_bucket(name: str):
    s3.create_bucket(Bucket=name)
    return name
```

### Step 5 — Upload an object

```python
def upload(bucket: str, key: str, data: bytes):
    s3.put_object(Bucket=bucket, Key=key, Body=data)
    return f"s3://{bucket}/{key}"

print(upload("my-test-bucket-2026", "hello.txt", b"hi cloud"))
```

The code is short but reveals an important shift: you create storage via API calls, place data in managed storage instead of local disk, and infrastructure becomes part of the code. This is why cloud is called an operating model.

## What to Notice in This Code

- Credentials live in environment variables, not source code.
- Clients are reusable — create once, call many times.
- Bucket names are globally unique across all of AWS.

These three are more operational habits than syntax rules. Putting credentials in code invites leaks; ignoring region and naming conventions makes automation fragile.

## How to Verify This Example

The point of the S3 example is not that the API call returns without throwing. The point is that you can confirm the bucket and object actually exist. That habit matters early because cloud workflows fail most often at the credential, region, and naming layers before the code itself gets interesting.

```bash
aws s3 ls
aws s3 ls s3://my-test-bucket-2026
```

**Expected output:**

- The first command should show the bucket you just created.
- The second command should show `hello.txt` inside that bucket.
- If both are empty, check credentials, active profile, region, and bucket-name uniqueness before you change the Python code.

### Where beginners usually get stuck

- `BucketAlreadyExists` usually means the bucket name is globally taken, not that your code is malformed.
- `AccessDenied` is often a credential or profile issue before it is a boto3 issue.
- Cleanup matters: even tiny learning resources turn into long-lived cost when no one deletes them.

### Cleanup Automation — Deleting Resources After Practice

The most important habit at the beginner stage is immediately cleaning up resources when you finish practicing. The code below empties all objects in a bucket and then deletes the bucket itself.

```python
def cleanup_bucket(name: str):
    """Delete all objects in a bucket, then remove the bucket."""
    bucket = boto3.resource("s3").Bucket(name)
    bucket.objects.all().delete()
    bucket.delete()
    print(f"Deleted: {name}")

cleanup_bucket("my-test-bucket-2026")
```

```bash
# Verify deletion
aws s3 ls | grep my-test-bucket-2026
# Empty output means success
```

Once you internalize this pattern, you can experiment safely in later exercises without cost leakage. In production, teams typically set Lifecycle Policies for automatic deletion.

## Why the Shared Responsibility Model Matters

The most common beginner misconception is about the responsibility boundary. Many teams assume "we put it on the cloud, so the provider handles security." In reality, the provider manages data centers, physical hardware, and hypervisors, but account permissions, data exposure scope, network access control, and application configuration usually remain the customer's responsibility.

For example, if data leaks because a bucket is public, the problem is almost always a configuration mistake, not a flaw in S3 itself. Understanding the responsibility boundary early—alongside cost—keeps every subsequent decision more stable.

## Service Models and Responsibility Boundary Summary

The most practical lens for understanding cloud is "who operates what." Even when the same capability is provided, the service model determines incident response speed, security operations difficulty, and cost structure. The table below compares IaaS, PaaS, and SaaS from the perspective of operational responsibility and change velocity, not just features.

| Aspect | IaaS | PaaS | SaaS |
| --- | --- | --- | --- |
| Examples | EC2, Compute Engine | App Engine, Heroku | Google Workspace, Notion |
| Customer manages | OS, runtime, app, data | App, data | User settings, data entry |
| Provider manages | Physical infra, virtualization | Infra, OS, runtime | Infra, platform, application |
| Deploy speed | Medium | Fast | Very fast |
| Control | High | Medium | Low |
| Ops difficulty | High | Medium | Low |
| Lock-in risk | Medium | Medium–High | High |

If a team needs rapid experimentation, PaaS or SaaS may be more suitable. If security regulations are strict and OS-level control is required, IaaS fits better. The question is not "which is more modern" but "which matches our team's current responsibility capacity and regulatory requirements."

### Responsibility Matrix

The matrix below clarifies responsibility separation that beginner cloud teams frequently confuse.

| Operations Item | On-Premises | IaaS | PaaS | SaaS |
| --- | --- | --- | --- | --- |
| Data center power/cooling | Customer | Provider | Provider | Provider |
| Physical server maintenance | Customer | Provider | Provider | Provider |
| Hypervisor | Customer | Provider | Provider | Provider |
| OS patching | Customer | Customer | Provider | Provider |
| Runtime/middleware | Customer | Customer | Provider | Provider |
| Application code | Customer | Customer | Customer | Provider |
| Data classification/access | Customer | Customer | Customer | Customer |
| Account/permission design | Customer | Customer | Customer | Customer |

The key insight is the last two rows. Regardless of the model, data classification and access control remain the customer's responsibility. Cloud adoption is not the elimination of security responsibility—it is the relocation of the responsibility boundary.

## When Cost Structure Changes, Decision-Making Changes Too

On-premises, buying a server once and using it until depreciation ends was rational. In the cloud, the opposite is true: shutting down unused resources quickly is rational. This difference reshapes a team's decision-making habits.

```bash
# Check current account's monthly cost estimate via AWS CLI
aws ce get-cost-and-usage \
  --time-period Start=2026-05-01,End=2026-05-21 \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --output table
```

This command is worth learning even at the beginner stage. When you check cost via CLI rather than console, extending to automated cost alerts or weekly report scripts becomes straightforward.

### Building Cost Intuition with Simple Calculations

```python
def monthly_cost(hourly_price: float, hours_per_day: int = 24, days: int = 30) -> float:
    """Estimate monthly cost for a single instance."""
    return hourly_price * hours_per_day * days

# t3.micro (~$0.0104/h) vs m5.large (~$0.096/h)
print(f"t3.micro monthly: ${monthly_cost(0.0104):.2f}")
print(f"m5.large monthly: ${monthly_cost(0.096):.2f}")
print(f"m5.large business-hours only: ${monthly_cost(0.096, hours_per_day=10, days=22):.2f}")
```

The point is clear: keeping a dev instance running 24/7 versus business-hours-only produces very different bills. In the cloud, "turning things off" is part of cost management.

### Major CSP Instance Comparison

Even with the same specifications, each CSP uses different names and pricing. Here is a comparison of general-purpose instances commonly used at the beginner level.

| Spec (2 vCPU, 8 GB RAM) | AWS | Azure | GCP |
| --- | --- | --- | --- |
| Instance type | m5.large | Standard_D2s_v3 | e2-standard-2 |
| Hourly price (US East) | $0.096 | $0.096 | $0.067 |
| Monthly cost (730h) | $70.08 | $70.08 | $48.91 |
| 1-year reserved discount | ~40% | ~35% | ~37% (CUD) |

Prices vary by region, payment option, and date, so these figures are directional references. The important point: cloud cost comparison does not end at hourly price. Network egress costs, storage IOPS charges, and managed-service pricing must be included for a realistic TCO (Total Cost of Ownership).

## Five Common Mistakes

1. **Doing daily work as the root account.**
2. **Skipping region — resources land somewhere unexpected.**
3. **Public bucket misconfiguration leading to data leaks.**
4. **No tags — billing becomes impossible to attribute.**
5. **Forgetting cleanup — costs accumulate silently.**

These are not beginner-only problems. The busier a team gets, the easier it is to push basic principles like tagging, budget alerts, and least privilege to the back. Setting rules early—even small ones—is far safer.

| Mistake | Immediate Fix | Preventive Automation |
| --- | --- | --- |
| Root account usage | Create IAM user, lock root | AWS Organizations SCP to block root API |
| Region not specified | Set AWS_DEFAULT_REGION env var | Pin region in Terraform provider block |
| Public bucket | Enable S3 Block Public Access | Account-level public-access block policy |
| No tags | Bulk-tag existing resources | AWS Config rule to detect untagged resources |
| Resources not deleted | Manual cleanup of non-prod resources | Lambda + EventBridge for nightly auto-stop |

## Operational Baseline Example

The example below shows how to manage a "minimum baseline" as code in real operations.

```yaml
cloud_baseline:
  account:
    root_mfa_required: true
    break_glass_account: enabled
  security:
    default_public_access_block: true
    iam_access_analyzer: enabled
  cost:
    monthly_budget_usd: 300
    alert_threshold_percent: [50, 80, 100]
  tagging:
    required_keys: [Project, Owner, Environment, CostCenter]
```

Maintaining this baseline as configuration rather than documentation reduces the chance of repeating the same mistakes when a new project starts. The cloud's advantage is fast creation; its downside is fast cost leakage from fast creation. Baseline automation structurally reduces this downside.

## How This Shows Up in Production

Startups begin on AWS Free Tier, scale with Auto Scaling Groups when traffic grows, and put budget alarms in place before bills get scary.

## How a Senior Engineer Thinks

- The cloud is for *fast experiments*.
- Document the responsibility boundary explicitly.
- Multi-region is a *result*, not a goal.
- Cost is an architectural metric.
- Apply least-privilege IAM from day one.

## Team Operating Contract Example

```yaml
team_operating_contract:
  deploy:
    requires_review: true
    rollback_plan_required: true
  security:
    least_privilege_default: true
    mfa_for_privileged_actions: true
  reliability:
    monthly_recovery_drill: true
    incident_postmortem_required: true
  cost:
    budget_alert_thresholds: [50, 80, 100]
    untagged_resource_policy: deny
```

Making the operating contract explicit ensures quality standards persist when team members change. The core of cloud is not the ability to create resources quickly—it is the ability to create resources at the same quality level repeatedly.

## Checklist

- [ ] Root account is locked down.
- [ ] MFA is enabled.
- [ ] Budget alarms are configured.
- [ ] A resource-tagging policy exists.
- [ ] Non-production resources have an auto-stop policy.

## Practice Problems

1. Add a delete-bucket helper to the code above.
2. In one sentence, explain why a closer region means lower latency.
3. Name one workload that is still better on-premises.

## Wrap-up and Next Steps

Cloud is a *model*, not a technology. The next post draws the lines between IaaS, PaaS, and SaaS.

## Answering the Opening Questions

- **Why have so many teams moved from buying servers to renting resources over the internet?**
  - Eliminating upfront investment accelerated experimentation and deployment cycles, letting teams focus on application design rather than hardware operations.
- **What are the core characteristics of the cloud, and how do they differ from on-premises?**
  - On-premises requires large capital expenditure and fixed costs, while the cloud offers pay-as-you-go billing and elastic scaling. The provider manages physical infrastructure and base services, significantly reducing the user team's operational burden.
- **What role do providers like AWS, Azure, and Google Cloud actually play?**
  - CSPs operate physical data centers, networks, and baseline security, then expose abstracted interfaces (VMs, storage, databases) to users. Users deploy their applications and data on top, handling access control, operational automation, and cost management.
<!-- toc:begin -->
## In this series

- **What is Cloud Computing? (current)**
- IaaS, PaaS, SaaS (upcoming)
- Region and Availability Zone (upcoming)
- Compute (upcoming)
- Storage (upcoming)
- Network (upcoming)
- Identity and Security (upcoming)
- Monitoring (upcoming)
- Cost Management (upcoming)
- Cloud Architecture Basics (upcoming)

<!-- toc:end -->

## References

- [NIST — definition of cloud computing](https://csrc.nist.gov/publications/detail/sp/800-145/final)
- [AWS Well-Architected](https://aws.amazon.com/architecture/well-architected/)
- [Google Cloud — concepts](https://cloud.google.com/docs/overview)
- [Azure — what is cloud computing](https://learn.microsoft.com/azure/cloud-adoption-framework/)

Tags: Cloud, AWS, Infrastructure, DevOps, Networking
