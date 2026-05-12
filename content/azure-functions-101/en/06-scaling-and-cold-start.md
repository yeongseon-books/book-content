---
title: Scaling and Cold Starts — When Serverless Feels Fast and When It Doesn’t
series: azure-functions-101
episode: 6
language: en
status: publish-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- Azure
- Azure Functions
- Serverless
- Cloud
last_reviewed: '2026-04-29'
seo_description: 'Serverless is usually sold with one sentence: it scales automatically,
  and you only pay for what you use. True, but incomplete.'
---

# Scaling and Cold Starts — When Serverless Feels Fast and When It Doesn’t

Serverless is usually sold with one sentence: it scales automatically, and you only pay for what you use. True, but incomplete. In production, that sentence only becomes useful once you ask what signals drive scale-out, how much concurrency a single instance can absorb, and why the first request after idle time is sometimes noticeably slower.

This chapter revisits the hosting-plan decision from an operations angle. When traffic jumps abruptly, how do Consumption, Flex Consumption, Premium, and Dedicated react? Where does cold-start time actually go? And what should you change first if the first request is too slow?

This is the sixth post in the Azure Functions 101 series. Here, we turn scaling and cold starts into concrete operational trade-offs.

---

## Questions this chapter answers

- What signals does the Functions scale controller use to add instances?
- Where exactly does cold start happen, and what do you measure to see it?
- How much cold start does Premium's always-ready instances actually erase?
- What goes wrong when burst traffic scales instances too quickly?
- Which patterns put external dependencies (DB connections) on a collision course with scale?

## Scaling Has Two Axes — Instance Count and In-Instance Concurrency

“Scaling” hides two different controls.

- **Horizontal scaling (scale out)** — how many instances the app gets
- **In-instance concurrency** — how many invocations one instance handles at the same time

![Two scaling axes: instances and concurrency](../../../assets/azure-functions-101/06/06-01-scaling-has-two-axes-instance-count-and.en.png)

*Two scaling axes: instances and concurrency*
Plans differ in who controls those axes and how exposed they are.

| Plan | Scale-out model | What actually distinguishes it |
|---|---|---|
| Consumption | Platform-managed automatic scaling. Depending on the trigger/extension, the platform may use event-driven or target-based decisions | Instance count is abstracted away; concurrency is influenced mostly by runtime and trigger settings |
| Flex Consumption | Same platform-managed autoscaling foundation, but adds **per-function scale groups** and **configurable per-instance HTTP concurrency** | The differentiator is not “target-based scaling exists,” but **function-level isolation and concurrency control** |
| Premium | Platform-managed automatic scaling with warm capacity available | Always Ready and prewarmed instances reduce startup latency |
| Dedicated (App Service Plan) | Scale rules are user-defined through App Service autoscale, or managed manually | No scale-to-zero; reaction speed depends on the autoscale rules you configured |

So target-based scaling is not a Flex-only idea. It applies more broadly across supported triggers. What makes Flex stand out is per-function scaling behavior and the ability to tune HTTP concurrency per instance.

---

## How the Plans React to a Traffic Spike

Differences are easier to see on a timeline. Assume the app is idle, then at t=0 an HTTP spike arrives.

![Plan reactions to a traffic spike](../../../assets/azure-functions-101/06/06-02-how-the-plans-react-to-a-traffic-spike.en.png)

*Plan reactions to a traffic spike*
Operationally, the differences are straightforward.

- **Consumption**: scale to zero is normal, so cold starts are the easiest to observe.
- **Flex Consumption**: Always Ready is optional and can be set to 0, so cold starts do not disappear by default. The big advantages are per-function scaling and HTTP concurrency control.
- **Premium**: warm instances are part of the design, so first-request latency is easier to suppress.
- **Dedicated**: there is no scale-to-zero cold start, but automatic reaction to a sudden spike depends on your App Service autoscale policy.

The common mistake is assuming Flex is always warm. It isn’t. A Flex app with Always Ready set to 0 can still scale to zero and cold start on the next request.

