---
series: cloud-computing-101
episode: 5
title: Storage
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
  - Storage
  - S3
  - EBS
  - Architecture
seo_description: Object, block, file, and archive cloud storage compared by access pattern, durability, and cost — with S3 lifecycle examples in boto3.
last_reviewed: '2026-05-14'
---

# Storage

S3, EBS, EFS, and Glacier exist separately for a reason. They may all hold data, but they are optimized for very different access patterns, durability expectations, and recovery trade-offs.

Storage mistakes often stay hidden at first. The system seems fine until backup, restore, sharing, or long-term retention turns into the expensive part of the design. Picking the right storage tier early prevents a surprising amount of later rework.

This is post 5 in the Cloud Computing 101 series.

In this post, we'll compare object, block, file, and archive storage and connect each one to the workload shape it actually fits.

> Storage is not just where data sits. It is part of the operating contract for latency, recovery time, cost, and sharing semantics.

## Questions This Chapter Answers

- The four storage types
- Durability vs availability
- Lifecycle policies
- Encryption basics
- Five common pitfalls

## Why It Matters

The wrong storage choice is *expensive, slow, and fragile*. The right one quietly works for years.

## Concept at a Glance

![Block, object, file, and archive storage split by access pattern and operating need](../../../assets/cloud-computing-101/05/05-01-concept-at-a-glance.en.png)

*Block, object, file, and archive storage split by access pattern and operating need*

## Key Terms

- **Object**: key-value with metadata (S3).
- **Block**: a disk-like surface in fixed blocks (EBS).
- **File**: a POSIX directory (EFS).
- **Durability**: probability your data survives (e.g., 11 nines).
- **Lifecycle**: tier transitions over time.

## Before/After

**Before**: every file lives on the VM disk, backups become a nightmare.

**After**: objects in S3 with a Glacier transition rule.

## Hands-on: S3 Object Lifecycle

### Step 1 — Client

```python
import boto3
s3 = boto3.client("s3")
```

### Step 2 — Put

```python
def put(bucket, key, body):
    s3.put_object(Bucket=bucket, Key=key, Body=body)
    return f"s3://{bucket}/{key}"
```

### Step 3 — Get

```python
def get(bucket, key):
    res = s3.get_object(Bucket=bucket, Key=key)
    return res["Body"].read()
```

### Step 4 — Lifecycle policy

```python
policy = {
    "Rules": [{
        "ID": "to-glacier-after-90d",
        "Status": "Enabled",
        "Filter": {"Prefix": "logs/"},
        "Transitions": [{"Days": 90, "StorageClass": "GLACIER"}],
    }]
}
```

### Step 5 — Apply

```python
def apply_lifecycle(bucket, policy):
    s3.put_bucket_lifecycle_configuration(
        Bucket=bucket, LifecycleConfiguration=policy,
    )
```

## What to Notice in This Code

- Prefixes group objects under a policy.
- Transitions are how you actually save money.
- EBS is typically attached to a single VM at a time.

## How to Verify This Example

A lifecycle policy only matters when it is truly attached to the bucket and scoped to the intended object prefix. Otherwise the cost optimization story exists in code review but never reaches production data.

```bash
aws s3api get-bucket-lifecycle-configuration --bucket my-test-bucket-2026
```

**Expected output:**

- You should see a rule ID such as `to-glacier-after-90d`.
- The `logs/` prefix and `GLACIER` transition should both be present.
- That confirmation is what turns lifecycle from documentation into an operating control.

### Where teams usually get stuck

- Bucket policy and lifecycle policy solve different problems: access control versus storage-tier movement.
- Glacier is cheap because retrieval is slower. Restore time belongs in the design conversation.
- EFS is a shared file system, not a drop-in replacement for high-IOPS block storage.

## Five Common Mistakes

1. **Public ACLs that expose buckets.**
2. **No lifecycle — costs grow forever.**
3. **No EBS snapshots.**
4. **Assuming EFS gives you high IOPS.**
5. **Forgetting Glacier restore time when you actually need data.**

## How This Shows Up in Production

Logs land in S3 and transition to Glacier after 90 days. Database volumes use EBS gp3. Shared directories live on EFS.

## How a Senior Engineer Thinks

- The access pattern decides the storage.
- Encryption is the default, not a feature request.
- Define lifecycle on day one.
- Restore cost is part of total cost.
- Backup is not the same as replication.

## Checklist

- [ ] Default encryption enabled.
- [ ] Lifecycle policies defined.
- [ ] Public access blocked by default.
- [ ] At least one restore drill per year.

## Practice Problems

1. Name the three Glacier restore speed tiers.
2. Describe a sensible scenario for enabling S3 versioning.
3. EBS vs EFS for sharing — explain the difference in one sentence.

## Wrap-up and Next Steps

Once data sits somewhere, you have to *connect* to it. The next post covers Network.

<!-- toc:begin -->
- [What is Cloud Computing?](./01-what-is-cloud-computing.md)
- [IaaS, PaaS, SaaS](./02-iaas-paas-saas.md)
- [Region and Availability Zone](./03-region-and-availability-zone.md)
- [Compute](./04-compute.md)
- **Storage (current)**
- Network (upcoming)
- Identity and Security (upcoming)
- Monitoring (upcoming)
- Cost Management (upcoming)
- Cloud Architecture Basics (upcoming)
<!-- toc:end -->

## References

- [AWS S3 user guide](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html)
- [AWS EBS](https://docs.aws.amazon.com/ebs/latest/userguide/ebs-volume-types.html)
- [AWS EFS](https://docs.aws.amazon.com/efs/latest/ug/whatisefs.html)
- [AWS Glacier — restore options](https://docs.aws.amazon.com/AmazonS3/latest/userguide/restoring-objects-retrieval-options.html)

Tags: Cloud, Storage, S3, EBS, Architecture
