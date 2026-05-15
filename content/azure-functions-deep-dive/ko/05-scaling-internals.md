---
title: 스케일링 내부 동작 — Scale Controller, ScaleMonitor, 그리고 플랜별 차이
series: azure-functions-deep-dive
episode: 5
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- Azure Functions
- Serverless
- Distributed Systems
- gRPC
last_reviewed: '2026-05-12'
seo_description: 이 글의 모든 코드 인용은 Azure/azure-functions-host @ 5e59423 기준입니다.
---

# 스케일링 내부 동작 — Scale Controller, ScaleMonitor, 그리고 플랜별 차이

앞선 네 편에서는 인스턴스 하나 안에서 벌어지는 일을 따라왔습니다. 호스트가 부팅되고, 언어 워커가 떠서, gRPC 스트림이 연결되고, invocation이 워커까지 왕복하는 경로를 확인했습니다. 하지만 실제 운영에서 더 어려운 질문은 그 다음 단계에서 나옵니다. **인스턴스 하나로 부족해졌을 때 누가 더 늘릴지를 결정하는가**입니다.

이 질문은 단순히 “자동 스케일이 된다”는 제품 설명으로는 답이 되지 않습니다. 호스트가 직접 인스턴스 수를 늘리는지, 외부 컴포넌트가 결정하는지, 같은 스케일링이라는 단어 아래에서 인스턴스 수와 인스턴스 내부 워커 수가 어떻게 구분되는지를 알아야 비용과 지연 시간을 함께 설계할 수 있습니다.

