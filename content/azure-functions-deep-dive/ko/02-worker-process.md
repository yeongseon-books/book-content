---
title: "Azure Functions Deep Dive (2/6): Worker 프로세스 — 한 호스트에서 여러 언어 런타임이 같이 사는 법"
series: azure-functions-deep-dive
episode: 2
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

# Azure Functions Deep Dive (2/6): Worker 프로세스 — 한 호스트에서 여러 언어 런타임이 같이 사는 법

호스트 부팅 경계를 이해하고 나면 곧바로 다음 질문이 생깁니다. .NET으로 작성된 Functions Host가 언어 선택 정보를 어떻게 실제 Node.js, Python, Java, PowerShell 프로세스로 바꾸는지, 그리고 그 순간부터 무엇이 운영체제 수준의 프로세스 관리 문제가 되는지입니다.

이 질문은 단순한 내부 구현 호기심으로 끝나지 않습니다. 워커가 죽었을 때 누가 그것을 감지하는지, stdout에 찍힌 로그가 왜 Application Insights의 `traces`로 들어가는지, 한 인스턴스 안에서 워커 수를 늘리는 설정이 정확히 무엇을 의미하는지까지 전부 이 경로 위에서 설명됩니다.

이번 글 역시 기준은 [`Azure/azure-functions-host @ 5e59423`](https://github.com/Azure/azure-functions-host/tree/5e59423ba45491041d18224c3e72c168a4a5b7f7)입니다. 1화에서 `InitializeAsync` 안쪽의 “worker channel preparation” 박스만 남겨 두었는데, 이번에는 그 박스를 끝까지 열어 실제 `Process.Start()` 호출 직전까지 따라갑니다.

이 글은 Azure Functions Deep Dive 시리즈의 두 번째 글입니다.

이제 호스트가 언어 런타임을 실제 워커 프로세스로 구체화하는 경로를 소스 기준으로 고정하겠습니다.

![Azure Functions Deep Dive 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/azure-functions-deep-dive/02/02-01-one-level-up-workerconfigfactory.ko.png)
*Azure Functions Deep Dive 2장 흐름 개요*
> Worker 프로세스 — 한 호스트에서 여러 언어 런타임이 같이 사는 법의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 먼저 던지는 질문

- 워커 프로세스 모델은 언어마다 어떻게 다르며, 운영적으로 무엇을 뜻할까요?
- 워커는 상태가 없다고 봐야 할까요, 아니면 인프로세스 상태를 어느 정도 믿어도 될까요?
- 워커가 OOM이나 hang에 빠지면 호스트는 어떤 신호로 그것을 감지할까요?

## 왜 이 글이 중요한가

Azure Functions의 out-of-proc 모델은 “호스트와 사용자 코드가 분리된다”는 한 문장으로 자주 설명되지만, 운영에서는 그 한 문장으로 충분하지 않습니다. 실제로는 언어별 워커 패키지, 워커 설정 수집, OS 프로세스 시작, stdout/stderr 연결, 프로세스 종료 감지 같은 단계가 따로 있고, 각 단계가 서로 다른 장애 모드를 가집니다.

예를 들어 Python 워커가 죽었는데 호스트는 멀쩡할 수 있습니다. 반대로 호스트는 계속 살아 있는데 워커 stdout에서만 오류가 쏟아질 수도 있습니다. 이 둘을 같은 장애로 취급하면 재시작 전략, 로그 수집 전략, 메모리 경보 전략이 모두 잘못 설계됩니다. 워커를 별도 자식 프로세스로 본다는 감각이 반드시 필요합니다.

또한 `FUNCTIONS_WORKER_PROCESS_COUNT`와 동적 워커 동시성은 이름이 비슷해 자주 혼동됩니다. 하나는 인스턴스당 워커 수를 정적으로 늘리는 설정이고, 다른 하나는 지연 시간 히스토리를 보고 런타임이 워커를 더 추가하는 메커니즘입니다. 이 차이를 모르면 “왜 워커가 예상보다 많이 떴지?” 혹은 “왜 늘어나지 않지?” 같은 질문에 제대로 답할 수 없습니다.

## 핵심 관점

Functions Host는 언어별 시작 방법을 코드에 직접 하드코딩하지 않습니다. 대신 각 언어 워커 패키지가 제공하는 `worker.config.json`을 읽고, 그 설정을 합쳐 `RpcWorkerConfig` 카탈로그를 만든 뒤, 필요할 때 그 설명에 따라 실제 OS 프로세스를 시작합니다. 즉 새 언어 지원은 호스트 본체 수정이라기보다 워커 패키지 추가에 더 가깝습니다.

이 관점을 잡으면 워커 시작도 하나의 큰 블랙박스가 아니라 설정 수집, 프로세스 생성, 로그 연결, 종료 감지, 채널 준비라는 별도 단계의 조합으로 보입니다. 이 구분이 있어야 설정 오류와 프로세스 장애, 채널 준비 지연을 한 덩어리로 섞지 않게 됩니다.

> 이번 글의 핵심은 “호스트가 언어를 실행한다”는 추상적인 설명이 아니라, `worker.config.json` 설명을 모아 실제 `Process.Start()`까지 내려가는 구체적인 경로를 잡는 데 있습니다.

## 핵심 개념

### 출발점은 `worker.config.json`입니다

호스트는 언어별 워커 실행 로직을 직접 들고 있지 않습니다. 워커 패키지가 제공하는 `worker.config.json`이 어떤 실행 파일을 띄울지, 어떤 엔트리 포인트를 줄지, 어떤 확장자를 이 워커가 맡을지 알려 줍니다.

Node.js 워커의 설정은 아래와 같습니다.

```json
{
  "description": {
    "language": "node",
    "extensions": [".js", ".mjs", ".cjs"],
    "defaultExecutablePath": "node",
    "defaultWorkerPath": "dist/src/nodejsWorker.js"
  }
}
```

이 파일은 세 가지를 알려 줍니다. 어떤 실행 파일을 띄울지, 어떤 워커 스크립트나 JAR를 넘길지, 어떤 소스 파일 확장자가 이 워커의 책임 범위인지입니다. 새 언어 지원이 호스트 패치보다 워커 패키지 배치에 가까운 이유가 바로 여기 있습니다.

### 한 단계 위에서는 `WorkerConfigurationResolver`가 설정을 모읍니다

호스트 부팅 시 중심에 있는 객체는 `WorkerConfigurationResolver`입니다. 이 객체가 혼자 모든 파일을 뒤지는 것은 아닙니다. 여러 provider가 `Dictionary<string, RpcWorkerConfig>`를 채우고, `WorkerConfigurationResolver.GetWorkerConfigs()`가 우선순위에 따라 결과를 합칩니다.

`5e59423` 기준으로는 `DefaultWorkerConfigurationProvider`, `DynamicWorkerConfigurationProvider`, `ExplicitWorkerConfigurationProvider`가 있고, 공통 기반은 `WorkerConfigurationProviderBase`입니다. 기본 provider는 내장 `workers/` 디렉터리를 스캔하고, 동적 provider는 probing path에서 버전별 워커를 찾고, explicit provider는 특정 워커 디렉터리에 대한 앱 설정 override를 적용합니다.

이 구조 덕분에 호스트는 언어별 런처 코드를 복제하지 않습니다. **설정 설명을 읽어 공통 모델로 올리고, 그 공통 모델에서 프로세스 생성으로 내려가는** 방식입니다.

### 실제 OS 프로세스 생성은 `RpcWorkerProcess`와 `WorkerProcess`가 맡습니다

워커 설정이 모이면 다음 단계는 실제 자식 프로세스를 띄우는 것입니다. 여기서 중심 클래스는 `RpcWorkerProcess`이지만, 이 클래스가 직접 곧바로 `Process`를 new 하는 것은 아닙니다. `CreateWorkerProcess()`가 `RpcWorkerContext`를 만들고, 주입된 `_processFactory.CreateWorkerProcess(workerContext)`로 위임합니다.

실제 시작은 `WorkerProcess.StartProcessAsync()`에서 일어납니다. 여기서 세 가지가 함께 일어납니다. 첫째, `System.Diagnostics.Process`로 OS 프로세스를 띄웁니다. 둘째, stdout/stderr를 가로채 호스트 로깅 파이프라인에 연결합니다. 셋째, 프로세스 종료 시 `Exited` 이벤트로 알림을 받을 콜백을 등록합니다.

이 stdout/stderr 연결은 운영적으로 특히 중요합니다. 워커가 표준 출력에 쓴 줄 상당수가 결국 호스트 로깅 시스템을 거쳐 Application Insights `traces`로 들어가기 때문입니다. “왜 `console.log`가 클라우드 로그에 보이지?”라는 질문의 답이 바로 여기 있습니다.

### 워커 프로세스가 떴다고 곧바로 준비 완료는 아닙니다

OS 프로세스가 살아 있다는 것과 워커가 호스트와 통신할 준비가 되었다는 것은 다른 단계입니다. 프로세스 부팅과 gRPC 핸드셰이크는 분리되어 있습니다.

![Worker process and channel readiness](https://yeongseon-books.github.io/book-public-assets/assets/azure-functions-deep-dive/02/02-02-worker-lifecycle-within-a-single-instanc.ko.png)

*Worker process and channel readiness*

여기서 보이는 `GrpcWorkerChannel`은 호스트 쪽에서 워커 하나를 대표하는 핸들입니다. 워커가 죽으면 채널도 함께 폐기되고, 호스트는 새 워커와 새 채널을 다시 만듭니다. 따라서 “워커 준비 완료”는 단순 프로세스 생성이 아니라 **프로세스 + 채널**이 모두 성립한 상태라고 보는 편이 정확합니다.

### `FUNCTIONS_WORKER_PROCESS_COUNT`는 인스턴스당 정적 워커 수 설정입니다

기본값은 1입니다. 즉 Function App 인스턴스 하나에 워커 하나가 뜹니다. 하지만 `FUNCTIONS_WORKER_PROCESS_COUNT=N`을 주면 같은 인스턴스 안에 워커 프로세스 N개가 나란히 뜹니다.

![Multiple worker layout within one instance](https://yeongseon-books.github.io/book-public-assets/assets/azure-functions-deep-dive/02/02-03-functions-worker-process-count-multiple.ko.png)

*Multiple worker layout within one instance*

이 설정은 특히 Node.js나 Python처럼 이벤트 루프 기반 단일 스레드 언어에서 의미가 큽니다. 워커 하나가 CPU 작업에 막혀 있으면 다른 호출이 그 안에 끼어들기 어렵기 때문입니다. 반대로 Java나 .NET처럼 멀티스레드 런타임에서는 추가 워커가 항상 필요한 것은 아니지만, 메모리 격리나 별도 GC를 원할 때 사용할 수 있습니다.

동시에 꼭 구분해야 할 것이 있습니다. `FUNCTIONS_WORKER_PROCESS_COUNT` / `WorkerProcessCountOptions`는 **정적 워커 수**를 의미하고, `WorkerConcurrencyOptions` / `WorkerConcurrencyManager`는 **지연 시간 히스토리를 보고 워커를 더 추가할지 판단하는 동적 동시성**입니다. 이름은 비슷하지만 다른 축입니다.

### 워커가 죽으면 호스트는 자식 프로세스 장애로 취급하고 회복합니다

워커는 사용자 코드를 실행하므로 언제든 죽을 수 있습니다. 무한 루프, 메모리 폭주, 처리되지 않은 예외, OOM이 모두 가능합니다. 호스트의 회복 전략은 자식 프로세스 장애 복구 모델에 가깝습니다.

![Worker failure detection and recovery flow](https://yeongseon-books.github.io/book-public-assets/assets/azure-functions-deep-dive/02/02-04-what-happens-when-a-worker-dies.ko.png)

*Worker failure detection and recovery flow*

순서는 이렇습니다. `WorkerProcess`의 `Exited` 이벤트로 죽음을 감지하고, 대응하는 `GrpcWorkerChannel`을 폐기하고, 새 워커 프로세스를 띄우고, 진행 중이던 `InvocationRequest`는 실패로 마킹합니다. 이 설계 덕분에 워커가 가끔 죽어도 호스트 전체는 계속 건강해 보일 수 있습니다. 즉 실패 단위는 호스트 프로세스가 아니라 **자식 워커 프로세스**입니다.

### 워커 채널 생명주기를 상태 기계로 보면 로그 해석이 쉬워집니다

운영 중 로그를 보면 "채널 준비 중", "워커 연결됨", "채널 폐기" 같은 문장이 섞여 나오는데, 이를 상태 기계로 보면 훨씬 명확합니다. `GrpcWorkerChannel` 관점에서 최소 상태를 정리하면 다음과 같습니다.

```text
Created
  -> StartingProcess
  -> WaitingForStartStream
  -> WaitingForWorkerInitResponse
  -> LoadingFunctions
  -> Ready
  -> Draining (shutdown/restart)
  -> Closed
```

이렇게 정리해 두면 장애 분석 시 문장이 바뀝니다. "워커가 죽었다"가 아니라 "Ready 진입 전 StartStream 대기에서 timeout"처럼 단계 중심으로 기술할 수 있습니다. 단계 중심 기술은 재현 실험 설계를 단순하게 만들어 줍니다.

### 워커 시작 명령줄이 어떻게 조립되는지 이해해야 환경 이슈를 잡습니다

`worker.config.json`을 읽는다고 끝이 아닙니다. 실제 런타임에서는 호스트가 실행 파일 경로, 워커 엔트리 파일, 환경변수, 추가 인자를 조합해 최종 프로세스 시작 명령을 만듭니다. 여기서 경로 공백, 잘못된 executable path, 누락된 런타임 설치가 바로 실패로 이어집니다.

아래는 Node 워커 기준의 단순화된 시작 예시입니다.

```text
Executable: node
Arguments: dist/src/nodejsWorker.js --host 127.0.0.1 --port 58432 --workerId 7f0d...
Env:
  FUNCTIONS_WORKER_RUNTIME=node
  FUNCTIONS_WORKER_DIRECTORY=/azure-functions-host/workers/node
  FUNCTIONS_WORKER_PROCESS_COUNT=2
```

이 출력에서 `Executable`과 `Arguments`가 맞아도 워커가 죽는 경우가 있습니다. 대표적으로 worker 디렉터리 권한, 런타임 버전 불일치, 시작 직후 native dependency 로딩 실패입니다. 그래서 워커 기동 문제는 반드시 "설정 파일 확인" 다음에 "최종 시작 명령 확인" 단계가 필요합니다.

### 동적 동시성 매니저는 지연 시간 히스토리를 기준으로 추가 워커를 판단합니다

`WorkerConcurrencyManager`는 단순히 queue length만 보고 판단하지 않습니다. `WorkerStatus`의 `LatencyHistory`와 스로틀 신호를 함께 읽어 현재 워커가 과포화인지 추정하고, 임계치를 넘으면 같은 인스턴스 내 워커 수를 증가시킵니다. 즉 이 로직은 스케일 아웃 컨트롤러와 달리 인스턴스 외부 상태를 직접 조정하지 않습니다.

실무에서 중요한 포인트는 "워커 수 증가 = 항상 처리량 증가"가 아니라는 점입니다. Python처럼 GIL 영향을 받는 워커는 I/O 중심 부하에서 이득이 크지만, CPU 바운드 함수는 워커를 늘려도 메모리 압박만 늘어날 수 있습니다. 따라서 워커 수 실험은 처리량과 함께 RSS, GC pause, OOM 빈도까지 같이 봐야 합니다.

### 성능 프로파일링 출력 예시로 튜닝 기준을 만들 수 있습니다

워커 경로 튜닝은 감으로 하기 어렵습니다. 아래처럼 지표를 수집해 비교 기준을 고정하는 것이 좋습니다.

```text
[WorkerProfile]
Instance=funcapp-7d9c
WorkerRuntime=python
WorkerCount=1
P50_InvocationLatencyMs=84
P95_InvocationLatencyMs=412
ProcessStartMs=920
ChannelReadyMs=1310
StdoutLinesPerMin=184
WorkerRestartsPerHour=3
```

`ProcessStartMs`가 높으면 런타임 초기화 부담, `ChannelReadyMs`만 높으면 gRPC handshake 또는 함수 로드 병목, `WorkerRestartsPerHour`가 높으면 메모리 누수나 예외 폭주를 의심할 수 있습니다. 이처럼 지표를 단계에 대응시키면 튜닝 우선순위가 명확해집니다.

### 워커 장애 시나리오를 사전에 주입해 회복 경로를 검증해야 합니다

문서만 읽고 회복을 신뢰하면 운영에서 놀라게 됩니다. 최소 세 가지 실패 주입을 권장합니다.

1) 워커 프로세스 강제 종료(SIGKILL): `Exited` 감지와 채널 재생성 여부 확인
2) 워커 hang(무한 루프): timeout, throttle, 재시도 동작 확인
3) 메모리 폭주(OOM): 재시작 후 in-flight invocation 실패 표면 확인

검증 포인트는 "재시작됐는가" 하나가 아닙니다. 실패한 invocation이 어느 오류 코드로 기록되는지, 재시도 정책과 poison 처리로 어떻게 연결되는지까지 확인해야 합니다. 그래야 애플리케이션 팀이 플랫폼 신호를 오해하지 않습니다.

### 언어별 워커 운영 차이를 표로 고정하면 온콜 대응이 빨라집니다

| 런타임 | 초기 기동 비용 | 메모리 특성 | 흔한 장애 패턴 |
|---|---|---|---|
| Node.js | 낮음~중간 | 상대적으로 작음 | 이벤트 루프 블로킹, native 모듈 오류 |
| Python | 중간 | 라이브러리 의존 시 급증 | OOM, import 지연, GIL로 인한 병렬성 착시 |
| Java | 높음 | 큼 | JVM warm-up 지연, GC pause |
| PowerShell | 중간~높음 | 중간 | 모듈 로드 지연, 시작 시간 편차 |

이 표의 목적은 우열 비교가 아닙니다. 같은 설정값이라도 런타임별 체감이 다르다는 사실을 운영 언어로 고정하는 것입니다. 워커 프로세스 수와 timeout, 메모리 한계값은 런타임별로 분리해 관리해야 합니다.

추가로, 같은 언어라도 워커 버전이 바뀌면 기동 시간과 로그 형식이 달라질 수 있습니다. 따라서 운영에서 "언어 런타임"만 기록하지 말고 워커 패키지 버전과 이미지 태그까지 함께 남겨야 합니다. 장애 회고에서 버전 축이 빠지면 재현 정확도가 크게 떨어집니다.

## 흔히 헷갈리는 지점

- **호스트가 언어별 실행 로직을 전부 하드코딩하는 것은 아닙니다.** 실제 시작 정보의 출발점은 각 워커 패키지의 `worker.config.json`입니다.
- **OS 프로세스가 떠 있는 것과 워커가 준비 완료인 것은 다릅니다.** 프로세스 생성 뒤에 채널 준비와 핸드셰이크가 따로 이어집니다.
- **`FUNCTIONS_WORKER_PROCESS_COUNT`와 동적 워커 동시성은 같은 기능이 아닙니다.** 전자는 정적 프로세스 수, 후자는 런타임이 추가 워커를 늘릴지 판단하는 메커니즘입니다.
- **워커 로그는 곧바로 사라지는 표준 출력 텍스트가 아닙니다.** stdout/stderr가 호스트 로깅 파이프라인에 연결됩니다.
- **워커 장애가 곧 호스트 장애는 아닙니다.** 호스트는 워커를 자식 프로세스로 보고 죽음을 감지해 재생성합니다.

## 운영 체크리스트

- [ ] 선택한 워커 언어와 실행 모델의 이유를 ADR에 남겼습니다.
- [ ] 인프로세스 상태에 의존하는 코드를 점검하고 외부 상태 저장소로 분리했습니다.
- [ ] 워커별 메모리와 CPU 경보를 별도로 구성했습니다.
- [ ] 워커 hang 또는 종료 시 자동 회복 동작을 실험으로 확인했습니다.
- [ ] 워커 로그와 비즈니스 로그를 구분해서 읽는 방법을 운영 문서에 정리했습니다.

## 정리

이번 글에서 가장 중요한 사실은 Azure Functions 워커 시작이 추상적 “런타임 선택”이 아니라는 점입니다. 각 언어 워커 패키지가 제공하는 `worker.config.json`에서 출발해, 호스트가 설정을 모아 `RpcWorkerConfig`를 만들고, 그 설명을 바탕으로 실제 OS 프로세스를 띄웁니다. 이 과정을 보면 언어 지원이 왜 호스트 본체 변경보다 워커 패키지 문제에 가까운지 이해됩니다.

또한 프로세스 생성, stdout/stderr 연결, 종료 감지, 채널 준비가 각각 다른 단계라는 점도 중요합니다. 운영에서 보는 “워커가 이상하다”는 증상은 이 네 단계 중 어디에서 문제가 났는지에 따라 완전히 다른 의미를 가집니다. 따라서 워커 장애 분석은 단순 재시작 여부보다 어느 단계가 실패했는지를 먼저 보는 것이 맞습니다.

다음 글에서는 이제 실제 통신 경로로 들어갑니다. 워커 프로세스가 떠 있는 것만으로는 아무 일도 일어나지 않기 때문에, 호스트와 워커가 단 하나의 양방향 gRPC 스트림 위에서 어떤 메시지를 주고받는지, 그리고 그 스트림이 호스트 내부에서 어떤 채널 구조로 다뤄지는지를 보겠습니다.

## 처음 질문으로 돌아가기

- **워커 프로세스 모델은 언어마다 어떻게 다르며, 운영적으로 무엇을 뜻할까요?**
  - 언어 차이는 호스트 코드에 하드코딩된 분기보다 각 워커 패키지의 `worker.config.json`에 먼저 표현됩니다. 운영적으로는 Node, Python, Java, PowerShell이 모두 별도 자식 프로세스로 뜨고, 기동 시간·메모리 사용·장애 패턴이 다르므로 같은 워커 수나 timeout을 공통값으로 두면 실제 체감이 달라집니다.
- **워커는 상태가 없다고 봐야 할까요, 아니면 인프로세스 상태를 어느 정도 믿어도 될까요?**
  - 워커는 호스트 밖의 자식 프로세스이므로 재시작될 수 있는 실행 단위로 보는 편이 맞습니다. 같은 프로세스 안에서 메모리 캐시나 모듈 상태가 잠시 유지될 수는 있지만, `Exited` 감지 후 새 워커와 새 채널이 만들어질 수 있으니 운영 기준의 상태는 외부 저장소에 두어야 안전합니다.
- **워커가 OOM이나 hang에 빠지면 호스트는 어떤 신호로 그것을 감지할까요?**
  - 워커 종료는 `WorkerProcess`의 `Exited` 이벤트로 직접 감지되고, 해당 `GrpcWorkerChannel`은 폐기된 뒤 새 워커 생성 경로로 넘어갑니다. hang처럼 즉시 죽지 않는 경우에는 채널 준비 지연, 상태 응답, 지연 시간 히스토리 같은 신호가 먼저 드러나므로 프로세스 생존과 채널 준비 완료를 따로 봐야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Azure Functions Deep Dive (1/6): 호스트 부팅 — `WebJobsScriptHostService`부터 따라가기](./01-host-bootstrap.md)
