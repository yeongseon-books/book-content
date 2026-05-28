---
series: devops-101
episode: 5
title: "DevOps 101 (5/10): Infrastructure as Code"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - DevOps
  - IaC
  - Terraform
  - Cloud
  - Automation
seo_description: Treat infrastructure as code with Terraform so changes are versioned, reviewable, and reproducible.
last_reviewed: '2026-05-15'
---

# DevOps 101 (5/10): Infrastructure as Code

Console-built infrastructure feels fast right up until you need the same environment again. Then you discover that the real system lives partly in screenshots, partly in memory, and partly in one person's habits.

Infrastructure as Code fixes that by moving cloud changes into the same review-and-history model we already expect from application code. The value is not the syntax itself. The value is repeatability, visibility, and safer change control.

This is the 5th post in the DevOps 101 series. In this chapter, we use Terraform to explain plan, apply, state, and remote backends as the operating model behind reproducible infrastructure.


![devops 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/devops-101/05/05-01-concept-at-a-glance.en.png)
*devops 101 chapter 5 flow overview*
> Infrastructure becomes an *asset*—not a hero's memory—when it *lives in code*, *passes review*, and *stays in sync* with reality.

## Questions to Keep in Mind

- What boundary should you inspect first when applying Infrastructure as Code?
- Which signal should the example or diagram make visible for Infrastructure as Code?
- What failure should be prevented first when Infrastructure as Code reaches a real system?

## Questions this article answers

- Why is *console-created infrastructure* so hard to reproduce in another environment?
- How does *IaC* improve change quality for the whole team rather than just making life easier for operators?
- How should you understand the basic *Terraform* flow around *plan* and *apply*?
- What is the *state* file, and why should it be managed in a *remote backend*?
- What traps still show up in practice after a team adopts *IaC*?

## Why It Matters

Console-built infrastructure exists *only in memory*. Replicating it elsewhere requires *clicking again*, and *drift* appears in between.

> *Code is the single source of truth (SSOT)*.

IaC means infrastructure—networks, servers, databases—lives in *version control* and *deploys via code*, not manual clicks. Changes are *reviewable*, *repeatable*, and *traceable*.

## Key Terms

- **IaC**: *Infrastructure as Code*. Define infrastructure *as code*.
- **Provider**: a cloud *adapter* like AWS or GCP.
- **Resource**: a *unit of creation* like an instance or bucket.
- **State**: a *record* of the current *real infrastructure*.
- **Module**: a *reusable bundle of infrastructure*.

## Before/After

**Before (console clicks)**

```text
- No record of *who* created what *when*
- Replicating to another region means *starting over*
- No change history
```

**After (Terraform)**

```hcl
# main.tf
resource "aws_s3_bucket" "logs" {
  bucket = "my-app-logs"
  tags   = { Env = "prod" }
}
```

## Hands-on: Five Steps with Terraform

### Step 1 - Define the provider

```hcl
terraform {
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
}
provider "aws" { region = "us-east-1" }
```

### Step 2 - Write a resource

```hcl
resource "aws_s3_bucket" "logs" {
  bucket = "my-app-logs-${var.env}"
}
```

### Step 3 - Inspect the change with plan

```bash
terraform init
terraform plan
# Plan: 1 to add, 0 to change, 0 to destroy.
```

### Step 4 - Apply

```bash
terraform apply
# enters yes to actually create
```

### Step 5 - Reuse with modules

```hcl
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  version = "5.0.0"
  cidr    = "10.0.0.0/16"
}
```

## Remote State and Locking Come Before Scale

Local state feels acceptable during solo experiments, but the moment multiple engineers touch the same stack, state location and locking become operational issues. One person may be applying while another is planning from stale data, and the resulting diff becomes harder to trust.

That is why mature teams usually set up remote state before they expand their Terraform footprint. On AWS, the common starting point is S3 plus DynamoDB locking.

```hcl
terraform {
  backend "s3" {
    bucket         = "my-tf-state"
    key            = "network/prod.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}
```

The most important feature here is not storage. It is concurrency control. Without locking, teams stop trusting the plan output, which makes IaC automation more dangerous instead of safer.

