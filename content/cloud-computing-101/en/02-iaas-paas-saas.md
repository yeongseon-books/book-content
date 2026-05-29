---
series: cloud-computing-101
episode: 2
title: "Cloud Computing 101 (2/10): IaaS, PaaS, SaaS"
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
  - IaaS
  - PaaS
  - SaaS
  - Architecture
seo_description: Compare IaaS, PaaS, and SaaS by what you operate vs what the provider runs, with five concrete selection criteria and example services.
last_reviewed: '2026-05-14'
---

# Cloud Computing 101 (2/10): IaaS, PaaS, SaaS

EC2, Heroku, and Notion are all cloud services, but they feel nothing alike when you operate them. One makes you think about instances and patching. One wants your code and a start command. One gives you a finished application and asks almost nothing about infrastructure.

IaaS, PaaS, and SaaS differ in what part of the stack the provider manages. With IaaS, you manage the OS and runtime. With PaaS, the platform handles more. With SaaS, you use a finished product. Picking the right level requires knowing what tradeoff you're making.

This is the 2nd post in the Cloud Computing 101 series.

In this post, we'll compare service models through control, speed, lock-in, and operational burden so you can match them to real workloads.

> Cloud service models are easiest to understand as operating boundaries: the more the provider runs for you, the less control you keep and the faster you usually move.


![cloud computing 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/cloud-computing-101/02/02-01-concept-at-a-glance.en.png)
*cloud computing 101 chapter 2 flow overview*
> The choice between IaaS, PaaS, and SaaS is a statement about who runs what, not about which is objectively better.

## Questions to Keep in Mind

- What boundary should you inspect first when applying IaaS, PaaS, SaaS?
- Which signal should the example or diagram make visible for IaaS, PaaS, SaaS?
- What failure should be prevented first when IaaS, PaaS, SaaS reaches a real system?

## Questions This Chapter Answers

- IaaS, PaaS, SaaS definitions
- The shared-responsibility diagram
- Five selection criteria
- Where serverless fits
- Five common pitfalls

## Why It Matters

Pick the wrong model and you waste both *cost* and *speed*. Each stage of an organization fits a different abstraction level.

## Key Terms

- **IaaS**: VMs, disks, and networks only.
- **PaaS**: also runs your runtime and deploys your code.
- **SaaS**: a finished application.
- **FaaS**: function-level execution (serverless).
- **Managed**: the provider runs it for you.

## Before/After

**Before**: do everything yourself — server, OS, app.

**After**: you ship code, the platform handles the rest.

The key insight is that as abstraction rises, operational burden drops—but so does fine-grained control. The right model depends on what you are willing to give up and what you gain in return.

## Hands-on: A PaaS Example with a Tiny Flask App

### Step 1 — App code

```python
# app.py
from flask import Flask
app = Flask(__name__)

@app.route("/")
def home():
    return {"hello": "cloud"}
```

### Step 2 — Dependencies

```text
flask==3.0.0
gunicorn==21.2.0
```

### Step 3 — Process file

```text
# Procfile
web: gunicorn app:app
```

### Step 4 — Deploy (PaaS is this short)

```bash
git init
git add .
git commit -m "init"
# example: heroku create && git push heroku main
```

### Step 5 — IaaS comparison

```python
# On IaaS you would also need to:
# - provision a VM
# - install OS packages
# - configure a reverse proxy
# - install a log shipper
print("PaaS = git push, IaaS = the four steps above by hand")
```

## What to Notice in This Code

- PaaS deployment is one Procfile line.
- On IaaS, every step is your responsibility.
- SaaS removes the code itself from your scope.

## How to Verify This Example

This example is really about the deployment contract. Run it locally in the same shape that a PaaS expects, then compare that short contract with the extra moving parts you would have to own on IaaS.

```bash
pip install -r requirements.txt
gunicorn app:app --bind 0.0.0.0:8000
curl http://127.0.0.1:8000/
```

**Expected output:**

- Gunicorn should start without import or path errors.
- `curl` should return a JSON payload like `{"hello":"cloud"}`.
- Once that works, it becomes obvious why PaaS can remove a large amount of platform setup from the critical path.

### Where teams usually get stuck

- A mismatched process command or module path is one of the most common reasons a PaaS deployment fails after a successful local test.
- Do not reduce the choice to convenience. The real question is where operations responsibility stops.
- SaaS evaluation should include export, SSO, and audit concerns, not just feature lists.

## Where Serverless Fits

