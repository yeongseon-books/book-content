---
title: "바이브코딩을 위한 Azure AKS 심화 (4/6): Scheduler와 Pod 배치"
series: azure-aks-deep-dive
episode: 4
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- AzureAKS심화
- Scheduler
- Pod배치
- AI코딩
seo_description: "바이브코딩을 위한 Azure AKS 심화 4편: Scheduler와 Pod 배치. kube-scheduler가 노드 후보를 좁히는 3단계(Filter, Score, Bind)와 배치 실패 진단 방법을 이해합니다."
---

# 바이브코딩을 위한 Azure AKS 심화 (4/6): Scheduler와 Pod 배치

이 글은 바이브코딩을 위한 Azure AKS 심화 시리즈의 4번째 글입니다.

Pending Pod를 보면 많은 팀이 가장 먼저 노드 상태나 container runtime 로그부터 떠올립니다. 하지만 실제로는 그보다 더 앞단의 결정이 먼저 끝나야 합니다. kube-scheduler가 제약 조건을 계산해 가능한 후보를 좁히고, 최종 Binding을 기록해야만 node-local 실행 경로가 시작될 수 있기 때문입니다. 스케줄링은 단순한 잔여 CPU 계산이 아닙니다. node affinity, taint와 toleration, topology spread, 볼륨 제약, 포트 충돌, 우선순위와 preemption이 모두 같은 판단 안으로 들어옵니다. Pending이라는 동일한 결과 뒤에는 완전히 다른 배치 실패 이유가 숨어 있을 수 있습니다. scheduler를 "Pod를 실행하는 컴포넌트"가 아니라 "노드 선택과 Binding 기록을 담당하는 control-plane 루프"로 읽어야 합니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI에게 Pod 배치 설정 코드를 요청할 때 nodeSelector, affinity, taint/toleration의 역할 차이를 명시하지 않으면, 모든 제약을 nodeSelector로 설정해 Fine-grained 배치 제어가 안 되는 코드가 생성되기 때문입니다.

> Scheduler와 Pod 배치의 핵심은 Filter(후보 노드 선별) → Score(우선순위) → Bind(배치 확정) 3단계 구조와 배치 실패 진단 순서를 이해하는 데 있습니다.

---

## 이 글에서 다룰 문제

- kube-scheduler는 하나의 Pod에 대해 어떤 단계로 노드 후보를 좁혀 갈까요?
- nodeSelector, affinity, taint/toleration, topology spread는 서로 어떤 다른 의도를 표현할까요?
- Filter에서 모두 탈락한 경우와 Binding 실패를 어떻게 구분할까요?
- Cluster Autoscaler는 scheduler가 Pending Pod를 만든 뒤 어떻게 연동될까요?
- 이 개념을 실무에 적용하는 방법은 무엇일까요?

Scheduler와 Pod 배치를 이해하면 AI에게 "GPU 워크로드를 gpu node pool에만 배치하고 일반 워크로드와 topology spread로 균등 분산하는 affinity/taint/toleration YAML과 Pending Pod Events에서 배치 실패 원인을 읽는 방법"을 정확하게 요청할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "Pod를 특정 노드에만 배치해줘"
→ nodeSelector만 사용
→ 선호도(soft) vs 필수(hard) 구분 없음
→ taint/toleration 미사용
→ topology spread 없어 노드 편중 발생
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "Pod 배치 전략을 세 단계로 구현해줘.
    1) GPU 워크로드: requiredDuringScheduling affinity로
       agentpool=gpupool 노드에만 배치 (hard)
    2) GPU node pool에 NoSchedule taint 설정,
       GPU Pod에만 toleration 추가
    3) 일반 워크로드: topology spread
       (maxSkew 1, topologyKey kubernetes.io/hostname)로 균등 분산
    Pending Pod Events에서 배치 실패 원인 읽는 KQL도 포함"
