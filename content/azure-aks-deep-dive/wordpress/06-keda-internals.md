---
title: "바이브코딩을 위한 Azure AKS 심화 (6/6): KEDA 내부"
series: azure-aks-deep-dive
episode: 6
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- AzureAKS심화
- KEDA
- ScaledObject
- AI코딩
seo_description: "바이브코딩을 위한 Azure AKS 심화 6편: KEDA 내부. KEDA가 ScaledObject를 통해 HPA를 생성하고 0에서 1로의 확장 경계를 직접 관리하는 구조를 이해합니다."
---

# 바이브코딩을 위한 Azure AKS 심화 (6/6): KEDA 내부

이 글은 바이브코딩을 위한 Azure AKS 심화 시리즈의 마지막 글입니다.

KEDA를 "HPA 대신 쓰는 스케일러"라고 부르는 설명은 가장 중요한 구조를 놓칩니다. KEDA는 HPA를 대체하지 않습니다. KEDA는 HPA 위에 앉아 있습니다. ScaledObject를 정의하면 KEDA operator가 그에 대응하는 HPA 오브젝트를 클러스터 안에 생성합니다. 외부 메트릭(Service Bus 큐 길이, Kafka offset lag 등)을 HPA가 이해할 수 있는 형태로 변환하는 것이 KEDA Metrics Adapter의 역할입니다. HPA는 그 변환된 메트릭을 읽고 평소처럼 복제본 수를 조정합니다. 단, 0↔1 경계는 HPA가 다룰 수 없는 영역입니다. HPA는 0을 최솟값으로 허용하지 않기 때문입니다. KEDA가 이 경계를 직접 관리합니다. ScaledObject에 minReplicaCount: 0을 설정하면, 메트릭이 없을 때 KEDA가 직접 Deployment를 0으로 내리고, 메트릭이 들어오면 1로 올린 뒤 HPA에게 제어권을 넘깁니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI에게 KEDA 설정 코드를 요청할 때 ScaledObject와 생성된 HPA의 관계, 0↔1 경계 관리를 명시하지 않으면, KEDA와 HPA를 중복 설정하거나 scale-to-zero가 동작하지 않는 코드가 생성되기 때문입니다.

> KEDA 내부의 핵심은 ScaledObject → 생성된 HPA → Metrics Adapter 경로와, 0↔1 경계는 KEDA가 직접 관리한다는 구조를 이해하는 데 있습니다.

---

## 이 글에서 다룰 문제

- KEDA ScaledObject를 정의하면 클러스터 안에 무슨 일이 일어날까요?
- KEDA Metrics Adapter는 왜 필요하고 어떤 역할을 할까요?
- 0↔1 경계에서 KEDA와 HPA는 각각 무엇을 담당할까요?
- ScaledObject와 별도로 HPA를 직접 만들면 어떤 충돌이 생길까요?
- 이 개념을 실무에 적용하는 방법은 무엇일까요?

KEDA 내부를 이해하면 AI에게 "Azure Service Bus 큐 길이 기반 ScaledObject YAML, minReplicaCount 0으로 scale-to-zero, KEDA가 생성한 HPA와 충돌하지 않도록 별도 HPA 생성 금지 명시"를 정확하게 요청할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "KEDA로 Service Bus 큐 기반 스케일링 설정해줘"
→ ScaledObject와 HPA 중복 생성
→ minReplicaCount: 0 설정 후 scale-to-zero 미동작
→ KEDA Metrics Adapter 역할 미이해
→ 0→1 경계 실패 시 원인 추적 불가
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "KEDA ScaledObject로 Service Bus 스케일링 설정해줘.
    구조: ScaledObject → KEDA가 HPA 자동 생성
    (별도 HPA 생성 금지)
    설정:
    - trigger: azure-servicebus
    - queueLength: 10 (큐 메시지 10개당 Pod 1개)
    - minReplicaCount: 0 (scale-to-zero 활성화)
    - maxReplicaCount: 20
    0→1 경계: KEDA 직접 관리
    1→N 경계: KEDA가 생성한 HPA가 관리
    ScaledObject 상태 확인 kubectl 명령 포함"
