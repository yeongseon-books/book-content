---
series: devops-101
episode: 3
title: "DevOps 101 (3/10): CD and Deployment Strategies"
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
  - CD
  - Deployment
  - BlueGreen
  - Canary
seo_description: Compare Rolling, Blue-Green, and Canary deployments and design a safe automated release flow.
last_reviewed: '2026-05-15'
---

# DevOps 101 (3/10): CD and Deployment Strategies

Many teams say they fear deployment, but the deeper fear is usually rollback. If a release goes bad, how quickly can you stop the blast radius, restore service, and explain what changed? Without a good answer, every deployment feels like a gamble.

That is why continuous delivery is not just about automation. It is about making releases small, observable, and reversible so production changes become a routine operating motion instead of a high-drama event.

This is post 3 in the DevOps 101 series. In this chapter, we compare deployment strategies, separate code deployment from feature release, and show what a safe promotion and rollback path looks like in practice.

## Questions to Keep in Mind

- What boundary should you inspect first when applying CD and Deployment Strategies?
- Which signal should the example or diagram make visible for CD and Deployment Strategies?
- What failure should be prevented first when CD and Deployment Strategies reaches a real system?

## Big Picture

![devops 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/devops-101/03/03-01-concept-at-a-glance.en.png)

*devops 101 chapter 3 flow overview*

This picture places CD and Deployment Strategies inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

> The core of CD and Deployment Strategies is not the feature name; it is deciding what to verify at each boundary and which signal to keep.

## Questions this article answers

- What does *CD* share with *CI*, and how is it different?
- What risks are *Rolling*, *Blue-Green*, and *Canary* strategies each meant to reduce?
- Why should *code deployment* be separated from *feature activation*?
- Why is *rollback* a core requirement in deployment design rather than an afterthought?
- What traps do teams still miss in practice even after they automate deployment?

## Why It Matters

Deployment is *the most dangerous moment*. A good strategy *shrinks the blast radius* and *makes rollback easy*.

> *Deployability* and *feature activation* must be *separated*.

## Concept at a Glance

## Key Terms

- **CD**: *Continuous Delivery/Deployment*. *Automated deployment*.
- **Rolling**: replace servers *one at a time* with the new version.
- **Blue-Green**: keep *two environments* and *switch traffic* between them.
- **Canary**: send *a slice of traffic* to the new version.
- **Feature flag**: *deploy the code* but *toggle the feature*.

## Before/After

**Before (big-bang deploy)**

```text
- All servers move to the new version *at once*
- A problem means *full outage*
- Rollback takes *more than 30 minutes*
```

**After (Canary + flag)**

```text
- New version receives *10%* of traffic
- After 5 minutes of monitoring, *50% then 100%*
- On failure, *flag off* blocks it *immediately*
```

## Hands-on: Five Steps to a Safe Deploy

### Step 1 - Auto-deploy to staging

```yaml
deploy-stage:
  if: github.ref == 'refs/heads/main'
  runs-on: ubuntu-latest
  steps:
    - run: ./deploy.sh stage
```

### Step 2 - Smoke test

```bash
curl -f https://stage.example.com/health || exit 1
pytest tests/smoke/ --base-url=https://stage.example.com
```

### Step 3 - Canary (10%)

```bash
kubectl set image deploy/api api=myapp:v2 --record
kubectl scale deploy/api-v2 --replicas=1   # 10%
```

### Step 4 - Monitor for 5 minutes

```text
- error rate < 0.1%
- p95 latency < 200ms
- 5xx counts within normal range
```

### Step 5 - Promote or rollback

```bash
# OK
kubectl scale deploy/api-v2 --replicas=10

# NG
kubectl rollout undo deploy/api
```

## The First 10 Minutes After Deploy Matter Most

A canary does not make a release safe by itself. What matters is whether the team checks the same signals in the same order during the first few minutes after traffic shifts. A simple post-deploy sequence like the one below makes promotions much more predictable.

