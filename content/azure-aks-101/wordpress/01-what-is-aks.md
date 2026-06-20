---
title: "바이브코딩을 위한 Azure AKS (1/7): Azure Kubernetes Service란?"
series: azure-aks-101
episode: 1
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- AzureAKS
- Kubernetes
- 관리형K8s
- AI코딩
seo_description: "바이브코딩을 위한 Azure AKS 1편: Azure Kubernetes Service란? Azure가 무엇을 대신 관리하고 사용자가 여전히 책임져야 하는 부분이 무엇인지 이해합니다."
---

# 바이브코딩을 위한 Azure AKS (1/7): Azure Kubernetes Service란?

이 글은 바이브코딩을 위한 Azure AKS 시리즈의 첫 번째 글입니다.

컨테이너 몇 개를 띄우는 일 자체는 이제 특별하지 않습니다. 어려운 지점은 그다음입니다. 장애가 난 Pod를 다시 살리고, 트래픽이 늘면 복제본과 노드를 함께 늘리고, 외부 요청을 안전하게 받아 주고, 로그와 메트릭을 한곳에 모아 운영 판단까지 내려야 비로소 플랫폼이 됩니다. Kubernetes는 바로 그 운영 문제를 표준화한 시스템입니다. AKS는 "Azure가 무엇을 대신 맡고 사용자는 무엇을 계속 책임져야 하는지"를 명확하게 분리하는 것이 핵심입니다. Azure가 관리하는 것: Control Plane(etcd, API server, scheduler), 업그레이드 지원. 사용자가 관리하는 것: Node Pool VM, 워크로드 YAML, Ingress, 스케일링 정책, 관측성. AKS 비용에서 클러스터 자체(Control Plane)는 무료이고, 실제 비용은 Node Pool VM, 네트워킹, 스토리지에서 발생합니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI에게 AKS 설정 코드를 요청할 때 책임 경계를 명시하지 않으면, Control Plane 설정과 Node Pool 설정을 혼동하거나 비용 구조를 잘못 이해한 코드가 생성되기 때문입니다.

> AKS의 핵심은 Azure가 관리하는 Control Plane과 사용자가 관리하는 Node Pool의 책임 경계를 이해하는 데 있습니다.

---

## 이 글에서 다룰 문제

- AKS는 self-managed Kubernetes와 비교할 때 무엇을 대신 운영해 줄까요?
- 관리형 Kubernetes라도 왜 kubectl, YAML, Service, Ingress를 이해해야 할까요?
- AKS 비용은 어디에서 발생하고 "클러스터 요금"보다 무엇이 더 중요할까요?
- AKS, ACA, App Service 중 언제 AKS를 선택해야 할까요?
- 이 개념을 실무에 적용하는 방법은 무엇일까요?

AKS 책임 경계를 이해하면 AI에게 "AKS 클러스터에서 system node pool과 user node pool을 분리하고 Control Plane 관리는 Azure에 위임하는 Bicep 코드와 클러스터 비용 구조 설명"을 정확하게 요청할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "Kubernetes 앱을 Azure에 올리는 코드 작성해줘"
→ Control Plane 설정과 Node 설정 혼동
→ 비용이 어디서 나오는지 불명확
→ system pool과 user pool 구분 없음
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "AKS 클러스터를 운영 관점으로 설계해줘.
    Control Plane(etcd, API server): Azure 관리
    system node pool: 클러스터 시스템 컴포넌트 전용
    user node pool: 워크로드 실행용 (VM 크기, 노드 수 명시)
    비용 구조: Control Plane 무료, Node VM 비용 추정 포함
    az aks create 명령으로 작성해줘"
