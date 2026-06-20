---
series: kubernetes-101
episode: 3
title: "Kubernetes 101 (3/10): Deployment"
status: published
published_to:
  tistory:
    url: "https://yeongseonchoe.tistory.com/265"
    published_at: '2026-06-02'
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Kubernetes
  - Deployment
  - ReplicaSet
  - RollingUpdate
  - DevOps
seo_description: Deployment와 ReplicaSet, 롤링 업데이트와 롤백의 기본을 설명합니다.
last_reviewed: '2026-05-15'
---

# Kubernetes 101 (3/10): Deployment

Pod를 이해한 다음 바로 마주치는 질문은 이것입니다. 파드가 죽었을 때 누가 다시 띄우는가입니다. Pod 자체는 실행 단위일 뿐이고, 스스로 자신의 개수를 유지하거나 버전을 안전하게 교체하지는 못합니다.

이 글은 Kubernetes 101 시리즈의 3번째 글입니다.

여기서는 Deployment를 파드를 여러 개 띄우는 단순 설정이 아니라, 원하는 개수를 유지하고 버전 교체와 롤백까지 책임지는 기본 워크로드 컨트롤러라는 관점에서 정리하겠습니다.

![Kubernetes 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/kubernetes-101/03/03-01-concept-at-a-glance.ko.png)
*Kubernetes 101 3장 흐름 개요*

> Deployment는 '파드를 N개 띄우는 설정'이 아니라 '원하는 개수를 유지하고 버전 교체와 롤백을 책임지는 컨트롤러'입니다 — 직접 Pod를 만들지 않는 이유는 Pod가 죽었을 때 자기 자신을 다시 띄우지 못하기 때문이고, 이 빈자리를 컨트롤러가 채우는 것이 Kubernetes 워크로드의 기본 모델입니다.

## 이 글에서 다룰 문제

- Deployment와 ReplicaSet은 어떤 관계일까요?
- `replicas`는 단순 숫자 이상의 어떤 의미를 가질까요?
- 이미지 변경이 왜 무중단 배포 흐름으로 이어질까요?
- 이 리소스의 설정을 잘못하면 운영에서 어떤 장애가 발생할까요?
- 프로덕션 환경에서 이 기능을 쓸 때 가장 먼저 점검할 항목은 무엇일까요?

Kubernetes를 도입하는 가장 큰 이유 가운데 하나는 자동 복구와 점진적 배포입니다. 그런데 이 두 기능은 클러스터가 막연히 제공하는 마법이 아닙니다. 원하는 개수의 파드를 유지하고, 새 버전으로 서서히 갈아 끼우고, 문제가 생기면 이전 상태로 되돌릴 수 있도록 관리하는 객체가 필요합니다.

그 역할을 맡는 것이 Deployment입니다. 입문 단계에서 이 객체를 제대로 이해하면 이후의 HPA, Helm, GitOps까지도 훨씬 자연스럽게 읽힙니다. 반대로 Pod만 알고 Deployment를 건너뛰면 Kubernetes 운영이 매번 수동 조작처럼 보이기 쉽습니다.

## 한눈에 보는 구조

Deployment는 직접 파드 수를 세는 대신 ReplicaSet을 통해 파드를 관리합니다. 그래서 이미지가 바뀌면 새 ReplicaSet이 생기고, 이전 ReplicaSet은 점진적으로 줄어듭니다. 이 중간 계층이 있어야 롤링 업데이트와 롤백이 구조적으로 가능해집니다.

- Deployment: 파드 집합의 원하는 상태를 선언하는 상위 객체입니다.
- ReplicaSet: 원하는 파드 개수를 맞추는 컨트롤러입니다.
- replicas: 유지하고 싶은 파드 수입니다.
- rollout: 새 버전으로 점진적으로 교체하는 흐름입니다.
- rollback: 이전 ReplicaSet으로 되돌리는 흐름입니다.

## 도입 전과 후

