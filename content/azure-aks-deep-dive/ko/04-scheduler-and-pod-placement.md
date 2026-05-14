---
title: Scheduler와 Pod 배치 — 어느 노드로 갈지 누가 정하는가
series: azure-aks-deep-dive
episode: 4
language: ko
status: publish-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- AKS
- Kubernetes
- Distributed Systems
- Containers
last_reviewed: '2026-05-12'
seo_description: Kubernetes 스케줄러가 Pod를 배치하는 3단계 과정과 메커니즘을 분석하여 배치 실패 원인을 정확히 진단하는 방법을 제시합니다.
---

# Scheduler와 Pod 배치 — 어느 노드로 갈지 누가 정하는가

Pending Pod를 보면 많은 팀이 가장 먼저 노드 상태나 container runtime 로그부터 떠올립니다.
하지만 실제로는 그보다 더 앞단의 결정이 먼저 끝나야 합니다.
kube-scheduler가 제약 조건을 계산해 가능한 후보를 좁히고, 최종 Binding을 기록해야만 node-local 실행 경로가 시작될 수 있기 때문입니다.

스케줄링이 어려운 이유는 이것이 단순한 잔여 CPU 계산이 아니기 때문입니다.
node affinity, taint와 toleration, topology spread, 볼륨 제약, 포트 충돌, 우선순위와 preemption이 모두 같은 판단 안으로 들어옵니다.
따라서 Pending이라는 동일한 결과 뒤에는 완전히 다른 배치 실패 이유가 숨어 있을 수 있습니다.

이 글은 Azure AKS Deep Dive 시리즈의 네 번째 글입니다.

이번 글의 목적은 scheduler를 “Pod를 실행하는 컴포넌트”가 아니라 “노드 선택과 Binding 기록을 담당하는 control-plane 루프”로 다시 읽는 것입니다.
이 관점이 잡혀야 Pending Pod를 placement 실패, binding 시점 실패, node-local 실행 지연으로 정확히 나눠 볼 수 있습니다.
이제 kube-scheduler가 어떤 순서로 후보를 줄이고 결정을 남기는지 따라가 보겠습니다.

## 이 글에서 다룰 문제

- kube-scheduler는 하나의 Pod에 대해 어떤 단계로 노드 후보를 좁혀 갈까요?
- `nodeSelector`, affinity, taint/toleration, topology spread는 서로 어떤 다른 의도를 표현할까요?
- Filter에서 모두 탈락한 경우와 feasible node는 있었지만 Binding이 실패한 경우는 어떻게 구분할까요?
- PriorityClass와 preemption은 왜 강력하지만 조심해서 써야 할까요?
- stateless와 stateful 워크로드의 배치 정책은 어떤 지점에서 달라져야 할까요?

## 왜 이 글이 중요한가

스케줄링을 이해하지 못하면 Pending Pod의 원인을 뒤쪽 계층으로 너무 빨리 밀어 버리게 됩니다.
예를 들어 kubelet 로그를 열심히 뒤져도, 애초에 Pod가 어느 노드에도 배정되지 않았다면 답이 나오지 않습니다.
배치 실패를 실행 실패로 오해하는 순간 진단 시간은 길어지고, 원인은 더 늦게 보이게 됩니다.

또한 scheduler는 클러스터 정책의 집약 지점입니다.
조직이 어떤 워크로드를 어느 zone에 두고 싶은지, 어떤 노드를 spot 전용으로 쓰고 싶은지, 어떤 서비스는 같은 호스트에 몰리지 않게 하고 싶은지가 모두 이 단계의 제약 조건으로 표현됩니다.
따라서 placement 정책이 흐리면 비용, 가용성, 성능이 동시에 흔들리기 쉽습니다.

마지막으로 이 글은 autoscaling 이해에도 직접 연결됩니다.
HPA가 replica를 늘려도 scheduler가 배치할 수 없으면 Pod는 Pending으로 남습니다.
그 상태를 Cluster Autoscaler가 보고 노드를 늘리는 것이 5화의 핵심이므로, 먼저 placement 자체를 분리해서 이해하는 편이 훨씬 실용적입니다.

