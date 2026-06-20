---
title: "바이브코딩을 위한 Azure AKS (6/7): 스케일링"
series: azure-aks-101
episode: 6
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- AzureAKS
- HPA
- KEDA
- AI코딩
seo_description: "바이브코딩을 위한 Azure AKS 6편: 스케일링. HPA는 Pod 수를, Cluster Autoscaler는 Node 수를, KEDA는 외부 이벤트를 HPA 경로로 연결한다는 구조를 이해합니다."
---

# 바이브코딩을 위한 Azure AKS (6/7): 스케일링

이 글은 바이브코딩을 위한 Azure AKS 시리즈의 6번째 글입니다.

AKS에서 스케일링이 헷갈리는 이유는 "늘린다"는 말이 여러 층을 동시에 가리키기 때문입니다. 어떤 경우에는 Pod 수를 늘리는 일이 핵심이고, 어떤 경우에는 새 Pod를 담을 노드를 늘리는 일이 핵심입니다. HPA, Cluster Autoscaler, KEDA는 같은 문제를 반복해서 푸는 도구가 아닙니다. HPA는 Pod 수를 조절합니다(CPU, 메모리 또는 custom metric 기반). Cluster Autoscaler는 Node 수를 조절합니다(Pod가 스케줄되지 못할 때). KEDA는 외부 이벤트 신호를 HPA가 이해하는 형태로 번역합니다(Service Bus 큐 길이, Event Hub offset 등). Pod는 늘어났는데 응답이 바로 좋아지지 않는 이유는 새 노드 프로비저닝 시간(2~5분) 때문입니다. HPA와 Cluster Autoscaler는 함께 동작해야 효과가 있습니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI에게 스케일링 설정 코드를 요청할 때 세 도구의 역할을 명시하지 않으면, 큐 worker에 CPU 기반 HPA를 설정해 메시지가 쌓여도 scale이 안 되는 코드가 생성되기 때문입니다.

> AKS 스케일링의 핵심은 HPA(Pod 수), Cluster Autoscaler(Node 수), KEDA(외부 이벤트 → HPA)가 서로 다른 신호를 보고 다른 대상을 조절한다는 사실을 이해하는 데 있습니다.

---

## 이 글에서 다룰 문제

- HPA, Cluster Autoscaler, KEDA는 각각 어떤 신호를 보고 무엇을 바꿀까요?
- CPU나 메모리 기반 HPA만으로 부족한 상황은 언제일까요?
- Pod는 늘어났는데 응답이 바로 좋아지지 않는 이유는 어디에 있을까요?
- HPA와 Cluster Autoscaler를 함께 써야 하는 이유는 무엇일까요?
- 이 개념을 실무에 적용하는 방법은 무엇일까요?

AKS 스케일링을 이해하면 AI에게 "HTTP API에 CPU 70% 기준 HPA(min 2, max 10), Service Bus worker에 KEDA azure-servicebus scaler(queueLength 5, min 0, max 5), node pool에 Cluster Autoscaler(min 2, max 20) 설정 YAML"을 정확하게 요청할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "AKS 자동 스케일링 설정해줘"
→ HPA CPU 기준으로 모든 앱에 동일 설정
→ 큐 worker도 CPU HPA로 설정
→ 노드 수 증가 설정 없음
→ 새 노드 프로비저닝 시간 미고려
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "AKS 스케일링을 세 도구로 분리해서 설정해줘.
    HPA: HTTP API Deployment에 CPU 70% 기준, min 2 max 10
    KEDA: Service Bus worker에 queueLength 5 기준, min 0 max 5
    Cluster Autoscaler: node pool min 2 max 20
    새 노드 프로비저닝 2~5분을 고려한 burst 대응 전략도 포함"
