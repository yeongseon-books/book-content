---
series: cloud-computing-101
episode: 5
title: "Cloud Computing 101 (5/10): Storage"
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

# Cloud Computing 101 (5/10): Storage

S3, EBS, EFS, and Glacier exist separately for a reason. They may all hold data, but they are optimized for very different access patterns, durability expectations, and recovery trade-offs.

Block storage is for OS disks and databases. Object storage is for files, backups, and archives. File storage is for NFS-like shared access. Databases are for structured data with queries. Archive is for data you almost never touch. Each has a different cost curve, latency profile, and use case.

This is the 5th post in the Cloud Computing 101 series.

In this post, we'll compare object, block, file, and archive storage and connect each one to the workload shape it actually fits.

> Storage is not just where data sits. It is part of the operating contract for latency, recovery time, cost, and sharing semantics.


![cloud computing 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/cloud-computing-101/05/05-01-concept-at-a-glance.en.png)
*cloud computing 101 chapter 5 flow overview*
> Storage decisions lock in performance characteristics, cost patterns, and operational constraints that are hard to change later.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Storage?
- Which signal should the example or diagram make visible for Storage?
- What failure should be prevented first when Storage reaches a real system?

## Questions This Chapter Answers

- The four storage types
- Durability vs availability
- Lifecycle policies
- Encryption basics
- Five common pitfalls

## Why It Matters

The wrong storage choice is *expensive, slow, and fragile*. The right one quietly works for years.

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

## Answering the Opening Questions

- **How do object, block, file, and archive storage differ?**
  - They differ fundamentally in access method (key-value vs block I/O vs POSIX filesystem vs long-term archival), latency, and scaling model. Choosing the type that matches your workload's I/O pattern is the key decision.
- **Why are durability and availability not the same thing?**
  - Durability is the probability that data is preserved without loss; availability is whether you can access it right now. Glacier has 99.999999999% durability but immediate reads are impossible.
- **What problem do S3 lifecycle policies solve?**
  - They automatically move data that decreases in access frequency over time to cheaper tiers, continuously reducing costs without manual cleanup.
<!-- toc:begin -->
## In this series

- [Cloud Computing 101 (1/10): What is Cloud Computing?](./01-what-is-cloud-computing.md)
- [Cloud Computing 101 (2/10): IaaS, PaaS, SaaS](./02-iaas-paas-saas.md)
- [Cloud Computing 101 (3/10): Region and Availability Zone](./03-region-and-availability-zone.md)
- [Cloud Computing 101 (4/10): Compute](./04-compute.md)
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