→ 책임 경계 명확한 클러스터 설계
→ 비용 구조 이해 포함
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| Control Plane 비용을 예산에 포함 | AKS Control Plane은 무료 | Node VM, 네트워킹, 스토리지 비용 계획 |
| AKS를 ACA 대체재로 혼동 | 운영 복잡도와 자유도가 다름 | K8s 네이티브 기능 필요 시 AKS, 컨테이너 관리 간소화는 ACA |
| 관리형 = 운영 없음으로 오해 | Node Pool, 업그레이드, 스케일링은 사용자 책임 | AKS 책임 경계 명확히 이해 필요 |
| kubectl 없이 AKS 운영 시도 | AKS는 kubectl과 YAML로 운영 | az aks get-credentials로 kubectl 연결 필수 |
| system pool에 워크로드 배포 | system pool은 클러스터 컴포넌트 전용 | user node pool 별도 생성 후 워크로드 배포 |

## AI 협업 팁

AKS 기본 이해 관련 효과적인 AI 프롬프트 패턴:

1. **클러스터 생성 요청**: "AKS 클러스터를 system pool과 user pool 분리해서 만드는 az aks create 명령 작성해줘. 비용 구조 설명 포함."
2. **책임 경계 설명 요청**: "AKS에서 Azure가 관리하는 부분과 사용자가 관리해야 하는 부분을 표로 정리해줘"
3. **플랫폼 선택 요청**: "컨테이너 워크로드에서 AKS vs ACA vs App Service 선택 기준을 운영 복잡도와 제어 수준으로 설명해줘"

예시 프롬프트:
> "AKS 클러스터를 처음 설계해줘. system node pool(클러스터 전용, Standard_D2s_v3 x3), user node pool(워크로드용, Standard_D4s_v3, min 2 max 10 Cluster Autoscaler), kubectl 연결 명령, 월 예상 비용 구조 포함."

## 운영 체크리스트

- [ ] AKS Control Plane이 Azure 관리임을 이해했는가?
- [ ] Node Pool VM 비용이 주요 비용 항목임을 알고 있는가?
- [ ] system pool과 user pool을 분리해서 만들 계획인가?
- [ ] kubectl과 YAML로 운영할 준비가 됐는가?
- [ ] 다음 글에서 클러스터 아키텍처를 이해할 준비가 됐는가?

## 처음 질문으로 돌아가기

AKS 기본 개념을 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. 책임 경계와 비용 구조를 명시한 사람과 그렇지 않은 사람이 AI에게 받는 AKS 클러스터 설계 코드의 완성도는 크게 다릅니다.

## 정리

Azure Kubernetes Service란? 편은 바이브코딩을 위한 Azure AKS 시리즈의 시작 단계입니다. Azure가 관리하는 Control Plane과 사용자가 관리하는 Node Pool의 책임 경계, 그리고 AKS 비용 구조를 이해했습니다. 다음 글에서는 클러스터 아키텍처의 Control Plane과 Node Pool 구조를 다룹니다.

## 참고 자료

- [Azure Kubernetes Service overview](https://docs.microsoft.com/azure/aks/intro-kubernetes)
- [AKS pricing](https://azure.microsoft.com/pricing/details/kubernetes-service/)
- [Compare container options in Azure](https://docs.microsoft.com/azure/container-apps/compare-options)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-aks-101/ko/01-what-is-aks)

---

<!-- toc:begin -->
## 시리즈 목차

- **바이브코딩을 위한 Azure AKS (1/7): Azure Kubernetes Service란? (현재 글)**
- 바이브코딩을 위한 Azure AKS (2/7): 클러스터 아키텍처
- 바이브코딩을 위한 Azure AKS (3/7): 첫 클러스터 만들고 앱 배포하기
- 바이브코딩을 위한 Azure AKS (4/7): Pod, Deployment, Service
- 바이브코딩을 위한 Azure AKS (5/7): 네트워킹과 Ingress
- 바이브코딩을 위한 Azure AKS (6/7): 스케일링
- 바이브코딩을 위한 Azure AKS (7/7): 모니터링과 운영
<!-- toc:end -->

Tags: 바이브코딩, AzureAKS, Kubernetes, AI코딩
