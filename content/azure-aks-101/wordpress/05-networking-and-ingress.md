---
title: "바이브코딩을 위한 Azure AKS (5/7): 네트워킹과 Ingress"
series: azure-aks-101
episode: 5
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- AzureAKS
- Ingress
- CNI
- AI코딩
seo_description: "바이브코딩을 위한 Azure AKS 5편: 네트워킹과 Ingress. Pod IP 할당 모델(CNI)과 외부 HTTP 라우팅(Ingress)을 분리해서 이해합니다."
---

# 바이브코딩을 위한 Azure AKS (5/7): 네트워킹과 Ingress

이 글은 바이브코딩을 위한 Azure AKS 시리즈의 5번째 글입니다.

AKS를 쓰다 막히는 지점은 대개 네트워크입니다. Pod끼리는 통신이 되는데 외부에서 붙지 않거나, Service는 있는데 도메인 라우팅이 되지 않거나, 서브넷이 충분해 보였는데 노드 수가 늘어나자 갑자기 IP 계획이 빡빡해집니다. 이 주제를 정리하려면 두 가지를 분리해야 합니다. 하나는 Pod가 어떤 주소 체계를 쓰는지(CNI), 다른 하나는 외부 HTTP 요청이 어떤 경로로 클러스터 안 Service까지 들어오는지(Ingress)입니다. Service와 Ingress는 같은 레이어가 아닙니다. Service는 L4(TCP/UDP), Ingress는 L7(HTTP 경로, 호스트 기반 라우팅)입니다. Azure CNI Overlay는 새 클러스터의 자연스러운 기본 선택지입니다. Pod에 가상 IP를 할당해 서브넷 IP를 절약하므로 대규모 클러스터에서 IP 고갈 문제를 줄입니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI에게 Ingress 설정 코드를 요청할 때 CNI 모델과 L4/L7 계층 구분을 명시하지 않으면, Service와 Ingress를 동일하게 다루거나 IP 고갈 위험이 있는 코드가 생성되기 때문입니다.

> AKS 네트워킹의 핵심은 Pod IP 할당(CNI)과 외부 HTTP 라우팅(Ingress)이 서로 다른 문제라는 사실을 이해하는 데 있습니다.

---

## 이 글에서 다룰 문제

- Pod IP 할당 방식과 외부 HTTP 라우팅을 왜 별개의 문제로 봐야 할까요?
- kubenet, Azure CNI, Azure CNI Overlay는 각각 어떤 운영 trade-off를 가질까요?
- Service(L4)와 Ingress(L7)는 어떻게 다르고 각각 언제 써야 할까요?
- Ingress Controller를 따로 설치해야 하는 이유는 무엇일까요?
- 이 개념을 실무에 적용하는 방법은 무엇일까요?