→ ScaledObject만 정의, 생성된 HPA 충돌 없음
→ scale-to-zero 정상 동작
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| ScaledObject와 HPA 중복 생성 | KEDA가 만든 HPA와 사용자 HPA 충돌 | ScaledObject만 정의, HPA는 KEDA가 자동 생성 |
| KEDA가 HPA를 대체한다고 가정 | KEDA는 HPA 위에서 동작, HPA 제거 불가 | ScaledObject → 생성된 HPA 구조 이해 |
| minReplicaCount: 0 설정 후 scale-to-zero 미동작 | KEDA operator가 0↔1 경계를 직접 관리하는 구조 미이해 | KEDA operator 로그에서 scale-to-zero 이벤트 확인 |
| 외부 메트릭 직접 HPA에 연결 시도 | HPA는 external metric type을 Metrics Adapter 없이 읽지 못함 | KEDA Metrics Adapter가 변환 역할 담당 |
| ScaledObject 삭제 후 HPA가 남는 문제 | KEDA가 생성한 HPA는 ScaledObject와 수명이 연동됨 | ScaledObject 삭제 시 생성된 HPA 자동 삭제 확인 |

## AI 협업 팁

KEDA 설정 관련 효과적인 AI 프롬프트 패턴:

1. **ScaledObject 생성 요청**: "Azure Service Bus 큐 기반 KEDA ScaledObject YAML 작성해줘. queueLength 10, minReplicaCount 0, maxReplicaCount 20, scale-to-zero 활성화"
2. **생성된 HPA 확인 요청**: "KEDA ScaledObject 적용 후 자동 생성된 HPA를 kubectl로 확인하는 명령과 ScaledObject 상태 확인 명령 작성해줘"
3. **scale-to-zero 진단 요청**: "KEDA scale-to-zero가 동작하지 않을 때 ScaledObject Events와 KEDA operator 로그에서 원인을 찾는 방법 설명해줘"

예시 프롬프트:
> "KEDA로 Azure Service Bus 큐 기반 scale-to-zero 설정을 작성해줘. ScaledObject만 정의(별도 HPA 생성 금지). trigger: azure-servicebus, queueLength 10, minReplicaCount 0, maxReplicaCount 20. KEDA가 생성한 HPA 확인 명령과 ScaledObject 상태 확인 kubectl 명령 포함."

## 운영 체크리스트

- [ ] ScaledObject만 정의하고 별도 HPA를 생성하지 않았는가?
- [ ] KEDA가 생성한 HPA를 kubectl get hpa로 확인했는가?
- [ ] minReplicaCount: 0으로 scale-to-zero를 설정했는가?
- [ ] ScaledObject 삭제 시 생성된 HPA도 함께 삭제되는지 확인했는가?
- [ ] KEDA Metrics Adapter가 외부 메트릭을 HPA에 올바르게 전달하는지 확인했는가?

## 처음 질문으로 돌아가기

KEDA 내부를 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. ScaledObject와 생성된 HPA의 관계, 0↔1 경계 관리를 명시한 사람과 그렇지 않은 사람이 AI에게 받는 KEDA 설정 코드의 완성도는 크게 다릅니다.

## 정리

KEDA 내부 편은 바이브코딩을 위한 Azure AKS 심화 시리즈의 마지막 단계입니다. ScaledObject → 생성된 HPA → Metrics Adapter 경로, 0↔1 경계의 KEDA 직접 관리 구조를 이해했습니다. 이 시리즈에서 배운 Control Plane 해부, kubelet 실행 사슬, CNI 모델, Scheduler, HPA/CA 루프, KEDA 내부 구조를 명시해서 AI에게 요청하면 훨씬 완성도 높은 AKS 운영 코드를 얻을 수 있습니다.

## 참고 자료

- [KEDA documentation](https://keda.sh/docs/)
- [KEDA scalers](https://keda.sh/docs/scalers/)
- [KEDA with AKS](https://docs.microsoft.com/azure/aks/keda-about)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-aks-deep-dive/ko/06-keda-internals)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Azure AKS 심화 (1/6): Control Plane 해부
- 바이브코딩을 위한 Azure AKS 심화 (2/6): kubelet과 containerd
- 바이브코딩을 위한 Azure AKS 심화 (3/6): CNI와 Azure CNI Overlay
- 바이브코딩을 위한 Azure AKS 심화 (4/6): Scheduler와 Pod 배치
- 바이브코딩을 위한 Azure AKS 심화 (5/6): HPA와 Cluster Autoscaler 내부
- **바이브코딩을 위한 Azure AKS 심화 (6/6): KEDA 내부 (현재 글)**
<!-- toc:end -->

Tags: 바이브코딩, AzureAKS심화, KEDA, AI코딩
