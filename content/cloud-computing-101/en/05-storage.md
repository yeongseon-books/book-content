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

## Storage Selection Criteria — Detailed Comparison

| Type | Representative Service | Latency | Scaling Model | Best-Fit Workload |
| --- | --- | --- | --- | --- |
| Block | EBS | Low | Per-volume | DB, transaction logs |
| Object | S3 | Medium | Virtually unlimited | Images, backups, logs |
| File | EFS | Medium | Shared filesystem | Multi-instance shared directories |
| Archive | Glacier | High | Long-term retention | Regulatory archives, cold backups |

| Question | Block | Object | File | Archive |
| --- | --- | --- | --- | --- |
| Random I/O performance critical? | Good fit | Poor | Fair | Poor |
| Direct HTTP access needed? | Poor | Good fit | Poor | Poor |
| Multiple servers writing concurrently? | Limited | Limited | Good fit | Poor |

```yaml
storage_lifecycle:
  logs:
    hot_days: 30
    warm_class: STANDARD_IA
    archive_after_days: 90
    delete_after_days: 365
  uploads:
    versioning: true
    replication: cross_region
```

## EBS Volume Types Compared

EBS is not a single volume type — it splits into four families based on workload characteristics. A wrong choice means either IOPS starvation slowing your database, or unnecessary provisioning wasting budget.

| Volume Type | Max IOPS | Max Throughput | Latency | Best-Fit Workload |
| --- | --- | --- | --- | --- |
| gp3 | 16,000 | 1,000 MB/s | Single-digit ms | General purpose — web servers, dev, small DBs |
| io2 Block Express | 256,000 | 4,000 MB/s | Sub-ms | High-perf DB — Oracle, SAP HANA, large OLTP |
| st1 | 500 | 500 MB/s | Medium | Sequential reads — log analytics, data lake ETL |
| sc1 | 250 | 250 MB/s | High | Cold data — archives, inactive file servers |

gp3 includes a baseline of 3,000 IOPS and 125 MB/s, making it more cost-effective than gp2 for most workloads. io2 lets you provision IOPS independently of volume size — ideal for small volumes needing high IOPS. st1 and sc1 cannot be used as boot volumes.

## S3 Storage Class Cost Comparison

S3 costs cannot be judged on storage price alone. Retrieval costs, minimum retention periods, and restore latency significantly affect total cost.

| Storage Class | Storage (GB/mo, us-east-1) | GET per 1,000 | Min Retention | Restore Time |
| --- | --- | --- | --- | --- |
| Standard | $0.023 | $0.0004 | None | Immediate |
| Standard-IA | $0.0125 | $0.001 | 30 days | Immediate |
| One Zone-IA | $0.01 | $0.001 | 30 days | Immediate |
| Glacier Instant Retrieval | $0.004 | $0.01 | 90 days | Immediate |
| Glacier Flexible Retrieval | $0.0036 | $0.0004 + restore fee | 90 days | Minutes–hours |
| Glacier Deep Archive | $0.00099 | $0.0004 + restore fee | 180 days | 12–48 hours |

Lower storage prices mean higher retrieval costs. Placing frequently accessed data in Glacier actually raises total cost. Intelligent-Tiering automatically moves objects between tiers when access patterns are unpredictable, but adds a monitoring fee ($0.0025/object/month).

## S3 Bucket Cost Analyzer

The script below compares a bucket's current storage cost against projected cost after lifecycle policies.