| 항목 | Pod 직접 관리 | Deployment 사용 |
|---|---|---|
| 파드 장애 복구 | 수동 재생성 필요 | 컨트롤러가 자동 교체 |
| 버전 업데이트 | 기존 삭제 후 신규 생성 (중단 발생) | 롤링 업데이트로 무중단 교체 |
| 롤백 | 이전 YAML을 다시 적용해야 함 | `kubectl rollout undo` 한 줄 |
| 스케일 조절 | 수동 파드 추가/삭제 | `kubectl scale` 또는 HPA 연동 |
| 배포 이력 | 없음 | revision 이력 자동 보관 |

## Deployment YAML 완전 이해

### 기본 Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
  labels:
    app: web
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web           # 이 라벨과 일치하는 파드를 관리
  template:
    metadata:
      labels:
        app: web         # selector와 반드시 일치해야 함
    spec:
      containers:
      - name: app
        image: nginx:1.25
        ports:
        - containerPort: 80
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 256Mi
```

이 예제에서 가장 먼저 볼 값은 `replicas: 3`입니다. 이는 단순한 숫자가 아니라 서비스가 감당해야 할 최소 실행 개수에 대한 선언입니다. 하나가 죽어도 세 개를 유지하려는 의도가 여기에 담깁니다.

### 롤링 업데이트 전략 명시

```yaml
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1   # 동시에 중단 허용 파드 수 (또는 25%)
      maxSurge: 1         # 기존 replicas를 초과해 추가 생성 허용 수 (또는 25%)
  selector:
    matchLabels:
      app: web
  template:
    spec:
      containers:
      - name: app
        image: nginx:1.25
        readinessProbe:
          httpGet:
            path: /healthz
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 10
```

`maxUnavailable`과 `maxSurge`를 명시하면 배포 속도와 안정성을 균형 있게 조절할 수 있습니다. readinessProbe가 없으면 새 파드가 실제로 준비되기 전에 트래픽이 흘러 오류가 발생합니다.

## 단계별로 무중단 배포 흐름 보기

### 1단계 — 적용

```bash
kubectl apply -f deployment.yaml
```

적용 이후부터는 Deployment와 ReplicaSet이 현재 상태를 원하는 상태에 맞추기 시작합니다. 사용자가 일일이 파드를 세거나 다시 만들지 않아도 되는 이유가 바로 여기에 있습니다.

### 2단계 — 이미지 업데이트

```bash
# 이미지 태그 변경으로 롤링 업데이트 시작
kubectl set image deployment/web app=nginx:1.26

# 또는 YAML 수정 후 재적용
# image: nginx:1.26 으로 변경 후
kubectl apply -f deployment.yaml
```

이미지 태그만 바꿔도 Deployment는 이를 새 버전 배포로 해석합니다. 기존 파드를 한 번에 모두 없애는 대신, 전략에 따라 새 파드를 띄우고 준비 상태를 확인하면서 교체합니다.

### 3단계 — rollout 상태 확인

```bash
# 배포 완료까지 대기
kubectl rollout status deployment/web

# 출력 예시
# Waiting for deployment "web" rollout to finish: 1 out of 3 new replicas have been updated...
# Waiting for deployment "web" rollout to finish: 2 out of 3 new replicas have been updated...
# deployment "web" successfully rolled out
```

배포는 명령이 끝났다고 끝나는 일이 아닙니다. 새 파드가 실제로 준비 완료 상태가 되어 트래픽을 받을 수 있는지 확인해야 비로소 배포가 끝났다고 볼 수 있습니다.

### 4단계 — 배포 이력 확인

```bash
kubectl rollout history deployment/web

# 출력 예시
# REVISION  CHANGE-CAUSE
# 1         <none>
# 2         <none>

# 특정 revision 상세 보기
kubectl rollout history deployment/web --revision=2
```

### 5단계 — 롤백

```bash
# 직전 버전으로 롤백
kubectl rollout undo deployment/web

