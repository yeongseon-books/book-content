---
series: kubernetes-101
episode: 3
title: "Kubernetes 101 (3/10): Deployment"
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

## 먼저 던지는 질문

- Deployment와 ReplicaSet은 어떤 관계일까요?
- `replicas`는 단순 숫자 이상의 어떤 의미를 가질까요?
- 이미지 변경이 왜 무중단 배포 흐름으로 이어질까요?

## 왜 중요한가

Kubernetes를 도입하는 가장 큰 이유 가운데 하나는 자동 복구와 점진적 배포입니다. 그런데 이 두 기능은 클러스터가 막연히 제공하는 마법이 아닙니다. 원하는 개수의 파드를 유지하고, 새 버전으로 서서히 갈아 끼우고, 문제가 생기면 이전 상태로 되돌릴 수 있도록 관리하는 객체가 필요합니다.

그 역할을 맡는 것이 Deployment입니다. 입문 단계에서 이 객체를 제대로 이해하면 이후의 HPA, Helm, GitOps까지도 훨씬 자연스럽게 읽힙니다. 반대로 Pod만 알고 Deployment를 건너뛰면 Kubernetes 운영이 매번 수동 조작처럼 보이기 쉽습니다.

## 한눈에 보는 구조

Deployment는 직접 파드 수를 세는 대신 ReplicaSet을 통해 파드를 관리합니다. 그래서 이미지가 바뀌면 새 ReplicaSet이 생기고, 이전 ReplicaSet은 점진적으로 줄어듭니다. 이 중간 계층이 있어야 롤링 업데이트와 롤백이 구조적으로 가능해집니다.

## 핵심 용어

- Deployment: 파드 집합의 원하는 상태를 선언하는 상위 객체입니다.
- ReplicaSet: 원하는 파드 개수를 맞추는 컨트롤러입니다.
- replicas: 유지하고 싶은 파드 수입니다.
- rollout: 새 버전으로 점진적으로 교체하는 흐름입니다.
- rollback: 이전 ReplicaSet으로 되돌리는 흐름입니다.

## 도입 전과 후

Deployment가 없으면 파드 하나가 죽었을 때 서비스가 바로 흔들릴 수 있습니다. 새 버전 배포도 기존 파드를 지우고 새 파드를 띄우는 식으로 거칠게 끝나기 쉽습니다.

Deployment를 사용하면 죽은 파드는 다시 만들어지고, 이미지 변경은 배포 전략에 따라 서서히 적용되며, 이전 버전 이력도 남습니다. Kubernetes 운영이 훨씬 예측 가능해지는 이유가 바로 여기에 있습니다.

## 단계별로 무중단 배포 흐름 보기

### 1단계 — Deployment 매니페스트 작성

```python
"""
apiVersion: apps/v1
kind: Deployment
metadata: {name: web}
spec:
  replicas: 3
  selector: {matchLabels: {app: web}}
  template:
    metadata: {labels: {app: web}}
    spec:
      containers:
      - name: app
        image: nginx:1.25
"""
```

이 예제에서 가장 먼저 볼 값은 `replicas: 3`입니다. 이는 단순한 숫자가 아니라 서비스가 감당해야 할 최소 실행 개수에 대한 선언입니다. 하나가 죽어도 세 개를 유지하려는 의도가 여기에 담깁니다.

### 2단계 — 적용

```python
import subprocess

def apply(path):
    subprocess.run(["kubectl", "apply", "-f", path], check=True)
```

적용 이후부터는 Deployment와 ReplicaSet이 현재 상태를 원하는 상태에 맞추기 시작합니다. 사용자가 일일이 파드를 세거나 다시 만들지 않아도 되는 이유가 바로 여기에 있습니다.

### 3단계 — 이미지 업데이트

```python
def set_image(dep, container, image):
    subprocess.run([
        "kubectl", "set", "image",
        f"deployment/{dep}", f"{container}={image}",
    ], check=True)
```