- **Azure Functions Deep Dive (2/6): Worker 프로세스 — 한 호스트에서 여러 언어 런타임이 같이 사는 법 (현재 글)**
- Azure Functions Deep Dive (3/6): gRPC 이벤트 스트림 — 호스트와 워커는 무엇을 주고받는가 (예정)
- Azure Functions Deep Dive (4/6): Dispatcher와 Invocation — 함수 호출이 워커에 도달하기까지 (예정)
- Azure Functions Deep Dive (5/6): 스케일링 내부 동작 — Scale Controller, ScaleMonitor, 그리고 플랜별 차이 (예정)
- Azure Functions Deep Dive (6/6): 콜드 스타트와 Placeholder Mode — 새 인스턴스가 만들어질 때 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [`Azure/azure-functions-host @ 5e59423`](https://github.com/Azure/azure-functions-host/tree/5e59423ba45491041d18224c3e72c168a4a5b7f7)
- [`RpcWorkerProcess.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423/src/WebJobs.Script.Grpc/Rpc/RpcWorkerProcess.cs)
- [`WorkerProcess.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423/src/WebJobs.Script.Grpc/ProcessManagement/WorkerProcess.cs)
- [`GrpcWorkerChannel.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423/src/WebJobs.Script.Grpc/Channel/GrpcWorkerChannel.cs)
- [`WorkerProcessCountOptions.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423/src/WebJobs.Script/Workers/WorkerProcessCountOptions.cs)
- [`WorkerConcurrencyOptions.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423/src/WebJobs.Script/Config/WorkerConcurrencyOptions.cs)
- [`WorkerConcurrencyManager.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423/src/WebJobs.Script.Grpc/WorkerConcurrencyManager.cs)
- [PR #4210 — `FUNCTIONS_WORKER_PROCESS_COUNT`](https://github.com/Azure/azure-functions-host/pull/4210)
- [`Azure/azure-functions-nodejs-worker` `worker.config.json`](https://github.com/Azure/azure-functions-nodejs-worker/blob/v3.x/worker.config.json)
- [`Azure/azure-functions-java-worker` `worker.config.json`](https://github.com/Azure/azure-functions-java-worker/blob/dev/worker.config.json)
- [`Azure/azure-functions-python-worker`](https://github.com/Azure/azure-functions-python-worker)

### 관련 시리즈
- [Azure Functions 101 — Host와 Worker](../../azure-functions-101/ko/03-host-and-worker.md)
- [Azure Functions 101 — 스케일링과 콜드 스타트](../../azure-functions-101/ko/06-scaling-and-cold-start.md)
- [Azure App Service Deep Dive — App Service 플랫폼 아키텍처](../../azure-app-service-deep-dive/ko/01-platform-architecture.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-functions-deep-dive/ko/02-worker-process)

Tags: Azure Functions, Serverless, Distributed Systems, gRPC
