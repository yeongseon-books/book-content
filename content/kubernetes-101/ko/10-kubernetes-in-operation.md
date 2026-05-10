---
series: kubernetes-101
episode: 10
title: 운영 관점의 Kubernetes
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Kubernetes
  - SRE
  - Observability
  - GitOps
  - DevOps
seo_description: Kubernetes 운영의 핵심인 probe, RBAC, 네트워크 정책, 관측성, 용량 산정, GitOps, 런북을 입문자 관점에서 정리한 글
last_reviewed: '2026-05-04'
---

# 운영 관점의 Kubernetes

> Kubernetes 101 시리즈 (10/10)


## 이 글에서 다룰 문제

*기능* 이 *돌아가는 것* 과 *야간* 에도 *문제 없이 돌아가는 것* 은 다릅니다. *운영성* 이 *서비스 신뢰* 입니다.

## 개념 한눈에 보기

```mermaid
flowchart LR
    Probe["probes"] --> App["application"]
    App --> Obs["metrics/logs/traces"]
    Obs --> SRE["sre runbooks"]
    SRE --> GitOps["gitops"]
```

## Before/After

**Before**: *수동 kubectl*, *log grep*, *추측 디버깅*.

**After**: *probe* + *대시보드* + *런북* 으로 *재현 가능한 대응*.

## 실습: 운영 기본기

### 1단계 — Probe 추가

```python
"""
livenessProbe:
  httpGet: {path: /healthz, port: 8080}
readinessProbe:
  httpGet: {path: /ready, port: 8080}
"""
```

### 2단계 — RBAC

```python
"""
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata: {name: reader, namespace: web}
rules:
- apiGroups: [""]
  resources: ["pods", "pods/log"]
  verbs: ["get", "list"]
"""
```

### 3단계 — NetworkPolicy

```python
"""
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: {name: web-only, namespace: web}
spec:
  podSelector: {matchLabels: {app: web}}
  ingress:
  - from:
    - podSelector: {matchLabels: {role: lb}}
"""
```

### 4단계 — 관측성 수집

```python
import subprocess

def top_pods(ns):
    res = subprocess.run(
        ["kubectl", "top", "pods", "-n", ns],
        capture_output=True, text=True, check=True,
    )
    return res.stdout
```

### 5단계 — 런북 스니펫

```python
def runbook_step(name):
    return {
        "name": name,
        "preconditions": ["alert fired", "owner paged"],
        "actions": ["check probe", "rollout status", "rollback if needed"],
    }
```

## 이 코드에서 주목할 점

- *readiness* 가 *0/1* 일 때 *트래픽 차단*.
- *RBAC* 는 *최소 권한* 부터 시작.
- *NetworkPolicy* 는 *기본 deny* 가 가장 안전.

## 자주 하는 실수 5가지

1. ***liveness* 만 두고 *readiness* 누락.**
2. ***모든 권한* 을 *기본* 으로.**
3. ***NetworkPolicy* 미적용으로 *측면 이동* 허용.**
4. ***로그* 만 보고 *지표* 무시.**
5. ***런북* 없이 *대응* 시도.**

## 실무에서는 이렇게 쓰입니다

*Argo CD* 같은 *GitOps* 도구가 *Git* 의 상태를 *클러스터* 에 *수렴* 시키며, *대시보드* 와 *런북* 으로 *야간* 에도 대응합니다.

## 체크리스트

- [ ] *probe* 3종 검토.
- [ ] *RBAC 최소 권한*.
- [ ] *NetworkPolicy 기본 deny*.
- [ ] *대시보드 + 알람*.
- [ ] *런북* 존재.

## 정리 및 다음 단계

여기까지가 *Kubernetes 101* 시리즈입니다. 다음 단계는 *Serverless* 와 *SRE* 시리즈에서 *운영성* 을 더 깊이 다룹니다.

<!-- toc:begin -->
- [Kubernetes란 무엇인가?](./01-what-is-kubernetes.md)
- [Pod](./02-pod.md)
- [Deployment](./03-deployment.md)
- [Service](./04-service.md)
- [Ingress](./05-ingress.md)
- [ConfigMap과 Secret](./06-configmap-and-secret.md)
- [Volume](./07-volume.md)
- [HPA](./08-hpa.md)
- [Helm](./09-helm.md)
- **운영 관점의 Kubernetes (현재 글)**
<!-- toc:end -->

## 참고 자료

- [Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- [RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
- [NetworkPolicy](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
- [Argo CD](https://argo-cd.readthedocs.io/)

Tags: Kubernetes, SRE, Observability, GitOps, DevOps
