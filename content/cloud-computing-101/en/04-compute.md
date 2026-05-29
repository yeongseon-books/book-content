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

VMs, containers, serverless, and bare metal sit on a spectrum. More control on one end, more abstraction on the other. The best choice for you depends on your workload, team, and constraints — not on what is trendy.

This is the 4th post in the Cloud Computing 101 series.

In this post, we'll compare VMs, containers, serverless, and bare metal, then connect those choices to Auto Scaling and pricing models.

> Compute choices trade control for automation. The right answer depends less on fashion and more on the failure modes and operating rhythm of the workload.


![cloud computing 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/cloud-computing-101/04/04-01-concept-at-a-glance.en.png)
*cloud computing 101 chapter 4 flow overview*
> The compute choice you make cascades through cost, operational complexity, and what kinds of problems you can solve.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Compute?
- Which signal should the example or diagram make visible for Compute?
- What failure should be prevented first when Compute reaches a real system?

## Questions This Chapter Answers

- The four compute styles (VM / container / serverless / bare metal)
- What Auto Scaling actually does
- Reserved vs On-Demand vs Spot
- How to read instance type names
- Five common pitfalls

## Why It Matters

Compute choice drives roughly 60% of your bill and most of your operational pain.

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

- **When should you choose VMs, containers, serverless, or bare metal?**
  - VMs for long-running stable workloads, containers for microservice architectures, serverless for irregular traffic or event-driven tasks, and bare metal when extremely high performance is required.
- **What does Auto Scaling actually automate, and what does it not?**
  - Auto Scaling Groups automatically adjust instance count based on demand. However, instance type changes, storage resizing, and network policy changes still require manual intervention.
- **How should you combine On-Demand, Reserved, and Spot instances?**
  - On-Demand for unpredictable traffic, Reserved for predictable baseline capacity, and Spot for interruptible batch jobs. Most teams combine all three for cost efficiency.

## Compute Option Selection Table and Cost Model

Compute is the first suspect when performance issues arise, but it also has the biggest impact on cost optimization. When comparing VMs, containers, and serverless, the right question is not "which is convenient" but "which fits our load pattern."

| Dimension | VM | Container | Serverless |
| --- | --- | --- | --- |
| Startup time | Minutes | Seconds to minutes | Milliseconds to seconds |
| Operational responsibility | High (includes OS) | Medium (includes orchestration) | Low (runtime only) |
| Long-running tasks | Strong | Strong | Constrained |
| Traffic spikes | Requires ASG design | Requires HPA design | Strong auto-scaling |
| Cost model | Hourly | Node/usage hybrid | Per-invocation + duration |
| Debugging difficulty | Medium | Medium to high | High |

### Simplified Cost Model

These formulas are for rough early-stage comparison, not precise forecasting.

- VM monthly cost = instance price × 24 × 30 × instance count
- Container monthly cost = node price × node count + managed control-plane fee
- Serverless monthly cost = request count × per-request fee + execution time (GB-s) × rate

Example scenarios:

| Scenario | Monthly requests | Avg duration | Recommended model |
| --- | --- | --- | --- |
| Batch API | Low, sporadic | Short | Serverless |
| Back-office web | Steady | Medium | Container/VM |
| Real-time session server | High, sustained | Long | VM/Container |

### Rightsizing Review Table

| Metric | Threshold example | Action |
| --- | --- | --- |
| CPU average | Below 20% for 2+ weeks | Downsize instance |
| Memory peak | Above 85% repeatedly | Upsize or separate cache |
| Disk IOPS | Saturation frequent | Change volume type or distribute |
| Network egress | Periodic spikes | Adjust auto-scale policy |

### Auto Scaling Policy Example

```yaml
auto_scaling:
  target_group: web-asg
  min_size: 2
  max_size: 12
  policies:
    - metric: cpu_utilization
      target: 55
    - metric: request_per_target
      target: 800
  cooldown_seconds: 180
```

A commonly overlooked point in production: teams define scale-out conditions but forget scale-in safeguards. Overly aggressive scale-in causes latency spikes; overly conservative scale-in keeps costs permanently high. Scaling policies should be tested with the same rigor as feature deployments.

## Instance Family Naming Convention

EC2 instance type names follow a `family + generation + attributes.size` structure. Knowing this convention lets you infer purpose immediately when scanning hundreds of types in the console.

| Family prefix | Optimized for | Typical use cases |
| --- | --- | --- |
| t | Burstable general-purpose | Dev environments, small web servers, CI runners |
| m | Balanced general-purpose | Mid-scale applications, backend APIs |
| c | Compute-optimized | Batch processing, encoding, scientific compute |
| r | Memory-optimized | In-memory caches, large-scale analytics |
| i | Storage-optimized | High-frequency I/O, NoSQL databases |
| g | GPU graphics | ML inference, graphics rendering |
| p | GPU high-performance | Large model training, HPC |
| d | Dense local storage | Distributed file systems, data-lake nodes |
| hpc | HPC-optimized | Tightly-coupled parallel, finite-element simulation |

