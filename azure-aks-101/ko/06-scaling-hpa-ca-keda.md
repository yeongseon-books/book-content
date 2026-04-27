# 스케일링 — HPA, Cluster Autoscaler, KEDA

> Azure Kubernetes Service 101 시리즈 (6/7)

AKS에서 스케일링이 헷갈리는 이유는 “늘린다”는 말이 두 가지를 동시에 가리키기 때문입니다. Pod를 늘리는 일과 Node를 늘리는 일은 다른 계층입니다. 여기에 외부 이벤트 기반 스케일링까지 들어오면 HPA, Cluster Autoscaler, KEDA가 한 덩어리처럼 보이기 쉽습니다.

이번 글에서는 이 셋을 분리해서 봅니다. 어떤 신호를 보고, 무엇을 늘리고, 서로 어떤 순서로 연결되는지 이해하면 운영 중 스케일링 문제를 훨씬 덜 감으로 다루게 됩니다.

---

## 먼저 한 장으로 정리

```mermaid
flowchart LR
    M[CPU / Memory / Custom Metrics] --> HPA[HPA]
    HPA --> PODS[Pod replicas]
    PODS --> PENDING[Unschedulable Pods?]
    PENDING --> CA[Cluster Autoscaler]
    CA --> NODES[Node count]
    E[Service Bus / Event Hub / Cron] --> KEDA[KEDA]
    KEDA --> HPA
```

이 그림의 문장을 풀면 이렇게 됩니다.

- HPA는 **Pod 수**를 조절합니다.
- Cluster Autoscaler는 **Node 수**를 조절합니다.
- KEDA는 외부 이벤트를 받아 **HPA를 만들어 활용하는 방식**으로 Pod 스케일링을 확장합니다.

가장 많이 나오는 오해를 먼저 지우면, **KEDA는 HPA를 대체하는 것이 아니라 그 위에 얹히는 구조**입니다.

---

## HPA — Pod 수를 자동으로 조절

HPA는 Horizontal Pod Autoscaler입니다.

- 대상은 보통 Deployment
- 입력은 CPU, 메모리, 혹은 custom/external metrics
- 결과는 replica 수 변경

즉 HPA는 “이 앱 인스턴스를 몇 개 돌릴까”를 정합니다.

### HPA가 잘 작동하려면

HPA는 메트릭을 보고 판단하므로, 기본적으로 metrics-server와 적절한 리소스 요청값이 중요합니다.

- CPU request가 너무 엉뚱하면 HPA 판단도 왜곡될 수 있습니다.
- readiness probe가 부정확하면 늘어난 Pod가 트래픽을 받아도 되는 시점이 흐려집니다.

HPA는 마법이 아니라 피드백 루프입니다. 입력 신호가 나쁘면 결과도 나빠집니다.

---

## HPA의 결정 루프

```mermaid
flowchart TB
    A[현재 메트릭 수집] --> B[목표값과 비교]
    B --> C[원하는 replica 계산]
    C --> D[Deployment replica 조정]
    D --> E[새 Pod 생성 또는 축소]
```

예를 들어 CPU 평균 사용률 목표를 60%로 두고, 현재 두 Pod가 계속 90% 근처라면 HPA는 replica를 늘리려 합니다.

하지만 여기서 끝나지 않습니다. 새 Pod를 올릴 노드 자리가 없으면 Pending 상태가 생기고, 그 다음엔 Cluster Autoscaler 차례가 옵니다.

---

## Cluster Autoscaler — Node 수를 자동으로 조절

Cluster Autoscaler는 이름 그대로 노드 레벨 스케일러입니다.

- 새 Pod가 스케줄되지 못하면 노드를 늘릴 수 있습니다.
- 비어 있는 노드가 오래 남으면 노드를 줄일 수 있습니다.

중요한 점은 이것입니다.

> Cluster Autoscaler는 Pod를 직접 늘리지 않습니다. 스케줄할 자리가 부족할 때 Node Pool의 노드 수를 조절합니다.

