---
title: "바이브코딩을 위한 Azure AKS (2/7): 클러스터 아키텍처"
series: azure-aks-101
episode: 2
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- AzureAKS
- ControlPlane
- NodePool
- AI코딩
seo_description: "바이브코딩을 위한 Azure AKS 2편: 클러스터 아키텍처. Control Plane(두뇌)과 Node Pool(실행 공간)을 분리하고 system pool과 user pool을 나눠야 하는 이유를 이해합니다."
---

# 바이브코딩을 위한 Azure AKS (2/7): 클러스터 아키텍처

이 글은 바이브코딩을 위한 Azure AKS 시리즈의 2번째 글입니다.

AKS를 이해할 때 가장 먼저 분리해야 하는 것은 클러스터의 두뇌와 실제 실행 공간입니다. 이 둘을 섞어서 보면 업그레이드, 장애 범위, 비용, 스케일링이 모두 흐려집니다. Control Plane(API server, scheduler, controller manager, etcd)은 Azure가 관리하고 사용자는 직접 접근하지 않습니다. Node Pool은 사용자가 VM 크기, 노드 수, 업그레이드 정책을 결정하고 워크로드가 실제로 실행되는 공간입니다. system node pool과 user node pool을 분리해야 하는 실무적 이유가 있습니다. system pool에 워크로드를 같이 두면 클러스터 컴포넌트(CoreDNS, kube-proxy 등)와 경쟁하다가 예측 불가능한 장애가 생깁니다. API server 쪽 문제인지 노드 쪽 문제인지 구분하는 것만으로도 원인 분석 속도가 크게 달라집니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI에게 AKS 클러스터 설계 코드를 요청할 때 system pool과 user pool 분리를 명시하지 않으면, 클러스터 컴포넌트와 워크로드가 같은 노드에서 충돌하는 코드가 생성되기 때문입니다.

> 클러스터 아키텍처의 핵심은 Control Plane과 Node Pool의 경계, system pool과 user pool의 분리를 이해하는 데 있습니다.

---

## 이 글에서 다룰 문제

- API server, scheduler, controller manager, etcd는 각각 어떤 일을 할까요?
- Node Pool은 단순한 VM 묶음 이상으로 왜 중요한 관리 단위일까요?
- system node pool과 user node pool을 분리해야 하는 실무적 이유는 무엇일까요?
- Control Plane 장애와 Node Pool 장애는 어떻게 구분할까요?
- 이 개념을 실무에 적용하는 방법은 무엇일까요?

클러스터 아키텍처를 이해하면 AI에게 "system pool(Standard_D2s_v3 x3, 클러스터 전용)과 user pool(Standard_D4s_v3, min 2 max 10)을 분리 생성하고 user pool에 NoSchedule taint를 설정하지 않아도 system 컴포넌트가 user pool로 가지 않게 하는 방법"을 정확하게 요청할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "AKS 클러스터 노드 설정해줘"
→ system pool과 user pool 구분 없음
→ 클러스터 컴포넌트와 워크로드 같은 노드
→ 업그레이드 시 워크로드 중단 위험
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "AKS 클러스터를 system/user pool 분리로 설계해줘.
    system pool: Standard_D2s_v3 3노드,
      클러스터 컴포넌트(CoreDNS, kube-proxy) 전용
    user pool: Standard_D4s_v3, 2~10노드, Cluster Autoscaler 활성화
      모드=User (워크로드 전용)
    업그레이드 시 user pool을 먼저 drain하는 전략 포함"
→ system/user 완전 분리
→ 업그레이드 영향 범위 예측 가능
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| system pool에 워크로드 배포 | 클러스터 컴포넌트와 자원 경쟁 | user node pool 별도 생성 후 워크로드 배포 |
| node pool을 단순 VM 그룹으로 이해 | 업그레이드, 스케일링 관리 단위 누락 | node pool을 별도 관리 단위로 인식 |
| Control Plane API server 장애를 node 장애로 혼동 | 진단 방향 오류 | kubectl 응답 여부로 Control Plane 상태 먼저 확인 |
| single node pool로 모든 워크로드 혼재 | GPU, high-memory 등 특수 노드 분리 불가 | 워크로드 특성별 node pool 분리 |
| node pool 업그레이드를 전체 동시 진행 | 모든 워크로드 동시 중단 가능 | maxSurge, maxUnavailable으로 롤링 업그레이드 |

## AI 협업 팁

클러스터 아키텍처 관련 효과적인 AI 프롬프트 패턴:

1. **system/user pool 분리 요청**: "AKS system pool과 user pool을 분리해서 az aks create와 az aks nodepool add로 만드는 명령 작성해줘"
2. **Control Plane 진단 요청**: "AKS에서 API server 응답과 node 상태를 각각 확인하는 kubectl 명령 작성해줘"
3. **node pool 업그레이드 요청**: "AKS user node pool을 롤링 업그레이드하는 az aks nodepool upgrade 명령과 안전한 maxSurge 설정 작성해줘"

예시 프롬프트:
> "AKS 클러스터 아키텍처를 설계해줘. system pool: Standard_D2s_v3 3노드, 클러스터 전용. user pool: Standard_D4s_v3 min 2 max 10, Cluster Autoscaler 활성화, OS 업그레이드 mode=NodeImage. kubectl로 pool별 node 상태 확인 명령 포함."

## 운영 체크리스트

- [ ] system node pool과 user node pool을 분리해서 만들었는가?
- [ ] Control Plane 장애와 Node 장애 진단 방법을 구분하고 있는가?
- [ ] node pool 업그레이드 전략(maxSurge)을 설정했는가?
- [ ] 워크로드 특성별로 node pool을 분리할 계획이 있는가?
- [ ] 다음 글에서 첫 클러스터 배포 실습을 이해할 준비가 됐는가?

## 처음 질문으로 돌아가기

클러스터 아키텍처를 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. system/user pool 분리와 Control Plane 경계를 명시한 사람과 그렇지 않은 사람이 AI에게 받는 클러스터 설계 코드의 완성도는 크게 다릅니다.

## 정리

클러스터 아키텍처 편은 바이브코딩을 위한 Azure AKS에서 Control Plane과 Node Pool의 역할 분리를 이해하는 핵심 단계입니다. API server, scheduler, etcd의 역할과 system/user node pool 분리 이유를 이해했습니다. 다음 글에서는 실제 클러스터를 만들고 FastAPI 앱을 배포하는 실습을 다룹니다.

## 참고 자료

- [AKS cluster architecture](https://docs.microsoft.com/azure/aks/concepts-clusters-workloads)
- [Node pools in AKS](https://docs.microsoft.com/azure/aks/use-multiple-node-pools)
- [AKS upgrade best practices](https://docs.microsoft.com/azure/aks/upgrade-cluster)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-aks-101/ko/02-cluster-architecture)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Azure AKS (1/7): Azure Kubernetes Service란?
- **바이브코딩을 위한 Azure AKS (2/7): 클러스터 아키텍처 (현재 글)**
- 바이브코딩을 위한 Azure AKS (3/7): 첫 클러스터 만들고 앱 배포하기
- 바이브코딩을 위한 Azure AKS (4/7): Pod, Deployment, Service
- 바이브코딩을 위한 Azure AKS (5/7): 네트워킹과 Ingress
- 바이브코딩을 위한 Azure AKS (6/7): 스케일링
- 바이브코딩을 위한 Azure AKS (7/7): 모니터링과 운영
<!-- toc:end -->

Tags: 바이브코딩, AzureAKS, ControlPlane, AI코딩
