---
title: "바이브코딩을 위한 Azure AKS (4/7): Pod, Deployment, Service"
series: azure-aks-101
episode: 4
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- AzureAKS
- Pod
- Deployment
- AI코딩
seo_description: "바이브코딩을 위한 Azure AKS 4편: Pod, Deployment, Service. 스케줄링 단위, 원하는 상태 관리자, 안정적인 네트워크 정체성이라는 세 층으로 워크로드를 이해합니다."
---

# 바이브코딩을 위한 Azure AKS (4/7): Pod, Deployment, Service

이 글은 바이브코딩을 위한 Azure AKS 시리즈의 4번째 글입니다.

처음 Kubernetes 매니페스트를 보면 객체가 불필요하게 많아 보입니다. "컨테이너 하나 띄우면 되는데 왜 Pod가 있고 Deployment가 있고 Service까지 따로 있지?"라는 질문이 자연스럽습니다. 하지만 실제 운영에서는 이 셋을 분리해 둔 덕분에 배포와 복구와 네트워크 경계가 훨씬 명확해집니다. Pod는 스케줄링 단위입니다. Deployment는 원하는 상태(replicas 수, 이미지 버전)를 관리하는 제어 루프입니다. Service는 Pod IP가 변해도 안정적인 네트워크 정체성을 제공합니다. Pod IP를 직접 쓰지 않게 하는 이유는 Pod가 재시작하면 IP가 바뀌기 때문입니다. Service의 selector가 새 Pod를 자동으로 찾아줍니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI에게 워크로드 YAML을 요청할 때 Pod, Deployment, Service의 역할을 명시하지 않으면, Pod를 직접 배포해 장애 시 자동 복구가 안 되거나 Service 없이 Pod IP를 하드코딩하는 코드가 생성되기 때문입니다.

> Pod, Deployment, Service의 핵심은 스케줄링 단위(Pod), 원하는 상태 관리(Deployment), 안정적 네트워크 정체성(Service) 세 층이 분리된 이유를 이해하는 데 있습니다.

---

## 이 글에서 다룰 문제

- Pod와 컨테이너는 왜 같은 말이 아니며, 왜 Pod를 스케줄링 단위로 볼까요?
- Deployment는 Pod를 직접 여러 개 만드는 것과 무엇이 다를까요?
- Service는 왜 Pod IP를 직접 쓰지 않게 만들까요?
- ClusterIP, NodePort, LoadBalancer는 각각 언제 사용할까요?
- 이 개념을 실무에 적용하는 방법은 무엇일까요?

Pod, Deployment, Service를 이해하면 AI에게 "FastAPI Deployment(replicas 3, RollingUpdate, maxSurge 1)와 ClusterIP Service(port 80 → targetPort 8000) YAML, 그리고 배포 후 kubectl rollout history로 이력 확인하는 명령"을 정확하게 요청할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "Kubernetes에 FastAPI 컨테이너 올려줘"
→ Pod manifest만 생성
→ 장애 시 자동 복구 없음
→ Pod IP 직접 사용
→ 재시작 시 IP 변경으로 연결 끊김
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "FastAPI 워크로드를 세 객체로 분리해서 구현해줘.
    1) Deployment: replicas 3, RollingUpdate(maxSurge 1, maxUnavailable 0),
       readinessProbe /health 설정
    2) ClusterIP Service: port 80 → targetPort 8000, selector app=fastapi
    3) LoadBalancer Service: 외부 노출용 (프로덕션에서 Ingress로 교체 예정)
    장애 시 Deployment controller가 Pod 자동 재생성하는 원리 설명 포함"
