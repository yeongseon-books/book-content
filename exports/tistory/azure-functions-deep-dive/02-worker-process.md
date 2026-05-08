
# Worker 프로세스 — 한 호스트에서 여러 언어 런타임이 같이 사는 법

> Azure Functions Deep Dive 시리즈 (2/6)

## Source Version

이 글의 모든 코드 인용은 [`Azure/azure-functions-host @ 5e59423`](https://github.com/Azure/azure-functions-host/tree/5e59423ba45491041d18224c3e72c168a4a5b7f7) 기준입니다.

1화 끝에서 “`InitializeAsync` 안의 Worker 채널 준비 박스에 무슨 일이 일어나는가”라는 질문을 남겼습니다. 이번 화의 주제입니다. .NET으로 작성된 Functions Host가 Node.js, Python, Java, PowerShell Worker 프로세스를 어떻게 띄우고 어떻게 연결하는가. **OS의 `Process.Start`가 호출되기 직전까지** 따라갑니다.

기준 커밋은 1화와 같은 `5e59423`입니다.

---

<!-- a-grade-intro:begin -->
## 핵심 질문

Worker 프로세스 구조를 이해하면 어떤 언어 런타임 사고를 예방할 수 있을까요?

이 글은 그 질문에 답하기 위해 Worker 프로세스의 핵심 결정과 운영 함정을 살펴봅니다.

<!-- a-grade-intro:end -->

## 이 글에서 답할 질문

- Worker 프로세스는 언어별로 어떻게 다르고, 그 차이는 운영에 어떤 의미를 갖는가?
- Worker는 stateless인가? in-process state는 어디까지 안전한가?
- Worker가 OOM이나 hang에 빠질 때 호스트는 어떤 신호로 감지하는가?
- Worker pool 크기와 함수의 실행 모델(in-process, out-of-process)은 어떻게 만나는가?
- Worker 로그와 함수 로그는 어디에서 분리되어 보이는가?

## 출발점 — `worker.config.json`

여러 언어 런타임을 어떻게 같이 띄우는지의 답은 단순합니다. Host는 “어떤 언어를 어떻게 띄울지”를 직접 하드코딩하지 않습니다. 대신 **각 언어 워커 패키지에 들어 있는 `worker.config.json`**을 읽고 그 설명을 따릅니다. 새 언어를 붙이는 일은 Host 코드를 뜯어고치는 작업이 아니라, 해당 언어 워커 패키지를 추가하는 작업에 가깝습니다.

대표적으로 Node.js 워커의 설정은 다음과 같이 생겼습니다.

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

> 코드 위치: [Node.js worker repo의 `worker.config.json`](https://github.com/Azure/azure-functions-nodejs-worker/blob/v3.x/worker.config.json)

Java 워커의 설정도 비슷한 구조로 별도 파일에 들어 있습니다.

> 코드 위치: [Java worker repo의 `worker.config.json`](https://github.com/Azure/azure-functions-java-worker/blob/dev/worker.config.json)

이 파일들이 Host에게 알려주는 정보는 셋입니다.

- **어떤 실행 파일로 띄울지** (`node`, `java -jar ...`, `python` 등)
- **어떤 진입점 스크립트를 줄지** (`nodejsWorker.js`, `azure-functions-java-worker.jar` 등)
- **어떤 파일 확장자를 다루는지** (`.js`, `.py`, `.java`, ...)

---

## 한 단계 위 — `WorkerConfigurationResolver`

Host가 부팅할 때 모든 언어의 `worker.config.json`을 모아 통합 카탈로그를 만드는 중심 객체는 `WorkerConfigurationResolver`입니다. 이 객체가 직접 디렉터리를 뒤지는 게 아니라, 여러 provider가 `Dictionary<string, RpcWorkerConfig>`를 채우고 `WorkerConfigurationResolver.GetWorkerConfigs()`가 그것들을 우선순위 순서로 합칩니다.

`5e59423` 기준으로 provider는 세 개입니다. `DefaultWorkerConfigurationProvider`는 호스트의 기본 `workers/` 디렉터리를 스캔하고, `DynamicWorkerConfigurationProvider`는 probing path와 버전 호환성을 반영해 동적으로 고르며, `ExplicitWorkerConfigurationProvider`는 app setting으로 지정한 worker directory override를 적용합니다. 셋 다 `WorkerConfigurationProviderBase`를 공통 베이스로 사용합니다.

![워커 설정 provider를 합치는 해석 구조](https://yeongseon-books.github.io/book-public-assets/assets/azure-functions-deep-dive/02/02-01-one-level-up-workerconfigfactory.ko.png)

*워커 설정 provider를 합치는 해석 구조*
언어별 워커가 플러그인처럼 붙는 이유가 이 그림에 있습니다. **Host는 워커 구현을 직접 품지 않고, 워커 설정 파일이 설명하는 실행 규칙만 읽습니다.**

---

## Worker 프로세스 띄우기 — `RpcWorkerProcess`

설정이 모이면 다음 단계는 실제 OS 프로세스를 띄우는 일입니다. 이 책임을 지는 클래스가 `RpcWorkerProcess`입니다. 다만 `RpcWorkerProcess`가 직접 프로세스를 생성하는 방식은 아닙니다. `CreateWorkerProcess()`는 `RpcWorkerContext`를 만든 뒤, 주입받은 `_processFactory.CreateWorkerProcess(workerContext)`에 위임합니다.

> 코드 위치: [`RpcWorkerProcess.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423/src/WebJobs.Script.Grpc/Rpc/RpcWorkerProcess.cs)

실제 시작은 추상 베이스 클래스 `WorkerProcess`의 `StartProcessAsync()`에서 일어납니다. 여기서 다음 셋이 수행됩니다.

1. `System.Diagnostics.Process`로 OS 프로세스를 띄움
2. **stdout/stderr를 가로채서 Host의 로그 파이프라인에 연결**
3. 프로세스가 죽으면 콜백 등록 (`Exited` 이벤트)

> 코드 위치: [`WorkerProcess.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423/src/WebJobs.Script.Grpc/ProcessManagement/WorkerProcess.cs)

stdout/stderr 와이어링이 운영 관점에서 중요합니다. **워커가 표준 출력으로 쓴 모든 글이 Host의 로깅 시스템을 통해 Application Insights로 흘러갑니다.** 입문편 7화에서 본 traces 테이블의 상당수가 사실은 워커가 stdout으로 쓴 줄들입니다. `console.log` 한 줄이 어떻게 클라우드 로그에 들어가는지의 답이 여기에 있습니다.

---

## 한 인스턴스 안의 Worker 라이프사이클

OS 프로세스가 떠 있다고 해서 Worker가 “준비 완료”인 건 아닙니다. 프로세스 부팅과 gRPC 핸드셰이크는 별개입니다. 다음 시퀀스가 한 인스턴스 안에서 한 Worker가 “준비 완료” 상태에 도달하는 전체 과정입니다.

![워커 프로세스와 채널 준비 단계](https://yeongseon-books.github.io/book-public-assets/assets/azure-functions-deep-dive/02/02-02-worker-lifecycle-within-a-single-instanc.ko.png)

*워커 프로세스와 채널 준비 단계*
여기서 등장한 `GrpcWorkerChannel`은 “하나의 워커 프로세스에 대응하는 호스트 측 핸들”입니다. 워커가 죽으면 이 채널도 정리되고, 호스트는 새 워커를 띄우면서 새 채널을 만듭니다.

> 코드 위치: [`GrpcWorkerChannel.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423/src/WebJobs.Script.Grpc/Channel/GrpcWorkerChannel.cs)

---

## `FUNCTIONS_WORKER_PROCESS_COUNT` — 한 인스턴스에 워커 여러 개

기본값은 1입니다. 즉 한 Function App 인스턴스 안에 Worker는 한 개입니다. 그런데 환경변수 `FUNCTIONS_WORKER_PROCESS_COUNT`를 N으로 설정하면, 같은 인스턴스 안에 N개의 워커 프로세스가 뜹니다.

이게 의미가 있는 경우는 다음 둘입니다.

- **Node.js / Python처럼 단일 스레드 이벤트 루프 기반 언어** — 한 워커가 CPU 작업으로 블록되면 다른 호출이 못 들어옵니다. 워커를 여럿 띄우면 OS 레벨 멀티프로세스로 병렬화가 됩니다.
- **Java / .NET 등 멀티스레드 언어** — 굳이 워커를 여럿 띄울 필요는 적지만, 메모리 격리나 GC 분리를 원할 때 쓸 수 있습니다.

이 지점에서 두 개념을 분리해서 봐야 합니다.

- **`FUNCTIONS_WORKER_PROCESS_COUNT` / `WorkerProcessCountOptions`**: 한 인스턴스 안에 기본으로 몇 개의 워커 프로세스를 띄울지 정하는 **정적 개수 설정**입니다.
- **`WorkerConcurrencyOptions` / `WorkerConcurrencyManager`**: 런타임이 지연 시간 이력을 보고 워커를 더 붙일지 판단하는 **동적 동시성 제어**입니다.

즉 `FUNCTIONS_WORKER_PROCESS_COUNT=4`는 시작 시점에 워커 4개를 준비하는 설정이고, `WorkerConcurrencyOptions`는 실행 중 상태를 보고 추가 워커를 붙일지 감시하는 쪽입니다. 동적 동시성은 Node.js, Python, PowerShell 같은 일부 런타임에서만 동작하고, `FUNCTIONS_WORKER_PROCESS_COUNT`가 설정돼 있으면 비활성화됩니다.

![한 인스턴스의 다중 워커 배치 구조](https://yeongseon-books.github.io/book-public-assets/assets/azure-functions-deep-dive/02/02-03-functions-worker-process-count-multiple.ko.png)

*한 인스턴스의 다중 워커 배치 구조*
---

## 워커가 죽으면 어떻게 되는가

워커 프로세스는 임의의 사용자 코드를 실행합니다. 즉 죽을 가능성이 늘 있습니다. 무한 루프, 메모리 폭주, 처리되지 않은 예외, 알 수 없는 OOM. Host의 회복 전략은 다음과 같습니다.

1. `WorkerProcess`의 `Exited` 이벤트로 사망 감지
2. 해당 워커 채널 정리 (`GrpcWorkerChannel.Dispose`)
3. 새 워커 프로세스 띄우기
4. 진행 중이던 InvocationRequest는 실패로 처리

운영 관점에서 “함수가 가끔 한 번씩 실패하더라도 호스트 자체는 멀쩡하게 살아 있는” 이유가 이 격리 덕분입니다. Host는 자기 프로세스가 아닌 **자식 프로세스**의 죽음을 감지하고 회복하는 모델로 설계돼 있습니다.

![워커 종료 뒤 감지와 복구 흐름](https://yeongseon-books.github.io/book-public-assets/assets/azure-functions-deep-dive/02/02-04-what-happens-when-a-worker-dies.ko.png)

*워커 종료 뒤 감지와 복구 흐름*
---

## 2화 정리

이번 화의 그림을 한 문단으로 줄이면 다음과 같습니다.

> 각 언어 워커 패키지가 디스크에 `worker.config.json`을 둡니다. Host는 부팅할 때 `WorkerConfigurationResolver`와 provider들로 이 설정을 모아 `RpcWorkerConfig` 카탈로그를 만듭니다. 워커를 띄울 때가 되면 `RpcWorkerProcess.CreateWorkerProcess()`가 `RpcWorkerContext`를 만든 뒤 `_processFactory.CreateWorkerProcess(...)`에 위임하고, `WorkerProcess.StartProcessAsync()`가 최종적으로 OS의 `Process.Start()`를 호출합니다. stdout/stderr는 호스트의 로그 파이프라인으로 묶여 들어갑니다.

여기까지 오면 워커는 **떠 있고, 호스트와 연결돼 있고, 함수 메타데이터를 받을 준비**가 됐습니다. 이 시점에서 기억할 모델은 분명합니다. 워커 시작은 한 번의 "실행"이 아니라, 설정 수집·프로세스 생성·로그 파이프 연결·채널 준비가 차례로 이어지는 다단계 절차입니다.

---

## 시리즈 안에서의 위치

이 글은 Azure Functions Deep Dive 시리즈 2화입니다. 1화가 호스트 부팅의 외곽선을 그렸다면, 이번 화는 그 안에서 언어 워커가 어떤 설정 카탈로그를 거쳐 실제 OS 프로세스로 올라오는지에 초점을 맞춥니다.

---

## Call Path Summary

- `WorkerConfigurationResolver.GetWorkerConfigs()` → `DynamicWorkerConfigurationProvider` / `DefaultWorkerConfigurationProvider` / `ExplicitWorkerConfigurationProvider` → `RpcWorkerConfig`
- `GrpcWorkerChannel.StartWorkerProcessAsync()` → `IWorkerProcess.StartProcessAsync()` → `RpcWorkerProcess.CreateWorkerProcess()` → `_processFactory.CreateWorkerProcess(workerContext)` → `Process.Start()`

---

## 시니어 엔지니어는 이렇게 생각합니다

- **Out-of-proc 워커가 격리의 핵심** — 한 언어 사고가 호스트로 전파되지 않습니다.
- **워커는 단명일 수 있다는 전제** — 재시작·이동에 내성 있는 코드를 씁니다.
- **동시성 설정이 워커당 부하를 결정** — max concurrent 값이 메모리·CPU 사고의 원인이 됩니다.
- **OOM·CPU 한계를 메트릭으로 본다** — 워커 크래시의 가장 흔한 원인입니다.
- **로컬 캐시 의존을 줄인다** — 워커 재시작 시 일관성 문제로 이어집니다.

## 운영 체크리스트

- [ ] Worker 언어/모델 선택의 근거(in-proc vs isolated)를 ADR로 남겼다
- [ ] in-process state를 가정한 코드를 검토하고 외부화했다
- [ ] Worker 프로세스 단위 메모리/CPU 알림을 분리해서 운영한다
- [ ] Worker hang 발생 시 자동 회복 동작을 검증했다
- [ ] Worker 로그와 비즈니스 로그를 별도 카테고리로 분리했다

## 시리즈 목차

- [호스트 부팅 — `WebJobsScriptHostService`부터 따라가기](./01-host-bootstrap.md)
- **Worker 프로세스 — 한 호스트에서 여러 언어 런타임이 같이 사는 법 (현재 글)**
- gRPC 이벤트 스트림 — 호스트와 워커는 무엇을 주고받는가 (예정)
- Dispatcher와 Invocation — 함수 호출이 워커에 도달하기까지 (예정)
- 스케일링 내부 동작 — Scale Controller, ScaleMonitor, 그리고 플랜별 차이 (예정)
- 콜드 스타트와 Placeholder Mode — 새 인스턴스가 만들어질 때 (예정)

---

## 참고 자료

**소스코드 (commit `5e59423`)**
- [`RpcWorkerProcess.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423/src/WebJobs.Script.Grpc/Rpc/RpcWorkerProcess.cs)
- [`WorkerProcess.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423/src/WebJobs.Script.Grpc/ProcessManagement/WorkerProcess.cs)
- [`GrpcWorkerChannel.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423/src/WebJobs.Script.Grpc/Channel/GrpcWorkerChannel.cs)
- [PR #4210 — `FUNCTIONS_WORKER_PROCESS_COUNT`](https://github.com/Azure/azure-functions-host/pull/4210)
- [`WorkerProcessCountOptions.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423/src/WebJobs.Script/Workers/WorkerProcessCountOptions.cs)
- [`WorkerConcurrencyOptions.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423/src/WebJobs.Script/Config/WorkerConcurrencyOptions.cs)
- [`WorkerConcurrencyManager.cs`](https://github.com/Azure/azure-functions-host/blob/5e59423/src/WebJobs.Script.Grpc/WorkerConcurrencyManager.cs)

**관련 워커 레포**
- [`Azure/azure-functions-nodejs-worker`의 `worker.config.json`](https://github.com/Azure/azure-functions-nodejs-worker/blob/v3.x/worker.config.json)
- [`Azure/azure-functions-python-worker`](https://github.com/Azure/azure-functions-python-worker)
- [`Azure/azure-functions-java-worker`의 `worker.config.json`](https://github.com/Azure/azure-functions-java-worker/blob/dev/worker.config.json)

Tags: Azure Functions, Serverless, Distributed Systems, gRPC

---

© 2026 영선북스. 이 글의 저작권은 저자에게 있습니다.
