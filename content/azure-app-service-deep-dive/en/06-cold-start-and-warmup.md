---
title: Cold start and warmup — why the first request is expensive
series: azure-app-service-deep-dive
episode: 6
language: en
status: ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- Azure
- App Service
- Distributed Systems
- Platform Engineering
last_reviewed: '2026-04-29'
---

# Cold start and warmup — why the first request is expensive

## Source Version

This post grounds its claims in the following public sources.

- Microsoft Learn — Azure App Service documentation (https://learn.microsoft.com/azure/app-service)
- Project Kudu (https://github.com/projectkudu/kudu) — only for deployment-engine and Windows-sandbox context

Microsoft doesn't publicly document the full implementation details of the App Service Front-End, Worker, and File Server layers.
In this series, Learn is the primary source of truth, and Kudu material is used only as supporting evidence where it is actually public.

> Azure App Service Deep Dive series (6/6)

The last question in this series is the most visible one.

**Why is the first request so expensive,
and how does App Service try to reduce that cost?**

Cold start is not a vague symptom.
It means there is no warm execution unit ready yet,
or the new process or container has not finished becoming traffic-eligible.

---

## The cold path and the warm path

![The cold path and the warm path](../../../assets/azure-app-service-deep-dive/06/06-01-the-cold-path-and-the-warm-path.en.png)
That one diagram is the whole story.
The cost the user feels on the first request is usually the cost of turning an execution unit from “not ready” into “ready.”

---

## Are warm-up signals the same on Windows and Linux?

No.
The goal is the same.
The mechanisms are not.

### Windows code apps

- IIS `applicationInitialization` is available
- Always On reduces idle unload behavior

### Linux apps

- the platform can repeatedly call `WEBSITE_WARMUP_PATH`
- startup timeout is shaped by `WEBSITES_CONTAINER_START_TIME_LIMIT`

![Linux apps](../../../assets/azure-app-service-deep-dive/06/06-02-linux-apps.en.png)
You need that split in your head before you design a warm-up strategy.

---

## What Always On really does

Microsoft documentation and the App Service team blog describe Always On in similar terms.
It reduces idle cooling by periodically pinging the app.

Operationally,
that means:

- the app is less likely to fall into an idle cold path
- app-pool unload or equivalent idle behavior becomes less visible
- worst-case first-request latency often improves

![What Always On really does](../../../assets/azure-app-service-deep-dive/06/06-03-what-always-on-really-does.en.png)
Always On does not erase all startup cost.
Redeployments,
restarts,
new scale-out workers,
and container recycles can still require explicit warm-up logic.

---

## When Windows needs `applicationInitialization`

Sometimes hitting the root URL is not enough to fully prepare the app.
Examples include:

- opening the first database pool
- priming a large cache
- template compilation
- JIT or other expensive startup paths

That is where IIS `applicationInitialization` matters.

![When Windows needs applicationInitialization](../../../assets/azure-app-service-deep-dive/06/06-04-when-windows-needs-applicationinitializa.en.png)
Endpoint design matters here.
Return success too early and incomplete instances start receiving traffic.
Make the endpoint too heavy and warm-up itself becomes a bottleneck.

---

## Linux warm-up path and startup timeout

The App Service app-settings reference gives the critical Linux startup contract.

- the platform can repeatedly hit `WEBSITE_WARMUP_PATH`
- without `WEBSITE_WARMUP_STATUSES`, almost any response can count as readiness
- `WEBSITE_WARMUP_STATUSES` can narrow accepted status codes
- `WEBSITES_CONTAINER_START_TIME_LIMIT` bounds how long the platform waits

![Linux warm-up path and startup timeout](../../../assets/azure-app-service-deep-dive/06/06-05-linux-warm-up-path-and-startup-timeout.en.png)
That model creates two very common Linux mistakes.

1. the app is not ready, but a permissive response still gets treated as readiness
2. the startup limit is too short, so the app loops through startup failures

---

## What makes cold start expensive

The first-request cost is usually a stack of smaller costs.

- worker or container allocation
- process startup
- framework bootstrap
- dependency connection warm-up
- cache, module import, or JIT work
- health and warm-up eligibility gates

![What makes cold start expensive](../../../assets/azure-app-service-deep-dive/06/06-06-what-makes-cold-start-expensive.en.png)
That is why cold-start reduction is rarely a single magic setting.
It is an app-platform contract problem.

---

## What a good warm-up endpoint looks like

A warm-up endpoint overlaps with a health endpoint,
but the purpose is not identical.
Its job is to say whether the app is truly ready to enter traffic.

A good warm-up endpoint usually has these properties.

- the platform can call it without authentication friction
- it includes the critical dependency readiness checks
- it does not return success before startup is actually complete
- it avoids repeating unnecessarily heavy work

If that endpoint is inaccurate,
you usually get one of two bad outcomes.

- success returns too early and incomplete workers receive traffic
- success returns too late and scale-out or slot swap slows down badly

---

## Why deployment slots help so much

Slots let the platform pay the cold-start cost off the production URL.

![Why deployment slots help so much](../../../assets/azure-app-service-deep-dive/06/06-07-why-deployment-slots-help-so-much.en.png)
That is the value proposition in one line.
If staging workers have already booted and passed warm-up,
production users are much less likely to experience that startup cost directly.

This is why episode 4 and episode 6 are really two halves of the same story.

---

## Always On, warm-up, and health are not the same thing

These three features do related work.
They do not do the same work.

- **Always On**: reduce idle coldness
- **warm-up path**: decide readiness during startup
- **health check**: decide whether the instance should keep receiving traffic

![Always On, warm-up, and health are not the same thing](../../../assets/azure-app-service-deep-dive/06/06-08-always-on-warm-up-and-health-are-not-the.en.png)
If you blur them together,
the settings may be enabled while the behavior still looks wrong.
That is where questions like “Always On is enabled, so why is deployment still slow?” come from.

---

## Episode 6 wrap

Compressed into one paragraph,
the core point is this.

> In App Service, cold start is the cost of serving a request before a warm worker is already ready, or before a new process or container has finished its readiness path. On Windows, `applicationInitialization` and Always On are the key tools. On Linux, `WEBSITE_WARMUP_PATH`, `WEBSITE_WARMUP_STATUSES`, and `WEBSITES_CONTAINER_START_TIME_LIMIT` shape the startup contract. Always On reduces idle coldness, but startup readiness after deployment, restart, or scale-out still depends on explicit warm-up behavior.

That closes the series.
At this point,
App Service should look less like “a place to push code” and more like a full platform where Front-End routing,
workers,
sandbox rules,
Kudu,
shared storage,
autoscale,
and warm-up all connect.

---

## Where this fits in the series

This final post explains the startup window that the earlier episodes kept pointing toward: the time between worker allocation and traffic eligibility.
Read back through the series and the whole model lines up: entry, routing, execution boundary, deployment, scaling, and warm-up are all parts of one App Service operating system.

---

## Documented Behavior Summary

- Always On reduces idle cooling, but it doesn't remove startup cost after deployment, restart, or new scale-out allocation.
- Linux App Service exposes startup-readiness controls through `WEBSITE_WARMUP_PATH`, `WEBSITE_WARMUP_STATUSES`, and `WEBSITES_CONTAINER_START_TIME_LIMIT`.
- Windows App Service can use IIS `applicationInitialization` and slot warm-up behavior to prepare instances before production traffic arrives.
- Slot swap helps by warming the source-slot instances first and only then switching Front-End routing rules.

<!-- toc:begin -->
## In this series

- [App Service platform architecture — Front-End, Worker, File Server](./01-platform-architecture.md)
- [Front-End and ARR — how a request reaches a worker](./02-front-end-and-arr.md)
- [Workers and the sandbox — where user code actually runs](./03-worker-and-sandbox.md)
- [Deployment and Kudu — build, sync, release from the inside](./04-deployment-and-kudu.md)
- [Scaling internals — how Scale Out decisions become new workers](./05-scaling-internals.md)
- **Cold start and warmup — why the first request is expensive (current)**

<!-- toc:end -->

---

## References

### Primary sources
- [Environment variables and app settings reference](https://learn.microsoft.com/azure/app-service/reference-app-settings)
- [Deploy staging slots in Azure App Service](https://learn.microsoft.com/azure/app-service/deploy-staging-slots)
- [IIS 8.0 Application Initialization](https://learn.microsoft.com/iis/get-started/whats-new-in-iis-8/iis-80-application-initialization)

### Secondary sources
- [Robust Apps for the Cloud — App Service team blog](https://azure.github.io/AppService/2020/05/15/Robust-Apps-for-the-cloud.html)

### Related Series
- [Azure App Service 101 — Request Lifecycle](../../azure-app-service-101/en/02-request-lifecycle.md)
- [Azure Functions Deep Dive — Cold start and Placeholder Mode](../../azure-functions-deep-dive/en/06-cold-start-placeholder.md)

Tags: Azure, App Service, Distributed Systems, Platform Engineering