Higher generation numbers mean better performance at the same price. Attribute suffixes also carry meaning:

| Attribute letter | Meaning |
| --- | --- |
| a | AMD processor |
| g | AWS Graviton (ARM) |
| i | Intel processor |
| n | Enhanced networking |
| d | Local NVMe disk included |
| e | Extra memory or storage |

### Extended Instance Type Parser

In production you often need to decompose names like `m5a.2xlarge` into family, generation, attributes, and size.

```python
import re
from dataclasses import dataclass

@dataclass
class InstanceType:
    family: str
    generation: int
    attributes: str
    size: str

    @property
    def full_name(self) -> str:
        return f"{self.family}{self.generation}{self.attributes}.{self.size}"

    @property
    def is_graviton(self) -> bool:
        return "g" in self.attributes

    @property
    def has_local_disk(self) -> bool:
        return "d" in self.attributes

def parse_instance_type(name: str) -> InstanceType:
    """Parse an EC2 instance type name into a structured object."""
    pattern = r"^([a-z]+)(\d+)([a-z]*)\.(.+)$"
    match = re.match(pattern, name)
    if not match:
        raise ValueError(f"Invalid instance type format: {name}")
    return InstanceType(
        family=match.group(1),
        generation=int(match.group(2)),
        attributes=match.group(3),
        size=match.group(4),
    )

# Usage
examples = ["t3.micro", "m5a.2xlarge", "c7g.large", "r6id.4xlarge", "p4d.24xlarge"]
for name in examples:
    it = parse_instance_type(name)
    print(f"{name:>16} -> family={it.family}, gen={it.generation}, "
          f"attr={it.attributes or 'none'}, size={it.size}, "
          f"graviton={it.is_graviton}")
```

Connecting this parser to cost reports or tagging policies makes it easy to aggregate which families dominate your spend.

## Spot Instance Interruption Handler

Spot instances receive a 2-minute warning via the metadata endpoint before AWS reclaims capacity. Polling this signal and performing a graceful shutdown is mandatory.

```python
import time
import signal
import sys
from urllib.request import urlopen, Request
from urllib.error import URLError

METADATA_URL = "http://169.254.169.254/latest/meta-data/spot/instance-action"
TOKEN_URL = "http://169.254.169.254/latest/api/token"
POLL_INTERVAL_SECONDS = 5

def get_imds_token(ttl_seconds: int = 21600) -> str:
    """Retrieve an IMDSv2 token."""
    req = Request(TOKEN_URL, method="PUT")
    req.add_header("X-aws-ec2-metadata-token-ttl-seconds", str(ttl_seconds))
    with urlopen(req, timeout=2) as resp:
        return resp.read().decode()

def check_spot_interruption(token: str) -> dict | None:
    """Return action info if a Spot interruption notice exists."""
    req = Request(METADATA_URL)
    req.add_header("X-aws-ec2-metadata-token", token)
    try:
        with urlopen(req, timeout=2) as resp:
            import json
            return json.loads(resp.read().decode())
    except URLError:
        return None

def graceful_shutdown():
    """Safely terminate in-progress work."""
    print("[SPOT] Interruption notice received - starting graceful shutdown")
    # 1. Stop accepting new work (pause queue polling)
    # 2. Save checkpoint for in-progress tasks
    # 3. Deregister from load balancer
    # 4. Flush logs
    print("[SPOT] Checkpoint saved")
    print("[SPOT] Deregistered from load balancer")
    sys.exit(0)

def run_spot_monitor():
    """Poll for Spot interruption signals."""
    token = get_imds_token()
    print(f"[SPOT] Monitor started (poll interval: {POLL_INTERVAL_SECONDS}s)")

    while True:
        action = check_spot_interruption(token)
        if action is not None:
            print(f"[SPOT] Interruption scheduled: {action}")
            graceful_shutdown()
        time.sleep(POLL_INTERVAL_SECONDS)

if __name__ == "__main__":
    signal.signal(signal.SIGTERM, lambda *_: graceful_shutdown())
    run_spot_monitor()
```

The key is deciding in advance what you can accomplish within 2 minutes: checkpoint saves, queue message returns, and load-balancer deregistration are the standard sequence. Without this pattern, Spot's cost advantage is offset by operational incidents.

## Purchase Option Mix Strategy

Most production workloads do not run on a single purchase option. The standard approach is a three-tier strategy: Reserved for baseline, On-Demand for unpredictable bursts, Spot for cost reduction.