따라서 HPA와 Cluster Autoscaler는 경쟁 관계가 아니라 **서로 다른 층의 보완 관계**입니다.

---

## HPA와 CA가 같이 움직이는 모습

```mermaid
sequenceDiagram
    autonumber
    participant Load as Traffic
    participant H as HPA
    participant D as Deployment
    participant S as Scheduler
    participant C as Cluster Autoscaler

    Load->>H: CPU 상승
    H->>D: replicas 증가
    D->>S: 새 Pod 생성
    S-->>D: 자리가 부족해 Pending
    S->>C: unschedulable pod 존재
    C->>S: 노드 추가 후 재스케줄
```

이 그림을 머리에 넣어 두면 “Pod는 늘었는데 왜 아직 응답이 느리지?”라는 질문에 답하기 쉽습니다. HPA가 먼저 반응해도, 노드가 붙는 데 시간이 걸리면 잠깐 Pending이 생길 수 있습니다.

---

## KEDA — 이벤트 기반으로 HPA를 확장

KEDA는 Kubernetes Event-driven Autoscaling입니다.

- Azure Service Bus 메시지 수
- Event Hub lag
- Cron
- Kafka, RabbitMQ 같은 외부 시스템 신호

이런 이벤트를 읽어 스케일링 신호로 바꾸는 역할을 합니다.

KEDA의 구조에서 중요한 부분은 두 개입니다.

- **KEDA operator**가 `ScaledObject`를 읽음
- **KEDA metrics server**가 HPA에 외부 메트릭을 제공함

즉 KEDA는 “외부 이벤트를 HPA가 이해할 수 있는 형태로 번역하고 연결하는 장치”라고 보면 됩니다.

---

## KEDA는 HPA 위에 올라간다

```mermaid
flowchart TB
    SO[ScaledObject] --> OP[KEDA operator]
    OP --> EXT[External metrics]
    EXT --> HPA[HPA]
    HPA --> DEP[Deployment replicas]
```

이 관계를 정확히 잡아야 합니다.

- HPA는 메트릭 기반 Pod autoscaler
- KEDA는 외부 이벤트 기반 메트릭을 연결하는 확장
- 결과적으로 KEDA도 보통 Pod 수를 바꾼다

따라서 같은 워크로드를 두고 사용자가 별도 HPA를 만들고, KEDA도 같은 대상을 스케일하려 하면 충돌하기 쉽습니다. 보통은 **KEDA가 그 워크로드의 HPA 경로를 책임지게 둡니다**.

---

## 언제 무엇을 쓰나

### HPA가 잘 맞는 경우

- HTTP API의 CPU 사용률이 부하와 잘 비례할 때
- 메모리나 애플리케이션 메트릭으로 스케일 판단이 가능할 때

### Cluster Autoscaler가 필요한 경우

- HPA가 늘린 Pod를 담을 노드 자리가 부족할 때
- 워크로드 밀도에 따라 노드 수를 줄였다 늘리고 싶을 때

### KEDA가 잘 맞는 경우

- 큐 길이나 스트림 lag가 부하의 핵심 신호일 때
- 이벤트가 없으면 0까지 줄이고 싶을 때
- 배치성, 비동기성 워크로드가 중심일 때

---

## FastAPI 예시로 보면

웹 요청을 직접 받는 FastAPI API라면 보통 HPA부터 봅니다.

- CPU 60% 목표
- 최소 2개, 최대 10개 replica

반면 FastAPI 앱이 Service Bus 큐를 소비하는 워커라면 KEDA가 더 어울릴 수 있습니다.

- 큐 메시지 0이면 replica 0
- 메시지가 쌓이면 1, 2, 5, 10으로 증가

즉 “웹 API냐, 이벤트 소비자냐”가 스케일링 전략을 가르는 경우가 많습니다.

---