## scheduler를 이해하는 가장 좋은 방법: 불가능한 후보를 지우고 가능한 후보를 순위화한 뒤 Binding만 기록한다고 보는 것입니다

이 경로에서 가장 중요한 문장은 이것입니다.
**kube-scheduler는 Pod를 실행하지 않습니다. 불가능한 노드를 제거하고, 가능한 노드를 순위화하고, 선택 결과를 Binding으로 기록합니다.**
이 한 줄이 스케줄링을 실행 경로와 분리해 줍니다.

이 관점이 중요한 이유는 Pending Pod 진단의 첫 분기점이 여기서 생기기 때문입니다.
feasible node가 아예 없었던 것인지, 후보는 있었지만 Bind 단계에서 드물게 실패한 것인지, 아니면 Binding 이후에 kubelet 쪽 실행이 느린 것인지에 따라 다음 행동이 완전히 달라집니다.

즉 scheduler를 잘 이해한다는 말은 모든 plugin 이름을 외운다는 뜻이 아닙니다.
오히려 Filter, Score, Binding이라는 세 단계를 기준으로 증상을 어디에 붙일지 빠르게 결정하는 능력에 더 가깝습니다.

> Pending Pod를 볼 때 가장 먼저 물어야 할 질문은 “실행이 늦는가”가 아니라 “scheduler가 이 Pod에 대해 feasible node를 하나라도 남겼는가”입니다.

## 핵심 개념

### 스케줄링은 세 단계로 읽는 편이 가장 정확합니다

아래 그림은 scheduler를 이해할 때 가장 중요한 기준점입니다.
Pod가 queue에 들어오고, 후보 노드를 걸러 내고, 점수를 매기고, Binding을 기록하는 흐름이 한 장에 들어 있습니다.
이 경로를 눈에 익혀 두면 Pending Pod를 볼 때도 훨씬 덜 막막합니다.

![대기 Pod가 Binding까지 가는 스케줄링 단계](../../../assets/azure-aks-deep-dive/04/04-01-the-three-steps.ko.png)

*대기 Pod가 Binding까지 가는 스케줄링 단계*

핵심은 scheduler의 출력이 “실행 중인 Pod”가 아니라 `Pod -> Node` 결정이라는 사실입니다.
따라서 스케줄링 단계와 노드 실행 단계는 반드시 분리해서 읽어야 합니다.

### `ScheduleOne()`은 scheduling cycle과 binding cycle을 나눕니다

upstream `ScheduleOne()`은 구조를 꽤 정직하게 보여 줍니다.
먼저 scheduling cycle에서 가능한 후보를 찾고, 이후 binding cycle에서 선택 결과를 API server에 기록합니다.
이 분리가 있어야 selection과 commitment를 별개 단계로 볼 수 있습니다.

운영에서는 이 구분이 생각보다 중요합니다.
후보를 찾는 데 실패한 것과, 후보는 있었지만 결과를 기록하는 과정에서 문제가 생긴 것은 대응 대상이 다르기 때문입니다.

### Filter는 “안 되는 노드”를 제거합니다

Filter 단계는 불가능한 노드를 제거합니다.
리소스 부족, node affinity 불일치, taint 미허용, topology 제약, volume 관련 조건 등이 여기서 많이 걸립니다.
즉 Filter를 통과하지 못한 노드는 점수 경쟁에 들어오지도 못합니다.

이 단계의 의미를 잘 잡아야 `0/10 nodes are available` 같은 메시지를 읽을 수 있습니다.
이 메시지는 대개 실행 실패가 아니라 placement 실패를 말하고 있기 때문입니다.

### Score는 “가능한 노드 중 더 나은 후보”를 고릅니다

Filter를 통과한 뒤에는 Score가 남은 후보를 순위화합니다.
기본 plugin 집합에는 `NodeResourcesFit`, `NodeAffinity`, `PodTopologySpread`, `InterPodAffinity` 같은 이름이 보입니다.
즉 scheduler는 단순히 제약을 만족하는지만 보는 것이 아니라, 그중 더 좋은 배치 후보를 계산합니다.

