---
title: "Azure Functions Deep Dive (1/6): 호스트 부팅 — `WebJobsScriptHostService`부터 따라가기"
series: azure-functions-deep-dive
episode: 1
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

# Azure Functions Deep Dive (1/6): 호스트 부팅 — `WebJobsScriptHostService`부터 따라가기

Azure Functions를 운영하다 보면 가장 먼저 부딪히는 질문은 의외로 단순합니다. 새 인스턴스가 켜질 때 정확히 어디까지를 호스트 부팅이라고 부를 수 있는지, 그리고 어느 시점부터 함수가 실제 호출을 받을 준비가 끝났다고 봐야 하는지입니다. 이 경계를 모르면 시작 실패, 재시작, 리스너 활성화 지연 같은 현상이 한 덩어리로 보입니다.

이번 시리즈는 문서 요약이 아니라 호스트 소스를 직접 따라가며 그 경계를 고정하는 작업입니다. 기준은 [`Azure/azure-functions-host @ 5e59423`](https://github.com/Azure/azure-functions-host/tree/5e59423ba45491041d18224c3e72c168a4a5b7f7)입니다. 이후 글들도 모두 같은 커밋에 고정해, 설명과 코드가 어긋나지 않도록 맞춥니다.

이번 글의 초점은 부팅 직후입니다. `Program.cs`의 표면적인 진입점보다 한 단계 안쪽으로 들어가, `WebJobsScriptHostService`가 `ScriptHost`를 만들고 `InitializeAsync`를 끝낼 때까지 무슨 준비를 하는지 봅니다. 함수 메타데이터 인덱싱과 host.json 옵션 로딩이 정확히 어디에 들어가는지도 이 경로 안에서 확인합니다.

이 글은 Azure Functions Deep Dive 시리즈의 첫 번째 글입니다.

이제 이후 다섯 편의 기준점이 되는 호스트 부팅 경계를 먼저 선명하게 고정하겠습니다.

## 먼저 던지는 질문

- Functions Host는 정확히 어떤 프로세스이며, 어떤 순서로 부팅될까요?
- `host.json`은 단순 설정 파일일까요, 아니면 런타임 동작을 바꾸는 실제 구성 입력일까요?
- 호스트 시작 실패는 어디에 기록되고, 첫 번째 진단 지점은 어디일까요?

## 큰 그림

![Azure Functions Deep Dive 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/azure-functions-deep-dive/01/01-01-the-big-picture-one-azure-functions-host.ko.png)

*Azure Functions Deep Dive 1장 흐름 개요*

이 그림에서는 호스트 부팅 — `WebJobsScriptHostService`부터 따라가기를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 호스트 부팅 — `WebJobsScriptHostService`부터 따라가기의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 이 글이 중요한가

운영에서 자주 보는 증상은 “앱이 안 뜬다”라는 한 문장으로 들어오지만, 실제 원인은 제각각입니다. `host.json` 옵션이 잘못 들어가 부팅이 깨질 수도 있고, 함수 메타데이터 인덱싱이 끝나지 않았을 수도 있고, 그 다음 단계인 리스너 시작에서 시간이 걸릴 수도 있습니다. 부팅 경계를 모르면 서로 다른 장애 모드를 하나로 뭉뚱그리게 됩니다.

또 하나 중요한 점은 Azure Functions의 언어 실행 모델이 호스트와 워커로 분리되어 있다는 사실입니다. 이 시리즈는 gRPC 채널, 워커 프로세스, 스케일링, 콜드 스타트까지 모두 다루지만, 그 모든 설명은 `ScriptHost`가 언제 준비 완료 상태가 되는지 이해한 뒤에야 의미를 갖습니다. 첫 단추가 틀리면 이후 개념도 계속 비껴갑니다.

무엇보다 이 글은 운영자가 로그를 읽는 순서를 바꿔 줍니다. “왜 함수가 실행되지 않았지?”가 아니라 “호스트가 부팅을 끝냈는지, 함수 목록을 만들었는지, 리스너 시작 직전까지 도달했는지”를 먼저 묻게 만듭니다. 이 차이가 있어야 재시작 로그와 시작 실패 로그를 같은 의미로 오해하지 않게 됩니다.

## 핵심 관점

Azure Functions 호스트 부팅은 거대한 블랙박스처럼 보이지만, 실제로는 역할이 분명한 두 층으로 나뉩니다. 바깥쪽에는 ASP.NET Core 호스팅 모델 위에 올라간 `WebJobsScriptHostService`가 있고, 안쪽에는 실제 함수 앱 준비를 수행하는 `ScriptHost`가 있습니다. 바깥 껍질은 생명주기를 관리하고, 안쪽 커널은 설정 로드·메타데이터 인덱싱·리스너 시작 직전 상태까지를 책임집니다.

이 구분이 중요한 이유는 회복 전략이 바로 여기서 나오기 때문입니다. 호스트가 죽더라도 외피가 살아 있으면 새 `ScriptHost`를 만들어 다시 붙일 수 있습니다. 즉, “호스트가 재시작됐다”는 운영 현상을 볼 때 실제로 교체된 것이 무엇인지 구분할 수 있어야 합니다.

> 이 글에서 호스트 부팅이란 ASP.NET Core 프로세스 전체가 아니라, `WebJobsScriptHostService`가 `ScriptHost`를 구성하고 `InitializeAsync`를 끝내서 리스너 시작 직전까지 올려놓는 경계입니다.

## 핵심 개념

### 시리즈 전체 지도를 먼저 머리에 넣어야 합니다

이 그림은 이번 시리즈 전체의 기준점입니다. 이번 글은 이 중에서 Host 부팅 경계만 따로 떼어 봅니다.

인스턴스 안에는 Host와 Worker가 함께 있지만, 이번 글의 범위는 Worker와의 실제 통신 이전입니다. 먼저 Host가 함수 앱으로서 서기 위해 무엇을 끝내야 하는지부터 확정해야 이후 gRPC 채널과 invocation 경로도 정확히 읽을 수 있습니다.

### 호스트 부팅은 네 단계로 압축됩니다

겉으로는 복잡해 보여도, 이번 글이 따라갈 경로는 결국 네 단계입니다.

![호스트 부팅 4단계 진행 흐름](https://yeongseon-books.github.io/book-public-assets/assets/azure-functions-deep-dive/01/01-02-the-big-picture-host-bootstrap-in-4-stag.ko.png)

1단계는 `WebJobsScriptHostService` 진입, 2단계는 `ScriptHost.InitializeAsync`, 3단계는 `host.json`의 구성 트리 편입, 4단계는 함수 메타데이터 인덱싱입니다. 여기까지 끝나면 트리거가 들어왔을 때 함수를 받을 준비가 됩니다.

### 1단계: `WebJobsScriptHostService`는 호스트 자체가 아니라 호스트 수명주기 관리자입니다

ASP.NET Core 호스트가 올라오면 Functions 쪽 진짜 주인공은 `IHostedService` 구현인 `WebJobsScriptHostService`입니다. `StartAsync` 안에서 이 서비스는 타이머 기반 호스트 헬스 체크 루프를 만들고, `HostPerformanceManager`와 연결하고, `ScriptHost`를 만든 뒤 `InitializeAsync`를 호출합니다. 실패 시 재시도와 재시작 정책도 이 바깥층이 잡습니다.

이 지점에서 가장 중요한 사실은 **`WebJobsScriptHostService`가 호스트 자체가 아니라는 점**입니다. 실제 함수 앱 호스트는 내부의 `ScriptHost`이고, `WebJobsScriptHostService`는 그것을 감싸는 외피입니다. 이 분리 덕분에 안쪽 커널이 죽어도 바깥쪽이 새 커널을 만들어 교체할 수 있습니다.

### 2단계: `ScriptHost.InitializeAsync`에서 실제 부팅 작업이 일어납니다

호스트 준비의 실질적인 내용은 `ScriptHost.InitializeAsync` 안에 있습니다. 여기서 설정을 읽고, 함수 메타데이터를 인덱싱하고, 나중에 리스너가 붙을 수 있는 런타임 기반을 만듭니다.

![초기화 단계에서 진행되는 호스트 준비 흐름](https://yeongseon-books.github.io/book-public-assets/assets/azure-functions-deep-dive/01/01-03-stage-2-scripthost-initializeasync-where.ko.png)

순서도 중요합니다. `ScriptHost.StartAsyncCore()`는 먼저 `InitializeAsync()`를 끝까지 수행한 뒤에야 `base.StartAsyncCore()`를 호출합니다. 따라서 `JobHost.StartAsync()`로 이어지는 트리거 리스너 활성화는 초기화 내부가 아니라 그 **다음 단계**입니다. 이 선을 알아야 부팅 실패와 리스너 활성화 실패를 분리해 읽을 수 있습니다.

### 3단계: `host.json`은 `IConfiguration` 트리로 들어가 런타임 옵션이 됩니다

`host.json`은 단순 파일이 아니라 런타임 옵션의 실제 입력입니다. `HostJsonFileConfigurationSource`가 파일을 읽어 .NET `IConfiguration` 트리에 넣고, `WellKnownHostJsonProperties`가 알려진 키 집합을 정의합니다. `concurrency`, `extensions.queues`, `extensions.http`, `functionTimeout` 같은 값이 여기서 시작됩니다.

그 뒤 매핑은 매우 직접적입니다. 예를 들어 `functionTimeout`은 `ScriptJobHostOptionsSetup.ConfigureFunctionTimeout`를 거쳐 `ScriptJobHostOptions.FunctionTimeout`으로 들어갑니다.

![host.json 설정이 옵션으로 매핑되는 경로](https://yeongseon-books.github.io/book-public-assets/assets/azure-functions-deep-dive/01/01-04-stage-3-where-and-how-host-json-is-read.ko.png)

운영에서 중요한 포인트는 두 가지입니다. 첫째, 환경변수도 같은 `IConfiguration` 트리에 들어가므로 `host.json` 값을 덮어쓸 수 있습니다. 둘째, `FUNCTIONS_WORKER_PROCESS_COUNT` 같은 앱 설정은 호스트 부팅 단계에서 워커 프로세스 수 결정에 직접 영향을 줍니다. 즉 파일 설정과 환경 설정은 같은 구성 시스템 안에서 만납니다.

### 4단계: 함수 메타데이터 인덱싱은 호스트의 함수 카탈로그를 만듭니다

설정을 읽은 뒤 `ScriptHost`는 앱 안에 어떤 함수가 있는지 인덱싱합니다. 그 결과는 `FunctionMetadata` 목록이며, 여기에는 함수 이름, 트리거 종류와 설정, 입출력 바인딩, 코드 진입점, 사용 언어가 들어갑니다.

이 단계가 중요한 이유는 이후 모든 동작이 이 메타데이터에 기대기 때문입니다. 워커는 먼저 `WorkerInitRequest`로 호스트 capability를 받고, 실제 함수 목록은 `FunctionLoadRequest` 또는 `FunctionLoadRequestCollection`으로 받습니다. 트리거 리스너도 이 목록을 기준으로 어떤 큐를 폴링하고 어떤 라우트를 잡을지 결정합니다.

즉 인덱싱은 단순 탐색이 아니라 **호스트가 자신이 실행할 함수들의 카탈로그를 확정하는 단계**입니다. 이후 gRPC 채널, invocation, scale signal은 모두 이 목록이 있다는 전제 위에서 움직입니다.

### 헬스 모니터는 별도 서비스가 아니라 타이머 루프와 성능 관리자 조합입니다

`WebJobsScriptHostService`는 생성자에서 `_hostHealthCheckTimer`를 만들고, 주기적으로 `OnHostHealthCheckTimer`를 호출합니다. 이 루프가 `HostPerformanceManager`와 함께 현재 인스턴스가 건강한지, 과부하인지, 재시작이 필요한지를 판단합니다.

![호스트 상태 점검과 재시작 판단 흐름](https://yeongseon-books.github.io/book-public-assets/assets/azure-functions-deep-dive/01/01-05-the-host-health-monitor.ko.png)

따라서 별도 “헬스 모니터 서비스”를 상상할 필요는 없습니다. 이 저장소 안에서 보이는 구현은 타이머 루프와 성능 판단 조합입니다. 부팅 예외, 지나치게 긴 부팅 시간, 메모리·CPU 임계치 초과 같은 현상이 결국 여기서 재시작 판단으로 이어집니다.

### 운영 점검에 바로 쓸 수 있는 명령

아래 명령은 현재 함수 앱의 핵심 앱 설정과 라이브 로그를 빠르게 확인할 때 유용합니다.

```bash
az functionapp config appsettings list -n my-func -g my-rg \
  --query "[?starts_with(name, 'FUNCTIONS_') || starts_with(name, 'WEBSITE_')]" -o table

az functionapp log tail -n my-func -g my-rg
```

이 출력에서 `FUNCTIONS_EXTENSION_VERSION`, 워커 관련 설정, `WEBSITE_` 계열 값과 시작 로그를 함께 보면, 호스트 부팅 문제인지 워커 연결 이후 문제인지 빠르게 범위를 좁힐 수 있습니다.

## 흔히 헷갈리는 지점

- **`WebJobsScriptHostService`가 곧 실행 호스트는 아닙니다.** 이것은 수명주기 관리자이고, 실제 함수 앱 호스트는 내부의 `ScriptHost`입니다.
- **`host.json`은 단순 문서형 설정이 아닙니다.** `IConfiguration`과 옵션 객체로 바로 이어지는 런타임 입력입니다.
- **함수 메타데이터 인덱싱은 선택적 부가 단계가 아닙니다.** 워커 로드와 트리거 리스너 활성화의 전제가 되는 카탈로그 생성 단계입니다.
- **호스트 시작과 리스너 시작은 같은 순간이 아닙니다.** `InitializeAsync`가 끝난 뒤에야 `JobHost.StartAsync()`가 이어집니다.
- **재시작 로그가 보인다고 해서 항상 앱 코드 문제는 아닙니다.** 타이머 기반 헬스 모니터와 성능 판단이 호스트 교체를 일으킬 수도 있습니다.

## 운영 체크리스트

- [ ] `FUNCTIONS_EXTENSION_VERSION`과 워커 런타임 버전을 명시적으로 고정했습니다.
- [ ] `host.json` 변경이 포함될 때 회귀 테스트 절차를 문서화했습니다.
- [ ] 호스트 시작 실패와 반복 재시작에 대한 알림 규칙을 만들었습니다.
- [ ] Host와 Worker가 별도 프로세스라는 실행 모델을 팀 운영 문서에 반영했습니다.
- [ ] 시작 로그를 볼 때 부팅 단계와 리스너 활성화 단계를 분리해서 읽도록 RUNBOOK을 정리했습니다.

## 정리

이번 글의 핵심은 호스트 부팅을 하나의 덩어리로 보지 않는 것입니다. ASP.NET Core 위에서 `WebJobsScriptHostService`가 수명주기를 잡고, 그 안에서 `ScriptHost`가 설정 로드와 함수 메타데이터 인덱싱을 수행한 뒤, 그 다음에야 리스너 시작 단계로 넘어갑니다. 이 순서를 알면 “함수가 왜 아직 실행되지 않는가”라는 질문이 훨씬 구체적인 단계 질문으로 바뀝니다.

또한 `host.json`과 환경변수가 같은 구성 트리 안에서 런타임 옵션으로 합쳐진다는 점도 중요합니다. 운영자는 설정 파일과 앱 설정을 따로 보지 말고, 하나의 호스트 구성 표면으로 봐야 합니다. 이 관점을 잡아 두면 워커 수, 타임아웃, 동시성 설정이 왜 부팅 초기에 이미 결정되는지 이해하기 쉬워집니다.

이제 시리즈는 이 부팅 경계 바깥으로 한 단계 더 나갑니다. 다음 글에서는 호스트가 선택한 언어 런타임을 어떻게 실제 OS 프로세스로 띄우는지, 그리고 그 과정이 어디서부터 운영체제 수준의 워커 관리 문제로 바뀌는지를 보겠습니다.

## 처음 질문으로 돌아가기

- **Functions Host는 정확히 어떤 프로세스이며, 어떤 순서로 부팅될까요?**
  - 본문의 기준은 호스트 부팅 — `WebJobsScriptHostService`부터 따라가기를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **`host.json`은 단순 설정 파일일까요, 아니면 런타임 동작을 바꾸는 실제 구성 입력일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **호스트 시작 실패는 어디에 기록되고, 첫 번째 진단 지점은 어디일까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- **Azure Functions Deep Dive (1/6): 호스트 부팅 — `WebJobsScriptHostService`부터 따라가기 (현재 글)**
- Azure Functions Deep Dive (2/6): Worker 프로세스 — 한 호스트에서 여러 언어 런타임이 같이 사는 법 (예정)
- Azure Functions Deep Dive (3/6): gRPC 이벤트 스트림 — 호스트와 워커는 무엇을 주고받는가 (예정)
- Azure Functions Deep Dive (4/6): Dispatcher와 Invocation — 함수 호출이 워커에 도달하기까지 (예정)
- Azure Functions Deep Dive (5/6): 스케일링 내부 동작 — Scale Controller, ScaleMonitor, 그리고 플랜별 차이 (예정)
- Azure Functions Deep Dive (6/6): 콜드 스타트와 Placeholder Mode — 새 인스턴스가 만들어질 때 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [`Azure/azure-functions-host @ 5e59423`](https://github.com/Azure/azure-functions-host/tree/5e59423ba45491041d18224c3e72c168a4a5b7f7)
- [`WebJobsScriptHostService.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423/src/WebJobs.Script.WebHost/WebJobsScriptHostService.cs)
- [`ScriptHost.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423/src/WebJobs.Script/Host/ScriptHost.cs)
- [`HostJsonFileConfigurationSource.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423/src/WebJobs.Script/Config/HostJsonFileConfigurationSource.cs)
- [`ScriptJobHostOptionsSetup.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423/src/WebJobs.Script/Config/ScriptJobHostOptionsSetup.cs)
- [host.json reference](https://learn.microsoft.com/en-us/azure/azure-functions/functions-host-json)
- [Azure Functions app settings reference](https://learn.microsoft.com/en-us/azure/azure-functions/functions-app-settings)
- [PR #4210 — introducing `FUNCTIONS_WORKER_PROCESS_COUNT`](https://github.com/Azure/azure-functions-host/pull/4210)

### 관련 시리즈
- [Azure Functions 101 — Host와 Worker](../../azure-functions-101/ko/03-host-and-worker.md)
- [Azure Functions 101 — 스케일링과 콜드 스타트](../../azure-functions-101/ko/06-scaling-and-cold-start.md)
- [Azure App Service Deep Dive — App Service 플랫폼 아키텍처](../../azure-app-service-deep-dive/ko/01-platform-architecture.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-functions-deep-dive/ko/01-host-bootstrap)

Tags: Azure Functions, Serverless, Distributed Systems, gRPC
