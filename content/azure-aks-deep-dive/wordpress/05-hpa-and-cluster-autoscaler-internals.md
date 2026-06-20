---
title: "바이브코딩을 위한 Azure AKS 심화 (5/6): HPA와 Cluster Autoscaler 내부"
series: azure-aks-deep-dive
episode: 5
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- AzureAKS심화
- HPA
- ClusterAutoscaler
- AI코딩
seo_description: "바이브코딩을 위한 Azure AKS 심화 5편: HPA와 Cluster Autoscaler 내부. 두 개의 독립 제어 루프(HPA=복제본, CA=노드)가 어떻게 순서대로 동작하며 구조적 지연이 왜 발생하는지 이해합니다."
---

# 바이브코딩을 위한 Azure AKS 심화 (5/6): HPA와 Cluster Autoscaler 내부

이 글은 바이브코딩을 위한 Azure AKS 심화 시리즈의 5번째 글입니다.

트래픽이 늘었는데 새 Pod가 바로 Ready가 되지 않으면 많은 팀이 "autoscaling이 느리다"라고 말합니다. 하지만 그 표현 안에는 사실 두 개의 서로 다른 루프가 숨어 있습니다. HPA는 메트릭을 보고 복제본 수를 조정합니다. Cluster Autoscaler는 Pending Pod를 보고 노드 수를 조정합니다. 두 루프는 입력도 다르고, 반응 시간도 다르고, 결정 단위도 다릅니다. HPA가 먼저 실행되어 새 Pod를 만들어도, 기존 노드에 여유가 없으면 그 Pod는 Pending 상태로 대기합니다. Cluster Autoscaler는 그 Pending Pod를 신호로 받아서야 비로소 노드 추가를 시작합니다. 이 순서를 모르면 "CA가 늦게 반응했다"는 현상을 HPA 설정 문제로 오해하거나, 반대로 HPA 스케일업이 늦었다고 CA를 탓하게 됩니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI에게 AKS autoscaling 설정 코드를 요청할 때 두 루프를 구분하지 않으면, HPA와 CA를 연결된 단일 시스템으로 잘못 설계하거나 루프 간 지연을 없애려는 잘못된 튜닝 코드가 생성되기 때문입니다.

> HPA와 Cluster Autoscaler의 핵심은 두 루프가 독립적으로 동작한다는 점과, HPA 스케일업 → Pending Pod → CA 노드 추가라는 순서 구조를 이해하는 데 있습니다.

---

## 이 글에서 다룰 문제

- HPA와 Cluster Autoscaler는 각각 무엇을 입력으로 받고 무엇을 조정할까요?
- 두 루프 사이에 구조적 지연이 발생하는 이유는 무엇이고, 이것이 버그가 아닌 이유는 무엇일까요?
- HPA가 scaleDown을 결정하면 CA는 언제 노드를 회수할까요?
- CA가 노드를 추가하지 않는 경우와 HPA가 반응하지 않는 경우를 어떻게 구분할까요?
- 이 개념을 실무에 적용하는 방법은 무엇일까요?

HPA와 Cluster Autoscaler 내부를 이해하면 AI에게 "HPA scaleUp 이후 CA 노드 추가까지의 지연이 구조적으로 정상인 이유와, 두 루프를 각각 독립적으로 튜닝하는 minReplicas/maxReplicas/scaleDown delay/CA expander 설정 YAML"을 정확하게 요청할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "AKS autoscaling이 느린데 빠르게 해줘"
→ HPA와 CA를 하나의 시스템으로 가정
→ CA 반응 시간을 HPA 설정으로 해결 시도
→ 두 루프의 입력 차이 미고려
→ 구조적 지연을 설정 오류로 오해
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "HPA와 CA 두 루프를 각각 튜닝해줘.
    HPA 루프:
    - metrics: CPU utilization 60%
    - minReplicas: 2, maxReplicas: 20
    - scaleDown.stabilizationWindowSeconds: 300
    CA 루프:
    - scaleDownDelayAfterAdd: 10m (노드 추가 후 회수 유예)
    - expander: least-waste
    두 루프 간 구조적 지연(HPA 스케일업 → Pending →
    CA 노드 추가)은 정상이므로 별도 대응 없음.
    각 루프 Pending/Events 진단 KQL 포함"
