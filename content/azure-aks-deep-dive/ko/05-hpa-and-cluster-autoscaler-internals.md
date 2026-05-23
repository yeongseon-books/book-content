---
title: "Azure Kubernetes Service Deep Dive (5/6): HPA와 Cluster Autoscaler 내부 — 두 컨트롤 루프"
series: azure-aks-deep-dive
episode: 5
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- AKS
- Kubernetes
- Distributed Systems
- Containers
last_reviewed: '2026-05-12'
seo_description: AKS HPA와 Cluster Autoscaler의 작동 원리를 루프별로 분석하여 두 루프 간 지연 현상의 구조적 원인을 설명합니다.
---

# Azure Kubernetes Service Deep Dive (5/6): HPA와 Cluster Autoscaler 내부 — 두 컨트롤 루프

트래픽이 늘었는데 새 Pod가 바로 Ready가 되지 않으면 많은 팀이 “autoscaling이 느리다”라고 말합니다.
하지만 그 표현 안에는 사실 두 개의 서로 다른 루프가 숨어 있습니다.
하나는 replica 수를 바꾸는 HPA이고, 다른 하나는 node 수를 바꾸는 Cluster Autoscaler이며, 둘은 다른 입력과 다른 시간축으로 움직입니다.

이 두 루프를 분리하지 않으면 정상 지연도 장애처럼 보이기 쉽습니다.
HPA는 이미 replica를 올렸지만 scheduler가 새 Pod를 놓을 빈자리가 없어서 Pending이 생길 수 있습니다.
그 다음에야 Cluster Autoscaler가 unschedulable Pod를 보고 새 node를 준비하므로, 두 단계 사이의 기다림은 구조적으로 자연스러운 현상입니다.

이번 글의 목표는 HPA와 Cluster Autoscaler를 하나의 autoscaling 블랙박스로 보지 않고, 서로 다른 제어 루프로 분리해서 읽는 것입니다.
그래야 replica 조정과 node 조정을 각각 다른 mental bucket에 넣고, 어디서 race window가 생기는지 분리해서 볼 수 있습니다.
이제 두 루프가 어디서 만나고 왜 race window가 생기는지 보겠습니다.

![Azure Kubernetes Service Deep Dive 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/azure-aks-deep-dive/05/05-01-put-both-loops-in-one-diagram.ko.png)
*Azure Kubernetes Service Deep Dive 5장 흐름 개요*
> HPA와 Cluster Autoscaler 내부 — 두 컨트롤 루프의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 먼저 던지는 질문

- HPA는 어떤 메트릭을 어떤 주기로 읽고 desired replica를 계산할까요?
- Cluster Autoscaler는 어떤 신호를 보고 “새 노드가 필요하다”고 판단할까요?
- HPA와 Cluster Autoscaler가 동시에 움직일 때 race window는 왜 생길까요?

## 왜 이 글이 중요한가

autoscaling은 단순한 비용 최적화 기능이 아닙니다.
실제 운영에서는 지연 시간, 가용성, downstream 보호, 비용이 모두 여기서 만납니다.
특히 replica가 늘었는데도 Ready Pod가 늦게 붙는 현상을 이해하지 못하면, 팀은 HPA 임계치만 계속 만지거나 node pool 크기만 과도하게 올리는 식으로 잘못된 보정에 빠지기 쉽습니다.

또한 AKS에서 Cluster Autoscaler는 사용자가 직접 배포하는 일반 워크로드가 아니라 관리형 control plane의 일부로 다뤄집니다.
즉 HPA와 CA를 모두 “내가 클러스터 안에서 운영하는 Pod”처럼 생각하면 관찰 표면과 설정 표면을 잘못 잡게 됩니다.
어디까지가 내가 조정하는 정책이고, 어디부터가 서비스가 운영하는 루프인지를 구분해야 합니다.

