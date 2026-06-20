---
title: "바이브코딩을 위한 Azure AKS (7/7): 모니터링과 운영"
series: azure-aks-101
episode: 7
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- AzureAKS
- ContainerInsights
- 관측성
- AI코딩
seo_description: "바이브코딩을 위한 Azure AKS 7편: 모니터링과 운영. Container Insights, Log Analytics, kube-state-metrics, 알람 계층으로 AKS day-2 운영 시야를 이해합니다."
---

# 바이브코딩을 위한 Azure AKS (7/7): 모니터링과 운영

이 글은 바이브코딩을 위한 Azure AKS 시리즈의 마지막 글입니다.

AKS는 배포가 끝났다고 운영이 끝나는 서비스가 아닙니다. Pod가 왜 재시작하는지, 어떤 node pool이 먼저 포화되는지, HPA가 왜 예상대로 반응하지 않았는지를 보려면 관측 체계가 잘 잡혀 있어야 합니다. Kubernetes 객체 상태, 노드 압력, 애플리케이션 에러율, 스케일링 신호를 서로 다른 계층에서 함께 읽어야 합니다. 로그만으로는 추세가 보이지 않고, 메트릭만으로는 원인이 보이지 않습니다. Container Insights는 클러스터/노드/컨테이너 수준 메트릭과 로그를 Log Analytics로 보냅니다. kube-state-metrics는 Kubernetes 객체(Pod, Deployment, Node) 상태를 메트릭으로 드러냅니다. 두 데이터를 KQL로 함께 조회해야 "HPA가 왜 scale하지 않았는지"를 정확하게 진단할 수 있습니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI에게 AKS 모니터링 코드를 요청할 때 계층(메트릭 vs 로그 vs Kubernetes 객체 상태)을 명시하지 않으면, 앱 로그만 확인하는 불완전한 관측 설정이 생성되기 때문입니다.

> AKS 모니터링의 핵심은 Container Insights(메트릭/로그), kube-state-metrics(K8s 객체 상태), 알람을 각각 다른 질문에 답하는 계층으로 이해하는 데 있습니다.

---

## 이 글에서 다룰 문제

- Container Insights는 AKS 운영에서 무엇을 가장 빠르게 보여 줄까요?
- 로그와 메트릭은 왜 서로 다른 질문에 답할까요?
- Log Analytics에서 어떤 KQL 테이블과 쿼리부터 익히는 편이 좋을까요?
- kube-state-metrics가 HPA 진단에 어떻게 도움을 줄까요?
- 이 개념을 실무에 적용하는 방법은 무엇일까요?

AKS 모니터링을 이해하면 AI에게 "Container Insights 활성화, KubePodInventory에서 Pod 재시작 급증 KQL 알람, Deployment 복제본 부족 알람, HPA maxReplicas 도달 알람 설정"을 정확하게 요청할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "AKS 앱 모니터링 설정해줘"
→ 앱 로그만 수집
→ Pod 재시작 원인 불명확
→ HPA 반응 미확인
→ 노드 포화 사전 감지 없음
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "AKS 관측성을 세 계층으로 설정해줘.
    1) Container Insights: az aks enable-addons로 활성화
       KubePodInventory로 Pod 재시작 빈도 KQL
    2) kube-state-metrics: HPA maxReplicas 도달 여부 확인 KQL
    3) 알람: Pod 재시작 5회 초과, Node CPU 80% 초과,
       Deployment 목표 복제본 불충족 알람 설정"
