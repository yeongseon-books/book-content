---
title: "Azure Functions Deep Dive (6/6): 콜드 스타트와 Placeholder Mode — 새 인스턴스가 만들어질 때"
series: azure-functions-deep-dive
episode: 6
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

# Azure Functions Deep Dive (6/6): 콜드 스타트와 Placeholder Mode — 새 인스턴스가 만들어질 때

스케일아웃은 왜 새 인스턴스가 생겼는지를 설명해 줍니다. 하지만 사용자가 체감하는 문제는 그 다음에 남습니다. 어떤 인스턴스는 첫 요청을 거의 즉시 처리하는데, 어떤 인스턴스는 몇 초를 기다리게 만듭니다. 이 차이는 새 인스턴스가 **placeholder 상태에서 specialization 상태로 넘어가는 경로**에 숨어 있습니다.

콜드 스타트는 종종 “서버리스는 느리다”는 한 문장으로 소비되지만, 실제 비용은 하나가 아닙니다. VM 할당, 호스트 부팅, DI 컨테이너 준비, 코드 주입, 워커 재구성, `ScriptHost` 재시작이 서로 다른 단계로 쌓입니다. 따라서 정확한 운영 판단을 하려면 “콜드 스타트가 있다”가 아니라 “콜드 스타트 비용의 어느 부분이 공통이고 어느 부분이 사용자별인지”를 봐야 합니다.