마지막으로 이 글은 KEDA를 정확히 위치시키기 위한 준비 단계이기도 합니다.
5화에서 HPA와 CA를 먼저 분리해 두어야 6화에서 KEDA가 HPA를 대체하는 것이 아니라 그 위에 올라타 external metric과 0↔1 경계를 맡는다는 설명이 훨씬 선명해집니다.

## 핵심 관점

이 주제에서 가장 먼저 잡아야 할 문장은 이것입니다.
**HPA는 Pod 수를 바꾸고, Cluster Autoscaler는 node 수를 바꿉니다. 둘은 같은 autoscaling 우산 아래 있지만 서로를 대체하지 않습니다.**
이 한 줄이 autoscaling 관련 혼란의 절반을 정리해 줍니다.

이 구분이 중요한 이유는 두 루프가 서로 다른 입력을 사용하기 때문입니다.
HPA는 메트릭을 보고 desired replica를 계산합니다.
Cluster Autoscaler는 unschedulable Pod를 보고 “이 Pod들이 새 node가 생기면 스케줄 가능해질까”를 시뮬레이션합니다.

따라서 둘이 동시에 움직일 때는 반드시 시간차가 생깁니다.
HPA가 먼저 Pod를 늘리고, scheduler가 빈자리를 못 찾아 Pending을 만들고, 그 후에야 CA가 node를 추가합니다.
이 대기 구간이 바로 운영에서 자주 보이는 race window입니다.

> “autoscaling이 느리다”는 말은 보통 하나의 문제라기보다 HPA의 replica 결정, scheduler의 placement 결과, Cluster Autoscaler의 node 추가가 서로 다른 속도로 움직이는 현상을 한 문장으로 줄인 표현입니다.

## 핵심 개념

### 두 루프를 한 그림으로 봐야 관계가 선명해집니다

아래 그림은 이번 글의 기준점입니다.
Pod 수를 다루는 루프와 node 수를 다루는 루프가 같은 화면에 놓여 있어야 race window가 왜 생기는지 자연스럽게 보입니다.
특히 scheduler가 중간에 들어간다는 점이 중요합니다.

이 그림을 읽는 핵심은 HPA가 replica를 늘려도 곧바로 node가 생기는 것은 아니라는 사실입니다.
중간에 placement와 unschedulable 판정이 있어야 CA가 움직입니다.

### HPA는 메트릭 비율을 replica 수로 바꾸는 빠른 루프입니다

HPA control loop의 기본 sync period는 `--horizontal-pod-autoscaler-sync-period` 기준 15초입니다.
대표적인 계산 모델은 `desiredReplicas = ceil(currentReplicas * (currentMetric / targetMetric))`입니다.
실제 구현은 tolerance, missing metric, stabilization window를 더 고려하지만, 큰 그림은 비율 기반 replica 조정입니다.

운영적으로는 HPA가 두 루프 중 더 빠른 편입니다.
그래서 수요가 늘면 먼저 replica 증가 결정이 나오고, 클러스터에 빈 node 자원이 없으면 새 Pod는 Ready 대신 Pending으로 보일 수 있습니다.