이번 글은 [`Azure/azure-functions-host @ 5e59423`](https://github.com/Azure/azure-functions-host/tree/5e59423ba45491041d18224c3e72c168a4a5b7f7) 기준으로 호스트가 바깥으로 내보내는 scale signal만 다룹니다. 의도적으로 Azure 내부 Scale Controller의 비공개 구현을 추측하지 않고, host repo 안에 있는 것과 없는 것을 명확히 나눕니다.

이 글은 Azure Functions Deep Dive 시리즈의 다섯 번째 글입니다.

이제 외부 scale-out 결정과 인스턴스 내부 worker concurrency를 분리해서 보는 운영 모델을 고정하겠습니다.

## 이 글에서 다룰 문제

- Consumption, Premium, Dedicated 플랜은 같은 스케일 의사결정 트리를 공유할까요?
- Scale Controller가 인스턴스를 더 늘리기로 결정하게 만드는 신호는 무엇일까요?
- burst 트래픽에서 scale-out 지연은 어디에 가장 많이 쌓일까요?
- 동시성 제어와 스케일링은 어떻게 협력하고, 어디서 충돌할까요?
- scale-in 시점에 진행 중인 invocation은 어떻게 보호될까요?

## 왜 이 글이 중요한가

Functions를 운영하면서 가장 자주 만나는 오해 중 하나는 “호스트가 바쁘면 스스로 인스턴스를 더 띄운다”는 상상입니다. 실제로 호스트는 인스턴스 수를 직접 늘리지 않습니다. 호스트는 자신의 상태와 trigger 쪽 메트릭을 외부에 노출할 뿐이고, 실제 인스턴스 수 증감은 **호스트 바깥의 Scale Controller 또는 플랜별 외부 결정 계층**이 맡습니다. 이 선을 모르면 scale-out 문제를 host bug처럼 디버깅하게 됩니다.

또한 인스턴스 수 증가와 인스턴스 내부 워커 수 증가는 전혀 다른 문제입니다. 인스턴스를 더 만드는 것은 비용, 콜드 스타트, 네트워크 격리와 연결되고, 인스턴스 안에서 워커를 더 띄우는 것은 같은 VM 자원 안에서 처리량을 어떻게 끌어올릴지와 연결됩니다. 같은 “동시성”이나 “확장”이라는 단어를 써도 실제 조정 단위가 다릅니다.

마지막으로 플랜 차이는 제품 브로셔가 아니라 운영 감각의 차이입니다. Consumption, Flex Consumption, Premium, Dedicated는 같은 호스트 바이너리를 써도 바깥 결정 계층이 다르기 때문에 사용자가 체감하는 scale-out, cold start, 비용 구조가 달라집니다. 플랜별 차이를 host code 위에 올려서 이해해야 적절한 설계를 할 수 있습니다.

## 스케일링을 이해하는 가장 좋은 방법: 호스트가 인스턴스 수를 직접 결정하지 않고 health ping과 trigger 메트릭만 내보내며, 인스턴스 내부 worker concurrency는 별도 루프가 관리한다고 보는 것입니다

스케일링 경계를 선명하게 보려면 먼저 결정 단위를 둘로 나눠야 합니다. 첫째는 **인스턴스 수**입니다. 이 결정은 호스트 바깥의 Scale Controller가 내립니다. 둘째는 **인스턴스 내부 워커 수**입니다. 이 결정은 호스트 내부 `WorkerConcurrencyManager`가 내립니다. 두 메커니즘은 신호도, 비용도, 장애 모드도 다릅니다.

호스트는 외부 Scale Controller에 두 종류의 입력을 제공합니다. 하나는 `HostPerformanceManager`가 응답하는 health ping이고, 다른 하나는 trigger extension 쪽 `IScaleMonitor` / `ITargetScaler`가 수집한 메트릭을 저장해 두는 역할입니다. 그 이상은 하지 않습니다. 이 관점을 잡아야 scale signal과 scale decision을 헷갈리지 않게 됩니다.

> 이번 글의 핵심은 “Functions가 자동 스케일한다”는 설명을 “호스트는 신호를 내보내고, 외부 계층이 인스턴스 수를 결정하며, 호스트 내부는 별도로 워커 수만 조절한다”는 구조로 바꾸는 것입니다.

## 핵심 개념

### 큰 그림부터 보면 두 개의 다른 결정이 보입니다

먼저 전체 구조를 한 장으로 보겠습니다.

![외부 스케일아웃과 내부 워커 확장 경계](../../../assets/azure-functions-deep-dive/05/05-01-the-big-picture-where-scaling-decisions.ko.png)

핵심은 두 개의 다른 결정이 서로 다른 곳에서 일어난다는 점입니다.

| Decision | Decided by | Signal | Result |
|---|---|---|---|
| **Instance count** (scale-out) | Scale Controller (outside the host) | ScaleMonitor / TargetScaler metrics + host health ping | Move instances from N → N±k |
| **Workers per instance** | `WorkerConcurrencyManager` (inside the host) | Latency history from worker status responses | Add worker processes on the same instance |

이 둘을 섞어 버리면 “왜 Premium에서 worker count만 올리면 안 되지?” 같은 질문에 답하기 어려워집니다. 인스턴스 수는 플랫폼 단위이고, 워커 수는 host runtime 단위이기 때문입니다.

### host repo 안에 있는 것과 없는 것을 먼저 구분해야 합니다

중요한 사실 하나를 먼저 고정하겠습니다. `IScaleMonitor`와 `ITargetScaler` 정의는 `azure-functions-host` 저장소에 없습니다. 이 인터페이스들은 [`Azure/azure-webjobs-sdk`](https://github.com/Azure/azure-webjobs-sdk) 쪽에 있고, Storage Queue, Service Bus, Event Hubs 같은 trigger extension이 그 SDK를 기준으로 자기 메트릭 수집기를 구현합니다.

반면 host repo의 `src/WebJobs.Script/Scale/`에는 `ApplicationPerformanceCounters.cs`와 `HostPerformanceManager.cs`만 있습니다. 또 `src/WebJobs.Script.WebHost/Scale/`에는 `TableStorageScaleMetricsRepository.cs`와 `TableEntityConverter.cs`가 있습니다. 즉 호스트가 하는 일은 **자기 부하를 보고하고 메트릭을 저장하는 것**이지, 외부 Scale Controller 역할을 대체하는 것이 아닙니다.

이 선이 잡히면 비공개 Azure 내부 알고리즘을 추측할 필요가 줄어듭니다. 운영에 필요한 것은 외부 결정기 내부를 상상하는 능력이 아니라, **호스트가 어떤 증거를 바깥에 내놓는지**를 정확히 아는 능력입니다.

### 외부 Scale Controller는 health ping으로 호스트의 현재 수용 가능 상태를 봅니다

Scale Controller가 “이 인스턴스가 더 받아도 되는가”를 물을 때 가장 직접적으로 보는 신호는 HTTP health ping입니다. 호스트 쪽 응답 코드는 `HostPerformanceManager.TryHandleHealthPingAsync`입니다.

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

여기서 호스트는 `User-Agent`를 보고 이 요청이 scale health check인지 판단하고, 현재 부하가 임계치를 넘지 않으면 `200 OK`, 넘으면 `429 Too Many Requests`를 돌려줍니다. 즉 외부 Scale Controller 입장에서는 호스트가 “지금 더 받아도 된다 / 이미 한계다”라는 현재 상태 신호를 내보내는 셈입니다.

### `IsUnderHighLoadAsync`는 호스트와 워커 상태를 함께 봅니다

health ping의 실제 판단은 다음 메서드에 있습니다.

```csharp
public virtual async Task<bool> IsUnderHighLoadAsync(ILogger logger = null)
{
    return PerformanceCountersExceeded(logger: logger) || await ProcessThresholdsExceeded(logger: logger);
}
```

여기서 `PerformanceCountersExceeded`는 `ActiveConnections`, `Threads`, `NamedPipes` 같은 sandbox counter 임계치 초과 여부를 보고, `ProcessThresholdsExceeded`는 host/worker CPU, ThreadPool, gRPC channel health를 포괄하는 throttle 상태를 봅니다. 후자에서는 호스트가 자기가 가진 OOP worker 상태를 직접 묻는 코드도 나옵니다.

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

즉 외부에서 보면 HTTP 한 번이지만, 호스트 내부에서는 자기 자신과 모든 워커 상태를 합산한 결과를 바깥에 돌려주는 구조입니다. 이것이 인스턴스가 “여기까지가 내 현재 한계다”라고 바깥에 알리는 방식입니다.

### `ScaleMonitor`와 `TargetScaler`는 trigger가 직접 측정한 적체 신호입니다

health ping이 “지금 더 받을 수 있나”에 대한 호스트 쪽 답변이라면, `ScaleMonitor`와 `TargetScaler`는 “일이 얼마나 쌓였나”에 대한 trigger 쪽 답변입니다.

![Trigger metrics flowing into scale decisions](../../../assets/azure-functions-deep-dive/05/05-02-scalemonitor-and-targetscaler-the-signal.ko.png)

두 모드는 성격이 다릅니다.

`IScaleMonitor`는 기존 증분형 모델입니다. 각 monitor가 자기 메트릭을 보고 `ScaleVote`를 던지며, 한 라운드에 최대 1개 인스턴스만 증감합니다. 모든 trigger가 지원합니다.

`ITargetScaler`는 2022년 도입된 target-based 모델입니다. 기본식은 “event source length / target executions per instance = desired instances”입니다. Microsoft 문서 기준으로 여러 trigger에서 기본값이 정해져 있고, 4.19.0+에서는 기본 활성화됩니다. 필요하면 `TARGET_BASED_SCALING_ENABLED=0`으로 증분형으로 되돌릴 수 있습니다.

대표 trigger 기본값은 아래와 같습니다.

| Trigger | Setting for target executions per instance | Default |
|---|---|---|
| Storage Queue | `extensions.queues.batchSize` | 16 |
| Service Bus (single dispatch, v5+) | `extensions.serviceBus.maxConcurrentCalls` | 16 |
| Service Bus (batch, v5+) | `extensions.serviceBus.maxMessageBatchSize` | 1000 |
| Event Hubs (v5+) | `extensions.eventHubs.maxEventBatchSize` | 100 |
| Cosmos DB | `MaxItemsPerInvocation` (function attribute) | 100 |
| Apache Kafka | `LagThreshold` (function attribute) | 1000 |

호스트의 역할은 이 메트릭을 저장하는 repository입니다. 그 구현이 `TableStorageScaleMetricsRepository`이고, 외부 Scale Controller가 이 값을 읽어 판단합니다. 따라서 호스트는 메트릭 흐름의 중간 저장소이지 의사결정 주체가 아닙니다.

### 인스턴스 내부 동시성은 `WorkerConcurrencyManager`가 따로 관리합니다

외부 scale-out과 별개로, 같은 인스턴스 안에서 워커를 더 띄울지 결정하는 구성요소는 `WorkerConcurrencyManager`입니다. 이 경로는 겉보기보다 더 좁습니다. `StartAsync`는 Node, PowerShell, Python에 대해서만 동적 worker concurrency를 켜고, `HttpFunctionInvocationDispatcher` 경로는 제외하며, `FUNCTIONS_WORKER_PROCESS_COUNT`가 명시되면 아예 시작하지 않습니다.

즉 `FUNCTIONS_WORKER_PROCESS_COUNT`는 인스턴스당 정적 워커 수 설정이고, `WorkerConcurrencyOptions`는 지연 시간 히스토리를 기준으로 **워커를 하나 더 추가할지** 판단하는 동적 루프입니다. 둘은 대체 관계가 아닙니다.

`IsOverloaded`는 queue depth를 보지 않습니다. `LatencyHistory`에서 최근 샘플을 보고, 임계치 이상 비율이 `NewWorkerThreshold`를 넘으면 과부하라고 봅니다. 그 다음 `NewWorkerIsRequired`가 최소 한 워커가 과부하이고 현재 워커 수가 `MaxWorkerCount` 미만일 때만 새 워커를 추가합니다. 중요한 점은 이 코드에 대칭적인 scale-in 경로가 없다는 것입니다. 이것은 **외부 scale-out의 축소판이 아니라, 인스턴스 내부 병렬성 확장 루프**입니다.

| Aspect | Instance scale-out | Worker concurrency |
|---|---|---|
| Decided by | Scale Controller (external) | `WorkerConcurrencyManager` (inside the host) |
| Unit | VM instance | Worker process within an instance |
| Signal | ScaleMonitor metrics + health ping | Proportion of overloaded samples in `LatencyHistory` |
| Impact | Bill, cold-start time | Throughput within the instance |
| Scope | Varies by plan | Node / PowerShell / Python only; excludes HTTP worker; disabled when static process count is set |

### 같은 호스트 코드라도 플랜별 바깥 결정 계층이 다릅니다

아래 그림은 같은 코드가 플랜마다 다른 운영 의미를 갖는 이유를 보여 줍니다.

![Plan-specific scaling decision differences](../../../assets/azure-functions-deep-dive/05/05-03-plan-by-plan-same-code-different-behavio.ko.png)

#### Consumption

- 고전적인 Scale Controller가 결정합니다.
- scale to zero를 지원합니다.
- 최대 200 인스턴스입니다.
- target-based scaling을 지원합니다.

#### Flex Consumption

Flex Consumption은 사실상 Consumption의 후속 플랫폼입니다. 호스트 코드는 같지만 그 위의 결정 모델이 다릅니다.

- **per-function scaling**을 지원합니다. scale group은 `http`, `blob`, `durable`, `function:<NAMED_FUNCTION>`로 고정됩니다.
- **Always Ready** 인스턴스를 둘 수 있어 cold start를 줄이는 주된 레버가 됩니다.
- 앱당 기본 최대 인스턴스 수는 **100**이고, 필요하면 **1000까지 구성**할 수 있습니다.
- 지역 구독 쿼터는 별개입니다. 기본 지역 쿼터가 **250코어**이므로 앱 최대값을 올려도 그 전에 막힐 수 있습니다.
- 인스턴스 메모리를 512 / 2048 / 4096 MB에서 선택할 수 있습니다.

#### Premium

- pre-warmed 인스턴스가 있어 사실상 초기 Always Ready 역할을 합니다.
- VNet-bound trigger에서는 runtime scale monitoring을 켤 수 있어, 외부 Scale Controller가 VNet 밖에 있어도 host-side scale monitor 로직을 활용할 수 있습니다.
- target-based scaling을 지원합니다.

#### Dedicated

- Functions 이벤트 기반 scaler가 돌지 않습니다.
- App Service Auto-Scale 규칙이나 수동 확장을 사용합니다.
- 같은 host code가 돌아도, 바깥에서 인스턴스 수를 event-driven으로 결정해 주는 계층이 없으므로 ScaleMonitor 메트릭의 의미가 달라집니다.

전체를 한 표로 정리하면 아래와 같습니다.

| Plan | Scale decided by | Scale to zero | Max instances | Per-function | Always ready | VNet |
|---|---|---|---|---|---|---|
| Consumption | Scale Controller | Yes | 200 | No | No | No |
| Flex Consumption | Scale Controller (new) | Yes | 100 default; configurable to 1000 | Yes | Yes | Yes |
| Premium | Scale Controller (+ option) | No (min 1) | Varies by SKU/region | No | pre-warmed | Yes |
| Dedicated | App Service Auto-Scale | No | Depends on plan | No | Always On available | Yes |

## 흔히 헷갈리는 지점

- **호스트가 인스턴스 수를 직접 결정하지는 않습니다.** 호스트는 health ping과 메트릭을 내보내고, 외부 계층이 인스턴스 수를 결정합니다.
- **`IScaleMonitor`와 `ITargetScaler`는 host repo 안의 인터페이스가 아닙니다.** WebJobs SDK와 trigger extension 쪽 개념입니다.
- **worker concurrency는 scale-out이 아닙니다.** 같은 인스턴스 안에 워커를 더 추가하는 병렬성 메커니즘입니다.
- **`FUNCTIONS_WORKER_PROCESS_COUNT`와 `WorkerConcurrencyOptions`는 같은 축이 아닙니다.** 전자는 정적 워커 수, 후자는 지연 시간 기반 동적 추가입니다.
- **같은 host code가 돌더라도 플랜별 운영 의미는 달라집니다.** 바깥 결정 계층과 placeholder 정책, App Service autoscale 여부가 다르기 때문입니다.

## 운영 체크리스트

- [ ] 플랜 선택 시 비용과 지연 시간 trade-off를 표로 정리했습니다.
- [ ] burst 시나리오에 대한 부하 테스트와 결과 기록을 남겼습니다.
- [ ] concurrency 설정이 downstream quota와 충돌하지 않는지 확인했습니다.
- [ ] scale-in 시 graceful shutdown 동작을 검증했습니다.
- [ ] Premium 또는 Flex Consumption의 cold-start 보호 전략을 문서화했습니다.

## 정리

이번 글의 핵심은 스케일링을 한 단어로 보지 않는 것입니다. 인스턴스 수를 결정하는 scale-out은 호스트 바깥의 Scale Controller 또는 플랜별 외부 계층이 맡고, 호스트는 health ping과 trigger 메트릭 저장소 역할만 합니다. 반면 인스턴스 내부 워커 수 증가는 `WorkerConcurrencyManager`가 맡는 별도 메커니즘입니다.

이 구분을 잡아 두면 운영 질문이 훨씬 정확해집니다. “왜 인스턴스가 안 늘지?”는 외부 scale signal과 플랜 정책의 문제이고, “왜 같은 인스턴스 안에서 처리량이 낮지?”는 worker concurrency나 downstream bottleneck 문제일 가능성이 큽니다. 서로 다른 층의 문제를 같은 디버깅 경로로 섞지 않게 됩니다.

다음 글에서는 새 인스턴스가 실제로 만들어진 뒤 어떤 일이 벌어지는지 봅니다. scale-out이 인스턴스 수 증가를 설명한다면, 콜드 스타트는 그 인스턴스가 왜 때로는 즉시 응답하고 때로는 느리게 준비되는지를 설명합니다. 마지막 편에서는 placeholder에서 specialization으로 넘어가는 코드 경로를 추적하겠습니다.

<!-- toc:begin -->
## 시리즈 목차

- [호스트 부팅 — `WebJobsScriptHostService`부터 따라가기](./01-host-bootstrap.md)
- [Worker 프로세스 — 한 호스트에서 여러 언어 런타임이 같이 사는 법](./02-worker-process.md)
- [gRPC 이벤트 스트림 — 호스트와 워커는 무엇을 주고받는가](./03-grpc-event-stream.md)
- [Dispatcher와 Invocation — 함수 호출이 워커에 도달하기까지](./04-dispatcher-and-invocation.md)
- **스케일링 내부 동작 — Scale Controller, ScaleMonitor, 그리고 플랜별 차이 (현재 글)**
- 콜드 스타트와 Placeholder Mode — 새 인스턴스가 만들어질 때 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [`Azure/azure-functions-host @ 5e59423`](https://github.com/Azure/azure-functions-host/tree/5e59423ba45491041d18224c3e72c168a4a5b7f7)
- [`src/WebJobs.Script/Scale/HostPerformanceManager.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script/Scale/HostPerformanceManager.cs)
- [`src/WebJobs.Script/Scale/ApplicationPerformanceCounters.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script/Scale/ApplicationPerformanceCounters.cs)
- [`src/WebJobs.Script.WebHost/Scale/TableStorageScaleMetricsRepository.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.WebHost/Scale/TableStorageScaleMetricsRepository.cs)
- [`src/WebJobs.Script.Grpc/WorkerConcurrencyManager.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.Grpc/WorkerConcurrencyManager.cs)
- [Azure Functions Flex Consumption plan hosting](https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan)
- [Target-based scaling in Azure Functions](https://learn.microsoft.com/en-us/azure/azure-functions/functions-target-based-scaling)
- [Event-driven scaling in Azure Functions](https://learn.microsoft.com/en-us/azure/azure-functions/event-driven-scaling)
- [Azure Functions hosting options](https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale)

### 관련 시리즈
- [Azure Functions 101 — 스케일링과 콜드 스타트](../../azure-functions-101/ko/06-scaling-and-cold-start.md)
- [Azure Functions 101 — Host와 Worker](../../azure-functions-101/ko/03-host-and-worker.md)
- [Azure App Service Deep Dive — App Service 플랫폼 아키텍처](../../azure-app-service-deep-dive/ko/01-platform-architecture.md)

Tags: Azure Functions, Serverless, Distributed Systems, gRPC
