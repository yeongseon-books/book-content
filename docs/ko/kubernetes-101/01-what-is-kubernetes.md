---
series: kubernetes-101
episode: 1
title: What is Kubernetes?
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
  - Orchestration
  - Containers
  - DevOps
  - SRE
seo_description: Kubernetes의 기본 아이디어, 컨테이너 오케스트레이션, 컨트롤 플레인과 워커 노드의 역할을 입문자 관점에서 정리한 글
last_reviewed: '2026-05-04'
---

# What is Kubernetes?

> Kubernetes 101 시리즈 (1/10)


## 이 글에서 다룰 문제

*컨테이너* 한두 개는 *Compose* 로 충분합니다. *수십 개* 부터는 *오케스트레이터* 가 *생존 조건* 입니다.

## 전체 흐름
```mermaid
flowchart LR
    User["kubectl"] --> API["api-server"]
    API --> Etcd["etcd"]
    API --> Sched["scheduler"]
    Sched --> Node["worker node"]
    Node --> Pod["pod"]
```

## Before/After

**Before**: *서버마다* *수동 docker run* 으로 *재현 불가*.

**After**: *YAML* 한 장으로 *어디서나* 동일 결과.

## 첫 클러스터 둘러보기

### 1단계 — 컨텍스트 확인

```python
import subprocess

def current_context():
    res = subprocess.run(
        ["kubectl", "config", "current-context"],
        capture_output=True, text=True, check=True,
    )
    return res.stdout.strip()
```

### 2단계 — 노드 조회

```python
def get_nodes():
    res = subprocess.run(
        ["kubectl", "get", "nodes", "-o", "wide"],
        capture_output=True, text=True, check=True,
    )
    return res.stdout
```

### 3단계 — 네임스페이스

```python
def list_namespaces():
    res = subprocess.run(
        ["kubectl", "get", "ns"],
        capture_output=True, text=True, check=True,
    )
    return res.stdout
```

### 4단계 — 시스템 파드

```python
def system_pods():
    res = subprocess.run(
        ["kubectl", "-n", "kube-system", "get", "pods"],
        capture_output=True, text=True, check=True,
    )
    return res.stdout
```

### 5단계 — 헬스 체크

```python
def cluster_info():
    res = subprocess.run(
        ["kubectl", "cluster-info"],
        capture_output=True, text=True, check=True,
    )
    return res.stdout
```

## 이 코드에서 주목할 점

- *kubectl* 은 *api-server* 만 호출.
- *etcd* 는 *직접 다루지 않는다*.
- *namespace* 가 *기본 격리 단위*.

## 자주 하는 실수 5가지

1. ***Kubernetes = 컨테이너* 와 동의어로 오해.**
2. **노드 *수* 만 늘리면 *해결* 된다고 착각.**
3. ***etcd* 를 *직접* 만지려 함.**
4. ***kubectl* 컨텍스트 혼동으로 *프로덕션* 에 적용.**
5. **소규모인데 *Kubernetes* 부터 도입.**

## 실무에서는 이렇게 쓰입니다

*EKS / GKE / AKS* 같은 *managed Kubernetes* 가 *컨트롤 플레인* 을 *대신 운영*, 팀은 *워크로드 YAML* 에 집중합니다.

## 체크리스트

- [ ] *컨텍스트* 명시적으로 전환.
- [ ] *네임스페이스* 분리.
- [ ] *희망 상태* 를 *YAML* 로 보관.
- [ ] *managed* 우선 검토.

## 정리 및 다음 단계

오케스트레이션의 *큰 그림* 이 잡혔습니다. 다음 글은 *가장 작은 단위* 인 *Pod*.

<!-- toc:begin -->
- **Kubernetes란 무엇인가? (현재 글)**
- Pod (예정)
- Deployment (예정)
- Service (예정)
- Ingress (예정)
- ConfigMap과 Secret (예정)
- Volume (예정)
- HPA (예정)
- Helm (예정)
- 운영 관점의 Kubernetes (예정)
<!-- toc:end -->

## 참고 자료

- [Kubernetes Overview](https://kubernetes.io/docs/concepts/overview/)
- [Kubernetes components](https://kubernetes.io/docs/concepts/overview/components/)
- [kubectl reference](https://kubernetes.io/docs/reference/kubectl/)
- [Managed Kubernetes options](https://landscape.cncf.io/)
