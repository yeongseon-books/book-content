<!-- tags: Azure, App Service, Distributed Systems, Platform Engineering -->
# 콜드 스타트와 Warmup — 첫 요청이 비싼 이유

> Azure App Service Deep Dive 시리즈 (6/6)

이번 시리즈의 마지막 질문은 가장 체감이 강한 질문입니다.

**왜 첫 요청은 유난히 비싸고,
그 비용을 App Service는 어떻게 줄이려 하는가.**

cold start는 추상적 현상이 아닙니다.
worker가 아직 준비되지 않았거나,
프로세스가 막 올라오고 있거나,
새 container가 readiness를 통과하기 전이라는 뜻입니다.

---

## 큰 그림 — cold path와 warm path

![큰 그림 — cold path와 warm path](../../assets/azure-app-service-deep-dive/06/06-01-the-cold-path-and-the-warm-path.ko.png)
이 한 그림이 핵심입니다.
사용자가 느끼는 첫 요청 비용은,
사실상 “아직 ready하지 않은 실행 단위를 ready 상태로 만드는 비용”입니다.

---

## Windows와 Linux의 warm-up 신호는 같은가

같지 않습니다.
목표는 같지만 수단이 다릅니다.

### Windows code app

- IIS `applicationInitialization` 사용 가능
- Always On이 루트 경로 ping으로 idle unload를 줄임

### Linux app

- 플랫폼이 `WEBSITE_WARMUP_PATH`를 반복 호출 가능
- startup timeout은 `WEBSITES_CONTAINER_START_TIME_LIMIT` 영향을 받음

![Linux app](../../assets/azure-app-service-deep-dive/06/06-02-linux-apps.ko.png)
이 차이를 구분해야 warm-up 전략이 플랫폼과 맞습니다.

---

## Always On이 실제로 하는 일

App Service 관련 Microsoft 문서와 App Service 팀 블로그는 Always On의 역할을 비교적 일관되게 설명합니다.
idle 상태로 앱이 내려가거나 식는 것을 줄이기 위해 주기적으로 ping을 보냅니다.

현업에서는 보통 이렇게 이해하면 충분합니다.

- 유휴 시간을 오래 두지 않게 한다
- app pool unload 또는 cold path 진입 빈도를 낮춘다
- 첫 요청의 최악값을 줄인다

![Always On이 실제로 하는 일](../../assets/azure-app-service-deep-dive/06/06-03-what-always-on-really-does.ko.png)
중요한 건 Always On이 “모든 시작 비용을 제거”하지는 않는다는 점입니다.
재배포,
재시작,
새 scale-out worker,
container recycle은 여전히 별도 warm-up이 필요할 수 있습니다.

---

## Windows: `applicationInitialization`이 필요한 경우

루트 URL 한 번 치는 것만으로 앱이 완전히 준비되지 않는 경우가 많습니다.
예를 들면,

- 첫 DB connection pool 준비
- large cache priming
- 템플릿 컴파일
- JIT 또는 expensive startup path

이때 IIS `applicationInitialization`은 warm-up endpoint를 명시적으로 호출하게 해 줍니다.

![Windows: `applicationInitialization`이 필요한 경우](../../assets/azure-app-service-deep-dive/06/06-04-when-windows-needs-applicationinitializa.ko.png)
중요한 포인트는 endpoint 설계입니다.
200을 너무 빨리 주면 아직 안 된 인스턴스가 traffic pool에 들어갑니다.
반대로 너무 무거우면 warm-up 자체가 병목이 됩니다.

---

## Linux: warm-up path와 startup timeout

App settings reference는 Linux startup에 대해 매우 중요한 사실을 적습니다.

- 플랫폼이 `WEBSITE_WARMUP_PATH`에 반복 요청을 보냅니다.
- 기본적으로는 거의 어떤 응답이라도 readiness 신호로 간주할 수 있습니다.
- `WEBSITE_WARMUP_STATUSES`로 허용 상태 코드를 좁힐 수 있습니다.
- `WEBSITES_CONTAINER_START_TIME_LIMIT` 안에 ready가 안 되면 startup 실패로 간주됩니다.

![Linux: warm-up path와 startup timeout](../../assets/azure-app-service-deep-dive/06/06-05-linux-warm-up-path-and-startup-timeout.ko.png)
이 설정을 모르면 Linux 앱은 아주 자주 두 가지 실수를 합니다.

1. 아직 준비 안 됐는데 404/500도 readiness로 받아들여짐
2. startup time limit이 짧아 초기화 중 재시작 루프에 빠짐

---

## cold start를 비싸게 만드는 구성 요소

첫 요청 비용은 보통 한 원인이 아니라 여러 비용의 합입니다.

- worker 또는 container 생성
- 앱 프로세스 시작
- framework bootstrap
- dependency connection warm-up
- cache/JIT/module import
- health or warm-up path 성공까지의 시간

![cold start를 비싸게 만드는 구성 요소](../../assets/azure-app-service-deep-dive/06/06-06-what-makes-cold-start-expensive.ko.png)
그래서 cold start 최적화는 한 줄 설정이 아니라,
앱과 플랫폼의 계약을 같이 다루는 작업입니다.

---

## 좋은 warm-up endpoint의 조건

