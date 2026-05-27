---
title: "Azure Kubernetes Service Deep Dive (1/6): Control Plane 해부 — AKS가 사용자에게서 가린 것"
series: azure-aks-deep-dive
episode: 1
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- AKS
- Kubernetes
- Distributed Systems
- Containers
last_reviewed: '2026-05-12'
seo_description: AKS 관리형 컨트롤 플레인의 내부 구조와 API 서버의 역할을 해부하고, 운영자가 읽어야 할 핵심 표면을 정리합니다.
---

# Azure Kubernetes Service Deep Dive (1/6): Control Plane 해부 — AKS가 사용자에게서 가린 것

AKS를 관리형 Kubernetes라고 부르는 설명은 출발점으로는 충분합니다.
하지만 실제 운영 판단을 해야 하는 순간에는 그 문장이 너무 거칠게 느껴집니다.
지연이 control plane에서 시작된 것인지, node 쪽 실행 경로에서 시작된 것인지, 아니면 둘 사이의 상태 수렴 지점에서 생긴 것인지 분리해서 봐야 하기 때문입니다.

이 글은 Azure Kubernetes Service Deep Dive 시리즈의 첫 번째 글입니다.

AKS에서 특히 어려운 점은 control plane이 보이지 않는다는 사실입니다.
self-managed Kubernetes라면 `etcd` 백업 전략, `kube-apiserver` 플래그, scheduler 프로세스 상태를 직접 다루면서 감을 쌓을 수 있습니다.
반대로 AKS에서는 API endpoint, 객체 상태, 진단 로그, 그리고 AKS가 노출한 설정 표면만 가지고 내부를 추론해야 합니다.

그래서 이 글의 목적은 control plane을 더 추상적으로 설명하는 데 있지 않습니다.
오히려 control plane과 data plane의 경계를 먼저 고정하고, 그 위에서 이후 글들의 kubelet, CNI, scheduler, autoscaling 이야기가 정확히 어디에 걸리는지 보이게 만드는 데 있습니다.
이제 AKS에서 보이는 control plane과 보이지 않는 control plane을 같은 지도 위에 올려 보겠습니다.

![Azure Kubernetes Service Deep Dive 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/azure-aks-deep-dive/01/01-01-aks-control-vs-data-plane.ko.png)
*Azure Kubernetes Service Deep Dive 1장 흐름 개요*
> Control Plane 해부 — AKS가 사용자에게서 가린 것의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 먼저 던지는 질문

- AKS control plane은 정확히 어떤 컴포넌트로 이루어져 있고, 사용자는 그중 무엇을 직접 볼 수 있을까요?
- 관리형 control plane이라는 약속은 어디까지를 의미하고, 어디부터는 여전히 사용자의 운영 책임일까요?
- API server SLA를 읽을 때 왜 `etcd`, scheduler, controller-manager의 내부 구현보다 API 표면을 먼저 봐야 할까요?

## 왜 이 글이 중요한가

AKS 운영에서 가장 비싼 실수 중 하나는 control plane 문제와 node 문제를 같은 범주로 다루는 것입니다.
예를 들어 Pod가 Pending으로 오래 남았다고 해서 곧바로 kubelet 로그부터 보기 시작하면, scheduler 단계에서 이미 실패한 상황을 한참 뒤늦게 발견하게 됩니다.
반대로 API server 자체가 느린 상황을 node pool 확장 문제로 오해하면, 증상은 비슷해 보여도 대응 우선순위가 완전히 어긋납니다.

또 하나 중요한 이유는 AKS가 추론 중심의 운영 모델을 강제하기 때문입니다.
AKS에서는 control plane 프로세스에 로그인해 직접 보는 방식이 기본 경로가 아닙니다.
따라서 API 성공률, 객체 상태 변화, watch 지연, 진단 로그 같은 간접 신호를 읽는 습관이 없으면 관리형 서비스의 이점을 제대로 활용하기 어렵습니다.

