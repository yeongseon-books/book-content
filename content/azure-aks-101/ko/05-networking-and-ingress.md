---
title: 네트워킹과 Ingress — 클러스터 안과 밖을 잇는 길
series: azure-aks-101
episode: 5
language: ko
status: ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- Azure
- AKS
- Kubernetes
- Cloud
last_reviewed: '2026-04-29'
---

# 네트워킹과 Ingress — 클러스터 안과 밖을 잇는 길

> Azure Kubernetes Service 101 시리즈 (5/7)

AKS를 쓰다 막히는 지점은 대개 네트워크입니다. Pod끼리는 왜 되는데 외부에서 안 붙는지, Service는 있는데 도메인 라우팅은 왜 안 되는지, 서브넷을 왜 그렇게 크게 잡아야 하는지, 처음엔 전부 비슷한 문제처럼 보입니다. 하지만 층을 나누면 정리가 됩니다.

이번 글은 AKS 네트워킹을 두 층으로 나눠 봅니다. 첫째는 Pod IP를 어떻게 다루는지, 둘째는 외부 HTTP 요청을 어떻게 클러스터 안 Service까지 보내는지입니다. 이 둘을 분리해 보면 Azure CNI Overlay를 왜 새 클러스터의 기본 추천으로 보는지도 자연스럽게 읽힙니다.

---

## 요청 경로부터 먼저 보자

![Ingress 앞단의 외부 요청 흐름](../../../assets/azure-aks-101/05/05-01-start-with-the-request-path.ko.png)
외부 요청 관점에서 보면 이 그림입니다. 4화에서 본 Service가 클러스터 내부의 고정 진입점이라면, Ingress는 그 앞단의 HTTP 라우터입니다.

반면 Pod IP와 노드 서브넷 문제는 이 그림의 더 아래층입니다. 즉 **트래픽 경로 설계**와 **IP 할당 모델**은 관련 있지만 같은 문제는 아닙니다.

---

## AKS 네트워킹에서 먼저 결정할 것

클러스터를 만들 때 네트워킹은 꽤 이른 시점에 결정됩니다.

- Pod IP를 어떤 방식으로 할당할 것인가
- 노드와 Pod가 같은 VNet 주소 체계를 쓸 것인가
- 외부에서 Pod IP를 직접 볼 필요가 있는가
- 클러스터 수와 노드 수가 어느 정도까지 커질 것인가

AKS 문서 기준으로 새 클러스터에는 **Azure CNI Overlay**를 먼저 검토하는 흐름이 가장 자연스럽습니다.

---

## kubenet, Azure CNI, Azure CNI Overlay

### 1) kubenet

kubenet은 오래된 기본 선택지였습니다.

- 노드는 VNet 서브넷 IP를 가집니다.
- Pod는 별도 논리 주소 공간을 씁니다.
- 라우팅과 NAT가 추가로 개입합니다.
- IP를 아끼는 데 유리했습니다.

하지만 AKS 문서 기준으로 kubenet은 **2028년 3월 31일 지원 종료 예정**입니다. 새 클러스터에서 장기 선택지로 보기 어렵습니다.

### 2) Azure CNI

Azure CNI의 flat 모델에서는 Pod가 VNet 쪽 IP를 직접 받습니다.

- 외부 네트워크와의 직접 연결성이 좋습니다.
- 대신 IP 계획이 빡빡해질 수 있습니다.
- 큰 비연속 서브넷 공간을 미리 잡아야 하는 부담이 생길 수 있습니다.

### 3) Azure CNI Overlay

Azure CNI Overlay는 새 클러스터에서 가장 먼저 추천할 만한 선택지입니다.

- Pod는 VNet과 분리된 논리 CIDR을 씁니다.
- VNet IP를 아끼기 쉽습니다.
- 관리가 단순한 편입니다.
- 대규모 확장성 측면에서도 유리합니다.

직관적으로 말하면, Azure CNI Overlay는 **Azure 통합을 유지하면서도 Pod IP 소비 압박을 크게 줄인 모델**입니다.

---

## 세 모델을 한 그림으로 비교

![세 가지 AKS 네트워크 모델 비교](../../../assets/azure-aks-101/05/05-02-three-models-on-one-diagram.ko.png)
겉으로 보면 kubenet과 Overlay가 비슷해 보일 수 있습니다. 하지만 지원 방향과 운영 경험은 다릅니다. 실무 질문은 “오버레이냐 아니냐”보다 **Azure에서 앞으로 무엇을 장기 지원하고 추천하느냐**에 더 가깝습니다. 그 답이 현재는 Azure CNI Overlay입니다.

---

## 새 클러스터에서는 무엇을 권하나

대부분의 새 AKS 클러스터에는 다음처럼 생각하면 무난합니다.

