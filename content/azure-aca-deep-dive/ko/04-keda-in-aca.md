---
title: ACA 안의 KEDA — Scale Rule이 만드는 것
series: azure-aca-deep-dive
episode: 4
language: ko
status: ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- Container Apps
- KEDA
- Dapr
- Envoy
last_reviewed: '2026-04-29'
---

# ACA 안의 KEDA — Scale Rule이 만드는 것

> Azure Container Apps Deep Dive 시리즈 (4/6)

Azure Container Apps의 제품 표면에서 스케일링은 몇 개 필드로 끝납니다.

`minReplicas`를 적습니다.
`maxReplicas`를 적습니다.
HTTP, TCP, 또는 custom rule을 추가합니다.
나머지는 플랫폼이 처리합니다.

표면이 짧은 이유는 의도적입니다.
진짜 질문은, 이 규칙이 replica 수로 바뀌려면 플랫폼이 아래에서 무엇을 만들어야 하는가입니다.

답은 KEDA입니다.

Microsoft 문서도 Container Apps 스케일링이 KEDA 기반이라고 분명히 적습니다.
이 사실은 즉시 두 가지를 알려 줍니다.

1. 플랫폼은 완전히 별개의 스케일링 모델을 새로 만든 것이 아니라 event-driven autoscaling 계열을 사용합니다.
2. ACA scale rule은, 실제 Kubernetes object를 직접 보여주지 않더라도, KEDA의 `ScaledObject` 중심 control loop와 비슷한 모양으로 번역된다고 보는 편이 맞습니다.

이번 화는 그 숨은 번역 과정을 따라갑니다.

---

## 짧게 말하면: Scale rule은 scaler 자체가 아닙니다

ACA에서 여러분이 적는 scale rule은 제품 설정입니다.
런타임 scaler object 자체가 아닙니다.

플랫폼은 이 rule을 KEDA가 reconcile할 수 있는 형태로 바꿔야 합니다.

가장 맞는 그림은 이것입니다.

![짧게 말하면: Scale rule은 scaler 자체가 아닙니다](../../../assets/azure-aca-deep-dive/04/04-01-the-short-version-a-scale-rule-is-not-th.ko.png)
숨은 오브젝트를 직접 보지는 못합니다.
그래도 알아야 하는 이유는, 여러분이 관찰하는 동작이 이 번역 단계의 downstream이기 때문입니다.

---

## 왜 KEDA가 정확한 고정점인가

Upstream KEDA는 구조가 매우 분명합니다.

- `ScaledObject`가 target과 trigger를 기술합니다.
- KEDA operator가 이를 reconcile합니다.
- KEDA가 HPA를 만들고 갱신합니다.
- metrics adapter가 HPA의 external metric 질의에 응답합니다.

Upstream KEDA source는 이 구조를 그대로 보여 줍니다.
`ScaledObject` 타입은 trigger metadata, cooldown, min/max replica, target reference를 담습니다.
Controller는 이를 reconcile하고 HPA spec을 만듭니다.

그래서 ACA 심화 시리즈에서 pinned KEDA source를 반드시 보라는 품질 게이트가 붙어 있는 것입니다.
ACA 자체는 closed-source여도, 숨은 autoscaling loop의 모양은 KEDA가 설명해 줍니다.

---

## ACA가 노출하는 것과 KEDA가 필요로 하는 것

나란히 놓으면 대응이 쉬워집니다.

![ACA가 노출하는 것과 KEDA가 필요로 하는 것](../../../assets/azure-aca-deep-dive/04/04-02-what-aca-exposes-versus-what-keda-needs.ko.png)
KEDA는 scale target, metric 또는 trigger 정의, 그리고 limit 정보를 원합니다.
ACA의 revision template는 이미 그 개념들을 갖고 있습니다.

그래서 ACA scale rule에서 숨은 KEDA 오브젝트로의 개념 점프는 작습니다.
제품이 실제 object를 private하게 감췄을 뿐입니다.

---

## 첫 번째 핵심 동작: 스케일링은 Revision 단위입니다

ACA의 traffic은 app-facing입니다.
스케일링은 revision-facing입니다.

그래서 scale rule을 바꾸면 revision-scope 변경이 되고, 새 Revision이 생성됩니다.
Microsoft의 revisions 문서도 이 사실을 분명히 적습니다.

즉 스케일 엔진은 mutable한 배포 정체성이 아니라, 불변 Revision 스냅샷에 붙습니다.