FaaS is easiest to understand as a higher abstraction than PaaS. Users focus on function code and triggers while the platform handles infrastructure and scaling. However, cold starts, short execution limits, and statelessness constraints mean FaaS does not suit every workload.

Event-driven tasks, intermittent execution, and batch processing are strong fits. Long-lived connections or applications that hold large in-memory state for extended periods are poor fits. So rather than viewing FaaS as "newer therefore better," treat it as a distinct execution model optimized for event-centric workloads.

## IaaS Hands-on: Provisioning an EC2 Instance

While PaaS deploys with a single Procfile line, IaaS requires creating infrastructure resources one by one. Below is a minimal AWS CLI example for launching an EC2 instance.

```bash
# 1. Check VPC and subnet (using default VPC)
aws ec2 describe-vpcs --filters Name=isDefault,Values=true \
  --query 'Vpcs[0].VpcId' --output text

# 2. Create security group
aws ec2 create-security-group \
  --group-name demo-sg \
  --description "Demo security group" \
  --vpc-id vpc-0abc1234

# 3. Allow SSH
aws ec2 authorize-security-group-ingress \
  --group-name demo-sg \
  --protocol tcp --port 22 \
  --cidr 203.0.113.0/32

# 4. Launch instance
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.micro \
  --key-name my-key \
  --security-groups demo-sg \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=demo}]'
```

The contrast with PaaS is immediate. PaaS was `git push`; IaaS requires VPC verification, security group creation, port policy, and instance launch—four steps minimum. In exchange, you get direct control over networking and security.

### Follow-up Tasks Easy to Miss on IaaS

After the instance is running, these tasks remain:

| Follow-up Task | Description | Risk if Skipped |
| --- | --- | --- |
| OS patching | Apply security updates | CVE exposure |
| Log agent install | CloudWatch Agent or Fluentd | No logs during incidents |
| Monitoring setup | CPU/memory/disk alerts | Unresponsive instance goes unnoticed |
| Backup policy | Automated EBS snapshots | Data loss |
| Tagging | Project, Owner, Environment | Cost tracking impossible |

On PaaS, the platform handles most of these. If you choose IaaS, the team must accept these follow-up tasks as part of their operational scope.

## SaaS Evaluation Framework

Evaluating SaaS only by feature lists leads to lock-in and operational pain later. The framework below covers items that must be checked before adoption.

| Evaluation Area | Check Item | Risk Signal |
| --- | --- | --- |
| Data Ownership | Export API availability | CSV-only, no automation possible |
| Auth Integration | SSO/SAML/OIDC support | Only proprietary accounts |
| SLA | Availability guarantee level | Below 99.9%, unclear compensation |
| Audit Log | Admin action tracking | Log retention under 30 days |
| Pricing Model | Per-seat or usage-based structure | Annual prepay only, no downgrade |
| Regional Compliance | Data storage location | No region selection, stored outside EU |

```yaml
saas_evaluation:
  product: "Notion"
  export_api: true
  sso_support: [SAML, OIDC]
  sla_percent: 99.9
  audit_log_retention_days: 90
  data_region_selectable: false
  contract_flexibility: annual_only
  risk_level: medium
  mitigation: "quarterly data export to S3"
```

Running this evaluation before adoption lets you predict costs and risks when you eventually need to switch providers or migrate data.

## Cost Comparison: Same App on Three Models

Compare cost structures when running the same web application on IaaS, PaaS, and FaaS. Baseline: 1 million requests/month, average response time 200ms.

| Item | IaaS (EC2 t3.small) | PaaS (Heroku Standard-1X) | FaaS (Lambda) |
| --- | --- | --- | --- |
| Compute monthly cost | $15.18 (24/7) | $25.00 (dyno) | $2.08 (1M req x 200ms) |
| Load balancer | $16.20 (ALB) | Included | Included (API Gateway $3.50) |
| Logs/monitoring | $5-15 (CloudWatch) | Included (basic) | $3-5 (CloudWatch) |
| OS patch/ops labor | High | None | None |
| Total (infra only) | ~$36 + labor | $25 | ~$9 |
| Best traffic pattern | Steady traffic | Steady + occasional peaks | Intermittent/event-driven |

The key takeaway is not "cheapest wins." FaaS is dramatically cheaper for intermittent traffic but can become more expensive under sustained high load. IaaS infrastructure cost is predictable, but the comparison is incomplete without factoring in operations labor.

### TCO Calculation Tips