![메트릭으로 replica 수를 조정하는 HPA 루프](https://yeongseon-books.github.io/book-public-assets/assets/azure-aks-deep-dive/05/05-02-the-hpa-side.ko.png)

*메트릭으로 replica 수를 조정하는 HPA 루프*

즉 HPA가 빠르다는 사실은 곧 Pending Pod의 증가로 먼저 체감될 수 있다는 뜻이기도 합니다.
이 현상은 장애가 아니라 정상 제어 루프의 중간 상태일 수 있습니다.

### Cluster Autoscaler는 unschedulable Pod를 보고 node 수를 조정합니다

CA는 메트릭을 직접 보고 replica를 계산하지 않습니다.
대신 unschedulable Pod를 감시하고, 각 node pool의 template node를 기준으로 binpacking estimator를 돌려 “새 노드가 생기면 이 Pod들이 스케줄 가능해지는가”를 따집니다.
이후 적절한 pool을 선택해 node 수 조정을 요청합니다.

AKS에서는 CA도 관리형 control plane 이야기의 일부입니다.
사용자는 `az aks update --cluster-autoscaler-profile` 같은 표면으로 프로필을 조정하지만, 일반적으로 CA Pod를 직접 배포하거나 운영하지는 않습니다.

### CA 기본값은 일부러 보수적입니다

AKS 기본값에서 `scan-interval`은 10초이고, 새 node provisioning 대기 한계인 `max-node-provision-time`은 기본 15분입니다.
또한 `scale-down-unneeded-time`과 `scale-down-delay-after-add`는 둘 다 기본 10분으로 꽤 보수적입니다.
이 설계는 scale-up과 scale-down이 같은 속도로 움직이지 않도록 의도한 것입니다.

![미배치 Pod를 보고 노드를 늘리는 CA 루프](https://yeongseon-books.github.io/book-public-assets/assets/azure-aks-deep-dive/05/05-03-the-ca-side.ko.png)

*미배치 Pod를 보고 노드를 늘리는 CA 루프*

운영 관점에서는 이 기본값이 비용과 안정성 사이의 기본 타협점입니다.
빠른 scale-up은 중요하지만, 빠른 scale-down은 오히려 출렁임과 재기동 비용을 키울 수 있습니다.

### race window는 설계 버그가 아니라 구조적 결과입니다

HPA가 replica를 늘리고, scheduler가 새 Pod를 Pending으로 남기고, CA가 이를 감지해 새 node를 준비하고, node가 Ready 된 뒤에야 Pending Pod가 Binding됩니다.
이 순서를 보면 race window는 우연한 버그가 아니라 두 제어 루프가 서로 다른 입력을 사용하기 때문에 생기는 구조적 결과입니다.

실무에서 중요한 것은 이 대기 구간을 없애겠다고 무조건 임계치를 공격적으로 만드는 것이 아닙니다.
오히려 워크로드 특성에 따라 baseline replica, 적절한 min node, scale-down 지연, burst 대응 전략을 함께 잡는 편이 더 현실적입니다.

### scale-up은 빠르게, scale-down은 느리게 설계하는 편이 안전합니다

사용자 요청을 놓치는 비용은 대개 여분 자원을 잠시 더 쓰는 비용보다 큽니다.
그래서 autoscaling은 보통 scale-up을 빠르게, scale-down을 더 천천히 만드는 방향으로 설계됩니다.
HPA stabilization window와 CA의 보수적인 scale-down 지연도 같은 철학에서 읽을 수 있습니다.

이 감각이 없으면 운영자는 scale-down이 늦다는 이유만으로 지나치게 공격적인 값을 넣고, 결과적으로 thrashing과 재배치 비용을 키우기 쉽습니다.

### VPA와 HPA를 함께 쓸 수 있는지 여부는 워크로드 형태에 달려 있습니다

VPA, HPA, CA는 모두 자원을 움직이지만 역할이 다릅니다.
특히 HPA가 사용하는 지표와 VPA가 조정하는 request/limit의 관계를 무시하면 예기치 않은 상호작용이 생길 수 있습니다.
따라서 어떤 워크로드를 VPA 허용 대상으로 둘지, 어떤 워크로드는 HPA 중심으로 둘지를 정책으로 나누는 편이 좋습니다.

이 분류는 autoscaling 설계에서 자주 뒤로 밀리지만, 실제로는 비용과 안정성에 큰 영향을 줍니다.

### HPA와 CA 상태는 각자 다른 표면에서 점검해야 합니다

HPA는 Kubernetes 객체 표면에서 직접 확인하기 쉽습니다.
반면 CA는 로그와 node 변화, node pool 상태를 함께 봐야 합니다.
둘을 같은 표면에서 찾으려 하면 오히려 더 헷갈립니다.

```bash
kubectl get hpa -A
kubectl describe hpa my-app -n my-ns | tail -30

kubectl -n kube-system logs -l component=cluster-autoscaler --tail=80
kubectl get nodes -L agentpool,kubernetes.azure.com/scalesetpriority
```

## 흔히 헷갈리는 지점

## HPA 동작을 manifest와 출력으로 고정하기

autoscaling 논의가 추상적으로 흐르지 않으려면 HPA 객체 자체를 명확히 보여 주는 편이 좋습니다.
아래 예시는 CPU와 메모리를 함께 보는 기본 패턴입니다.

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: checkout-api
  namespace: prod
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: checkout-api
  minReplicas: 3
  maxReplicas: 30
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 65
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 70
```

상태 확인:

```bash
kubectl get hpa checkout-api -n prod
kubectl describe hpa checkout-api -n prod | tail -40
```

예시 출력:

```text
NAME           REFERENCE                 TARGETS          MINPODS   MAXPODS   REPLICAS   AGE
checkout-api   Deployment/checkout-api   78%/65%,72%/70% 3         30        12         9d
```

이 출력은 HPA가 이미 scale-up 판단을 내렸음을 보여 줍니다.
이후 Pending이 남아 있다면 문제는 scheduler 또는 node capacity 경계일 가능성이 높습니다.

## Cluster Autoscaler 프로필을 의도적으로 설정하기

AKS에서 CA는 관리형이지만 동작 성향은 프로필로 조정할 수 있습니다.
기본값이 보수적이므로 burst 특성이 강한 서비스는 값 조정 근거를 명시해야 합니다.

```bash
az aks update \
  --resource-group my-rg \
  --name my-cluster \
  --cluster-autoscaler-profile scan-interval=10s \
    scale-down-unneeded-time=15m \
    scale-down-delay-after-add=15m \
    max-node-provision-time=20m
```

확인:

```bash
az aks show -g my-rg -n my-cluster --query "autoScalerProfile" -o yaml
```

핵심은 빠른 scale-up 요구와 안정적 scale-down 요구를 동시에 만족하는 균형점입니다.

## HPA-CA race window를 시각화해서 팀 공통 언어 만들기

같은 현상을 사람마다 다르게 부르면 대응이 느려집니다.
아래 다이어그램처럼 타임라인을 공유하면 on-call 커뮤니케이션이 빨라집니다.

```mermaid
flowchart LR
  A["Load Spike"] --> B["HPA Scale Up"]
  B --> C["New Pods Pending"]
  C --> D["CA Detects Unschedulable Pods"]
  D --> E["Node Provisioning"]
  E --> F["Pods Scheduled and Ready"]
```

이 흐름을 팀 런북에 그대로 넣어 두면 “현재 C 단계인지 D 단계인지”를 빠르게 맞출 수 있습니다.

## 워크로드 보호를 위한 PDB와 선제 용량

autoscaling만으로 모든 급증을 흡수하려 하면 대기 구간이 길어질 수 있습니다.
핵심 API에는 baseline replica와 PDB를 함께 두어 “최소 서비스 용량”을 보장하는 편이 안전합니다.

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: checkout-api-pdb
  namespace: prod
spec:
  minAvailable: 4
  selector:
    matchLabels:
      app: checkout-api
```

그리고 node pool에도 `min-count`를 충분히 둡니다.
이 설계는 비용을 약간 늘리지만 급격한 트래픽 변동에서 사용자 체감 지연을 줄이는 데 효과적입니다.

## Prometheus/Grafana로 두 루프를 한 화면에서 보기

HPA와 CA를 각자 다른 대시보드에서만 보면 상관관계가 안 보입니다.
아래 구성처럼 한 화면에서 나란히 보는 편이 좋습니다.

- HPA current/desired replicas
- Pending Pod 수
- Node 개수와 NotReady 노드 수
- 요청 지연 시간 p95/p99

Grafana 패널을 `HPA desired`, `Pending`, `Node count`, `Latency p95`로 고정하면 race window가 애플리케이션 지연으로 번지는 순간을 즉시 파악할 수 있습니다.

## 트러블슈팅 시나리오: HPA는 올랐는데 응답 지연이 계속 증가하는 경우

아래 순서를 따라가면 대부분의 원인을 1차 분리할 수 있습니다.

1) `kubectl describe hpa`에서 이미 scale-up 판단이 있었는지 확인
2) Pending Pod가 증가하는지 확인
3) CA 이벤트 또는 node 증가 여부 확인
4) 새 노드 Ready 이후에도 지연이 지속되면 애플리케이션 콜드 스타트/DB 병목 확인