→ 자동 복구가 되는 Deployment
→ Pod IP 변경에도 안정적인 Service
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| Pod를 직접 배포 | 장애 시 자동 복구 안 됨 | Deployment를 통해 Pod 생성 |
| Pod IP를 Service URL로 직접 사용 | Pod 재시작 시 IP 변경으로 연결 끊김 | Service name으로 접근 (DNS 자동 해석) |
| 모든 Service를 LoadBalancer로 설정 | 클러스터 내부 서비스에 불필요한 외부 IP | 내부 통신은 ClusterIP, 외부 노출만 LoadBalancer/Ingress |
| readinessProbe 미설정 | 준비 안 된 Pod에 트래픽 전달 | readinessProbe로 준비된 Pod만 트래픽 수신 |
| RollingUpdate 파라미터 미설정 | 배포 중 모든 Pod 동시 재시작 가능 | maxSurge, maxUnavailable로 롤링 속도 제어 |

## AI 협업 팁

Pod, Deployment, Service 관련 효과적인 AI 프롬프트 패턴:

1. **Deployment YAML 요청**: "FastAPI Deployment를 replicas 3, RollingUpdate, readinessProbe /health로 구성하는 YAML 작성해줘"
2. **Service YAML 요청**: "ClusterIP Service로 port 80을 FastAPI의 targetPort 8000에 매핑하는 YAML과 LoadBalancer로 외부 노출하는 YAML 작성해줘"
3. **배포 이력 관리 요청**: "kubectl rollout history와 kubectl rollout undo로 Deployment 배포 이력 확인 및 롤백하는 명령 작성해줘"

예시 프롬프트:
> "FastAPI AKS 워크로드 YAML을 작성해줘. Deployment: replicas 3, RollingUpdate(maxSurge 1, maxUnavailable 0), readinessProbe GET /health. ClusterIP Service: port 80 targetPort 8000. 배포 후 rollout status 확인 명령 포함."

## 운영 체크리스트

- [ ] Deployment를 통해 Pod를 배포했는가 (직접 Pod 배포가 아닌가)?
- [ ] Service selector가 Pod label과 일치하는가?
- [ ] readinessProbe를 설정해 준비된 Pod만 트래픽을 받는가?
- [ ] RollingUpdate 파라미터(maxSurge, maxUnavailable)를 명시했는가?
- [ ] 다음 글에서 네트워킹과 Ingress를 이해할 준비가 됐는가?

## 처음 질문으로 돌아가기

Pod, Deployment, Service를 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. 세 객체의 역할을 분리해 명시한 사람과 그렇지 않은 사람이 AI에게 받는 워크로드 YAML의 완성도는 크게 다릅니다.

## 정리

Pod, Deployment, Service 편은 바이브코딩을 위한 Azure AKS에서 워크로드 모델의 세 층을 이해하는 핵심 단계입니다. 스케줄링 단위(Pod), 원하는 상태 관리(Deployment), 안정적 네트워크 정체성(Service)의 역할 분리를 이해했습니다. 다음 글에서는 클러스터 내외부를 잇는 네트워킹과 Ingress를 다룹니다.

## 참고 자료

- [Deployments in Kubernetes](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Services in Kubernetes](https://kubernetes.io/docs/concepts/services-networking/service/)
- [AKS workloads overview](https://docs.microsoft.com/azure/aks/concepts-clusters-workloads)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-aks-101/ko/04-pod-deployment-service)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Azure AKS (1/7): Azure Kubernetes Service란?
- 바이브코딩을 위한 Azure AKS (2/7): 클러스터 아키텍처
- 바이브코딩을 위한 Azure AKS (3/7): 첫 클러스터 만들고 앱 배포하기
- **바이브코딩을 위한 Azure AKS (4/7): Pod, Deployment, Service (현재 글)**
- 바이브코딩을 위한 Azure AKS (5/7): 네트워킹과 Ingress
- 바이브코딩을 위한 Azure AKS (6/7): 스케일링
- 바이브코딩을 위한 Azure AKS (7/7): 모니터링과 운영
<!-- toc:end -->

Tags: 바이브코딩, AzureAKS, Pod, AI코딩