→ 메트릭/로그/K8s 객체 상태 계층별 관측
→ HPA 반응 불량 원인 정확히 진단 가능
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| Container Insights 비활성화 | 노드/컨테이너 메트릭과 로그 수집 불가 | az aks enable-addons --addons monitoring 실행 |
| 로그만 확인하고 메트릭 미확인 | 재시작 원인이 메트릭(OOMKilled, CPU throttle)에 있음 | KubePodInventory + Perf 테이블 함께 조회 |
| kube-state-metrics 없이 HPA 진단 | HPA maxReplicas 도달 여부 확인 불가 | kube-state-metrics로 HPA 상태 메트릭 확인 |
| 알람 미설정 | 장애를 사용자 신고 후 발견 | Pod 재시작, Node 압력, Deployment 불충족 알람 사전 설정 |
| Log Analytics workspace를 클러스터마다 분리 | 크로스 클러스터 KQL 조회 불가 | 팀/환경 단위로 workspace 통합 |

## AI 협업 팁

AKS 모니터링 관련 효과적인 AI 프롬프트 패턴:

1. **Container Insights 활성화 요청**: "AKS에 Container Insights를 활성화하고 기존 Log Analytics workspace에 연결하는 az CLI 명령 작성해줘"
2. **Pod 재시작 KQL 요청**: "Log Analytics KubePodInventory에서 지난 1시간 Pod 재시작 횟수를 네임스페이스별로 집계하는 KQL 쿼리 작성해줘"
3. **알람 설정 요청**: "AKS Pod 재시작 5회 초과, Node CPU 80% 초과를 Azure Monitor 알람으로 설정하는 az CLI 명령 작성해줘"

예시 프롬프트:
> "AKS 운영 관측성을 설정해줘. Container Insights 활성화 → KubePodInventory Pod 재시작 KQL → Deployment 복제본 불충족 KQL → HPA maxReplicas 도달 kube-state-metrics 쿼리 → 세 가지 알람(재시작, CPU, 복제본 불충족) 설정 명령."

## 운영 체크리스트

- [ ] Container Insights가 활성화되고 Log Analytics에 연결됐는가?
- [ ] Pod 재시작 빈도 KQL 쿼리를 준비했는가?
- [ ] HPA maxReplicas 도달 알람을 설정했는가?
- [ ] Node 압력(CPU, 메모리) 알람을 설정했는가?
- [ ] 로그(원인)와 메트릭(추세)을 함께 조회하는 운영 습관이 있는가?

## 처음 질문으로 돌아가기

AKS 모니터링을 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. 관측 계층을 명시한 사람과 그렇지 않은 사람이 AI에게 받는 모니터링 설정 코드의 완성도는 크게 다릅니다.

## 정리

모니터링과 운영 편은 바이브코딩을 위한 Azure AKS 시리즈의 마지막 단계입니다. Container Insights, kube-state-metrics, Log Analytics KQL, 알람 계층을 통해 AKS day-2 운영 시야를 이해했습니다. 이 시리즈에서 배운 클러스터 구조, 워크로드, 네트워킹, 스케일링, 관측성 개념을 명시해서 AI에게 요청하면 훨씬 완성도 높은 코드를 얻을 수 있습니다.

## 참고 자료

- [Container Insights for AKS](https://docs.microsoft.com/azure/azure-monitor/containers/container-insights-overview)
- [kube-state-metrics](https://github.com/kubernetes/kube-state-metrics)
- [Azure Monitor alerts for AKS](https://docs.microsoft.com/azure/aks/monitor-aks)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-aks-101/ko/07-monitoring-and-ops)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Azure AKS (1/7): Azure Kubernetes Service란?
- 바이브코딩을 위한 Azure AKS (2/7): 클러스터 아키텍처
- 바이브코딩을 위한 Azure AKS (3/7): 첫 클러스터 만들고 앱 배포하기
- 바이브코딩을 위한 Azure AKS (4/7): Pod, Deployment, Service
- 바이브코딩을 위한 Azure AKS (5/7): 네트워킹과 Ingress
- 바이브코딩을 위한 Azure AKS (6/7): 스케일링
- **바이브코딩을 위한 Azure AKS (7/7): 모니터링과 운영 (현재 글)**
<!-- toc:end -->

Tags: 바이브코딩, AzureAKS, ContainerInsights, AI코딩