![첫 번째 핵심 동작: 스케일링은 Revision 단위입니다](../../../assets/azure-aca-deep-dive/04/04-03-the-first-key-behavior-scaling-is-per-re.ko.png)
두 Revision이 동시에 active 상태라면, 같은 app-level ingress 표면을 공유하면서도 각자 별도의 scale behavior를 가질 수 있습니다.

그래서 rollout 수학과 scaling 수학을 같은 개념으로 합치면 안 됩니다.

---

## `ScaledObject`는 HPA를 대체하는 것이 아니라 HPA를 만들어 냅니다

이 부분은 KEDA에서 가장 흔한 오해입니다.
KEDA는 HPA를 마법처럼 대체하는 전혀 다른 시스템이 아닙니다.
HPA 동작을 관리하고 먹이는 계층입니다.

Upstream KEDA source를 보면 이 사실이 분명합니다.
Controller는 `ScaledObject`를 reconcile하고 HPA spec을 생성합니다.
HPA 생성 로직은 min/max replica, metric target, scale target reference를 채웁니다.

![`ScaledObject`는 HPA를 대체하는 것이 아니라 HPA를 만들어 냅니다](../../../assets/azure-aca-deep-dive/04/04-04-a-scaledobject-creates-hpa-behavior-not.ko.png)
ACA에서도 이 큰 역할 분담은 그대로라고 보는 편이 맞습니다.
제품 표면이 KEDA에게 Revision에 대한 HPA류 결정을 만들 정보만 전달하는 구조입니다.

---

## `minReplicas`가 0일 수 있다는 점이 모든 것을 바꿉니다

ACA는 `minReplicas: 0`을 명시적으로 허용합니다.
이것이 scale-to-zero 이야기입니다.

여기서 event-driven 모델이 plain HPA 사고방식보다 중요해집니다.
전통적인 HPA만으로는 event signal에 의해 0에서 깨어나는 activation을 자연스럽게 설명하기 어렵습니다.
KEDA는 그 부분을 설명합니다.

![`minReplicas`가 0일 수 있다는 점이 모든 것을 바꿉니다](../../../assets/azure-aca-deep-dive/04/04-05-minreplicas-can-be-zero-and-that-changes.ko.png)
Microsoft의 scaling 문서도 마지막 replica에서 0으로 내려갈 때 cooldown이 특히 중요하다고 설명합니다.
이건 바로 KEDA식 event-driven lifecycle이 잘 드러나는 지점입니다.

---

## Custom rule이 replica가 되기까지의 control loop

Custom rule은 흐름이 가장 선명합니다.

![Custom rule이 replica가 되기까지의 control loop](../../../assets/azure-aca-deep-dive/04/04-06-the-control-loop-how-a-custom-rule-becom.ko.png)
실제 Kubernetes object를 직접 볼 수 없더라도, 이 흐름이 가장 맞는 추상화입니다.

---

## HTTP scaling은 built-in 기능이지만, 모양은 여전히 KEDA 계열입니다

ACA는 request concurrency 기반 built-in HTTP scaler를 제공합니다.
Microsoft 문서는 concurrent requests와 15초 측정 창 기준으로 이 규칙을 설명합니다.

여기서 조심할 구분이 있습니다.

ACA HTTP scaling이 upstream `kedacore/http-add-on`과 완전히 같은 구현이라고 말하면 안 됩니다.
그 주장은 소스가 보장하지 않습니다.

대신 이렇게 말하면 정확합니다.

- ACA는 HTTP scaling을 built-in product feature로 노출합니다.
- 그 스케일링 모델은 KEDA의 event-driven autoscaling 사고방식과 개념적으로 맞닿아 있습니다.
- Trigger 입력은 request concurrency입니다.

![HTTP scaling은 built-in 기능이지만, 모양은 여전히 KEDA 계열입니다](../../../assets/azure-aca-deep-dive/04/04-07-http-scaling-is-built-in-but-the-shape-s.ko.png)
이렇게 써야 정확성을 지키면서도 실제 동작을 설명할 수 있습니다.

---

## TCP scaling도 큰 모양은 같습니다

ACA는 TCP concurrency scaling도 제공합니다.
제품 표면은 HTTP와 거의 평행합니다.

- 동시 연결 수 임계치 정의
- 측정 창에서 수요 관측
- 임계치 초과 시 replica 증가

깊은 내부 설명도 동일합니다.
구체 구현은 플랫폼이 책임집니다.
그래도 전체 모양은 KEDA류 autoscaling loop로 보는 편이 맞습니다.

