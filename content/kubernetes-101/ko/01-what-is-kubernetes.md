---
series: kubernetes-101
episode: 1
title: "Kubernetes 101 (1/10): Kubernetes란 무엇인가?"
status: published
published_to:
  tistory:
    url: "https://yeongseonchoe.tistory.com/263"
    published_at: '2026-06-02'
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Kubernetes
  - Orchestration
  - Containers
  - DevOps
  - SRE
seo_description: Kubernetes의 기본 구조와 원하는 상태 모델을 입문자 관점에서 정리합니다.
last_reviewed: '2026-05-15'
---

# Kubernetes 101 (1/10): Kubernetes란 무엇인가?

컨테이너를 처음 다룰 때는 `docker run` 몇 번으로도 충분해 보입니다. 앱 하나, 데이터베이스 하나, 프록시 하나 정도라면 사람이 직접 상태를 맞춰도 큰 문제 없이 굴러갑니다. 하지만 서비스가 커지고 컨테이너 수가 늘어나면 상황이 달라집니다. 어느 서버에 무엇이 떠 있는지, 죽은 컨테이너를 누가 다시 띄우는지, 버전 교체를 어떻게 안전하게 할지부터 사람이 기억하고 맞추기 어려워집니다.

이 글은 Kubernetes 101 시리즈의 첫 번째 글입니다.

여기서는 Kubernetes를 단순히 "컨테이너를 많이 돌리는 도구"가 아니라, 원하는 상태를 선언하면 시스템이 그 상태로 계속 수렴하도록 만드는 오케스트레이터라는 관점에서 정리하겠습니다.

![Kubernetes 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/kubernetes-101/01/01-01-concept-at-a-glance.ko.png)
*Kubernetes 101 1장 흐름 개요*

> Kubernetes는 '컨테이너를 많이 돌리는 도구'가 아니라 원하는 상태(desired state)를 선언하면 시스템이 그 상태로 계속 수렴하도록 만드는 오케스트레이터입니다 — 사람이 명령형으로 맞추던 일을 컨트롤러 루프에 위임한다는 한 가지 발상이 모든 리소스 설계의 출발점입니다.

## 이 글에서 다룰 문제

- 오케스트레이션이라는 말은 실제로 무엇을 대신해 줄까요?
- 컨트롤 플레인과 워커 노드는 어떤 식으로 역할을 나눌까요?
- 원하는 상태 모델이 왜 Kubernetes의 핵심 철학일까요?
- 이 리소스의 설정을 잘못하면 운영에서 어떤 장애가 발생할까요?
- 프로덕션 환경에서 이 기능을 쓸 때 가장 먼저 점검할 항목은 무엇일까요?

컨테이너 몇 개는 Docker Compose만으로도 충분합니다. 하지만 수십 개가 넘어가면 누가 어떤 컨테이너를 어디에 배치할지, 장애가 나면 어떻게 복구할지, 새 버전으로 어떻게 교체할지 같은 문제가 한꺼번에 밀려옵니다. 이때부터는 컨테이너 런타임보다 오케스트레이터가 더 중요해집니다.

Kubernetes를 배우는 이유도 여기 있습니다. 많은 입문자가 Kubernetes를 "컨테이너 플랫폼" 정도로 받아들이지만, 실제로는 사람이 반복하던 운영 결정을 시스템 규칙으로 옮기는 도구에 가깝습니다. 이 관점을 먼저 잡아 두면 뒤에서 나오는 Pod, Deployment, Service도 훨씬 자연스럽게 이어집니다.

## 한눈에 보는 구조

이 그림을 볼 때 가장 먼저 기억할 점은 `kubectl`이 직접 컨테이너를 띄우지 않는다는 사실입니다. 사용자는 `kubectl`로 원하는 상태를 API 서버에 전달하고, 이후의 배치와 조정은 컨트롤 플레인 구성요소가 맡습니다. Kubernetes를 이해하려면 이 제어 흐름부터 알아야 합니다.

- 클러스터: 컨트롤 플레인과 워커 노드를 묶은 전체 실행 환경입니다.
- 컨트롤 플레인: API 서버, etcd, scheduler, controller-manager처럼 클러스터의 제어를 맡는 영역입니다.
- 노드: 실제로 컨테이너가 실행되는 머신입니다.
- 원하는 상태: YAML에 선언한 목표 상태입니다.
- `kubectl`: 클러스터 API와 통신하는 CLI입니다.

## 도입 전과 후