AKS 네트워킹을 이해하면 AI에게 "Azure CNI Overlay로 클러스터 생성 후 NGINX Ingress Controller를 Helm으로 설치하고 FastAPI 두 서비스를 /api/v1과 /api/v2 경로로 라우팅하는 Ingress YAML"을 정확하게 요청할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "AKS에서 외부 트래픽을 여러 서비스로 라우팅해줘"
→ 서비스마다 LoadBalancer 생성
→ 외부 IP 여러 개 = 비용 증가
→ Ingress 없이 L7 라우팅 불가
→ CNI 모델 고려 없음
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "AKS 네트워킹을 두 계층으로 설계해줘.
    CNI 계층: Azure CNI Overlay로 서브넷 IP 절약
    Ingress 계층: NGINX Ingress Controller(Helm) 설치
    Ingress YAML: /api/orders → orders-svc:80,
                  /api/payments → payments-svc:80
    TLS termination Ingress에서 처리 (cert-manager + Let's Encrypt)"
→ L4 Service와 L7 Ingress 역할 분리
→ 외부 IP 하나로 여러 서비스 라우팅
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| 서비스마다 LoadBalancer 생성 | 외부 IP 여러 개 = 비용 증가 + 관리 복잡 | Ingress 하나로 여러 서비스 라우팅 |
| Service와 Ingress 역할 혼동 | L4와 L7 라우팅을 같은 객체로 시도 | Service=L4, Ingress=L7 HTTP 라우팅으로 분리 |
| kubenet으로 대규모 클러스터 운영 | 노드 수 증가 시 UDR 관리 복잡, IP 고갈 | Azure CNI Overlay로 마이그레이션 계획 수립 |
| Ingress Controller 미설치 | Ingress 리소스 생성해도 동작 안 함 | NGINX 또는 App Gateway Ingress Controller 설치 필수 |
| TLS를 Ingress 대신 앱에서 직접 처리 | 인증서 관리 분산, 갱신 복잡 | Ingress에서 TLS termination, cert-manager 사용 |

## AI 협업 팁

AKS 네트워킹 관련 효과적인 AI 프롬프트 패턴:

1. **CNI 설정 요청**: "Azure CNI Overlay로 AKS 클러스터를 만드는 az aks create 명령과 기존 kubenet 대비 장점 설명 작성해줘"
2. **Ingress Controller 설치 요청**: "AKS에 NGINX Ingress Controller를 Helm으로 설치하고 LoadBalancer Service로 외부 노출하는 명령 작성해줘"
3. **Ingress YAML 요청**: "두 서비스를 /orders와 /payments 경로로 라우팅하는 Ingress YAML과 cert-manager로 TLS를 자동 발급하는 설정 작성해줘"

예시 프롬프트:
> "AKS Ingress 설정을 완성해줘. NGINX Ingress Controller Helm 설치 → Ingress YAML(orders-svc /api/orders, payments-svc /api/payments) → cert-manager + Let's Encrypt TLS → Ingress에서 TLS termination. CNI는 Azure CNI Overlay 기준."

## 운영 체크리스트

- [ ] Azure CNI Overlay로 서브넷 IP 계획을 수립했는가?
- [ ] Ingress Controller를 설치했는가?
- [ ] Service(L4)와 Ingress(L7) 역할을 분리해서 사용하는가?
- [ ] TLS termination을 Ingress에서 처리하는가?
- [ ] 다음 글에서 HPA, Cluster Autoscaler, KEDA 스케일링을 이해할 준비가 됐는가?

## 처음 질문으로 돌아가기

AKS 네트워킹을 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. CNI 모델과 L4/L7 계층을 명시한 사람과 그렇지 않은 사람이 AI에게 받는 네트워킹 설정 코드의 완성도는 크게 다릅니다.

## 정리

네트워킹과 Ingress 편은 바이브코딩을 위한 Azure AKS에서 클러스터 안과 밖을 잇는 네트워크 계층을 이해하는 핵심 단계입니다. Pod IP 할당(CNI)과 외부 HTTP 라우팅(Ingress)의 분리, Service L4와 Ingress L7의 역할 차이를 이해했습니다. 다음 글에서는 HPA, Cluster Autoscaler, KEDA 스케일링을 다룹니다.

## 참고 자료

- [AKS networking concepts](https://docs.microsoft.com/azure/aks/concepts-network)
- [Azure CNI Overlay in AKS](https://docs.microsoft.com/azure/aks/azure-cni-overlay)
- [NGINX Ingress Controller for AKS](https://docs.microsoft.com/azure/aks/ingress-basic)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-aks-101/ko/05-networking-and-ingress)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Azure AKS (1/7): Azure Kubernetes Service란?
- 바이브코딩을 위한 Azure AKS (2/7): 클러스터 아키텍처
- 바이브코딩을 위한 Azure AKS (3/7): 첫 클러스터 만들고 앱 배포하기
- 바이브코딩을 위한 Azure AKS (4/7): Pod, Deployment, Service
- **바이브코딩을 위한 Azure AKS (5/7): 네트워킹과 Ingress (현재 글)**
- 바이브코딩을 위한 Azure AKS (6/7): 스케일링
- 바이브코딩을 위한 Azure AKS (7/7): 모니터링과 운영
<!-- toc:end -->

Tags: 바이브코딩, AzureAKS, Ingress, AI코딩
