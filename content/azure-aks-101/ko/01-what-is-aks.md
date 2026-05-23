---
title: "Azure Kubernetes Service 101 (1/7): Azure Kubernetes Service란? — 직접 운영하지 않아도 되는 Kubernetes"
series: azure-aks-101
episode: 1
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
seo_description: 컨테이너를 몇 개 띄우는 일은 이제 어렵지 않습니다. 어려운 쪽은 그 다음입니다.
---

# Azure Kubernetes Service 101 (1/7): Azure Kubernetes Service란? — 직접 운영하지 않아도 되는 Kubernetes

컨테이너 몇 개를 띄우는 일 자체는 이제 특별하지 않습니다. 어려운 지점은 그다음입니다. 장애가 난 Pod를 다시 살리고, 트래픽이 늘면 복제본과 노드를 함께 늘리고, 외부 요청을 안전하게 받아 주고, 로그와 메트릭을 한곳에 모아 운영 판단까지 내려야 비로소 플랫폼이 됩니다.

Kubernetes는 바로 그 운영 문제를 표준화한 시스템입니다. 다만 직접 운영하는 Kubernetes는 학습비와 운영비가 함께 큽니다. etcd와 API server를 직접 다룰 필요는 없어도, 적어도 그 경계가 어떻게 생겼는지 이해해야 안정적으로 운영할 수 있습니다.

여기서는 AKS를 “Azure에서 쓰는 Kubernetes” 정도로 흐리게 보지 않고, **Azure가 무엇을 대신 맡고 사용자는 무엇을 계속 책임져야 하는지**를 먼저 분명하게 정리하겠습니다. 이 책임 경계가 선명해야 이후의 클러스터 구조, 배포, 네트워킹, 스케일링, 운영 이야기가 흔들리지 않습니다.

![Azure Kubernetes Service 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/azure-aks-101/01/01-01-the-big-picture-one-aks-cluster-at-a-gla.ko.png)
*Azure Kubernetes Service 101 1장 흐름 개요*
> Azure Kubernetes Service란? — 직접 운영하지 않아도 되는 Kubernetes의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 먼저 던지는 질문

- AKS는 self-managed Kubernetes와 비교할 때 정확히 무엇을 대신 운영해 줄까요?
- 관리형 Kubernetes라고 해도 왜 여전히 `kubectl`, YAML, Service, Ingress를 이해해야 할까요?
- AKS 비용은 어디에서 발생하고, 왜 “클러스터 요금”보다 노드와 주변 리소스가 더 중요할까요?

## 왜 이 글이 중요한가

AKS를 처음 볼 때 가장 흔한 오해는 “관리형이면 운영이 거의 사라진다”는 기대입니다. 하지만 실제로 사라지는 것은 Kubernetes 전체가 아니라 **Control Plane 운영의 상당 부분**입니다. 워크로드 배치, 네트워크 노출, 스케일 정책, 비용 통제, 관측성 설계는 여전히 사용자 책임입니다.

이 구분이 흐리면 문제를 잘못된 층에서 보기 시작합니다. 예를 들어 Pod가 Pending인데도 Control Plane 장애부터 의심하거나, 반대로 노드 풀 설계가 핵심인데 “AKS가 알아서 해 주지 않나”라고 생각하며 지나치기 쉽습니다. 운영 문제는 대개 추상화가 끝나는 지점에서 드러나므로, 서비스 설명보다 책임 경계가 더 중요합니다.

또 하나 중요한 이유는 비교 기준입니다. AKS는 단순히 Azure의 컨테이너 서비스 하나가 아닙니다. App Service보다 낮은 추상화, self-managed Kubernetes보다 높은 추상화에 놓인 선택지입니다. 이 위치를 이해해야 플랫폼 선택도 더 정확해집니다.

## 핵심 관점

