# Scaling — HPA, Cluster Autoscaler, KEDA

> Azure Kubernetes Service 101 series (6/7)

Scaling in AKS gets confusing because the word “scale” points at more than one layer. Scaling pods and scaling nodes are not the same thing. Add event-driven scaling on top, and HPA, Cluster Autoscaler, and KEDA can start to look like overlapping tools.

They are related, but they are not the same. This post separates them by input signal, control target, and operating layer.

---

## One diagram first

![One diagram first](../../assets/azure-aks-101/06/06-01-one-diagram-first.en.png)
That is the whole relationship.

- HPA changes **pod count**.
- Cluster Autoscaler changes **node count**.
- KEDA extends pod autoscaling by feeding external-event signals into the HPA path.

The biggest misconception to remove early is this one: **KEDA does not replace HPA. It sits on top of it.**

---

## HPA — automatically change pod count

HPA stands for Horizontal Pod Autoscaler.

- target is usually a Deployment
- signal comes from CPU, memory, or custom metrics
- outcome is a replica-count change

HPA answers a very specific question: how many instances of this workload should be running right now?

### What HPA depends on

HPA is a feedback loop. That means its input quality matters.

- metrics-server must be available for the standard metrics path
- CPU requests should be meaningful
- readiness behavior should reflect when a pod can truly receive traffic

If the input signal is bad, autoscaling decisions get noisy or misleading.

---

## The HPA loop

![The HPA loop](../../assets/azure-aks-101/06/06-02-the-hpa-loop.en.png)
Suppose a FastAPI API is running with two pods and the target CPU utilization is 60%. If the average keeps sitting around 90%, HPA will try to raise the replica count.

But that is not the end of the story. If no nodes have room for the new pods, those pods go Pending. That is where Cluster Autoscaler enters.

---

## Cluster Autoscaler — automatically change node count

Cluster Autoscaler works one layer lower.

- if new pods cannot be scheduled, it can add nodes
- if nodes stay underused for long enough, it can remove nodes

The crucial sentence is this one:

> Cluster Autoscaler does not scale pods. It scales node pools when there is not enough capacity to place pods.

That makes HPA and Cluster Autoscaler complementary, not competing.

---

## HPA and Cluster Autoscaler together

![HPA and Cluster Autoscaler together](../../assets/azure-aks-101/06/06-03-hpa-and-cluster-autoscaler-together.en.png)
This explains a very common operational moment: pod count increases, but response quality does not improve immediately because the new pods still need actual node capacity.

---

## KEDA — event-driven autoscaling on top of HPA

KEDA stands for Kubernetes Event-driven Autoscaling.

It is useful when the best scaling signal is not CPU or memory but an external event source, such as:

- Azure Service Bus queue depth
- Event Hub lag
- cron-based schedules
- Kafka or RabbitMQ backlog

KEDA introduces two critical components.

- the **KEDA operator**, which reads `ScaledObject` definitions
- the **KEDA metrics server**, which exposes external metrics into the autoscaling path

That is why the most accurate short description is: KEDA translates external event pressure into the HPA model.

---

## KEDA sits on top of HPA

![KEDA sits on top of HPA](../../assets/azure-aks-101/06/06-04-keda-sits-on-top-of-hpa.en.png)
This relationship is worth being exact about.

- HPA is the pod autoscaling mechanism.
- KEDA extends the set of signals that can drive that mechanism.
- KEDA-managed workloads usually still scale by way of HPA behavior underneath.

That is also why you generally should not attach your own separate HPA to the same workload that KEDA is already scaling.

---

## Which tool fits which workload?

### HPA is a good fit when

- request load maps reasonably well to CPU or memory
- custom application metrics exist and reflect real pressure

### Cluster Autoscaler is needed when

- HPA can create pods faster than the cluster can place them
- you want node capacity to expand and contract with demand

### KEDA is a good fit when

- queue depth or lag is the real demand signal
- scale-to-zero matters
- workloads are event-driven or batch-heavy

---

## Read it through a FastAPI lens

For an HTTP-serving FastAPI API, HPA is usually the first place to look.

- target CPU utilization
- minimum and maximum replicas

For a FastAPI worker consuming Service Bus messages, KEDA is often a better fit.

- no messages means replica count can fall to zero
- backlog growth drives replicas back up

So the question is not “which autoscaler is best?” The question is “what signal best represents demand for this workload?”

---

## A minimal HPA example

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

This uses average CPU utilization to change the Deployment replica count.

---

## A minimal KEDA example

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

Here the queue depth becomes the pressure signal. KEDA translates that into autoscaling behavior by way of the HPA path.

---

## Three common misconceptions

### “`kubectl scale` is basically HPA”

No. `kubectl scale` is a manual replica-count change. HPA is an automated metrics-driven control loop.

### “Cluster Autoscaler scales pods”

No. It scales nodes.

### “KEDA replaces HPA”

No. KEDA extends autoscaling by feeding event-driven signals into the HPA mechanism.

---

## Scaling is also a cost story

Autoscaling is not only about elasticity. It is also a billing story.

- HPA affects application responsiveness and pod density
- Cluster Autoscaler affects VM count directly
- KEDA can save substantial money on event-driven workloads by allowing scale-to-zero

That is why a good scaling design starts with signal selection, not with “turn every autoscaler on.”

---

## The metrics you usually want nearby

- CPU and memory utilization
- pod Pending count
- node utilization
- HPA current vs desired replicas
- queue depth or lag

Those signals live at different layers. Looking at CPU alone can hide a node-capacity problem. Looking at queue depth alone can hide a readiness or throughput problem.

---

## What the next post adds

Once you have multiple scaling layers reacting to traffic and events, observability becomes the next requirement. You need to see whether HPA is working, whether nodes are saturating, whether restarts are climbing, and whether backlog is actually falling.

That takes us to part 7: Container Insights, logs, kube-state-metrics, and alerts.

---

This is part 6 of the Azure Kubernetes Service 101 series. Up to this point, the series focused on cluster shape, workload objects, and traffic flow. This post added the feedback loops that change capacity over time. Part 7 closes the series by showing how to observe and operate those loops in a real AKS environment.

---

## References

### Official Docs
- [Scaling options for applications in AKS](https://learn.microsoft.com/en-us/azure/aks/concepts-scale)
- [Cluster autoscaler on AKS](https://learn.microsoft.com/en-us/azure/aks/cluster-autoscaler)
- [Kubernetes Event-driven Autoscaling (KEDA)](https://learn.microsoft.com/en-us/azure/aks/keda-about)
- [Autoscale pods in AKS](https://learn.microsoft.com/en-us/azure/aks/tutorial-kubernetes-scale#autoscale-pods)

### Related Series
- [Azure App Service 101](../../azure-app-service-101/en/07-scaling-101.md) — useful when comparing instance scaling with Kubernetes pod and node scaling
- [Azure Functions 101](../../azure-functions-101/en/06-scaling-and-cold-start.md) — useful when comparing orchestrated scaling with serverless scaling
