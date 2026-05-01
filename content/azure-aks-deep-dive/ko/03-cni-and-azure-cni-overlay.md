---
title: CNI와 Azure CNI Overlay — Pod IP가 어디서 오는가
series: azure-aks-deep-dive
episode: 3
language: ko
status: ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- AKS
- Kubernetes
- Distributed Systems
- Containers
last_reviewed: '2026-04-29'
---

# CNI와 Azure CNI Overlay — Pod IP가 어디서 오는가

## Source Version

이 글의 외부 인용은 다음 upstream 버전을 기준으로 합니다.
- Kubernetes: v1.30.x (https://github.com/kubernetes/kubernetes)
- containerd: v1.7.x (https://github.com/containerd/containerd)
- KEDA: v2.13.x (https://github.com/kedacore/keda)

AKS의 control plane은 Microsoft가 관리하므로, 여기서 보는 upstream 코드는 실제 서비스 내부 바이너리 단정이 아니라 동작 모델 비교 기준입니다.

> Azure Kubernetes Service Deep Dive 시리즈 (3/6)

Pod IP는 네트워킹 모드에 따라 다른 주소 모델에서 옵니다.
이제는 이것을 뭉뚱그려 "Azure CNI"라고만 부르면 오해가 생깁니다.
새 flat 네트워킹 기준점인 Azure CNI Pod Subnet,
구형 flat 모델인 Azure CNI Node Subnet,
그리고 Pod IP를 별도 overlay CIDR에 두는 Azure CNI Overlay를 나눠서 봐야 합니다.

---

## 세 모델을 먼저 나란히 보기

![세 가지 AKS 네트워크 모델 비교 구조](../../../assets/azure-aks-deep-dive/03/03-01-put-both-models-side-by-side.ko.png)
---

## CNI가 하는 일

CNI는 Pod sandbox에 네트워크를 붙이는 계약입니다.
인터페이스 생성,
IP 할당,
라우팅과 규칙 설치가 이 단계에서 일어납니다.
즉 2화의 `RunPodSandbox`와 3화의 Pod IP 이야기는 분리된 주제가 아닙니다.

---

## Azure CNI Pod Subnet, Node Subnet, Overlay의 차이

2026년 기준으로 실무 비교는 다음 세 줄이 핵심입니다.

- **Azure CNI Pod Subnet**: Pod는 전용 pod subnet에서 VNet-routable IP를 받고, 노드는 별도 node subnet에 남습니다. node 주소 계획과 pod 주소 계획을 분리할 수 있어서 flat 모델 중에서는 가장 깔끔합니다.
- **Azure CNI Node Subnet(legacy)**: Pod와 노드가 같은 node subnet에서 IP를 같이 씁니다. 모델은 단순하지만 IP 고갈 압박이 가장 빨리 옵니다.
- **Azure CNI Overlay**: Pod는 기본 `10.244.0.0/16` 같은 overlay CIDR에서 IP를 받고, 노드는 일반 VNet subnet에 남습니다. 클러스터 밖으로 나갈 때는 node IP 기준 SNAT가 걸립니다.

Pod Subnet과 Node Subnet은 Pod IP가 VNet 공간에 있기 때문에 연결된 네트워크에서 Pod를 직접 보는 모델입니다. Overlay는 VNet IP 절약에는 가장 유리하지만, 클러스터 간에 native Pod IP로 직접 라우팅하는 모델은 아닙니다.

![세 AKS 네트워크 모델의 IP 경로 차이](../../../assets/azure-aks-deep-dive/03/03-02-azure-cni-versus-overlay.ko.png)
---

## kubenet의 위치

AKS 문서는 kubenet retirement 일정을 분명히 적고 있습니다.
따라서 새 설계에서 kubenet을 장기 기본값처럼 두는 것은 위험합니다.
AKS의 공식 방향은 Azure CNI Overlay로 이동하는 쪽에 더 가깝습니다.

---

## 이번 화의 요점

> 이제 AKS 네트워킹은 세 갈래로 봐야 합니다. Azure CNI Pod Subnet은 Pod 전용 subnet을 쓰는 현재 flat 모델이고, Azure CNI Node Subnet은 Pod와 노드가 같은 subnet을 태우는 legacy flat 모델입니다. Azure CNI Overlay는 Pod를 별도 overlay CIDR에 두어 VNet IP를 가장 아끼지만, native Pod IP를 클러스터 밖에서 직접 라우팅하는 모델은 아닙니다.

---

## 시리즈 안에서의 위치

이 글은 Azure Kubernetes Service Deep Dive 시리즈 3화입니다.
2화가 노드 로컬 실행 경로를 따라갔다면, 이번 화는 그 실행 경로 옆에서 CNI가 Pod 네트워크를 어떻게 붙이는지 설명합니다. 이 구분이 있어야 노드 실행 문제와 Pod 주소 할당 문제를 같은 장애 영역으로 섞어 읽지 않게 됩니다.

---

## Call Path Summary

- kubelet `RunPodSandbox` → CNI plugin 호출
- CNI plugin → interface 생성, IPAM 할당, route/rule 프로그래밍
- Pod sandbox가 Pod IP를 가진 network-ready 상태가 됨
- 이후 트래픽은 모드에 따라 VNet pod subnet으로 직접 나가거나 overlay에서 node IP로 SNAT되어 나감

<!-- blog-only:start -->
다음 글: [Scheduler와 Pod 배치 — 어느 노드로 갈지 누가 정하는가](./04-scheduler-and-pod-placement.md)
<!-- blog-only:end -->

<!-- toc:begin -->
## 시리즈 목차

- [Control Plane 해부 — AKS가 사용자에게서 가린 것](./01-control-plane-anatomy.md)
- [kubelet과 containerd — 노드 위에서 컨테이너가 뜨기까지](./02-kubelet-and-containerd.md)
- **CNI와 Azure CNI Overlay — Pod IP가 어디서 오는가 (현재 글)**
- Scheduler와 Pod 배치 — 어느 노드로 갈지 누가 정하는가 (예정)
- HPA와 Cluster Autoscaler 내부 — 두 컨트롤 루프 (예정)
- KEDA 내부 — ScaledObject가 HPA를 만드는 방식 (예정)

<!-- toc:end -->

---

## 참고 자료

### 1차 출처
- [CRI API 네트워크 상태 필드 — `api.proto` @ `v1.30.0`](https://github.com/kubernetes/kubernetes/blob/v1.30.0/staging/src/k8s.io/cri-api/pkg/apis/runtime/v1/api.proto)
- [`kuberuntime_sandbox.go` @ `v1.30.0`](https://github.com/kubernetes/kubernetes/blob/v1.30.0/pkg/kubelet/kuberuntime/kuberuntime_sandbox.go)

### 2차 출처
- [Azure CNI Pod Subnet](https://learn.microsoft.com/en-us/azure/aks/concepts-network-azure-cni-pod-subnet)
- [Azure CNI Overlay](https://learn.microsoft.com/en-us/azure/aks/azure-cni-overlay)
- [Concepts - CNI Networking in AKS](https://learn.microsoft.com/en-us/azure/aks/concepts-network-cni-overview)
- [Configure kubenet networking in AKS](https://learn.microsoft.com/en-us/azure/aks/configure-kubenet)
- [Update Azure CNI IPAM mode and data plane technology](https://learn.microsoft.com/en-us/azure/aks/update-azure-cni)

### 관련 시리즈
- [Azure AKS 101](../../azure-aks-101/ko/)
- [Azure Functions Deep Dive 1화 — 큰 그림 먼저 보기](../../azure-functions-deep-dive/ko/01-host-bootstrap.md)

Tags: AKS, Kubernetes, Distributed Systems, Containers
