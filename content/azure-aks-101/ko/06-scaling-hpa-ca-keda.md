---
title: "Azure Kubernetes Service 101 (6/7): 스케일링 — HPA, Cluster Autoscaler, KEDA"
series: azure-aks-101
episode: 6
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
seo_description: AKS에서 스케일링이 헷갈리는 이유는 “늘린다”는 말이 두 가지를 동시에 가리키기 때문입니다.
---

# Azure Kubernetes Service 101 (6/7): 스케일링 — HPA, Cluster Autoscaler, KEDA

AKS에서 스케일링이 헷갈리는 이유는 “늘린다”는 말이 여러 층을 동시에 가리키기 때문입니다. 어떤 경우에는 Pod 수를 늘리는 일이 핵심이고, 어떤 경우에는 새 Pod를 담을 노드를 늘리는 일이 핵심입니다. 여기에 외부 이벤트 기반 워크로드까지 들어오면 HPA, Cluster Autoscaler, KEDA가 서로 비슷한 도구처럼 보이기 쉽습니다.

하지만 이 셋은 같은 문제를 반복해서 푸는 도구가 아닙니다. 보는 신호도 다르고, 조절하는 대상도 다르고, 비용에 미치는 방식도 다릅니다. 이 차이를 모르고 쓰면 autoscaling이 “자동”이 아니라 오히려 예측하기 어려운 비용과 지연의 원인이 되기도 합니다.

이 글은 Azure AKS 101 시리즈의 6번째 글입니다.

여기서는 **HPA는 Pod 수를, Cluster Autoscaler는 Node 수를, KEDA는 외부 이벤트를 HPA 경로로 연결한다**는 기본 구조를 분리해서 보겠습니다. 그 위에서 어떤 워크로드에 어떤 스케일러가 잘 맞는지도 함께 정리하겠습니다.

## 먼저 던지는 질문

- HPA, Cluster Autoscaler, KEDA는 각각 어떤 신호를 보고 무엇을 바꿀까요?
- CPU나 메모리 기반 HPA만으로 부족한 상황은 언제일까요?
- Pod는 늘어났는데 응답이 바로 좋아지지 않는 이유는 어디에 있을까요?

## 큰 그림

![Azure Kubernetes Service 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/azure-aks-101/06/06-01-one-diagram-first.ko.png)

*Azure Kubernetes Service 101 6장 흐름 개요*

이 그림에서는 스케일링 — HPA, Cluster Autoscaler, KEDA를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 스케일링 — HPA, Cluster Autoscaler, KEDA의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 이 글이 중요한가

스케일링은 AKS에서 가장 쉽게 오해되는 운영 주제 중 하나입니다. CPU가 높으니 HPA만 켜면 된다고 생각하기 쉽지만, 실제로는 새 Pod를 놓을 노드 자리가 없어서 Pending이 쌓일 수 있습니다. 반대로 노드를 자동으로 늘려도, 정작 수요 신호가 큐 길이에 있는데 CPU만 보고 있다면 핵심 압력을 놓칠 수 있습니다.

또한 autoscaling은 비용과 직결됩니다. Pod를 늘리는 정책은 애플리케이션 비용과 응답성에 영향을 주고, 노드를 늘리는 정책은 VM 비용과 직접 연결됩니다. KEDA는 scale to zero를 가능하게 해 큰 비용 절감을 줄 수 있지만, 잘못 쓰면 외부 시스템 신호에 과민하게 반응할 수도 있습니다.

무엇보다 HPA, Cluster Autoscaler, KEDA를 구분해서 볼 수 있어야 운영 현상을 읽을 수 있습니다. “Pod는 늘었는데 왜 아직 느리지?”, “노드는 남는데 왜 큐가 밀리지?”, “왜 replica가 0까지 내려가도 되는 워크로드와 안 되는 워크로드가 있지?” 같은 질문은 모두 이 구조를 정확히 알아야 답할 수 있습니다.

## 핵심 관점

세 스케일러를 한 번에 외우기보다, 먼저 세 가지 질문으로 나누는 편이 좋습니다. 어떤 신호를 보는가, 무엇을 늘리거나 줄이는가, 어느 계층에서 동작하는가. 이 세 질문을 붙이면 HPA는 Pod 레벨, Cluster Autoscaler는 Node Pool 레벨, KEDA는 외부 이벤트를 Pod autoscaling 경로로 번역하는 레벨이라는 구조가 자연스럽게 드러납니다.