마지막으로 이 글은 시리즈 전체의 기준 좌표를 잡습니다.
2화의 kubelet과 containerd, 3화의 CNI, 4화의 scheduler, 5화의 HPA와 Cluster Autoscaler, 6화의 KEDA는 모두 결국 control plane과 data plane 사이의 호출 경계 위에서 이해해야 연결됩니다.
첫 지도가 흐리면 뒤의 세부 설명도 계속 따로 놀게 됩니다.

## 핵심 관점

AKS control plane을 볼 때 가장 먼저 고정해야 할 문장은 이것입니다.
**사용자가 만나는 control plane은 거의 항상 API server 표면이고, 그 뒤에서 상태를 수렴시키는 루프는 대부분 Microsoft 관리 경계 안에 숨어 있습니다.**
이 구분이 있어야 같은 장애 증상을 보고도 어디까지는 관찰 가능하고 어디부터는 증상으로만 추론해야 하는지 정리됩니다.

이 관점이 중요한 이유는 AKS의 SLA와 운영 표면이 모두 API 중심으로 설계되어 있기 때문입니다.
사용자는 `kubectl`, GitOps controller, Terraform, Azure CLI 같은 도구로 API server와 대화합니다.
반면 `etcd` 배치, scheduler 인스턴스 수, controller-manager의 내부 가용성 구성은 일반적으로 서비스 내부 구현입니다.

즉 control plane을 잘 이해한다는 말은 보이지 않는 VM을 더 자세히 상상한다는 뜻이 아닙니다.
오히려 **API 요청이 성공하는가, 원하는 상태가 수렴하는가, 그리고 그 수렴이 어느 층에서 멈췄는가를 구분하는 능력**에 더 가깝습니다.

> AKS의 control plane은 “내가 직접 관리하지 않는 Kubernetes 핵심 컴포넌트 묶음”이지만, 운영자가 실제로 읽어야 하는 표면은 거의 언제나 API server와 그 뒤에 남는 상태 변화입니다.

## 핵심 개념

### control plane과 data plane의 경계를 먼저 고정해야 합니다

시리즈 전체의 기준점은 아래 그림입니다.
이번 글은 이 경계를 정의하고, 이후 글들은 각 박스를 하나씩 확대하는 방식으로 이어집니다.
control plane이 원하는 상태를 기록하고 조정하며, data plane이 실제 컨테이너를 실행한다는 선을 먼저 잡아 두면 뒤의 모든 설명이 훨씬 덜 헷갈립니다.

이 그림에서 `kube-apiserver`, `etcd`, `kube-controller-manager`, `kube-scheduler`는 control plane 쪽입니다.
반대로 `kubelet`, container runtime, CNI, 실제 Pod 프로세스는 node 쪽 data plane입니다.
AKS가 관리형이라고 해도 이 분리는 사라지지 않습니다.
다만 control plane 쪽 운영 책임과 가시성이 Microsoft 경계 안으로 더 깊게 들어갈 뿐입니다.

### AKS에서는 control plane 호스트가 아니라 API endpoint가 표면입니다

self-managed Kubernetes에서는 control plane 호스트를 직접 운영합니다.
`kube-apiserver` 플래그, 인증서 회전, `etcd` 백업, 장애 복구 전략을 직접 결정합니다.
AKS는 이 무거운 층을 관리형 서비스 내부로 밀어 넣고, 사용자에게는 API endpoint와 연결된 node pool 중심 표면을 제공합니다.

이 설계가 주는 장점은 분명합니다.
control plane 패치, 고가용성 구성, 핵심 컴포넌트 수명주기를 서비스가 대신 맡습니다.
대신 문제를 볼 때는 프로세스에 로그인해 직접 보는 대신 API 동작, 객체 상태, Azure 진단 로그, 그리고 AKS가 노출한 설정만으로 추론해야 합니다.

### SLA를 읽을 때 핵심 표면은 API server입니다