→ Pod 수(HPA/KEDA)와 Node 수(CA)를 별개로 관리
→ 큐 worker에 외부 이벤트 신호 적용
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| 큐 worker를 CPU 기반 HPA로 scale | 큐 길이 증가해도 CPU 높지 않으면 scale 안 됨 | KEDA azure-servicebus scaler 사용 |
| HPA만 설정하고 CA 미설정 | 새 Pod를 담을 노드가 없어 Pending 상태 | Cluster Autoscaler로 노드 자동 증가 설정 |
| 노드 증가 시간(2~5분)을 즉각 반응으로 기대 | 트래픽 급증 시 수 분간 응답 불가 | 최소 노드 수 유지로 warm node 확보 |
| HPA와 CA의 동작 순서 미이해 | scale 이벤트 순서가 예상과 달라 디버깅 혼란 | HPA → Pod Pending → CA → 노드 추가 순서 이해 |
| KEDA ScaledObject minReplicaCount 0 + 외부 API | cold start + API 지연으로 첫 요청 실패 가능 | 외부 API 호출하는 worker는 min 1 권장 |

## AI 협업 팁

AKS 스케일링 관련 효과적인 AI 프롬프트 패턴:

1. **HPA 설정 요청**: "AKS Deployment에 CPU 70% 기준 HPA min 2 max 10으로 설정하는 YAML 작성해줘"
2. **KEDA ScaledObject 요청**: "Service Bus 큐 길이 5 기준으로 worker를 scale하는 KEDA ScaledObject YAML 작성해줘"
3. **Cluster Autoscaler 설정 요청**: "AKS node pool에 Cluster Autoscaler min 2 max 20으로 활성화하는 az CLI 명령 작성해줘"

예시 프롬프트:
> "AKS 스케일링 전략을 작성해줘. orders-api HPA: CPU 70% min 2 max 10. order-worker KEDA ScaledObject: azure-servicebus queueLength 5 min 0 max 5. node pool Cluster Autoscaler: min 2 max 20. HPA→Pending Pod→CA→노드 추가 순서 흐름도 설명 포함."

## 운영 체크리스트

- [ ] 큐 worker에 KEDA ScaledObject를 사용하는가 (CPU HPA가 아닌가)?
- [ ] Cluster Autoscaler로 노드 자동 증가를 설정했는가?
- [ ] HPA와 Cluster Autoscaler가 함께 동작하는 순서를 이해했는가?
- [ ] 노드 프로비저닝 시간을 고려해 최소 노드 수를 설정했는가?
- [ ] 다음 글에서 모니터링과 운영을 이해할 준비가 됐는가?

## 처음 질문으로 돌아가기

AKS 스케일링을 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. HPA, Cluster Autoscaler, KEDA의 역할을 분리해 명시한 사람과 그렇지 않은 사람이 AI에게 받는 스케일링 설정 코드의 완성도는 크게 다릅니다.

## 정리

스케일링 편은 바이브코딩을 위한 Azure AKS에서 Pod 수와 Node 수를 별개 제어 루프로 이해하는 핵심 단계입니다. HPA(Pod), Cluster Autoscaler(Node), KEDA(외부 이벤트 → HPA)의 역할 분리와 함께 동작하는 순서를 이해했습니다. 다음 글에서는 Container Insights, 로그, 알람으로 AKS 운영을 다룹니다.

## 참고 자료

- [HPA in AKS](https://docs.microsoft.com/azure/aks/concepts-scale)
- [Cluster Autoscaler in AKS](https://docs.microsoft.com/azure/aks/cluster-autoscaler)
- [KEDA add-on for AKS](https://docs.microsoft.com/azure/aks/keda-about)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-aks-101/ko/06-scaling-hpa-ca-keda)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Azure AKS (1/7): Azure Kubernetes Service란?
- 바이브코딩을 위한 Azure AKS (2/7): 클러스터 아키텍처
- 바이브코딩을 위한 Azure AKS (3/7): 첫 클러스터 만들고 앱 배포하기
- 바이브코딩을 위한 Azure AKS (4/7): Pod, Deployment, Service
- 바이브코딩을 위한 Azure AKS (5/7): 네트워킹과 Ingress
- **바이브코딩을 위한 Azure AKS (6/7): 스케일링 (현재 글)**
- 바이브코딩을 위한 Azure AKS (7/7): 모니터링과 운영
<!-- toc:end -->

Tags: 바이브코딩, AzureAKS, HPA, AI코딩