---

## Custom rule은 ACA 안에서 가장 KEDA 냄새가 진한 부분입니다

Microsoft scaling 가이드는 custom ACA rule이 KEDA scaler에서 어떻게 옮겨지는지 꽤 직접적으로 설명합니다.
KEDA scaler metadata와 authentication을 ACA rule field로 번역하는 과정까지 안내합니다.

이건 사실상 "여기는 KEDA 식으로 생각해도 된다"는 신호에 가깝습니다.

![Custom rule은 ACA 안에서 가장 KEDA 냄새가 진한 부분입니다](../../../assets/azure-aca-deep-dive/04/04-08-custom-rules-are-the-clearest-keda-shape.ko.png)
즉 제품은 완전히 새로운 autoscaling 언어를 만든 것이 아니라, 선별된 KEDA 표면을 제품화해서 내놓은 셈입니다.

---

## Scale rule 인증도 번역 경계입니다

Upstream KEDA는 `TriggerAuthentication` 리소스나 identity 구성을 자주 사용합니다.
ACA는 그런 raw object를 직접 노출하지 않습니다.

대신 같은 의도를 제품 표면으로 바꿔 제공합니다.

- Scale rule auth field에 연결되는 secret
- 지원되는 Azure trigger용 managed identity 설정

![Scale rule 인증도 번역 경계입니다](../../../assets/azure-aca-deep-dive/04/04-09-authentication-for-scale-rules-is-anothe.ko.png)
모양은 여전히 알아볼 수 있습니다.
리소스 모델만 제품화되었을 뿐입니다.

---

## 이름을 몰라도 metrics adapter는 중요합니다

Upstream KEDA에 metrics adapter가 있는 이유는 HPA가 metric 답변을 받아야 하기 때문입니다.
KEDA의 HPA 생성 코드는 external metric selector를 붙여, adapter가 올바른 scaled object의 metric 질의에 응답할 수 있게 만듭니다.

이 연결 고리는 숨겨져 있지만 중요합니다.

![이름을 몰라도 metrics adapter는 중요합니다](../../../assets/azure-aca-deep-dive/04/04-10-why-the-metrics-adapter-matters-even-whe.ko.png)
ACA에서는 adapter를 직접 건드리지 않습니다.
그래도 외부 이벤트나 concurrency 규칙이 replica 수를 바꾸는 순간마다, 그 효과를 간접적으로 보고 있는 셈입니다.

---

## KEDA 기본값은 ACA에서 나중에 눈에 띄는 동작을 설명합니다

Microsoft scaling 문서는 custom rule의 기본 polling interval과 cooldown 값도 짚습니다.
이 숫자들은 KEDA control loop의 감각과 잘 맞습니다.

운영 중 자주 보이는 현상도 여기서 설명됩니다.

- 스케일 변화가 밀리초 단위로 연속 발생하지는 않음
- 1에서 0으로 내려갈 때 cooldown 성격이 눈에 띔
- 0에서 깨어나는 activation과, 0이 아닌 구간의 steady-state scaling이 체감상 다름

이건 임의의 제품 quirks가 아닙니다.
Polling과 cooldown을 가진 event-driven autoscaling loop의 자연스러운 결과입니다.

---

## 여러 rule 중 하나만 활성화돼도 Revision은 깨어날 수 있습니다

ACA 문서도 여러 scale rule이 있으면 첫 번째 조건을 만족한 rule 하나만으로 scale이 시작될 수 있다고 설명합니다.

Activation logic은 이렇게 보는 편이 맞습니다.

![여러 rule 중 하나만 활성화돼도 Revision은 깨어날 수 있습니다](../../../assets/azure-aca-deep-dive/04/04-11-one-rule-can-wake-the-revision-up.ko.png)
즉 여러 rule이 하나의 거대한 평균 임계치로 합쳐지는 것이 아닙니다.
같은 scale target으로 들어가는 여러 activation path입니다.

---

## Scale rule이 revision template에 붙는 이유

왜 ACA는 scale rule을 revision-scope로 두었을까요.

스케일링이 metadata가 아니라 runtime behavior이기 때문입니다.

Canary Revision은 stable Revision과 다른 limit나 threshold를 원할 수 있습니다.
새 버전이 요청 처리 효율을 바꾸면 concurrency threshold도 달라질 수 있습니다.