# 특정 revision으로 롤백
kubectl rollout undo deployment/web --to-revision=1
```

롤백은 마지막 안전장치입니다. 자동화가 잘 되어 있어도, 실제로 이전 ReplicaSet으로 되돌리는 흐름을 알고 있어야 야간 장애 대응 속도가 달라집니다.

## 검증 흐름

```bash
kubectl get deploy,rs,pods -l app=web
kubectl rollout status deployment/web
kubectl rollout history deployment/web
```

**예상되는 결과:** Deployment와 ReplicaSet, Pod 수가 서로 맞아야 하고, `rollout status`는 새 ReplicaSet이 준비 완료될 때까지 대기한 뒤 성공 메시지를 반환해야 합니다. `rollout history`에는 최소 한 개 이상의 revision이 남아 있어야 롤백 판단이 쉬워집니다.

**먼저 의심할 실패 모드:**

- Deployment는 있는데 Pod가 없으면 selector와 template labels가 어긋난 경우가 많습니다.
- rollout이 멈추면 이미지 문제보다 readiness probe 실패를 먼저 확인하는 편이 실무에서 더 자주 맞습니다.
- revision 이력이 없거나 너무 짧으면 rollback 자체보다 배포 기록 정책부터 손봐야 합니다.

## 트러블슈팅 시나리오

### 시나리오 1: 롤아웃이 멈춘 경우

```bash
# 현재 상태 확인
kubectl rollout status deployment/web
# Waiting for deployment "web" rollout to finish...

# 파드 상태 확인
kubectl get pods -l app=web

# 특정 파드 상세 확인
kubectl describe pod <pod-name>

# 원인 분석 포인트
# 1. readiness probe 실패 -> 새 파드가 Ready 상태 안 됨
# 2. 이미지 Pull 실패 -> ImagePullBackOff
# 3. 자원 부족 -> Pending 상태 지속
# 4. 컨테이너 크래시 -> CrashLoopBackOff
```

### 시나리오 2: selector 불일치

```bash
# ReplicaSet이 파드를 관리 못하는 경우
kubectl get rs
# NAME         DESIRED   CURRENT   READY   AGE
# web-abc123   3         0         0       1m  <- 파드 0개

# 원인: spec.selector.matchLabels와 spec.template.metadata.labels 불일치
# 해결: 두 값을 정확히 일치시킨 후 재적용
```

### 시나리오 3: 롤백 후에도 문제 지속

```bash
# 현재 이미지 확인
kubectl get deployment web -o jsonpath='{.spec.template.spec.containers[0].image}'

# 모든 revision 이미지 확인
kubectl rollout history deployment/web --revision=1
kubectl rollout history deployment/web --revision=2

# 이력 정책 확인 (보관할 revision 수)
kubectl get deployment web -o jsonpath='{.spec.revisionHistoryLimit}'
```

## 자주 하는 실수

| 실수 | 문제 | 올바른 방법 |
|---|---|---|
| Pod 직접 생성 후 복구 기대 | 죽으면 그대로 사라짐 | Deployment로 상위 컨트롤러에 위임 |
| `replicas: 1` 설정 | 단일 파드 장애 시 서비스 중단 | 최소 2개 이상 설정 |
| maxUnavailable을 너무 크게 설정 | 배포 중 과도한 서비스 용량 감소 | 서비스 특성에 맞게 조정 |
| readiness probe 없이 배포 | 준비 안 된 파드에 트래픽 유입 | httpGet 또는 exec probe 필수 설정 |
| 롤백 절차 미연습 | 장애 시 실수 가능성 증가 | 정기적으로 롤백 절차 검증 |

## 실무에서는 이렇게 봅니다

실무에서는 Deployment YAML을 Git에 두고, Argo CD나 Flux가 그 선언을 클러스터와 맞추는 구조를 자주 봅니다. 이때 Deployment는 단순 리소스가 아니라 배포 단위의 기준점이 됩니다.

시니어 엔지니어는 Deployment를 볼 때 두 가지를 특히 봅니다. 첫째, 대부분의 stateless 워크로드에서 Deployment는 기본값입니다. 둘째, 무중단 배포의 본질은 Deployment라는 이름이 아니라 readiness와 배포 전략을 얼마나 제대로 잡았는가에 달려 있습니다.

```bash
# 실무에서 Deployment 운영 시 자주 쓰는 명령 모음
kubectl get deployment web -o yaml              # 현재 전체 스펙 확인
kubectl describe deployment web                 # 이벤트 포함 상세 확인
kubectl get rs -l app=web                       # ReplicaSet 이력 확인
kubectl rollout history deployment/web          # 배포 이력
kubectl scale deployment web --replicas=5       # 즉시 스케일 조절
kubectl rollout pause deployment/web            # 배포 일시 중지
kubectl rollout resume deployment/web           # 배포 재개
```

## Readiness와 Liveness Probe 설정

Probe는 무중단 배포의 실제 핵심입니다. 올바르게 설정해야 롤링 업데이트가 안전하게 동작합니다.

```yaml
spec:
  containers:
  - name: app
    image: myorg/app:1.0
    readinessProbe:              # 파드가 트래픽을 받을 준비가 됐는지 확인
      httpGet:
        path: /health/ready
        port: 8080
      initialDelaySeconds: 10   # 컨테이너 시작 후 첫 확인까지 대기
      periodSeconds: 5          # 확인 간격
      failureThreshold: 3       # 3번 실패 시 Ready 상태 해제 (트래픽 제외)
    livenessProbe:               # 파드가 살아있는지 확인 (죽었으면 재시작)
      httpGet:
        path: /health/live
        port: 8080
      initialDelaySeconds: 30   # readiness보다 늦게 시작
      periodSeconds: 10
      failureThreshold: 5       # 5번 실패 시 컨테이너 재시작
    startupProbe:                # 느린 시작 앱을 위한 시작 완료 확인
      httpGet:
        path: /health/startup
        port: 8080
      failureThreshold: 30      # 30번 × 10초 = 최대 5분 대기
      periodSeconds: 10