| Tier | Purchase option | Target workload | Approximate discount |
| --- | --- | --- | --- |
| Baseline | Reserved (1yr/3yr) | 24/7 always-on services | 30-60% |
| Variable | On-Demand | Unpredictable traffic peaks | 0% (list price) |
| Cost reduction | Spot | Batch, queue workers, CI/CD | 60-90% |

### Cost Simulation Code

```python
from dataclasses import dataclass

@dataclass
class PurchaseMix:
    reserved_count: int
    ondemand_count: int
    spot_count: int
    reserved_hourly: float   # RI hourly rate
    ondemand_hourly: float   # On-Demand hourly rate
    spot_hourly: float       # Spot hourly rate
    spot_interruption_rate: float = 0.05  # monthly interruption ratio

    @property
    def monthly_hours(self) -> int:
        return 24 * 30

    def monthly_cost(self) -> dict:
        hours = self.monthly_hours
        reserved = self.reserved_count * self.reserved_hourly * hours
        ondemand = self.ondemand_count * self.ondemand_hourly * hours
        spot_effective = self.spot_count * self.spot_hourly * hours
        # Fallback cost when Spot is interrupted
        fallback = (self.spot_count * self.spot_interruption_rate
                    * self.ondemand_hourly * hours * 0.1)
        return {
            "reserved": round(reserved, 2),
            "ondemand": round(ondemand, 2),
            "spot": round(spot_effective, 2),
            "spot_fallback": round(fallback, 2),
            "total": round(reserved + ondemand + spot_effective + fallback, 2),
        }

    def vs_all_ondemand(self) -> float:
        """Return savings percentage compared to all On-Demand."""
        total_instances = (self.reserved_count + self.ondemand_count
                          + self.spot_count)
        all_od = total_instances * self.ondemand_hourly * self.monthly_hours
        actual = self.monthly_cost()["total"]
        return round((1 - actual / all_od) * 100, 1)

# Simulation: 10 m5.large instances
mix = PurchaseMix(
    reserved_count=4,
    ondemand_count=3,
    spot_count=3,
    reserved_hourly=0.056,   # 1-year RI
    ondemand_hourly=0.096,
    spot_hourly=0.035,
)

result = mix.monthly_cost()
print(f"Monthly cost breakdown: {result}")
print(f"Savings vs all On-Demand: {mix.vs_all_ondemand()}%")
```

This simulation is a directional tool, not a precise forecast. It shows the tradeoff: too much Reserved reduces flexibility, too much Spot reduces stability.

## Container vs Serverless Decision Flow

When torn between containers and serverless, check these five questions in order:

1. **Does execution time exceed 15 minutes?** If yes, Lambda is off the table. Consider ECS/EKS or Step Functions splitting.
2. **Does cold start affect your SLA?** If p99 latency is strict for a synchronous API, factor in Provisioned Concurrency cost. If that exceeds always-on container cost, containers win.
3. **Must you hold state locally?** WebSocket sessions, in-memory caches, and similar patterns are a poor fit for serverless.
4. **Does traffic drop to zero?** If there are quiet hours (nights, weekends), serverless billing is advantageous. If traffic is constant, container fixed cost is more predictable.
5. **Can your team operate container orchestration?** A small team without Kubernetes experience may benefit more from the reduced ops burden of serverless.

If any answer is unfavorable to serverless, containers deserve first consideration. If all five favor serverless, Lambda + API Gateway significantly reduces operational cost.

## Lambda CLI Operations

Common AWS CLI commands when operating serverless functions:

### Create function

```bash
aws lambda create-function \
  --function-name my-handler \
  --runtime python3.12 \
  --role arn:aws:iam::123456789012:role/lambda-exec \
  --handler app.handler \
  --zip-file fileb://deployment.zip \
  --timeout 30 \
  --memory-size 256
```

### Provisioned Concurrency

Use this for synchronous APIs where cold start is unacceptable. Incurs cost, so size it to actual need.

```bash
# Publish a version
aws lambda publish-version \
  --function-name my-handler \
  --description "v1 for provisioned concurrency"

# Allocate Provisioned Concurrency
aws lambda put-provisioned-concurrency-config \
  --function-name my-handler \
  --qualifier 1 \
  --provisioned-concurrent-executions 10
```

### Reserved Concurrency

Prevents a single function from monopolizing the account-wide concurrency limit — or guarantees minimum capacity for a critical function.

```bash
aws lambda put-function-concurrency \
  --function-name my-handler \
  --reserved-concurrent-executions 50
```

### Invoke test

```bash
aws lambda invoke \
  --function-name my-handler \
  --payload '{"key": "value"}' \
  --cli-binary-format raw-in-base64-out \
  response.json

cat response.json
```

Provisioned Concurrency and Reserved Concurrency sound similar but serve different purposes. Provisioned means "pre-warm"; Reserved means "concurrency cap". Confusing them leads to unnecessary cost or unexpected throttling.

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
