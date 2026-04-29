# Oracle Content Review — azure-functions-deep-dive

- **Session**: `ses_228fe0098ffe8AyXbzmwrgMMDn`
- **Date**: 2026-04-29
- **Verdict**: **not shippable** (rework)
- **Effort**: Large
- **Source pin**: `azure/azure-functions-host @ 5e59423` (vendored at `/root/Github/tech-blog/azure-functions-host/`)

## Critical: Hallucinated/invented host abstractions

Names cited that **do not exist in `5e59423`**:
- `WorkerConfigFactory` — actual: `WorkerConfigurationResolver` + provider classes
- `WorkerProcess.Start()` — actual: `StartProcessAsync()`
- `SendStartStreamMessage` — does not exist on `GrpcWorkerChannel`
- `maxConcurrentRequests` — invented setting
- `functions.json` scanning in specialization flow — does not exist
- `HostHealthMonitor` as concrete wired component — actual: `WebJobsScriptHostService` timer + `HostPerformanceManager`

## Scorecard

| Article | Score | Verdict |
|---|---:|---|
| ko/01-host-bootstrap.md | 3/5 | minor |
| en/01-host-bootstrap.md | 3/5 | minor |
| ko/02-worker-process.md | **2/5** | rework |
| en/02-worker-process.md | **2/5** | rework |
| ko/03-grpc-event-stream.md | **2/5** | rework |
| en/03-grpc-event-stream.md | **2/5** | rework |
| ko/04-dispatcher-and-invocation.md | **2/5** | rework |
| en/04-dispatcher-and-invocation.md | **2/5** | rework |
| ko/05-scaling-internals.md | 3/5 | minor |
| en/05-scaling-internals.md | 3/5 | minor |
| ko/06-cold-start-placeholder.md | **2/5** | rework |
| en/06-cold-start-placeholder.md | **2/5** | rework |

## Top issues by episode

### Ep1 — host bootstrap
- `ko|en/01:50-63` `HostHealthMonitor` doesn't exist; actual = `WebJobsScriptHostService` timer + `HostPerformanceManager`
- `ko|en/01:117` "Worker registers via `WorkerInitRequest`/`FunctionLoadRequest`" — `WorkerInitRequest` is host init/capabilities; functions delivered via `FunctionLoadRequest`/`FunctionLoadRequestCollection`
- `ko|en/01:119` Scale Controller claim not in vendored source; mark as architecture inference

### Ep2 — worker process
- `ko|en/02:61-66` `WorkerConfigFactory` invented; real path = `Workers/Rpc/Configuration/WorkerConfigurationResolver.cs`
- `ko|en/02:72-76` `RpcWorkerProcess.CreateWorkerProcess` description wrong; actual delegates to `_processFactory.CreateWorkerProcess(...)`
- `ko|en/02:76-82` `WorkerProcess.Start()` doesn't exist; use `StartProcessAsync()`
- `ko|en/02:22` wrong series count `(2/7)` — series is 6 parts

### Ep3 — gRPC event stream
- `ko|en/03:108-114` message-direction table sloppy; `WorkerTerminate` is host→worker only
- `ko|en/03:177` "host uses intersection of capabilities" — code uses `ApplyCapabilities()` merge, not intersection model
- `ko|en/03:208-210` FALSE: `Server/Startup.cs` maps `FunctionRpc.FunctionRpcBase`, not `MapGrpcService<FunctionRpcService>`
- `ko|en/03:226` `SendStartStreamMessage` does not exist on `GrpcWorkerChannel`/`WorkerChannel`

### Ep4 — dispatcher and invocation
- `ko|en/04:83-90` `ScriptInvocationContext` description wrong; actual fields = `FunctionMetadata`, `ExecutionContext`, `Inputs`, `BindingData`, `ResultSource`, trace
- `ko|en/04:148` FALSE: `SendInvocationRequest` does NOT wrap with `request_id = new GUID`. Source at `WorkerChannel.cs:925-928` sends `new StreamingMessage { InvocationRequest = invocationRequest }`; correlation key = `invocation_id`
- `ko|en/04:202` `maxConcurrentRequests` not a real setting in `5e59423`
- `ko|en/04:215-217` `WorkerConcurrencyManager` mischaracterized — works off `WorkerStatus.LatencyHistory`, not invocation-count thresholds

### Ep5 — scaling internals
- Honest about controller abstractions not in repo (good), but means it's not really a `5e59423` deep-dive
- Target-based scaling section is Learn-doc driven, not source-grounded
- Plan-by-plan comparison is hosting-doc summary

### Ep6 — cold start / placeholder
- **CRITICAL MISS**: explains specialization via `StandbyManager` only, misses real placeholder-channel reuse path: `WebHostRpcWorkerChannelManager.SpecializeAsync()` / `UsePlaceholderChannel()` / `SendFunctionEnvironmentReloadRequest()`
- `ko|en/06:291-292` hand-wavy on real branch conditions (version match, bitness, RO filesystem, runtime, placeholder-channel compatibility)
- `ko|en/06:302` FALSE: `functions.json` scanning not in specialization flow

## Cross-cutting concerns

- **Missing required deep-dive sections in all 12 files**: `## Source Version`, `## Call Path Summary` per STYLE_GUIDE.md
- **Broken series counters**: ep2-ep5 say `/7`, series is 6 parts
- Korean S1 leaks: `ko/06:203` (`요약하면`), `ko/02:113` (`게다가`)

## Verdict: not-shippable

## Action list

1. **P0** Replace invented names: `WorkerConfigFactory`, `WorkerProcess.Start`, `SendStartStreamMessage`, `maxConcurrentRequests`, `functions.json`, `HostHealthMonitor`. Map every claim to real type/member in `5e59423`.
2. **P0** Rewrite ep6 around real specialization: `StandbyManager` + `WebHostRpcWorkerChannelManager.SpecializeAsync()`/`UsePlaceholderChannel()`/`SendFunctionEnvironmentReloadRequest()`
3. **P0** Fix ep4 invocation path: `WorkerFunctionInvoker` → `ScriptInvocationContext` → `WorkerChannel.SendInvocationRequest`; remove fake `request_id`-GUID story
4. **P1** Rework ep2 around `WorkerConfigurationResolver` + provider classes; keep `RpcWorkerProcess` only for process creation/context handoff
5. **P1** Add `## Source Version` and `## Call Path Summary` to all 12 files; fix `(2/7)…(5/7)` counters to `/6`
6. **P1** Reframe ep5 as "host-side scale signals + plan semantics"
7. **P2** Korean prose pass (`요약하면`, `게다가`)
