<!-- tags: AKS, Kubernetes, Distributed Systems, Containers -->
# CNI와 Azure CNI Overlay — Pod IP가 어디서 오는가

> Azure Kubernetes Service Deep Dive 시리즈 (3/6)

Pod IP는 네트워킹 모드에 따라 다른 주소 모델에서 옵니다.
Azure CNI 전통 모드에서는 Pod가 VNet IP를 직접 소비합니다.
Azure CNI Overlay에서는 Pod IP가 별도 overlay CIDR에서 오고,
VNet 쪽에는 주로 노드 IP가 보입니다.

---

## 두 모델을 먼저 나란히 보기

![두 모델을 먼저 나란히 보기](../../assets/azure-aks-deep-dive/03/03-01-put-both-models-side-by-side.ko.png)
---

## CNI가 하는 일

CNI는 Pod sandbox에 네트워크를 붙이는 계약입니다.
인터페이스 생성,
IP 할당,
라우팅과 규칙 설치가 이 단계에서 일어납니다.
즉 2화의 `RunPodSandbox`와 3화의 Pod IP 이야기는 분리된 주제가 아닙니다.

---

## Azure CNI와 Overlay의 차이

전통 Azure CNI는 네트워크 모델이 직관적이지만 IP 소비가 큽니다.
Overlay는 Pod IP를 non-routable overlay 대역에서 가져오고,
VNet 리소스로 나갈 때 node-side NAT를 사용합니다.
그래서 node subnet과 Pod CIDR을 분리해서 설계할 수 있습니다.

![Azure CNI와 Overlay의 차이](../../assets/azure-aks-deep-dive/03/03-02-azure-cni-versus-overlay.ko.png)
---

## kubenet의 위치

AKS 문서는 kubenet retirement 일정을 분명히 적고 있습니다.
따라서 새 설계에서 kubenet을 장기 기본값처럼 두는 것은 위험합니다.
AKS의 공식 방향은 Azure CNI Overlay로 이동하는 쪽에 더 가깝습니다.

---

## 이번 화의 요점

> Azure CNI 전통 모드에서는 Pod가 VNet IP를 직접 받기 때문에 모델이 단순하지만 주소 소비가 큽니다. Azure CNI Overlay에서는 Pod IP가 별도 overlay 대역에서 오고, VNet 쪽에는 노드 IP로 NAT되어 나가기 때문에 주소 효율이 좋고 장기 운영에도 유리합니다.

---

## 시리즈 안에서의 위치

이 글은 Azure Kubernetes Service Deep Dive 시리즈 3화입니다.
2화가 노드 로컬 실행 경로를 따라갔다면, 이번 화는 그 실행 경로 옆에서 CNI가 Pod 네트워크를 어떻게 붙이는지 설명합니다. 다음 4화에서는 scheduler가 어떤 기준으로 노드를 고르는지 다룹니다.

---

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
- [Azure CNI Overlay](https://learn.microsoft.com/en-us/azure/aks/azure-cni-overlay)
- [Configure kubenet networking in AKS](https://learn.microsoft.com/en-us/azure/aks/configure-kubenet)
- [Update Azure CNI IPAM mode and data plane technology](https://learn.microsoft.com/en-us/azure/aks/update-azure-cni)

### 관련 시리즈
- [Azure AKS 101](../../azure-aks-101/ko/)
- [Azure Functions Deep Dive 1화 — 큰 그림 먼저 보기](../../azure-functions-deep-dive/ko/01-host-bootstrap.md)
