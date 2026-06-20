---
title: "바이브코딩을 위한 Azure AKS 심화 (3/6): CNI와 Azure CNI Overlay"
series: azure-aks-deep-dive
episode: 3
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- AzureAKS심화
- CNI
- AzureCNI
- AI코딩
seo_description: "바이브코딩을 위한 Azure AKS 심화 3편: CNI와 Azure CNI Overlay. Pod IP가 어디서 오는지, kubenet/Azure CNI/Azure CNI Overlay의 IP 소비와 라우팅 차이를 이해합니다."
---

# 바이브코딩을 위한 Azure AKS 심화 (3/6): CNI와 Azure CNI Overlay

이 글은 바이브코딩을 위한 Azure AKS 심화 시리즈의 3번째 글입니다.

AKS 네트워킹은 "Azure CNI냐 아니냐" 정도로만 말하면 중요한 차이가 거의 다 사라집니다. 실제 운영 질문은 훨씬 더 구체적입니다. Pod가 어느 주소 공간에서 IP를 받는지, VNet의 희소한 IP를 무엇이 소비하는지, 클러스터 밖으로 나가는 트래픽이 어떤 경로로 SNAT되는지를 먼저 갈라서 봐야 합니다. 특히 2026년 기준 AKS에서는 kubenet, Azure CNI Pod Subnet, Azure CNI Node Subnet, Azure CNI Overlay를 서로 다른 모델로 봐야 합니다. Azure CNI Overlay는 Pod에 가상 IP를 할당해 VNet IP를 절약하므로 대규모 클러스터에서 IP 고갈 문제를 줄입니다. 클러스터 생성 단계에서 CNI 모델을 한 번 결정하면 변경이 어렵습니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI에게 AKS 클러스터 네트워크 설계 코드를 요청할 때 CNI 모델을 명시하지 않으면, 기본값인 kubenet을 선택해 대규모 클러스터에서 IP 고갈과 UDR 관리 복잡도가 생기는 코드가 생성되기 때문입니다.

> CNI와 Azure CNI Overlay의 핵심은 Pod IP가 실제 VNet 공간을 소비하는지(Azure CNI), 아니면 가상 overlay 주소를 사용하는지(Overlay)의 차이와 그 운영 trade-off를 이해하는 데 있습니다.

---

## 이 글에서 다룰 문제

- kubenet, Azure CNI Pod Subnet, Azure CNI Node Subnet, Azure CNI Overlay는 IP 소비와 라우팅 면에서 무엇이 다를까요?
- Pod IP가 실제 VNet 공간을 직접 소비할 때 어떤 운영 한계가 가장 먼저 드러날까요?
- Overlay 모드에서 Pod에서 외부로 나가는 트래픽이 어떤 SNAT 경로를 거칠까요?
- NetworkPolicy가 각 CNI 모델에서 어떻게 다르게 동작할까요?
- 이 개념을 실무에 적용하는 방법은 무엇일까요?

CNI와 Azure CNI Overlay를 이해하면 AI에게 "Azure CNI Overlay로 AKS 클러스터 생성 시 podCidr 설정, VNet 서브넷 크기 계획, 외부 트래픽 SNAT 경로 설명을 포함한 Bicep 코드"를 정확하게 요청할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "AKS 네트워크 설정해줘"
→ 기본값 kubenet 사용
→ 대규모 클러스터에서 IP 고갈 위험
→ UDR 관리 복잡도 미고려
→ CNI 모델 변경 불가 나중에 발견
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "AKS CNI를 Azure CNI Overlay로 설계해줘.
    이유: VNet IP를 노드당 1개만 소비(Pod는 가상 IP)
    설정:
    - networkPlugin: azure
    - networkPluginMode: overlay
    - podCidr: 192.168.0.0/16 (VNet과 분리)
    - serviceCidr: 10.0.0.0/16
    외부 트래픽: SNAT through node IP 설명 포함
    az aks create 명령과 Bicep 코드 작성해줘"
