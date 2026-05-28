---
series: cloud-computing-101
episode: 10
title: "Cloud Computing 101 (10/10): Cloud Architecture Basics"
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
  - Architecture
  - WellArchitected
  - AWS
  - DevOps
seo_description: The five Well-Architected pillars and a layered web architecture pattern — closing out Cloud Computing 101 with a practical reference design.
last_reviewed: '2026-05-14'
---

# Cloud Computing 101 (10/10): Cloud Architecture Basics

By the end of a cloud fundamentals series, the risk is thinking in product lists instead of systems. Compute, storage, networking, security, monitoring, and cost all make sense individually, but production architecture begins when those pieces reinforce each other inside one design.

Availability, scalability, automation, and resilience are not yes-or-no questions. They are degrees. How much redundancy is enough? When should you automate? What failure rate is acceptable? Your business context answers these, not engineering ideals.

This is the final post in the Cloud Computing 101 series.

In this post, we'll pull the series together through the Well-Architected pillars and a layered reference design you can reuse as a review lens.

> Cloud architecture is the discipline of turning separate service choices into one coherent operating system for reliability, security, performance, and cost.


![cloud computing 101 chapter 10 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/cloud-computing-101/10/10-01-concept-at-a-glance.en.png)
*cloud computing 101 chapter 10 flow overview*
> Architecture is not about perfect design. It is about deliberate tradeoffs and systems that are easy to debug and repair.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Cloud Architecture Basics?
- Which signal should the example or diagram make visible for Cloud Architecture Basics?
- What failure should be prevented first when Cloud Architecture Basics reaches a real system?

## Questions This Chapter Answers

- The five Well-Architected pillars
- A layered web architecture pattern
- Stateless vs stateful separation
- Why IaC is non-negotiable
- Five common pitfalls

## Why It Matters

The same feature can cost ten times more or ten times less depending on the architecture. This final post pulls the whole series into one picture.

## Key Terms

- **Well-Architected**: AWS framework of design best practices.
- **Stateless**: the server holds no client state.
- **IaC**: infrastructure expressed as code (Terraform, CloudFormation).
- **Loose coupling**: components decoupled through queues.
- **Idempotent**: a request can be repeated safely.

## Before/After

**Before**: a monolith pinned to one server — changes are scary, outages are catastrophic.

**After**: stateless app tier plus a Multi-AZ database, all defined in IaC. Change is safe.

## Hands-on: Layered Web Architecture (illustrative)

### Step 1 — IaC skeleton (pseudo-Terraform)

```python
def vpc(): return {"cidr": "10.0.0.0/16", "azs": 2}
def subnets(): return ["public-a", "public-b", "private-a", "private-b"]
```

### Step 2 — Compute

```python
def asg(min_, max_): return {"min": min_, "max": max_, "policy": "cpu>60"}
```

### Step 3 — Data

```python
def rds(): return {"engine": "postgres", "multi_az": True, "backup_days": 7}
def cache(): return {"engine": "redis", "nodes": 2}
```

### Step 4 — Object and queue

```python
def s3(): return {"versioning": True, "lifecycle": "to-glacier-90d"}
def queue(): return {"visibility_timeout": 30, "dlq": True}
```

### Step 5 — Routing

```python
def alb(): return {"listeners": [{"port": 443, "tls": True}], "target": "asg"}
```

## What to Notice in This Code

- Multi-AZ is the default, not a feature flag.
- A DLQ is your retry safety net.
- Stateless is the precondition for ASG to actually work.

## How to Verify This Design

In an architecture chapter, verification is mostly about whether the design explains safe behavior under change, failure, and recovery. Read each layer and ask what it protects you from operationally.

**Expected output:**

- You should be able to explain why the app tier can scale horizontally without breaking user state.
- You should be able to point to which resources absorb retries, which preserve data, and which carry Multi-AZ responsibility.
- You should be able to justify the queue and DLQ as failure-isolation tools rather than decorative components.

### Questions to ask in a real review

- Where does a single point of failure still remain?
- Which changes still require manual intervention, and how would IaC reduce that risk?
- When reliability and cost goals pull in opposite directions, which principle wins for this workload?

## Five Common Mistakes

1. **Trying to horizontally scale a stateful app.**
2. **Running databases in a single AZ.**
3. **Manual changes, no IaC.**
4. **Calling external services without retries.**
5. **Never practicing backup restore.**

## How This Shows Up in Production

CloudFront in front of ALB, an ASG of stateless apps, RDS Multi-AZ, Redis for hot data, S3 for blobs. Terraform reproduces the same shape across environments. On-call leans on dashboards and runbooks.

## How a Senior Engineer Thinks

- Well-Architected is a conversation tool, not a checklist.
- Change safety beats every other quality.
- Restore drills matter more than backups.
- Start small, modularize as you grow.
- Docs and runbooks ship with the code.

## Checklist

- [ ] Multi-AZ enabled.
- [ ] Environment is reproducible from IaC.
- [ ] Restore drill scheduled.
- [ ] Five-pillar review at least once a quarter.

## Practice Problems

1. List all five Well-Architected pillars.
2. Give one canonical technique for making an app stateless.
3. Explain in one line why IaC is safer than manual changes.

## Wrap-up and Next Steps

That closes out *Cloud Computing 101*. The next series — *Containers 101*, *Kubernetes 101*, and *Serverless 101* — go deep on the compute abstractions.

## Answering the Opening Questions

- **What does each of the six Well-Architected pillars tell you to examine?**
  - Operational Excellence looks at repeatability of change and response procedures; Security at least privilege and encryption; Reliability at failure response and recovery; Performance Efficiency at resource selection and scaling strategy; Cost Optimization at waste-reducing structure; Sustainability at minimizing environmental impact.
- **What does a basic multi-tier web architecture look like?**
  - CDN → ALB → Stateless App (Multi-AZ) → Cache/DB/Object Storage, with each tier independently scalable.
- **Why must stateless and stateful layers be separated?**
  - Stateless tiers can freely add or remove instances for horizontal scaling. Delegating state to dedicated tiers (DB, cache) is what makes Auto Scaling safe to operate.
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
- [Cloud Computing 101 (9/10): Cost Management](./09-cost-management.md)
- **Cloud Architecture Basics (current)**

<!-- toc:end -->

## References

- [AWS Well-Architected Framework](https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html)
- [Multi-AZ design](https://docs.aws.amazon.com/whitepapers/latest/aws-overview/global-infrastructure.html)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Twelve-Factor App](https://12factor.net/)

Tags: Cloud, Architecture, WellArchitected, AWS, DevOps