```python
import boto3
from datetime import datetime, timezone

s3 = boto3.client("s3")
cw = boto3.client("cloudwatch")

PRICE_PER_GB = {
    "STANDARD": 0.023,
    "STANDARD_IA": 0.0125,
    "ONEZONE_IA": 0.01,
    "GLACIER": 0.0036,
    "DEEP_ARCHIVE": 0.00099,
}


def get_bucket_size_by_class(bucket: str) -> dict[str, float]:
    """Query CloudWatch for bucket size per storage class."""
    result = {}
    for storage_class in PRICE_PER_GB:
        response = cw.get_metric_statistics(
            Namespace="AWS/S3",
            MetricName="BucketSizeBytes",
            Dimensions=[
                {"Name": "BucketName", "Value": bucket},
                {"Name": "StorageType", "Value": storage_class},
            ],
            StartTime=datetime.now(timezone.utc).replace(hour=0, minute=0),
            EndTime=datetime.now(timezone.utc),
            Period=86400,
            Statistics=["Average"],
        )
        points = response.get("Datapoints", [])
        if points:
            result[storage_class] = points[0]["Average"] / (1024**3)
    return result


def estimate_monthly_cost(size_by_class: dict[str, float]) -> float:
    """Calculate monthly cost based on current storage class distribution."""
    total = 0.0
    for cls, gb in size_by_class.items():
        total += gb * PRICE_PER_GB.get(cls, 0.023)
    return total


def estimate_optimized_cost(
    size_by_class: dict[str, float],
    ia_ratio: float = 0.4,
    glacier_ratio: float = 0.3,
) -> float:
    """Project cost after lifecycle policies are applied."""
    total_gb = sum(size_by_class.values())
    standard_gb = total_gb * (1 - ia_ratio - glacier_ratio)
    ia_gb = total_gb * ia_ratio
    glacier_gb = total_gb * glacier_ratio
    return (
        standard_gb * PRICE_PER_GB["STANDARD"]
        + ia_gb * PRICE_PER_GB["STANDARD_IA"]
        + glacier_gb * PRICE_PER_GB["GLACIER"]
    )


if __name__ == "__main__":
    bucket_name = "my-app-prod"
    sizes = get_bucket_size_by_class(bucket_name)
    current = estimate_monthly_cost(sizes)
    optimized = estimate_optimized_cost(sizes)
    saving = current - optimized
    print(f"Current monthly cost: ${current:.2f}")
    print(f"Optimized estimate:   ${optimized:.2f}")
    print(f"Potential savings:    ${saving:.2f} ({saving/current*100:.1f}%)")
```

The point of this script is showing "how much can we save" in hard numbers. When proposing cost optimization to your team, you present evidence — not gut feeling.

## Cross-Region Replication Setup

When disaster recovery or regulatory requirements demand data copies in another region, use S3 Cross-Region Replication (CRR). Prerequisites: versioning enabled on both buckets, and an IAM role with write access to the destination.

```bash
# 1. Enable versioning on source and destination
aws s3api put-bucket-versioning \
  --bucket my-app-prod-us-east-1 \
  --versioning-configuration Status=Enabled

aws s3api put-bucket-versioning \
  --bucket my-app-prod-ap-northeast-2 \
  --versioning-configuration Status=Enabled

# 2. Apply replication rule
aws s3api put-bucket-replication \
  --bucket my-app-prod-us-east-1 \
  --replication-configuration '{
    "Role": "arn:aws:iam::123456789012:role/S3ReplicationRole",
    "Rules": [{
      "ID": "replicate-all",
      "Status": "Enabled",
      "Priority": 1,
      "Filter": {},
      "Destination": {
        "Bucket": "arn:aws:s3:::my-app-prod-ap-northeast-2",
        "StorageClass": "STANDARD_IA"
      },
      "DeleteMarkerReplication": {"Status": "Enabled"}
    }]
  }'

# 3. Verify replication status
aws s3api head-object \
  --bucket my-app-prod-us-east-1 \
  --key uploads/test.txt \
  --query ReplicationStatus
```

Setting the destination storage class to STANDARD_IA reduces replica storage cost. Replication is asynchronous — most objects reach the target region within 15 minutes.

## Backup and Recovery Strategy: RTO/RPO Comparison

Each storage type has different backup mechanisms and recovery characteristics. Choose the strategy that matches your service-level objectives.

| Storage | Backup Method | RPO (Recovery Point) | RTO (Recovery Time) | Notes |
| --- | --- | --- | --- | --- |
| EBS | Incremental snapshots | Depends on snapshot frequency (1h–1d) | Minutes (restore from snapshot) | Automate with DLM |
| S3 | Versioning + CRR | Near-zero (versions created instantly) | Immediate (access previous version) | Watch for delete markers |
| EFS | AWS Backup | Depends on backup frequency | Tens of minutes–hours | File-level restore possible |
| Glacier | Vault Lock + CRR | N/A (archive itself is the backup) | 12–48 hours | Regulatory retention |

If RPO must approach zero, use S3 versioning or synchronous replication. If RTO must be short, create EBS snapshots frequently and automate the restore procedure. Glacier is less a "backup target" and more a purpose-built retention tier.

## EBS Snapshot Automation

Manual snapshots are easy to forget. The script below finds EBS volumes with a specific tag, creates snapshots, and cleans up expired ones.