명령 예시:

```bash
kubectl get hpa -n prod
kubectl get pods -n prod --field-selector=status.phase=Pending
kubectl get nodes -L agentpool
kubectl get events -A --sort-by=.lastTimestamp | tail -30
```

이 순서는 “autoscaling이 느리다”라는 막연한 불만을 실행 가능한 진단 단계로 바꾸는 최소 절차입니다.

- **HPA와 Cluster Autoscaler는 같은 일을 하지 않습니다.** 하나는 replica를, 다른 하나는 node를 조정합니다.
- **HPA가 scale-up을 결정했다고 곧바로 Ready Pod가 늘어나는 것은 아닙니다.** 빈 node 자원이 없으면 Pending 단계가 먼저 보입니다.
- **CA는 메트릭 비율을 직접 계산하지 않습니다.** unschedulable Pod와 template node 시뮬레이션이 핵심입니다.
- **scale-down이 느린 것은 무능이 아니라 의도된 보수성일 수 있습니다.** 비용보다 안정성을 우선한 기본값이 많습니다.
- **autoscaling 문제를 하나의 튜닝 파라미터로 해결하려고 하면 안 됩니다.** HPA 임계치, node pool 전략, baseline capacity를 함께 봐야 합니다.

## 운영 체크리스트

## node pool 스케일 정책을 워크로드 클래스별로 분리하기

