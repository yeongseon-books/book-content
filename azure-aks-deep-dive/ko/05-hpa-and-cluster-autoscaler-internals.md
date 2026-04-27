# HPA와 Cluster Autoscaler 내부 — 두 컨트롤 루프

> Azure Kubernetes Service Deep Dive 시리즈 (5/6)

HPA는 replica 수를 바꾸고,
Cluster Autoscaler는 node 수를 바꿉니다.
둘은 같은 autoscaling 아래에 있지만 서로를 대체하지 않습니다.
HPA는 `kube-controller-manager` 안에서 메트릭을 읽고 desired replica를 계산합니다.
Cluster Autoscaler는 별도 Deployment로 떠서 unschedulable Pod를 보고 node pool 확장을 시뮬레이션합니다.

---

## 두 루프를 한 그림으로 보기

![두 루프를 한 그림으로 보기](../../assets/azure-aks-deep-dive/05/05-01-put-both-loops-in-one-diagram.ko.png)
---

## HPA의 핵심

기본 sync period는 15초입니다.
대표적인 계산 모델은 `desiredReplicas = ceil(currentReplicas * (currentMetric / targetMetric))`입니다.
실제 코드는 tolerance,
missing metrics,
stabilization window를 더 고려합니다.

![HPA의 핵심](../../assets/azure-aks-deep-dive/05/05-02-the-hpa-side.ko.png)
---

## CA의 핵심

CA는 unschedulable Pod를 보고,
각 node pool의 template node를 기준으로 binpacking estimator를 돌립니다.
새 노드가 생기면 scheduler가 이 Pod를 배치할 수 있을지 먼저 시뮬레이션한 뒤,
가장 적절한 pool을 선택해 node 수를 늘립니다.

![CA의 핵심](../../assets/azure-aks-deep-dive/05/05-03-the-ca-side.ko.png)
---

## 이번 화의 요점

> HPA는 기본 15초 주기로 메트릭을 읽고 replica 수를 조정하는 ratio controller입니다. Cluster Autoscaler는 별도 컴포넌트로서 unschedulable Pod를 보고 각 node pool에 대해 "새 노드가 생기면 스케줄 가능한가"를 시뮬레이션한 뒤 node 수를 조정합니다. HPA는 pod를 늘리고, CA는 node를 늘립니다.

---

## 시리즈 안에서의 위치

이 글은 Azure Kubernetes Service Deep Dive 시리즈 5화입니다.
4화가 scheduler의 배치 결정을 다뤘다면 이번 화는 그 결과를 보고 반응하는 두 control loop를 설명합니다. 다음 6화에서는 KEDA가 이 HPA 위에 어떻게 올라타는지 봅니다.

---

## 참고 자료

### 1차 출처
- [`horizontal.go` @ `v1.30.0`](https://github.com/kubernetes/kubernetes/blob/v1.30.0/pkg/controller/podautoscaler/horizontal.go)
- [`replica_calculator.go` @ `v1.30.0`](https://github.com/kubernetes/kubernetes/blob/v1.30.0/pkg/controller/podautoscaler/replica_calculator.go)
- [`hpacontroller.go` @ `v1.30.0`](https://github.com/kubernetes/kubernetes/blob/v1.30.0/cmd/kube-controller-manager/app/options/hpacontroller.go)
- [`static_autoscaler.go` @ `cluster-autoscaler-1.30.0`](https://github.com/kubernetes/autoscaler/blob/cluster-autoscaler-1.30.0/cluster-autoscaler/core/static_autoscaler.go)
- [`orchestrator.go` @ `cluster-autoscaler-1.30.0`](https://github.com/kubernetes/autoscaler/blob/cluster-autoscaler-1.30.0/cluster-autoscaler/core/scaleup/orchestrator/orchestrator.go)
- [`binpacking_estimator.go` @ `cluster-autoscaler-1.30.0`](https://github.com/kubernetes/autoscaler/blob/cluster-autoscaler-1.30.0/cluster-autoscaler/estimator/binpacking_estimator.go)

### 2차 출처
- [Use the cluster autoscaler in AKS](https://learn.microsoft.com/en-us/azure/aks/cluster-autoscaler)
- [Horizontal Pod Autoscaling](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)

### 관련 시리즈
- [Azure AKS 101](../../azure-aks-101/ko/)
- [Azure Functions Deep Dive 5화 — scaling internals](../../azure-functions-deep-dive/ko/05-scaling-internals.md)
