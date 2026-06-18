---
title: "바이브코딩을 위한 Kubernetes 기초 (10/10): 운영 관점의 Kubernetes"
series: kubernetes-101
episode: 10
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - Kubernetes
  - SRE
  - Observability
  - GitOps
  - DevOps
---

# 바이브코딩을 위한 Kubernetes 기초 (10/10): 운영 관점의 Kubernetes

이 글은 "바이브코딩을 위한 Kubernetes 기초" 시리즈의 마지막 글입니다.

---

클러스터가 떠 있다는 사실과 운영 가능하다는 사실은 다릅니다. 바이브코딩에서 AI는 Kubernetes 매니페스트를 빠르게 만들어 주지만, 파드가 실행 중이어도 준비되지 않은 상태로 트래픽을 받을 수 있고, 장애가 나도 대응 절차가 없으면 복구는 매번 사람 기억에 의존하게 됩니다.

probes, 접근 권한, 네트워크 경계, 관측성, GitOps, 런북이 함께 맞물려야 비로소 신뢰할 수 있는 서비스가 됩니다. Kubernetes 운영이 어려운 이유는 기능이 많아서가 아니라 이 계약들이 서로 연결되어 있기 때문입니다.

> **핵심 인사이트:** '클러스터가 떠 있다'와 '운영 가능하다'는 다른 말입니다. probes·RBAC·NetworkPolicy·관측성·GitOps·런북이 함께 맞물려야 사람의 기억이 아닌 시스템으로 장애 대응이 흘러갑니다.

## 이 글에서 다룰 문제

- liveness, readiness, startup probe는 어떤 역할을 나눌까요?
- RBAC와 NetworkPolicy는 왜 운영의 기본 경계일까요?
- 메트릭, 로그, 트레이스는 왜 함께 봐야 할까요?
- AI가 만든 매니페스트에서 운영 관점으로 확인할 것은 무엇인가요?
- 장애 대응 런북은 어떻게 만들어야 할까요?

## 운영 핵심 패턴

```yaml
# Deployment with probes and resources
spec:
  containers:
    - name: api
      image: ghcr.io/example/api:1.2.0
      livenessProbe:
        httpGet: {path: /healthz, port: 8000}
      readinessProbe:
        httpGet: {path: /ready, port: 8000}
        initialDelaySeconds: 5
        periodSeconds: 10
      resources:
        requests: {cpu: "200m", memory: "256Mi"}
        limits: {cpu: "500m", memory: "512Mi"}
```

```yaml
# RBAC 최소 권한
kind: Role
rules:
- apiGroups: [""]
  resources: ["pods", "pods/log"]
  verbs: ["get", "list"]

# NetworkPolicy 기본 거부 + 허용
kind: NetworkPolicy
spec:
  podSelector: {matchLabels: {app: web}}
  ingress:
  - from:
    - podSelector: {matchLabels: {role: lb}}
```

## 변경 전후 비교

**Before: 운영 기준 없음**
```text
- 수동 kubectl 명령으로 대응
- 로그 검색과 추측 중심 디버깅
- 같은 장애가 반복될 때마다 처음부터 시작
- probe, RBAC, NetworkPolicy 없음
```

**After: 운영 체계 갖춤**
```text
- probe가 트래픽 차단/재시작 신호를 자동 처리
- 대시보드와 알림이 이상 징후를 먼저 보여줌
- 런북이 대응 순서를 표준화
- GitOps로 변경 이력 추적 가능
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| liveness만 두고 readiness 생략 | 준비 안 된 파드로 트래픽 유입 | liveness + readiness 분리 필수 |
| 권한을 넓게 열고 기본값처럼 사용 | 실수 하나가 전체 서비스에 영향 | 최소 권한 RBAC부터 시작 |
| NetworkPolicy 없이 전부 허용 | 보안 사고 시 측면 이동 차단 어려움 | 필수 경로만 허용하는 NetworkPolicy |
| 로그만 보고 메트릭/트레이스 무시 | 장애 원인 추측에 의존 | 메트릭 + 로그 + 트레이스 함께 수집 |
| 런북 없이 사람 기억에 의존 | 담당자 교체 시 대응 품질 저하 | 장애 유형별 런북 작성 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"Kubernetes Deployment를 만들어줘.
liveness/readiness probe,
resource request/limit,
비root 실행,
RBAC 최소 권한까지 포함해야 해"

# 장애 시 빠른 진단 순서:
kubectl rollout status deploy/api -n prod
kubectl describe pod -n prod -l app=api
kubectl logs -n prod deploy/api --tail=200
kubectl get events -n prod --sort-by=.metadata.creationTimestamp
```

## 운영 체크리스트

- [ ] 모든 워크로드에 liveness + readiness probe가 있다
- [ ] resource request와 limit이 설정됐다
- [ ] RBAC를 최소 권한으로 설계했다
- [ ] NetworkPolicy 기본 거부 전략을 검토했다
- [ ] 메트릭, 로그, 트레이스를 수집한다
- [ ] 장애 유형별 런북이 있다
- [ ] `latest` 대신 고정 버전 태그를 사용한다

## 처음 질문으로 돌아가기

- **liveness와 readiness의 차이는?** liveness는 재시작 필요 여부, readiness는 트래픽 수용 가능 여부를 판단합니다. 둘을 섞으면 배포와 장애 대응이 모두 흔들립니다.
- **RBAC와 NetworkPolicy가 기본 경계인 이유는?** 권한과 네트워크 경계가 없으면 실수 하나가 전체 서비스로 번질 수 있습니다.
- **메트릭, 로그, 트레이스를 함께 봐야 하는 이유는?** 각각 현재 상태, 이벤트 순서, 요청 경로를 보여주며 셋을 함께 봐야 장애 원인을 구조적으로 좁힐 수 있습니다.

## 정리

Kubernetes 운영 성숙도는 기능 사용량이 아니라 "동일 장애를 같은 속도로 복구할 수 있는가"로 측정합니다. 바이브코딩에서 AI가 만든 매니페스트에 probe, resource limits, RBAC, NetworkPolicy가 빠져 있다면 이 글의 체크리스트로 보완하세요. Kubernetes 101 시리즈를 통해 클러스터 운영의 기본기를 갖추셨기를 바랍니다.

## 참고 자료

- [Kubernetes Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- [RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
- [NetworkPolicy](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
- [Argo CD](https://argo-cd.readthedocs.io/)
- [Kubernetes 101 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/kubernetes-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Kubernetes 기초 (1/10): Kubernetes란 무엇인가?
- 바이브코딩을 위한 Kubernetes 기초 (2/10): Pod
- 바이브코딩을 위한 Kubernetes 기초 (3/10): Deployment
- 바이브코딩을 위한 Kubernetes 기초 (4/10): Service
- 바이브코딩을 위한 Kubernetes 기초 (5/10): Ingress
- 바이브코딩을 위한 Kubernetes 기초 (6/10): ConfigMap과 Secret
- 바이브코딩을 위한 Kubernetes 기초 (7/10): Volume
- 바이브코딩을 위한 Kubernetes 기초 (8/10): HPA
- 바이브코딩을 위한 Kubernetes 기초 (9/10): Helm
- **바이브코딩을 위한 Kubernetes 기초 (10/10): 운영 관점의 Kubernetes (현재 글)**
<!-- toc:end -->

Tags: 바이브코딩, Kubernetes, SRE, Observability, GitOps, DevOps