AKS를 배울 때 가장 실용적인 출발점은 기능 목록이 아니라 책임 경계입니다. 저는 AKS를 볼 때 먼저 “누가 Control Plane을 운영하는가”, “누가 Node Pool을 설계하는가”, “누가 워크로드와 네트워크 정책을 책임지는가”를 나눠 봅니다. 이 셋이 구분되면 대부분의 운영 질문이 훨씬 덜 추상적으로 바뀝니다.

이 관점이 좋은 이유는 Kubernetes 개념이 그대로 남아 있기 때문입니다. AKS를 쓴다고 해서 Deployment, Service, Ingress, HPA가 사라지지 않습니다. Azure는 클러스터 운영의 일부를 대신 맡아 주지만, 애플리케이션 플랫폼 설계까지 대체해 주지는 않습니다.

이 글의 목적도 바로 여기에 있습니다. AKS를 “쉽게 쓸 수 있는 Kubernetes”라는 문장으로 끝내지 않고, **어떤 어려움은 사라지고 어떤 어려움은 남는지**를 분리해서 보는 기준을 만드는 것입니다.

> AKS는 Kubernetes를 감추는 서비스가 아니라, Kubernetes를 유지한 채 Control Plane 운영 부담의 큰 부분을 Azure가 대신 맡아 주는 서비스입니다.

## 핵심 개념

### 전체 그림부터 먼저 잡아야 합니다

AKS를 처음 볼 때는 세부 설정으로 바로 내려가기보다 전체 구조를 먼저 보는 편이 좋습니다. 이후 글들은 모두 아래 그림의 특정 상자를 확대하는 과정이라고 생각하면 됩니다.

이 그림이 중요한 이유는 모든 화가 여기서 출발하기 때문입니다. 2화는 Control Plane과 Node Pool 경계를, 3화와 4화는 워크로드 객체를, 5화는 네트워킹을, 6화는 스케일링을, 7화는 운영과 관측을 다룹니다. 한 장의 지도를 먼저 붙잡아 두면 뒤의 디테일이 어디에 속하는지 빠르게 정리됩니다.

### 한 문장으로 정의하면 이렇습니다

AKS는 **Azure가 Kubernetes Control Plane을 운영하고, 사용자는 주로 Node Pool과 워크로드를 운영하는 관리형 Kubernetes 서비스**입니다.

이 정의에는 AKS를 이해하는 데 필요한 핵심이 거의 다 들어 있습니다.

- Azure는 API server, scheduler, etcd 같은 Control Plane 계층을 배치하고 운영합니다.
- 사용자는 노드 풀을 만들고, 그 위에 Deployment, Pod, Service, Ingress 같은 Kubernetes 객체를 올립니다.
- Azure는 업그레이드와 통합 운영의 많은 부분을 줄여 주지만, 애플리케이션 아키텍처와 운영 품질까지 대신 보장하지는 않습니다.

즉 AKS의 핵심은 “Kubernetes를 안 써도 된다”가 아니라 “Kubernetes를 직접 처음부터 끝까지 운영하지 않아도 된다”에 있습니다.

### 관리형이라고 해서 운영이 없어지는 것은 아닙니다

“관리형”이라는 말은 추상적이면 별 의미가 없습니다. 실무에서 중요한 것은 이 말이 실제로 무엇을 바꾸는가입니다.