이미지 태그만 바꿔도 Deployment는 이를 새 버전 배포로 해석합니다. 기존 파드를 한 번에 모두 없애는 대신, 전략에 따라 새 파드를 띄우고 준비 상태를 확인하면서 교체합니다.

### 4단계 — rollout 상태 확인

```python
def rollout_status(dep):
    res = subprocess.run(
        ["kubectl", "rollout", "status", f"deployment/{dep}"],
        capture_output=True, text=True, check=True,
    )
    return res.stdout
```

배포는 명령이 끝났다고 끝나는 일이 아닙니다. 새 파드가 실제로 준비 완료 상태가 되어 트래픽을 받을 수 있는지 확인해야 비로소 배포가 끝났다고 볼 수 있습니다.

### 5단계 — 롤백

```python
def rollback(dep):
    subprocess.run(
        ["kubectl", "rollout", "undo", f"deployment/{dep}"],
        check=True,
    )
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

## 이 코드에서 먼저 봐야 할 점

- `selector`와 `labels`는 정확히 일치해야 합니다.
- 이미지 변경은 작아 보여도 실제로는 배포 이벤트입니다.
- `undo`는 직전 ReplicaSet 기준으로 돌아갑니다.

이 세 가지를 놓치면 Deployment는 "파드를 많이 띄우는 YAML" 정도로만 보입니다. 하지만 실제로는 배포 이력과 복구 흐름까지 포함한 운영 객체입니다.

## 자주 하는 실수 다섯 가지

1. Pod를 직접 만들고 재시작과 복구를 Kubernetes가 알아서 해 줄 거라고 기대합니다.
2. `replicas: 1`로 두고도 고가용성을 기대합니다.
3. RollingUpdate 관련 옵션을 대충 넘겨 한 번에 너무 많이 교체합니다.
4. readiness 없이 배포해서 절반만 살아 있는 상태로 rollout을 끝냅니다.
5. 롤백이 있다고 믿지만 실제 절차를 한 번도 연습하지 않습니다.

## 실무에서는 이렇게 봅니다

실무에서는 Deployment YAML을 Git에 두고, Argo CD나 Flux가 그 선언을 클러스터와 맞추는 구조를 자주 봅니다. 이때 Deployment는 단순 리소스가 아니라 배포 단위의 기준점이 됩니다.

시니어 엔지니어는 Deployment를 볼 때 두 가지를 특히 봅니다. 첫째, 대부분의 stateless 워크로드에서 Deployment는 기본값입니다. 둘째, 무중단 배포의 본질은 Deployment라는 이름이 아니라 readiness와 배포 전략을 얼마나 제대로 잡았는가에 달려 있습니다.

## 체크리스트

- [ ] `replicas`를 2 이상으로 둘지 검토했는가
- [ ] Readiness probe를 정의했는가
- [ ] RollingUpdate 옵션을 명시했는가
- [ ] 롤백 절차를 문서화했는가

## 연습 문제

1. Deployment와 ReplicaSet의 차이를 한 줄로 설명해 보세요.
2. readiness가 무중단 배포의 핵심인 이유를 한 줄로 적어 보세요.
3. 롤백이 느리거나 어려워지는 상황을 하나 떠올려 보세요.

## 마무리와 다음 글

이 글에서는 Deployment를 파드 개수 유지, 롤링 업데이트, 롤백을 맡는 기본 워크로드 컨트롤러로 정리했습니다. Pod만 직접 다룰 때보다 운영이 훨씬 안정되고, 배포를 반복 가능한 절차로 바꾸는 출발점도 바로 여기입니다.

다음 글에서는 이렇게 떠 있는 파드 집합을 내부와 외부에서 어떻게 안정적으로 찾고 호출하는지, Service를 중심으로 보겠습니다.

## 매니페스트 중심 운영 예시

Kubernetes의 강점은 명령형 조작보다 선언형 매니페스트에 있습니다. 아래 예시는 Deployment, Service, Ingress를 분리해 책임 경계를 명확히 둔 기본 형태입니다.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  labels:
    app: api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
        - name: api
          image: ghcr.io/example/api:1.2.0
          ports:
            - containerPort: 8000
          readinessProbe:
            httpGet:
              path: /healthz
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 10
          resources:
            requests:
              cpu: "200m"
              memory: "256Mi"
            limits:
              cpu: "500m"
              memory: "512Mi"
---
apiVersion: v1
kind: Service
metadata:
  name: api
spec:
  selector:
    app: api
  ports:
    - port: 80
      targetPort: 8000
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api
spec:
  ingressClassName: nginx
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: api
                port:
                  number: 80
```