```python
def monthly_tco(
    compute_usd: float,
    ops_hours: float,
    hourly_rate: float = 50.0,
    managed_services_usd: float = 0.0,
) -> dict:
    """Total Cost of Ownership = infra + ops labor + managed services."""
    ops_cost = ops_hours * hourly_rate
    total = compute_usd + ops_cost + managed_services_usd
    return {"compute": compute_usd, "ops": ops_cost, "managed": managed_services_usd, "total": total}

# IaaS: infra $36, 2 hours/week ops (8 hours/month)
print(monthly_tco(36, ops_hours=8))  # total: $436
# PaaS: infra $25, 0.5 hours/week ops (2 hours/month)
print(monthly_tco(25, ops_hours=2))  # total: $125
# FaaS: infra $9, nearly zero ops (0.5 hours/month)
print(monthly_tco(9, ops_hours=0.5)) # total: $34
```

Once you include operations labor, the real cost of IaaS can exceed 10x its infrastructure price. This is why the intuition that "IaaS is cheapest" frequently inverts in practice.

## Five Selection Criteria

1. Does our team have the capacity and time to manage OS and networking directly?
2. Is deployment speed or control more important right now?
3. How much vendor lock-in can we tolerate?
4. Is the workload event-driven or long-running?
5. Do security and regulatory requirements demand fine-grained environment control?

Early-stage startups usually prioritize speed, favoring PaaS or managed services. Larger platform teams move toward IaaS or container platforms for cost optimization and fine control. SaaS is strongest in domains where building in-house has no competitive advantage.

## Five Common Mistakes

1. **Treating a PaaS like a VM.**
2. **Going IaaS without enough operations headcount.**
3. **Ignoring data lock-in when adopting SaaS.**
4. **Underestimating cold starts on FaaS.**
5. **Mixing models without a clear responsibility boundary.**

In practice, the fifth mistake causes the most damage. If auth is SaaS, the app is PaaS, and data processing is IaaS—but there is no responsibility document—tracing where a failure started during an incident becomes nearly impossible. If you cannot determine "is this a provider issue or our code issue?" within five minutes, your responsibility boundaries are unclear.

## How This Shows Up in Production

Early-stage startups run on PaaS like Heroku or Render. As they grow they move workloads to IaaS such as AWS with EKS, while keeping office tools on SaaS.

## How a Senior Engineer Thinks

- Self-host only what you do *better* than the provider.
- The PaaS-to-IaaS jump is a cost-vs-control decision.
- SaaS includes vendor risk in the price.
- FaaS is great for event-driven workloads.
- Abstraction = freedom *and* lock-in.

To make this concrete: "self-host only what you do better" becomes clear with a database example. Installing PostgreSQL on EC2 means the team owns replicas, backups, failover, and version upgrades. Using RDS hands most of that to AWS. If you have no DBA, RDS is the realistic choice. If you have a dedicated DBA and need custom extensions or kernel tuning, self-hosting makes sense.

"Abstraction = freedom and lock-in" means you should prepare an exit strategy alongside adoption. When using PaaS, structure your app for easy containerization so migrating to Kubernetes later costs less. When using SaaS, export data periodically to maintain the ability to switch tools.

## Model Transition Scenarios

Three transition scenarios commonly seen in practice:

**Scenario 1: PaaS to Container Platform**

- Trigger: Traffic growth pushes dyno costs above $500/month, and platform constraints make WebSocket support unstable.
- Path: Heroku → Docker containerization → ECS/EKS or Cloud Run.
- Prerequisite: 12-Factor App code structure, ability to write Dockerfiles.

**Scenario 2: IaaS to Managed Service**

- Trigger: Repeated incidents from self-managed DB failover, difficulty hiring a DBA.
- Path: EC2 PostgreSQL → RDS PostgreSQL (pg_dump/pg_restore).
- Prerequisite: No custom extension modules, compatible RDS version.

**Scenario 3: SaaS to Self-hosted**

- Trigger: SaaS vendor raises prices 30%+ annually, or API limitations block workflow automation.
- Path: Notion → self-hosted wiki (e.g., Outline) + S3 + RDS.
- Prerequisite: Export API enables data migration, team has operations capacity.

Model transitions always cost money. The key is defining the trigger quantitatively in advance: "when monthly cost exceeds $X" or "when operational incidents exceed Y per month." Pre-set thresholds prevent emotional decision-making.

## Making Selection Criteria Numeric

Choosing IaaS, PaaS, or SaaS by gut feeling leads to inconsistent decisions across teams. In practice, fixing criteria in a scoring table works better. The table below quantifies common evaluation questions.