AKS 문서가 Standard, Premium tier와 Uptime SLA를 설명할 때 실제로 사용자가 체감하는 표면은 Kubernetes API server입니다.
이 말은 운영자가 느끼는 control plane 품질이 대체로 API 요청 성공률과 지연 시간으로 드러난다는 뜻입니다.
내부적으로 `etcd`가 어떻게 배치되어 있는지, scheduler가 몇 개 인스턴스로 동작하는지는 서비스 내부 구현이더라도, 그 결과는 결국 API 표면의 건강도로 간접 반영됩니다.

이 때문에 AKS 장애를 볼 때 첫 질문은 대개 같습니다.
API server가 죽었는가, 느린가, 아니면 살아 있지만 scheduler 혹은 reconciliation 루프가 뒤에서 밀리고 있는가입니다.
이 구분이 되면 원인 후보가 빠르게 줄어듭니다.

### 요청 한 번이 실제 실행으로 이어지는 경로를 이해해야 합니다

`kubectl apply -f deployment.yaml`은 겉으로는 한 번의 명령처럼 보이지만, control plane 안에서는 여러 단계를 거칩니다.
API server가 요청을 받고, 객체를 저장하고, controller가 후속 객체를 만들고, scheduler가 `Pod -> Node` 결정을 기록하고, 그 뒤에야 kubelet과 runtime이 노드에서 실제 실행을 시작합니다.
이 구조를 이해해야 “API는 성공했는데 왜 아직 컨테이너가 안 떴지?” 같은 질문에 정확하게 답할 수 있습니다.