```

| Probe 종류 | 실패 시 동작 | 주 용도 |
|---|---|---|
| readinessProbe | 트래픽에서 제외 (재시작 안 함) | 준비 완료 전 트래픽 차단 |
| livenessProbe | 컨테이너 재시작 | 데드락, 무한루프 감지 |
| startupProbe | 일정 시간 내 준비 안 되면 재시작 | 느린 초기화 앱 보호 |

```bash
# Probe 동작 상태 확인
kubectl describe pod <pod-name> | grep -A 10 "Readiness\|Liveness\|Startup"

# Probe 실패로 인한 재시작 횟수 확인
kubectl get pod <pod-name> -o jsonpath='{.status.containerStatuses[0].restartCount}'
```

## 운영 체크리스트

- [ ] `replicas`를 2 이상으로 둘지 검토했는가
- [ ] Readiness probe를 정의했는가
- [ ] RollingUpdate 옵션을 명시했는가
- [ ] 롤백 절차를 문서화했는가
- [ ] `revisionHistoryLimit`을 적절히 설정했는가
- [ ] selector와 template labels가 정확히 일치하는가

## 연습 문제

1. Deployment와 ReplicaSet의 차이를 한 줄로 설명해 보세요.
2. readiness가 무중단 배포의 핵심인 이유를 한 줄로 적어 보세요.
3. 롤백이 느리거나 어려워지는 상황을 하나 떠올려 보세요.
4. `maxUnavailable: 0`으로 설정하면 어떤 효과가 있나요?
5. Deployment와 StatefulSet은 어떤 상황에서 나눠 쓰나요?

## Deployment와 유사한 워크로드 컨트롤러 비교

Deployment가 기본값이지만, 워크로드 특성에 따라 다른 컨트롤러를 선택해야 합니다.

| 컨트롤러 | 사용 시나리오 | 특징 |
|---|---|---|
| Deployment | Stateless 애플리케이션 | 가장 일반적, 롤링 업데이트/롤백 |
| StatefulSet | 데이터베이스, 메시지 큐 | 파드마다 고정 이름, 안정적 스토리지 |
| DaemonSet | 모든 노드에 배치 | 로그 수집기, 모니터링 에이전트 |
| Job | 일회성 작업 | 배치 처리, 마이그레이션 |
| CronJob | 주기적 작업 | 정기 백업, 리포트 생성 |

```bash
# StatefulSet과 Deployment 파드 이름 비교
kubectl get pods -l app=web           # web-abc123-xyz (Deployment: 랜덤)
kubectl get pods -l app=db            # db-0, db-1, db-2 (StatefulSet: 고정)

