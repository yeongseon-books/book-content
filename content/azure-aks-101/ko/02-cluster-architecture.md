---
title: "Azure Kubernetes Service 101 (2/7): 클러스터 아키텍처 — Control Plane과 Node Pool"
series: azure-aks-101
episode: 2
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- Azure
- AKS
- Kubernetes
- Cloud
last_reviewed: '2026-05-12'
seo_description: AKS를 이해할 때 가장 먼저 분리해야 하는 것은 “클러스터의 두뇌”와 “실제로 컨테이너가 돌아가는 자리”입니다.
---

# Azure Kubernetes Service 101 (2/7): 클러스터 아키텍처 — Control Plane과 Node Pool

AKS를 이해할 때 가장 먼저 분리해야 하는 것은 클러스터의 두뇌와 실제 실행 공간입니다. 이 둘을 섞어서 보면 업그레이드, 장애 범위, 비용, 스케일링이 모두 흐려집니다. AKS가 관리형 Kubernetes라는 말도 결국 이 구조를 어디까지 Azure가 맡는지로 풀어야 정확합니다.

특히 입문 단계에서는 Pod와 Deployment 같은 워크로드 객체가 눈에 먼저 들어오지만, 운영 관점에서는 그보다 아래에 있는 Control Plane과 Node Pool의 경계가 더 중요할 때가 많습니다. API server 쪽 문제인지, 노드 풀 쪽 문제인지 구분하는 것만으로도 원인 분석 속도가 크게 달라집니다.

이 글은 Azure AKS 101 시리즈의 2번째 글입니다.

여기서는 1화에서 잡은 책임 경계를 실제 클러스터 구조로 바꾸어 보겠습니다. **Control Plane은 어떤 결정을 내리고, Node Pool은 그 결정을 어디에서 실행하며, system pool과 user pool은 왜 분리해야 하는가**를 운영 관점에서 차례로 정리하겠습니다.

![Azure Kubernetes Service 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/azure-aks-101/02/02-01-cut-the-cluster-in-half.ko.png)
*Azure Kubernetes Service 101 2장 흐름 개요*
> 클러스터 아키텍처 — Control Plane과 Node Pool의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 먼저 던지는 질문

- API server, scheduler, controller manager, etcd는 각각 어떤 일을 할까요?
- Node Pool은 단순한 VM 묶음 이상으로 왜 중요한 관리 단위일까요?
- system node pool과 user node pool을 분리해야 하는 실무적 이유는 무엇일까요?

## 왜 이 글이 중요한가

AKS 운영에서 많은 문제는 “클러스터가 이상하다”는 막연한 문장으로 시작합니다. 하지만 실제 원인은 매우 다릅니다. Kubernetes API 응답이 느린 문제, 특정 노드 풀만 포화되는 문제, system Pod가 밀려나는 문제, Pod는 생성됐지만 스케줄되지 못하는 문제는 모두 다른 층의 현상입니다. 구조를 모르면 이들을 한데 섞어 보게 됩니다.

또한 아키텍처를 정확히 이해해야 비용과 가용성 설계도 가능해집니다. Control Plane이 별도 과금되지 않는 이유, Node Pool이 비용과 용량의 중심인 이유, Spot 사용이 user pool로 한정되는 이유는 모두 클러스터 구조에서 자연스럽게 나옵니다.

무엇보다 이 글은 이후 실습의 기반입니다. 3화에서 클러스터를 만들고 FastAPI 앱을 올릴 때도 결국 어디에 Pod를 배치하고 어떤 풀에 용량을 둘 것인가가 핵심이 됩니다. 구조를 먼저 잡아 두면 실습이 훨씬 덜 기계적으로 보입니다.

## 핵심 관점

AKS를 읽을 때 가장 좋은 멘탈 모델은 클러스터를 둘로 가르는 것입니다. 왼쪽에는 원하는 상태를 저장하고 배치 결정을 내리는 계층이 있고, 오른쪽에는 실제로 컨테이너가 돌아가는 실행 계층이 있습니다. Kubernetes 객체를 아무리 많이 만들어도, 결국 이 두 층 사이에서 해석되고 실행됩니다.

