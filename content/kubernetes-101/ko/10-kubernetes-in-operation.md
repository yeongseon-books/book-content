---
series: kubernetes-101
episode: 10
title: "Kubernetes 101 (10/10): 운영 관점의 Kubernetes"
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

# Kubernetes 101 (10/10): 운영 관점의 Kubernetes

클러스터가 떠 있다는 사실과 운영 가능하다는 사실은 다릅니다. 파드가 실행 중이어도 준비되지 않은 상태로 트래픽을 받을 수 있고, 로그가 쌓여도 누가 볼 수 있는지 정리가 안 돼 있을 수 있으며, 장애가 나도 대응 절차가 없으면 복구는 매번 사람 기억에 의존하게 됩니다.

이 글은 Kubernetes 101 시리즈의 마지막 글입니다.

여기서는 Kubernetes 운영을 기능 목록이 아니라 probes, 접근 권한, 네트워크 경계, 관측성, GitOps, 런북이 함께 맞물려야 성립하는 운영 모델로 정리하겠습니다.

## 먼저 던지는 질문

- liveness, readiness, startup probe는 어떤 역할을 나눌까요?
- RBAC와 NetworkPolicy는 왜 운영의 기본 경계일까요?
- 메트릭, 로그, 트레이스는 왜 함께 봐야 할까요?

## 큰 그림

![Kubernetes 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/kubernetes-101/10/10-01-concept-at-a-glance.ko.png)

*Kubernetes 101 10장 흐름 개요*

## 왜 중요한가

애플리케이션이 기능적으로 동작하는 것과, 야간에도 문제 없이 유지되는 것은 전혀 다른 수준의 이야기입니다. 운영성이 부족하면 장애가 났을 때 원인을 찾는 시간보다 추측하는 시간이 더 길어집니다.

Kubernetes는 많은 자동화를 제공하지만, 운영 감각까지 자동으로 주지는 않습니다. probe를 어떻게 나눌지, 권한을 어디까지 열지, 어떤 지표를 모으고 어떤 절차로 배포를 되돌릴지까지 정해야 비로소 신뢰할 수 있는 서비스가 됩니다.

## 한눈에 보는 구조

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

## 운영 런북: 탐지-완화-복구-회고

운영 관점의 Kubernetes는 명령어 숙련도보다 의사결정 순서가 더 중요합니다. 장애 대응은 네 단계로 고정하는 것이 좋습니다.

1. **탐지**: 알림 신호와 영향 범위를 수치로 확인
2. **완화**: 롤백, 트래픽 우회, replica 확장으로 즉시 영향 축소
3. **복구**: 근본 원인 제거 후 정상 상태 수렴 확인
4. **회고**: 재발 방지 항목을 매니페스트/런북으로 반영

```bash
kubectl get deploy,po,svc,ing -n prod
kubectl get events -n prod --sort-by=.metadata.creationTimestamp
kubectl rollout undo deploy/api -n prod
kubectl scale deploy/api -n prod --replicas=6
```

## SLO와 자원 정책을 연결하기

가용성 목표(SLO)를 정했다면 리소스 정책과 연결해야 합니다. 예를 들어 99.9% 목표라면 단일 replica, 무제한 eviction 허용, probe 미설정 상태로는 목표를 유지하기 어렵습니다. SLO는 문서가 아니라 매니페스트 필드로 구현되어야 합니다.

```yaml
spec:
  minReadySeconds: 10
  template:
    spec:
      containers:
        - name: api
          resources:
            requests:
              cpu: "300m"
              memory: "384Mi"
            limits:
              cpu: "900m"
              memory: "1Gi"
```

## 온콜 인수인계를 위한 최소 산출물

- 최근 7일 장애 타임라인과 조치 결과
- 서비스별 "먼저 볼 명령" 5개
- 롤백 기준 버전과 금지 변경 목록
- Secret 교체 일정과 담당자

기술 부채는 코드보다 운영 문서에서 먼저 보입니다. Kubernetes를 오래 안정적으로 쓰려면, 매니페스트와 런북을 같은 수준으로 관리해야 합니다.

## 운영 시뮬레이션 확장

운영 체계 관점의 문서를 읽고 끝내면 실제 운영에서 금방 잊힙니다. 그래서 학습 직후에 "장애를 일부러 만들어 보고 복구하는" 시뮬레이션을 반드시 권장합니다. 여기서 중요한 점은 성공 데모를 반복하는 것이 아니라, 실패 신호를 표준 절차로 읽는 훈련을 하는 것입니다. 팀이 성장할수록 기술 격차보다 절차 격차가 더 큰 장애를 만듭니다.

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

- **liveness, readiness, startup probe는 어떤 역할을 나눌까요?**
  - 본문의 기준은 운영 관점의 Kubernetes를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **RBAC와 NetworkPolicy는 왜 운영의 기본 경계일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **메트릭, 로그, 트레이스는 왜 함께 봐야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Kubernetes 101 (1/10): Kubernetes란 무엇인가?](./01-what-is-kubernetes.md)
- [Kubernetes 101 (2/10): Pod](./02-pod.md)
- [Kubernetes 101 (3/10): Deployment](./03-deployment.md)
- [Kubernetes 101 (4/10): Service](./04-service.md)
- [Kubernetes 101 (5/10): Ingress](./05-ingress.md)
- [Kubernetes 101 (6/10): ConfigMap과 Secret](./06-configmap-and-secret.md)
- [Kubernetes 101 (7/10): Volume](./07-volume.md)
- [Kubernetes 101 (8/10): HPA](./08-hpa.md)
- [Kubernetes 101 (9/10): Helm](./09-helm.md)
- **운영 관점의 Kubernetes (현재 글)**

<!-- toc:end -->

## 참고 자료

- [Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- [RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
- [NetworkPolicy](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
- [Argo CD](https://argo-cd.readthedocs.io/)
- [kubectl auth can-i](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_auth/kubectl_auth_can-i/)

- [Kubernetes 101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/kubernetes-101/ko)

Tags: Kubernetes, SRE, Observability, GitOps, DevOps
