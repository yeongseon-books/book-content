---
series: kubernetes-101
episode: 10
title: 운영 관점의 Kubernetes
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Kubernetes
  - SRE
  - Observability
  - GitOps
  - DevOps
seo_description: 프로브, RBAC, 관측성, GitOps로 보는 Kubernetes 운영 기본기를 설명합니다.
last_reviewed: '2026-05-15'
---

# 운영 관점의 Kubernetes

클러스터가 떠 있다는 사실과 운영 가능하다는 사실은 다릅니다. 파드가 실행 중이어도 준비되지 않은 상태로 트래픽을 받을 수 있고, 로그가 쌓여도 누가 볼 수 있는지 정리가 안 돼 있을 수 있으며, 장애가 나도 대응 절차가 없으면 복구는 매번 사람 기억에 의존하게 됩니다.

이 글은 Kubernetes 101 시리즈의 마지막 글입니다.

여기서는 Kubernetes 운영을 기능 목록이 아니라 probes, 접근 권한, 네트워크 경계, 관측성, GitOps, 런북이 함께 맞물려야 성립하는 운영 모델로 정리하겠습니다.

## 이 글에서 다룰 문제

> Kubernetes 운영은 클러스터를 띄우는 일에서 끝나지 않고, 트래픽 수용 조건과 권한 경계, 관측 데이터, 변경 절차, 장애 대응 문서를 함께 갖춰야 비로소 완성됩니다.

- liveness, readiness, startup probe는 어떤 역할을 나눌까요?
- RBAC와 NetworkPolicy는 왜 운영의 기본 경계일까요?
- 메트릭, 로그, 트레이스는 왜 함께 봐야 할까요?
- GitOps는 수동 `kubectl` 운영과 무엇이 다를까요?
- 런북은 왜 문서가 아니라 운영 도구일까요?

## 왜 중요한가

애플리케이션이 기능적으로 동작하는 것과, 야간에도 문제 없이 유지되는 것은 전혀 다른 수준의 이야기입니다. 운영성이 부족하면 장애가 났을 때 원인을 찾는 시간보다 추측하는 시간이 더 길어집니다.

Kubernetes는 많은 자동화를 제공하지만, 운영 감각까지 자동으로 주지는 않습니다. probe를 어떻게 나눌지, 권한을 어디까지 열지, 어떤 지표를 모으고 어떤 절차로 배포를 되돌릴지까지 정해야 비로소 신뢰할 수 있는 서비스가 됩니다.

## 한눈에 보는 구조