CA가 하나의 pool만 보고 있다고 가정하면 실제 클러스터와 맞지 않습니다.
대부분의 AKS 운영 환경은 system pool, 일반 API pool, batch/spot pool을 함께 사용합니다.
따라서 autoscaling 정책도 pool별로 분리해 설계해야 합니다.

예시 전략:

- system pool: 고정 최소 노드, CA 비활성 또는 매우 보수적
- api pool: 빠른 scale-up, 느린 scale-down
- batch/spot pool: 공격적 scale-up, 실패 허용 범위 명시

AKS 명령 예시:

```bash
az aks nodepool update -g my-rg --cluster-name my-cluster -n apipool --enable-cluster-autoscaler --min-count 3 --max-count 30
az aks nodepool update -g my-rg --cluster-name my-cluster -n batchpool --enable-cluster-autoscaler --min-count 0 --max-count 50
```

이 분리는 비용 최적화뿐 아니라 장애 격리에도 중요합니다.
batch 폭증이 API 응답 경로에 직접 영향 주는 상황을 줄일 수 있기 때문입니다.

## 관측 경보 기준을 루프별로 나누기

autoscaling 경보를 하나로 묶으면 원인 구분이 늦습니다.
아래처럼 HPA/CA 각각에 경보를 두는 편이 좋습니다.

- HPA desired replicas 급증 + current replicas 미추종
- Pending Pod 지속 시간 임계치 초과
- node provisioning 시간 임계치 초과
- scale-down 이후 10분 내 재확장 반복(출렁임 신호)

이 기준을 적용하면 “확장 자체가 실패한 것”과 “확장은 성공했지만 지연이 긴 것”을 운영 알림 단계에서 이미 분리할 수 있습니다.

