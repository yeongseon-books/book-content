---
title: 모니터링과 운영 — Container Insights, 로그, 알람
series: azure-aks-101
episode: 7
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
seo_description: kube-state-metrics는 이름 그대로 Kubernetes 오브젝트의 상태를 메트릭으로 드러냅니다.
---

# 모니터링과 운영 — Container Insights, 로그, 알람

AKS는 배포가 끝났다고 운영이 끝나는 서비스가 아닙니다. 오히려 그때부터가 시작입니다. Pod가 왜 재시작하는지, 어떤 node pool이 먼저 포화되는지, HPA가 왜 예상대로 반응하지 않았는지, 장애 조짐을 사용자보다 먼저 볼 수 있는지는 결국 관측 체계가 얼마나 잘 잡혀 있는가에 달려 있습니다.

특히 AKS 운영은 단순히 로그 몇 줄을 보는 일이 아닙니다. Kubernetes 객체 상태, 노드 압력, 애플리케이션 에러율, 스케일링 신호, 외부 이벤트 backlog를 서로 다른 계층에서 함께 읽어야 합니다. 로그만으로는 추세가 보이지 않고, 메트릭만으로는 원인이 보이지 않습니다.

이 글은 Azure AKS 101 시리즈의 마지막 글입니다.

여기서는 앞선 여섯 화에서 본 클러스터, 워크로드, 네트워크, 스케일링 이야기를 운영 관점에서 하나로 묶겠습니다. **Container Insights, Log Analytics, kube-state-metrics, 알람 계층**을 중심으로 AKS day-2 운영의 기본 시야를 정리하겠습니다.

## 이 글에서 다룰 문제

- Container Insights는 AKS 운영에서 무엇을 가장 빠르게 보여 줄까요?
- 로그와 메트릭은 왜 같은 관측 데이터가 아니라 서로 다른 질문에 답할까요?
- Log Analytics에서 어떤 KQL 테이블과 쿼리부터 익히는 편이 좋을까요?
- kube-state-metrics는 CPU·메모리 메트릭과 무엇이 다를까요?
- 알람은 애플리케이션, Kubernetes 객체, 노드 계층에 어떻게 나누어 두는 편이 좋을까요?

## 왜 이 글이 중요한가

운영 문제의 상당수는 이미 발생한 뒤에 찾는 것이 아니라, 징후를 먼저 읽는 능력에서 갈립니다. Pod restart가 조금씩 늘어나는 패턴, 특정 Deployment의 available replicas가 desired보다 계속 낮은 상태, HPA가 max replica 근처에 오래 붙어 있는 현상은 모두 사용자가 불편을 체감하기 전에 먼저 보일 수 있는 신호입니다.

또한 AKS에서는 Kubernetes 객체 상태를 읽는 능력이 특히 중요합니다. VM 기반 운영에서는 프로세스 로그와 CPU 그래프가 중심일 수 있지만, Kubernetes에서는 Deployment, Pod, HPA, Node 상태 자체가 운영 판단의 핵심이 됩니다. kube-state-metrics가 중요한 이유도 바로 여기에 있습니다.

마지막으로 관측은 많이 모으는 것보다 잘 읽는 것이 중요합니다. 모든 로그를 무한히 쌓는 것이 목표가 아니라, 실제 장애를 빠르게 진단할 만큼은 모으되 비용을 통제하는 것이 목표입니다. 운영 관점의 observability는 수집량 경쟁이 아니라 **질문에 답하는 체계**입니다.

## 운영을 이해하는 가장 좋은 방법: 로그 경로와 메트릭 경로를 분리해서 보는 것입니다

AKS 운영을 처음 정리할 때 가장 실용적인 기준은 텔레메트리 경로를 둘로 나누는 것입니다. 하나는 로그 경로이고, 다른 하나는 메트릭 경로입니다. 로그는 사건의 문맥과 정확한 에러 텍스트를 주고, 메트릭은 추세와 압력과 드리프트를 보여 줍니다. 이 둘을 섞으면 둘 다 애매하게 보입니다.

이 구분이 좋은 이유는 실제 운영 질문도 둘 중 하나로 자연스럽게 떨어지기 때문입니다. “왜 재시작했는가”는 로그와 이벤트 쪽 질문이고, “어떤 배포가 계속 desired보다 available이 부족한가”는 메트릭과 상태 지표 쪽 질문입니다. 즉 장애 원인과 상태 추세는 다른 관찰 도구를 요구합니다.

따라서 이 글에서는 먼저 운영 시야 전체를 그림으로 보고, 그다음 Container Insights와 KQL, kube-state-metrics, 알람 설계를 차례로 정리하겠습니다.

> AKS 운영에서는 로그가 사건의 이유를, 메트릭이 사건의 패턴을 보여 줍니다. 둘은 대체 관계가 아니라 보완 관계입니다.

