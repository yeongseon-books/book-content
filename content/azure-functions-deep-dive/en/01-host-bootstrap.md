---
title: "Azure Functions Deep Dive (1/6): Host Bootstrap — Following `WebJobsScriptHostService`"
series: azure-functions-deep-dive
episode: 1
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

# Azure Functions Deep Dive (1/6): Host Bootstrap — Following `WebJobsScriptHostService`

This is the first post in the Azure Functions Deep Dive series.

## Source Version

All code citations in this post are based on [`Azure/azure-functions-host @ 5e59423`](https://github.com/Azure/azure-functions-host/tree/5e59423ba45491041d18224c3e72c168a4a5b7f7).

In episode 3 of the intro series, I wrote that Functions runs the Host process (.NET) and the Worker process (your language) separately, with gRPC between them. This series checks that sentence against the actual host code. It reads the [`Azure/azure-functions-host`](https://github.com/Azure/azure-functions-host) repo directly, one stage per post, from bootstrap through invocation, scaling, and cold starts.

This post focuses on one question: **what happens the moment a Function App instance powers on**. Everything is pinned to commit `5e59423`, and every host code citation uses that commit.

![azure functions deep dive chapter 1 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/azure-functions-deep-dive/01/01-01-the-big-picture-one-azure-functions-host.en.png)
*azure functions deep dive chapter 1 flow overview*

## Questions to Keep in Mind

- What process is the Functions Host exactly, and in what order does it bootstrap?
- Is host.json just a config file, or a runtime configuration that changes host behaviour?
- Where do host startup failures get logged, and where do you start looking?

## One Azure Functions host instance

This is the map for the rest of the series.
Each later part zooms into one box from this picture.
Get the layout in your head first; the code paths land more cleanly after that.

This post stays on host bootstrap only. The rest of the boxes are pinned in the series TOC below; here the job is to make the bootstrap boundary itself explicit.

---

## Host bootstrap in 4 stages

It looks complicated, but host bootstrap really compresses down to these four stages:

![Four-stage host bootstrap flow](https://yeongseon-books.github.io/book-public-assets/assets/azure-functions-deep-dive/01/01-02-the-big-picture-host-bootstrap-in-4-stag.en.png)

*Four-stage host bootstrap flow*
This post walks through each of these four boxes in order. After stage 4, **the function is ready to run the moment a trigger fires**.

---

## Stage 1: Enter `WebJobsScriptHostService`

The entry point is `Program.cs`, but the real protagonist of the Functions "host lifecycle" is an `IHostedService` named `WebJobsScriptHostService`. It sits on top of ASP.NET Core's standard hosting model, so its lifecycle is managed by `StartAsync` / `StopAsync` just like any other hosted service.

The key method is `StartAsync`. Inside it, the following happens:

- Set up the `WebJobsScriptHostService` timer-driven host health loop
- Feed that loop into `HostPerformanceManager` so the host can evaluate current load and health
- Create a `ScriptHost` instance and call `InitializeAsync`
- Apply retry / restart policy on failure
- Publish bootstrap state events (Standby → Running transitions, etc.)

> Code location: [`WebJobsScriptHostService.cs` (commit `5e59423`)](https://github.com/Azure/azure-functions-host/blob/5e59423/src/WebJobs.Script.WebHost/WebJobsScriptHostService.cs)

One important design decision here. **`WebJobsScriptHostService` is not "the host itself."** It's a shell that "manages" the host lifecycle. The actual host is the `ScriptHost` inside. By separating the shell from the kernel, recovery becomes possible: when the host dies, the shell can spin up a new kernel and swap it in.

---

## Stage 2: `ScriptHost.InitializeAsync` — where bootstrap actually happens

Inside `ScriptHost.InitializeAsync`, called by `WebJobsScriptHostService`, the host does the work required to become a running function app.

![Host setup inside initialization stage](https://yeongseon-books.github.io/book-public-assets/assets/azure-functions-deep-dive/01/01-03-stage-2-scripthost-initializeasync-where.en.png)

*Host setup inside initialization stage*
The ordering matters. In `ScriptHost.StartAsyncCore()`, `InitializeAsync()` runs first and finishes before `base.StartAsyncCore()` runs. Trigger listener activation through `JobHost.StartAsync()` is therefore **after** initialization, not part of it. This post stays on config loading and function indexing so the bootstrap boundary itself is clear.

> Code location: [`ScriptHost.cs` (commit `5e59423`)](https://github.com/Azure/azure-functions-host/blob/5e59423/src/WebJobs.Script/Host/ScriptHost.cs)

---

## Stage 3: where and how `host.json` is read

`host.json` is the "single source of truth" for Functions. Concurrency, timeouts, logging, per-trigger options — they all live here. Let's follow how this file gets converted into an options tree in code.

The entry point is `HostJsonFileConfigurationSource`. This class reads host.json and pushes it into .NET's `IConfiguration` tree. A constants list called `WellKnownHostJsonProperties` defines the keys this file is "expected to know about." Some representative ones:

- `concurrency` — concurrent invocation limits
- `extensions.queues` — queue trigger options (batch size, polling interval, etc.)
- `extensions.http` — HTTP trigger routing / concurrency
- `functionTimeout` — timeout for a single invocation

> Code location: [`HostJsonFileConfigurationSource.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423/src/WebJobs.Script/Config/HostJsonFileConfigurationSource.cs)

Values from `host.json` map straight to options objects. For example, `functionTimeout` flows into `ScriptJobHostOptions.FunctionTimeout` via `ScriptJobHostOptionsSetup.ConfigureFunctionTimeout`.

> Code location: [`ScriptJobHostOptionsSetup.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423/src/WebJobs.Script/Config/ScriptJobHostOptionsSetup.cs)

![host.json mapping path to runtime options](https://yeongseon-books.github.io/book-public-assets/assets/azure-functions-deep-dive/01/01-04-stage-3-where-and-how-host-json-is-read.en.png)

*host.json mapping path to runtime options*
This diagram is the path `host.json` takes into runtime options. **One key in the file → one node in IConfiguration → a Setup class → one field on an options object**. The mapping stays that direct.

Two things operators should know:

1. **Environment variables land in the same IConfiguration tree.** That means env vars can override values written in `host.json`. Example: the `AzureFunctionsJobHost__functionTimeout` env var beats `functionTimeout` in host.json.
2. **`FUNCTIONS_WORKER_PROCESS_COUNT`** — sets how many Worker processes to spin up inside a single instance. This option was introduced in [PR #4210](https://github.com/Azure/azure-functions-host/pull/4210), and it's the knob that directly controls the "in-instance concurrency" axis I covered in episode 6 of the intro series.

---

## Stage 4: function metadata indexing

After reading host.json, `ScriptHost` indexes "what functions does this app have." The result is a list of `FunctionMetadata`. Each entry contains:

- Function name
- Trigger type and trigger configuration
- Input/output binding list
- Code entry point (the handler the Worker will invoke)
- Language used

Why does this indexing matter? Because **this metadata is the foundation for every downstream behavior**.

- The Worker first receives host init/capability data through `WorkerInitRequest`, then receives actual function metadata through `FunctionLoadRequest` or `FunctionLoadRequestCollection`
- Trigger listeners look at this list to decide "which queue to poll, which route to bind to"
- The Scale Controller is architecturally downstream of this metadata, but that controller itself is out of tree for this vendored source. Episode 5 stays on the host-side scale signals.

In other words, **indexing is the stage that builds the Functions host's "function catalog."**

---

## The host health monitor

`WebJobsScriptHostService` creates `_hostHealthCheckTimer` in its constructor and periodically runs `OnHostHealthCheckTimer`. That loop works with `HostPerformanceManager` to decide whether the current instance is overloaded or unhealthy. In other words, there is no separate wired health-monitor component in this source tree; the health-monitoring behavior is the combination of **the timer inside `WebJobsScriptHostService` plus `HostPerformanceManager`**.

- Host throws during bootstrap → retry
- Bootstrap takes too long → forced restart
- Memory/CPU thresholds exceeded → instance reclaim signal

![Host health checks and restart decisions](https://yeongseon-books.github.io/book-public-assets/assets/azure-functions-deep-dive/01/01-05-the-host-health-monitor.en.png)

*Host health checks and restart decisions*
This state machine is the root cause of the operational symptom "my function suddenly restarted." If you see frequent "Host started" log entries in App Insights, this state machine is probably cycling more often than you'd like.

---

## Episode 1 wrap

The flow this post traced, compressed into one paragraph:

> ASP.NET Core boots and starts an `IHostedService` named `WebJobsScriptHostService`. Inside it, a `ScriptHost` is created and `InitializeAsync` runs first, reading host.json and environment-backed options and indexing function metadata. Only after that does `JobHost.StartAsync` run and activate trigger listeners. The host health monitor watches the whole sequence and replaces the host when it fails.

The key boundary to keep from this post is simple: host bootstrap is the work required to get `ScriptHost` configured, indexed, and ready for listener startup. That gives us a clean line between host bring-up and everything that happens after the host begins talking to language workers.

---

## Where this fits in the series

This is part 1 of the Azure Functions Deep Dive series. It isolates the host-bootstrap boundary before the series moves into worker lifecycle, transport, invocation, scale signals, and specialization.

---

## Call Path Summary

- `Program.Main()` → ASP.NET Core host bootstrap → `WebJobsScriptHostService.StartAsync()` → `ScriptHost.InitializeAsync()` → `JobHost.StartAsync()`
- `HostJsonFileConfigurationSource` → `IConfiguration` → `ScriptJobHostOptionsSetup` → `ScriptJobHostOptions`
- `WebJobsScriptHostService` health timer → `OnHostHealthCheckTimer(...)` → `HostPerformanceManager`

---

### Inspect host bootstrap logs and host.json

```bash
az functionapp config appsettings list -n my-func -g my-rg \
  --query "[?starts_with(name, 'FUNCTIONS_') || starts_with(name, 'WEBSITE_')]" -o table

az functionapp log tail -n my-func -g my-rg
```

## Operational checklist

- [ ] Explicitly pinned FUNCTIONS_EXTENSION_VERSION and the worker runtime version
- [ ] Defined a regression-test flow for host.json changes
- [ ] Added host-startup-failure alerts and the first diagnostic step to the runbook
- [ ] Reviewed how the host/worker split affects your code
- [ ] Decided runtime-upgrade policy (automatic vs manual)

## Answering the Opening Questions

- **What process is the Functions Host exactly, and in what order does it bootstrap?**
  - The Functions Host is an ASP.NET Core process where `WebJobsScriptHostService` manages the lifecycle, and the inner `ScriptHost` handles the actual function app preparation. The order is: enter `WebJobsScriptHostService.StartAsync`, create `ScriptHost`, run `InitializeAsync` (loading settings and indexing metadata), then enter `base.StartAsyncCore()` to start listeners.
- **Is host.json just a config file, or a runtime configuration that changes host behaviour?**
  - `host.json` is not a documentation file — it enters the `IConfiguration` tree via `HostJsonFileConfigurationSource` and is a real runtime input. Settings like `functionTimeout`, concurrency, and extension configuration map directly to options objects, and any app settings in the same tree can override final behaviour.
- **Where do host startup failures get logged, and where do you start looking?**
  - The first diagnostic point is how far `WebJobsScriptHostService` progressed in bootstrap and whether `ScriptHost.InitializeAsync` completed. Immediate post-start exceptions, function metadata indexing failures, and pre-listener-start failures occur at different stages, so check logs around `WebJobsScriptHostService`, `FunctionMetadataManager`, and `StartAsyncCore` in order.

<!-- toc:begin -->
## In this series

- **Azure Functions Deep Dive (1/6): Host Bootstrap — Following `WebJobsScriptHostService` (current)**
- Azure Functions Deep Dive (2/6): Worker Processes — How One Host Hosts Many Languages (upcoming)
- Azure Functions Deep Dive (3/6): The gRPC Event Stream — What Do the Host and Worker Actually Exchange? (upcoming)
- Azure Functions Deep Dive (4/6): Dispatcher and Invocation — How a Function Call Reaches the Worker (upcoming)
- Azure Functions Deep Dive (5/6): Scaling Internals — Scale Controller, ScaleMonitor, and What Differs Across Plans (upcoming)
- Azure Functions Deep Dive (6/6): Cold Start and Placeholder Mode — What Happens When a New Instance Is Born (upcoming)

<!-- toc:end -->

---

## References

### Primary sources (host code, commit `5e59423`)
- [`WebJobsScriptHostService.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423/src/WebJobs.Script.WebHost/WebJobsScriptHostService.cs)
- [`ScriptHost.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423/src/WebJobs.Script/Host/ScriptHost.cs)
- [`HostJsonFileConfigurationSource.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423/src/WebJobs.Script/Config/HostJsonFileConfigurationSource.cs)
- [`ScriptJobHostOptionsSetup.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423/src/WebJobs.Script/Config/ScriptJobHostOptionsSetup.cs)
- [PR #4210 — introducing `FUNCTIONS_WORKER_PROCESS_COUNT`](https://github.com/Azure/azure-functions-host/pull/4210)

### Secondary sources
- [host.json reference](https://learn.microsoft.com/en-us/azure/azure-functions/functions-host-json)
- [Azure Functions app settings reference](https://learn.microsoft.com/en-us/azure/azure-functions/functions-app-settings)

### Other parts in the series
- [Azure Functions 101 — intro series](../../azure-functions-101/en/) (especially episode 3, "Host and Worker")

Tags: Azure Functions, Serverless, Distributed Systems, gRPC