- [ ] 각 워크로드의 HPA 메트릭과 임계치 선택 근거를 ADR로 남겼습니다.
- [ ] CA의 scale-down 관련 지연 값을 비용과 지연 요구사항에 맞게 검토했습니다.
- [ ] HPA가 먼저 Pod를 늘리고 CA가 뒤따르는 race 시나리오를 부하 테스트로 확인했습니다.
- [ ] spot node pool을 쓴다면 drain 정책과 우선순위 정책을 함께 정리했습니다.
- [ ] VPA 허용 워크로드와 금지 워크로드를 명시적으로 분류했습니다.

## 부하 테스트에서 꼭 재현해야 하는 두 가지 패턴

autoscaling 정책 검증은 평균 부하보다 급격한 변화 패턴에서 의미가 큽니다.
최소한 아래 두 시나리오는 정기적으로 재현하는 편이 좋습니다.

1) 2분 이내 급격한 scale-up이 필요한 burst 트래픽
2) 30분 이상 완만한 감소 후 scale-down 안정성 확인

각 테스트에서 기록할 항목은 동일합니다.
HPA desired/current, Pending Pod 지속 시간, 새 노드 Ready 시간, 그리고 사용자 응답 지연 p95입니다.
이 데이터를 쌓아 두면 임계치 조정이 감각이 아니라 근거 기반 결정으로 바뀝니다.
특히 동일 부하 프로파일을 분기마다 반복 실행하면, 클러스터 버전 업그레이드 후 autoscaling 거동이 어떻게 달라졌는지도 안정적으로 비교할 수 있습니다.

AKS autoscaling을 정확히 이해하려면 먼저 HPA와 Cluster Autoscaler를 분리해야 합니다.
HPA는 메트릭을 읽고 replica 수를 조정하는 빠른 루프이고, Cluster Autoscaler는 unschedulable Pod를 보고 node 수를 조정하는 느리고 보수적인 루프입니다.
둘은 같은 umbrella 아래 있지만 서로 다른 질문에 답합니다.

이 글에서 가장 중요한 운영 감각은 race window가 정상적이라는 사실입니다.
HPA가 먼저 움직이고, scheduler가 빈자리를 못 찾고, CA가 나중에 node를 더하는 동안 Pending Pod가 잠시 남을 수 있습니다.
따라서 autoscaling 문제를 볼 때는 어떤 루프가 지금 움직였고 어떤 루프가 아직 따라오지 않았는지를 먼저 구분해야 합니다.

다음 글에서는 HPA 위에 올라타는 KEDA를 봅니다.
이번 글에서 HPA와 CA를 분리해 두었기 때문에, 마지막 글에서는 KEDA가 external metric과 0↔1 경계를 어떻게 맡는지 더 정확하게 읽을 수 있습니다.

## 정리

## 처음 질문으로 돌아가기

- **HPA는 어떤 메트릭을 어떤 주기로 읽고 desired replica를 계산할까요?**
  - 본문 기준으로 HPA는 기본 15초 sync period에서 CPU·메모리 같은 메트릭을 읽고, `desiredReplicas = ceil(currentReplicas * (currentMetric / targetMetric))`에 가까운 비율 계산으로 replica 수를 정합니다. 실제 구현에서는 tolerance, missing metric, stabilization window가 더해지지만, 운영 감각으로는 “메트릭 비율을 replica 수로 바꾸는 빠른 루프”로 보면 됩니다. 그래서 부하가 오르면 node 증설보다 먼저 replica 증가 결정이 보이기 쉽습니다.
- **Cluster Autoscaler는 어떤 신호를 보고 “새 노드가 필요하다”고 판단할까요?**
  - Cluster Autoscaler는 HPA처럼 메트릭 비율을 직접 읽지 않고, scheduler가 배치하지 못한 unschedulable Pod를 핵심 입력으로 봅니다. 그리고 각 node pool의 template node를 기준으로 binpacking estimator를 돌려 “새 node가 생기면 이 Pod들이 실제로 올라갈 수 있는가”를 판단한 뒤 node 수 조정을 요청합니다. 본문이 CA를 느리고 보수적인 루프로 설명한 이유가 바로 이 중간 시뮬레이션과 provisioning 대기 시간 때문입니다.
