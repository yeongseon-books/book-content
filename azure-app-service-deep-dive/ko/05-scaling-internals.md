# 스케일링 내부 동작 — Scale Out 결정과 워커 추가 경로

> Azure App Service Deep Dive 시리즈 (5/6)

스케일링 101에서는 무엇을 언제 늘릴지 판단 기준을 다뤘습니다.
이번 화는 그 다음 질문입니다.

**Scale Out을 하기로 결정한 뒤,
그 결정은 어떤 경로를 거쳐 실제 worker 증가가 되는가.**

공개 문서 기준으로 안전하게 말할 수 있는 범위는 분명합니다.

- scale up은 App Service Plan SKU를 바꿉니다.
- scale out은 인스턴스 수를 바꿉니다.
- autoscale 규칙은 Azure Monitor autoscale이 평가합니다.
- 대상은 app이 아니라 App Service Plan입니다.

그 위에서 worker pool 관점의 멘탈 모델을 정리하는 것이 이번 화의 목표입니다.

---

## 큰 그림 — autoscale에서 worker 추가까지

![큰 그림 — autoscale에서 worker 추가까지](../../assets/azure-app-service-deep-dive/05/05-01-the-control-path-in-one-diagram.ko.png)
이 그림에서 중요한 건 두 가지입니다.

1. 판단 엔진과 실행 substrate를 분리해서 보는 것
2. “app이 직접 VM을 띄운다”는 상상을 버리는 것

scale-out은 control plane이 App Service Plan의 원하는 인스턴스 수를 바꾸고,
플랫폼이 그만큼의 worker capacity를 반영하는 과정으로 이해하는 편이 맞습니다.

---

## scale up과 scale out은 무엇을 실제로 바꾸는가

![scale up과 scale out은 무엇을 실제로 바꾸는가](../../assets/azure-app-service-deep-dive/05/05-02-what-scale-up-and-scale-out-actually-cha.ko.png)
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

![autoscale 규칙은 app이 아니라 plan에 붙는다](../../assets/azure-app-service-deep-dive/05/05-03-autoscale-attaches-to-the-plan-not-the-a.ko.png)
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

![Azure Monitor autoscale이 하는 일](../../assets/azure-app-service-deep-dive/05/05-04-what-azure-monitor-autoscale-actually-do.ko.png)
이 로직은 운영적으로 아주 중요합니다.
scale-out이 OR처럼,
scale-in이 AND처럼 행동한다는 뜻이기 때문입니다.
그래서 확장은 빠르고,
축소는 더 보수적이어야 합니다.

---

## 새 worker가 추가된다는 말의 실제 의미

공개 문서는 내부 배치 알고리즘을 세세하게 열어두지는 않습니다.
하지만 멘탈 모델은 충분히 잡을 수 있습니다.

1. autoscale 또는 수동 설정이 plan의 desired count를 올립니다.
2. App Service control plane이 그 desired state를 반영합니다.
3. 해당 plan의 앱들은 늘어난 worker capacity를 통해 더 많은 인스턴스를 가질 수 있습니다.
4. Front-End가 새 healthy worker로도 요청을 보내기 시작합니다.

![새 worker가 추가된다는 말의 실제 의미](../../assets/azure-app-service-deep-dive/05/05-05-what-adding-a-worker-means-in-practice.ko.png)
이 정도가 공개 출처를 벗어나지 않으면서도 실전적으로 충분한 설명입니다.

---

## 왜 autoscale은 즉시성이 아니라 피드백 루프로 봐야 하는가

101에서도 말했지만,
autoscale은 예언이 아니라 반응입니다.

![왜 autoscale은 즉시성이 아니라 피드백 루프로 봐야 하는가](../../assets/azure-app-service-deep-dive/05/05-06-why-autoscale-should-be-read-as-a-feedba.ko.png)
그래서 예측 가능한 이벤트에는 선제적 확장이 더 안전합니다.
메트릭이 쌓이고,
규칙이 평가되고,
새 worker가 준비되기까지 시간차가 있기 때문입니다.

이 시간차를 무시하면 “autoscale 켰는데도 첫 5분이 아프다”가 반복됩니다.

---

## Front-End와 health가 scale-out 완료 시점을 사실상 마감한다

worker를 추가했다고 바로 요청을 받는 것은 아닙니다.
Front-End 입장에서 그 worker가 받아도 되는 상태여야 합니다.

![Front-End와 health가 scale-out 완료 시점을 사실상 마감한다](../../assets/azure-app-service-deep-dive/05/05-07-health-and-readiness-are-the-real-end-of.ko.png)
즉,
scale-out의 끝은 instance count 숫자가 아니라,
새 worker가 healthy pool에 들어오는 시점입니다.

이게 6화의 warm-up과 바로 이어집니다.

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

---

## 5화 정리

이번 화의 핵심을 한 문단으로 줄이면 다음과 같습니다.

> App Service의 scale-out은 app 자체가 서버를 직접 추가하는 모델이 아니라, Azure Monitor autoscale 또는 수동 설정이 App Service Plan의 desired instance count를 바꾸고, App Service control plane이 그 상태를 반영해 worker capacity를 늘리는 과정입니다. 그 뒤 새 worker가 앱 startup과 health 통과를 마쳐야 Front-End가 실제 트래픽을 보내기 시작합니다. scale up은 SKU 변경이고, scale out은 worker count 변경이며, 둘 모두 plan 단위로 생각해야 정확합니다.

다음 6화에서는 바로 그 마지막 구간,
새 worker가 organic traffic을 받기 전까지의 비싼 시간,
즉 cold start와 warm-up을 다룹니다.

---

## 이 시리즈에서의 위치

이번 글은 101의 스케일링 판단 기준을 내부 경로로 번역하는 편입니다.
다음 글에서는 새 worker가 실제로 첫 요청을 받기 전 어떤 준비 과정을 거치는지, Always On과 warm-up path가 그 시간을 어떻게 줄이는지로 이어집니다.

---

## 참고 자료

### 1차 출처
- [Oryx README @ 20240408.1](https://github.com/microsoft/Oryx/blob/20240408.1/README.md)

### 2차 출처
- [Scale up an app in Azure App Service](https://learn.microsoft.com/azure/app-service/manage-scale-up)
- [Get started with autoscale in Azure](https://learn.microsoft.com/azure/azure-monitor/autoscale/autoscale-get-started)
- [Autoscale in Azure Monitor](https://learn.microsoft.com/azure/azure-monitor/autoscale/autoscale-overview)
- [Best practices for autoscale](https://learn.microsoft.com/azure/azure-monitor/autoscale/autoscale-best-practices)
- [Architecture best practices for Azure App Service web apps](https://learn.microsoft.com/azure/well-architected/service-guides/app-service-web-apps)

### 관련 시리즈
- [Azure App Service 101 — Scaling 101](../../azure-app-service-101/ko/07-scaling-101.md)
- [Azure Functions Deep Dive — 스케일링 내부 동작](../../azure-functions-deep-dive/ko/05-scaling-internals.md)