이 관점이 좋은 이유는 관리형 Kubernetes의 본질을 그대로 보여 주기 때문입니다. Azure는 Control Plane 운영을 맡지만, Node Pool의 용량과 특성, 워크로드 배치 정책, 스케일 범위는 여전히 사용자가 설계합니다. 즉 “관리형”은 클러스터 전체를 Azure가 대신 생각해 준다는 뜻이 아닙니다.

따라서 이 글에서는 세부 기능보다도 먼저 **누가 결정하고 누가 실행하는가**를 분리해서 보겠습니다. 이 한 가지 기준만 정확해도 system/user pool 분리, Spot 전략, 업그레이드 범위 같은 주제가 훨씬 쉽게 정리됩니다.

> Control Plane은 원하는 상태를 받아 결정을 내리고, Node Pool은 그 결정을 실제 용량 위에서 실행합니다. AKS는 이 둘 중 앞단 운영을 Azure가 맡는 구조입니다.

## 핵심 개념

### 클러스터를 반으로 자르면 구조가 선명해집니다

전체 아키텍처를 처음 볼 때는 구성 요소 나열보다 경계를 먼저 보는 편이 좋습니다.

왼쪽은 Azure가 운영하는 계층이고, 오른쪽은 사용자가 더 직접 다루는 계층입니다. 이 그림 하나만 정확히 기억해도 왜 Control Plane 비용이 따로 청구되지 않는지, 왜 노드 수를 사용자가 정하는지, 왜 Pod 스케일링과 노드 스케일링이 다른 문제인지가 자연스럽게 이어집니다.

즉 AKS는 단일 박스가 아니라 **의사결정 계층과 실행 계층이 분리된 플랫폼**입니다. 이후의 모든 실무 판단은 이 구분 위에서 이루어집니다.

### Control Plane은 클러스터의 의사결정 계층입니다

Control Plane은 Kubernetes의 두뇌입니다. 사용자가 `kubectl apply`로 원하는 상태를 선언하면, 이 계층이 그것을 받아 저장하고 해석하고 실행 방향을 결정합니다.

- **API server**: 모든 선언과 조회의 출입구입니다.
- **etcd**: 클러스터 상태를 저장하는 영속 계층입니다.
- **Scheduler**: 새 Pod를 어느 노드에 올릴지 결정합니다.
- **Controller loops**: Deployment, Endpoint, Node 상태 같은 리소스가 원하는 상태로 수렴하도록 계속 조정합니다.

AKS에서는 이 계층을 Azure가 배치하고 운영합니다. 사용자는 API를 끊임없이 사용하지만, API server 노드나 etcd 토폴로지를 직접 설계하는 일은 일반적으로 하지 않습니다. 이것이 관리형 Kubernetes의 가장 구체적인 의미입니다.

### Node Pool은 추상적 의도를 실제 용량으로 바꾸는 실행 계층입니다

Node Pool은 같은 설정을 가진 노드 VM의 묶음입니다. 같은 VM 크기, 같은 OS SKU, 같은 스케일 범위, 같은 모드를 공유하는 관리 단위라고 생각하면 됩니다.

Pod는 논리적 워크로드 단위지만, 실제로 Pod가 올라갈 자리와 비용은 Node Pool이 결정합니다. 그래서 실무 질문은 금방 Node Pool 질문으로 바뀝니다.

- 어떤 VM 크기를 써야 하는가
- 어느 풀이 system workload를 받을 것인가
- Spot을 어디까지 허용할 것인가
- autoscaler 최소/최대 범위를 어떻게 둘 것인가

즉 Pod는 애플리케이션 언어이고, Node Pool은 **용량과 비용의 언어**입니다. Kubernetes를 이해해도 Node Pool 설계를 못 하면 운영이 흔들리는 이유가 여기 있습니다.