이 기준이 유용한 이유는 autoscaling 문제를 디버깅할 때도 그대로 쓰이기 때문입니다. HPA가 replica를 올렸는데 Pending이 쌓이면 Node 계층을 봐야 하고, CPU는 평온한데 큐 backlog가 늘어나면 KEDA 같은 외부 신호 경로를 봐야 합니다. 즉 “무엇이 자동으로 조절되고 있는가”보다 “어떤 신호가 어느 계층을 움직이는가”가 더 중요합니다.

따라서 이 글에서는 HPA, Cluster Autoscaler, KEDA를 각각 독립적으로 본 뒤, 마지막에 셋이 함께 움직일 때 어떤 현상이 나타나는지 연결하겠습니다.

> HPA는 Pod 수를, Cluster Autoscaler는 Node 수를, KEDA는 외부 이벤트를 Pod autoscaling 신호로 바꾸는 역할을 맡습니다. 세 도구는 경쟁 관계가 아니라 계층 분담 관계입니다.

## 핵심 개념

### 먼저 관계를 한 장으로 정리합니다

전체 구조를 먼저 보면 이후 세부가 훨씬 쉬워집니다.

이 그림의 문장을 풀면 다음과 같습니다.

- HPA는 **Pod 수**를 조절합니다.
- Cluster Autoscaler는 **Node 수**를 조절합니다.
- KEDA는 외부 이벤트를 읽어 **HPA 경로를 확장하는 방식**으로 Pod autoscaling을 돕습니다.

초반에 가장 먼저 지워야 할 오해는 이것입니다. **KEDA는 HPA를 대체하는 것이 아니라, HPA가 이해할 수 있는 신호의 범위를 넓혀 주는 확장 계층**입니다.

### HPA는 Pod 수를 자동으로 조절합니다

HPA는 Horizontal Pod Autoscaler입니다. 대상은 보통 Deployment이고, 입력은 CPU, 메모리, 또는 custom/external metrics이며, 결과는 replica 수 변경입니다.

즉 HPA가 답하는 질문은 하나입니다. **지금 이 워크로드 인스턴스가 몇 개 있어야 하는가**입니다.

#### HPA가 잘 동작하려면 입력 품질이 좋아야 합니다

HPA는 피드백 루프입니다. 따라서 입력 신호가 나쁘면 결과도 흔들립니다.

- metrics-server가 정상이어야 합니다.
- CPU request가 현실적인 값이어야 합니다.
- readiness 동작이 실제 트래픽 수용 가능 시점을 반영해야 합니다.

CPU request가 너무 엉뚱하면 utilization 계산 자체가 왜곡됩니다. readiness가 부정확하면 새 Pod가 너무 빨리 트래픽을 받거나 너무 늦게 붙습니다. 그래서 HPA는 “켜기만 하면 되는 기능”이 아니라 입력 신호 품질에 민감한 제어 루프라고 보는 편이 맞습니다.

### HPA의 결정 루프를 보면 Pending 현상이 왜 생기는지 이해됩니다