## Use Plan as a Drift Detection Loop

IaC does not magically eliminate manual console changes. It gives you a better way to detect them. In practice, teams use `plan` not only before apply, but also as a repeated drift check in CI or scheduled reviews.

```bash
terraform plan -detailed-exitcode
# 0 = no changes
# 2 = drift or intentional change detected
# 1 = error
```

That single command is enough to tell you when code and reality no longer match. The operational value of IaC shows up in that loop as much as in the resource syntax.

## What to Notice in This Code

- *Plan* before *apply* — execute only after the change is *visually confirmed*.
- *State* lives in a *remote backend* (S3, GCS).
- *Modules* keep *per-environment differences* in *variables only*.

## Five Common Mistakes

1. **Keeping state *locally*.** It conflicts with teammates and risks *loss*.
2. **Storing *secrets* in plain text in state.** Use S3 backend with KMS encryption.
3. **Manual changes in the console.** *Drift* appears.
4. **No automation for `apply`.** Manual runs invite *typos and accidents*.
5. **Running `destroy` *directly against production*.** Environment separation plus an approval gate is mandatory.

## How This Shows Up in Production

Mature teams automate *PR-based plan/apply* with *Terraform Cloud* or *Atlantis*. *Infrastructure review* becomes equivalent to *code review*.

## How a Senior Engineer Thinks

- *The console is read-only*. Changes go through *code only*.
- *State* requires *backups and locking*.
- *Modules* enforce *team standards*.
- *Plan diffs* are core information for *PR review*.
- *Tag policies* track *cost and ownership*.

## Checklist

- [ ] *All infrastructure* is defined in code.
- [ ] *State* lives in a *remote backend*.
- [ ] *Plan* is auto-rendered on *PRs*.
- [ ] *Tag policies* are enforced.

## Practice Problems

1. Create a single *S3 bucket* with *Terraform*.
2. Parameterize the same code with *variables* and apply it to *dev/prod*.
3. Configure *remote state* on S3 + DynamoDB.

## Wrap-up and Next Steps

IaC is *reproducible infrastructure*. In the next post we cover *containers*, which deliver reproducibility for the *application*.

## Answering the Opening Questions

- **Why is infrastructure created through console clicks hard to reproduce in other environments?**
  - Console operations leave no code or history recording who changed what and when, and recreating the same configuration in another region or account easily introduces subtle differences. The article emphasizes drift and state because this is exactly where reproducibility breaks.
- **How does IaC connect to the entire team's change quality rather than just operations convenience?**
  - With IaC, infrastructure changes can be handled inside the same PR, plan review, policy checks, and approval flows as application code. The `terraform validate`, OPA tag policy, and remote state with locking examples are mechanisms that transform infrastructure changes from individual know-how into a team quality management concern.
- **How should you understand Terraform's basic flow centered on plan and apply?**
  - The basic flow is `init -> plan -> apply`, with the key habit being reviewing the change diff visually before apply. Adding S3 + DynamoDB remote backend, `plan -detailed-exitcode`, and module reuse turns a one-time execution into a continuously validated operational loop.
<!-- toc:begin -->
## In this series

- [DevOps 101 (1/10): What Is DevOps?](./01-what-is-devops.md)
- [DevOps 101 (2/10): CI Pipeline](./02-ci-pipeline.md)
- [DevOps 101 (3/10): CD and Deployment Strategies](./03-cd-and-deployment.md)
- [DevOps 101 (4/10): Environments and Configuration](./04-environments-and-config.md)
- **Infrastructure as Code (current)**
- Containers and Build (upcoming)
- Monitoring and Alerting (upcoming)
- Logging and Analysis (upcoming)
- Incident Response and On-Call (upcoming)
- An Operable DevOps Flow (upcoming)

<!-- toc:end -->

## References

- [Terraform docs](https://developer.hashicorp.com/terraform)
- [Terraform AWS Modules](https://registry.terraform.io/namespaces/terraform-aws-modules)
- [Atlantis](https://www.runatlantis.io/)
- [HashiCorp — IaC](https://www.hashicorp.com/resources/what-is-infrastructure-as-code)

Tags: DevOps, IaC, Terraform, Cloud, Automation
