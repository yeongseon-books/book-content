---
series: cloud-computing-101
episode: 6
title: "Cloud Computing 101 (6/10): Network"
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
  - Networking
  - VPC
  - Security
  - AWS
seo_description: VPC, subnets, security groups, and load balancers — the core of cloud networking explained with boto3 examples for beginners.
last_reviewed: '2026-05-14'
---

# Cloud Computing 101 (6/10): Network

Cloud networking looks simple until you have to change it. VPCs, subnets, security groups, NACLs, and load balancers all sound like pieces of the same thing, but they solve different boundary problems at different layers.

A VPC is your network boundary. Inside, subnets partition the address space. Security groups and network ACLs filter traffic. Load balancers distribute it. VPN and Direct Connect bring on-prem into the picture. Networking often stays abstract until something breaks, then becomes very real.

This is the 6th post in the Cloud Computing 101 series.

In this post, we'll use a four-step mental model — isolate, place, allow, distribute — to make the core cloud networking pieces easier to reason about.

> Cloud networking is mostly boundary design: isolate with VPCs, place with subnets, define trust with SGs and NACLs, and shape traffic with load balancers.


![cloud computing 101 chapter 6 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/cloud-computing-101/06/06-01-concept-at-a-glance.en.png)
*cloud computing 101 chapter 6 flow overview*
> Good network design prevents failures from cascading and makes debugging possible when things break.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Network?
- Which signal should the example or diagram make visible for Network?
- What failure should be prevented first when Network reaches a real system?

## Questions This Chapter Answers

- VPCs vs subnets
- Security Groups vs NACLs
- Public and private subnet patterns
- Load balancer basics
- Five common pitfalls

## Why It Matters

Network design is the hardest decision to undo later. The first hour shapes the next several years.

## Key Terms

- **VPC**: a logically isolated virtual network.
- **Subnet**: an IP range inside a VPC, scoped to an AZ.
- **Security Group**: a stateful, instance-level firewall.
- **NACL**: a stateless, subnet-level firewall.
- **Load Balancer**: distributes traffic across targets.

## Before/After

**Before**: every server has a public IP and the attack surface explodes.

**After**: apps live in private subnets, only the ALB faces the internet.

## Hands-on: Create a Security Group

### Step 1 — Client

```python
import boto3
ec2 = boto3.client("ec2")
```

### Step 2 — Create SG

```python
def create_sg(vpc_id, name):
    res = ec2.create_security_group(
        GroupName=name, Description=name, VpcId=vpc_id,
    )
    return res["GroupId"]
```

### Step 3 — Allow inbound

```python
def allow_https(sg_id):
    ec2.authorize_security_group_ingress(
        GroupId=sg_id,
        IpPermissions=[{
            "IpProtocol": "tcp", "FromPort": 443, "ToPort": 443,
            "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
        }],
    )
```

### Step 4 — DB SG references the app SG

```python
def allow_db_from_app(db_sg, app_sg):
    ec2.authorize_security_group_ingress(
        GroupId=db_sg,
        IpPermissions=[{
            "IpProtocol": "tcp", "FromPort": 5432, "ToPort": 5432,
            "UserIdGroupPairs": [{"GroupId": app_sg}],
        }],
    )
```

### Step 5 — Verify

```python
def describe(sg_id):
    return ec2.describe_security_groups(GroupIds=[sg_id])
```

## What to Notice in This Code

- DB SGs reference an SG, not a CIDR — that is the canonical pattern.
- 0.0.0.0/0 is an explicit statement of public exposure.
- SGs are stateful; NACLs are stateless.

## How to Verify This Example

The real test here is whether trust boundaries are encoded correctly. A database security group should trust the application security group, not a broad CIDR range that is harder to reason about and easier to misuse later.

```bash
aws ec2 describe-security-groups --group-ids sg-xxxxxxxx sg-yyyyyyyy
```

**Expected output:**

- The app security group should show inbound `443` rules.
- The DB security group should show port `5432` scoped to the application SG reference.
- If the database group exposes `0.0.0.0/0`, the design intent is already compromised.

### Where teams usually get stuck

- NAT only solves outbound routing. It does not magically make inbound exposure safe.
- Public and private subnet separation should be reflected in both route tables and SG rules.
- CIDR planning should leave room for future AZ growth and VPC peering decisions.

## Five Common Mistakes

1. **Opening SSH to 0.0.0.0/0.**
2. **Putting databases in public subnets.**
3. **Confusing NACLs and SG responsibilities.**
4. **Ignoring cross-AZ traffic costs.**
5. **Forgetting to review egress rules.**

## How This Shows Up in Production

The ALB sits in public subnets. App servers live in private subnets. RDS sits in DB private subnets. A NAT Gateway handles outbound calls.

## How a Senior Engineer Thinks

- Private by default; public is the exception.
- Split SGs by role.
- Restrict egress just as explicitly as ingress.
- VPC Flow Logs are on by default.
- Plan CIDR ranges with future merges in mind.

## Checklist

- [ ] No databases in public subnets.
- [ ] SGs are split by role.
- [ ] Flow Logs are enabled.
- [ ] Egress rules are explicit.

