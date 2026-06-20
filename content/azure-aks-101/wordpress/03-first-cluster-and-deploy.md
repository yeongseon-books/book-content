---
title: "바이브코딩을 위한 Azure AKS (3/7): 첫 클러스터 만들고 앱 배포하기"
series: azure-aks-101
episode: 3
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- AzureAKS
- kubectl
- FastAPI
- AI코딩
seo_description: "바이브코딩을 위한 Azure AKS 3편: 첫 클러스터 만들고 앱 배포하기. az와 kubectl의 경계, ACR 이미지 빌드, Deployment와 Service 배포 흐름을 이해합니다."
---

# 바이브코딩을 위한 Azure AKS (3/7): 첫 클러스터 만들고 앱 배포하기

이 글은 바이브코딩을 위한 Azure AKS 시리즈의 3번째 글입니다.

Kubernetes는 개념만 오래 붙들고 있으면 필요 이상으로 추상적으로 느껴집니다. 실제로는 작은 앱 하나를 올려 보면 훨씬 빨리 감이 옵니다. AKS 입문에서 가장 중요한 경험은 az와 kubectl의 경계가 몸으로 들어오는 것입니다. az는 Azure 리소스(클러스터, node pool, ACR)를 만들고, kubectl은 Kubernetes API에 원하는 상태(Deployment, Service)를 선언합니다. `az aks get-credentials`는 이 두 세계를 연결하는 다리입니다. FastAPI 앱 배포 흐름은 간단합니다. 이미지 빌드(ACR) → Deployment 선언(kubectl) → Service 노출(kubectl) → 상태 확인(kubectl get, describe) → 로그 확인(kubectl logs). 이 흐름을 한 번 직접 밟아 보면 뒤의 네트워킹과 스케일링도 갑자기 현실적인 문제로 바뀝니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI에게 AKS 배포 코드를 요청할 때 az와 kubectl의 역할 분리를 명시하지 않으면, Azure 리소스 생성과 Kubernetes 객체 선언이 뒤섞인 코드가 생성되기 때문입니다.

> 첫 배포의 핵심은 az(Azure 리소스)와 kubectl(Kubernetes 상태 선언)의 역할을 분리해서 이해하는 데 있습니다.

---

## 이 글에서 다룰 문제

- AKS 클러스터를 만들 때 최소한 무엇을 결정해야 할까요?
- az aks get-credentials 이후 kubectl이 실제로 어떤 계층과 대화할까요?
- FastAPI 앱을 ACR에 빌드하고 AKS에 Deployment로 배포하는 전체 흐름은 어떻게 될까요?
- 배포 성공과 앱 정상 응답을 어떻게 분리해서 확인할까요?
- 이 개념을 실무에 적용하는 방법은 무엇일까요?

첫 배포 흐름을 이해하면 AI에게 "ACR에 FastAPI 이미지 빌드 → AKS Deployment 3 replicas 배포 → ClusterIP Service 생성 → kubectl rollout status로 배포 완료 확인 → Port 8000 응답 확인하는 순서별 명령"을 정확하게 요청할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "FastAPI를 AKS에 배포하는 코드 작성해줘"
→ az와 kubectl 명령 순서 없음
→ ACR 이미지 빌드 단계 누락
→ 배포 완료 확인 없음
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "FastAPI AKS 배포를 단계별로 작성해줘.
    1) az acr build로 이미지 빌드 및 ACR 푸시
    2) az aks get-credentials로 kubectl 연결
    3) kubectl apply -f deployment.yaml (replicas 3, image 명시)
    4) kubectl apply -f service.yaml (ClusterIP, port 8000)
    5) kubectl rollout status로 배포 완료 확인
    6) kubectl port-forward 또는 LoadBalancer로 응답 확인"