```text
T+0m  Confirm the health endpoint returns 200
T+2m  Compare 5xx rate and p95 latency to baseline
T+5m  Search new-version logs for fresh exception patterns
T+7m  Check DB connection pool, queue depth, cache hit ratio
T+10m Promote further or roll back
```

This sequence works because it checks dependencies as well as the application itself. Many bad deploys do not fail at the HTTP layer first. They show up as connection pressure, queue growth, or cache churn before customers describe the symptom clearly.

## Design Rollback Before You Need It

Rollback is not an after-the-fact emergency button. It has to exist in the release design before the deploy starts. Application rollback and database rollback are different problems, and treating them as one often extends incidents.

A practical release checklist usually includes these questions:

- Can a feature flag contain the blast radius immediately?
- Does rolling back the image restore the service by itself?
- Are schema changes backward compatible via an expand/contract pattern?
- After rollback, is the path to redeploy forward also tested?

If those answers are vague, the deployment is still risk-heavy even if the automation looks polished.

## What to Notice in This Code

- *Staging* must mirror *production*.
- The *baseline metrics* for the canary are *defined in advance*.
- *Rollback commands* live in the *runbook*.

## Five Common Mistakes

1. **Automated CI but *manual CD*.** Humans inject *mistakes*.
2. **Staging differs from production.** Bugs become *unreproducible*.
3. **Promoting to 100% *without checking metrics* after canary.** The canary loses its meaning.
4. **Never cleaning up feature flags.** After six months you *cannot tell which flags are alive*.
5. **No rollback drill.** A real incident becomes *the first practice*.

## How This Shows Up in Production

Large services automate *Canary Analysis (CAA)* with tools that compare metrics for them. Spinnaker and Argo Rollouts are common examples.

## How a Senior Engineer Thinks

- *Every deploy* must be *reversible*.
- *Feature releases* go through *flags*. Decoupled from deployment.
- *Canary metrics* are agreed by the *whole team*.
- *DB migrations* must be *backward compatible*.
- *Higher deploy frequency* makes things *safer*.

## Checklist

- [ ] *Auto-deploy to staging* exists.
- [ ] *Smoke tests* are automated.
- [ ] *Rollback commands* are *documented*.
- [ ] A *feature flag* system exists.

## Practice Problems

1. *Sketch* the deploy stages of your service.
2. Add *rollback commands* to the *runbook*.
3. Agree on *three canary metrics* with your team.

## Wrap-up and Next Steps

CD is *a stream of small, reversible changes*. In the next post we cover *configuration management* across environments.

## Answering the Opening Questions

- **What boundary should you inspect first when applying CD and Deployment Strategies?**
  - The article treats CD and Deployment Strategies as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **Which signal should the example or diagram make visible for CD and Deployment Strategies?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **What failure should be prevented first when CD and Deployment Strategies reaches a real system?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [DevOps 101 (1/10): What Is DevOps?](./01-what-is-devops.md)
- [DevOps 101 (2/10): CI Pipeline](./02-ci-pipeline.md)
- **CD and Deployment Strategies (current)**
- Environments and Configuration (upcoming)
- Infrastructure as Code (upcoming)
- Containers and Build (upcoming)
- Monitoring and Alerting (upcoming)
- Logging and Analysis (upcoming)
- Incident Response and On-Call (upcoming)
- An Operable DevOps Flow (upcoming)

<!-- toc:end -->

## References

- [Martin Fowler — Continuous Delivery](https://martinfowler.com/bliki/ContinuousDelivery.html)
- [Argo Rollouts](https://argoproj.github.io/rollouts/)
- [LaunchDarkly — Feature Flags](https://launchdarkly.com/blog/what-are-feature-flags/)
- [Spinnaker](https://spinnaker.io/)

Tags: DevOps, CD, Deployment, BlueGreen, Canary