![한눈에 보는 구조](https://yeongseon-books.github.io/book-public-assets/assets/kubernetes-101/10/10-01-concept-at-a-glance.ko.png)
*운영 관점에서는 probe, 관측성, 런북, GitOps가 따로가 아니라 하나의 대응 체계로 연결됩니다.*


이 그림은 운영이 단일 기능이 아니라 연결된 체계라는 점을 보여 줍니다. probe는 트래픽과 재시작 조건을 만들고, 관측성은 상태를 읽게 하며, 런북과 GitOps는 대응과 변경 절차를 반복 가능하게 만듭니다.

## 핵심 용어

- liveness probe: 재시작이 필요한지 판단하는 신호입니다.
- readiness probe: 트래픽을 받아도 되는지 판단하는 신호입니다.
- RBAC: 역할 기반 접근 제어입니다.
- NetworkPolicy: 파드 간 통신 범위를 제한하는 규칙입니다.
- GitOps: Git을 진실 원천으로 두는 선언적 운영 방식입니다.

## 도입 전과 후

운영 기준이 없으면 수동 `kubectl`, 로그 검색, 추측 중심 디버깅이 반복됩니다. 문제를 해결해도 같은 종류의 장애가 다시 오면 대응이 매번 처음부터 시작됩니다.

probe, 대시보드, 알림, 권한 경계, 런북을 갖추면 대응이 반복 가능한 절차로 바뀝니다. 운영의 핵심은 더 많은 명령어가 아니라 같은 문제를 다시 만났을 때 더 빨리, 더 안전하게 움직일 수 있는 구조를 갖추는 데 있습니다.

## 단계별로 운영 기본기 살펴보기

### 1단계 — 프로브 추가

```python
"""
livenessProbe:
  httpGet: {path: /healthz, port: 8080}
readinessProbe:
  httpGet: {path: /ready, port: 8080}
"""
```

같은 헬스 체크처럼 보여도 역할은 다릅니다. liveness는 다시 시작해야 하는지를, readiness는 지금 트래픽을 받아도 되는지를 판단합니다. 운영에서 이 둘을 섞으면 배포와 장애 대응이 함께 흔들립니다.

### 2단계 — RBAC 정의

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

권한은 가능한 한 작게 시작하는 편이 좋습니다. Kubernetes에서 기본적으로 너무 많은 권한을 열어 두면, 실수 한 번이 훨씬 큰 운영 사고로 이어질 수 있습니다.

### 3단계 — NetworkPolicy 적용

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

파드 간 통신을 모두 열어 두는 방식은 편하지만, 사고가 나면 측면 이동을 막기 어렵습니다. NetworkPolicy는 네트워크 경계를 선언적으로 표현하는 기본 수단입니다.

### 4단계 — 관측 데이터 수집

```python
import subprocess

def top_pods(ns):
    res = subprocess.run(
        ["kubectl", "top", "pods", "-n", ns],
        capture_output=True, text=True, check=True,
    )
    return res.stdout
```

메트릭은 현재 자원 상태를 읽는 가장 빠른 신호입니다. 하지만 메트릭만으로는 충분하지 않고, 로그와 트레이스까지 함께 봐야 장애 원인을 구조적으로 좁힐 수 있습니다.

### 5단계 — 런북 단계 정리

```python
def runbook_step(name):
    return {
        "name": name,
        "preconditions": ["alert fired", "owner paged"],
        "actions": ["check probe", "rollout status", "rollback if needed"],
    }
```

런북은 문서만 예쁘게 쓰는 일이 아닙니다. 어떤 알림이 울렸을 때 무엇부터 확인하고, 어디서 멈추고, 언제 롤백할지까지 표준화하는 운영 도구입니다.

## 검증 흐름

```bash
kubectl describe pod web-xxxxx
kubectl auth can-i get pods --as system:serviceaccount:web:default -n web
kubectl get networkpolicy -n web
```

**예상되는 결과:** `describe pod`에서는 readiness/liveness 이벤트를 통해 트래픽 차단과 재시작 신호를 분리해서 읽을 수 있어야 합니다. `auth can-i`는 서비스어카운트 권한이 실제로 최소 권한에 맞는지 검증하고, NetworkPolicy 목록은 네트워크 경계가 선언으로 남아 있는지 보여 줍니다.

**먼저 의심할 실패 모드:**

- Pod가 살아 있어도 readiness가 실패하면 애플리케이션 성공이 아니라 운영 계약 실패로 봐야 합니다.
- RBAC를 YAML로만 보고 안심하면 실제 서비스어카운트 바인딩 누락을 놓치기 쉽습니다.
- NetworkPolicy가 하나도 없다면 보안 문제는 구현 세부가 아니라 기본 경계 부재에서 시작합니다.

## 이 코드에서 먼저 봐야 할 점

- readiness가 실패하면 트래픽을 막는다는 사실이 중요합니다.
- RBAC는 최소 권한부터 시작해야 합니다.
- NetworkPolicy는 기본 거부 모델과 함께 볼 때 더 안전합니다.

이 세 가지를 먼저 잡아 두면 운영을 단순 점검 항목으로 보지 않게 됩니다. 모두 서비스 신뢰도를 결정하는 계약입니다.

## 자주 하는 실수 다섯 가지

1. liveness만 두고 readiness를 빼먹습니다.
2. 권한을 넓게 열어 두고 기본값처럼 씁니다.
3. NetworkPolicy를 생략해 파드 간 통신을 모두 허용합니다.
4. 로그만 보고 메트릭과 트레이스를 무시합니다.
5. 런북 없이 매번 사람 기억에 의존해 대응합니다.

## 실무에서는 이렇게 봅니다

실무에서는 Argo CD 같은 GitOps 도구가 Git 상태를 클러스터에 수렴시키고, 대시보드와 알림이 이상 징후를 먼저 보여 주며, 런북이 대응 순서를 표준화합니다. 이 세 가지가 함께 있어야 야간 대응이 사람 경험에만 매이지 않습니다.

시니어 엔지니어는 운영을 개별 기능으로 보지 않습니다. probe는 트래픽 계약이고, RBAC는 권한 계약이며, GitOps는 변경 계약이고, 런북은 장애 대응 계약입니다. Kubernetes 운영이 어려운 이유도 기능이 많아서가 아니라 이 계약들이 서로 연결되어 있기 때문입니다.

## 체크리스트

- [ ] 세 가지 probe를 모두 검토했는가
- [ ] RBAC를 최소 권한으로 설계했는가
- [ ] NetworkPolicy 기본 거부 전략을 검토했는가
- [ ] 대시보드와 알림을 준비했는가
- [ ] 런북이 존재하고 실제로 쓸 수 있는가

## 연습 문제

1. liveness와 readiness의 차이를 한 줄로 설명해 보세요.
2. GitOps의 핵심 이점을 한 줄로 적어 보세요.
3. 기본 거부 NetworkPolicy의 효과를 한 줄로 정리해 보세요.

## 마무리와 다음 글

이 글에서는 Kubernetes 운영을 probes, RBAC, NetworkPolicy, 관측성, GitOps, 런북이 함께 맞물린 구조로 정리했습니다. 클러스터가 떠 있다는 사실보다, 이 요소들이 연결돼 있어야 서비스가 안정적으로 운영된다는 점이 더 중요합니다.

여기까지가 Kubernetes 101 시리즈입니다. 다음 단계에서는 더 깊은 운영성과 플랫폼 선택 문제를 다른 시리즈에서 이어 볼 수 있습니다.

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
- [kubectl auth can-i](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_auth/kubectl_auth_can-i/)

Tags: Kubernetes, SRE, Observability, GitOps, DevOps