| 항목 | Kubernetes 이전 | Kubernetes 도입 후 |
|---|---|---|
| 컨테이너 관리 | 서버마다 수동 `docker run` | 원하는 상태 선언으로 자동 유지 |
| 장애 복구 | 사람이 직접 컨테이너 재시작 | 컨트롤러 루프가 자동 감지·복구 |
| 환경 재현 | 설정 파일을 별도 관리, 실수 잦음 | YAML 파일 하나로 반복 재현 가능 |
| 배포 방식 | 서비스 중단 후 수동 교체 | 롤링 업데이트로 무중단 배포 |
| 스케일링 | 수동으로 서버 추가 및 배포 | HPA 등으로 부하에 따라 자동 조절 |

Kubernetes를 도입하면 상황이 달라집니다. 원하는 상태를 YAML로 선언하면 같은 구성을 다른 환경에 반복해서 적용할 수 있고, 시스템이 현재 상태를 계속 목표 상태에 맞추려 합니다. 재현성과 자동 복구가 여기서 시작됩니다.

## 핵심 컴포넌트 살펴보기

Kubernetes 클러스터는 크게 컨트롤 플레인과 워커 노드로 나뉩니다.

### 컨트롤 플레인 컴포넌트

```yaml
# 컨트롤 플레인의 주요 구성요소
controlPlane:
  apiServer:
    역할: 클러스터의 모든 요청을 처리하는 프론트엔드
    통신: kubectl, 다른 컴포넌트와 REST API로 통신
  etcd:
    역할: 클러스터 전체 상태를 저장하는 분산 키-값 스토어
    주의: 직접 접근 금지, API 서버를 통해서만 조작
  scheduler:
    역할: 새 파드를 어느 노드에 배치할지 결정
    기준: 노드의 자원 가용량, taint/toleration, affinity
  controllerManager:
    역할: 다양한 컨트롤러를 실행하는 프로세스
    예시: ReplicaSet 컨트롤러, Node 컨트롤러
```

### 워커 노드 컴포넌트

```yaml
# 각 워커 노드에서 실행되는 컴포넌트
workerNode:
  kubelet:
    역할: API 서버와 통신하며 파드를 생성·유지·삭제
    특징: 노드에서 실제 컨테이너 상태를 맞추는 에이전트
  kubeProxy:
    역할: 네트워크 규칙을 관리해 서비스 통신 경로 구성
    방식: iptables 또는 IPVS 기반 로드밸런싱
  containerRuntime:
    역할: 실제로 컨테이너를 실행하는 런타임
    예시: containerd, CRI-O
```

## 단계별로 첫 클러스터 둘러보기

### 1단계 — 현재 컨텍스트 확인

```bash
kubectl config current-context
```

가장 먼저 볼 값은 현재 컨텍스트입니다. `kubectl`은 단일 클러스터 전용 도구가 아니므로, 지금 어떤 클러스터를 바라보는지부터 확인해야 합니다. 입문 단계에서도 이 습관이 중요합니다.

```bash
# 여러 클러스터 컨텍스트 목록 보기
kubectl config get-contexts

# 특정 컨텍스트로 전환
kubectl config use-context my-cluster
```

### 2단계 — 노드 목록 확인

```bash
kubectl get nodes -o wide
```

출력 예시:
```
NAME          STATUS   ROLES           AGE   VERSION   INTERNAL-IP    OS-IMAGE
master-node   Ready    control-plane   5d    v1.28.0   192.168.1.10   Ubuntu 22.04
worker-01     Ready    <none>          5d    v1.28.0   192.168.1.11   Ubuntu 22.04
worker-02     Ready    <none>          5d    v1.28.0   192.168.1.12   Ubuntu 22.04
```

노드 목록은 이 클러스터가 실제로 어떤 실행 자원을 갖고 있는지 보여 줍니다. Kubernetes가 논리적인 제어 시스템처럼 보여도, 결국 워크로드는 워커 노드 위에서 돌아갑니다.

### 3단계 — 네임스페이스 확인

```bash
kubectl get namespaces
```

출력 예시:
```
NAME              STATUS   AGE
default           Active   5d
kube-node-lease   Active   5d
kube-public       Active   5d
kube-system       Active   5d
```

네임스페이스는 Kubernetes에서 가장 기본적인 격리 단위입니다. 워크로드를 그냥 한곳에 모두 넣는 대신, 환경이나 팀 단위로 나눠 운영하기 시작하는 출발점이라고 보면 됩니다.

### 4단계 — 시스템 파드 보기

```bash
kubectl -n kube-system get pods
```

출력 예시:
```
NAME                                   READY   STATUS    RESTARTS   AGE
coredns-5dd5756b68-4j9lm              1/1     Running   0          5d
etcd-master-node                      1/1     Running   0          5d
kube-apiserver-master-node            1/1     Running   0          5d
kube-controller-manager-master-node   1/1     Running   0          5d
kube-scheduler-master-node            1/1     Running   0          5d
```