![API 요청이 노드 실행으로 이어지는 경로](https://yeongseon-books.github.io/book-public-assets/assets/azure-aks-deep-dive/01/01-02-diagram.ko.png)

*API 요청이 노드 실행으로 이어지는 경로*

이 그림에서 중요한 점은 API server가 실행기가 아니라 조정자라는 사실입니다.
control plane은 원하는 상태를 기록하고 수렴시키는 층이고, 실제 컨테이너 시작은 node-local 경로에서 일어납니다.
이 선이 흐려지면 스케일링 문제, 배치 문제, 노드 문제를 잘못 섞어 읽게 됩니다.

### `kube-apiserver`는 모든 사용자가 반드시 거치는 control-plane 컴포넌트입니다

AKS 사용자가 control plane과 대화하는 경로는 거의 전부 API server를 통합니다.
`kubectl`, GitOps controller, Terraform, admission webhook, 내부 operator 모두 결국 API server에 객체를 읽고 씁니다.
즉 API server는 단순한 REST 프런트가 아니라 인증, 인가, admission, 객체 검증, watch fan-out을 모으는 중심축입니다.

운영적으로 기억할 포인트도 명확합니다.
API server 지연은 거의 모든 control plane 문제처럼 보일 수 있습니다.
반대로 API server가 건강하다면 상당수 문제는 scheduler, controller-manager, 또는 node 측 실행 경로로 내려가서 봐야 합니다.

### `etcd`는 보이지 않아도 계속 영향을 주는 상태 저장소입니다

Kubernetes는 결국 상태 저장소를 읽고 쓰는 분산 시스템입니다.
Deployment, Pod, Node, Lease, Secret 같은 객체는 모두 `etcd`를 거칩니다.
AKS에서는 사용자가 직접 `etcdctl`을 다루지 않는 경우가 대부분이지만, 그 영향은 API write latency, watch 지연, Lease 갱신 이상 같은 증상으로 계속 드러납니다.

즉 `etcd`를 직접 운용하지 않는다고 해서 그 존재를 잊어도 된다는 뜻은 아닙니다.
오히려 HPA, Cluster Autoscaler, scheduler, controller-manager를 모두 같은 패턴으로 읽으려면 “상태를 읽고, 판단하고, 다시 쓴다”는 감각이 먼저 필요합니다.

### `kube-controller-manager`는 원하는 상태로 수렴시키는 루프 묶음입니다

controller-manager는 하나의 기능이 아니라 수많은 컨트롤 루프 묶음입니다.
ReplicaSet controller, Node controller, endpoint 관련 루프, HPA controller까지 모두 현재 상태와 원하는 상태 사이의 차이를 계속 계산하고, 필요하면 API server에 다시 씁니다.
Kubernetes가 즉시 실행이 아니라 점진적 수렴으로 보이는 이유가 여기에 있습니다.

![desired state 수렴을 맡는 컨트롤 루프 구조](https://yeongseon-books.github.io/book-public-assets/assets/azure-aks-deep-dive/01/01-03-kube-controller-manager.ko.png)

*desired state 수렴을 맡는 컨트롤 루프 구조*

AKS에서는 controller-manager 프로세스를 직접 만지지 않더라도, 이 루프가 느려질 때 나타나는 현상은 충분히 체감합니다.
HPA 반응이 늦거나, 노드 상태 전이가 늦거나, 서비스 엔드포인트 반영이 지연될 때가 대표적입니다.
중요한 것은 “리소스를 만들었으니 끝”이 아니라 “어떤 루프가 그 변화를 관측하고 후속 상태를 써야 끝”이라는 모델입니다.

### `kube-scheduler`는 실행하지 않고 배치 결정을 기록합니다

scheduler의 역할은 Pod를 실제로 띄우는 것이 아닙니다.
`nodeName`이 없는 Pod를 보고, 불가능한 노드를 Filter로 제거하고, 가능한 후보를 Score로 정렬한 뒤, 선택 결과를 Binding으로 API server에 기록합니다.
즉 scheduler의 출력은 실행 중인 컨테이너가 아니라 `Pod -> Node` 매핑입니다.

이 구분은 Pending Pod를 해석할 때 특히 중요합니다.
배치 결정이 아직 없는 문제인지, 배치는 끝났지만 노드 실행이 늦는 문제인지, 아니면 그보다 앞단에서 API 자체가 흔들리는 문제인지 먼저 나눠야 하기 때문입니다.
이후 4화에서 이 배치 경로를 더 깊게 보게 됩니다.

### 이 글의 핵심 호출 경로는 아래 명령으로도 점검할 수 있습니다

아래 명령은 현재 AKS 클러스터의 control-plane 표면과 진단 설정을 빠르게 확인할 때 유용합니다.
특히 API server 접근 방식, SKU, auto-upgrade 프로필, diagnostic settings 같은 관리형 표면을 한 번에 점검할 수 있습니다.
관리형 control plane은 직접 접속보다 이런 표면 점검이 먼저라는 사실을 기억해 둘 만합니다.

```bash
az aks show -n my-cluster -g my-rg \
  --query "{kubernetes:kubernetesVersion, sku:sku, apiServer:apiServerAccessProfile, autoUpgrade:autoUpgradeProfile}"

az monitor diagnostic-settings list \
  --resource $(az aks show -n my-cluster -g my-rg --query id -o tsv) -o table
```

## 흔히 헷갈리는 지점

## control plane 운영 표면을 실제 객체로 고정하기

control plane을 추상 개념으로만 이해하면 장애 시점마다 같은 질문을 다시 하게 됩니다.
그래서 운영팀은 관찰 표면을 객체 단위로 고정해 두는 편이 좋습니다.
아래처럼 API 응답을 기준으로 “지금 내가 볼 수 있는 control-plane 표면”을 표준화하면, 사람마다 다른 감으로 판단하는 시간을 줄일 수 있습니다.

```bash
# 1) API 서버 연결성과 버전 확인
kubectl version --short

# 2) API 서버 readiness 표면 확인
kubectl get --raw='/readyz?verbose'

# 3) API 우선순위/공정성으로 인한 지연 의심 시
kubectl get --raw='/metrics' | grep apiserver_request_duration_seconds_bucket | head -5
```

예시 출력은 다음과 같이 읽습니다.

```text
Client Version: v1.30.2
Kustomize Version: v5.0.4
Server Version: v1.30.9

[+]ping ok
[+]log ok
[+]etcd ok
[+]poststarthook/start-apiextensions-controllers ok
readyz check passed
```

`readyz` 결과에서 `etcd`와 admission 관련 훅이 함께 통과하는지 보면, 단순 네트워크 단절과 control-plane 내부 지연을 1차로 분리할 수 있습니다.
물론 AKS에서 내부 호스트를 직접 다루지는 않지만, API 표면의 준비 상태 신호만으로도 “요청을 받을 준비가 되어 있는가”를 꽤 정확히 읽을 수 있습니다.

## private API 서버를 쓸 때 경계가 어떻게 달라지는가

AKS 운영에서 control plane 경계를 가장 크게 바꾸는 선택 중 하나가 private cluster입니다.
public endpoint를 끄는 순간 진단 습관도 함께 바뀌어야 합니다.
사내 점프 호스트, VPN, Bastion 경유 경로가 없으면 “클러스터가 죽은 것처럼” 보일 수 있기 때문입니다.

아래 다이어그램은 운영팀이 자주 쓰는 private API 접근 구조입니다.

```mermaid
flowchart LR
  A["Engineer Laptop"] --> B["Corp VPN"]
  B --> C["Jump Host"]
  C --> D["AKS Private API Server"]
  D --> E["Managed Control Plane"]
```

경계가 바뀌면 런북도 같이 바뀌어야 합니다.
예를 들어 “kubectl 연결 실패”는 더 이상 곧바로 API 서버 장애를 의미하지 않습니다.
VPN 세션 만료, DNS split-horizon 누락, 점프 호스트 NSG 변경도 같은 증상을 만들 수 있으므로, 네트워크 경로 검증을 control-plane 진단의 0단계로 넣어야 합니다.

## 컨트롤러 수렴 지연을 이벤트로 읽는 연습

control plane은 결국 상태 수렴 루프입니다.
그래서 단일 에러 로그보다 “상태 전이가 얼마나 늦어지는가”를 보는 편이 더 실용적일 때가 많습니다.
아래는 Deployment 롤아웃이 느릴 때 자주 쓰는 확인 순서입니다.

```bash
kubectl rollout status deploy/my-api -n prod --timeout=120s
kubectl get rs -n prod -l app=my-api
kubectl get events -n prod --sort-by=.lastTimestamp | tail -25
```

출력이 아래와 비슷하면 controller-manager와 scheduler 경계에서 지연을 의심할 수 있습니다.

```text
deployment "my-api" exceeded its progress deadline
Warning  FailedScheduling  26s   default-scheduler  0/9 nodes are available: 3 Insufficient cpu, 6 node(s) didn't match Pod's node affinity.
Normal   ScalingReplicaSet 21s   deployment-controller Scaled up replica set my-api-7fb6d84f8d to 8
```

이 경우 deployment-controller는 원하는 replica를 올렸지만 scheduler 단계에서 실제 배치가 막혀 수렴이 지연됩니다.
즉 control plane 문제를 “API 서버 문제” 하나로 뭉치지 않고, 어떤 루프가 이미 성공했고 어떤 루프가 아직 실패하는지 분해해서 볼 수 있습니다.

## Admission/RBAC를 control-plane 안전장치로 쓰는 방법

AKS는 관리형이라도 정책 계층은 사용자 책임입니다.
특히 운영팀이 자주 배포하는 namespace에는 RBAC과 admission 정책을 같이 두는 편이 안전합니다.
아래 예시는 운영자가 특정 namespace의 읽기 진단만 수행하도록 제한하는 최소 권한 패턴입니다.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: prod-readonly-debug
  namespace: prod
rules:
  - apiGroups: [""]
    resources: ["pods", "services", "events", "configmaps"]
    verbs: ["get", "list", "watch"]
  - apiGroups: ["apps"]
    resources: ["deployments", "replicasets"]
    verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: prod-readonly-debug-binding
  namespace: prod
subjects:
  - kind: Group
    name: aks-oncall
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: prod-readonly-debug
```

여기에 Pod Security admission, image policy webhook, OPA Gatekeeper 같은 계층을 더하면 control plane은 단순 API 엔드포인트가 아니라 “변경을 허용할지 거절할지 결정하는 정책 경계”가 됩니다.
운영 품질은 결국 이 경계의 엄격함과 관측 가능성에 비례합니다.

- **관리형 control plane은 control plane이 없다는 뜻이 아닙니다.** 여전히 `kube-apiserver`, `etcd`, controller-manager, scheduler가 동작하며, 다만 사용자가 직접 운영하지 않을 뿐입니다.
- **API server가 곧 control plane 전체는 아닙니다.** 사용자가 만나는 표면이 API server일 뿐, 뒤에서는 상태 저장과 수렴 루프가 계속 작동합니다.
- **Pending Pod를 보면 곧바로 node 문제라고 단정하면 안 됩니다.** scheduler의 Filter/Score/Binding 단계에서 이미 막혔을 수 있습니다.
- **`kubectl` 명령이 성공했다고 실제 실행이 끝난 것은 아닙니다.** 그 뒤에도 controller와 scheduler, kubelet이 각자의 단계를 완료해야 합니다.
- **AKS에서 내부 호스트가 안 보인다고 해서 진단이 불가능한 것은 아닙니다.** 대신 API 동작, 객체 상태, 진단 로그를 더 구조적으로 읽어야 합니다.

## 운영 체크리스트

- [ ] API server 지연과 throttling 지표를 기본 대시보드에 포함했습니다.
- [ ] control plane 장애 시 data plane 워크로드가 어떤 범위까지 계속 동작하는지 런북에 문서화했습니다.
- [ ] audit log와 diagnostic settings의 보존 기간, 수집 위치, 비용 책임을 팀 내에서 합의했습니다.
- [ ] private cluster 또는 API server access profile 사용 여부와 우회 접근 경로를 결정했습니다.
- [ ] control plane 문제와 node 문제를 분리하는 1차 진단 순서를 운영 체크리스트에 반영했습니다.

## 정리

AKS의 control plane은 사용자가 직접 로그인해 운영하는 호스트 집합이 아니라, API server를 중심으로 관찰 가능한 관리형 표면과 그 뒤에서 상태를 수렴시키는 숨겨진 루프 묶음입니다.
따라서 AKS 운영의 핵심은 내부 VM을 더 많이 상상하는 데 있지 않고, API 표면과 상태 변화를 통해 어떤 층이 지금 멈췄는지 구분하는 데 있습니다.

이 글에서 가장 먼저 가져가야 할 문장은 세 가지입니다.
control plane은 원하는 상태를 기록하고 조정합니다.
data plane은 실제 실행을 담당합니다.
그리고 AKS에서는 control plane의 대부분을 Microsoft가 관리하므로, 운영자는 API server와 객체 상태를 통해 그 동작을 읽어야 합니다.

이 지도가 잡히면 이후 글들이 자연스럽게 연결됩니다.
2화에서는 kubelet과 containerd가 노드에서 실제 실행을 어떻게 시작하는지 보고, 3화에서는 Pod IP가 어디서 생기는지, 4화에서는 scheduler가 어느 노드를 고르는지, 5화와 6화에서는 autoscaling 루프가 어떻게 겹치는지 이어서 보게 됩니다.

## 처음 질문으로 돌아가기

- **AKS control plane은 정확히 어떤 컴포넌트로 이루어져 있고, 사용자는 그중 무엇을 직접 볼 수 있을까요?**
  - 본문에서 정리했듯이 AKS control plane의 핵심 컴포넌트는 `kube-apiserver`, `etcd`, `kube-controller-manager`, `kube-scheduler`입니다. 다만 AKS 사용자가 직접 만나는 표면은 대개 control plane 호스트가 아니라 API endpoint, 객체 상태, `readyz` 같은 API 신호, 그리고 diagnostic settings로 수집한 로그입니다. 즉 내부 프로세스를 직접 다루기보다 API 표면을 통해 뒤의 상태 저장과 수렴 루프를 읽는 구조입니다.
- **관리형 control plane이라는 약속은 어디까지를 의미하고, 어디부터는 여전히 사용자의 운영 책임일까요?**
  - 관리형이라는 약속은 control plane 패치, 고가용성 구성, 핵심 컴포넌트 수명주기를 Microsoft가 맡는다는 뜻입니다. 반대로 사용자는 private API 접근 경로, RBAC와 admission 정책, audit log와 diagnostic settings 보존, 그리고 control plane 문제와 node 문제를 가르는 런북을 여전히 책임져야 합니다. 그래서 AKS에서는 “내가 직접 프로세스를 운영하지 않는다”와 “운영 책임이 없다”를 같은 말로 보면 안 됩니다.
- **API server SLA를 읽을 때 왜 `etcd`, scheduler, controller-manager의 내부 구현보다 API 표면을 먼저 봐야 할까요?**
  - 사용자가 `kubectl`, GitOps controller, Terraform으로 실제로 대화하는 경로가 모두 API server이기 때문에, 체감되는 control plane 품질도 먼저 API 요청 성공률과 지연 시간으로 드러납니다. `etcd` 지연이나 scheduler 수렴 문제도 결국 객체 상태 변화, watch 지연, `readyz` 결과 같은 API 표면의 이상으로 간접 반영됩니다. 그래서 장애 초기에 내부 구현을 상상하기보다 API가 죽었는지, 느린지, 아니면 뒤쪽 루프가 밀리는지를 먼저 가르는 편이 더 정확합니다.

<!-- toc:begin -->
## 시리즈 목차

- **Azure Kubernetes Service Deep Dive (1/6): Control Plane 해부 — AKS가 사용자에게서 가린 것 (현재 글)**
- Azure Kubernetes Service Deep Dive (2/6): kubelet과 containerd — 노드 위에서 컨테이너가 뜨기까지 (예정)
- Azure Kubernetes Service Deep Dive (3/6): CNI와 Azure CNI Overlay — Pod IP가 어디서 오는가 (예정)
- Azure Kubernetes Service Deep Dive (4/6): Scheduler와 Pod 배치 — 어느 노드로 갈지 누가 정하는가 (예정)
- Azure Kubernetes Service Deep Dive (5/6): HPA와 Cluster Autoscaler 내부 — 두 컨트롤 루프 (예정)
- Azure Kubernetes Service Deep Dive (6/6): KEDA 내부 — ScaledObject가 HPA를 만드는 방식 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [AKS core concepts](https://learn.microsoft.com/en-us/azure/aks/core-aks-concepts)
- [AKS pricing tiers and Uptime SLA](https://learn.microsoft.com/en-us/azure/aks/free-standard-pricing-tiers)
- [Kubernetes components overview](https://kubernetes.io/docs/concepts/overview/components/)

### 업스트림 코드
- [`schedule_one.go` @ `v1.30.0`](https://github.com/kubernetes/kubernetes/blob/v1.30.0/pkg/scheduler/schedule_one.go)
- [`default_plugins.go` @ `v1.30.0`](https://github.com/kubernetes/kubernetes/blob/v1.30.0/pkg/scheduler/apis/config/v1/default_plugins.go)
- [`api.proto` @ `v1.30.0`](https://github.com/kubernetes/kubernetes/blob/v1.30.0/staging/src/k8s.io/cri-api/pkg/apis/runtime/v1/api.proto)

### 관련 시리즈
- [Azure AKS 101](../../azure-aks-101/ko/)
- [Azure Functions Deep Dive 1화 — 호스트 부트스트랩과 전체 구조](../../azure-functions-deep-dive/ko/01-host-bootstrap.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-aks-deep-dive/ko/01-control-plane-anatomy)

Tags: AKS, Kubernetes, Distributed Systems, Containers