![후보 노드를 거르고 점수화하는 배치 경로](../../../assets/azure-aks-deep-dive/04/04-02-filter-and-score.ko.png)

*후보 노드를 거르고 점수화하는 배치 경로*

운영 감각으로 바꾸면 이렇습니다.
Filter는 “실행 가능성”의 질문이고, Score는 “그중 어디가 더 적절한가”의 질문입니다.
두 단계를 섞어 생각하면 placement 정책이 왜 그렇게 나왔는지 설명하기 어려워집니다.

### Binding은 선택 결과를 API server에 기록하는 단계입니다

binding cycle은 선택된 노드를 API server에 기록합니다.
이 write가 끝나야 비로소 선택된 노드의 kubelet이 Pod를 보고 후속 실행 경로를 시작할 수 있습니다.
즉 scheduler는 실행을 직접 담당하지 않으며, 실행의 전제 조건인 배치 결정을 남기는 쪽에 가깝습니다.

이 사실을 기억하면 Pending Pod를 읽는 문장이 더 정밀해집니다.
“아직 배치 결정이 없다”와 “배치 결정은 끝났는데 노드 실행이 늦다”는 완전히 다른 상태입니다.

### placement 정책은 CPU 여유보다 훨씬 넓은 의미를 가집니다

많은 팀이 스케줄링을 남는 CPU, 메모리 계산 정도로만 생각합니다.
하지만 실제로는 조직의 운영 정책이 이 단계에 녹아 있습니다.
예를 들어 zone spread를 강하게 요구할지, spot node에만 갈 수 있게 할지, stateful workload를 특정 zone에 묶을지, anti-affinity로 분산할지가 모두 placement 정책입니다.

즉 scheduler는 자원 배분기이면서 동시에 정책 집행기입니다.
이 점을 놓치면 왜 어떤 Pod가 특정 노드에 절대 가지 못하는지, 왜 분산이 의도대로 안 되는지 설명하기 어렵습니다.

### PriorityClass와 preemption은 강력하지만 부작용 비용도 큽니다

우선순위 정책은 중요한 워크로드를 살리는 데 유용합니다.
하지만 preemption은 결국 다른 Pod에게 비용을 전가하는 선택입니다.
따라서 “중요한 서비스이니 우선순위를 높이자”는 판단은 단독으로 끝나면 안 되고, 누가 밀려날지와 어떤 SLO를 보호할지를 함께 봐야 합니다.

특히 multi-tenant 클러스터에서는 PriorityClass 남용이 조용한 갈등을 만듭니다.
높은 우선순위는 강한 권한이므로 소유자와 정책 근거를 명확히 두는 편이 좋습니다.

### stateful workload는 zone과 volume 제약을 함께 봐야 합니다

stateless workload는 비교적 유연하게 분산할 수 있습니다.
반면 stateful workload는 PVC와 zone 제약이 함께 걸리므로 placement 정책이 훨씬 민감합니다.
노드는 있는데 volume이 같은 zone에 없어 배치가 안 되는 상황은 생각보다 자주 나옵니다.

따라서 stateful workload의 배치 정책은 node affinity만이 아니라 storage topology까지 함께 설계해야 합니다.
이 점을 놓치면 autoscaling이 충분해 보여도 실제로는 Pod가 계속 Pending에 머무를 수 있습니다.

### Pending Pod 진단은 이벤트와 노드 라벨부터 보는 편이 실용적입니다

스케줄링 문제는 무작정 로그를 많이 보는 것보다 placement 신호를 먼저 읽는 편이 효율적입니다.
Pending Pod 목록, `describe` 이벤트, 최근 이벤트 스트림, zone과 agentpool 라벨이 붙은 노드 목록을 함께 보면 실패 이유가 빠르게 좁혀집니다.
이 순서는 운영 런북의 기본 진단 템플릿으로 두기 좋습니다.