### 노드 내부 경로도 한 번쯤은 떠올려 두는 편이 좋습니다

Pod가 노드 위에 올라간다고 할 때, 실제로는 kubelet, kube-proxy, container runtime 같은 구성 요소가 함께 움직입니다. 입문 단계에서 모든 디테일을 외울 필요는 없지만, Control Plane의 결정이 노드 쪽 실행 경로로 어떻게 내려오는지는 감각으로라도 알고 있는 편이 좋습니다.

- kubelet은 노드에서 Pod 실행 상태를 맞춥니다.
- container runtime은 실제 컨테이너를 띄웁니다.
- kube-proxy는 서비스 네트워크 경로 구성에 관여합니다.

즉 Control Plane이 “어디에 올릴지”를 결정한다면, 노드 내부 구성 요소는 “그 결정을 실제 실행 상태로 바꾸는 일”을 맡습니다.

### system node pool과 user node pool은 운영 안정성을 위한 분리입니다

AKS에서 가장 먼저 익혀야 할 Node Pool 구분은 system과 user입니다.

![시스템 풀과 사용자 풀의 역할 분리](https://yeongseon-books.github.io/book-public-assets/assets/azure-aks-101/02/02-02-system-node-pool-vs-user-node-pool.ko.png)

*시스템 풀과 사용자 풀의 역할 분리*

#### System node pool

System pool은 클러스터 유지에 필요한 핵심 Pod가 우선 올라가는 자리입니다.

- CoreDNS
- metrics-server
- 각종 클러스터 애드온

작은 실습 클러스터에서는 애플리케이션 Pod가 system pool에 올라갈 수도 있습니다. 하지만 운영 환경에서는 system Pod와 앱 워크로드를 분리하는 편이 훨씬 안전합니다.

#### User node pool

User pool은 애플리케이션 워크로드용 풀입니다.

- 웹 API
- 비동기 워커
- 배치 처리
- CronJob

이 분리가 중요한 이유는 안정성 때문입니다. 앱 워크로드가 폭주하거나 잘못된 설정으로 노드를 압박하더라도, 클러스터 자체를 유지하는 핵심 구성 요소와 충돌할 가능성을 줄일 수 있습니다.

### 왜 system과 user를 굳이 분리해야 할까요

이 분리는 철학이 아니라 운영상의 안전장치입니다.

1. 시스템 Pod와 애플리케이션 Pod가 같은 자리를 두고 경쟁하지 않습니다.
2. user pool만 따로 스케일링하기 쉬워집니다.
3. Spot을 user pool에만 적용하는 전략을 세우기 쉽습니다.
4. 필요하면 Linux system pool과 Windows user pool을 함께 운용할 수 있습니다.

짧게 요약하면 이렇습니다.

> system node pool은 클러스터를 살리는 자리이고, user node pool은 비즈니스 코드를 실행하는 자리입니다.

운영에서 강한 팀일수록 이 경계를 초기에 강하게 잡습니다. 이유는 단순합니다. 문제의 blast radius가 작아지기 때문입니다.

### Node Pool 개수는 팀 경계보다 워크로드 특성으로 나누는 편이 좋습니다

처음부터 풀을 많이 쪼갤 필요는 없습니다. 대부분의 입문 클러스터는 아래 정도로 시작해도 충분합니다.

#### 작은 시작

- system pool 1개
- user pool 1개

#### 클러스터가 커지면

- latency-sensitive API용 user pool
- batch/worker용 user pool
- Spot 전용 user pool
- GPU 또는 메모리 최적화용 specialized pool

풀은 팀 조직도보다 **워크로드 성격**에 맞게 나누는 편이 좋습니다. 같은 팀이 운영해도 API와 배치는 리소스 패턴과 중단 허용도가 다르므로, 풀을 분리해야 읽기 쉽고 안전한 구조가 됩니다.

### Spot node pool은 비용 절감 장치이지 기본 안정성 계층이 아닙니다

AKS 비용 이야기를 하면 Spot을 빼기 어렵습니다.

#### 일반 node pool

- 안정성이 우선일 때 사용합니다.
- 핵심 API의 기준 용량을 담당하게 두는 편이 안전합니다.
- 중단이 비싼 워크로드에 적합합니다.

#### Spot node pool

- 할인된 Azure 용량을 사용합니다.
- 대신 축출될 수 있습니다.
- 재시도가 쉽고 중단 내성이 큰 워크로드에 적합합니다.

대표적으로 큐 기반 워커, 배치 작업, 재시도 가능한 비동기 처리에 잘 맞습니다. 반대로 사용자 트래픽을 직접 받는 핵심 API의 유일한 실행 공간을 Spot만으로 구성하는 것은 대개 좋지 않습니다.

실무에서는 기준 용량은 일반 pool로 두고, burst 용량이나 비핵심 처리만 Spot으로 보내는 식의 혼합 전략을 자주 씁니다. 이렇게 해야 비용을 줄이면서도 서비스 핵심 경로의 안정성을 해치지 않을 수 있습니다.

### 스케줄러는 Node Pool이 아니라 노드에 배치합니다

여기서 하나 헷갈리기 쉬운 점이 있습니다. Kubernetes 스케줄러는 “Node Pool” 객체를 직접 대상으로 배치하지 않습니다. 실제 스케줄 대상은 노드입니다.

다만 AKS에서는 각 노드가 어떤 Pool에 속하는지가 라벨, taint, 설정으로 드러납니다. 그래서 실무에서는 다음 식으로 이해하는 편이 좋습니다.

- Node Pool: 관리 단위
- Node: 실제 스케줄 대상
- Pod: selector, affinity, taint toleration, resource request를 통해 특정 성격의 노드로 유도됨

이 관계를 이해하면 placement policy가 왜 중요한지도 보입니다. 예를 들어 system pool에 `CriticalAddonsOnly=true:NoSchedule` 같은 taint를 두면 일반 앱 Pod가 실수로 그쪽에 올라가는 일을 줄일 수 있습니다.

### 업그레이드를 이야기할 때는 층을 구분해야 합니다

팀이 “클러스터를 업그레이드했다”라고 말할 때는 보통 몇 가지가 섞여 있습니다.

- Control Plane 버전 업그레이드
- Node Pool Kubernetes 버전 업그레이드
- 노드 이미지 업그레이드

이 셋은 서로 관련 있지만 같은 말이 아닙니다. Control Plane이 먼저 올라가고, Node Pool이 뒤따르는 경우도 흔합니다. 그래서 운영 문장으로는 “클러스터 버전을 올렸다”만으로 충분하지 않습니다. **어느 Node Pool까지 따라왔는지**를 같이 봐야 의미가 있습니다.

여기서 하나 더 기억할 점은 blast radius입니다. Control Plane 업그레이드는 API 레벨과 관리 경로에 영향을 주고, Node Pool 업그레이드는 실제 워크로드 배치와 재시작에 더 직접적인 영향을 줍니다. 같은 “업그레이드”라는 단어 아래에 있지만, 체감 리스크는 다를 수 있습니다.

### 빠르게 확인하기

실제 클러스터에서 현재 실행 계층을 보는 가장 빠른 방법은 노드와 kube-system Pod를 함께 보는 것입니다.

```bash
kubectl get nodes -o wide
kubectl get pods -n kube-system
```

첫 번째 명령은 노드 상태와 주소를 보여 주고, 두 번째 명령은 system workload가 어디에서 어떻게 돌아가는지 감각을 줍니다. 구조를 이해한 뒤 이 명령을 보면 system/user 분리가 실제로 어떻게 드러나는지도 읽기 쉬워집니다.

Node Pool 관점까지 더 분명히 보고 싶다면 아래 두 명령을 이어서 보는 편이 좋습니다.

```bash
az aks nodepool list \
  --resource-group $RG \
  --cluster-name $CLUSTER \
  --query "[].{name:name, mode:mode, count:count, vmSize:vmSize, osType:osType}"

kubectl get nodes -L kubernetes.azure.com/agentpool,kubernetes.azure.com/mode
```

앞의 명령은 **Azure 리소스 관점의 풀 설정**을 보여 주고, 뒤의 명령은 **실제 노드가 어느 풀과 모드에 속하는지**를 Kubernetes 관점에서 보여 줍니다. 둘을 같이 봐야 “설계한 풀”과 “실제로 배치에 쓰이는 노드”가 한 화면에서 연결됩니다.

## 클러스터가 이상해 보일 때는 이 순서로 잘라 봅니다

구조를 아는 가장 좋은 증거는 아키텍처를 설명하는 능력보다, 이상 징후를 올바른 층으로 보내는 능력입니다.

### 1. API 문제인지부터 봅니다

`kubectl get nodes` 자체가 이상하게 느리거나 실패하면, 먼저 Control Plane 경계와 자격 증명 문제를 의심하는 편이 맞습니다. 이 경우는 애플리케이션 Pod부터 보는 것보다 API 연결 상태를 먼저 확인해야 시간을 덜 씁니다.

### 2. Pod가 안 뜨면 Node Pool 수용력을 봅니다

Pod가 `Pending`에 오래 머문다면 스케줄링과 용량 문제일 가능성이 큽니다. 이때는 “클러스터 전체가 죽었다”보다 **어느 풀에 자리가 없고 어떤 제약이 걸렸는가**를 먼저 봐야 합니다.

```bash
kubectl describe pod <pod-name>
kubectl top nodes
```

`describe`에는 taint, selector mismatch, insufficient CPU/memory 같은 단서가 바로 나오고, `kubectl top nodes`는 어느 풀이 실제로 포화 쪽으로 가는지 감을 줍니다.

### 3. system workload부터 흔들리면 blast radius를 크게 봅니다

앱 Pod만 불안정한지, 아니면 `kube-system`의 CoreDNS·metrics-server까지 흔들리는지는 의미가 다릅니다. 후자라면 애플리케이션 한 개의 문제가 아니라 클러스터 운영 기반이 압박받고 있을 가능성이 큽니다.

즉 이 글의 구조는 그림 설명으로 끝나지 않습니다. **Control Plane인지, user pool인지, system pool인지 먼저 자르는 습관**이 생겨야 실제 운영에서 아키텍처 이해가 힘을 발휘합니다.

## 노드 풀 설계를 YAML/명령으로 고정하는 방법

아키텍처를 팀 공통 언어로 만들려면 다이어그램만으로는 부족하고, 실제 설정값이 남아야 합니다. 최소한 아래 네 값은 항상 문서와 코드에 같이 남기는 편이 좋습니다. `mode(system/user)`, VM 크기, autoscaler 범위, taint 정책입니다.

```bash
az aks nodepool add \
  --resource-group "$RG" \
  --cluster-name "$CLUSTER" \
  --name userpoolapi \
  --mode User \
  --node-vm-size Standard_D4s_v5 \
  --enable-cluster-autoscaler \
  --min-count 1 \
  --max-count 6

kubectl taint nodes -l kubernetes.azure.com/mode=system \
  CriticalAddonsOnly=true:NoSchedule
```

첫 명령은 user pool을 별도 수용력 계층으로 두겠다는 선언이고, 두 번째 명령은 system 노드에 일반 앱 Pod가 섞이지 않게 하는 안전장치입니다. 이 두 줄만 있어도 “왜 분리했는지”가 설계 문장이 아니라 실행 가능한 정책으로 남습니다.

아래처럼 `kubectl get nodes -L kubernetes.azure.com/agentpool,kubernetes.azure.com/mode`를 주기적으로 확인하면 설계 의도와 실제 배치가 어긋났는지 빨리 찾을 수 있습니다. 운영에서 중요한 것은 완벽한 구조가 아니라, 구조가 깨졌을 때 즉시 보이는 관측 포인트를 갖추는 일입니다.

## 아키텍처를 검증하는 진단 시나리오

실제 현장에서는 “설계했다”보다 “설계가 지켜지고 있는지 검증했다”가 더 중요합니다. 아래는 system/user 분리, 스케줄링 제약, 용량 압력을 한 번에 점검하는 최소 진단 시나리오입니다.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-on-user-pool
spec:
  replicas: 4
  selector:
    matchLabels:
      app: api-on-user-pool
  template:
    metadata:
      labels:
        app: api-on-user-pool
    spec:
      nodeSelector:
        kubernetes.azure.com/mode: user
      containers:
        - name: app
          image: mcr.microsoft.com/azuredocs/aks-helloworld:v1
          resources:
            requests:
              cpu: 200m
              memory: 256Mi
```

```bash
kubectl apply -f api-on-user-pool.yaml
kubectl get pods -o wide
kubectl describe pod <pod-name>
kubectl get nodes -L kubernetes.azure.com/mode,kubernetes.azure.com/agentpool
```

이때 Pod가 system 노드에 올라가면 분리 정책이 깨진 것입니다. 반대로 user 노드에만 배치되고, scale-out 시 user pool만 확장된다면 설계 의도가 제대로 반영된 것입니다. 이 검증을 릴리스 전 점검 루틴에 포함하면 구조 드리프트를 초기에 막기 쉽습니다.

또한 장애 분석 템플릿에 “문제 Pod가 어느 pool에 있었는가”를 기본 항목으로 넣는 편이 좋습니다. 같은 오류 로그라도 system pool에서 발생한 문제와 user pool에서 발생한 문제는 운영 의미가 완전히 다르기 때문입니다.

## 흔히 헷갈리는 지점

- Control Plane과 Node Pool을 모두 “클러스터”라고만 부르면서 문제 층을 구분하지 못하는 경우가 많습니다.
- Node Pool을 단순한 VM 묶음으로만 보지만, 실제로는 비용과 가용성 전략의 핵심 관리 단위입니다.
- system pool에도 앱을 올려도 되니 운영에서도 큰 문제 없다고 생각하기 쉽지만, blast radius가 커집니다.
- Spot은 싸기 때문에 기본 선택지처럼 느껴지지만, 중단 허용도가 낮은 워크로드에는 위험합니다.
- “클러스터 업그레이드”를 하나의 작업으로 생각하기 쉽지만, Control Plane과 Node Pool 업그레이드는 다른 범위를 가집니다.

## 운영 체크리스트

- [ ] API server, scheduler, controller loops, etcd의 역할을 한 문장씩 설명할 수 있는가
- [ ] system node pool과 user node pool을 왜 분리하는지 운영 관점에서 설명할 수 있는가
- [ ] 현재 또는 예정된 Node Pool 구성이 워크로드 특성 기준으로 나뉘어 있는가
- [ ] Spot 사용 시 축출 가능성을 감수해도 되는 워크로드만 배치되도록 정책을 세웠는가
- [ ] 업그레이드 문서를 Control Plane, Node Pool, 노드 이미지 레벨로 분리해 표현하고 있는가

## 정리

이 글의 핵심은 AKS 클러스터를 하나의 뭉친 자원으로 보지 않는 것입니다. Control Plane은 원하는 상태를 저장하고 배치 결정을 내리는 계층이고, Node Pool은 실제 용량과 비용과 워크로드 실행을 담당하는 계층입니다. 관리형 Kubernetes는 이 둘 중 앞단 운영을 Azure가 대신 맡는 구조라고 보면 됩니다.

또한 system pool과 user pool의 분리는 선택적 미세 조정이 아니라 운영 안정성을 위한 기본 설계입니다. 여기에 Spot 전략, placement policy, 업그레이드 범위가 모두 얹힙니다. 즉 Node Pool 설계는 단순 용량 설정이 아니라 클러스터 운영 전략 그 자체입니다.

이 구조를 이해하면 다음 글의 실습도 훨씬 선명해집니다. 3화에서 실제 클러스터를 만들고 FastAPI 앱을 배포할 때, 우리는 단순히 명령 몇 줄을 실행하는 것이 아니라 **이 글에서 본 Control Plane과 Node Pool 경계 위에 워크로드를 올리는 일**을 하게 됩니다.

## 처음 질문으로 돌아가기

- **API server, scheduler, controller manager, etcd는 각각 어떤 일을 할까요?**
  - `API server`는 선언과 조회의 출입구이고, `etcd`는 그 상태를 저장하며, `scheduler`는 `Pod -> Node` 배치를 기록합니다. `controller loops`는 Deployment와 Endpoint 같은 객체를 원하는 상태로 계속 수렴시키므로, 네 컴포넌트는 모두 Control Plane 안에서 서로 다른 결정을 맡습니다.
- **Node Pool은 단순한 VM 묶음 이상으로 왜 중요한 관리 단위일까요?**
  - Node Pool은 `vmSize`, `count`, `osType`, autoscaler 범위를 같이 묶어 관리하는 실행 계층입니다. 그래서 `az aks nodepool list --query "[].{name:name, mode:mode, count:count, vmSize:vmSize, osType:osType}"` 출력이 곧 비용, 용량, 배치 전략을 읽는 표가 됩니다.
- **system node pool과 user node pool을 분리해야 하는 실무적 이유는 무엇일까요?**
  - `CoreDNS`, `metrics-server` 같은 시스템 Pod가 올라가는 system pool과 애플리케이션 Pod가 올라가는 user pool을 나누면 blast radius가 작아집니다. `CriticalAddonsOnly=true:NoSchedule` taint나 `kubernetes.azure.com/mode: user` 같은 기준을 두면 user workload 폭주가 클러스터 기반 계층까지 같이 흔드는 일을 줄일 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Azure Kubernetes Service 101 (1/7): Azure Kubernetes Service란? — 직접 운영하지 않아도 되는 Kubernetes](./01-what-is-aks.md)
- **Azure Kubernetes Service 101 (2/7): 클러스터 아키텍처 — Control Plane과 Node Pool (현재 글)**
- Azure Kubernetes Service 101 (3/7): 첫 클러스터 만들고 앱 배포하기 — Python/FastAPI (예정)
- Azure Kubernetes Service 101 (4/7): Pod·Deployment·Service — 워크로드를 표현하는 세 가지 방식 (예정)
- Azure Kubernetes Service 101 (5/7): 네트워킹과 Ingress — 클러스터 안과 밖을 잇는 길 (예정)
- Azure Kubernetes Service 101 (6/7): 스케일링 — HPA, Cluster Autoscaler, KEDA (예정)
- Azure Kubernetes Service 101 (7/7): 모니터링과 운영 — Container Insights, 로그, 알람 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [What is Azure Kubernetes Service (AKS)?](https://learn.microsoft.com/en-us/azure/aks/what-is-aks)
- [Use system node pools in Azure Kubernetes Service (AKS)](https://learn.microsoft.com/en-us/azure/aks/use-system-pools)
- [Create node pools in Azure Kubernetes Service (AKS)](https://learn.microsoft.com/en-us/azure/aks/create-node-pools)
- [Deploy an Azure Kubernetes Service (AKS) Cluster Using Azure CLI](https://learn.microsoft.com/en-us/azure/aks/learn/quick-kubernetes-deploy-cli)

### 관련 시리즈

- [Azure App Service 101](../../azure-app-service-101/ko/) — 노드 개념이 없는 PaaS와 비교할 때
- [Azure Functions 101](../../azure-functions-101/ko/) — 실행 단위와 스케일 단위가 어떻게 다른지 비교할 때

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-aks-101/ko/02-cluster-architecture)

Tags: Azure, AKS, Kubernetes, Cloud