- **HPA와 Cluster Autoscaler가 동시에 움직일 때 race window는 왜 생길까요?**
  - race window는 HPA와 CA가 서로 다른 입력과 시간축으로 움직이기 때문에 생깁니다. HPA가 먼저 replica를 늘리고, 빈 node 자원이 없으면 scheduler가 새 Pod를 Pending으로 남기고, 그 뒤에야 CA가 그 unschedulable Pod를 보고 node provisioning을 시작합니다. 따라서 잠시 Pending Pod가 늘어나는 구간은 설계 버그라기보다 두 제어 루프가 순차적으로 만나는 정상적인 중간 상태입니다.

<!-- toc:begin -->
## 시리즈 목차

- [Azure Kubernetes Service Deep Dive (1/6): Control Plane 해부 — AKS가 사용자에게서 가린 것](./01-control-plane-anatomy.md)
- [Azure Kubernetes Service Deep Dive (2/6): kubelet과 containerd — 노드 위에서 컨테이너가 뜨기까지](./02-kubelet-and-containerd.md)
- [Azure Kubernetes Service Deep Dive (3/6): CNI와 Azure CNI Overlay — Pod IP가 어디서 오는가](./03-cni-and-azure-cni-overlay.md)
- [Azure Kubernetes Service Deep Dive (4/6): Scheduler와 Pod 배치 — 어느 노드로 갈지 누가 정하는가](./04-scheduler-and-pod-placement.md)
- **Azure Kubernetes Service Deep Dive (5/6): HPA와 Cluster Autoscaler 내부 — 두 컨트롤 루프 (현재 글)**
- Azure Kubernetes Service Deep Dive (6/6): KEDA 내부 — ScaledObject가 HPA를 만드는 방식 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [Use the cluster autoscaler in AKS](https://learn.microsoft.com/en-us/azure/aks/cluster-autoscaler)
- [Horizontal Pod Autoscaling](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)

### 업스트림 코드
- [`horizontal.go` @ `v1.30.0`](https://github.com/kubernetes/kubernetes/blob/v1.30.0/pkg/controller/podautoscaler/horizontal.go)
- [`replica_calculator.go` @ `v1.30.0`](https://github.com/kubernetes/kubernetes/blob/v1.30.0/pkg/controller/podautoscaler/replica_calculator.go)
- [`hpacontroller.go` @ `v1.30.0`](https://github.com/kubernetes/kubernetes/blob/v1.30.0/cmd/kube-controller-manager/app/options/hpacontroller.go)
- [`static_autoscaler.go` @ `cluster-autoscaler-1.30.0`](https://github.com/kubernetes/autoscaler/blob/cluster-autoscaler-1.30.0/cluster-autoscaler/core/static_autoscaler.go)
- [`orchestrator.go` @ `cluster-autoscaler-1.30.0`](https://github.com/kubernetes/autoscaler/blob/cluster-autoscaler-1.30.0/cluster-autoscaler/core/scaleup/orchestrator/orchestrator.go)
- [`binpacking_estimator.go` @ `cluster-autoscaler-1.30.0`](https://github.com/kubernetes/autoscaler/blob/cluster-autoscaler-1.30.0/cluster-autoscaler/estimator/binpacking_estimator.go)

### 관련 시리즈
- [Azure AKS 101](../../azure-aks-101/ko/)
- [Azure Functions Deep Dive 5화 — 스케일링 내부](../../azure-functions-deep-dive/ko/05-scaling-internals.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-aks-deep-dive/ko/05-hpa-and-cluster-autoscaler-internals)

Tags: AKS, Kubernetes, Distributed Systems, Containers