→ VNet IP 절약
→ IP 고갈 방지 설계
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| 기본값 kubenet 선택 후 클러스터 확장 | 노드 수 증가 시 UDR 관리 복잡, 노드당 30 Pod IP 한계 | 새 클러스터는 Azure CNI Overlay 검토 |
| CNI 모델을 클러스터 생성 후 변경 시도 | CNI 모델 변경 불가, 클러스터 재생성 필요 | 클러스터 생성 단계에서 CNI 모델 결정 |
| Pod IP와 VNet IP를 같은 공간으로 계획 | Azure CNI(non-Overlay)에서 Pod IP가 VNet 소비 | Overlay 모드로 Pod 주소 공간 분리 |
| NetworkPolicy 없이 클러스터 운영 | Pod 간 불필요한 통신 허용 | Calico 또는 Azure NetworkPolicy 적용 |
| SNAT 경로를 고려하지 않은 방화벽 설계 | 외부 트래픽 source IP가 node IP로 변환됨 | 방화벽에서 node IP 대역 허용 |

## AI 협업 팁

CNI 설계 관련 효과적인 AI 프롬프트 패턴:

1. **Azure CNI Overlay 클러스터 생성 요청**: "Azure CNI Overlay 모드로 AKS 클러스터를 만드는 az aks create 명령과 Bicep 코드 작성해줘"
2. **IP 계획 요청**: "Azure CNI Overlay 기준 VNet 서브넷 크기, podCidr, serviceCidr를 노드 100개, Pod 10000개 규모로 계획해줘"
3. **NetworkPolicy 설정 요청**: "AKS에서 Calico NetworkPolicy로 orders Pod가 payments Pod에만 접근하도록 제한하는 YAML 작성해줘"

예시 프롬프트:
> "AKS 네트워크를 Azure CNI Overlay로 설계해줘. 노드 50개, Pod 최대 5000개 기준. VNet /16, 노드 서브넷 /24, podCidr 192.168.0.0/16, serviceCidr 10.0.0.0/16. Calico NetworkPolicy 활성화. az aks create 명령과 Bicep 포함."

## 운영 체크리스트

- [ ] 클러스터 생성 전 CNI 모델을 결정했는가 (변경 불가)?
- [ ] Azure CNI Overlay로 VNet IP 소비를 최소화했는가?
- [ ] Pod CIDR와 VNet CIDR가 겹치지 않는가?
- [ ] NetworkPolicy로 Pod 간 통신을 제한하는가?
- [ ] 다음 글에서 Scheduler와 Pod 배치를 이해할 준비가 됐는가?

## 처음 질문으로 돌아가기

CNI와 Azure CNI Overlay를 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. CNI 모델과 IP 계획을 명시한 사람과 그렇지 않은 사람이 AI에게 받는 AKS 네트워크 설계 코드의 완성도는 크게 다릅니다.

## 정리

CNI와 Azure CNI Overlay 편은 바이브코딩을 위한 Azure AKS 심화에서 Pod IP 출처와 네트워크 모델을 이해하는 핵심 단계입니다. kubenet/Azure CNI/Azure CNI Overlay의 IP 소비 차이, Overlay 모드의 SNAT 경로를 이해했습니다. 다음 글에서는 Scheduler가 Pod를 어느 노드에 배치하는지 다룹니다.

## 참고 자료

- [Azure CNI Overlay in AKS](https://docs.microsoft.com/azure/aks/azure-cni-overlay)
- [AKS networking concepts](https://docs.microsoft.com/azure/aks/concepts-network)
- [NetworkPolicy in AKS](https://docs.microsoft.com/azure/aks/use-network-policies)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-aks-deep-dive/ko/03-cni-and-azure-cni-overlay)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Azure AKS 심화 (1/6): Control Plane 해부
- 바이브코딩을 위한 Azure AKS 심화 (2/6): kubelet과 containerd
- **바이브코딩을 위한 Azure AKS 심화 (3/6): CNI와 Azure CNI Overlay (현재 글)**
- 바이브코딩을 위한 Azure AKS 심화 (4/6): Scheduler와 Pod 배치
- 바이브코딩을 위한 Azure AKS 심화 (5/6): HPA와 Cluster Autoscaler 내부
- 바이브코딩을 위한 Azure AKS 심화 (6/6): KEDA 내부
<!-- toc:end -->

Tags: 바이브코딩, AzureAKS심화, CNI, AI코딩