readiness probe와 resource request/limit를 함께 정의하면 "배포는 되었지만 트래픽을 받으면 무너지는" 상태를 줄일 수 있습니다. 선언형 파일에서 운영 안정성을 미리 포함시키는 방식이 중요합니다.

## kubectl 운영 명령 모음

매니페스트를 적용한 뒤에는 상태 관찰 명령을 빠르게 순환해야 합니다. 아래 조합은 장애 분석에서 가장 자주 사용하는 기본 세트입니다.

```bash
kubectl apply -f k8s/
kubectl get deploy,rs,pod -n prod -o wide
kubectl rollout status deploy/api -n prod
kubectl describe pod -n prod -l app=api
kubectl logs -n prod deploy/api --tail=200
kubectl get events -n prod --sort-by=.metadata.creationTimestamp
```

`rollout status`와 `describe`를 먼저 보면 이미지 pull 실패, probe 실패, 스케줄링 실패를 빠르게 구분할 수 있습니다. 로그만 먼저 보면 인프라 원인을 애플리케이션 오류로 오판하기 쉽습니다.

## 아키텍처 관점에서 봐야 할 경계

- **API Server 경계**: 모든 선언 변경은 API 서버를 통과합니다. 직접 노드에 접속해 상태를 손으로 맞추는 방식은 drift를 만듭니다.
- **Scheduler 경계**: Pod 배치는 자원 요청, taint/toleration, affinity 규칙의 결과입니다. 노드 선택 문제는 애플리케이션 버그와 분리해 봐야 합니다.
- **Controller 경계**: Deployment Controller는 replica 수렴과 롤링 업데이트를 담당합니다. desired/current 값 차이를 관찰하는 습관이 핵심입니다.
- **Network 경계**: Service와 Ingress는 L4/L7 책임이 다릅니다. 내부 통신 실패와 외부 진입 실패를 분리해 진단해야 대응이 빨라집니다.

이 경계를 기준으로 장애를 분해하면 "클러스터 문제"라는 모호한 결론 대신, 어느 계층에서 어떤 신호가 깨졌는지 명확히 남길 수 있습니다.

## 배포 안정성을 높이는 실무 체크

1. 모든 워크로드에 readiness/liveness probe를 설정합니다.
2. `latest` 태그 대신 고정 버전 태그를 사용해 롤백 기준을 확보합니다.
3. 변경 전 `kubectl diff -f`로 영향을 검토해 무의식적 설정 누락을 줄입니다.
4. 운영 네임스페이스에는 ResourceQuota와 LimitRange를 적용해 폭주 범위를 제한합니다.
5. 배포 후 `kubectl rollout history`를 확인해 복구 경로를 문서화합니다.

Kubernetes는 기능이 많아서 어려운 도구가 아니라, 경계를 나누어 관찰하지 않으면 쉽게 혼란스러워지는 도구입니다. 매니페스트, 관찰 명령, 아키텍처 경계를 함께 묶어 운영하면 학습 속도와 안정성이 동시에 올라갑니다.

## 롤링 업데이트를 설계할 때 먼저 정할 값

Deployment는 "몇 개를 유지할지"보다 "어떻게 교체할지"가 더 중요합니다. `maxSurge`, `maxUnavailable`, `minReadySeconds`, `progressDeadlineSeconds`를 팀 합의값으로 정해 두면 장애가 줄어듭니다.

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1
    maxUnavailable: 0