```python
import boto3
from datetime import datetime, timezone, timedelta

ec2 = boto3.client("ec2")
RETENTION_DAYS = 14


def create_snapshots(tag_key: str = "Backup", tag_value: str = "true"):
    """Find EBS volumes by tag and create snapshots."""
    volumes = ec2.describe_volumes(
        Filters=[{"Name": f"tag:{tag_key}", "Values": [tag_value]}]
    )
    created = []
    for vol in volumes["Volumes"]:
        vol_id = vol["VolumeId"]
        snap = ec2.create_snapshot(
            VolumeId=vol_id,
            Description=f"auto-{vol_id}-{datetime.now(timezone.utc):%Y%m%d}",
            TagSpecifications=[{
                "ResourceType": "snapshot",
                "Tags": [
                    {"Key": "AutoBackup", "Value": "true"},
                    {"Key": "VolumeId", "Value": vol_id},
                ],
            }],
        )
        created.append(snap["SnapshotId"])
    return created


def cleanup_old_snapshots():
    """Delete auto-snapshots past retention period."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS)
    snapshots = ec2.describe_snapshots(
        Filters=[{"Name": "tag:AutoBackup", "Values": ["true"]}],
        OwnerIds=["self"],
    )
    deleted = []
    for snap in snapshots["Snapshots"]:
        if snap["StartTime"] < cutoff:
            ec2.delete_snapshot(SnapshotId=snap["SnapshotId"])
            deleted.append(snap["SnapshotId"])
    return deleted


if __name__ == "__main__":
    new_snaps = create_snapshots()
    print(f"Snapshots created: {len(new_snaps)}")
    old_snaps = cleanup_old_snapshots()
    print(f"Snapshots deleted: {len(old_snaps)}")
```

Wire this into Lambda + EventBridge schedule (e.g., daily at UTC 03:00) and snapshots maintain themselves without operator intervention. AWS Data Lifecycle Manager (DLM) does the same job, but a custom script offers more flexibility for custom tag logic or notification integrations.

## Encryption at Rest: SSE-S3 vs SSE-KMS vs SSE-C

All S3 objects should be encrypted at rest. Choose among three server-side encryption modes based on operational complexity and regulatory requirements.

| Aspect | SSE-S3 | SSE-KMS | SSE-C |
| --- | --- | --- | --- |
| Key management | AWS fully managed | AWS KMS (customer-controlled) | Customer provides key per request |
| Key rotation | Automatic (yearly) | Automatic or manual | Customer responsibility |
| Audit trail | S3 server logs only | CloudTrail records every key usage | None (customer must log externally) |
| Extra cost | None | Per-KMS-request charges | None |
| Compliance fit | Baseline | High (HIPAA, PCI-DSS) | Highest (full key separation) |
| Operational complexity | Low | Medium | High |
| Cross-account access | Bucket policy alone | Requires KMS key policy | Key must be sent with every request |

SSE-S3 is sufficient for most workloads. Use SSE-KMS when you need audit trails or fine-grained key access control. SSE-C is reserved for extreme regulatory environments where keys must never reside in AWS — lose the key and the data is unrecoverable, so a robust key management system must exist first.

```bash
# Set default encryption to SSE-KMS
aws s3api put-bucket-encryption \
  --bucket my-app-prod \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "aws:kms",
        "KMSMasterKeyID": "arn:aws:kms:us-east-1:123456789012:key/abcd-1234"
      },
      "BucketKeyEnabled": true
    }]
  }'
```

`BucketKeyEnabled: true` activates S3 Bucket Keys, reducing KMS API calls and lowering costs. Enable this on any bucket handling large object volumes.

## Storage Operations — Verification and IaC

Below are commonly used verification commands and IaC examples for production. The key discipline: after creating any storage resource, validate access control, encryption, lifecycle, and recoverability together.

```bash
# AWS S3 — check security and retention settings
aws s3api get-public-access-block --bucket my-app-prod
aws s3api get-bucket-encryption --bucket my-app-prod
aws s3api get-bucket-versioning --bucket my-app-prod

# Azure Blob — check container access level
az storage container show --account-name mystorageacct --name uploads --query properties.publicAccess

# Google Cloud Storage — check lifecycle rules
gcloud storage buckets describe gs://my-app-prod --format="value(lifecycle)"
```

```hcl
resource "aws_s3_bucket" "app" {
  bucket = "my-app-prod"
}

resource "aws_s3_bucket_versioning" "app" {
  bucket = aws_s3_bucket.app.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "app" {
  bucket = aws_s3_bucket.app.id
  rule {
    id     = "logs-tiering"
    status = "Enabled"
    filter { prefix = "logs/" }
    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }
    transition {
      days          = 90
      storage_class = "GLACIER"
    }
  }
}
```

| Comparison | S3 Standard | S3 Standard-IA | S3 Glacier Instant Retrieval |
| --- | --- | --- | --- |
| Access frequency | High | Medium–Low | Low |
| Read latency | Low | Low | Medium |
| Storage price trend | High | Medium | Low |
| Primary use | Operational data | Long-term logs | Audit/archival data |

Text architecture diagram:
`App -> S3(Standard) -> Lifecycle(30d) -> S3 IA -> Lifecycle(90d) -> Glacier -> Restore Job`

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
