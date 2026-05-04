---
title: kubelet과 containerd — 노드 위에서 컨테이너가 뜨기까지
series: azure-aks-deep-dive
episode: 2
language: ko
status: publish-ready
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
seo_description: 이 글의 외부 인용은 다음 upstream 버전을 기준으로 합니다.
---

# kubelet과 containerd — 노드 위에서 컨테이너가 뜨기까지

## Source Version

이 글의 외부 인용은 다음 upstream 버전을 기준으로 합니다.
- Kubernetes: v1.30.x (https://github.com/kubernetes/kubernetes)
- containerd: v1.7.x (https://github.com/containerd/containerd)
- KEDA: v2.13.x (https://github.com/kedacore/keda)

AKS의 control plane은 Microsoft가 관리하므로, 여기서 보는 upstream 코드는 실제 서비스 내부 바이너리 단정이 아니라 동작 모델 비교 기준입니다.

> Azure Kubernetes Service Deep Dive 시리즈 (2/6)

1화에서 control plane은 Pod를 어느 노드에 둘지 결정하고 Binding을 기록하는 층이라고 정리했습니다.
이번 화는 그다음입니다.
실행은 누가 맡는가.
답은 노드의 `kubelet`과 container runtime입니다.
AKS에서는 Linux 노드 기준으로 `containerd`가 기본 runtime이고,
Docker는 여기서 주인공이 아닙니다.

실제 경로는 이렇게 흐릅니다.
API server에서 PodSpec을 본 kubelet이,
Unix socket으로 CRI를 호출하고,
containerd가 sandbox와 container를 만들고,
마지막에는 `runc`가 실제 프로세스를 띄웁니다.

---

## 이 글에서 답할 질문

- kubelet은 정확히 어떤 주기로 무엇을 폴링하고, 그 주기는 어떻게 튜닝되는가?
- containerd로의 전환 이후 docker 명령은 왜 사라졌고, 디버깅은 어떻게 바뀌었는가?
- image pull은 노드 단위로 캐시되는가, 풀시 누가 인증하는가?
- PodSpec의 resources.requests와 limits는 kubelet eviction 결정과 어떻게 만나는가?
- kubelet이 unhealthy로 빠지는 가장 흔한 원인 세 가지는 무엇이고, 어떤 메트릭에서 보이는가?

## 한 장으로 보는 실행 경로

![API server에서 runc까지 이어지는 실행 경로](../../../assets/azure-aks-deep-dive/02/02-01-the-execution-path-in-one-picture.ko.png)
이 다이어그램이 이번 화 전체입니다.
앞의 절반은 kubelet의 책임이고,
뒤의 절반은 runtime 계층의 책임입니다.

---

## kubelet은 무엇을 하는 프로세스인가

kubelet은 노드의 에이전트입니다.
control plane이 결정한 desired state를 노드에서 실제 상태로 바꾸는 주체입니다.
API server를 watch해서 자기 노드에 배정된 Pod를 보고,
볼륨을 준비하고,
secret과 config를 주입하고,
CRI를 호출해 sandbox와 container를 띄웁니다.

중요한 점이 하나 있습니다.
kubelet은 직접 컨테이너 엔진을 구현하지 않습니다.
대신 CRI라는 추상 인터페이스 뒤에 runtime을 둡니다.
그 덕분에 kubelet은 "무엇을 실행할지"에 집중하고,
runtime은 "어떻게 실행할지"에 집중합니다.

---

## CRI는 왜 필요한가

Kubernetes가 특정 엔진 구현에 묶이지 않기 위해서입니다.
CRI는 kubelet과 runtime 사이의 계약입니다.
업스트림 `api.proto`를 보면 runtime service와 image service가 분리돼 있습니다.

- `RunPodSandbox`
- `CreateContainer`
- `StartContainer`
- `StopContainer`
- `PullImage`

이 메서드 이름만 봐도 책임 분할이 보입니다.
Pod 수준의 네트워크 namespace와 sandbox를 먼저 만들고,
그 안에 컨테이너를 만들어 넣는 구조입니다.

---

## kubelet은 Unix socket으로 CRI를 부른다

AKS Linux 노드에서 kubelet과 containerd는 같은 노드 안에 있습니다.
그래서 통신은 네트워크 RPC라기보다 로컬 Unix socket RPC에 가깝습니다.
실무적으로는 "kubelet이 containerd 소켓으로 CRI를 호출한다"고 이해하면 됩니다.

![kubelet과 containerd를 잇는 로컬 CRI 호출 경로](../../../assets/azure-aks-deep-dive/02/02-02-kubelet-talks-to-a-unix-socket.ko.png)
이 그림은 2화에서 가장 기억할 구조입니다.
control plane은 여기까지 내려오지 않습니다.
노드 안의 로컬 호출 사슬입니다.

---

## `RunPodSandbox`가 먼저인 이유

컨테이너보다 sandbox가 먼저 만들어집니다.
이 sandbox는 Pod의 공유 namespace와 네트워크 문맥을 담는 바깥 상자입니다.
Pod IP는 보통 이 sandbox가 준비되는 시점과 연결됩니다.

업스트림 `kuberuntime_sandbox.go`의 `createPodSandbox()`는 kubelet이 `PodSandboxConfig`를 만든 뒤 `RunPodSandbox`를 호출하는 경로를 보여 줍니다.
이 함수 안에는 hostname,
log directory,
port mapping,
linux security context,
namespace 옵션 같은 Pod 수준 설정이 들어갑니다.

---

## 이미지 pull과 container start

`kuberuntime_container.go`의 `startContainer()`는 먼저 image pull을 수행하고,
그다음 config를 만들고,
`CreateContainer`, `StartContainer`를 순서대로 호출합니다.
이 순서 때문에 Pending,
ContainerCreating,
ImagePullBackOff,
CrashLoopBackOff를 다른 층의 증상으로 나눠 읽을 수 있습니다.

---

## `runc`는 어디에서 등장하는가

kubelet은 `runc`를 직접 부르지 않습니다.
containerd가 OCI runtime 계층으로 내려가면서 `runc`를 사용합니다.
즉 호출 사슬은 대체로 kubelet -> CRI -> containerd -> `runc` -> process 순서입니다.

---

## Pod 생성 경로를 코드 기준으로 다시 쓰면

![Pod 시작 순서를 따라가는 kubelet 제어 흐름](../../../assets/azure-aks-deep-dive/02/02-03-startup-path-as-control-flow.ko.png)
---

## 이번 화의 요점

> AKS에서 노드 위 컨테이너 실행은 kubelet이 주도합니다. kubelet은 API server에서 자기 노드의 PodSpec을 보고, Unix socket으로 CRI를 호출해 먼저 `RunPodSandbox`를 실행하고, 이어서 `PullImage`, `CreateContainer`, `StartContainer`를 순서대로 요청합니다. 실제 프로세스 생성은 containerd 아래의 OCI runtime, 보통 `runc`가 맡습니다.

---

## 시리즈 안에서의 위치

이 글은 Azure Kubernetes Service Deep Dive 시리즈 2화입니다.
1화가 관리형 control plane의 경계를 그렸다면 이번 화는 그 반대편 끝, 즉 노드 로컬 실행 경로를 따라갑니다. 다음 3화에서는 오늘 본 `RunPodSandbox`와 자연스럽게 이어지는 네트워킹 계층으로 넘어가서 Pod IP가 실제로 어디서 오는지 정리합니다.

---

## Call Path Summary

- kubelet → CRI gRPC
- CRI runtime endpoint → containerd
- containerd → `containerd-shim`
- `containerd-shim` → `runc`
- `runc` → container process

### kubelet/containerd 상태 진단 (노드 디버그 컨테이너)

```bash
kubectl debug node/aks-nodepool1-12345 -it \
  --image=mcr.microsoft.com/cbl-mariner/busybox:2.0 -- chroot /host

# inside the node
systemctl status kubelet
journalctl -u kubelet --since '15 min ago' | tail -50
crictl ps -a | head
crictl images | grep my-app
```

## 운영 체크리스트

- [ ] node-level disk pressure / memory pressure 알림을 켰다
- [ ] kubelet의 image GC 정책과 disk quota를 노드 SKU에 맞춰 설정했다
- [ ] private registry 인증 방식(MI vs imagePullSecret)을 결정했다
- [ ] containerd snapshotter 변경의 영향도를 검토했다
- [ ] 노드 디버깅을 위한 kubectl debug 권한과 ephemeral container 정책을 정리했다

<!-- toc:begin -->
## 시리즈 목차

- [Control Plane 해부 — AKS가 사용자에게서 가린 것](./01-control-plane-anatomy.md)
- **kubelet과 containerd — 노드 위에서 컨테이너가 뜨기까지 (현재 글)**
- CNI와 Azure CNI Overlay — Pod IP가 어디서 오는가 (예정)
- Scheduler와 Pod 배치 — 어느 노드로 갈지 누가 정하는가 (예정)
- HPA와 Cluster Autoscaler 내부 — 두 컨트롤 루프 (예정)
- KEDA 내부 — ScaledObject가 HPA를 만드는 방식 (예정)

<!-- toc:end -->

---

## 참고 자료

### 1차 출처
- [CRI API — `api.proto` @ `v1.30.0`](https://github.com/kubernetes/kubernetes/blob/v1.30.0/staging/src/k8s.io/cri-api/pkg/apis/runtime/v1/api.proto)
- [`kuberuntime_manager.go` @ `v1.30.0`](https://github.com/kubernetes/kubernetes/blob/v1.30.0/pkg/kubelet/kuberuntime/kuberuntime_manager.go)
- [`kuberuntime_sandbox.go` @ `v1.30.0`](https://github.com/kubernetes/kubernetes/blob/v1.30.0/pkg/kubelet/kuberuntime/kuberuntime_sandbox.go)
- [`kuberuntime_container.go` @ `v1.30.0`](https://github.com/kubernetes/kubernetes/blob/v1.30.0/pkg/kubelet/kuberuntime/kuberuntime_container.go)

### 2차 출처
- [AKS core concepts](https://learn.microsoft.com/en-us/azure/aks/core-aks-concepts)
- [Kubernetes node components](https://kubernetes.io/docs/concepts/overview/components/#node-components)

### 관련 시리즈
- [Azure AKS 101](../../azure-aks-101/ko/)
- [Azure Functions Deep Dive 3화 — 단일 RPC 채널 관점](../../azure-functions-deep-dive/ko/03-grpc-event-stream.md)

Tags: AKS, Kubernetes, Distributed Systems, Containers