- 특별한 이유가 없다면 **Azure CNI Overlay** 우선 검토
- Pod IP가 외부 네트워크에서 직접 보여야 하는 강한 요구가 있으면 flat 모델 검토
- kubenet은 신규 선택보다는 기존 클러스터 마이그레이션 대상에 가깝게 보기

이 판단은 네트워크 팀과 플랫폼 팀이 함께 해야 합니다. CIDR 설계는 나중에 바꾸기 싫은 축이기 때문입니다.

---

## Service는 L4, Ingress는 L7

이 구분이 매우 중요합니다.

### Service

- TCP/UDP 수준의 접근 지점
- Pod 집합에 안정적인 가상 IP와 DNS 부여
- LoadBalancer 타입이면 클라우드 LB와 연결 가능

### Ingress

- HTTP/HTTPS 레벨 라우팅
- 호스트 기반, 경로 기반 라우팅 가능
- TLS 종료 가능
- 여러 Service를 하나의 진입점 뒤에 둘 수 있음

단일 앱 하나만 잠깐 공개할 때는 LoadBalancer Service로 끝낼 수도 있습니다. 하지만 앱이 둘만 되어도 대개 Ingress가 필요해집니다.

---

## Ingress 컨트롤러가 꼭 필요한 이유

Ingress 리소스는 “이런 라우팅을 원한다”는 선언일 뿐입니다. 실제로 그 규칙을 읽고 프록시를 구성하는 컨트롤러가 있어야 합니다.

AKS에서 자주 나오는 선택지는 세 가지입니다.

### NGINX Ingress Controller

가장 익숙한 선택지입니다.

- 커뮤니티 사용량이 많습니다.
- 문서와 예제가 풍부합니다.
- Ingress 개념 학습에 좋습니다.

### Application Gateway Ingress Controller (AGIC)

Azure Application Gateway를 L7 진입점으로 쓰는 방식입니다.

- Application Gateway 기능을 활용할 수 있습니다.
- WAF, TLS, Azure 네트워크 통합 관점에서 매력적일 수 있습니다.
- 클러스터 안의 Pod가 Azure 리소스를 제어하는 구조를 이해해야 합니다.

### Application Routing add-on

AKS가 제공하는 관리형 NGINX 경로입니다.

- Microsoft가 권장하는 쉬운 진입점입니다.
- Azure DNS, Key Vault 통합이 좋습니다.
- 운영면을 덜 직접 만지고 싶을 때 편합니다.

입문 단계에서는 “NGINX는 가장 흔한 형태, AGIC는 Application Gateway 기반, Application Routing add-on은 AKS가 관리해 주는 NGINX” 정도로 잡아 두면 충분합니다.

다만 2026년 기준으로는 한 문장을 더 붙여야 합니다. 업스트림 `kubernetes/ingress-nginx`는 이미 retirement 단계에 들어가 read-only 아카이브 상태이므로, 새 설계의 장기 투자 방향으로 보기는 어렵습니다. 그렇다고 AKS의 Application Routing add-on까지 바로 버려야 한다는 뜻은 아닙니다. AKS 관리형 NGINX 경로는 Microsoft가 계속 지원하고 있어서, 빠르게 관리형 Ingress를 쓰고 싶은 새 클러스터에도 여전히 유효합니다. 다만 장기 방향은 `gateway.networking.k8s.io` 기반의 **Gateway API**입니다. AKS도 application routing의 Gateway API 구현을 제공하므로, 기존 ingress-nginx 워크로드는 App Routing으로 옮기기 쉽고, 2026년 이후 신규 설계는 Gateway API를 먼저 평가하는 편이 더 미래지향적입니다.

---

## Ingress 예시

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: fastapi-hello
spec:
  ingressClassName: webapprouting.kubernetes.azure.com
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: fastapi-hello
                port:
                  number: 80