![메트릭 기반 HPA 스케일링 루프](https://yeongseon-books.github.io/book-public-assets/assets/azure-aks-101/06/06-02-the-hpa-loop.ko.png)

*메트릭 기반 HPA 스케일링 루프*

예를 들어 FastAPI API가 두 Pod로 실행 중이고 목표 CPU가 60%인데 평균이 계속 90%라면, HPA는 replica 수를 늘리려 합니다. 여기까지는 비교적 직관적입니다.

하지만 HPA가 replica를 늘린다고 곧바로 응답 품질이 좋아지는 것은 아닙니다. 새 Pod를 놓을 노드 자리가 없으면 Pod는 Pending 상태가 됩니다. 바로 이 지점에서 Node 계층의 autoscaling이 필요해집니다.

### Cluster Autoscaler는 Node Pool 용량을 조절합니다

Cluster Autoscaler는 이름 그대로 노드 레벨 스케일러입니다.

- 새 Pod가 스케줄되지 못하면 노드를 늘릴 수 있습니다.
- 노드가 오래 비어 있으면 노드를 줄일 수 있습니다.

가장 중요한 문장은 아래와 같습니다.

> Cluster Autoscaler는 Pod를 직접 늘리지 않습니다. Pod를 놓을 자리가 부족할 때 Node Pool의 노드 수를 조절합니다.

즉 HPA와 Cluster Autoscaler는 경쟁 관계가 아닙니다. HPA가 Pod 레벨의 수요를 반영하고, Cluster Autoscaler가 그 Pod를 담을 수용 공간을 확장하는 구조입니다.

### HPA와 Cluster Autoscaler가 함께 움직일 때 현상이 보입니다

![Pod 증가와 노드 확장의 연동 흐름](https://yeongseon-books.github.io/book-public-assets/assets/azure-aks-101/06/06-03-hpa-and-cluster-autoscaler-together.ko.png)

*Pod 증가와 노드 확장의 연동 흐름*

이 그림을 이해하면 “Pod는 늘었는데 왜 아직 느리지?”라는 질문에 답하기 쉬워집니다. HPA는 먼저 반응하지만, 노드가 실제로 붙고 스케줄링이 끝나고 새 Pod가 Ready가 되기까지는 시간이 걸립니다. 즉 Pod autoscaling과 Node autoscaling 사이에는 늘 시간차가 있습니다.

운영에서는 이 시간차를 고려해 최소 replica, 최소 node 수, probe 설정, startup time을 함께 설계해야 합니다. autoscaling은 즉시 마법처럼 해결되는 기능이 아니라, 여러 계층의 반응 시간을 조합하는 제어 시스템입니다.

### KEDA는 외부 이벤트를 HPA 경로로 연결합니다

KEDA는 Kubernetes Event-driven Autoscaling입니다. CPU나 메모리보다 큐 길이, lag, cron schedule 같은 외부 이벤트가 수요를 더 잘 설명할 때 특히 유용합니다.

- Azure Service Bus 메시지 수
- Event Hub lag
- cron 기반 스케줄
- Kafka, RabbitMQ backlog

KEDA 구조에서 중요한 구성 요소는 두 개입니다.

- **KEDA operator**가 `ScaledObject`를 읽습니다.
- **KEDA metrics server**가 외부 메트릭을 autoscaling 경로에 제공합니다.

그래서 KEDA를 가장 정확하게 짧게 설명하면 “외부 이벤트 압력을 HPA가 이해할 수 있는 형태로 번역하는 장치”입니다.

### KEDA는 HPA 위에 올라가는 확장 계층입니다

![KEDA와 HPA의 확장 관계](https://yeongseon-books.github.io/book-public-assets/assets/azure-aks-101/06/06-04-keda-sits-on-top-of-hpa.ko.png)

*KEDA와 HPA의 확장 관계*

이 관계는 정확히 기억해 두는 편이 좋습니다.

- HPA는 Pod autoscaling 메커니즘입니다.
- KEDA는 그 메커니즘을 움직일 신호 종류를 넓혀 줍니다.
- KEDA가 관리하는 워크로드도 대체로 Pod 수를 바꾸는 방식으로 동작합니다.

그래서 같은 워크로드에 사용자가 별도 HPA를 붙이고 KEDA도 붙이면 충돌이 나기 쉽습니다. 보통은 **KEDA가 그 워크로드의 autoscaling 경로를 책임지게 두는 편**이 더 단순합니다.

### 어떤 워크로드에 무엇이 맞는지 구분할 수 있어야 합니다

#### HPA가 잘 맞는 경우

- HTTP API의 부하가 CPU나 메모리와 reasonably well하게 연결될 때
- custom application metrics가 실제 압력을 잘 표현할 때

#### Cluster Autoscaler가 필요한 경우

- HPA가 만든 Pod를 담을 노드 자리가 부족할 때
- 수요에 따라 Node Pool 용량도 같이 확장·축소하고 싶을 때

#### KEDA가 잘 맞는 경우

- 큐 길이나 lag가 진짜 수요 신호일 때
- 이벤트가 없을 때 0까지 줄이고 싶을 때
- 비동기·배치·이벤트 중심 워크로드일 때

즉 “어느 autoscaler가 더 좋나”보다 “이 워크로드의 압력을 가장 잘 설명하는 신호가 무엇인가”를 먼저 묻는 편이 맞습니다.

### FastAPI 예시로 보면 선택이 더 쉬워집니다

웹 요청을 직접 받는 FastAPI API라면 보통 HPA부터 보는 편이 자연스럽습니다.

- CPU 60% 목표
- 최소 2개, 최대 10개 replica

반면 FastAPI 워커가 Azure Service Bus 큐를 소비한다면 KEDA가 더 어울릴 수 있습니다.

- 메시지가 없으면 replica 0
- backlog가 쌓이면 1, 2, 5, 10처럼 증가

즉 HTTP-serving API와 event consumer는 겉으로는 둘 다 Python 앱일 수 있어도, 스케일링 신호가 전혀 다를 수 있습니다.

### 최소 HPA 예시는 이렇게 생깁니다

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

이 예시는 평균 CPU 사용률을 기준으로 Deployment 복제본 수를 조절합니다. 가장 단순하지만, 실제 운영에서도 여전히 매우 흔한 패턴입니다.

### KEDA Service Bus 예시는 외부 신호 wiring을 보여 줍니다

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: servicebus-secret
type: Opaque
stringData:
  connection: "Endpoint=sb://your-namespace.servicebus.windows.net/;SharedAccessKeyName=...;SharedAccessKey=..."
---
apiVersion: keda.sh/v1alpha1
kind: TriggerAuthentication
metadata:
  name: servicebus-trigger-auth
spec:
  secretTargetRef:
    - parameter: connection
      name: servicebus-secret
      key: connection
---
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: orders-scaler
spec:
  scaleTargetRef:
    name: orders-deployment
  pollingInterval: 30
  minReplicaCount: 0
  maxReplicaCount: 20
  triggers:
    - type: azure-servicebus
      metadata:
        queueName: orders
        messageCount: "5"
      authenticationRef:
        name: servicebus-trigger-auth
```

여기서 핵심은 인증 wiring입니다. `TriggerAuthentication`이 `connection` 파라미터를 어디서 읽을지 정의하고, Secret이 실제 연결 문자열을 담고 있으며, `authenticationRef`가 이를 trigger와 연결합니다. 외부 이벤트 기반 autoscaling은 결국 신호 자체보다도 **그 신호를 안정적으로 읽는 연결 구조**가 중요합니다.

### 스케일링은 곧 비용입니다

autoscaling은 신뢰성과 비용을 동시에 다룹니다.

- HPA는 애플리케이션 응답성과 가용성에 직접 연결됩니다.
- Cluster Autoscaler는 VM 비용과 직결됩니다.
- KEDA는 이벤트가 없을 때 0까지 줄일 수 있어 비용 절감 폭이 큽니다.

따라서 스케일링 설계는 “더 자동화된다”보다 “어떤 신호를 기준으로 어떤 비용을 지불할 것인가”로 읽는 편이 더 정확합니다. 잘못된 min/max 범위나 과민한 임계값은 곧 비용 문제로 돌아옵니다.

### HPA와 Cluster Autoscaler를 함께 볼 때는 이벤트 순서를 확인합니다

스케일링 장애 분석에서 가장 유용한 습관은 시간 순서를 보는 것입니다. “HPA가 먼저 replica를 올렸는가”, “그다음 Pending이 생겼는가”, “마지막에 노드가 추가됐는가”를 분리하면 원인을 빠르게 좁힐 수 있습니다.

```bash
kubectl get hpa -w
kubectl get pods -A --field-selector=status.phase=Pending
kubectl get events -A --sort-by=.lastTimestamp
kubectl get nodes -o wide
```

실전에서 자주 보는 흐름은 이렇습니다. HPA가 목표치를 초과해 replica를 올리고, 잠시 뒤 `0/2 nodes are available`류의 스케줄링 이벤트가 발생하고, Cluster Autoscaler가 노드를 늘린 다음 새 Pod가 Ready가 됩니다. 이 시간차를 모르면 autoscaling이 실패한 것처럼 보이기 쉽습니다.

### KEDA 워크로드는 안정화 구간과 cooldown을 같이 설계합니다

KEDA는 외부 이벤트 신호를 매우 빠르게 반영할 수 있어 장점이 큽니다. 다만 입력 신호가 출렁이면 replica도 출렁일 수 있으므로 안정화 구간을 함께 잡는 편이 좋습니다. 특히 큐 기반 워크로드는 짧은 burst가 잦아 과민 반응을 피하는 설정이 중요합니다.

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: orders-scaler
spec:
  scaleTargetRef:
    name: orders-deployment
  minReplicaCount: 0
  maxReplicaCount: 30
  pollingInterval: 30
  cooldownPeriod: 300
  advanced:
    horizontalPodAutoscalerConfig:
      behavior:
        scaleUp:
          stabilizationWindowSeconds: 0
        scaleDown:
          stabilizationWindowSeconds: 300
  triggers:
    - type: azure-servicebus
      metadata:
        queueName: orders
        messageCount: "10"
      authenticationRef:
        name: servicebus-trigger-auth
```

이 예시는 scale up은 빠르게, scale down은 천천히 하겠다는 의도를 명확히 드러냅니다. 트래픽 품질과 비용을 동시에 보려면 “얼마나 빨리 늘릴까”만큼 “얼마나 신중히 줄일까”도 중요합니다.

### 스케일링 장애를 재현 가능한 방식으로 읽는 예시

다음은 운영에서 자주 보는 시나리오입니다. 평균 CPU가 목표치를 넘어서 HPA가 replica를 올렸지만, user pool 용량이 부족해 일부 Pod가 Pending으로 남는 상황입니다. 이때는 HPA가 실패한 것이 아니라 계층 간 시간차가 발생한 것입니다.

```bash
kubectl get hpa fastapi-hello
kubectl describe hpa fastapi-hello
kubectl get pods -l app=fastapi-hello -o wide
kubectl describe pod <pending-pod-name>
```

`describe hpa`에서 desired replica가 증가했다면 Pod 계층은 반응한 상태입니다. 이어서 `describe pod`에 `Insufficient cpu` 또는 `No nodes are available`가 보이면 Node 계층 병목입니다. 이런 식으로 읽어야 “어떤 autoscaler를 조정할지”가 명확해집니다.

### Cluster Autoscaler 범위 설계는 워크로드 등급과 같이 봅니다

많은 팀이 min/max 노드 값을 임의 숫자로 두는데, 더 안전한 방법은 워크로드 등급별로 기준 용량을 먼저 정하는 것입니다. 예를 들어 핵심 API는 최소 2노드 유지, 비핵심 워커 풀은 0까지 허용처럼 명시하면 비용과 가용성을 동시에 관리하기 쉬워집니다.

```bash
az aks nodepool update \
  --resource-group "$RG" \
  --cluster-name "$CLUSTER" \
  --name userpoolapi \
  --enable-cluster-autoscaler \
  --min-count 2 \
  --max-count 10
```

이 숫자는 성능 테스트와 장애 예행연습으로 검증해야 합니다. autoscaling은 설정 자체보다 검증 루프가 더 중요합니다. 값이 그럴듯해 보여도 실제 burst 트래픽에서 ready 지연이 길면 사용자 체감은 여전히 나쁠 수 있습니다.

마지막으로 autoscaling을 도입한 워크로드는 배포 직후 꼭 baseline 부하 테스트를 남겨 두는 편이 좋습니다. 평상시 트래픽, 2배 burst, 5분 지속 부하 같은 단순 시나리오라도 기록해 두면 이후 임계값 조정의 기준점이 생깁니다. 기준점이 없으면 “느린 것 같다”는 체감만 남고, 정책 튜닝이 반복 시행착오로 흐르기 쉽습니다.

그리고 이 결과를 릴리스 노트에 함께 남기면, 다음 버전에서 스케일링 특성이 바뀌었는지 비교하기 쉬워집니다. autoscaling은 코드 변경과 분리된 운영 영역처럼 보이지만, 실제로는 애플리케이션 동작 변화에 매우 민감하게 반응합니다.

## 흔히 헷갈리는 지점

- `kubectl scale`과 HPA를 비슷한 것으로 생각하기 쉽지만, 하나는 수동 변경이고 다른 하나는 자동 제어 루프입니다.
- Cluster Autoscaler가 Pod를 늘린다고 오해하기 쉽지만, 실제로는 Node Pool 용량만 바꿉니다.
- KEDA가 HPA를 대체한다고 생각하기 쉽지만, 보통은 HPA 경로를 확장하는 구조입니다.
- Pod 수가 늘면 즉시 응답성이 좋아질 것이라 기대하기 쉽지만, 노드 확보와 Ready 시간 때문에 지연이 생길 수 있습니다.
- scale to zero가 모든 워크로드에 좋다고 생각하기 쉽지만, 항상 떠 있어야 하는 HTTP 서비스에는 적합하지 않을 수 있습니다.

## 운영 체크리스트

- [ ] 각 워크로드의 실제 수요 신호가 CPU인지, 메모리인지, 큐 backlog인지 구분했는가
- [ ] HPA 임계값과 min/max replica를 측정 기반으로 정했는가
- [ ] Pending Pod가 생길 때 Cluster Autoscaler가 개입할 충분한 Node Pool 범위를 두었는가
- [ ] KEDA 사용 시 별도 HPA와 충돌하지 않도록 autoscaling 책임 경계를 정했는가
- [ ] autoscaling 정책이 신뢰성 목표뿐 아니라 비용 한도와도 맞는지 검토했는가

## 정리

이 글의 핵심은 HPA, Cluster Autoscaler, KEDA를 같은 종류의 도구로 보지 않는 것입니다. HPA는 Pod 수를, Cluster Autoscaler는 Node 수를, KEDA는 외부 이벤트를 Pod autoscaling 신호로 연결합니다. 즉 세 도구는 경쟁 관계가 아니라 서로 다른 계층을 맡는 분업 구조입니다.

또한 autoscaling은 성능 기능이면서 동시에 비용 기능입니다. 잘 맞는 신호를 고르고, 현실적인 min/max 범위를 정하고, Pending과 node expansion 사이의 시간차를 고려해야 안정성과 비용을 함께 잡을 수 있습니다. 자동화라고 해서 설계 판단이 사라지는 것은 아닙니다.

이제 마지막 7화로 넘어가면 오늘 나온 메트릭과 이벤트를 어디서 보고 어떻게 알람으로 연결할지 다루게 됩니다. 즉 스케일링의 동작 자체를 본 뒤, 다음 글에서는 그 동작을 **관찰하고 경고로 연결하는 운영 시야**를 정리하게 됩니다.

## 처음 질문으로 돌아가기

- **HPA, Cluster Autoscaler, KEDA는 각각 어떤 신호를 보고 무엇을 바꿀까요?**
  - 본문의 기준은 스케일링 — HPA, Cluster Autoscaler, KEDA를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **CPU나 메모리 기반 HPA만으로 부족한 상황은 언제일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **Pod는 늘어났는데 응답이 바로 좋아지지 않는 이유는 어디에 있을까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Azure Kubernetes Service 101 (1/7): Azure Kubernetes Service란? — 직접 운영하지 않아도 되는 Kubernetes](./01-what-is-aks.md)
- [Azure Kubernetes Service 101 (2/7): 클러스터 아키텍처 — Control Plane과 Node Pool](./02-cluster-architecture.md)
- [Azure Kubernetes Service 101 (3/7): 첫 클러스터 만들고 앱 배포하기 — Python/FastAPI](./03-first-cluster-and-deploy.md)
- [Azure Kubernetes Service 101 (4/7): Pod·Deployment·Service — 워크로드를 표현하는 세 가지 방식](./04-pod-deployment-service.md)
- [Azure Kubernetes Service 101 (5/7): 네트워킹과 Ingress — 클러스터 안과 밖을 잇는 길](./05-networking-and-ingress.md)
- **Azure Kubernetes Service 101 (6/7): 스케일링 — HPA, Cluster Autoscaler, KEDA (현재 글)**
- Azure Kubernetes Service 101 (7/7): 모니터링과 운영 — Container Insights, 로그, 알람 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [Scaling options for applications in AKS](https://learn.microsoft.com/en-us/azure/aks/concepts-scale)
- [Cluster autoscaler on AKS](https://learn.microsoft.com/en-us/azure/aks/cluster-autoscaler)
- [Kubernetes Event-driven Autoscaling (KEDA)](https://learn.microsoft.com/en-us/azure/aks/keda-about)
- [Autoscale pods in AKS](https://learn.microsoft.com/en-us/azure/aks/tutorial-kubernetes-scale#autoscale-pods)

### 관련 시리즈

- [Azure App Service 101](../../azure-app-service-101/ko/07-scaling-101.md) — 인스턴스 스케일과 Kubernetes 스케일의 차이를 비교할 때
- [Azure Functions 101](../../azure-functions-101/ko/06-scaling-and-cold-start.md) — 서버리스 스케일 모델과 비교할 때

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-aks-101/ko/06-scaling-hpa-ca-keda)

Tags: Azure, AKS, Kubernetes, Cloud