warm-up endpoint는 health endpoint와 비슷하지만 목적이 조금 다릅니다.
traffic eligibility를 열기 전에 “정말 준비됐는가”를 판단하는 신호이기 때문입니다.

좋은 warm-up endpoint는 보통 이 조건을 만족합니다.

- 인증 없이 platform이 호출할 수 있다
- 핵심 dependency readiness를 포함한다
- 끝나기 전에는 성공 코드를 주지 않는다
- 불필요한 heavy work는 반복하지 않는다

이 endpoint가 부정확하면 두 가지 나쁜 방향이 생깁니다.

- 너무 빨리 성공해서 미완성 worker가 traffic을 받음
- 너무 늦게 성공해서 scale-out과 swap이 계속 지연됨

---

## deployment slot warm-up이 중요한 이유

slot은 cold start를 사용자 앞에서 치르지 않게 해 주는 장치입니다.

![deployment slot warm-up이 중요한 이유](../../assets/azure-app-service-deep-dive/06/06-07-why-deployment-slots-help-so-much.ko.png)
이 흐름이 의미하는 바는 분명합니다.
warm-up이 staging에서 끝났다면 production 사용자 요청이 그 비용을 직접 부담할 가능성이 낮아집니다.

그래서 4화의 배포와 이번 화의 warm-up은 사실 같은 이야기의 앞뒤입니다.

---

## Always On, health, warm-up은 서로 다른가

서로 다릅니다.

- **Always On**: idle coldness를 줄임
- **warm-up path**: 시작 직후 readiness 판단
- **health check**: traffic을 계속 받을 자격 판단

![Always On, health, warm-up은 서로 다른가](../../assets/azure-app-service-deep-dive/06/06-08-always-on-warm-up-and-health-are-not-the.ko.png)
이 셋을 섞어 생각하면 설정은 켰는데 효과는 엇갈립니다.
특히 “Always On 켰는데 왜 배포 직후는 느리지?”라는 질문이 여기서 나옵니다.

---

## 6화 정리

이번 화의 핵심을 한 문단으로 줄이면 이렇습니다.

> App Service에서 cold start는 warm worker가 아직 없거나 새 process/container가 readiness를 통과하지 못한 상태에서 첫 요청이 들어올 때의 비용입니다. Windows에서는 `applicationInitialization`과 Always On이, Linux에서는 `WEBSITE_WARMUP_PATH`, `WEBSITE_WARMUP_STATUSES`, `WEBSITES_CONTAINER_START_TIME_LIMIT`이 중요한 계약입니다. Always On은 idle coldness를 줄일 뿐이고, 배포·재시작·scale-out 직후의 startup readiness는 별도 warm-up 경로가 책임집니다.

이번 화로 시리즈를 닫습니다.
이제 App Service를 “코드 올리는 곳”이 아니라,
Front-End,
ARR,
worker,
sandbox,
Kudu,
shared storage,
autoscale,
warm-up이 한 시스템으로 이어진 플랫폼으로 볼 수 있습니다.

---

## 이 시리즈에서의 위치

이번 글은 앞선 다섯 편에서 계속 예고했던 마지막 박스, 즉 새로운 worker가 실제 트래픽을 받기 전까지의 준비 시간을 정리합니다.
시리즈 전체를 다시 따라가면 요청 진입, 실행 경계, 배포, 스케일링, warm-up이 하나의 운영 모델로 이어진다는 점이 보일 것입니다.

---

<!-- toc:begin -->
## 시리즈 목차

- [App Service 플랫폼 아키텍처 — Front-End·Worker·File Server](./01-platform-architecture.md)
- [Front-End과 ARR — 요청은 어떻게 워커에 도달하는가](./02-front-end-and-arr.md)
- [Worker 인스턴스와 샌드박스 — 사용자 코드를 어디에 가두는가](./03-worker-and-sandbox.md)
- [배포와 Kudu — 빌드·동기화·릴리스의 안쪽](./04-deployment-and-kudu.md)
- [스케일링 내부 동작 — Scale Out 결정과 워커 추가 경로](./05-scaling-internals.md)
- **콜드 스타트와 Warmup — 첫 요청이 비싼 이유 (현재 글)**

<!-- toc:end -->

---

## 참고 자료

### 1차 출처
- [Oryx README @ 20240408.1](https://github.com/microsoft/Oryx/blob/20240408.1/README.md)

### 2차 출처
- [Environment variables and app settings reference](https://learn.microsoft.com/azure/app-service/reference-app-settings)
- [Deploy staging slots in Azure App Service](https://learn.microsoft.com/azure/app-service/deploy-staging-slots)
- [IIS 8.0 Application Initialization](https://learn.microsoft.com/iis/get-started/whats-new-in-iis-8/iis-80-application-initialization)
- [Robust Apps for the Cloud — App Service team blog](https://azure.github.io/AppService/2020/05/15/Robust-Apps-for-the-cloud.html)

### 관련 시리즈
- [Azure App Service 101 — Request Lifecycle](../../azure-app-service-101/ko/02-request-lifecycle.md)
- [Azure Functions Deep Dive — 콜드 스타트와 Placeholder Mode](../../azure-functions-deep-dive/ko/06-cold-start-placeholder.md)