```

이 예시는 Application Routing add-on의 ingress class를 쓰는 예입니다. 핵심은 단순합니다. `api.example.com/` 요청을 `fastapi-hello` Service로 보냅니다.

즉 Ingress는 Pod와 직접 대화하지 않고, **대체로 Service를 대상으로 삼습니다**.

---

## AGIC와 NGINX의 감각 차이

둘 다 Ingress를 읽지만, 구현 위치가 다릅니다.

![NGINX와 AGIC의 배치 위치 차이](../../../assets/azure-aks-101/05/05-03-nginx-and-agic-feel-different-because-th.ko.png)
NGINX는 클러스터 안 프록시라는 느낌이 강하고, AGIC는 Azure 네이티브 L7 게이트웨이를 클러스터 앞단으로 두는 느낌이 강합니다. 어느 쪽이 더 낫다기보다, 운영 주체와 기존 Azure 네트워크 자산에 따라 선택이 갈립니다.

---

## TLS 종료는 어디서 하나

보통 두 위치 중 하나입니다.

- Ingress 컨트롤러에서 종료
- Application Gateway 같은 외부 게이트웨이에서 종료

입문 단계에서는 “TLS 종료도 Ingress 계층의 일” 정도로 이해하면 충분합니다. Service는 L4 수준의 연결을 제공할 뿐, 도메인 인증서 운용의 중심은 아닙니다.

---

## 네트워크 설계에서 초반에 자주 하는 실수

### kubenet을 신규 기본값처럼 생각함

현재 방향은 아닙니다. 기존 자산이 아니라면 Azure CNI Overlay부터 검토하는 편이 안전합니다.

### Pod IP 설계를 나중 문제로 미룸

IPAM 방식은 나중에 바꾸기 싫은 축입니다. 클러스터 수, 노드 수, peering, 온프레미스 연결까지 같이 봐야 합니다.

### 외부 공개를 모두 LoadBalancer Service로만 해결하려 함

앱이 하나일 때는 되지만, 서비스 수가 늘면 Ingress 계층이 필요해집니다.

---

## FastAPI 예시를 여기 다시 올려 보면

3화의 FastAPI Service가 `LoadBalancer`였다면, 오늘부터는 다음 식으로 진화할 수 있습니다.

1. Service를 `ClusterIP`로 바꾼다.
2. 앞단에 Ingress를 둔다.
3. 한 IP 또는 도메인 집합에서 여러 Service를 경로로 분기한다.

이 구조가 되면 `/api`는 FastAPI API로, `/admin`은 다른 관리 UI로 보낼 수 있습니다. 운영면에서는 공개 지점을 줄이고, 인증서 관리도 더 일관되게 가져갈 수 있습니다.

---

## 다음 화에서 이어질 질문

트래픽이 늘어나면 어떤 일이 벌어질까요.

- Pod를 더 늘려야 하나
- 노드를 더 늘려야 하나
- 외부 이벤트가 들어올 때만 0에서 깨어나게 할 수 있나

이 질문이 6화의 HPA, Cluster Autoscaler, KEDA입니다. 5화까지 오면 이제 스케일링 얘기를 할 준비가 끝난 셈입니다.

---

이 글은 Azure Kubernetes Service 101 시리즈의 5화입니다. 앞선 글에서 Pod, Deployment, Service가 클러스터 내부의 구조였다면, 이번 화는 그 구조를 외부 요청과 Azure 네트워크에 연결하는 층을 설명했습니다. 다음 6화에서는 이 네트워크 위로 들어오는 부하에 맞춰 Pod 수와 Node 수가 어떻게 늘어나는지 보게 됩니다.

---

<!-- blog-only:start -->
다음 글: [스케일링 — HPA, Cluster Autoscaler, KEDA](./06-scaling-hpa-ca-keda.md)
<!-- blog-only:end -->

<!-- toc:begin -->
## 시리즈 목차

- [Azure Kubernetes Service란? — 직접 운영하지 않아도 되는 Kubernetes](./01-what-is-aks.md)
- [클러스터 아키텍처 — Control Plane과 Node Pool](./02-cluster-architecture.md)
- [첫 클러스터 만들고 앱 배포하기 — Python/FastAPI](./03-first-cluster-and-deploy.md)
- [Pod·Deployment·Service — 워크로드를 표현하는 세 가지 방식](./04-pod-deployment-service.md)
- **네트워킹과 Ingress — 클러스터 안과 밖을 잇는 길 (현재 글)**
- 스케일링 — HPA, Cluster Autoscaler, KEDA (예정)
- 모니터링과 운영 — Container Insights, 로그, 알람 (예정)

<!-- toc:end -->

---

## 참고 자료

### 공식 문서
- [Concepts - CNI Networking in AKS](https://learn.microsoft.com/en-us/azure/aks/concepts-network-cni-overview)
- [Configure kubenet networking in AKS](https://learn.microsoft.com/en-us/azure/aks/configure-kubenet)
- [Concepts - Ingress Networking in AKS](https://learn.microsoft.com/en-us/azure/aks/concepts-network-ingress)
- [AKS managed NGINX ingress with the application routing add-on](https://learn.microsoft.com/en-us/azure/aks/app-routing)
- [What is Application Gateway Ingress Controller?](https://learn.microsoft.com/en-us/azure/application-gateway/ingress-controller-overview)

### 관련 시리즈
- [Azure App Service 101](../../azure-app-service-101/ko/02-request-lifecycle.md) — 외부 요청이 애플리케이션 인스턴스로 들어가는 경로를 비교할 때
- [Azure Functions 101](../../azure-functions-101/ko/01-what-is-azure-functions.md) — HTTP 엔드포인트 노출이 플랫폼에 더 많이 추상화된 모델과 비교할 때

Tags: Azure, AKS, Kubernetes, Cloud