---

## What a Cold Start Actually Includes

Cold start is not just “the first request felt slow.” It is the total time needed for a fresh execution environment to become ready and serve the first invocation.

> **Cold start = the time to allocate a new instance, boot the host and worker, prepare the function, and run the first invocation**

That usually looks like this:

![Cold start stages before first invocation](../../../assets/azure-functions-101/06/06-03-what-a-cold-start-actually-includes.en.png)

*Cold start stages before first invocation*
| Step | Typical source of latency | Typical mitigation |
|---|---|---|
| 1 | A new execution environment must be prepared | Warm capacity, Always Ready, platform optimizations |
| 2 | Host initialization | Usually not much to tune directly |
| 3 | Language worker startup cost | Language choice, runtime startup review |
| 4 | Application dependencies, imports, initialization logic | Dependency trimming, lazy import, lazy init |
| 5 | The first invocation itself is heavy | Cache priming, warmup trigger, lighter first request |

In practice, step 4 often dominates more than people expect. If imports pull in large SDKs, open connections, or load models during startup, the application is manufacturing its own cold-start pain before plan choice even enters the conversation.

---

## What the platform already does before your code runs

Azure Functions is not leaving cold starts entirely to your application. The platform already uses a **placeholder model** to reduce some of the host-boot and environment-allocation cost before a real workload lands, and Premium adds **prewarmed / Always Ready instances** so capacity is already online before the next request arrives. Flex Consumption gives you a similar lever through the **alwaysReady instance count**: set it to 0 and the app can still scale to zero; set it higher and you are paying to keep warm capacity available.

That is the useful boundary to keep in mind. The platform can shorten the path to “an instance exists and the host is basically ready.” It cannot make your imports smaller, remove expensive startup code, or fix a first request that blocks on slow downstream dependencies. In other words, Azure can buy down infrastructure startup latency for you, but application initialization is still your problem.

---

## What to Change First When Cold Starts Hurt

### 1) Plan-level choices

- If first-request latency is a hard business requirement, start with **Premium** or **Flex Consumption plus Always Ready**.
- If occasional startup latency is acceptable, plain Consumption or baseline Flex is often good enough.

### 2) Code-level choices

- **Trim dependencies** — don’t pull in a large package just to use one feature.
- **Delay expensive initialization** — avoid opening DB connections, loading big files, or downloading metadata at import time.
- **Reuse process-local state carefully** — cache clients that are safe to reuse across invocations in module scope.

The next snippet is intentionally schematic. `create_cosmos_client()` stands in for your own client-construction code so the example can stay focused on lazy initialization.

```python
import azure.functions as func

app = func.FunctionApp()
_client = None

def get_client():
    global _client
    if _client is None:
        _client = create_cosmos_client()
    return _client

@app.function_name(name="hello")
@app.route(route="hello")
def hello(req: func.HttpRequest) -> func.HttpResponse:
    client = get_client()
    return func.HttpResponse("ok")
```

The point is simple: pay the heavy initialization cost once per worker, not once per invocation.

### 3) Operations-level choices

- **Warmup trigger** — available on every plan except classic Consumption. Flex, Premium, and Dedicated can use it when new instances are added.
- **Always Ready instances** — on Flex and Premium, this is the minimum warm baseline you keep online. At 0, scale-to-zero remains possible. At 1 or higher, first-request latency is easier to suppress.

Warmup trigger and Always Ready solve different problems. Warmup trigger is a hook that runs when an instance is being brought online. Always Ready is a capacity setting that keeps warm instances around in the first place.

---

## Concurrency Shapes Reliability and Cost

Automatic scale-out does not remove the need to think about concurrency.

### 1) Downstream systems do not scale with your function app

Database pools, external API rate limits, and Redis connection limits stay fixed unless you scale them too. A function app can scale out quickly and still bottleneck immediately on the systems behind it.

![Mismatch between function scale and downstream capacity](../../../assets/azure-functions-101/06/06-04-1-downstream-systems-do-not-scale-with-y.en.png)

