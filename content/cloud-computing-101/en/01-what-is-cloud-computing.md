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

That convenience is only half of the story. Cloud is not just "someone else's server." It is an operating model where you provision compute, storage, and network on demand, pay for what you actually use, and split responsibility with the provider.

This is the first post in the Cloud Computing 101 series.

In this post, we'll build the mental model that makes later topics like service models, regions, networking, security, and cost control easier to reason about.

> Cloud computing is an operating model: rent compute, storage, and network on demand, then manage cost and responsibility as deliberately as performance.

## Questions to Keep in Mind

- What boundary should you inspect first when applying What is Cloud Computing??
- Which signal should the example or diagram make visible for What is Cloud Computing??
- What failure should be prevented first when What is Cloud Computing? reaches a real system?

## Big Picture

![cloud computing 101 chapter 1 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/cloud-computing-101/01/01-01-concept-at-a-glance.en.png)

*cloud computing 101 chapter 1 flow overview*

This picture places What is Cloud Computing? inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of What is Cloud Computing? is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## Questions This Chapter Answers

- The five essential characteristics of cloud
- On-premises vs cloud
- The three major providers
- The shared responsibility model
- Five common pitfalls

## Why It Matters

You can launch a global service with *zero up-front capital*. The trade-off is that you must understand *cost* and *responsibility boundaries* from day one.

## Concept at a Glance

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

## What to Notice in This Code

- Credentials live in environment variables, not source code.
- Clients are reusable — create once, call many times.
- Bucket names are globally unique across all of AWS.

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

## Five Common Mistakes

1. **Doing daily work as the root account.**
2. **Skipping region — resources land somewhere unexpected.**
3. **Public bucket misconfiguration leading to data leaks.**
4. **No tags — billing becomes impossible to attribute.**
5. **Forgetting cleanup — costs accumulate silently.**

## How This Shows Up in Production

Startups begin on AWS Free Tier, scale with Auto Scaling Groups when traffic grows, and put budget alarms in place before bills get scary.

## How a Senior Engineer Thinks

- The cloud is for *fast experiments*.
- Document the responsibility boundary explicitly.
- Multi-region is a *result*, not a goal.
- Cost is an architectural metric.
- Apply least-privilege IAM from day one.

## Checklist

- [ ] Root account is locked down.
- [ ] MFA is enabled.
- [ ] Budget alarms are configured.
- [ ] A resource-tagging policy exists.

## Practice Problems

1. Add a delete-bucket helper to the code above.
2. In one sentence, explain why a closer region means lower latency.
3. Name one workload that is still better on-premises.

## Wrap-up and Next Steps

Cloud is a *model*, not a technology. The next post draws the lines between IaaS, PaaS, and SaaS.

## Answering the Opening Questions

- **What boundary should you inspect first when applying What is Cloud Computing??**
  - The article treats What is Cloud Computing? as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for What is Cloud Computing??**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when What is Cloud Computing? reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

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