## 핵심 개념

### 운영 시야를 한 장으로 보면 두 축이 먼저 보입니다

전체 운영 구조를 먼저 그림으로 보는 편이 좋습니다.

![로그와 메트릭 기반 운영 관측 구조](../../../assets/azure-aks-101/07/07-01-the-operations-view-in-one-diagram.ko.png)

*로그와 메트릭 기반 운영 관측 구조*

이 그림에서 먼저 기억할 것은 두 축입니다.

- **로그 축**: Log Analytics, Container Insights, KQL
- **메트릭 축**: Prometheus 계열 메트릭, kube-state-metrics, Grafana, 메트릭 알람

AKS day-2 운영은 이 둘 중 하나만으로 잘 되지 않습니다. 로그는 원인을 좁히고, 메트릭은 추세를 읽게 해 줍니다. 함께 봐야 운영이 안정됩니다.

### Container Insights는 AKS 상태를 가장 빠르게 보여 주는 창입니다

Container Insights는 Azure Monitor의 AKS 관측 경험입니다.

- 노드, Pod, 컨테이너 상태 뷰
- 로그 수집
- 기본 시각화
- 성능과 인벤토리 데이터

입문 단계에서는 “클러스터가 지금 무엇을 하고 있는가”를 가장 빨리 보는 창구라고 생각하면 됩니다. Kubernetes API를 직접 조회해도 되지만, 실제 운영은 중앙 수집과 히스토리가 함께 있어야 추세를 읽을 수 있습니다.

### 로그와 메트릭은 다른 질문에 답합니다

#### 로그가 잘하는 것

- 정확한 에러 메시지 확인
- 시작/종료 문맥 파악
- 이벤트 타임라인 재구성

#### 메트릭이 잘하는 것

- CPU, 메모리 추세
- replica 변화와 드리프트
- HPA 목표 대비 현재 상태
- 노드 포화나 압력 패턴

예를 들어 Pod가 자주 재시작된다는 사실 자체는 메트릭이나 인벤토리에서 쉽게 보일 수 있습니다. 하지만 왜 재시작됐는지는 보통 로그와 이벤트를 봐야 드러납니다. 즉 “무슨 일이 일어났는가”와 “왜 일어났는가”는 서로 다른 도구에서 더 잘 보입니다.

### Log Analytics 경로는 KQL을 중심으로 읽습니다

Container Insights가 수집한 AKS 로그는 Log Analytics Workspace에 들어가고, 여기서 KQL이 핵심 도구가 됩니다.

입문 단계에서 먼저 익혀 둘 테이블은 네 개면 충분합니다.

- `ContainerLogV2`
- `KubeEvents`
- `KubePodInventory`
- `KubeNodeInventory`

이 네 테이블만으로도 상당수 1차 장애 대응이 가능합니다. 이벤트, Pod 상태, 노드 인벤토리, 컨테이너 로그를 서로 엮어 보는 기본 감각이 생기기 때문입니다.

### 바로 써먹는 KQL 예시

#### 최근 Kubernetes 이벤트 보기

```kusto
KubeEvents
| where not(isempty(Namespace))
| sort by TimeGenerated desc
| take 50
```

이 쿼리는 배포 직후 이상 동작이나 예상치 못한 실패가 있을 때 가장 먼저 던지기 좋습니다. rollout 실패, scheduling 이슈, image pull 문제의 단서를 빠르게 찾는 데 유용합니다.

#### 특정 Pod 로그 보기

```kusto
ContainerLogV2
| where PodNamespace == "default"
| where PodName startswith "fastapi-hello"
| project TimeGenerated, PodName, ContainerName, LogMessage
| order by TimeGenerated desc
```

이 쿼리는 특정 워크로드의 직전 로그를 훑는 기본 패턴입니다. restart 직전 문맥이나 애플리케이션 예외를 좁힐 때 특히 자주 쓰게 됩니다.

#### 실패한 Pod 찾기

```kusto
KubePodInventory
| where PodStatus == "Failed"
| project TimeGenerated, Namespace, Name, PodStatus, ContainerStatusReason
| order by TimeGenerated desc
```

이 세 쿼리만으로도 “무슨 일이 있었는가”를 빠르게 좁혀 갈 수 있습니다. 처음부터 복잡한 KQL보다 자주 쓰는 기본 패턴을 익히는 편이 더 실용적입니다.

### kube-state-metrics는 Kubernetes 오브젝트 상태를 메트릭으로 보여 줍니다

kube-state-metrics는 이름 그대로 Kubernetes 객체 상태를 메트릭으로 드러냅니다.

- Deployment desired replicas와 available replicas
- HPA current replicas와 desired replicas
- Pod phase
- Node condition

