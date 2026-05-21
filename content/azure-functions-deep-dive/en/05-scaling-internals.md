---
title: "Azure Functions Deep Dive (5/6): Scaling Internals — Scale Controller, ScaleMonitor, and What Differs Across Plans"
series: azure-functions-deep-dive
episode: 5
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- Azure Functions
- Serverless
- Distributed Systems
- gRPC
last_reviewed: '2026-04-29'
seo_description: All code citations in this post are based on Azure/azure-functions-host
  @ 5e59423.
---

# Azure Functions Deep Dive (5/6): Scaling Internals — Scale Controller, ScaleMonitor, and What Differs Across Plans

> Azure Functions Deep Dive series (5/6)

Everything in the previous parts happened inside one instance. The harder operational question begins when that instance is no longer enough: who decides to add more instances, what signals feed that decision, and which parts of the story still belong to the host itself?

This is the fifth post in the Azure Functions Deep Dive series. Here, we separate external scale-out decisions from in-instance worker concurrency and compare how that boundary changes across hosting plans.

## Source Version

All code citations in this post are based on [`Azure/azure-functions-host @ 5e59423`](https://github.com/Azure/azure-functions-host/tree/5e59423ba45491041d18224c3e72c168a4a5b7f7).

For four installments now we've stayed inside a **single** instance, watching how the host and its workers run functions. This time we step up one level.

> The instance itself — **who decides to add or remove it, based on what signal, and when?**

This is what people usually call "scaling out." And the decision **does not happen inside the host process.** The host only supplies the **inputs** to the decision; the actual call is made by a **Scale Controller** that lives outside the host — though the exact form of that controller depends on the plan.

So let's frame the boundary up front: **the Scale Controller implementation itself is not in this vendored `azure-functions-host` repo.** This post does not speculate about Azure-internal controller internals; it sticks to the host-side scale signals and their plan-dependent meaning.

This installment has three goals:

1. Pin down what Scale Controller, ScaleMonitor, and ITargetScaler each are, and where they live.
2. Separate two distinct mechanisms: deciding the **number of instances** (scale-out) vs. deciding the **number of workers inside an instance** (worker concurrency).
3. Compare how the same code behaves differently across the four plans: Consumption, Flex Consumption, Premium, and Dedicated.

> All code citations are pinned to [`Azure/azure-functions-host` @ `5e59423`](https://github.com/Azure/azure-functions-host/tree/5e59423ba45491041d18224c3e72c168a4a5b7f7).

![azure functions deep dive chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/azure-functions-deep-dive/05/05-01-the-big-picture-where-scaling-decisions.en.png)
*azure functions deep dive chapter 5 flow overview*

## Questions to Keep in Mind

- Do the Consumption, Premium, and Dedicated plan scalers share the same decision tree?
- What signal makes the Scale Controller decide to add another instance?
- Where does scale-out latency pile up most in burst traffic?

## Where scaling decisions are made

Before we touch any code, here's the whole thing in one diagram.

The key insight is that two different decisions are made in two different places.

| Decision | Decided by | Signal | Result |
|---|---|---|---|
| **Instance count** (scale-out) | Scale Controller (outside the host) | ScaleMonitor / TargetScaler metrics + host health ping | Move instances from N → N±k |
| **Workers per instance** | `WorkerConcurrencyManager` (inside the host) | Latency history from worker status responses | Add worker processes on the same instance |

If you blur these two together, you can't answer questions like "Why can't I just bump up the worker count on Premium myself?" Let's take them one at a time.

---

## What lives in the host repo — and what doesn't

First, a fact worth pinning down up front: **the definitions of `IScaleMonitor` and `ITargetScaler` do not live in the `azure-functions-host` repo.** Those interfaces live in [`Azure/azure-webjobs-sdk`](https://github.com/Azure/azure-webjobs-sdk) — the WebJobs SDK repo — and each trigger extension (Storage Queue, Service Bus, Event Hubs, etc.) takes a dependency on that SDK and implements its own metric collector.

The host repo's [`src/WebJobs.Script/Scale/`](https://github.com/Azure/azure-functions-host/tree/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script/Scale) directory has only two files:

- `ApplicationPerformanceCounters.cs`: the sandbox counter DTO
- `HostPerformanceManager.cs`: judges host load and handles the Scale Controller's health ping

And in [`src/WebJobs.Script.WebHost/Scale/`](https://github.com/Azure/azure-functions-host/tree/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.WebHost/Scale) there are two more:

- `TableStorageScaleMetricsRepository.cs`: persists the metrics ScaleMonitors report into Azure Table Storage
- `TableEntityConverter.cs`: a serialization helper for it

In other words, the host's job is just to **report its own load** and **store the metrics**. The decision belongs to the external Scale Controller. Once that picture is locked in, everything else falls into place.

---

## How the Scale Controller talks to the host — the health ping

When the Scale Controller looks at a single instance and asks "should this be scaled further?", the most direct signal it relies on is an **HTTP health ping**. The code on the host that answers that ping is `HostPerformanceManager.TryHandleHealthPingAsync`.

```csharp
// src/WebJobs.Script/Scale/HostPerformanceManager.cs
public async Task<IActionResult> TryHandleHealthPingAsync(HttpRequest request, ILogger logger)
{
    var healthPingEnabled = _environment.GetEnvironmentVariableOrDefault(
        EnvironmentSettingNames.HealthPingEnabled, "1");
    if (healthPingEnabled.Equals("0"))
    {
        return null;
    }

    bool checkHealth = false;
    var userAgent = request.GetHeaderValueOrDefault("User-Agent");
    if (!string.IsNullOrEmpty(userAgent) &&
        (userAgent.IndexOf(ScriptConstants.HttpScaleUserAgent, StringComparison.OrdinalIgnoreCase) != -1 ||
         userAgent.IndexOf(ScriptConstants.ScaleControllerUserAgent, StringComparison.OrdinalIgnoreCase) != -1))
    {
        // for these user agents, we default to true
        checkHealth = true;
    }
    // ...
    if (checkHealth)
    {
        int statusCode = (int)HttpStatusCode.OK;
        if (await IsUnderHighLoadAsync(logger: logger))
        {
            statusCode = 429;
        }
        return new StatusCodeResult(statusCode);
    }
    return null;
}
```

[`HostPerformanceManager.cs#L67-103`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script/Scale/HostPerformanceManager.cs#L67-L103)

In plain language:

1. The Scale Controller (or the HTTP scale component) sends a ping to the host's admin endpoint. **It identifies itself via the User-Agent header.**
2. The host inspects that User-Agent and decides "this is a health check."
3. It measures current load and returns **200 OK** if it's below the threshold, **429 Too Many Requests** if it's over.
4. The Scale Controller looks at the response, decides whether this instance can take more work, and makes its scaling call.

`IsUnderHighLoadAsync` looks at two kinds of load:

```csharp
public virtual async Task<bool> IsUnderHighLoadAsync(ILogger logger = null)
{
    return PerformanceCountersExceeded(logger: logger) || await ProcessThresholdsExceeded(logger: logger);
}
```

- `PerformanceCountersExceeded`: whether sandbox counters (`ActiveConnections`, `Threads`, `NamedPipes`, …) are over their limits.
- `ProcessThresholdsExceeded`: an aggregated throttle state covering host/worker CPU, ThreadPool, and gRPC channel health.

In the latter, you can see the host **directly pinging the OOP workers it owns**:

```csharp
// same file, inside ProcessThresholdsExceeded
var workerManager = _serviceProvider.GetScriptHostServiceOrNull<IScriptHostWorkerManager>();
if (workerManager != null)
{
    // TEMP: This call pings all the OOP workers, to ensure we include any channel latency
    // in the upstream ping result.
    await workerManager.GetWorkerStatusesAsync();
}

var throttleManager = _serviceProvider.GetScriptHostServiceOrNull<IConcurrencyThrottleManager>();
if (throttleManager != null)
{
    var status = throttleManager.GetStatus();
    return status.State == ThrottleState.Enabled;
}
```

Put another way: **a single HTTP call from the external Scale Controller is answered by the host with a verdict that aggregates its own state and that of every worker.** That's the mechanism by which an instance signals to the outside world that it has hit its ceiling.

---

## ScaleMonitor and TargetScaler — the signals triggers measure directly

If the health ping is the host's answer to "can you take more right now?", then **ScaleMonitor / TargetScaler** is the trigger's answer to "how much work is piling up?"

The code for these lives in the SDK, but the way they flow from the host's perspective is clear.

![Trigger metrics flowing into scale decisions](https://yeongseon-books.github.io/book-public-assets/assets/azure-functions-deep-dive/05/05-02-scalemonitor-and-targetscaler-the-signal.en.png)

*Trigger metrics flowing into scale decisions*
There are two modes, introduced at different points in time.

### Incremental scaling (`IScaleMonitor`)

The original model. Each ScaleMonitor looks at its own metrics and casts a `ScaleVote` (ScaleOut / ScaleIn / None). At most **one instance** is added or removed per round. Every trigger type supports it.

### Target-based scaling (`ITargetScaler`)

Introduced in 2022 and now the **default** for several triggers. It uses a simple formula:

> desired instances = event source length / target executions per instance

Microsoft's official docs put it this way:

> "target-based scaling allows scale up of **four instances at a time**, and the scaling decision is based on a simple target-based equation"
> — [Target-based scaling in Azure Functions](https://learn.microsoft.com/en-us/azure/azure-functions/functions-target-based-scaling)

The supported triggers are a fixed set:

| Trigger | Setting for target executions per instance | Default |
|---|---|---|
| Storage Queue | `extensions.queues.batchSize` | 16 |
| Service Bus (single dispatch, v5+) | `extensions.serviceBus.maxConcurrentCalls` | 16 |
| Service Bus (batch, v5+) | `extensions.serviceBus.maxMessageBatchSize` | 1000 |
| Event Hubs (v5.x) | `extensions.eventHubs.maxEventBatchSize` | 10 |
| Event Hubs (v6+) | `extensions.eventHubs.maxEventBatchSize` | 100 |
| Cosmos DB | `MaxItemsPerInvocation` (function attribute) | 100 |
| Apache Kafka | `LagThreshold` (function attribute) | 1000 |

For Event Hubs specifically, do not read `100` as a generic default for every `v5+` extension build. Microsoft documents that `maxEventBatchSize` changed from `10` to `100` in `Microsoft.Azure.WebJobs.Extensions.EventHubs` v6.0.0.

Target-based scaling is enabled by default on **Functions runtime 4.19.0 and above**, and you can disable it with `TARGET_BASED_SCALING_ENABLED=0` to fall back to incremental.

> Source: [Target-based scaling in Azure Functions](https://learn.microsoft.com/en-us/azure/azure-functions/functions-target-based-scaling)

### What does the host do?

In either of these models, the host plays only the role of a **metric repository**. That role is filled by `TableStorageScaleMetricsRepository` ([`src/WebJobs.Script.WebHost/Scale/TableStorageScaleMetricsRepository.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.WebHost/Scale/TableStorageScaleMetricsRepository.cs)). It stores the values the ScaleMonitor measures, and the Scale Controller reads them back to decide.

So the host **does not participate** in the decision. It just lets the metrics flow through.

---

## Concurrency inside an instance — `WorkerConcurrencyManager`

Everything above was the story of how "instance count" is decided. Now we look at the other decision — **how many worker processes to run inside the same instance**.

For OOP workers (Python, Node, Java), a worker is typically a single process, which means **you can run more than one worker process within the same instance**. The component that decides this is [`WorkerConcurrencyManager`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/WorkerConcurrencyManager.cs).

This path is narrower than it first appears. `StartAsync` only enables dynamic worker concurrency for **Node, PowerShell, and Python**. It explicitly skips the `HttpFunctionInvocationDispatcher` path, and it does not start at all when `FUNCTIONS_WORKER_PROCESS_COUNT` is set. That environment variable is a **static worker-count setting** per instance.

`WorkerConcurrencyOptions` is something else: it defines the thresholds for the **dynamic add-a-worker loop**. The two knobs solve different problems. `FUNCTIONS_WORKER_PROCESS_COUNT` says "start with this many worker processes." `WorkerConcurrencyOptions` says "given recent latency, should I add one more?"

`IsOverloaded` does not look at queue depth. It looks at `LatencyHistory`. Once the history has at least `HistorySize` samples, it counts how many are at or above `LatencyThreshold`, divides that by `HistorySize`, and compares the result to `NewWorkerThreshold`. Then `NewWorkerIsRequired` adds a worker only when at least one worker is overloaded and the current worker count is still below `MaxWorkerCount`.

There is no symmetric scale-in path here. This code is about **adding** workers when recent latency stays high. That makes it an in-instance parallelism mechanism, not a miniature version of external scale-out.

Putting these two side by side:

| Aspect | Instance scale-out | Worker concurrency |
|---|---|---|
| Decided by | Scale Controller (external) | `WorkerConcurrencyManager` (inside the host) |
| Unit | VM instance | Worker process within an instance |
| Signal | ScaleMonitor metrics + health ping | Proportion of overloaded samples in `LatencyHistory` |
| Impact | Bill, cold-start time | Throughput within the instance |
| Scope | Varies by plan | Node / PowerShell / Python only; excludes HTTP worker; disabled when static process count is set |

---

## Plan-by-plan — same code, different behavior

The host code is identical wherever it runs. The `HostPerformanceManager.cs` we just looked at, the `TableStorageScaleMetricsRepository.cs`, the `WorkerConcurrencyManager.cs` — all one codebase. What differs is **who is making decisions outside this code**.

![Plan-specific scaling decision differences](https://yeongseon-books.github.io/book-public-assets/assets/azure-functions-deep-dive/05/05-03-plan-by-plan-same-code-different-behavio.en.png)

*Plan-specific scaling decision differences*
Plan by plan, in a sentence each:

### Consumption

- The classic Scale Controller makes the call.
- Scales to zero, max 200 instances.
- Supports target-based scaling (4.19.0+).
- No VNet integration.

### Flex Consumption — the newest model

Flex Consumption is the successor to Consumption and, in practice, a different platform. The host code is the same, but the decision model layered on top is different.

- **Per-function scaling**: instances scale per function or per function group. The groups are fixed:

| Scale group | Triggers included |
|---|---|
| `http` | HTTP trigger, SignalR trigger |
| `blob` | Blob storage trigger (Event Grid–based) |
| `durable` | Orchestration / Activity / Entity trigger |
| `function:<NAMED_FUNCTION>` | Every other function (individually) |

> Source: [Flex Consumption per-function scaling](https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan#per-function-scaling)

- **Always ready instances**: you can set a non-zero floor, configurable per group or per function. This is the main lever for cutting cold starts.
- **Default per-app maximum of 100 instances**, configurable up to 1000.
- **Regional subscription quota remains separate**: the default regional quota is 250 cores, so you can hit that limit before the app-level ceiling.
- **Selectable instance memory**: 512 / 2048 / 4096 MB. A larger instance can absorb more concurrency within the same function group.
- VNet integration and Azure Files mounts are supported.

> Source: [Azure Functions Flex Consumption plan hosting](https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan)

### Premium (Elastic Premium)

- Pre-warmed instances behave like an early version of Always Ready.
- For VNet-bound triggers you can enable **runtime scale monitoring**, which moves the ScaleMonitor logic inside the host and sidesteps the problem of the external Scale Controller being walled off from the VNet.
- Supports target-based scaling (4.19.0+; with runtime scale monitoring, certain extension package minimums apply).

### Dedicated (App Service Plan)

- The Functions event-driven scaler **does not run.** You use the standard App Service Auto-Scale rules (CPU/memory-based) or scale manually.
- The host code is the same, but since nothing outside is sizing the instance count for you, the metrics ScaleMonitor reports lose their meaning.

> Source: [Target-based scaling considerations](https://learn.microsoft.com/en-us/azure/azure-functions/functions-target-based-scaling#considerations) — "Event-driven scaling isn't supported when running on Dedicated (App Service) plans."

---

## All in one table

| Plan | Scale decided by | Scale to zero | Max instances | Per-function | Always ready | VNet |
|---|---|---|---|---|---|---|
| Consumption | Scale Controller | Yes | 200 | No | No | No |
| Flex Consumption | Scale Controller (new) | Yes | 100 default; configurable to 1000 | Yes | Yes | Yes |
| Premium | Scale Controller (+ option) | No (min 1) | Varies by SKU/region | No | pre-warmed | Yes |
| Dedicated | App Service Auto-Scale | No | Depends on plan | No | Always On available | Yes |

Different decision layers sit on top of the same host binary; the way the host itself works doesn't change.

---

## Wrap-up — the model to keep

- Scale decisions happen **outside the host**. The host reports metrics and answers health pings.
- `IScaleMonitor` (incremental) and `ITargetScaler` (formula-based) are SDK / extension-side interfaces; the host just persists their metrics in Table Storage.
- Deciding the **number of instances** and deciding the **number of workers inside an instance** are different mechanisms. The latter is handled in-process by `WorkerConcurrencyManager`, and in this code path it only **adds** workers.
- `FUNCTIONS_WORKER_PROCESS_COUNT` is a static worker-count setting. `WorkerConcurrencyOptions` controls the thresholds for dynamic worker addition. They are not interchangeable.
- The same host code behaves differently across Consumption / Flex / Premium / Dedicated because the external decision layer is different. The host itself is unchanged.
- Flex Consumption introduces per-function scaling and Always Ready, deciding "how many instances for which function" at the group level.

The model in this post stops at the boundary where an external component has already decided instance count and the host has answered with metrics, health pings, or worker-latency signals. That boundary matters because it keeps host-side evidence separate from Azure-managed scale-controller behavior.

---

## Call Path Summary

- external scale component → `HostPerformanceManager.TryHandleHealthPingAsync(...)` → `IsUnderHighLoadAsync()` → host/worker-aware 200 or 429
- trigger-side `IScaleMonitor` / `ITargetScaler` metrics → `TableStorageScaleMetricsRepository` → external Scale Controller reads persisted metrics
- `WorkerConcurrencyManager` timer loop → `WorkerStatus.LatencyHistory` evaluation → add worker inside the current instance when needed

---

## Operational checklist

- [ ] Tabulated cost vs latency trade-offs for plan selection
- [ ] Have load-test runs and recorded results for burst scenarios
- [ ] Validated concurrency settings against downstream quotas
- [ ] Verified graceful-shutdown behaviour on scale-in
- [ ] Decided Premium-plan minimum instances and cold-start protection strategy

## Answering the Opening Questions

- **Do the Consumption, Premium, and Dedicated plan scalers share the same decision tree?**
  - The article treats Scaling Internals — Scale Controller, ScaleMonitor, and What Differs Across Plans as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **What signal makes the Scale Controller decide to add another instance?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **Where does scale-out latency pile up most in burst traffic?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [Azure Functions Deep Dive (1/6): Host Bootstrap — Following `WebJobsScriptHostService`](./01-host-bootstrap.md)
- [Azure Functions Deep Dive (2/6): Worker Processes — How One Host Hosts Many Languages](./02-worker-process.md)
- [Azure Functions Deep Dive (3/6): The gRPC Event Stream — What Do the Host and Worker Actually Exchange?](./03-grpc-event-stream.md)
- [Azure Functions Deep Dive (4/6): Dispatcher and Invocation — How a Function Call Reaches the Worker](./04-dispatcher-and-invocation.md)
- **Azure Functions Deep Dive (5/6): Scaling Internals — Scale Controller, ScaleMonitor, and What Differs Across Plans (current)**
- Azure Functions Deep Dive (6/6): Cold Start and Placeholder Mode — What Happens When a New Instance Is Born (upcoming)

<!-- toc:end -->

---

## References

### Primary sources (host code, commit `5e59423`)

- [`src/WebJobs.Script/Scale/HostPerformanceManager.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script/Scale/HostPerformanceManager.cs) — Scale Controller health ping handling, throttle aggregation
- [`src/WebJobs.Script/Scale/ApplicationPerformanceCounters.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script/Scale/ApplicationPerformanceCounters.cs) — sandbox counter DTO
- [`src/WebJobs.Script.WebHost/Scale/TableStorageScaleMetricsRepository.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.WebHost/Scale/TableStorageScaleMetricsRepository.cs) — persists ScaleMonitor metrics
- [`src/WebJobs.Script.Grpc/WorkerConcurrencyManager.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/WorkerConcurrencyManager.cs) — worker concurrency inside an instance

### Secondary sources (Microsoft Learn official docs)

- [Azure Functions Flex Consumption plan hosting](https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan)
- [Target-based scaling in Azure Functions](https://learn.microsoft.com/en-us/azure/azure-functions/functions-target-based-scaling)
- [Event-driven scaling in Azure Functions](https://learn.microsoft.com/en-us/azure/azure-functions/event-driven-scaling)
- [Azure Functions hosting options](https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale)

### Related series

This is part 5 of the Deep Dive series. Part 4 followed a single invocation into the worker; this one separated the outside scale controller from the inside worker-concurrency logic that can add more worker processes on the same instance. The intro series' parts 5 and 6 cover the same territory from an operator-facing angle.

Tags: Azure Functions, Serverless, Distributed Systems, gRPC