## Practice Problems

1. List three differences between Security Groups and NACLs.
2. Explain in one sentence why public/private subnet separation helps security.
3. Give one major difference between ALB and NLB.

## Wrap-up and Next Steps

Once the wires are in, the question becomes *who* may use them. The next post covers Identity and Security.

## Answering the Opening Questions

- **What is the difference between a VPC and a subnet?**
  - A VPC is a logically isolated network boundary; a subnet is a smaller IP range within it, divided by AZ. If the VPC is a building, subnets are floors.
- **Why do Security Groups and NACLs exist separately?**
  - Security Groups are stateful per-instance allow rules; NACLs are stateless per-subnet allow/deny rules. Since SGs cannot explicitly deny, NACLs are needed to block specific IPs at the subnet level.
- **What is the common pattern for dividing public and private subnets?**
  - Place only the ALB in the public subnet; keep app servers and databases in private subnets. This three-tier pattern minimizes external exposure, simplifies firewall rules, and narrows the attack surface.

## Why Public / Private Is the Default Pattern

A public subnet is for resources that need direct internet connectivity. A private subnet blocks all inbound from outside — egress goes through NAT or dedicated endpoints only. App servers and databases belong in private subnets because you expose only the absolute minimum entry points.

In practice: ALB lives in the public subnet, app servers in a private subnet, RDS in a dedicated DB-only private subnet. This makes the ingress path explicit and keeps firewall rules simple per role.

## VPC Connectivity Options

As services grow, a single VPC becomes insufficient. Teams split VPCs by environment or shared-service boundary, and you must choose how to connect them.

| Aspect | VPC Peering | Transit Gateway | PrivateLink |
| --- | --- | --- | --- |
| Topology | 1:1 | Hub-and-spoke | Provider–Consumer |
| Overlapping CIDRs | Not allowed | Not allowed | Allowed |
| Transitive routing | No (A-B + B-C ≠ A-C) | Yes | N/A |
| Cost | Data transfer only | Hourly + data transfer | Hourly + data transfer |
| Best fit | 2–3 VPCs, same team | 10+ VPCs, central management | Expose a single service externally |
| Management complexity | O(n²) as VPCs grow | Centralized | Per-service, independent |

**Decision heuristic**: ≤3 VPCs owned by one team → Peering. Growing beyond that → Transit Gateway. Need to expose one internal service to a partner or external team → PrivateLink.

## Load Balancer Types Compared

AWS offers three load balancer types. Selection criteria: protocol and performance requirements.

| Aspect | ALB (Application) | NLB (Network) | CLB (Classic) |
| --- | --- | --- | --- |
| Layer | L7 (HTTP/HTTPS) | L4 (TCP/UDP/TLS) | L4 + L7 hybrid |
| Routing | Path, host, header-based | Port-based | Simple round-robin |
| Performance | Millions of RPS | Hundreds of millions PPS, static IP | Legacy |
| WebSocket | Supported | Supported | Not supported |
| Static IP | No (DNS-based) | Yes (EIP attachment) | No |
| Primary use | Web APIs, microservices | gRPC, gaming, IoT | Not recommended for new projects |

Most web services start with ALB. Choose NLB when you need L4-level control (gRPC) or must whitelist a static IP in partner firewalls. CLB is legacy — never use in new projects.

### ALB Path-Based Routing Example

ALB can distribute traffic to different target groups based on URL path — useful for placing multiple microservices behind a single domain.

```text
api.example.com/users/*   → Target Group A (user service)
api.example.com/orders/*  → Target Group B (order service)
api.example.com/health    → Target Group C (health check)
```

This enables independent deployment and scaling per service. The key: isolate target groups so one service's failure doesn't cascade.

## DNS Resolution Flow

DNS resolution inside a VPC follows this order:

```text
[Application]
    → VPC DNS Resolver (VPC CIDR + 2, e.g., 10.0.0.2)
        → Route 53 Resolver
            → Private Hosted Zone (internal domains)
            → Public Hosted Zone (external domains)
            → External DNS (recursive resolution)
```

`EnableDnsSupport` lets instances use the Amazon-provided DNS. `EnableDnsHostnames` auto-assigns DNS hostnames to instances with public IPs. Both settings are prerequisites for RDS endpoint resolution, VPC endpoints, and ACM certificate validation.

## NAT Gateway and VPC Endpoints

When private-subnet instances need outbound internet access (package updates, external API calls, license validation), use a NAT Gateway. It allows outbound only — inbound is blocked — providing security and convenience.

However, NAT Gateway is expensive: hourly charge plus per-GB data processing. When accessing AWS-internal services like S3 or DynamoDB through NAT Gateway, you're paying unnecessary fees. Gateway Endpoints route traffic directly over the AWS backbone, bypassing NAT entirely.

```text
[Private subnet instance]
    ├─ Internet     → NAT Gateway → Internet Gateway → Internet
    ├─ S3 access    → Gateway Endpoint → S3 (free, AWS internal)
    └─ SQS access   → Interface Endpoint → SQS (hourly + per-GB)
```