![Azure와 사용자의 운영 책임 경계](https://yeongseon-books.github.io/book-public-assets/assets/azure-aks-101/01/01-02-what-managed-means-in-practice.ko.png)

*Azure와 사용자의 운영 책임 경계*

AKS를 쓰면 etcd 토폴로지나 API server 자체의 수명주기를 직접 설계하는 부담은 크게 줄어듭니다. 대신 운영의 중심은 워크로드 배치, Pod와 노드의 스케일링, 트래픽 진입점, 관측성, 비용 구조 쪽으로 이동합니다. 즉 운영이 사라지는 것이 아니라, **운영해야 할 층이 바뀌는 것**입니다.

이 구분은 기대치를 맞추는 데도 중요합니다. AKS는 잘못된 readiness probe를 자동으로 고쳐 주지 않습니다. CPU 요청값이 비현실적이거나, Service selector가 틀렸거나, 노드 풀 설계가 잘못됐다면 문제는 그대로 발생합니다. 관리형 Kubernetes는 플랫폼 운영 부담을 줄여 주지만, 워크로드 품질과 배포 설계는 여전히 사용자 책임입니다.

### 왜 self-managed Kubernetes 대신 AKS를 고를까요

직접 운영 Kubernetes가 완전히 사라진 선택지는 아닙니다. 다만 일반적인 애플리케이션 팀에게는 AKS가 훨씬 현실적인 기본값인 경우가 많습니다.

| 항목 | 직접 운영 Kubernetes | AKS |
|---|---|---|
| Control Plane 구성 | 직접 설계·운영 | Azure 관리 |
| 업그레이드 부담 | 높음 | 낮음 |
| Azure 통합 | 직접 조립 | 기본 통합 경로 다수 |
| 시작 속도 | 느림 | 빠름 |
| 제어 수준 | 높음 | 일부 제약 |

중요한 점은 “그냥 쉬워진다”가 아니라, **표준 Kubernetes는 그대로 쓰면서 플랫폼 운영의 반복 작업을 줄일 수 있다**는 것입니다. 그래서 upstream Kubernetes 문서, 오픈소스 운영 패턴, Helm 차트, 일반적인 YAML 기반 배포 습관이 대부분 그대로 이어집니다.

### 비용은 Control Plane보다 주변 리소스에서 읽어야 합니다

AKS를 처음 보는 팀이 가장 먼저 묻는 질문 중 하나는 비용입니다. headline만 기억하면 이렇습니다.

> AKS의 Control Plane은 Microsoft가 관리하며 별도 요금이 청구되지 않습니다. 실제 비용은 주로 Node Pool VM과 클러스터 주변 리소스에서 발생합니다.

하지만 실무 청구서는 이 문장보다 넓습니다.

- Node Pool VM 비용
- OS 디스크와 데이터 디스크 비용
- Load Balancer, Public IP 같은 네트워크 리소스 비용
- Azure Container Registry 저장 비용
- Log Analytics, Container Insights, Managed Prometheus 같은 관측성 비용

즉 AKS는 “클러스터 사용료”를 따지는 서비스라기보다, **클러스터를 어떤 용량과 어떤 운영 도구로 둘 것인가**를 따지는 서비스에 가깝습니다. 이후 스케일링과 모니터링 이야기가 비용과 강하게 연결되는 이유도 여기에 있습니다.

### AKS를 도입하기 전에 팀이 먼저 맞춰야 할 질문이 있습니다

AKS는 기능이 많은 서비스라서, 처음엔 “무엇을 할 수 있나”에 눈이 갑니다. 하지만 실제 도입 판단은 보통 더 현실적인 질문에서 갈립니다.

- 우리 팀은 Kubernetes 객체를 운영 언어로 받아들일 준비가 되어 있는가
- 여러 서비스가 공통 플랫폼을 공유해야 하는가
- 네트워크, 관측성, 릴리스 전략을 서비스별로 제각각 두기보다 표준화하고 싶은가
- App Service나 Container Apps보다 더 낮은 수준의 제어가 실제로 필요한가

이 질문에 대한 답이 대부분 “예”라면 AKS는 매우 설득력 있는 선택이 될 수 있습니다. 반대로 서비스 수가 적고 팀이 더 높은 추상화를 원한다면, AKS의 유연성이 장점이 아니라 학습 부담으로 느껴질 수도 있습니다.

### 이후 시리즈를 이해하려면 두 축만 먼저 붙잡으면 됩니다

이 시리즈를 따라가는 동안 가장 중요한 구조 축은 두 개입니다.

#### 1) Control Plane

Control Plane은 클러스터의 두뇌입니다.

- 원하는 상태를 저장합니다.
- Kubernetes API의 출입구가 됩니다.
- Pod를 어느 노드에 배치할지 결정합니다.

AKS에서는 이 계층을 Azure가 관리합니다.

#### 2) Node Pool

Node Pool은 실제로 컨테이너가 실행되는 VM 묶음입니다.

- system node pool은 CoreDNS, metrics-server 같은 핵심 시스템 Pod를 우선 수용합니다.
- user node pool은 애플리케이션 워크로드를 위한 공간입니다.

즉 아주 짧게 정리하면 **Control Plane은 결정하고, Node Pool은 실행합니다.** 이 한 문장이 뒤의 모든 화를 읽는 기준이 됩니다.

### AKS가 잘 맞는 팀과 그렇지 않은 팀이 있습니다

AKS는 다음 상황에서 특히 설득력이 큽니다.

- 여러 서비스가 공통 배포 플랫폼을 공유해야 할 때
- Deployment, Service, Ingress, HPA 같은 Kubernetes 표준 모델을 활용하고 싶을 때
- Azure 네트워크, Azure Monitor, Azure Container Registry와 자연스럽게 통합하고 싶을 때
- 플랫폼팀과 애플리케이션팀이 Kubernetes라는 공통 운영 언어를 쓰고 싶을 때

반대로 워크로드가 매우 작고, 팀이 Kubernetes 개념을 전혀 원하지 않으며, HTTP 앱 몇 개를 더 높은 수준의 PaaS로 빠르게 운영하는 것이 목표라면 App Service나 Container Apps가 더 경제적일 수 있습니다. 플랫폼 선택은 기능 수보다 추상화 수준이 더 중요합니다.

여기서 중요한 것은 “컨테이너를 쓰니까 AKS” 같은 단순한 결론을 피하는 것입니다. 컨테이너를 사용해도 App Service가 더 맞을 수 있고, 여러 서비스가 있어도 Container Apps가 더 맞을 수 있습니다. AKS의 강점은 Kubernetes 표준 모델을 직접 활용하면서도 Control Plane 운영 부담을 줄일 수 있다는 데 있습니다.

### Azure 안의 다른 선택지와 비교하면 위치가 더 선명해집니다

AKS는 Azure App Service, Azure Functions, Azure Container Apps와 자주 비교됩니다. 이 비교에서 중요한 질문은 “모두 코드를 실행하느냐”가 아니라 **어디까지를 플랫폼이 숨겨 주느냐**입니다.

- **Azure App Service**는 웹 앱 호스팅에 더 가까우며 런타임과 인스턴스 모델을 더 많이 숨깁니다.
- **Azure Functions**는 이벤트 기반 실행 모델이 중심이라 Pod와 Service를 직접 다루지 않습니다.
- **Azure Container Apps**는 컨테이너 중심이지만 클러스터 자체는 AKS보다 훨씬 덜 드러납니다.

AKS는 이 셋 중 raw Kubernetes에 가장 가깝습니다. 그래서 더 많은 제어를 얻는 대신, 더 많은 개념 표면적도 함께 가져옵니다. 이 시리즈가 기능 나열보다 구조와 책임 경계부터 시작하는 이유가 바로 여기에 있습니다.

실무에서는 같은 FastAPI 앱도 플랫폼에 따라 운영 언어가 크게 달라집니다. App Service에서는 인스턴스와 설정이 중심이 되고, Functions에서는 트리거와 실행 수명이 중심이 되며, AKS에서는 Deployment, Service, Ingress, HPA 같은 워크로드 객체가 중심이 됩니다. 코드보다 운영 모델이 먼저 달라진다고 생각하는 편이 더 정확합니다.

### 초반에 지워 두면 좋은 오해 두 가지가 있습니다

#### “AKS면 운영이 거의 없다”

아닙니다. Control Plane 운영 부담이 많이 줄어드는 것이지, 워크로드 운영이 사라지는 것은 아닙니다. 노드 풀 분리, 네트워크 노출, 리소스 요청, 로그 보존, 알람, 업그레이드 계획은 여전히 필요합니다.

#### “AKS는 마이크로서비스 팀만 쓰는 것”

그렇지도 않습니다. 단일 FastAPI 서비스 하나를 Deployment와 Service로 올리는 것만으로도 충분히 AKS를 시작할 수 있습니다. 오히려 작은 앱으로 시작해야 Pod, Service, Ingress, autoscaling이 어떻게 연결되는지 더 빨리 보입니다.

### 빠르게 확인하기

아직 실제 클러스터를 만들지 않았더라도, AKS 리소스를 볼 때 어떤 정보가 핵심인지 정도는 미리 감각을 잡아 둘 수 있습니다.

```bash
az aks show \
  --resource-group $RG --name $CLUSTER \
  --query '{kubernetesVersion:kubernetesVersion, fqdn:fqdn, nodeResourceGroup:nodeResourceGroup}'
```

이 명령은 Kubernetes 버전, API 엔드포인트 FQDN, 그리고 관리형 리소스가 들어가는 node resource group을 보여 줍니다. 이후 글에서 클러스터 구조를 더 자세히 볼 때도 자주 마주치는 정보들입니다.

실제 클러스터에 붙을 수 있는 상태라면 아래 세 줄까지 함께 보는 편이 더 좋습니다.

```bash
kubectl get nodes -o wide
kubectl get pods -n kube-system -o wide
kubectl get svc -A
```

이 세 명령이 주는 감각은 서로 다릅니다.

- `kubectl get nodes -o wide`는 **실행 계층이 실제로 몇 대인지**를 보여 줍니다.
- `kubectl get pods -n kube-system -o wide`는 **클러스터 핵심 구성 요소가 어느 노드에서 어떻게 떠 있는지**를 보여 줍니다.
- `kubectl get svc -A`는 **클러스터 안팎의 네트워크 진입점이 어디에 있는지**를 빠르게 보여 줍니다.

즉 AKS를 볼 때는 “Azure 리소스 정보”만 보지 말고, **노드·시스템 Pod·Service**까지 함께 봐야 책임 경계가 실제 운영 화면으로 연결됩니다.

## 문제가 생겼을 때 어느 층부터 볼지 빠르게 가르는 법

AKS를 처음 운영할 때 가장 많이 생기는 혼란은 모든 문제를 한 문장으로 묶는 것입니다. “클러스터가 이상하다”라고 말하는 순간, 사실은 서로 다른 층의 문제가 섞여 있을 가능성이 큽니다. 아래처럼 먼저 층을 나누면 훨씬 빨리 좁혀집니다.

| 보이는 증상 | 먼저 볼 층 | 첫 확인 명령 |
|---|---|---|
| `kubectl` 응답 자체가 이상하거나 느리다 | Control Plane 경계 | `az aks show --resource-group $RG --name $CLUSTER` |
| Pod가 `Pending`에 오래 머문다 | Node Pool / 스케줄링 | `kubectl get pods -A` / `kubectl describe pod <pod-name>` |
| 앱은 떴는데 외부에서 접속이 안 된다 | Service / LoadBalancer / Ingress | `kubectl get svc -A` |
| CoreDNS, metrics-server가 불안정하다 | system workload | `kubectl get pods -n kube-system -o wide` |

이 표의 목적은 모든 장애를 해결하는 것이 아닙니다. **첫 시선이 어디로 가야 하는지**를 맞추는 것입니다. AKS는 관리형 서비스라서 더 단순해 보일 수 있지만, 실제 장애는 여전히 Kubernetes 층에서 드러납니다. 그래서 “Azure가 맡는 층”과 “우리가 맡는 층”을 구분하는 일은 개념 설명이 아니라 첫 번째 장애 대응 기술에 가깝습니다.

## 아주 짧은 실전 시나리오로 감각 붙이기

개념을 현실로 붙이는 가장 빠른 방법은 클러스터 하나를 만든 뒤, 어떤 명령이 어떤 층을 보여 주는지 눈으로 확인하는 것입니다. 아래 예시는 production 설정이 아니라 책임 경계를 관찰하기 위한 최소 시나리오입니다.

```bash
# 1) Azure 리소스 계층: 클러스터 생성
az aks create \
  --resource-group "$RG" \
  --name "$CLUSTER" \
  --node-count 1 \
  --network-plugin azure \
  --network-plugin-mode overlay \
  --generate-ssh-keys

# 2) Kubernetes 계층 연결
az aks get-credentials --resource-group "$RG" --name "$CLUSTER"

# 3) 실행 계층 관찰
kubectl get nodes -o wide
kubectl get pods -n kube-system -o wide
```

여기서 첫 번째 명령은 Azure Resource Manager에 클러스터를 만드는 작업이고, 두 번째부터는 Kubernetes API를 조회하는 작업입니다. 즉 같은 AKS를 다루더라도 명령이 보여 주는 관점이 다릅니다. 운영팀이 장애 대응 문서에서 `az`와 `kubectl` 섹션을 분리하는 이유가 바로 이것입니다.

또한 클러스터를 만든 뒤 `kubectl get svc -A`를 함께 보면 “어떤 트래픽 진입점이 이미 생겼는가”를 빠르게 읽을 수 있습니다. 입문 단계에서는 복잡한 다이어그램보다 이 세 가지 화면을 자주 보는 습관이 더 강력합니다.

## 흔히 헷갈리는 지점

- AKS를 쓰면 Kubernetes 개념을 몰라도 된다고 생각하기 쉽지만, 실제로는 Kubernetes 개념이 그대로 남습니다.
- 관리형이므로 운영이 거의 없다고 생각하기 쉽지만, 사라지는 것은 주로 Control Plane 운영 부담입니다.
- AKS 비용을 “클러스터 사용료”로만 보려 하지만, 실제로는 노드와 네트워크와 관측성 비용이 더 중요합니다.
- AKS가 무조건 마이크로서비스용이라고 오해하기 쉽지만, 작은 FastAPI 서비스 하나로도 충분히 시작할 수 있습니다.
- App Service보다 무조건 더 좋다고 생각하기 쉽지만, 이는 추상화 수준과 운영 요구에 따라 달라집니다.

## 운영 체크리스트

- [ ] AKS의 책임 분담 모델을 팀이 같은 문장으로 설명할 수 있는가
- [ ] Control Plane과 Node Pool 중 어느 층이 사용자 책임인지 명확히 정리했는가
- [ ] 노드 VM, 디스크, 네트워크, 관측성 비용까지 포함해 대략적인 비용 구조를 읽었는가
- [ ] AKS가 App Service 또는 Container Apps보다 더 적합한 이유를 워크로드 기준으로 설명할 수 있는가
- [ ] 이후 설계를 위해 Control Plane과 Node Pool이라는 두 축을 팀 공통 멘탈 모델로 맞췄는가

## 정리

이 글의 핵심은 AKS를 “Azure에서 Kubernetes를 쓰는 서비스”로만 보지 않는 것입니다. 더 정확한 설명은 Azure가 Control Plane 운영의 상당 부분을 맡고, 사용자는 Node Pool과 워크로드, 네트워크, 관측성, 비용 설계를 중심으로 운영하는 관리형 Kubernetes라는 것입니다.

이 관점을 먼저 잡아 두면 뒤의 모든 주제가 더 현실적으로 이어집니다. 클러스터 아키텍처는 책임 경계의 구체적 형태가 되고, 첫 배포 실습은 그 경계 위에 워크로드를 올리는 일이 되며, 네트워킹과 스케일링과 운영은 모두 같은 모델의 다른 층으로 읽히게 됩니다.

시리즈의 첫 글에서 가장 중요하게 가져가야 할 문장은 이것입니다. **AKS는 Kubernetes를 대체하지 않습니다. Kubernetes를 유지한 채, 직접 운영해야 할 부담의 일부를 Azure가 대신 맡아 주는 플랫폼입니다.**

## 처음 질문으로 돌아가기

- **AKS는 self-managed Kubernetes와 비교할 때 정확히 무엇을 대신 운영해 줄까요?**
  - AKS는 `API server`, `scheduler`, `etcd`가 있는 Control Plane 운영을 Azure가 맡아 주는 서비스입니다. 대신 `kubectl get nodes -o wide`로 보게 되는 Node Pool 용량, `Deployment`·`Service`·`Ingress`로 표현하는 워크로드, 그리고 스케일링과 관측 설계는 여전히 사용자 책임입니다.
- **관리형 Kubernetes라고 해도 왜 여전히 `kubectl`, YAML, Service, Ingress를 이해해야 할까요?**
  - AKS를 써도 앱은 결국 `kubectl get svc -A`, `kubectl get pods -n kube-system -o wide` 같은 Kubernetes 표면에서 운영합니다. Azure는 Control Plane을 숨겨 주지만 `Service`, `Ingress`, YAML 선언, probe 품질 같은 워크로드 문법까지 대신 결정해 주지는 않습니다.
- **AKS 비용은 어디에서 발생하고, 왜 “클러스터 요금”보다 노드와 주변 리소스가 더 중요할까요?**
  - 본문에서 정리했듯이 비용의 중심은 `--node-count 1` 같은 노드 수와 Node Pool VM, 디스크, `Load Balancer`, `Public IP`입니다. 여기에 `Azure Container Registry`, `Log Analytics`, `Container Insights`, `Managed Prometheus`까지 붙기 때문에, AKS는 클러스터 사용료보다 주변 리소스 설계를 읽는 서비스에 가깝습니다.

<!-- toc:begin -->
## 시리즈 목차

- **Azure Kubernetes Service 101 (1/7): Azure Kubernetes Service란? — 직접 운영하지 않아도 되는 Kubernetes (현재 글)**
- Azure Kubernetes Service 101 (2/7): 클러스터 아키텍처 — Control Plane과 Node Pool (예정)
- Azure Kubernetes Service 101 (3/7): 첫 클러스터 만들고 앱 배포하기 — Python/FastAPI (예정)
- Azure Kubernetes Service 101 (4/7): Pod·Deployment·Service — 워크로드를 표현하는 세 가지 방식 (예정)
- Azure Kubernetes Service 101 (5/7): 네트워킹과 Ingress — 클러스터 안과 밖을 잇는 길 (예정)
- Azure Kubernetes Service 101 (6/7): 스케일링 — HPA, Cluster Autoscaler, KEDA (예정)
- Azure Kubernetes Service 101 (7/7): 모니터링과 운영 — Container Insights, 로그, 알람 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [What is Azure Kubernetes Service (AKS)?](https://learn.microsoft.com/en-us/azure/aks/what-is-aks)
- [Deploy an Azure Kubernetes Service (AKS) Cluster Using Azure CLI](https://learn.microsoft.com/en-us/azure/aks/learn/quick-kubernetes-deploy-cli)
- [Use system node pools in Azure Kubernetes Service (AKS)](https://learn.microsoft.com/en-us/azure/aks/use-system-pools)
- [Kubernetes core concepts for Azure Kubernetes Service (AKS)](https://learn.microsoft.com/en-us/azure/aks/concepts-clusters-workloads)

### 관련 시리즈

- [Azure App Service 101](../../azure-app-service-101/ko/) — Kubernetes까지 필요하지 않은 웹 앱 운영 모델과 비교할 때
- [Azure Functions 101](../../azure-functions-101/ko/) — 서버리스와 관리형 Kubernetes의 책임 경계를 비교할 때

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-aks-101/ko/01-what-is-aks)

Tags: Azure, AKS, Kubernetes, Cloud