`kube-system` 네임스페이스를 보면 클러스터가 스스로를 운영하기 위해 어떤 구성요소를 띄우는지 감이 옵니다. Kubernetes는 단일 바이너리 하나가 아니라 여러 컴포넌트가 함께 움직이는 시스템이라는 점이 여기서 드러납니다.

### 5단계 — 클러스터 상태 확인

```bash
kubectl cluster-info
```

`cluster-info`는 클러스터 접근 경로를 빠르게 확인할 때 유용합니다. 처음에는 단순 조회처럼 보이지만, 실제 운영에서는 API 서버 접근 문제를 확인하는 첫 단계가 되기도 합니다.

## 검증 흐름

```bash
kubectl config current-context
kubectl get nodes -o wide
kubectl cluster-info
```

**예상되는 결과:** 현재 컨텍스트 이름이 먼저 보이고, 이어서 노드 목록과 API 서버 엔드포인트가 정상적으로 출력돼야 합니다. 최소한 `Ready` 상태 노드 한 개 이상과 접근 가능한 control plane 주소를 확인할 수 있어야 합니다.

**먼저 의심할 실패 모드:**

- `current-context`가 예상한 클러스터가 아니면 잘못된 kubeconfig를 보고 있을 가능성이 큽니다.
- `kubectl get nodes`가 timeout 나면 인증 정보보다 네트워크 경로나 API 서버 가용성을 먼저 확인하는 편이 빠릅니다.
- `cluster-info`는 되는데 노드가 `NotReady`면 Kubernetes 개념 문제가 아니라 클러스터 상태 문제입니다.

## 트러블슈팅 시나리오

### 시나리오 1: 노드가 NotReady 상태

```bash
# 노드 상세 확인
kubectl describe node worker-01

# 노드에서 kubelet 로그 확인
journalctl -u kubelet -n 50

# 자주 나오는 원인
# - 디스크 공간 부족 (Condition: DiskPressure)
# - 메모리 부족 (Condition: MemoryPressure)
# - 네트워크 플러그인 오류 (Condition: NetworkUnavailable)
```

### 시나리오 2: kubectl 명령이 응답 없음

```bash
# API 서버 직접 접근 테스트
curl -k https://<api-server-ip>:6443/healthz

# kubeconfig 파일 확인
kubectl config view

# 인증서 만료 확인 (kubeadm 기반 클러스터)
kubeadm certs check-expiration
```

### 시나리오 3: 잘못된 컨텍스트에 명령 실행

```bash
# 현재 컨텍스트 확인 필수
kubectl config current-context

# 특정 컨텍스트로 단일 명령 실행 (전환 없이)
kubectl --context=staging-cluster get pods
```

## 자주 하는 실수

| 실수 | 증상 | 올바른 접근 |
|---|---|---|
| Kubernetes를 컨테이너와 동일시 | "컨테이너만 잘 돌리면 된다"는 사고방식 | 오케스트레이터 관점에서 원하는 상태 모델 이해 |
| 노드만 늘리면 해결된다고 생각 | 노드 추가 후에도 장애 지속 | 애플리케이션 설계와 리소스 제한을 함께 검토 |
| etcd 직접 수정 시도 | 클러스터 상태 불일치 | API 서버를 통한 상태 변경만 허용 |
| 컨텍스트 확인 없이 명령 실행 | 운영 클러스터에 개발 설정 적용 | 모든 작업 전 `kubectl config current-context` 확인 |
| 규모 무관하게 Kubernetes 도입 | 오버엔지니어링, 운영 부담 증가 | 컨테이너 수 기준으로 도구 선택 (소규모: Compose) |

## 실무에서는 이렇게 봅니다

실무에서는 EKS, GKE, AKS 같은 관리형 Kubernetes를 기본 선택지로 두는 경우가 많습니다. 이유는 단순합니다. 팀이 직접 운영하고 싶은 것은 대개 애플리케이션이지, 컨트롤 플레인 자체가 아니기 때문입니다.

시니어 엔지니어는 Kubernetes를 볼 때 기능 목록보다 멘탈 모델을 먼저 봅니다. 원하는 상태를 선언하는 도구인지, 현재 상태를 그쪽으로 계속 밀어 붙이는 제어 시스템인지, 그리고 그 제어를 사람이 어디까지 직접 맡아야 하는지부터 구분합니다. 이 관점이 있어야 뒤에서 Deployment와 HPA를 볼 때도 흐름이 이어집니다.