minReadySeconds: 10
progressDeadlineSeconds: 600
revisionHistoryLimit: 10
```

`maxUnavailable: 0`은 무중단 지향에 유리하지만 자원 여유가 필요합니다. 반대로 여유가 적은 클러스터라면 작은 중단을 허용하고 `PDB`로 보호 범위를 명확히 하는 편이 안전할 수 있습니다.

## 배포 실패를 빠르게 되돌리는 절차

```bash
kubectl rollout status deploy/api -n prod
kubectl rollout history deploy/api -n prod
kubectl rollout undo deploy/api -n prod
kubectl get rs -n prod -l app=api
```

실패 시에는 즉시 롤백하고, 원인 분석은 복구 후 진행하는 원칙이 좋습니다. 특히 온콜 시간에는 "서비스 복구"와 "근본 원인 분석"을 분리해야 사고가 커지지 않습니다.

## 카나리 배포 전 최소 체크

- 새 버전에만 필요한 환경 변수, Secret 키가 모두 준비되었는지
- readiness probe 통과 전 트래픽 유입이 차단되는지
- 롤백 시 데이터 스키마 호환성이 유지되는지
- HPA가 배포 중 replica 변화를 과도하게 만들지 않는지

Deployment는 선언이 단순해 보여도 운영 규칙을 어떻게 채워 넣느냐에 따라 안정성이 달라집니다.

## 운영 시뮬레이션 확장

Deployment 관점의 문서를 읽고 끝내면 실제 운영에서 금방 잊힙니다. 그래서 학습 직후에 "장애를 일부러 만들어 보고 복구하는" 시뮬레이션을 반드시 권장합니다. 여기서 중요한 점은 성공 데모를 반복하는 것이 아니라, 실패 신호를 표준 절차로 읽는 훈련을 하는 것입니다. 팀이 성장할수록 기술 격차보다 절차 격차가 더 큰 장애를 만듭니다.

먼저 시뮬레이션 전 공통 기준을 맞춥니다. 대상 네임스페이스를 분리하고, 적용한 매니페스트의 Git SHA를 기록하고, 관찰 명령 5개를 고정합니다. 이 기준이 있어야 "누가, 어떤 상태에서, 무엇을 바꿨는지"를 추적할 수 있습니다.

```bash
kubectl config current-context
kubectl get ns
kubectl get deploy,po,svc,ing -n prod -o wide
kubectl get events -n prod --sort-by=.metadata.creationTimestamp
kubectl top pod -n prod
```

다음으로 장애 주입 시나리오를 단계적으로 실행합니다. 첫째, 잘못된 이미지 태그를 넣어 `ImagePullBackOff`를 발생시킵니다. 둘째, readiness probe 경로를 의도적으로 틀려 `Ready` 전환 실패를 만듭니다. 셋째, 메모리 limit를 과도하게 낮춰 OOM 재시작을 유도합니다. 넷째, selector 불일치를 만들어 트래픽 블랙홀을 재현합니다. 이 네 가지는 초급 팀이 실제 운영에서 가장 자주 만나는 장애 패턴입니다.

```bash
kubectl set image deploy/api api=ghcr.io/example/api:not-found -n prod
kubectl rollout status deploy/api -n prod
kubectl describe pod -n prod -l app=api
kubectl logs -n prod deploy/api --previous
kubectl rollout undo deploy/api -n prod
```

복구 절차는 항상 동일한 순서를 사용합니다. 1) 영향 범위 확인, 2) 즉시 완화(rollback/scale), 3) 원인 확인, 4) 재발 방지 반영입니다. 순서를 바꾸면 현장에서 토론만 길어지고 복구는 늦어집니다. 특히 온콜 시간대에는 "정확한 분석"보다 "안전한 복구"를 먼저 해야 합니다.

운영 품질을 높이려면 기술 항목을 문서 항목으로 바꿔야 합니다. 예를 들어 "probe를 잘 설정한다"가 아니라 "모든 워크로드는 readiness/liveness를 필수로 포함하고, 경로는 헬스 라우터 표준(`/readyz`, `/livez`)을 사용한다"처럼 검증 가능한 규칙으로 적어야 합니다. 또 "리소스를 적절히 준다" 대신 "CPU request는 최근 7일 P50의 1.3배, memory limit는 P99의 1.2배" 같은 팀 기준선을 고정하면 논쟁 비용이 줄어듭니다.

### 런북에 남겨야 할 최소 항목

- 장애 유형별 최초 확인 명령 3개
- 즉시 완화 명령과 금지 명령
- 롤백 기준 버전과 검증 체크리스트
- 관련 대시보드 링크와 알림 임계치
- 동일 유형 재발 시 담당 팀 에스컬레이션 경로

문서를 이 수준으로 남기면 신규 팀원이 들어와도 대응 품질이 유지됩니다. Kubernetes 운영 성숙도는 기능 사용량이 아니라 "동일 장애를 같은 속도로 복구할 수 있는가"로 측정하는 편이 정확합니다.

## 실무 검증 체크포인트

운영에서 변경을 배포할 때는 코드 리뷰와 별도로 클러스터 검증 체크를 둬야 합니다. 체크 항목은 복잡할 필요가 없습니다. 적용 전 `kubectl diff`, 적용 후 `rollout status`, 엔드포인트 연결 확인, 로그 샘플 확인, 자원 사용률 확인 정도만 일관되게 수행해도 대다수 실수를 초기에 차단할 수 있습니다.

```bash
kubectl diff -f k8s/ -n prod
kubectl apply -f k8s/ -n prod
kubectl rollout status deploy/api -n prod
kubectl get endpoints api -n prod
kubectl top pod -n prod -l app=api
```

여기서 마지막으로 중요한 원칙은 "수동 핫픽스를 원복 가능한 상태로 남긴다"는 점입니다. 긴급 대응 중에 `kubectl edit`로 해결했다면, 근무 종료 전에 반드시 매니페스트에 같은 변경을 반영해 drift를 없애야 합니다. 선언형 시스템에서 drift는 시간이 지날수록 큰 장애로 돌아옵니다.

## 관측성과 보안 기본선

Kubernetes 학습이 진행될수록 기능 사용량은 늘어나지만, 실제 장애를 줄이는 요소는 관측성과 보안 기본선입니다. 최소한 애플리케이션 로그, 인프라 이벤트, 자원 메트릭이 같은 시간축에서 비교 가능해야 하고, 서비스 계정 권한과 시크릿 접근 범위가 분리되어 있어야 합니다. 이 두 축이 약하면 배포 속도가 빨라질수록 실패 속도도 같이 빨라집니다.

관측성 기본선은 거창할 필요가 없습니다. 워크로드마다 공통 레이블(`app`, `component`, `version`)을 강제하고, 로그에 요청 식별자와 에러 코드를 남기고, 대시보드에서 레이블 필터로 바로 분해할 수 있으면 됩니다. 이벤트 스트림까지 함께 보면 "배포 변경"과 "오류 급증"의 시간적 상관관계를 빠르게 확인할 수 있습니다.

```bash
kubectl get events -n prod --sort-by=.metadata.creationTimestamp
kubectl logs -n prod deploy/api --since=10m
kubectl top pod -n prod -l app=api
kubectl top node
```

보안 기본선에서는 RBAC 최소 권한 원칙을 먼저 적용하세요. 운영 계정이 모든 네임스페이스에 쓰기 권한을 가지면 단기적으로는 편하지만, 실수 한 번이 전체 서비스로 번질 수 있습니다. 네임스페이스 단위 Role/RoleBinding을 기본으로 두고, 클러스터 전역 권한은 예외 승인 절차를 거치도록 설계하는 편이 안전합니다.

또한 NetworkPolicy를 도입하면 "통신이 되는 것이 기본"인 상태를 "허용한 통신만 된다"는 상태로 바꿀 수 있습니다. 초기에는 DNS, 내부 API, 데이터베이스 같은 필수 경로부터 열고, 나머지는 점진적으로 차단하는 방식이 현실적입니다. 정책은 기능이 아니라 운영 안전장치입니다.

마지막으로, 변경 후 검증을 자동화하세요. `kubectl apply` 이후에 상태 확인 명령을 사람이 매번 동일하게 수행하기 어렵기 때문에, CI에서 `kubectl diff`, `kubeconform`류 스키마 체크, 서버 사이드 dry-run을 묶어 두면 기본 결함을 배포 전에 차단할 수 있습니다. Kubernetes 운영 성숙도는 고급 기능보다 "기본 검증을 빠짐없이 반복하는 능력"에서 먼저 올라갑니다.

## 최종 점검 메모

배포 전 마지막 점검은 단순하지만 효과가 큽니다. 첫째, 이번 변경이 어느 리소스에 영향을 주는지 `kubectl diff`로 확인합니다. 둘째, 적용 후 `rollout status`가 끝날 때까지 기다리고, 이벤트 로그에서 경고 신호가 없는지 확인합니다. 셋째, 사용자 경로 기준 헬스 체크를 직접 호출해 응답 코드와 지연 시간을 기록합니다. 넷째, 이전 안정 버전으로 되돌릴 명령을 미리 준비해 둡니다.

```bash
kubectl diff -f k8s/ -n prod
kubectl rollout status deploy/api -n prod
kubectl get events -n prod --sort-by=.metadata.creationTimestamp
curl -fsS https://app.example.com/healthz
```

이 네 단계를 표준화하면 변경 속도가 빨라져도 운영 안정성을 유지하기 쉽습니다.

## 처음 질문으로 돌아가기

- **Deployment와 ReplicaSet은 어떤 관계일까요?**
  - Deployment는 사용자 선언을 받고, 실제 Pod 복제 개수를 유지하는 일은 그 아래 ReplicaSet이 맡습니다. 본문의 롤링 업데이트 예시처럼 이미지 버전을 바꾸면 Deployment가 새 ReplicaSet을 만들고 옛 ReplicaSet의 Pod 수를 점진적으로 줄이는 식으로 두 객체가 나란히 동작합니다.
- **`replicas`는 단순 숫자 이상의 어떤 의미를 가질까요?**
  - `replicas`는 "현재 몇 개를 띄워라"가 아니라 "항상 이 개수를 유지하라"는 목표 선언입니다. Pod가 죽거나 노드가 사라져도 컨트롤러가 desired/current 차이를 계속 좁히기 때문에, 그 숫자가 가용성과 비용을 동시에 결정하는 운영 기준선이 됩니다.
- **이미지 변경이 왜 무중단 배포 흐름으로 이어질까요?**
  - 본문의 `kubectl set image`나 `apply` 흐름에서 보듯 이미지 태그를 바꾸면 Deployment가 새 ReplicaSet을 만들고 readiness probe가 통과한 새 Pod를 점진적으로 늘리는 동안 기존 Pod를 줄입니다. 이 점진적 교체와 probe 기반 트래픽 컷오프 덕분에 사용자가 보는 가용성은 끊기지 않습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Kubernetes 101 (1/10): Kubernetes란 무엇인가?](./01-what-is-kubernetes.md)
- [Kubernetes 101 (2/10): Pod](./02-pod.md)
- **Deployment (현재 글)**
- Service (예정)
- Ingress (예정)
- ConfigMap과 Secret (예정)
- Volume (예정)
- HPA (예정)
- Helm (예정)
- 운영 관점의 Kubernetes (예정)

<!-- toc:end -->

## 참고 자료

- [Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [ReplicaSet](https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/)
- [Rolling update strategy](https://kubernetes.io/docs/tutorials/kubernetes-basics/update/update-intro/)
- [kubectl rollout](https://kubernetes.io/docs/reference/generated/kubectl/kubectl-commands#rollout)
- [Update a Deployment](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/#updating-a-deployment)

- [Kubernetes 101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/kubernetes-101/ko)

Tags: Kubernetes, Deployment, ReplicaSet, RollingUpdate, DevOps