CPU와 메모리 같은 런타임 압력 메트릭은 시스템이 얼마나 바쁜지를 잘 보여 줍니다. 하지만 “Deployment가 원하는 수보다 준비된 replica가 계속 부족한가”, “HPA가 max 근처에 고착됐는가” 같은 질문은 객체 상태 메트릭이 더 잘 답합니다. 이 차이가 매우 중요합니다.

Azure Monitor managed Prometheus에서는 kube-state-metrics가 기본 scrape 대상 중 하나입니다. 즉 AKS 운영에서 객체 상태 메트릭은 선택 장식이 아니라 핵심 관측 축에 가깝습니다.

### 운영자가 자주 던지는 질문은 대개 객체 상태 질문입니다

실무 운영 질문을 메트릭 문장으로 바꾸면 아래와 같습니다.

- 중요한 Deployment가 desired보다 available이 계속 낮은가
- HPA가 max replica 근처에서 오래 머무는가
- Pending Pod가 누적되는가
- Node Pool이 압력 방향으로 가고 있는가

이 질문들은 단순 CPU 그래프보다 훨씬 운영적입니다. Kubernetes는 결국 객체 상태를 통해 의도를 표현하는 시스템이기 때문입니다. 따라서 observability도 객체 상태를 읽는 방향으로 설계하는 편이 맞습니다.

### 알람은 계층별로 나누어 두는 편이 좋습니다

![운영 알람을 나누는 계층 구조](../../../assets/azure-aks-101/07/07-02-where-alerts-should-live.ko.png)

*운영 알람을 나누는 계층 구조*

좋은 알람은 한 종류로 끝나지 않습니다. CPU 80% 알람 하나만으로는 운영 전략이 되기 어렵습니다.

#### 애플리케이션 계층

- 응답 시간 증가
- 에러율 증가
- 큐 적체

#### Kubernetes 객체 계층

- available replicas 부족
- Pod restart 급증
- HPA max replica 고착

#### 노드 계층

- node pool 포화
- disk pressure
- NotReady 노드 발생

이렇게 계층을 나누면 사용자 영향과 플랫폼 내부 상태를 함께 읽을 수 있습니다. 운영에서 강한 체계는 언제나 다층 알람 구조를 가집니다.

### Azure Monitor 알람 종류도 각자 자연스러운 자리가 있습니다

Azure Monitor는 AKS에 대해 여러 알람 경로를 제공합니다.

- **Metric alerts**
- **Log search alerts**
- **Prometheus alerts**

보통은 아래처럼 자연스럽게 나뉩니다.

- 빠른 임계값 감지는 metric alerts
- KQL 조건식 기반 탐지는 log alerts
- Prometheus 스타일 메트릭 규칙은 Prometheus alerts

그다음 action group을 통해 이메일, 웹훅, 자동화, incident 시스템과 연결합니다. 알람은 규칙 자체보다도 **누가 어떤 맥락으로 받는가**까지 설계되어야 실제 운영 도구가 됩니다.

### 101 수준에서 먼저 걸 만한 알람이 있습니다

처음부터 수십 개 알람을 만들 필요는 없습니다. 아래 정도가 좋은 시작점입니다.

1. 중요한 Deployment의 available replicas 부족
2. 비정상적인 Pod restart 증가
3. 특정 node pool 사용률 또는 압력 증가
4. HPA가 max replica 근처에 오래 머무름
5. 애플리케이션 5xx 또는 실패율 증가

특히 중요 서비스의 replica availability 알람은 비용 대비 가치가 큽니다. 사용자 영향과 가장 직접적으로 연결되기 때문입니다.

### Container Insights와 `kubectl`은 대체재가 아니라 보완재입니다

운영 중에는 둘 다 사용합니다.

#### Container Insights / Azure Monitor가 잘하는 것

- 장기 추세
- 중앙 수집
- 이력 조회
- 대시보드와 알람 연결

#### `kubectl`이 잘하는 것

- 즉시 객체 상태 확인
- `describe` 출력 확인
- rollout, event, scheduling 결과 확인

실무에서는 Container Insights에서 restart 패턴을 보고, 실제 원인은 `kubectl describe pod`와 KQL 로그 조회로 좁히는 흐름이 매우 흔합니다. 중앙 관측과 즉시 디버깅은 같이 가야 합니다.

### day-2 운영에서는 비용도 함께 봐야 합니다

운영 체크는 안정성만이 아닙니다. 관측 비용도 운영 일부입니다.

- system pool과 user pool이 의도대로 동작하는가
- LoadBalancer와 Ingress 경로가 건강한가
- Pending Pod가 반복되는가
- 로그 수집량이 가치보다 너무 커지지는 않는가
- namespace 필터와 collection preset이 실제 운영 목표에 맞는가

모니터링은 많이 모을수록 좋다가 아닙니다. **문제를 빨리 찾을 수 있을 만큼은 모으되 비용 통제를 잃지 않는 것**이 더 중요합니다.