## 아주 단순한 HPA 예시

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: fastapi-hello
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: fastapi-hello
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 60
```

이 예시는 평균 CPU 사용률을 기준으로 Deployment 복제본 수를 조절합니다.

---

## 아주 단순한 KEDA 예시

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: fastapi-worker
spec:
  scaleTargetRef:
    name: fastapi-worker
  minReplicaCount: 0
  maxReplicaCount: 20
  triggers:
    - type: azure-servicebus
      metadata:
        queueName: orders
        namespace: mybus
        messageCount: "10"
```

이 예시는 Service Bus 큐 길이를 보고 Deployment를 스케일합니다. 내부적으로는 KEDA가 메트릭을 제공하고, HPA 메커니즘을 이용해 복제본 수를 바꾸게 됩니다.

---

## 스케일링에서 자주 보는 오해

### “kubectl scale이면 HPA랑 같다”

아닙니다. `kubectl scale`은 수동으로 replica 수를 바꾸는 것입니다. HPA는 메트릭 기반 자동 조절입니다.

### “Cluster Autoscaler가 Pod를 늘린다”

아닙니다. Pod 수는 HPA나 수동 설정이 바꿉니다. Cluster Autoscaler는 노드 수를 바꿉니다.

### “KEDA가 HPA를 대체한다”

아닙니다. KEDA는 보통 HPA를 배경 메커니즘으로 활용합니다.

---

## 스케일링과 비용의 연결

스케일링은 곧 비용입니다.

- HPA는 애플리케이션 가용성과 응답성에 직접 연결됩니다.
- Cluster Autoscaler는 VM 비용과 직결됩니다.
- KEDA는 이벤트가 없을 때 0으로 내릴 수 있어 비용 절감 폭이 큽니다.

따라서 “더 잘 자동화된다”보다 “어떤 신호를 기준으로 어떤 비용을 지불할 것인가”로 읽는 편이 좋습니다.

---

## 운영에서 같이 봐야 하는 메트릭

- CPU, 메모리, 응답 시간
- Pending Pod 수
- 노드 사용률
- HPA 목표값 대비 현재값
- 큐 길이, lag, 처리량

이 메트릭들이 서로 다른 층의 신호라는 점이 중요합니다. CPU만 보면 Pod 레벨은 보이지만, 노드 포화나 큐 적체는 놓칠 수 있습니다.

---

## 다음 화에서

이번 글에서 나온 메트릭과 이벤트는 결국 “어디서 보고, 어떻게 알람을 거나”로 이어집니다. 7화에서는 Container Insights, Log Analytics 쿼리, kube-state-metrics, 알람을 묶어서 AKS 운영의 기본 관측 체계를 정리하겠습니다.

---

이 글은 Azure Kubernetes Service 101 시리즈의 6화입니다. 5화까지가 클러스터 구조와 요청 경로를 설명하는 글이었다면, 이번 화는 부하 변화에 시스템이 어떻게 반응하는지를 설명하는 글입니다. 마지막 7화에서는 이 반응을 관찰하고 경고로 연결하는 모니터링과 운영 도구를 정리합니다.

---

## 참고 자료

### 공식 문서
- [Scaling options for applications in AKS](https://learn.microsoft.com/en-us/azure/aks/concepts-scale)
- [Cluster autoscaler on AKS](https://learn.microsoft.com/en-us/azure/aks/cluster-autoscaler)
- [Kubernetes Event-driven Autoscaling (KEDA)](https://learn.microsoft.com/en-us/azure/aks/keda-about)
- [Autoscale pods in AKS](https://learn.microsoft.com/en-us/azure/aks/tutorial-kubernetes-scale#autoscale-pods)

### 관련 시리즈
- [Azure App Service 101](../../azure-app-service-101/ko/07-scaling-101.md) — 인스턴스 스케일과 Kubernetes 스케일의 차이를 비교할 때
- [Azure Functions 101](../../azure-functions-101/ko/06-scaling-and-cold-start.md) — 서버리스 스케일 모델과 비교할 때
