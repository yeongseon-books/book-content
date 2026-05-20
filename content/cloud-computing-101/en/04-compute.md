---
series: cloud-computing-101
episode: 4
title: "Cloud Computing 101 (4/10): Compute"
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
  - Compute
  - EC2
  - AutoScaling
  - DevOps
seo_description: VMs, containers, and serverless — when to pick which, plus Auto Scaling and pricing tradeoffs, with practical EC2 boto3 examples.
last_reviewed: '2026-05-14'
---

# Cloud Computing 101 (4/10): Compute

Compute is where cloud architecture becomes tangible. The same application can run on a VM, inside a container platform, or in a serverless runtime, but those choices produce very different bills, scaling behavior, and operational load.

That is why strong teams do not start with a favorite platform. They start with workload fit: how long the code runs, how bursty traffic is, how much control the runtime needs, and how much human operations time the team can afford.

This is post 4 in the Cloud Computing 101 series.

In this post, we'll compare VMs, containers, serverless, and bare metal, then connect those choices to Auto Scaling and pricing models.

> Compute choices trade control for automation. The right answer depends less on fashion and more on the failure modes and operating rhythm of the workload.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Compute?
- Which signal should the example or diagram make visible for Compute?
- What failure should be prevented first when Compute reaches a real system?

## Big Picture

![cloud computing 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/cloud-computing-101/04/04-01-concept-at-a-glance.en.png)

*cloud computing 101 chapter 4 flow overview*

This picture places Compute inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of Compute is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## Questions This Chapter Answers

- The four compute styles (VM / container / serverless / bare metal)
- What Auto Scaling actually does
- Reserved vs On-Demand vs Spot
- How to read instance type names
- Five common pitfalls

## Why It Matters

Compute choice drives roughly 60% of your bill and most of your operational pain.

## Concept at a Glance

## Key Terms

- **EC2**: AWS VM service.
- **AMI**: a VM image.
- **Auto Scaling Group**: demand-based instance management.
- **Spot**: spare capacity at a discount.
- **Reserved**: 1-3 year commitment for a discount.

## Before/After

**Before**: a permanently large server sized for the peak (waste).

**After**: an Auto Scaling group that grows and shrinks with demand.

## Hands-on: EC2 with boto3

### Step 1 — Client

```python
import boto3
ec2 = boto3.client("ec2", region_name="us-east-1")
```

### Step 2 — Launch an instance (example)

```python
def launch(ami: str, type_: str = "t3.micro"):
    res = ec2.run_instances(
        ImageId=ami, InstanceType=type_, MinCount=1, MaxCount=1,
    )
    return res["Instances"][0]["InstanceId"]
```

### Step 3 — Status

```python
def status(instance_id: str):
    res = ec2.describe_instances(InstanceIds=[instance_id])
    return res["Reservations"][0]["Instances"][0]["State"]["Name"]
```

### Step 4 — Terminate

```python
def terminate(instance_id: str):
    ec2.terminate_instances(InstanceIds=[instance_id])
```

### Step 5 — Parse instance type

```python
def parse_type(t: str) -> dict:
    family, size = t.split(".")
    return {"family": family, "size": size}

print(parse_type("t3.micro"))
print(parse_type("m5.large"))
```

## What to Notice in This Code

- The AMI is the VM's birth photo.
- `terminate` is irreversible.
- Instance type is `family.size`.

## How to Verify This Example

With compute resources, the useful thing to observe is state transition. Launch, inspect, and terminate are different operating events, and understanding their sequence makes later Auto Scaling and cost discussions much easier to follow.

```bash
aws ec2 describe-instances --instance-ids i-xxxxxxxx --query 'Reservations[0].Instances[0].State.Name'
```

**Expected output:**

- Right after launch you should see `pending`, then later `running`.
- After termination you should see `shutting-down` followed by `terminated`.
- If you cannot read these transitions, Auto Scaling events will stay mysterious and troubleshooting will stay slow.

### Where teams usually get stuck

- Stopped and terminated are not the same operational state or cost profile.
- Spot capacity belongs on interruption-tolerant work, not on stateful data tiers.
- Instance types are starting hypotheses. Metrics have to confirm whether the fit is still real.

## Five Common Mistakes

1. **Using Spot for the database.**
2. **No Auto Scaling — peaks take you offline.**
3. **Buying Reserved without flexibility headroom.**
4. **Believing "stopped instance = zero cost".**
5. **Terminating instances without log shipping — evidence is gone.**

## How This Shows Up in Production

Web tier runs On-Demand inside an ASG, batch jobs ride Spot, the database lives on Reserved, and unpredictable workloads land on Lambda.

## How a Senior Engineer Thinks

- Map workload to compute, not the other way around.
- Auto Scaling is the default.
- Spot belongs where retries are cheap.
- Reserve only your stable baseline.
- Serverless wins when human time costs more than compute.

## Checklist

- [ ] Each workload mapped to a compute style.
- [ ] Auto Scaling evaluated for every tier.
- [ ] Reserved/Spot ratio is intentional.
- [ ] Termination policy is documented.

## Practice Problems

1. What design constraints does Lambda's max execution time impose?
2. How do you implement graceful shutdown for Spot interruptions?
3. Compare `t3` vs `m5` from a workload-fit angle.

## Wrap-up and Next Steps

Compute moves data — and data has to live somewhere. The next post covers Storage.

## Answering the Opening Questions

- **What boundary should you inspect first when applying Compute?**
  - The article treats Compute as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for Compute?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when Compute reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Cloud Computing 101 (1/10): What is Cloud Computing?](./01-what-is-cloud-computing.md)
- [Cloud Computing 101 (2/10): IaaS, PaaS, SaaS](./02-iaas-paas-saas.md)
- [Cloud Computing 101 (3/10): Region and Availability Zone](./03-region-and-availability-zone.md)
- **Compute (current)**
- Storage (upcoming)
- Network (upcoming)
- Identity and Security (upcoming)
- Monitoring (upcoming)
- Cost Management (upcoming)
- Cloud Architecture Basics (upcoming)

<!-- toc:end -->

## References

- [AWS EC2 user guide](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/concepts.html)
- [AWS Auto Scaling](https://docs.aws.amazon.com/autoscaling/)
- [AWS — Spot Instances](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-spot-instances.html)
- [AWS Lambda overview](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html)

Tags: Cloud, Compute, EC2, AutoScaling, DevOps