```bash
# 실무에서 자주 쓰는 첫 진단 명령 모음
kubectl get nodes -o wide                    # 노드 전체 상태
kubectl get pods -A --field-selector=status.phase!=Running  # 비정상 파드 전체
kubectl top nodes                             # 노드 자원 사용량
kubectl get events --sort-by=.lastTimestamp  # 최근 이벤트 시간순
```

## 운영 체크리스트

- [ ] 적용 전 현재 컨텍스트를 확인했는가
- [ ] 워크로드를 네임스페이스로 나눌 계획이 있는가
- [ ] 원하는 상태를 YAML로 관리할 준비가 되었는가
- [ ] 관리형 Kubernetes를 먼저 검토했는가
- [ ] 컨트롤 플레인 컴포넌트 역할을 팀이 이해하고 있는가
- [ ] etcd 백업 전략을 마련했는가 (자체 운영 클러스터의 경우)

## 연습 문제

1. 컨트롤 플레인의 역할을 한 줄로 설명해 보세요.
2. 원하는 상태가 왜 Kubernetes의 핵심인지 한 줄로 적어 보세요.
3. Kubernetes 도입을 미루는 편이 나은 상황을 하나 떠올려 보세요.
4. `kubectl get nodes`가 timeout 날 때 가장 먼저 확인할 것은 무엇인가요?
5. kube-system 네임스페이스에 어떤 파드가 있어야 하는지 나열해 보세요.

## 마무리와 다음 글

이 글에서는 Kubernetes를 컨테이너 실행 도구가 아니라 원하는 상태를 유지하는 오케스트레이터로 보는 기본 관점을 잡았습니다. 컨트롤 플레인, 워커 노드, `kubectl`, 네임스페이스 같은 용어도 결국 이 모델 안에서 이해해야 서로 연결됩니다.

다음 글에서는 이 전체 시스템이 실제로 다루는 가장 작은 배포 단위인 Pod를 보겠습니다. Kubernetes의 많은 추상화는 결국 Pod를 중심으로 쌓여 있습니다.

## 정리

Kubernetes는 '컨테이너를 많이 돌리는 도구'가 아니라 원하는 상태(desired state)를 선언하면 시스템이 그 상태로 계속 수렴하도록 만드는 오케스트레이터입니다 — 사람이 명령형으로 맞추던 일을 컨트롤러 루프에 위임한다는 한 가지 발상이 모든 리소스 설계의 출발점입니다. 이 글에서는 한눈에 보는 구조부터 마무리와 다음 글까지 이 원칙을 구체적으로 살펴봤습니다. 핵심은 개념을 외우는 것이 아니라 실무에서 어떤 판단을 바꾸는지 이해하는 데 있습니다.

## 처음 질문으로 돌아가기

- **오케스트레이션이라는 말은 실제로 무엇을 대신해 줄까요?**
  - 사람이 수동으로 하던 배치, 복구, 교체, 스케일링 결정을 컨트롤러 루프가 대신합니다. `kubectl`이 직접 컨테이너를 띄우지 않고 API 서버에 원하는 상태를 전달하면, 이후는 시스템이 맞춥니다.
- **컨트롤 플레인과 워커 노드는 어떤 식으로 역할을 나눌까요?**
  - 컨트롤 플레인은 상태를 저장하고 스케줄을 결정하며 컨트롤러를 실행합니다. 워커 노드는 kubelet이 지시를 받아 실제로 컨테이너를 실행합니다.
- **원하는 상태 모델이 왜 Kubernetes의 핵심 철학일까요?**
  - 사람이 명령형으로 매번 상태를 맞추지 않아도, 선언한 목표를 시스템이 계속 유지하기 때문입니다. 이 차이가 재현성과 자동 복구의 출발점입니다.

<!-- toc:begin -->
## 시리즈 목차

- **Kubernetes 101 (1/10): Kubernetes란 무엇인가? (현재 글)**
- [Kubernetes 101 (2/10): Pod](./02-pod.md)
- [Kubernetes 101 (3/10): Deployment](./03-deployment.md)
- [Kubernetes 101 (4/10): Service](./04-service.md)
- [Kubernetes 101 (5/10): Ingress](./05-ingress.md)
- [Kubernetes 101 (6/10): ConfigMap과 Secret](./06-configmap-and-secret.md)
- [Kubernetes 101 (7/10): Volume](./07-volume.md)
- [Kubernetes 101 (8/10): HPA](./08-hpa.md)
- [Kubernetes 101 (9/10): Helm](./09-helm.md)
- [운영 관점의 Kubernetes](./10-kubernetes-in-operation.md)

<!-- toc:end -->