→ 두 루프를 독립적으로 튜닝
→ 구조적 지연을 버그로 취급하지 않음
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| HPA와 CA를 연결된 단일 시스템으로 가정 | 두 루프는 입력, 반응 시간, 결정 단위가 다름 | HPA=복제본 루프, CA=노드 루프로 분리해서 설계 |
| CA 지연을 HPA 설정 문제로 수정 | HPA scaleUp → Pending → CA 순서는 구조적 정상 | CA 지연은 scaleDownDelayAfterAdd, expander로 별도 튜닝 |
| scaleDown 유예 시간 미설정 | HPA가 너무 빠르게 복제본을 줄여 CA가 노드를 빨리 회수 | HPA stabilizationWindowSeconds와 CA scaleDownDelay 함께 설정 |
| CA가 노드를 추가하지 않는 원인을 HPA에서 탐색 | CA 입력은 Pending Pod, HPA 입력은 메트릭으로 다름 | kubectl describe pod에서 Pending 이유 확인 후 CA 로그 확인 |
| PodDisruptionBudget 없이 CA 운영 | CA node drain 시 서비스 중단 | PodDisruptionBudget으로 최소 가용 Pod 수 보장 |

## AI 협업 팁

HPA와 CA 설정 관련 효과적인 AI 프롬프트 패턴:

1. **HPA 설정 요청**: "AKS Deployment에 CPU 60% 기준 HPA를 설정하는 YAML 작성해줘. minReplicas 2, maxReplicas 20, scaleDown stabilizationWindow 5분 포함"
2. **CA 튜닝 요청**: "AKS Cluster Autoscaler에서 scaleDownDelayAfterAdd 10분, least-waste expander로 설정하는 az CLI 명령 작성해줘"
3. **루프 진단 요청**: "HPA scaleUp 후 CA가 노드를 추가하지 않는 경우 kubectl describe pod Events와 CA 로그에서 원인을 찾는 방법 설명해줘"

예시 프롬프트:
> "AKS HPA와 CA 튜닝 설정을 작성해줘. HPA: CPU 60%, minReplicas 2, maxReplicas 20, scaleDown stabilizationWindow 300s. CA: scaleDownDelayAfterAdd 10m, least-waste expander, PodDisruptionBudget minAvailable 2 포함. 두 루프 간 구조적 지연은 정상 동작으로 간주."

## 운영 체크리스트

- [ ] HPA와 CA를 독립 루프로 이해하고 각각 튜닝했는가?
- [ ] HPA scaleDown stabilizationWindowSeconds를 설정했는가?
- [ ] CA scaleDownDelayAfterAdd로 노드 조기 회수를 방지했는가?
- [ ] PodDisruptionBudget으로 CA drain 시 최소 가용 Pod를 보장했는가?
- [ ] 다음 글에서 KEDA가 HPA 위에서 어떻게 동작하는지 이해할 준비가 됐는가?

## 처음 질문으로 돌아가기

HPA와 Cluster Autoscaler 내부를 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. 두 루프의 입력과 결정 단위를 구분한 사람과 그렇지 않은 사람이 AI에게 받는 autoscaling 설정 코드의 완성도는 크게 다릅니다.

## 정리

HPA와 Cluster Autoscaler 편은 바이브코딩을 위한 Azure AKS 심화에서 두 스케일링 루프의 구조를 이해하는 핵심 단계입니다. HPA=복제본 루프, CA=노드 루프의 독립성, HPA 스케일업 → Pending → CA 순서의 구조적 정상성을 이해했습니다. 다음 글에서는 KEDA가 HPA 위에서 어떻게 ScaledObject를 생성하고 0↔1 경계를 관리하는지 다룹니다.

## 참고 자료

- [Horizontal Pod Autoscaler](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [Cluster Autoscaler in AKS](https://docs.microsoft.com/azure/aks/cluster-autoscaler)
- [CA FAQ](https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/FAQ.md)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-aks-deep-dive/ko/05-hpa-and-cluster-autoscaler-internals)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Azure AKS 심화 (1/6): Control Plane 해부
- 바이브코딩을 위한 Azure AKS 심화 (2/6): kubelet과 containerd
- 바이브코딩을 위한 Azure AKS 심화 (3/6): CNI와 Azure CNI Overlay
- 바이브코딩을 위한 Azure AKS 심화 (4/6): Scheduler와 Pod 배치
- **바이브코딩을 위한 Azure AKS 심화 (5/6): HPA와 Cluster Autoscaler 내부 (현재 글)**
- 바이브코딩을 위한 Azure AKS 심화 (6/6): KEDA 내부
<!-- toc:end -->

Tags: 바이브코딩, AzureAKS심화, HPA, AI코딩