*Mismatch between function scale and downstream capacity*
That is why operations work usually includes both of these:

- trigger-specific batch size, prefetch, and concurrency limits
- a queue in front of the downstream system so consumption rate matches downstream capacity

### 2) One instance can still execute many invocations concurrently

Depending on the runtime, trigger, and configuration, multiple invocations can overlap in the same instance and worker process. Module-level state therefore has to be safe for concurrent reuse.

This is one reason Flex’s HTTP concurrency setting matters. It affects not only how many instances you get, but how hard each instance is driven before the platform decides to add more.

---

## Scaling Is Also a Billing Model

Any scaling discussion that ignores cost is incomplete.

- **Consumption**: billing tracks execution time, memory, and invocation count. No traffic means little or no cost.
- **Flex Consumption**: similar serverless billing, plus the cost of Always Ready instances.
- **Premium**: you start paying for the warm baseline even before traffic rises.
- **Dedicated**: App Service Plan instances stay allocated, so the base cost is steady regardless of traffic.

Operations is not only about how fast the platform can add instances. It is also about how far you are willing to let it go. Maximum instance limits and concurrency settings are cost controls as much as performance controls.

---

## From behavior to observability

Scaling and cold starts only become manageable once you can observe them. The monitoring chapter moves from behavior to visibility: Application Insights, metrics, KQL, alerts, instance count, and the clues that explain why latency or cost moved.

If you want the implementation details behind those behaviors, pair this chapter with [Deep Dive — Scaling internals](../../azure-functions-deep-dive/en/05-scaling-internals.md) and [Deep Dive — Cold starts and Placeholder Mode](../../azure-functions-deep-dive/en/06-cold-start-placeholder.md). The 101 series is about operational judgment; the deep-dive series shows how those behaviors are implemented in the host.

---

## Operational checklist

- [ ] Cataloged scale-controller signals (queue length, HTTP queue) per workload
- [ ] Surfaced cold-start metrics (p50/p95) on a dashboard
- [ ] Decided the always-ready vs. cost tradeoff explicitly
- [ ] Sized DB connection pools alongside the function-instance ceiling
- [ ] Set max scale-out limits to throttle burst behavior

<!-- toc:begin -->
## In this series

- [What Is Azure Functions? — A World Where Events Call Your Code](./01-what-is-azure-functions.md)
- [Triggers and Bindings — Everything About Function I/O](./02-triggers-and-bindings.md)
- [Host and Worker — Who Actually Runs Your Functions?](./03-host-and-worker.md)
- [Deploy a Function App — From Localhost to Azure](./04-first-deploy.md)
- [Which Plan Should You Pick? — Consumption / Flex / Premium / Dedicated](./05-choosing-a-plan.md)
- **Scaling and Cold Starts — When Serverless Feels Fast and When It Doesn’t (current)**
- Monitoring and Operations Fundamentals (upcoming)

<!-- toc:end -->

---

## References

**Official Docs**
- [Azure Functions hosting options](https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale)
- [Event-driven scaling in Azure Functions](https://learn.microsoft.com/en-us/azure/azure-functions/event-driven-scaling)
- [Target-based scaling](https://learn.microsoft.com/en-us/azure/azure-functions/functions-target-based-scaling)
- [Warmup trigger for Azure Functions](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-warmup)
- [Manage connections in Azure Functions](https://learn.microsoft.com/en-us/azure/azure-functions/manage-connections)

**Related Series**
- [Azure Functions 101 — Choosing a plan](./05-choosing-a-plan.md)
- [Azure Functions 101 — Monitoring and operations fundamentals](./07-monitoring-and-ops.md)
- [Azure Functions Deep Dive — Scaling internals](../../azure-functions-deep-dive/en/05-scaling-internals.md)
- [Azure Functions Deep Dive — Cold starts and Placeholder Mode](../../azure-functions-deep-dive/en/06-cold-start-placeholder.md)

Tags: Azure, Azure Functions, Serverless, Cloud