# DaemonSet 파드 확인 (모든 노드에 하나씩)
kubectl get pods -n kube-system -o wide | grep node-exporter
```

## Deployment 배포 전략 선택

```yaml
# 전략 1: RollingUpdate (기본, 무중단 배포)
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxUnavailable: 1
    maxSurge: 1

# 전략 2: Recreate (전체 교체, 중단 발생)
# 데이터베이스 스키마 변경처럼 구버전과 병행 실행 불가 시 사용
strategy:
  type: Recreate
```

```bash
# 배포 진행 중 일시 중지 (카나리 배포 시뮬레이션)
kubectl rollout pause deployment/web

# 일부 파드가 새 버전으로 교체된 상태 확인
kubectl get pods -l app=web -o custom-columns=NAME:.metadata.name,IMAGE:.spec.containers[0].image

# 검증 후 재개
kubectl rollout resume deployment/web
```

## 마무리와 다음 글

이 글에서는 Deployment를 파드 개수 유지, 롤링 업데이트, 롤백을 맡는 기본 워크로드 컨트롤러로 정리했습니다. Pod만 직접 다룰 때보다 운영이 훨씬 안정되고, 배포를 반복 가능한 절차로 바꾸는 출발점도 바로 여기입니다.

다음 글에서는 이렇게 떠 있는 파드 집합을 내부와 외부에서 어떻게 안정적으로 찾고 호출하는지, Service를 중심으로 보겠습니다.

## 정리

Deployment는 '파드를 N개 띄우는 설정'이 아니라 '원하는 개수를 유지하고 버전 교체와 롤백을 책임지는 컨트롤러'입니다 — 직접 Pod를 만들지 않는 이유는 Pod가 죽었을 때 자기 자신을 다시 띄우지 못하기 때문이고, 이 빈자리를 컨트롤러가 채우는 것이 Kubernetes 워크로드의 기본 모델입니다. 이 글에서는 한눈에 보는 구조부터 마무리와 다음 글까지 이 원칙을 구체적으로 살펴봤습니다. 핵심은 개념을 외우는 것이 아니라 실무에서 어떤 판단을 바꾸는지 이해하는 데 있습니다.

## 처음 질문으로 돌아가기

- **Deployment와 ReplicaSet은 어떤 관계일까요?**
  - Deployment가 상위 객체이고 ReplicaSet을 통해 파드 수를 관리합니다. 이미지가 바뀌면 새 ReplicaSet이 생기고, 이전 ReplicaSet은 점진적으로 줄어듭니다.
- **`replicas`는 단순 숫자 이상의 어떤 의미를 가질까요?**
  - 서비스가 유지해야 할 최소 실행 개수 선언입니다. 이 수보다 적으면 컨트롤러가 자동으로 파드를 보충합니다.
- **이미지 변경이 왜 무중단 배포 흐름으로 이어질까요?**
  - 새 이미지로 새 ReplicaSet이 생기고, readiness probe를 통과한 파드가 생길 때마다 기존 파드를 하나씩 줄이는 방식으로 교체가 진행됩니다.

<!-- toc:begin -->
## 시리즈 목차

- [Kubernetes 101 (1/10): Kubernetes란 무엇인가?](./01-what-is-kubernetes.md)
- [Kubernetes 101 (2/10): Pod](./02-pod.md)
- **Kubernetes 101 (3/10): Deployment (현재 글)**
- [Kubernetes 101 (4/10): Service](./04-service.md)
- [Kubernetes 101 (5/10): Ingress](./05-ingress.md)
- [Kubernetes 101 (6/10): ConfigMap과 Secret](./06-configmap-and-secret.md)
- [Kubernetes 101 (7/10): Volume](./07-volume.md)
- [Kubernetes 101 (8/10): HPA](./08-hpa.md)
- [Kubernetes 101 (9/10): Helm](./09-helm.md)
- [운영 관점의 Kubernetes](./10-kubernetes-in-operation.md)

<!-- toc:end -->