Scale rule이 app-scope만 가졌다면, rollout 실험에서 가장 중요한 제어 노브 하나를 잃게 됩니다.

![Scale rule이 revision template에 붙는 이유](../../../assets/azure-aca-deep-dive/04/04-12-scale-rules-belong-to-the-revision-templ.ko.png)
Revision-scope scaling이기 때문에 이런 분리가 가능합니다.

---

## 무엇을 주장하면 안 되는가

여기서 꼭 지워야 할 오해가 두 가지 있습니다.

첫째, ACA HTTP scaling이 upstream KEDA HTTP add-on과 같은 것이라고 단정하면 안 됩니다.
개념적 친척 관계는 맞습니다.
구현이 1:1이라는 주장은 소스가 보장하지 않습니다.

둘째, KEDA가 HPA를 대체한다고 말하면 안 됩니다.
Upstream KEDA source는 KEDA가 HPA 동작을 관리하고 먹인다는 점을 분명히 보여 줍니다.
ACA도 이 모양을 개념적으로 상속합니다.

이 두 교정만 해도 설명의 정확도가 크게 올라갑니다.

---

## autoscaling 전체 그림을 한 장으로

![Autoscaling 전체 구조](../../../assets/azure-aca-deep-dive/04/04-13-the-whole-autoscaling-picture-in-one-dia.ko.png)
이 그림만 기억해도 ACA autoscaling 내부는 충분히 올바른 해상도로 머릿속에 남습니다.

---

## 4화 정리

압축하면 다음과 같습니다.

> Azure Container Apps에서 scale rule은 플랫폼이 KEDA 기반 autoscaling 동작으로 번역하는 제품 설정입니다. 그 결과 KEDA는 한 Revision에 대해 HPA류 control loop를 만들고, trigger 상태·concurrency·external metric을 replica 수로 바꿉니다. `minReplicas`가 0이면 scale-to-zero도 그 루프 안에 포함됩니다.

Scale 블레이드 뒤에 숨어 있는 기계가 바로 이것입니다.

---

## 시리즈 안에서의 위치

3화가 Revision이 어떻게 traffic을 받는지 설명했다면, 이번 4화는 같은 Revision이 아래에서 replica를 어떻게 늘리고 줄이는지 설명한 글입니다. 다음 5화에서는 ACA의 다른 대표적 숨은 메커니즘인 Dapr sidecar로 넘어가, injector부터 localhost API까지 따라갑니다. 마지막 6화에서는 Envoy 요청 경로로 돌아와, 이번 화의 scaling 결정과 3화의 routing 결정이 실제 요청 경로에서 어떻게 만나는지 보게 됩니다.

---

<!-- toc:begin -->
## 시리즈 목차

- [ACA 아키텍처 — 사용자에게 보이지 않는 Kubernetes 위에 얹은 것](./01-aca-architecture.md)
- [Environment 내부 — 네트워크·관측·Dapr 스코프의 경계](./02-environment-internals.md)
- [Revision과 트래픽 분할 — Envoy 가중치는 어디에서 오는가](./03-revision-and-traffic-split.md)
- **ACA 안의 KEDA — Scale Rule이 만드는 것 (현재 글)**
- Dapr 사이드카 내부 — 컨테이너 옆에 뜨는 Go 프로세스 (예정)
- Envoy Ingress 경로 — 첫 요청이 사용자 컨테이너에 닿기까지 (예정)

<!-- toc:end -->

---

## 참고 자료

### 1차 출처
- [`kedacore/keda` tree at `v2.14.0`](https://github.com/kedacore/keda/tree/v2.14.0)
- [KEDA의 `ScaledObject` 타입](https://github.com/kedacore/keda/blob/v2.14.0/apis/keda/v1alpha1/scaledobject_types.go)
- [KEDA의 `ScaledObjectReconciler`](https://github.com/kedacore/keda/blob/v2.14.0/controllers/keda/scaledobject_controller.go)
- [KEDA의 HPA 생성 코드](https://github.com/kedacore/keda/blob/v2.14.0/controllers/keda/hpa.go)

### 2차 출처
- [Scaling in Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/scale-app)
- [Update and deploy changes in Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/revisions)

### 관련 시리즈
- [Azure Container Apps 101](../../azure-aca-101/ko/)
- [Azure AKS Deep Dive](../../azure-aks-deep-dive/ko/)
- [Azure Functions Deep Dive](../../azure-functions-deep-dive/ko/)

Tags: Container Apps, KEDA, Dapr, Envoy