Gateway Endpoints support S3 and DynamoDB only and are free. Interface Endpoints cover most other AWS services but incur hourly and per-GB charges. Still often cheaper than NAT Gateway for high-frequency service calls.

### VPC Endpoint Setup (CLI)

```bash
# Create Gateway Endpoint for S3
aws ec2 create-vpc-endpoint \
    --vpc-id vpc-xxx \
    --service-name com.amazonaws.ap-northeast-2.s3 \
    --route-table-ids rtb-xxx

# Create Interface Endpoint for SQS
aws ec2 create-vpc-endpoint \
    --vpc-id vpc-xxx \
    --vpc-endpoint-type Interface \
    --service-name com.amazonaws.ap-northeast-2.sqs \
    --subnet-ids subnet-xxx \
    --security-group-ids sg-xxx
```

## VPC Flow Logs

VPC Flow Logs record IP traffic information traversing network interfaces. Essential for security audits, troubleshooting, and cost analysis.

```bash
# Create VPC-level Flow Log (send to CloudWatch Logs)
aws ec2 create-flow-logs \
    --resource-type VPC \
    --resource-ids vpc-xxx \
    --traffic-type ALL \
    --log-destination-type cloud-watch-logs \
    --log-group-name /vpc/flow-logs/prod
```

Flow Logs capture:

- Source/destination IP and port
- Protocol number
- Packet count and byte count
- ACCEPT or REJECT verdict
- Timestamp

Filtering REJECT-only traffic quickly reveals blocked connection attempts by Security Groups or NACLs. Unexpected large transfers in ACCEPT logs help trace cost anomaly sources.

### Flow Log Analysis Tips

1. Review REJECT logs periodically — distinguish legitimate denials from misconfiguration.
2. Repeated REJECTs to a specific port may indicate scanning attempts.
3. Measuring cross-AZ traffic volume helps predict costs.
4. Sending logs directly to S3 is cheaper than CloudWatch Logs for long-term retention.

## Network Cost Awareness

Network costs directly influence architecture decisions. The same functionality can cost multiples more depending on traffic path.

| Traffic Path | Cost (per GB, Seoul region) | Notes |
| --- | --- | --- |
| Same AZ (private IP) | Free | Cheapest path |
| Cross-AZ (same region) | ~$0.01 (each direction) | The price of high availability |
| Cross-Region | ~$0.08 | Watch out in DR / multi-region |
| Internet outbound | $0.08–$0.12 (tiered) | Price drops after first 10 TB |
| NAT Gateway processing | $0.045/GB + hourly | Private subnet internet cost |
| VPC Endpoint (Gateway) | Free | S3, DynamoDB only |
| VPC Endpoint (Interface) | Hourly + $0.01/GB | Other AWS services |

**Cost optimization tips**:

1. If S3/DynamoDB access is frequent, Gateway Endpoints are non-negotiable. NAT Gateway pass-through is pure waste.
2. Accept cross-AZ costs for HA, but eliminate unnecessary inter-AZ calls.
3. One NAT Gateway per AZ is ideal for HA, but dev environments need only one.
4. For bulk data transfer, evaluate AWS Direct Connect or CloudFront.

## VPC Design Example and Security Group Template

| Tier | Subnet | Example CIDR | External Access |
| --- | --- | --- | --- |
| Edge | public-a / public-b | 10.0.0.0/24, 10.0.1.0/24 | Allowed (ALB) |
| App | private-app-a / private-app-b | 10.0.10.0/24, 10.0.11.0/24 | Not directly |
| Data | private-db-a / private-db-b | 10.0.20.0/24, 10.0.21.0/24 | Not directly |

```yaml
security_groups:
  alb_sg:
    inbound:
      - protocol: tcp
        port: 443
        cidr: 0.0.0.0/0
  app_sg:
    inbound:
      - protocol: tcp
        port: 8080
        source_sg: alb_sg
  db_sg:
    inbound:
      - protocol: tcp
        port: 5432
        source_sg: app_sg
```

<!-- toc:begin -->
## In this series

- [Cloud Computing 101 (1/10): What is Cloud Computing?](./01-what-is-cloud-computing.md)
- [Cloud Computing 101 (2/10): IaaS, PaaS, SaaS](./02-iaas-paas-saas.md)
- [Cloud Computing 101 (3/10): Region and Availability Zone](./03-region-and-availability-zone.md)
- [Cloud Computing 101 (4/10): Compute](./04-compute.md)
- [Cloud Computing 101 (5/10): Storage](./05-storage.md)
- **Network (current)**
- Identity and Security (upcoming)
- Monitoring (upcoming)
- Cost Management (upcoming)
- Cloud Architecture Basics (upcoming)

<!-- toc:end -->

## References

- [AWS VPC user guide](https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html)
- [AWS Security Groups](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html)
- [AWS Network ACL](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-network-acls.html)
- [AWS Elastic Load Balancing](https://docs.aws.amazon.com/elasticloadbalancing/latest/userguide/what-is-load-balancing.html)

Tags: Cloud, Networking, VPC, Security, AWS