| Evaluation Item | Question | IaaS Score Tendency | PaaS Score Tendency | SaaS Score Tendency |
| --- | --- | --- | --- | --- |
| Deployment Speed | Can we start today and deploy next week? | 2 | 4 | 5 |
| Control | Do we need fine OS/network control? | 5 | 3 | 1 |
| Ops Burden | Can we handle on-call and patching? | 1 | 3 | 5 |
| Customization | Do we need kernel/runtime modifications? | 5 | 2 | 1 |
| Regulatory Compliance | Do we need audit trails and isolation? | 4 | 3 | 2 |
| Vendor Lock-in | Can we tolerate platform dependency? | 3 | 2 | 1 |

Scores are relative comparison tools, not absolutes. For example, a small team weighting "Ops Burden" highly will find PaaS or SaaS the realistic choice.

### Detailed Responsibility Matrix

| Layer | User Responsibility on IaaS | User Responsibility on PaaS | User Responsibility on SaaS |
| --- | --- | --- | --- |
| Network | VPC/firewall/routing | App-level access policies | User access policies |
| Compute | Instance/OS patching | App code/build artifacts | None |
| Data | Encryption/backup/permissions | Data schema/permissions | Data classification/retention |
| Observability | Agent install/collection | App logs/metrics | Audit log review |
| Cost | Instance sizing/reservations | Usage tracking | License/seat management |

This table is useful because it exposes responsibility gaps quickly. For example, if you chose PaaS but assumed the platform handles all backups automatically, you may fail to guarantee a viable recovery point objective (RPO) during an incident.

### Hybrid Model Strategy

Real organizations rarely pick one model exclusively. They mix:

- Auth/collaboration: SaaS
- Customer-facing API: PaaS or container platform
- Data pipelines: IaaS + managed services

Mixing is fine, but without a responsibility document per service, incident response boundaries collapse. Attach a responsibility table like the following next to every architecture diagram:

```json
{
  "service": "customer-api",
  "model": "PaaS",
  "owner_team": "platform-app",
  "shared_responsibility": {
    "provider": ["runtime_patch", "base_network"],
    "customer": ["app_security", "data_classification", "iam_policy"]
  }
}
```

With this document in place, audit responses, incident analysis, and team handoffs all improve simultaneously. The purpose of model selection is not adopting the latest technology—it is increasing operational predictability.

## Checklist

- [ ] Each workload mapped to the right model.
- [ ] Vendor lock-in evaluated.
- [ ] Cost simulated, not just listed.
- [ ] Operational headcount lined up.

## Practice Problems

1. Compare hosting a database on IaaS vs PaaS.
2. Name one workload that is a *bad fit* for FaaS.
3. Why is data export a non-negotiable SaaS requirement?

## Wrap-up and Next Steps

Once you pick a model, the next question is *where it runs*. The next post covers Regions and Availability Zones.

## Answering the Opening Questions

- **Why do EC2, Heroku, and Notion—all cloud services—feel so different?**
  - EC2 is IaaS where you manage the virtual machine directly. Heroku is PaaS that automates deployment once you choose a language and runtime. Notion is SaaS where users consume a finished collaboration tool. Same cloud, but vastly different abstraction levels and operational responsibility.
- **Where does user responsibility end and provider responsibility begin for IaaS, PaaS, and SaaS?**
  - A small team building everything on IaaS slows deployment; forcing PaaS constraints costs adaptation time. The choice depends on development capability, regulatory requirements, and operations team size.
- **How should you choose a model based on organization size and workload characteristics?**
  - IaaS gives fine-grained control but heavy operational burden. PaaS offers fast deployment but platform constraints. SaaS is immediately usable but limited in customization. Understanding each model's tradeoffs and matching them to your team's situation is key.
<!-- toc:begin -->
## In this series

- [Cloud Computing 101 (1/10): What is Cloud Computing?](./01-what-is-cloud-computing.md)
- **IaaS, PaaS, SaaS (current)**
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

- [NIST SP 800-145 — service models](https://csrc.nist.gov/publications/detail/sp/800-145/final)
- [AWS — types of cloud computing](https://aws.amazon.com/types-of-cloud-computing/)
- [Heroku — platform overview](https://devcenter.heroku.com/categories/platform)
- [Vercel — serverless functions](https://vercel.com/docs/functions)

Tags: Cloud, IaaS, PaaS, SaaS, Architecture