→ hard/soft 배치 제약 분리
→ taint로 노드 오염 방지
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| nodeSelector만 사용 | 선호도(soft) 표현 불가, 라벨 변경 시 취약 | affinity의 required/preferred 조합 사용 |
| taint 없이 GPU node pool 운영 | 일반 Pod가 GPU 노드로 배치될 수 있음 | GPU node에 NoSchedule taint, GPU Pod에 toleration |
| topology spread 미설정 | Pod가 특정 노드에 편중, 단일 노드 장애 영향 큼 | topologySpreadConstraints로 균등 분산 |
| Pending Pod를 container runtime 문제로 가정 | scheduler 단계가 아직 안 끝난 것일 수 있음 | kubectl describe pod Events에서 "cannot be scheduled" 확인 |
| PodDisruptionBudget 없이 topology spread 설정 | node 유지보수 시 서비스 중단 | PodDisruptionBudget으로 최소 가용 Pod 수 보장 |

## AI 협업 팁

Pod 배치 설정 관련 효과적인 AI 프롬프트 패턴:

1. **GPU node 배치 요청**: "GPU 워크로드 Pod에 GPU node pool affinity와 toleration을 설정하는 YAML 작성해줘. GPU node에는 NoSchedule taint 추가."
2. **topology spread 요청**: "FastAPI Deployment가 AZ와 node에 균등 분산되도록 topologySpreadConstraints YAML 작성해줘"
3. **배치 실패 진단 요청**: "kubectl describe pod Events에서 scheduler 배치 실패 메시지를 읽고 원인을 분류하는 방법 설명해줘"

예시 프롬프트:
> "AKS Pod 배치 전략 YAML을 작성해줘. GPU Pod: agentpool=gpupool affinity(required) + Nvidia taint toleration. 일반 API Pod: topology spread(AZ와 hostname 균등 분산, maxSkew 1). PodDisruptionBudget: minAvailable 2."

## 운영 체크리스트

- [ ] GPU/특수 노드에 taint를 설정하고 해당 Pod에만 toleration을 추가했는가?
- [ ] topology spread로 Pod가 AZ와 노드에 균등 분산되는가?
- [ ] Pending Pod Events에서 scheduler 배치 실패 원인을 읽을 수 있는가?
- [ ] PodDisruptionBudget으로 최소 가용 Pod 수를 보장했는가?
- [ ] 다음 글에서 HPA와 Cluster Autoscaler 내부를 이해할 준비가 됐는가?

## 처음 질문으로 돌아가기

Scheduler와 Pod 배치를 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. Filter/Score/Bind 단계와 affinity/taint/topology spread의 역할을 명시한 사람과 그렇지 않은 사람이 AI에게 받는 Pod 배치 YAML의 완성도는 크게 다릅니다.

## 정리

Scheduler와 Pod 배치 편은 바이브코딩을 위한 Azure AKS 심화에서 Pod 배치 결정 과정을 이해하는 핵심 단계입니다. Filter→Score→Bind 3단계 구조, nodeSelector/affinity/taint/topology spread의 역할 차이, 배치 실패 진단 방법을 이해했습니다. 다음 글에서는 HPA와 Cluster Autoscaler의 두 제어 루프를 다룹니다.

## 참고 자료

- [Kubernetes scheduler](https://kubernetes.io/docs/concepts/scheduling-eviction/kube-scheduler/)
- [Taints and tolerations](https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/)
- [Topology spread constraints](https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-aks-deep-dive/ko/04-scheduler-and-pod-placement)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Azure AKS 심화 (1/6): Control Plane 해부
- 바이브코딩을 위한 Azure AKS 심화 (2/6): kubelet과 containerd
- 바이브코딩을 위한 Azure AKS 심화 (3/6): CNI와 Azure CNI Overlay
- **바이브코딩을 위한 Azure AKS 심화 (4/6): Scheduler와 Pod 배치 (현재 글)**
- 바이브코딩을 위한 Azure AKS 심화 (5/6): HPA와 Cluster Autoscaler 내부
- 바이브코딩을 위한 Azure AKS 심화 (6/6): KEDA 내부
<!-- toc:end -->

Tags: 바이브코딩, AzureAKS심화, Scheduler, AI코딩
