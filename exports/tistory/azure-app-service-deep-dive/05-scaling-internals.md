
# 스케일링 내부 동작 — Scale Out 결정과 워커 추가 경로

## Source Version

이 글의 인용과 판단은 다음 공개 출처를 기준으로 합니다.

- Microsoft Learn — Azure App Service 문서 (https://learn.microsoft.com/azure/app-service)
- Project Kudu (https://github.com/projectkudu/kudu) — 배포 엔진과 Windows 샌드박스 문맥에 한해

App Service의 Front-End, Worker, File Server 구현 세부사항은 Microsoft가 공개하지 않았습니다.
따라서 이 시리즈에서는 Learn 문서가 1차 출처이고, Kudu 공개 자료는 보조 출처로만 사용합니다.

> Azure App Service Deep Dive 시리즈 (5/6)

스케일링 101에서는 무엇을 언제 늘릴지 판단 기준을 다뤘습니다.
이번 화는 그 다음 질문입니다.

**Scale Out을 하기로 결정한 뒤,
그 결정은 어떤 경로를 거쳐 실제 워커 증가가 되는가.**

공개 문서 기준으로 안전하게 말할 수 있는 범위는 분명합니다.

- scale up은 App Service Plan SKU를 바꿉니다.
- scale out은 인스턴스 수를 바꿉니다.
- autoscale 규칙은 Azure Monitor autoscale이 평가합니다.
- 대상은 app이 아니라 App Service Plan입니다.

이번 글은 여기서 한 단계 더 들어갑니다.
비공개 배치 엔진을 추측하지 않고,
**공개 문서가 보여 주는 확장 판단 루프의 관측 가능한 내부 동작**을 정리하는 것이 목표입니다.

---

<!-- a-grade-intro:begin -->
## 핵심 질문

Scale 내부 동작을 이해하면 어떤 비용·지연 사고를 예방할 수 있을까요?

이 글은 그 질문에 답하기 위해 Scale 내부 동작의 핵심 결정과 운영 함정을 살펴봅니다.

<!-- a-grade-intro:end -->

## 이 글에서 답할 질문

- Auto-scale 룰은 어떤 메트릭 소스를 어떤 주기로 평가하는가?
- scale-out과 scale-up은 같은 의사결정 트리에 있지 않다 — 누가 어떻게 갈리는가?
- Per-site scaling은 언제 켜야 하고, 언제 켜면 위험한가?
- scale 동작 시 새 인스턴스의 cold-start는 어디까지 보호되는가?
- scale-in 시 기존 연결과 stateful 상태는 어떻게 처리되는가?

## 큰 그림 — autoscale에서 worker 추가까지

![autoscale 판단이 worker 추가로 이어지는 제어 경로](https://yeongseon-books.github.io/book-public-assets/assets/azure-app-service-deep-dive/05/05-01-the-control-path-in-one-diagram.ko.png)

*autoscale 판단이 worker 추가로 이어지는 제어 경로*
이 그림에서 중요한 건 두 가지입니다.

1. 판단 엔진과 실행 substrate를 분리해서 보는 것
2. “app이 직접 VM을 띄운다”는 상상을 버리는 것

scale-out은 control plane이 App Service Plan의 원하는 인스턴스 수를 바꾸고,
플랫폼이 그만큼의 워커 용량을 반영하는 과정으로 이해하는 편이 맞습니다.

---

## scale up과 scale out은 무엇을 실제로 바꾸는가

![scale up과 scale out이 바꾸는 대상 비교](https://yeongseon-books.github.io/book-public-assets/assets/azure-app-service-deep-dive/05/05-02-what-scale-up-and-scale-out-actually-cha.ko.png)

*scale up과 scale out이 바꾸는 대상 비교*
Learn 문서는 이 차이를 명확히 설명합니다.

- **Scale up**: 더 큰 CPU, memory, features를 가진 tier/SKU로 이동
- **Scale out**: 앱을 실행하는 VM instance count 증가

이 차이를 runtime 관점으로 번역하면 이렇습니다.

- scale up은 worker 한 대의 체급을 바꿉니다.
- scale out은 앱이 사용할 worker 수를 늘립니다.

그래서 메모리 부족과 동시 요청 부족은 같은 “느림”으로 보이더라도 확장 방향이 달라집니다.

---

## autoscale 규칙은 app이 아니라 plan에 붙는다

이 부분은 현업에서 자주 헷갈립니다.
App Service 앱 화면에서 autoscale을 설정하더라도,
실제 타깃 리소스는 **App Service Plan** 입니다.

![autoscale 규칙이 앱이 아닌 plan에 붙는 구조](https://yeongseon-books.github.io/book-public-assets/assets/azure-app-service-deep-dive/05/05-03-autoscale-attaches-to-the-plan-not-the-a.ko.png)

*autoscale 규칙이 앱이 아닌 plan에 붙는 구조*
이 구조 때문에 같은 plan에 여러 앱이 있으면 서로 영향이 생깁니다.
한 앱의 급격한 부하가 plan 전체 확장을 유도하고,
그 capacity를 다른 앱도 함께 공유하게 됩니다.

그래서 noisy-neighbor 문제를 피하려면,
확장 패턴이 크게 다른 앱을 같은 plan에 얹지 않는 설계가 중요합니다.

---

## Azure Monitor autoscale이 하는 일

Azure Monitor autoscale 문서는 역할을 명확히 말합니다.

- 메트릭 또는 스케줄 기반으로 규칙 평가
- 최소/기본/최대 instance count 유지
- scale-out은 조건 중 하나만 만족해도 실행 가능
- scale-in은 조건이 모두 만족해야 실행

![메트릭 평가와 cooldown으로 움직이는 autoscale 루프](https://yeongseon-books.github.io/book-public-assets/assets/azure-app-service-deep-dive/05/05-04-what-azure-monitor-autoscale-actually-do.ko.png)

*메트릭 평가와 cooldown으로 움직이는 autoscale 루프*
이 로직은 운영적으로 아주 중요합니다.
scale-out이 OR처럼,
scale-in이 AND처럼 행동한다는 뜻이기 때문입니다.
그래서 확장은 빠르고,
축소는 더 보수적이어야 합니다.

여기에 autoscale 문서가 하나를 더 붙입니다.
autoscale job은 리소스 종류에 따라 대략 **30~60초마다** 실행되고,
scale action이 발생한 뒤에는 cooldown 동안 다시 판단하지 않습니다.
즉 이 시스템은 인터럽트가 아니라 주기적 control loop입니다.

---

## autoscale 설정은 실제로 어떤 모양인가

Azure Monitor 문서가 공개하는 `Microsoft.Insights/autoscaleSettings` 스키마를 보면,
App Service scale-out을 읽는 시선도 더 선명해집니다.

- `targetResourceUri` — 실제 확장 대상 리소스
- `profiles` — 시간대별 또는 기본 확장 정책
- `capacity.minimum/default/maximum` — 하한, fallback, 상한
- `rules[].metricTrigger` — 어떤 메트릭을 어떤 창으로 볼지
- `rules[].scaleAction` — 몇 대를 늘리거나 줄일지와 cooldown

즉 autoscale은 “CPU 70%면 늘린다” 수준의 포털 토글이 아니라,
메트릭 창과 행동 규칙을 가진 ARM 리소스입니다.

---

## 메트릭 창이 반응 속도를 결정한다

autoscale 규칙은 임계값만 보지 않습니다.
문서는 `timeGrain`, `timeWindow`, `statistic`, `timeAggregation`을 함께 봐야 한다고 설명합니다.

- `timeGrain` — 메트릭 샘플링 단위
- `timeWindow` — 얼마 동안의 샘플을 볼지
- `statistic` / `timeAggregation` — 평균, 합계, 최대값 등 어떤 방식으로 집계할지

이 뜻은 단순합니다.
같은 CPU 80% 규칙이라도,
1분 평균을 10분 창으로 볼 때와 1분 창으로 볼 때의 반응 속도는 다릅니다.
autoscale은 스파이크를 즉시 반영하는 장치가 아니라,
메트릭 창을 통과한 신호에 반응하는 장치입니다.

---

## cooldown은 확장 속도보다 안정성을 위해 존재한다

autoscale 문서는 scale-out과 scale-in 모두에 cooldown이 적용된다고 명시합니다.
예시 스키마의 기본값도 흔히 `PT5M`입니다.

운영적으로 보면 cooldown의 의미는 분명합니다.

- worker를 하나 추가한 직후 메트릭이 안정될 시간을 줍니다.
- 막 줄인 capacity를 다시 바로 늘리는 출렁임을 줄입니다.
- startup과 warm-up 지연이 있는 App Service에서 과잉 반응을 줄입니다.

이 특성 때문에 scale-up이나 scale-out 판단은 “규칙을 만족한 시점”보다,
`timeWindow + evaluation cadence + cooldown + startup readiness` 전체를 같이 봐야 정확합니다.

---

## 새 worker가 추가된다는 말의 실제 의미

공개 문서는 내부 배치 알고리즘을 세세하게 열어두지는 않습니다.
하지만 멘탈 모델은 충분히 잡을 수 있습니다.

1. autoscale 또는 수동 설정이 plan의 목표 인스턴스 수를 올립니다.
2. App Service control plane이 그 목표 상태를 반영합니다.
3. 해당 plan의 앱들은 늘어난 워커 용량만큼 더 많은 인스턴스를 확보할 수 있습니다.
4. Front-End가 정상 상태에 들어온 새 워커로도 요청을 보내기 시작합니다.

![목표 인스턴스 수가 새 worker로 반영되는 흐름](https://yeongseon-books.github.io/book-public-assets/assets/azure-app-service-deep-dive/05/05-05-what-adding-a-worker-means-in-practice.ko.png)

*목표 인스턴스 수가 새 worker로 반영되는 흐름*
이 정도가 공개 출처를 벗어나지 않으면서도 실전적으로 충분한 설명입니다.

---

## 왜 autoscale은 즉시성이 아니라 피드백 루프로 봐야 하는가

101에서도 말했지만,
autoscale은 예언이 아니라 반응입니다.

![메트릭 지연과 cooldown이 끼는 확장 피드백 루프](https://yeongseon-books.github.io/book-public-assets/assets/azure-app-service-deep-dive/05/05-06-why-autoscale-should-be-read-as-a-feedba.ko.png)

*메트릭 지연과 cooldown이 끼는 확장 피드백 루프*
그래서 예측 가능한 이벤트에는 선제적 확장이 더 안전합니다.
메트릭이 쌓이고,
규칙이 평가되고,
cooldown이 지나고,
새 worker가 준비되기까지 시간차가 있기 때문입니다.

이 시간차를 무시하면 “autoscale 켰는데도 첫 5분이 아프다”가 반복됩니다.

---

## Front-End와 health가 scale-out 완료 시점을 사실상 마감한다

worker를 추가했다고 바로 요청을 받는 것은 아닙니다.
Front-End 입장에서 그 worker가 받아도 되는 상태여야 합니다.

![새 worker가 healthy pool에 들어가는 마지막 단계](https://yeongseon-books.github.io/book-public-assets/assets/azure-app-service-deep-dive/05/05-07-health-and-readiness-are-the-real-end-of.ko.png)

*새 worker가 healthy pool에 들어가는 마지막 단계*
즉,
scale-out의 끝은 instance count 숫자가 아니라,
새 worker가 healthy pool에 들어오는 시점입니다.

즉 문서가 보여 주는 scale-out 설명은 여기까지입니다. 그 다음에 남는 지연은 새 워커가 실제 트래픽을 받을 준비를 마치는 startup·readiness 구간입니다.

---

## 여러 앱이 같은 plan을 공유할 때 생기는 일

App Service Plan 단위 확장은 비용에는 유리할 수 있지만,
확장 내부 동작을 읽을 때는 주의가 필요합니다.

- autoscale 트리거는 plan 자원에 반응합니다.
- worker는 plan 수준 capacity입니다.
- 앱별 트래픽 패턴이 다르면 서로 간섭이 생깁니다.

이 구조는 한 앱의 scale event가 plan 전체 자원 곡선을 바꾼다는 뜻입니다.
그래서 deep dive 관점에서는 “내 앱이 확장된다”보다 “내 plan이 확장되고 그 안에서 내 앱의 인스턴스가 늘어난다”가 더 정확한 문장입니다.

---

## scale-in이 더 위험한 이유

scale-out은 부족한 capacity를 더하는 작업입니다.
scale-in은 사용 중인 capacity를 줄이는 작업입니다.

그래서 scale-in은 항상 더 위험합니다.

- 아직 붙어 있는 affinity 사용자
- 긴 요청 처리 중인 worker
- 아직 완전히 식지 않은 burst traffic

공개 autoscale best practice 문서가 scale-in을 더 보수적으로 다루라고 하는 이유가 여기에 있습니다.

autoscale 문서는 여기서 한 단계 더 나갑니다.
축소 결과가 다시 곧바로 scale-out 조건을 만들면 flapping으로 간주할 수 있고,
이 경우 autoscale은 축소를 미루거나 덜 줄이는 식으로 반응할 수 있습니다.
즉 scale-in은 단순 역연산이 아니라,
서비스 가용성을 우선하는 안정화 로직이 덧붙은 동작입니다.

---

## 진짜로 무슨 판단이 있었는지는 로그에서 본다

이 주제에서 가장 deep-dive다운 공개 정보는 Azure Monitor 진단 로그입니다.
autoscale 진단 문서는 다음 두 로그 범주를 명시합니다.

- `AutoscaleEvaluationsLog` — 어떤 규칙과 메트릭을 어떻게 평가했는지
- `AutoscaleScaleActionsLog` — 실제 scale action을 언제 시작했고 결과가 어땠는지

또 Activity Log에는 scale-up/scale-down initiated/completed 이벤트가 남습니다.

즉 App Service scaling을 운영에서 추적할 때는 “늘어난 것 같다”가 아니라,
**autoscale setting 리소스가 어떤 평가를 했고 어떤 action을 찍었는지**를 Log Analytics와 Activity Log에서 확인할 수 있습니다.

---

## 5화 정리

이번 화의 핵심을 한 문단으로 줄이면 다음과 같습니다.

> App Service의 scale-out은 app 자체가 서버를 직접 추가하는 모델이 아니라, Azure Monitor autoscale 또는 수동 설정이 App Service Plan의 목표 인스턴스 수를 바꾸고, App Service control plane이 그 상태를 반영해 워커 용량을 늘리는 과정입니다. 그 뒤 새 워커가 앱 startup과 health 통과를 마쳐야 Front-End가 실제 트래픽을 보내기 시작합니다. scale up은 SKU 변경이고, scale out은 워커 수 변경이며, 둘 모두 plan 단위로 생각해야 정확합니다.

이번 글의 경계는 여기까지입니다.
외부 autoscale 결정으로 worker capacity가 늘어난 뒤에도,
그 실행 단위가 실제 트래픽을 받기까지는 별도의 startup·readiness 구간이 남습니다.

---

## 이 시리즈에서의 위치

이번 글은 101의 스케일링 판단 기준을 내부 경로로 번역하는 편입니다. 여기서 얻는 가치는 scale-out 판단과 워커 준비 상태를 한 덩어리로 보지 않고, control plane과 실행 경계를 분리해 이해하게 된다는 점입니다.

---

## Documented Behavior Summary

- App Service autoscale의 실제 대상 리소스는 개별 앱이 아니라 App Service Plan입니다.
- Azure Monitor autoscale은 30~60초 주기의 평가 job, time window, cooldown, flapping 방지 로직으로 동작합니다.
- scale-out은 하나 이상의 확장 규칙이 충족되면 실행될 수 있지만, scale-in은 모든 축소 규칙이 충족되어야 합니다.
- `AutoscaleEvaluationsLog`, `AutoscaleScaleActionsLog`, Activity Log를 통해 실제 평가와 실행 결과를 추적할 수 있습니다.

### auto-scale 룰과 instance count 추적

```bash
az monitor autoscale show -g my-rg -n my-app-autoscale

az monitor metrics list \
  --resource $(az appservice plan show -n my-plan -g my-rg --query id -o tsv) \
  --metric "CpuPercentage,HttpQueueLength" --interval PT1M -o table
```

## 시니어 엔지니어는 이렇게 생각합니다

- **스케일 결정은 메트릭 윈도 기반** — 값이 짧으면 진동, 길면 지연이 됩니다.
- **scale-out과 scale-in의 정책을 분리** — 내림 정책이 비용을 결정합니다.
- **Plan 한도가 근본 상한** — SKU·지역 한도를 사전에 점검합니다.
- **워밍업 시간을 SLA에 포함** — 새 인스턴스가 준비되는 시간이 사용자 체감입니다.
- **로그·메트릭으로 스케일을 가시화** — 왜 스케일했는지 모르면 튜닝이 불가능합니다.

## 운영 체크리스트

- [ ] scale-out 메트릭과 임계치의 ‘정상 시’ baseline을 측정해 두었다
- [ ] per-site scaling 사용 여부를 ADR로 남겼다
- [ ] scale-in 동안 graceful drain을 위한 SIGTERM 핸들러를 점검했다
- [ ] scale 이벤트 알림과 instance count 그래프를 대시보드에 두었다
- [ ] scale-up(SKU 변경)과 scale-out 운영 절차를 분리했다

## 시리즈 목차

- [App Service 플랫폼 아키텍처 — Front-End·Worker·File Server](./01-platform-architecture.md)
- [Front-End과 ARR — 요청은 어떻게 워커에 도달하는가](./02-front-end-and-arr.md)
- [Worker 인스턴스와 샌드박스 — 사용자 코드를 어디에 가두는가](./03-worker-and-sandbox.md)
- [배포와 Kudu — 빌드·동기화·릴리스의 안쪽](./04-deployment-and-kudu.md)
- **스케일링 내부 동작 — Scale Out 결정과 워커 추가 경로 (현재 글)**
- 콜드 스타트와 Warmup — 첫 요청이 비싼 이유 (예정)

---

## 참고 자료

### 1차 출처
- [Understand autoscale settings in Azure Monitor](https://learn.microsoft.com/azure/azure-monitor/autoscale/autoscale-understanding-settings)
- [Diagnostic settings in autoscale](https://learn.microsoft.com/azure/azure-monitor/autoscale/autoscale-diagnostics)

### 2차 출처
- [Scale up an app in Azure App Service](https://learn.microsoft.com/azure/app-service/manage-scale-up)
- [Get started with autoscale in Azure](https://learn.microsoft.com/azure/azure-monitor/autoscale/autoscale-get-started)
- [Autoscale in Azure Monitor](https://learn.microsoft.com/azure/azure-monitor/autoscale/autoscale-overview)
- [Best practices for autoscale](https://learn.microsoft.com/azure/azure-monitor/autoscale/autoscale-best-practices)
- [Monitoring data reference for Azure Monitor](https://learn.microsoft.com/azure/azure-monitor/monitor-reference)
- [Architecture best practices for Azure App Service web apps](https://learn.microsoft.com/azure/well-architected/service-guides/app-service-web-apps)

### 관련 시리즈
- [Azure App Service 101 — Scaling 101](../../azure-app-service-101/ko/07-scaling-101.md)
- [Azure Functions Deep Dive — 스케일링 내부 동작](../../azure-functions-deep-dive/ko/05-scaling-internals.md)

Tags: Azure, App Service, Distributed Systems, Platform Engineering

---

© 2026 영선북스. 이 글의 저작권은 저자에게 있습니다.