이번 글은 [`Azure/azure-functions-host @ 5e59423`](https://github.com/Azure/azure-functions-host/tree/5e59423ba45491041d18224c3e72c168a4a5b7f7) 기준으로 `StandbyManager`, `PlaceholderSpecializationMiddleware`, `HostWarmupMiddleware`를 따라 placeholder 초기화, warmup, specialization, host restart까지 이어지는 경로를 정리합니다. 시리즈 마지막 글로서 앞선 다섯 편의 설명이 모두 여기로 모입니다.

이 글은 Azure Functions Deep Dive 시리즈의 마지막 글입니다.

이제 사용자가 실제로 체감하는 cold start가 어떤 코드 경로의 합으로 만들어지는지 끝까지 따라가겠습니다.

![Azure Functions Deep Dive 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/azure-functions-deep-dive/06/06-01-why-cold-start-is-expensive-decomposing.ko.png)
*Azure Functions Deep Dive 6장 흐름 개요*
> 콜드 스타트와 Placeholder Mode — 새 인스턴스가 만들어질 때의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 먼저 던지는 질문

- 호스트 부팅, 워커 시작, JIT 중 어느 부분이 cold start에서 가장 비쌀까요?
- Placeholder 인스턴스는 정확히 무엇을 미리 준비해 둘까요?
- Premium의 always-ready 인스턴스는 placeholder와 무엇이 다를까요?

## 왜 이 글이 중요한가

콜드 스타트는 비용과 지연 시간을 동시에 흔드는 주제입니다. 잘못 이해하면 “함수가 느리다”는 감각적인 표현만 남고, 실제로는 플랫폼이 미리 해 둘 수 있는 일과 사용자 코드 때문에 뒤로 밀리는 일을 구분하지 못하게 됩니다. 이 구분이 없으면 Always Ready, Premium pre-warmed, 의존성 경량화, lazy initialization 같은 대안을 서로 다른 층의 해결책으로 비교하지 못합니다.

또한 Placeholder Mode는 단순한 마케팅 용어가 아니라 호스트 코드에 실제로 드러나는 실행 전략입니다. 플랫폼은 사용자와 무관한 부트스트랩 단계를 미리 끝내 두고, 사용자가 배정된 뒤에만 specialization을 수행합니다. 즉 cold start 최적화는 “아무튼 빨리 한다”가 아니라 **공통 단계와 사용자별 단계를 분리하는 실행 모델**입니다.

시리즈 전체 관점에서도 이 글은 중요합니다. 1화에서 본 host bootstrap, 2화의 worker process, 3~4화의 host-worker protocol과 invocation, 5화의 scale-out이 모두 마지막에 새 인스턴스 한 대의 생애 주기로 다시 합쳐집니다. 이 마지막 그림이 잡혀야 Functions 운영 모델이 하나의 구조로 닫힙니다.

## 핵심 관점

콜드 스타트 비용은 하나의 거대한 지연이 아닙니다. VM 할당부터 DI 컨테이너 준비까지는 사용자 코드와 무관한 공통 비용이고, 코드 주입 이후는 사용자별 비용입니다. Placeholder Mode의 발상은 바로 이 선을 이용합니다. 플랫폼이 공통 비용을 미리 지불해 두고, 사용자가 실제로 배정되면 그 위에 specialization만 올리는 구조입니다.

이 관점을 잡으면 cold start 감소 전략도 훨씬 명확해집니다. Always Ready나 Premium pre-warmed는 specialization 이전 상태를 어디까지 미리 끝내 두느냐의 문제이고, 의존성 경량화는 specialization 이후 `RestartHostAsync` 비용을 얼마나 줄이느냐의 문제입니다. 서로 다른 지연을 다른 레버로 줄이는 셈입니다.

> 이번 글의 핵심은 cold start를 단일 현상이 아니라 “공통 placeholder 준비 + 사용자별 specialization + host restart”의 합으로 보는 것입니다.

## 핵심 개념

### 먼저 cold start 비용을 공통 단계와 사용자 단계로 나눠 봐야 합니다

새 인스턴스가 처음부터 함수를 실행할 준비가 될 때까지 거치는 단계는 다음처럼 나눌 수 있습니다.

1번부터 5번까지, 즉 VM 할당부터 DI 컨테이너 빌드까지는 **사용자 코드와 무관한 공통 부트스트랩**입니다. 6번 이후 코드 주입, 실제 런타임 환경 반영, worker specialization, host restart는 사용자별 단계입니다. Placeholder Mode는 바로 이 분리를 이용해 1~5번을 미리 끝내 둡니다.

### Placeholder는 `StandbyManager.InitializeAsync`에서 시작됩니다

플랫폼은 사용자가 없어도 warmed instance pool을 유지합니다. 이 인스턴스는 곧바로 사용자 앱으로 뜨지 않고 placeholder app으로 시작합니다. placeholder 단계에서 호스트가 실제로 해 두는 일은 `StandbyManager.InitializeAsync`와 warmup 경로를 함께 봐야 드러납니다.

```csharp
// src/WebJobs.Script.WebHost/Standby/StandbyManager.cs
public async Task InitializeAsync()
{
    using (_metricsLogger.LatencyEvent(MetricEventNames.SpecializationStandbyManagerInitialize))
    {
        if (await _semaphore.WaitAsync(timeout: TimeSpan.FromSeconds(30)))
        {
            try
            {
                // Flag to indicate a function was initialized from placeholder mode
                _environment.SetEnvironmentVariable(
                    EnvironmentSettingNames.InitializedFromPlaceholder, bool.TrueString);

                await CreateStandbyWarmupFunctions();

                // start a background timer to identify when specialization happens
                // specialization usually happens via an http request (e.g. scale controller
                // ping) but this timer is started as well to handle cases where we
                // might not receive a request
                _specializationTimer = new Timer(
                    OnSpecializationTimerTick, null,
                    _specializationTimerInterval, _specializationTimerInterval);
            }
            finally
            {
                _semaphore.Release();
            }
        }
    }
}
```

이 코드는 세 가지를 합니다. `InitializedFromPlaceholder` 환경변수를 세팅하고, placeholder 전용 `WarmUp` 함수 파일을 만들고, specialization 감지를 위한 50ms 주기 타이머를 시작합니다. 즉 placeholder는 빈 껍데기가 아니라 **warmup 전용 준비 상태를 가진 호스트**입니다.

### placeholder phase는 `WarmUp` 함수 파일과 JIT 준비 경로를 만듭니다

`CreateStandbyWarmupFunctions()`는 실제로 `WarmUp` 함수 디렉터리와 파일을 만듭니다.

```csharp
private async Task CreateStandbyWarmupFunctions()
{
    // ...
    string functionPath = Path.Combine(scriptPath, WarmUpConstants.FunctionName);
    Directory.CreateDirectory(functionPath);

    content = FileUtility.ReadResourceString(
        $"{ScriptConstants.ResourcePath}.Functions.{WarmUpConstants.FunctionName}.function.json");
    File.WriteAllText(Path.Combine(functionPath, "function.json"), content);

    content = FileUtility.ReadResourceString(
        $"{ScriptConstants.ResourcePath}.Functions.{WarmUpConstants.FunctionName}.run.csx");
    File.WriteAllText(Path.Combine(functionPath, "run.csx"), content);
    // ...
}
```

관련 상수는 `WarmUpConstants`에 있습니다.

```csharp
// src/WebJobs.Script.WebHost/Standby/WarmUpConstants.cs
public static class WarmUpConstants
{
    public const string FunctionName = "WarmUp";
    public const string AlternateRoute = "CSharpHttpWarmup";
    public const string PreJitFolderName = "PreJIT";
    public const string JitTraceFileName = "coldstart.jittrace";
    public const string LinuxJitTraceFileName = "linux.coldstart.jittrace";
}
```

중요한 점은 JIT trace 파일 이름이 여기 정의되어 있지만, 실제 실행은 나중 warmup 요청 경로에서 일어난다는 사실입니다. `StandbyManager.InitializeAsync`는 파일과 타이머를 준비하고, 이후 `HostWarmupMiddleware.WarmupInvoke`가 `PreJitPrepare`를 호출해 `coldstart.jittrace`를 사용합니다. Linux Consumption에서는 `linux.coldstart.jittrace`도 같이 사용됩니다.

즉 placeholder는 “미리 떠 있는 인스턴스”라는 추상 설명보다 더 구체적입니다. **공통 bootstrap을 끝내고 warmup 함수와 JIT 준비 경로를 심어 둔 호스트**입니다.

### specialization은 첫 요청 또는 50ms 타이머가 시작합니다

사용자 앱이 placeholder 인스턴스에 배정되면, 환경변수와 앱 콘텐츠는 들어오지만 호스트는 아직 placeholder 상태입니다. 이 전환을 middleware 첫 구간에서 감지하는 것이 `PlaceholderSpecializationMiddleware`입니다.

```csharp
// src/WebJobs.Script.WebHost/Middleware/PlaceholderSpecializationMiddleware.cs
public class PlaceholderSpecializationMiddleware
{
    private readonly RequestDelegate _next;
    private readonly IScriptWebHostEnvironment _webHostEnvironment;
    private readonly IStandbyManager _standbyManager;
    private readonly IEnvironment _environment;
    private RequestDelegate _invoke;
    private double _specialized = 0;

    public async Task Invoke(HttpContext httpContext)
    {
        await _invoke(httpContext);
    }

    private async Task InvokeSpecializationCheck(HttpContext httpContext)
    {
        if (!_webHostEnvironment.InStandbyMode && _environment.IsContainerReady())
        {
            // We don't want AsyncLocal context (like Activity.Current) to flow
            // here as it will contain request details.
            Task specializeTask;
            using (System.Threading.ExecutionContext.SuppressFlow())
            {
                specializeTask = _standbyManager.SpecializeHostAsync();
            }
            await specializeTask;

            if (Interlocked.CompareExchange(ref _specialized, 1, 0) == 0)
            {
                Interlocked.Exchange(ref _invoke, _next);
            }
        }

        await _next(httpContext);
    }
}
```

의도는 분명합니다. 첫 요청이 들어오면 specialization 체크를 하고, 컨테이너가 준비되었고 standby mode가 끝났다면 `SpecializeHostAsync()`를 호출합니다. `ExecutionContext.SuppressFlow()`는 현재 요청의 `AsyncLocal` 문맥이 specialization에 섞이지 않도록 막습니다. 이 세부 구현은 호스트가 **사용자 요청 한가운데서 자기 자신을 다시 구성**하는 코드라는 사실을 보여 줍니다.

그리고 50ms 타이머도 같은 일을 합니다.

```csharp
// same file, OnSpecializationTimerTick
private async void OnSpecializationTimerTick(object state)
{
    if (!_webHostEnvironment.InStandbyMode && _environment.IsContainerReady())
    {
        _specializationTimer?.Dispose();
        _specializationTimer = null;

        await SpecializeHostAsync();
    }
}
```

즉 specialization 트리거는 두 가지입니다. **첫 HTTP 요청** 또는 **50ms 타이머의 container-ready 감지**입니다. 둘 중 무엇이 먼저 오든 결과는 같습니다.

### specialization의 본체는 `SpecializeHostCoreAsync`입니다

placeholder 호스트를 실제 사용자 앱으로 바꾸는 본체는 `StandbyManager.SpecializeHostCoreAsync`입니다.

```csharp
// src/WebJobs.Script.WebHost/Standby/StandbyManager.cs
public async Task SpecializeHostCoreAsync()
{
    Activity activity = Activity.Current;
    activity.SetColdStartTag();

    // Go async immediately to ensure that any async context from
    // the PlaceholderSpecializationMiddleware is properly suppressed.
    await Task.Yield();

    using var initActivity = ActivityExtensions.StartSpecializationActivity();

    ApplyMcpCustomHandlerSettings();

    _logger.LogInformation(Resources.HostSpecializationTrace);

    // After specialization, we need to ensure that custom timezone
    // settings configured by the user (WEBSITE_TIME_ZONE) are honored.
    TimeZoneInfo.ClearCachedData();

    // Trigger a configuration reload to pick up all current settings
    _configuration?.Reload();

    _hostNameProvider.Reset();

    // Reset the shared load context to ensure we're reloading
    // user dependencies
    FunctionAssemblyLoadContext.ResetSharedContext();

    // Signals change of JobHost options from placeholder mode
    // (ex: ScriptPath is updated)
    NotifyChange();

    using (_metricsLogger.LatencyEvent(MetricEventNames.SpecializationLanguageWorkerChannelManagerSpecialize))
    {
        await _workerManager.SpecializeAsync();
    }

    using (_metricsLogger.LatencyEvent(MetricEventNames.SpecializationRestartHost))
    {
        await _scriptHostManager.RestartHostAsync("Host specialization.");
    }

    using (_metricsLogger.LatencyEvent(MetricEventNames.SpecializationDelayUntilHostReady))
    {
        await _scriptHostManager.DelayUntilHostReadyAsync();
    }
}
```

이 메서드 안에 cold start의 핵심이 있습니다.

첫째, `activity.SetColdStartTag()`로 cold start telemetry를 표시합니다. 둘째, timezone, configuration, hostname, assembly load context를 모두 reset해 placeholder 동안 캐시된 환경을 버립니다. 셋째, `_workerManager.SpecializeAsync()`로 worker specialization을 수행합니다. 넷째, `RestartHostAsync()`와 `DelayUntilHostReadyAsync()`로 specialized host가 실제 invocation을 받을 때까지 기다립니다.

사용자가 체감하는 cold start 비용의 대부분은 바로 이 specialization + host restart 구간에서 나옵니다. .NET CLR과 DI 컨테이너가 이미 따뜻하더라도, 사용자 환경으로 다시 구성하고 host를 재기동하는 비용은 사라지지 않습니다.

### placeholder channel 재사용은 조건부입니다

out-of-proc worker specialization은 “항상 placeholder worker를 버리고 새 워커를 띄운다”가 아닙니다. `StandbyManager`는 `_workerManager.SpecializeAsync()`만 호출하고, 실제 분기는 `WebHostRpcWorkerChannelManager.SpecializeAsync()` 안의 `UsePlaceholderChannel(...)`에 있습니다.

reuse가 허용되면 placeholder 채널을 유지한 채 `rpcWorkerChannel.SendFunctionEnvironmentReloadRequest()`를 보내 환경을 다시 로드합니다. reuse가 불가능하거나 reload가 실패하면 그때 placeholder 채널을 종료하고 새 경로로 갑니다.

분기 조건은 꽤 구체적입니다.

- 공통 gate: custom `languageWorkers:<runtime>:arguments`가 있으면 재사용하지 않습니다.
- `dotnet-isolated`: `UsePlaceholderDotNetIsolated()`가 켜져 있어야 하고, 64-bit이며, 사이트 런타임 버전이 placeholder worker와 맞아야 합니다.
- `node` / `python` / `powershell`: 파일시스템이 read-only여야 하고, `~3` + v2 compatibility 경로가 아니어야 합니다.
- 마지막 공통 gate: `_profileManager.IsCorrectProfileLoaded(workerRuntime)`가 true여야 합니다.

즉 재사용 여부는 막연한 “호환되면 재사용”이 아니라 런타임 종류, bitness, 버전, 파일시스템 모드, profile 적합성을 실제 코드로 확인한 뒤 결정됩니다.

### specialization 이후 middleware는 자기 자신을 핫패스에서 빼 버립니다

`PlaceholderSpecializationMiddleware`를 한 번 더 보면 재미있는 설계가 보입니다.

```csharp
if (Interlocked.CompareExchange(ref _specialized, 1, 0) == 0)
{
    Interlocked.Exchange(ref _invoke, _next);
}
```

specialization이 끝나면 `_invoke`가 직접 `_next`를 가리키도록 바뀝니다. 즉 두 번째 요청부터는 specialization check branch 자체가 사라집니다. 이것이 “cold start 비용은 첫 요청에서만 크다”는 운영 감각의 코드 수준 근거입니다. 콜드 패스는 한 번만 타고, 이후에는 일반 핫패스만 남습니다.

### 인스턴스 생애 주기를 한 장으로 보면 시리즈가 닫힙니다

이제 전체 생애 주기를 한 장으로 보면 앞선 글들이 모두 여기서 합쳐집니다.

![Instance lifecycle from placeholder to execution](https://yeongseon-books.github.io/book-public-assets/assets/azure-functions-deep-dive/06/06-02-the-whole-picture-the-life-of-an-instanc.ko.png)

scale-out으로 인스턴스가 생기고, placeholder가 공통 bootstrap을 준비하고, specialization이 사용자 환경을 입히고, host가 다시 준비 완료가 되면 invocation 경로와 worker channel, gRPC transport가 실제 요청을 받기 시작합니다.

### 플랜에 따라 cold start가 다르게 느껴지는 이유도 같은 코드 위에서 설명됩니다

같은 호스트 코드라도 플랜은 placeholder pool을 다르게 운용합니다.

| Plan | Cold start frequency | Mechanism |
|---|---|---|
| Consumption | Frequent (scale 0 → 1, or every new instance) | placeholder → specialization every time |
| Flex Consumption (on-demand) | Frequent (scale 0 → 1) | placeholder → specialization every time |
| Flex Consumption (Always Ready) | Almost none | Always-specialized instances kept around |
| Premium (pre-warmed) | Almost none (small on scale-out) | Pre-warmed instances play a role similar to the placeholder pool |
| Dedicated | Only at instance boot | App Service always-on, no placeholders involved |

Flex Consumption의 Always Ready는 사실상 **specialization까지 끝난 인스턴스를 유지하는 정책**이고, Premium의 pre-warmed도 비슷한 역할을 합니다. 반대로 Consumption은 placeholder → specialization 경로를 자주 타므로 사용자가 cold start를 더 자주 체감합니다. 즉 host code는 같아도, 사용자가 느끼는 cold start는 **외부 placeholder policy와 Always Ready 수량**이 결정합니다.

### 코드 수준에서 cold start를 줄이는 레버도 분해해서 봐야 합니다

host code를 따라가고 나면 어떤 레버가 어느 단계를 줄이는지 명확해집니다.

| Lever | Stage affected | Rationale |
|---|---|---|
| Always Ready instances | Skips specialization entirely | Flex Consumption docs + the code flow above |
| Premium pre-warmed | Owns a specialization pool directly | Same |
| Lighter dependencies | User-code load time during `RestartHostAsync` | `FunctionAssemblyLoadContext.ResetSharedContext` |
| Smaller deployment package | Content injection time | Outside this code; platform layer |
| Latest Functions runtime | Improved JIT trace | `WarmUpConstants.JitTraceFileName` |
| Application Initialization (Premium/Dedicated) | Time from host-ready to first request | App Service layer |

특히 `FunctionAssemblyLoadContext.ResetSharedContext()`가 specialization 단계 안에 있다는 사실은, 사용자 의존성이 무거울수록 specialization 시간이 직접 늘어난다는 것을 코드 수준에서 보여 줍니다. 큰 Python venv, 큰 .NET 패키지 묶음은 cold start를 체감적으로 늘릴 수 있습니다.

## 흔히 헷갈리는 지점

- **cold start는 단일 비용이 아닙니다.** 공통 placeholder 준비와 사용자별 specialization 비용이 합쳐진 결과입니다.
- **placeholder는 빈 프로세스가 아닙니다.** `WarmUp` 함수 파일, specialization 타이머, JIT warmup 경로를 갖춘 준비 상태입니다.
- **specialization은 첫 요청만이 유일한 트리거가 아닙니다.** 50ms 타이머의 container-ready 감지도 같은 경로를 시작할 수 있습니다.
- **worker specialization은 항상 새 워커를 띄우는 방식이 아닙니다.** 조건이 맞으면 placeholder channel을 재사용하고 `FunctionEnvironmentReloadRequest`를 보냅니다.
- **플랜별 cold start 차이는 host code 차이보다 placeholder policy 차이에서 더 많이 옵니다.** Always Ready, pre-warmed, App Service always-on 여부가 다르기 때문입니다.

## 운영 체크리스트

- [ ] cold-start 비용을 단계별로 측정하고 기록했습니다.
- [ ] 워크로드별 Premium 또는 Always Ready 인스턴스 수를 결정했습니다.
- [ ] 연결 초기화 같은 작업의 lazy/eager 정책을 문서화했습니다.
- [ ] SLO 문서에 cold-start latency 항목을 별도로 명시했습니다.
- [ ] scale-out으로 사용자가 cold start를 직접 맞는 시나리오를 부하 테스트했습니다.

## 정리

이번 글은 cold start를 설명 가능한 코드 경로로 바꿨습니다. placeholder 인스턴스는 공통 bootstrap을 미리 끝내고 `WarmUp` 함수와 JIT warmup 경로를 준비합니다. 이후 첫 요청 또는 50ms 타이머가 specialization을 시작하고, 환경 재설정, worker specialization, `ScriptHost` 재시작, host-ready 대기까지가 사용자가 실제로 느끼는 cold-start 비용을 만듭니다.

이 관점이 중요한 이유는 cold start 최적화가 더 이상 막연한 “성능 개선”이 아니게 되기 때문입니다. Always Ready와 pre-warmed는 specialization 자체를 건너뛰게 하는 전략이고, 의존성 경량화는 specialization 이후 host restart 구간을 줄이는 전략이며, 최신 런타임 사용은 JIT warmup 경로를 개선하는 전략입니다. 서로 다른 비용에 서로 다른 레버가 대응합니다.

이 글로 Azure Functions Deep Dive 시리즈를 마칩니다. 1화의 host bootstrap, 2화의 worker process, 3~4화의 gRPC 채널과 invocation, 5화의 scale-out이 모두 마지막에 한 인스턴스의 생애 주기로 닫혔습니다. 이제 Functions 운영을 볼 때는 “서버리스라서 느릴 수 있다”가 아니라, 어느 단계의 bootstrap과 specialization이 지금 지연을 만들고 있는지 더 정확하게 질문할 수 있습니다.

## 처음 질문으로 돌아가기

- **호스트 부팅, 워커 시작, JIT 중 어느 부분이 cold start에서 가장 비쌀까요?**
  - 본문의 기준은 콜드 스타트와 Placeholder Mode — 새 인스턴스가 만들어질 때를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **Placeholder 인스턴스는 정확히 무엇을 미리 준비해 둘까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **Premium의 always-ready 인스턴스는 placeholder와 무엇이 다를까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Azure Functions Deep Dive (1/6): 호스트 부팅 — `WebJobsScriptHostService`부터 따라가기](./01-host-bootstrap.md)
- [Azure Functions Deep Dive (2/6): Worker 프로세스 — 한 호스트에서 여러 언어 런타임이 같이 사는 법](./02-worker-process.md)
- [Azure Functions Deep Dive (3/6): gRPC 이벤트 스트림 — 호스트와 워커는 무엇을 주고받는가](./03-grpc-event-stream.md)
- [Azure Functions Deep Dive (4/6): Dispatcher와 Invocation — 함수 호출이 워커에 도달하기까지](./04-dispatcher-and-invocation.md)
- [Azure Functions Deep Dive (5/6): 스케일링 내부 동작 — Scale Controller, ScaleMonitor, 그리고 플랜별 차이](./05-scaling-internals.md)
- **Azure Functions Deep Dive (6/6): 콜드 스타트와 Placeholder Mode — 새 인스턴스가 만들어질 때 (현재 글)**

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [`Azure/azure-functions-host @ 5e59423`](https://github.com/Azure/azure-functions-host/tree/5e59423ba45491041d18224c3e72c168a4a5b7f7)
- [`src/WebJobs.Script.WebHost/Standby/IStandbyManager.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.WebHost/Standby/IStandbyManager.cs)
- [`src/WebJobs.Script.WebHost/Standby/StandbyManager.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.WebHost/Standby/StandbyManager.cs)
- [`src/WebJobs.Script.WebHost/Standby/WarmUpConstants.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.WebHost/Standby/WarmUpConstants.cs)
- [`src/WebJobs.Script.WebHost/Standby/StandbyChangeTokenSource.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.WebHost/Standby/StandbyChangeTokenSource.cs)
- [`src/WebJobs.Script.WebHost/Standby/StandbyInitializationService.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.WebHost/Standby/StandbyInitializationService.cs)
- [`src/WebJobs.Script.WebHost/Middleware/PlaceholderSpecializationMiddleware.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.WebHost/Middleware/PlaceholderSpecializationMiddleware.cs)
- [`src/WebJobs.Script.WebHost/Middleware/HostWarmupMiddleware.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423ba45491041d18224c3e72c168a4a5b7f7/src/WebJobs.Script.WebHost/Middleware/HostWarmupMiddleware.cs)
- [Azure Functions Flex Consumption — Always ready instances](https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan#always-ready-instances)
- [Azure Functions cold starts](https://learn.microsoft.com/en-us/azure/azure-functions/event-driven-scaling#cold-start)

### 관련 시리즈
- [Azure Functions 101 — 스케일링과 콜드 스타트](../../azure-functions-101/ko/06-scaling-and-cold-start.md)
- [Azure Functions Deep Dive — 호스트 부팅](./01-host-bootstrap.md)
- [Azure Functions Deep Dive — 스케일링 내부 동작](./05-scaling-internals.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-functions-deep-dive/ko/06-cold-start-placeholder)

Tags: Azure Functions, Serverless, Distributed Systems, gRPC