→ az(Azure 리소스)와 kubectl(K8s 선언) 역할 분리
→ 배포 완료와 앱 응답을 별도 단계로 검증
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| az aks get-credentials 생략 | kubectl이 클러스터를 모름 | az aks get-credentials --name --resource-group 실행 |
| image pull 오류 | ACR-AKS Managed Identity 연결 미설정 | az aks update --attach-acr로 연결 |
| kubectl apply 성공을 앱 응답으로 오해 | Pod 시작 실패해도 apply는 성공 | kubectl rollout status, kubectl get pods 별도 확인 |
| 모든 Service에 LoadBalancer 사용 | 클러스터 내부 서비스에 불필요한 외부 IP 생성 | 내부 서비스는 ClusterIP, 외부 노출만 LoadBalancer |
| Deployment 없이 Pod 직접 배포 | Pod 장애 시 자동 복구 안 됨 | Deployment를 통해 Pod 생성 |

## AI 협업 팁

첫 배포 관련 효과적인 AI 프롬프트 패턴:

1. **전체 배포 파이프라인 요청**: "FastAPI를 ACR 빌드 → AKS Deployment로 배포하는 bash 스크립트 작성해줘 (rollout status 확인 포함)"
2. **ACR-AKS 연결 요청**: "AKS가 ACR에서 이미지를 pull하도록 Managed Identity를 연결하는 az CLI 명령 작성해줘"
3. **배포 상태 확인 요청**: "AKS Deployment 배포 후 Pod 상태, 로그, 이벤트를 확인하는 kubectl 명령 작성해줘"

예시 프롬프트:
> "FastAPI AKS 배포 스크립트를 작성해줘. az acr build → kubectl apply Deployment(replicas 3) → kubectl apply Service(ClusterIP 8000) → kubectl rollout status → kubectl get pods로 상태 확인. ACR-AKS Managed Identity 연결 명령 포함."

## 운영 체크리스트

- [ ] az aks get-credentials로 kubectl을 클러스터에 연결했는가?
- [ ] ACR과 AKS의 Managed Identity 연결을 설정했는가?
- [ ] Deployment를 통해 Pod를 배포했는가 (직접 Pod 배포가 아닌가)?
- [ ] kubectl rollout status로 배포 완료를 확인했는가?
- [ ] 다음 글에서 Pod, Deployment, Service의 역할을 이해할 준비가 됐는가?

## 처음 질문으로 돌아가기

첫 배포 흐름을 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. az와 kubectl의 역할을 분리해 명시한 사람과 그렇지 않은 사람이 AI에게 받는 배포 스크립트의 완성도는 크게 다릅니다.

## 정리

첫 클러스터 만들고 앱 배포하기 편은 바이브코딩을 위한 Azure AKS에서 az와 kubectl의 역할 분리를 이해하는 핵심 단계입니다. ACR 이미지 빌드, Deployment, Service, 배포 검증 흐름을 이해했습니다. 다음 글에서는 Pod, Deployment, Service 각각의 역할을 더 깊이 다룹니다.

## 참고 자료

- [Deploy applications to AKS](https://docs.microsoft.com/azure/aks/tutorial-kubernetes-deploy-application)
- [ACR integration with AKS](https://docs.microsoft.com/azure/aks/cluster-container-registry-integration)
- [kubectl cheat sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-aks-101/ko/03-first-cluster-and-deploy)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Azure AKS (1/7): Azure Kubernetes Service란?
- 바이브코딩을 위한 Azure AKS (2/7): 클러스터 아키텍처
- **바이브코딩을 위한 Azure AKS (3/7): 첫 클러스터 만들고 앱 배포하기 (현재 글)**
- 바이브코딩을 위한 Azure AKS (4/7): Pod, Deployment, Service
- 바이브코딩을 위한 Azure AKS (5/7): 네트워킹과 Ingress
- 바이브코딩을 위한 Azure AKS (6/7): 스케일링
- 바이브코딩을 위한 Azure AKS (7/7): 모니터링과 운영
<!-- toc:end -->

Tags: 바이브코딩, AzureAKS, kubectl, AI코딩