## 흔히 헷갈리는 지점

- 로그를 많이 모으면 운영이 잘된다고 생각하기 쉽지만, 메트릭과 객체 상태가 빠지면 추세를 놓치기 쉽습니다.
- CPU와 메모리 그래프만으로 충분하다고 생각하기 쉽지만, Kubernetes 운영은 객체 상태 메트릭이 핵심입니다.
- Container Insights와 `kubectl` 중 하나만 있으면 된다고 여기기 쉽지만, 실제로는 둘이 서로 다른 질문에 답합니다.
- 알람을 임계값 한두 개로 끝내기 쉽지만, 애플리케이션·객체·노드 계층을 나눠야 운영 맥락이 생깁니다.
- observability를 많이 수집하는 문제로만 보지만, 실제로는 비용과 질문 설계의 문제이기도 합니다.

## 운영 체크리스트

- [ ] 로그 경로와 메트릭 경로를 분리해 운영 질문에 매핑했는가
- [ ] `ContainerLogV2`, `KubeEvents`, `KubePodInventory`, `KubeNodeInventory` 조회 흐름을 팀이 공유하는가
- [ ] kube-state-metrics 기반으로 Deployment, HPA, Pod 상태를 보는 대시보드나 규칙을 갖췄는가
- [ ] 애플리케이션, Kubernetes 객체, 노드 계층으로 나누어 핵심 알람을 정의했는가
- [ ] 로그 보존 기간과 수집 범위를 비용 한도 안에서 운영하도록 조정했는가

## 정리

이 글의 핵심은 AKS 운영을 로그 한 종류나 그래프 한 장으로 해결하려 하지 않는 것입니다. 로그는 정확한 원인과 문맥을 보여 주고, 메트릭은 추세와 압력과 드리프트를 보여 줍니다. AKS day-2 운영은 이 둘을 함께 읽는 체계 위에 서야 합니다.

또한 Kubernetes 운영에서는 객체 상태 메트릭이 특히 중요합니다. Deployment desired/available, HPA current/desired, Pending Pod, Node condition 같은 신호가 실제 사용자 영향과 플랫폼 상태를 가장 잘 연결해 주기 때문입니다. kube-state-metrics와 알람 계층 설계가 중요한 이유도 여기에 있습니다.

시리즈 전체를 마무리하며 가장 중요하게 남아야 할 감각은 이것입니다. **AKS는 배포 도구가 아니라 운영 플랫폼입니다.** 요청이 어디로 들어오고, 어떤 객체를 거치고, 어디서 스케일하며, 문제가 생기면 어떤 로그와 메트릭을 봐야 하는지까지 한 장의 그림으로 떠올릴 수 있다면, 이제 그다음 주제는 기능 암기가 아니라 깊이 확장 문제가 됩니다.

<!-- toc:begin -->
## 시리즈 목차

- [Azure Kubernetes Service란? — 직접 운영하지 않아도 되는 Kubernetes](./01-what-is-aks.md)
- [클러스터 아키텍처 — Control Plane과 Node Pool](./02-cluster-architecture.md)
- [첫 클러스터 만들고 앱 배포하기 — Python/FastAPI](./03-first-cluster-and-deploy.md)
- [Pod·Deployment·Service — 워크로드를 표현하는 세 가지 방식](./04-pod-deployment-service.md)
- [네트워킹과 Ingress — 클러스터 안과 밖을 잇는 길](./05-networking-and-ingress.md)
- [스케일링 — HPA, Cluster Autoscaler, KEDA](./06-scaling-hpa-ca-keda.md)
- **모니터링과 운영 — Container Insights, 로그, 알람 (현재 글)**

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [Kubernetes monitoring in Azure Monitor](https://learn.microsoft.com/en-us/azure/azure-monitor/containers/kubernetes-monitoring-overview)
- [Enable monitoring for AKS clusters](https://learn.microsoft.com/en-us/azure/azure-monitor/containers/kubernetes-monitoring-enable)
- [Query container logs in Azure Monitor](https://learn.microsoft.com/en-us/azure/azure-monitor/containers/container-insights-log-query)
- [Default Prometheus metrics configuration in Azure Monitor](https://learn.microsoft.com/en-us/azure/azure-monitor/containers/prometheus-metrics-scrape-default)
- [Overview of Azure Monitor alerts](https://learn.microsoft.com/en-us/azure/azure-monitor/alerts/alerts-overview)

### 관련 시리즈

- [Azure Functions 101](../../azure-functions-101/ko/07-monitoring-and-ops.md) — Application Insights 중심 운영과 비교할 때
- [Azure App Service 101](../../azure-app-service-101/ko/06-logging-monitoring.md) — 더 단순한 PaaS 운영 모델과 비교할 때

Tags: Azure, AKS, Kubernetes, Cloud