```bash
kubectl get pods -A --field-selector status.phase=Pending
kubectl describe pod my-pod -n my-ns | tail -30
kubectl get events --sort-by=.lastTimestamp -n my-ns | tail -20
kubectl get nodes -L topology.kubernetes.io/zone,agentpool
```

## 흔히 헷갈리는 지점

- **scheduler가 Pod를 직접 실행하는 것은 아닙니다.** scheduler의 출력은 `Pod -> Node` Binding입니다.
- **Pending은 곧바로 kubelet 문제를 뜻하지 않습니다.** feasible node가 없어서 placement 자체가 실패했을 수 있습니다.
- **Filter와 Score는 같은 단계가 아닙니다.** 하나는 가능 여부를, 다른 하나는 우선순위를 다룹니다.
- **PriorityClass는 공짜 성능 옵션이 아닙니다.** preemption 비용을 다른 워크로드가 부담할 수 있습니다.
- **stateful workload는 CPU 여유만으로 배치되지 않습니다.** zone과 volume 제약이 함께 따라옵니다.

## 운영 체크리스트

- [ ] 핵심 워크로드의 affinity/anti-affinity와 zone spread 정책을 명시했습니다.
- [ ] PriorityClass 사용 원칙과 preemption 허용 범위를 문서화했습니다.
- [ ] 모든 node taint와 toleration에 owner를 지정했습니다.
- [ ] Pending Pod 자동 진단 절차와 알림 기준을 마련했습니다.
- [ ] stateful workload의 PVC zone과 node zone 정합성을 사전에 검증했습니다.

## 정리

kube-scheduler는 Pod를 실행하는 컴포넌트가 아닙니다.
불가능한 노드를 Filter로 제거하고, 가능한 후보를 Score로 정렬하고, 마지막에 선택 결과를 Binding으로 기록하는 control-plane 루프입니다.
따라서 Pending Pod를 볼 때 가장 먼저 해야 할 일은 실행 지연과 placement 실패를 분리하는 것입니다.

이 글에서 가져가야 할 핵심은 세 가지입니다.
Scheduler의 출력은 실행이 아니라 배치 결정입니다.
Filter와 Score는 서로 다른 질문에 답합니다.
그리고 Priority, topology, volume 같은 제약은 placement를 단순한 자원 계산보다 훨씬 정책적인 문제로 만듭니다.

다음 글에서는 이 배치 결과를 입력으로 받아 움직이는 autoscaling 두 루프를 봅니다.
HPA가 replica를 늘리고, Cluster Autoscaler가 node를 늘릴 때 왜 race window가 생기는지 이어서 살펴보겠습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Control Plane 해부 — AKS가 사용자에게서 가린 것](./01-control-plane-anatomy.md)
- [kubelet과 containerd — 노드 위에서 컨테이너가 뜨기까지](./02-kubelet-and-containerd.md)
- [CNI와 Azure CNI Overlay — Pod IP가 어디서 오는가](./03-cni-and-azure-cni-overlay.md)
- **Scheduler와 Pod 배치 — 어느 노드로 갈지 누가 정하는가 (현재 글)**
- HPA와 Cluster Autoscaler 내부 — 두 컨트롤 루프 (예정)
- KEDA 내부 — ScaledObject가 HPA를 만드는 방식 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [Kubernetes scheduler](https://kubernetes.io/docs/concepts/scheduling-eviction/kube-scheduler/)
- [Assigning Pods to Nodes](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/)

### 업스트림 코드
- [`schedule_one.go` @ `v1.30.0`](https://github.com/kubernetes/kubernetes/blob/v1.30.0/pkg/scheduler/schedule_one.go)
- [`default_plugins.go` @ `v1.30.0`](https://github.com/kubernetes/kubernetes/blob/v1.30.0/pkg/scheduler/apis/config/v1/default_plugins.go)

### 관련 시리즈
- [Azure AKS 101](../../azure-aks-101/ko/)
- [Azure Functions Deep Dive 4화 — dispatcher와 invocation](../../azure-functions-deep-dive/ko/04-dispatcher-and-invocation.md)

Tags: AKS, Kubernetes, Distributed Systems, Containers
