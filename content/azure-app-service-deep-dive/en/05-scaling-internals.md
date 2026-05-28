---
title: "Azure App Service Deep Dive (5/6): Scaling internals — how Scale Out decisions become new workers"
series: azure-app-service-deep-dive
episode: 5
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- Azure
- App Service
- Distributed Systems
- Platform Engineering
last_reviewed: '2026-05-15'
seo_description: See how Azure Monitor autoscale changes App Service Plan instance count and when new workers actually become traffic-ready.
---

# Azure App Service Deep Dive (5/6): Scaling internals — how Scale Out decisions become new workers

Autoscale looks instantaneous in architecture diagrams, but production behavior is slower and more mechanical than that. There is a real control loop between a threshold crossing and a worker that is healthy enough to receive traffic.

This is the fifth post in the Azure App Service Deep Dive series.

## Source Version

This post grounds its claims in the following public sources.

- Microsoft Learn — Azure App Service documentation (https://learn.microsoft.com/azure/app-service)
- Project Kudu (https://github.com/projectkudu/kudu) — only for deployment-engine and Windows-sandbox context

Microsoft doesn't publicly document the full implementation details of the App Service Front-End, Worker, and File Server layers.
In this series, Learn is the primary source of truth, and Kudu material is used only as supporting evidence where it is actually public.

> Azure App Service Deep Dive series (5/6)

The intro series covered how to choose Scale Up versus Scale Out.
This post asks the next question.

**After the platform decides to scale out,
how does that decision become more real worker capacity?**

At the public-documentation level,
the safe facts are clear.

- scale up changes the App Service Plan SKU
- scale out changes instance count
- Azure Monitor autoscale evaluates autoscale rules
- the target is the App Service Plan, not an individual app

This episode goes one level deeper without inventing private internals.
The goal is to map the **publicly observable scale-decision loop** into a usable worker-pool mental model.

![azure app service deep dive chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/azure-app-service-deep-dive/05/05-01-the-control-path-in-one-diagram.en.png)
*azure app service deep dive chapter 5 flow overview*

## Questions to Keep in Mind

- On what metric sources and what cadence does auto-scale evaluate rules?
- Scale-out and scale-up are not the same decision tree — who decides what, and how?
- When should you turn per-site scaling on, and when is it dangerous?

## The control path in one diagram

Two things matter here.

1. separate the decision engine from the execution substrate
2. stop imagining that the app directly “creates VMs” for itself

Scale-out is better understood as a control-plane change to desired instance count,
followed by App Service making more worker capacity available to that plan.

---

## What scale up and scale out actually change

![Targets changed by scale up and scale out](https://yeongseon-books.github.io/book-public-assets/assets/azure-app-service-deep-dive/05/05-02-what-scale-up-and-scale-out-actually-cha.en.png)

*Targets changed by scale up and scale out*
The Learn documentation states the difference plainly.

- **Scale up**: move to a larger tier or SKU with more CPU, memory, or features
- **Scale out**: increase the number of VM instances running the app

Translated into runtime terms:

- scale up changes the size of a worker
- scale out changes how many workers the app can run across

That is why a memory bottleneck and a concurrency bottleneck can both look like “slowness” but still require different expansion paths.

---

## Autoscale attaches to the plan, not the app

This is one of the most common App Service misunderstandings.
Even if you enter autoscale from an app-centric portal experience,
the real target resource is the **App Service Plan**.

![Autoscale rules attached to the plan](https://yeongseon-books.github.io/book-public-assets/assets/azure-app-service-deep-dive/05/05-03-autoscale-attaches-to-the-plan-not-the-a.en.png)

*Autoscale rules attached to the plan*
That structure has consequences.
If several apps share the same plan,
one app's burst can drive plan-level scaling,
and the added capacity becomes shared plan capacity.

That is one reason noisy-neighbor thinking still matters inside a shared plan.

---

## What Azure Monitor autoscale actually does

The Azure Monitor autoscale documentation is explicit about the rule engine.

- metrics or schedules are evaluated
- minimum, default, and maximum counts are enforced
- scale-out can trigger when any scale-out rule is met
- scale-in requires all scale-in rules to be met

![Autoscale loop with metrics and cooldown](https://yeongseon-books.github.io/book-public-assets/assets/azure-app-service-deep-dive/05/05-04-what-azure-monitor-autoscale-actually-do.en.png)

*Autoscale loop with metrics and cooldown*
That logic matters operationally.
Scale-out behaves like OR.
Scale-in behaves like AND.
Expansion therefore tends to be faster,
while contraction should remain more conservative.

The autoscale documentation adds one more crucial detail.
The autoscale job runs roughly every **30 to 60 seconds** depending on resource type,
and after a scale action it waits through the configured cooldown before attempting another one.
This is a periodic control loop, not an interrupt-driven instant reaction.

---

## What the autoscale resource actually contains

The public `Microsoft.Insights/autoscaleSettings` schema tells you what App Service autoscale really is.

- `targetResourceUri` — the resource being scaled
- `profiles` — default, fixed-date, or recurring scaling policies
- `capacity.minimum/default/maximum` — lower bound, fallback, and ceiling
- `rules[].metricTrigger` — which metric is evaluated and over what observation window
- `rules[].scaleAction` — how much to change and what cooldown to apply

So autoscale is not just a portal toggle.
It is an ARM resource with explicit evaluation windows and explicit scale actions.

---

## The metric window shapes reaction speed

Autoscale rules are not only thresholds.
The documentation makes you read `timeGrain`, `timeWindow`, `statistic`, and `timeAggregation` together.

- `timeGrain` — sampling interval
- `timeWindow` — how far back autoscale looks
- `statistic` / `timeAggregation` — how samples are combined

That means even the same “CPU > 80%” rule can behave very differently depending on whether it is based on a 1-minute sample inside a 10-minute window or a much shorter observation window.
Autoscale reacts to signals that have already been sampled and aggregated,
not to the very first transient spike.

---

## Cooldown exists to protect stability, not speed

The autoscale docs explicitly apply cooldown to both scale-out and scale-in actions.
The schema examples commonly show `PT5M`.

Operationally, cooldown means:

- let metrics settle after adding or removing capacity
- reduce back-to-back oscillation
- account for the fact that new App Service workers still need startup and warm-up time

That is why real scaling latency is not just “when the threshold was crossed.”
It is better understood as `timeWindow + evaluation cadence + cooldown + worker readiness`.

---

## What “adding a worker” means in practice

The public docs do not expose every low-level placement detail.
They still support a sound mental model.

1. autoscale or a manual action raises the plan's desired count
2. the App Service control plane applies that desired state
3. the plan gains more worker capacity
4. the Front-End starts sending traffic to the new healthy workers

![Desired instance count becoming new workers](https://yeongseon-books.github.io/book-public-assets/assets/azure-app-service-deep-dive/05/05-05-what-adding-a-worker-means-in-practice.en.png)

*Desired instance count becoming new workers*
That is as far as you need to go without drifting into undocumented internals.

---

## Why autoscale should be read as a feedback loop

Autoscale is reactive,
not predictive.

![Scaling feedback loop with lag and cooldown](https://yeongseon-books.github.io/book-public-assets/assets/azure-app-service-deep-dive/05/05-06-why-autoscale-should-be-read-as-a-feedba.en.png)

*Scaling feedback loop with lag and cooldown*
That is why predictable spikes are safer with pre-scaling.
Metrics need time to accumulate.
Rules need time to evaluate.
Cooldown may still be active.
New workers still need time to become ready.

Ignore that lag,
and you get the familiar complaint:
“autoscale was enabled,
but the first few minutes still hurt.”

---

## Health and readiness are the real end of scale-out

Adding a worker does not mean that worker can instantly receive user traffic.
From the Front-End's perspective,
the worker must first become eligible.

![New worker entering the healthy pool](https://yeongseon-books.github.io/book-public-assets/assets/azure-app-service-deep-dive/05/05-07-health-and-readiness-are-the-real-end-of.en.png)

*New worker entering the healthy pool*
So the real end of scale-out is not the new instance count on paper.
It is the moment the new worker enters the healthy routing pool.

That is where the public scaling story stops: instance count on paper only matters once the newly allocated worker becomes traffic-eligible.

---

## What shared plans do to scaling behavior

A shared App Service Plan can be cost-efficient.
It also changes how you should read scaling.

- autoscale reacts to plan-level resource signals
- workers are plan-level capacity
- apps with different traffic patterns can interfere with each other

That means one app's scale event can reshape the resource curve of the whole plan.
From a deep-dive perspective,
“my app scales” is less accurate than,
“my plan scales and my app expands inside that plan.”

---

## Why scale-in is the riskier half

Scale-out adds capacity.
Scale-in removes active capacity.

That makes scale-in inherently riskier.

- users may still be pinned through affinity
- long requests may still be running
- burst traffic may not have fully cooled down

That is why autoscale best-practice guidance treats scale-in more conservatively.

The autoscale engine also checks for flapping.
If a scale-in result would immediately imply that the opposite scale-out rule should fire,
autoscale can defer the scale-in or reduce it less aggressively.
So scale-in is not merely “scale-out in reverse.”
It is a more defensive action path.

---

## The best public evidence is in the logs

The most valuable deep-dive surface here is the autoscale diagnostic log stream.
Microsoft documents two log categories for autoscale settings:

- `AutoscaleEvaluationsLog` — which rules and metrics were evaluated
- `AutoscaleScaleActionsLog` — which scale action was initiated and how it completed

The Azure activity log also records scale-up and scale-down initiated/completed events.

That means you do not have to guess why an App Service Plan scaled.
At the public-documentation layer,
you can inspect the autoscale setting resource, its evaluation logs, its scale-action logs, and the activity log.

---

## Episode 5 wrap

Compressed into one paragraph,
the core idea is this.

> In App Service, scale-out is not an app directly spinning up servers. Azure Monitor autoscale or a manual change updates the App Service Plan's desired instance count, the App Service control plane applies that desired state, and additional worker capacity becomes available to the plan. Only after the new worker finishes startup and passes readiness checks does the Front-End begin routing real traffic to it. Scale up changes SKU; scale out changes worker count; both are best understood at plan scope.

The control-plane story ends there. The remaining latency users feel lives in the startup and readiness window between worker allocation and traffic eligibility.

---

## Where this fits in the series

This post translates the intro-series scaling guidance into the internal App Service control path. Its value is separating scale-out decisions from the later startup-readiness window, so instance allocation and traffic eligibility do not collapse into the same mental model.

---

## Documented Behavior Summary

- App Service autoscale targets the App Service Plan, not an individual app.
- Azure Monitor autoscale uses a periodic evaluation loop, observation windows, cooldowns, and anti-flapping behavior.
- Scale-out can trigger when any scale-out rule matches, while scale-in requires all scale-in rules to match.
- `AutoscaleEvaluationsLog`, `AutoscaleScaleActionsLog`, and the activity log expose the actual decision trail.

### Track auto-scale rules and instance count

```bash
az monitor autoscale show -g my-rg -n my-app-autoscale

az monitor metrics list \
  --resource $(az appservice plan show -n my-plan -g my-rg --query id -o tsv) \
  --metric "CpuPercentage,HttpQueueLength" --interval PT1M -o table
```

## Operational checklist

- [ ] Measured a steady-state baseline for scale-out metrics and thresholds
- [ ] Recorded the per-site scaling decision in an ADR
- [ ] Verified SIGTERM handlers exist for graceful drain on scale-in
- [ ] Put scale-event alerts and instance-count graphs on the dashboard
- [ ] Split runbooks for scale-up (SKU change) and scale-out

## Answering the Opening Questions

- **What do scale-up and scale-out actually change in App Service?**
  - Scale-up increases a single worker's CPU, memory, and SKU tier, while scale-out increases the number of workers the App Service Plan uses. That's why you shouldn't look at memory pressure and worker concurrency shortage through the same scaling button—instead, judge which resource hit its limit first and choose the appropriate axis.
- **Why should autoscale rules be seen as attached to the App Service Plan rather than to an app?**
  - Because the autoscale target resource is the plan, what actually changes is shared worker capacity—not a dedicated server for one app. So one app's burst can shake the capacity used by other apps on the same plan, and scale events are more accurately read from plan-level metrics and activity logs than from a single app's logs.
- **What cadence and observation window does Azure Monitor autoscale use to evaluate rules?**
  - Azure Monitor autoscale isn't a feature that sees a metric once and reacts immediately—it's an engine that evaluates rules periodically. Because `timeGrain`, `timeWindow`, `statistic`, and `cooldown` together shape reaction speed, the actual perceived scaling time should be understood as the accumulated result of observation window, evaluation cadence, cooldown, and readiness—not just a single threshold crossing.

<!-- toc:begin -->
## In this series

- [Azure App Service Deep Dive (1/6): App Service platform architecture — Front-End, Worker, File Server](./01-platform-architecture.md)
- [Azure App Service Deep Dive (2/6): Front-End and ARR — how a request reaches a worker](./02-front-end-and-arr.md)
- [Azure App Service Deep Dive (3/6): Workers and the sandbox — where user code actually runs](./03-worker-and-sandbox.md)
- [Azure App Service Deep Dive (4/6): Deployment and Kudu — build, sync, release from the inside](./04-deployment-and-kudu.md)
- **Azure App Service Deep Dive (5/6): Scaling internals — how Scale Out decisions become new workers (current)**
- Azure App Service Deep Dive (6/6): Cold start and warmup — why the first request is expensive (upcoming)

<!-- toc:end -->

---

## References

### Primary sources
- [Understand autoscale settings in Azure Monitor](https://learn.microsoft.com/azure/azure-monitor/autoscale/autoscale-understanding-settings)
- [Diagnostic settings in autoscale](https://learn.microsoft.com/azure/azure-monitor/autoscale/autoscale-diagnostics)

### Secondary sources
- [Scale up an app in Azure App Service](https://learn.microsoft.com/azure/app-service/manage-scale-up)
- [Get started with autoscale in Azure](https://learn.microsoft.com/azure/azure-monitor/autoscale/autoscale-get-started)
- [Autoscale in Azure Monitor](https://learn.microsoft.com/azure/azure-monitor/autoscale/autoscale-overview)
- [Best practices for autoscale](https://learn.microsoft.com/azure/azure-monitor/autoscale/autoscale-best-practices)
- [Monitoring data reference for Azure Monitor](https://learn.microsoft.com/azure/azure-monitor/monitor-reference)
- [Architecture best practices for Azure App Service web apps](https://learn.microsoft.com/azure/well-architected/service-guides/app-service-web-apps)

### Related Series
- [Azure App Service 101 — Scaling 101](../../azure-app-service-101/en/07-scaling-101.md)
- [Azure Functions Deep Dive — Scaling internals](../../azure-functions-deep-dive/en/05-scaling-internals.md)

Tags: Azure, App Service, Distributed Systems, Platform Engineering
