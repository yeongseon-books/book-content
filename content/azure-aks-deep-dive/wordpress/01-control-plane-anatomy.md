---
title: "바이브코딩을 위한 Azure AKS 심화 (1/6): Control Plane 해부"
series: azure-aks-deep-dive
episode: 1
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- AzureAKS심화
- ControlPlane
- Kubernetes내부
- AI코딩
seo_description: "바이브코딩을 위한 Azure AKS 심화 1편: Control Plane 해부. AKS가 가린 Control Plane 내부 구조와 data plane 경계를 이해합니다."
---

# 바이브코딩을 위한 Azure AKS 심화 (1/6): Control Plane 해부

이 글은 바이브코딩을 위한 Azure AKS 심화 시리즈의 첫 번째 글입니다.

AKS를 관리형 Kubernetes라고 부르는 설명은 출발점으로는 충분합니다. 하지만 실제 운영 판단을 해야 하는 순간에는 그 문장이 너무 거칩니다. 지연이 control plane에서 시작된 것인지, node 쪽 실행 경로에서 시작된 것인지, 아니면 둘 사이의 상태 수렴 지점에서 생긴 것인지 분리해서 봐야 하기 때문입니다. AKS에서 control plane이 보이지 않는다는 사실이 특히 어렵습니다. self-managed Kubernetes라면 etcd, kube-apiserver, scheduler 프로세스를 직접 다루면서 감을 쌓을 수 있지만, AKS에서는 API endpoint, 객체 상태, 진단 로그, 그리고 AKS가 노출한 설정 표면만 가지고 내부를 추론해야 합니다. 이 심화 시리즈는 바로 그 추론 능력을 키우는 데 있습니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI에게 AKS 장애 진단 코드를 요청할 때 control plane과 data plane의 경계를 명시하지 않으면, 모든 문제를 앱 코드나 node 수준 문제로만 보는 코드가 생성되기 때문입니다.

> AKS Control Plane 해부의 핵심은 etcd, API server, scheduler, controller-manager가 어느 경계에서 무엇을 책임지는지, 그리고 AKS에서 사용자가 볼 수 있는 표면과 없는 표면을 구분하는 데 있습니다.

---

## 이 글에서 다룰 문제

- AKS control plane은 어떤 컴포넌트로 이루어지고, 사용자는 그중 무엇을 직접 볼 수 있을까요?
- 관리형 control plane이라는 약속은 어디까지를 의미하고 어디부터는 사용자 운영 책임일까요?
- control plane 장애와 data plane 장애는 어떻게 구분할까요?
- API server SLA를 읽을 때 왜 API 표면을 먼저 봐야 할까요?
- 이 개념을 실무에 적용하는 방법은 무엇일까요?

Control Plane 해부를 이해하면 AI에게 "AKS kubectl 응답 지연 시 API server 상태, etcd 상태를 진단 로그로 확인하고 data plane(kubelet, node) 문제와 분리하는 진단 명령"을 정확하게 요청할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "AKS kubectl 명령이 느린데 원인은?"
→ node 문제로 가정
→ kubectl get nodes만 확인
→ control plane vs data plane 구분 없음
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "AKS kubectl 응답 지연을 계층별로 진단해줘.
    1) control plane 계층: API server 응답 시간
       az aks show --query 'fqdn'로 API endpoint 확인
       curl -v https://API_FQDN/healthz
    2) data plane 계층: kubectl get nodes, kubectl describe node
    3) 진단 로그: az aks get-credentials,
       AKS 진단 로그에서 kube-apiserver-audit 확인
    control plane과 data plane 중 어느 계층인지 먼저 분류"
→ control plane / data plane 계층별 진단
→ 원인 계층 빠르게 특정
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| kubectl 지연을 항상 node 문제로 가정 | API server 응답 지연일 수 있음 | API server healthz 확인으로 계층 분류 |
| AKS control plane을 직접 접근 시도 | AKS는 control plane VM에 SSH 불가 | API 표면과 진단 로그로만 추론 |
| etcd 문제를 사용자가 직접 해결 시도 | etcd는 Azure 관리 영역 | Azure 지원 케이스로 에스컬레이션 |
| controller-manager 로그 직접 확인 시도 | control plane 컴포넌트 로그 직접 접근 불가 | AKS 진단 설정에서 kube-controller-manager-log 활성화 |
| data plane 문제와 control plane 문제 혼재 진단 | 원인 계층을 잘못 찾아 시간 낭비 | API server 응답 → node 상태 → pod 상태 순서 진단 |

## AI 협업 팁

Control Plane 진단 관련 효과적인 AI 프롬프트 패턴:

1. **계층별 진단 요청**: "AKS kubectl 응답 지연을 control plane(API server)과 data plane(node, kubelet)으로 분리해서 진단하는 명령 작성해줘"
2. **진단 로그 활성화 요청**: "AKS 진단 로그에서 kube-apiserver-audit을 Log Analytics로 전송하는 az CLI 명령 작성해줘"
3. **API server 상태 확인 요청**: "AKS API server 응답 시간을 확인하고 SLA 범위인지 판단하는 방법과 명령 작성해줘"

예시 프롬프트:
> "AKS 운영 장애 진단 플레이북을 작성해줘. control plane(API server healthz, 진단 로그) → data plane(node Ready 상태, kubelet 로그) → pod(describe, events) 순서로 계층별 진단 명령과 정상/비정상 판별 기준 포함."

## 운영 체크리스트

- [ ] control plane과 data plane 경계를 이해하고 있는가?
- [ ] AKS 진단 로그를 Log Analytics로 전송하는가?
- [ ] kubectl 지연 시 API server healthz를 먼저 확인하는가?
- [ ] control plane 이슈는 Azure 지원으로 에스컬레이션하는가?
- [ ] 다음 글에서 kubelet과 containerd 실행 경로를 이해할 준비가 됐는가?

## 처음 질문으로 돌아가기

Control Plane 해부를 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. 계층별 진단 순서를 명시한 사람과 그렇지 않은 사람이 AI에게 받는 AKS 장애 진단 코드의 완성도는 크게 다릅니다.

## 정리

Control Plane 해부 편은 바이브코딩을 위한 Azure AKS 심화 시리즈의 출발점입니다. AKS가 가린 control plane 내부 구조와 사용자가 볼 수 있는 표면, data plane과의 경계를 이해했습니다. 다음 글에서는 kubelet과 containerd가 노드에서 컨테이너를 실행하는 경로를 다룹니다.

## 참고 자료

- [AKS cluster architecture](https://docs.microsoft.com/azure/aks/concepts-clusters-workloads)
- [AKS diagnostics logs](https://docs.microsoft.com/azure/aks/monitor-aks)
- [Kubernetes control plane components](https://kubernetes.io/docs/concepts/overview/components/)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-aks-deep-dive/ko/01-control-plane-anatomy)

---

<!-- toc:begin -->
## 시리즈 목차

- **바이브코딩을 위한 Azure AKS 심화 (1/6): Control Plane 해부 (현재 글)**
- 바이브코딩을 위한 Azure AKS 심화 (2/6): kubelet과 containerd
- 바이브코딩을 위한 Azure AKS 심화 (3/6): CNI와 Azure CNI Overlay
- 바이브코딩을 위한 Azure AKS 심화 (4/6): Scheduler와 Pod 배치
- 바이브코딩을 위한 Azure AKS 심화 (5/6): HPA와 Cluster Autoscaler 내부
- 바이브코딩을 위한 Azure AKS 심화 (6/6): KEDA 내부
<!-- toc:end -->

Tags: 바이브코딩, AzureAKS심화, ControlPlane, AI코딩
