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

This is post 2 in the Cloud Computing 101 series.

In this post, we'll compare service models through control, speed, lock-in, and operational burden so you can match them to real workloads.

> Cloud service models are easiest to understand as operating boundaries: the more the provider runs for you, the less control you keep and the faster you usually move.

## Questions to Keep in Mind

- What boundary should you inspect first when applying IaaS, PaaS, SaaS?
- Which signal should the example or diagram make visible for IaaS, PaaS, SaaS?
- What failure should be prevented first when IaaS, PaaS, SaaS reaches a real system?

## Big Picture

![cloud computing 101 chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/cloud-computing-101/02/02-01-concept-at-a-glance.en.png)

*cloud computing 101 chapter 2 flow overview*

This picture places IaaS, PaaS, SaaS inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The choice between IaaS, PaaS, and SaaS is a statement about who runs what, not about which is objectively better.

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

## Five Common Mistakes

1. **Treating a PaaS like a VM.**
2. **Going IaaS without enough operations headcount.**
3. **Ignoring data lock-in when adopting SaaS.**
4. **Underestimating cold starts on FaaS.**
5. **Mixing models without a clear responsibility boundary.**

## How This Shows Up in Production

Early-stage startups run on PaaS like Heroku or Render. As they grow they move workloads to IaaS such as AWS with EKS, while keeping office tools on SaaS.

## How a Senior Engineer Thinks

- Self-host only what you do *better* than the provider.
- The PaaS-to-IaaS jump is a cost-vs-control decision.
- SaaS includes vendor risk in the price.
- FaaS is great for event-driven workloads.
- Abstraction = freedom *and* lock-in.

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

- **What boundary should you inspect first when applying IaaS, PaaS, SaaS?**
  - The article treats IaaS, PaaS, SaaS as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for IaaS, PaaS, SaaS?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when IaaS, PaaS, SaaS reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

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
