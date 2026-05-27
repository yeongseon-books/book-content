---
series: kubernetes-101
episode: 8
title: "Kubernetes 101 (8/10): HPA"
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
  - HPA
  - Autoscaling
  - Metrics
  - DevOps
seo_description: HPA와 metrics-server, 요청량 기반 파드 자동 조절의 기본을 설명합니다.
last_reviewed: '2026-05-15'
---

# Kubernetes 101 (8/10): HPA

트래픽은 하루 종일 일정하지 않습니다. 어떤 시간에는 요청이 몰리고, 어떤 시간에는 거의 비어 있습니다. 이런 변화를 운영자가 수동으로 따라가면 대응은 늘 늦고, 넉넉하게 파드를 띄워 두면 비용이 계속 낭비됩니다.

이 글은 Kubernetes 101 시리즈의 8번째 글입니다.

여기서는 HPA를 단순히 CPU가 높으면 파드를 늘리는 기능이 아니라, 메트릭을 기준으로 Deployment의 원하는 개수를 자동 조절하는 운영 자동화 계층이라는 관점에서 정리하겠습니다.

![Kubernetes 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/kubernetes-101/08/08-01-concept-at-a-glance.ko.png)
*Kubernetes 101 8장 흐름 개요*

> HPA는 'CPU 높으면 파드 늘리는 기능'이 아니라 '메트릭을 입력으로 Deployment의 desired replicas를 조절하는 컨트롤러 루프'입니다 — 어떤 메트릭을 보느냐, 어떻게 안정화하느냐, 무엇을 최대로 두느냐가 자동화의 안정성을 결정합니다.

## 먼저 던지는 질문

- 트래픽이 바뀔 때마다 사람이 직접 파드 수를 조절하면 왜 느리고 비싸질까요?
- HPA는 어떤 지표를 보고 스케일 아웃과 스케일 인을 결정할까요?
- resource requests가 없으면 왜 제대로 동작하지 않을까요?

## 왜 중요한가

수동 스케일링은 거의 항상 한 박자 늦습니다. 이미 응답 시간이 나빠진 뒤에 파드를 늘리거나, 한가한 시간에도 그대로 둬서 비용을 낭비하기 쉽습니다. 운영자가 직접 숫자를 바꾸는 방식은 규모가 커질수록 더 취약해집니다.

HPA는 이 문제를 메트릭 기반 자동화로 줄입니다. 다만 자동화라고 해서 무조건 똑똑한 것은 아닙니다. 기준 지표가 부정확하면 엉뚱한 결정을 내릴 수 있고, 파드를 늘려도 노드가 부족하면 실제 스케일은 진행되지 않습니다. 그래서 HPA는 메트릭과 클러스터 용량을 함께 봐야 합니다.

## 한눈에 보는 구조

HPA는 파드를 직접 만들고 지우기보다 Deployment의 원하는 개수를 조정합니다. 즉, 자동 스케일링의 판단 계층이라고 보는 편이 더 정확합니다. 뒤의 실제 파드 생성과 유지 작업은 여전히 Deployment가 맡습니다.

## 핵심 용어

- HPA: 파드 개수를 자동으로 조절하는 오토스케일러입니다.
- metrics-server: CPU, 메모리 같은 기본 메트릭을 수집하는 구성요소입니다.
- 목표 사용률: requests 대비 목표 CPU 또는 메모리 비율입니다.
- 커스텀 메트릭: 큐 길이, 요청 수 같은 외부 지표입니다.
- VPA: 파드 수가 아니라 파드 하나의 자원 요청값을 조절하는 도구입니다.

## 도입 전과 후

HPA가 없으면 피크 시간에는 503이 늘어나고, 한가한 시간에는 파드가 과하게 떠 있을 수 있습니다. 운영자는 트래픽 패턴을 보고 수동으로 replicas를 바꿔야 합니다.

HPA를 두면 현재 부하에 맞춰 파드 수를 자동으로 조절할 수 있습니다. 물론 자동화의 핵심은 기능 자체보다 기준값과 한계값을 어떻게 잡느냐에 있습니다. 최소 개수, 최대 개수, 메트릭 품질이 함께 맞아야 기대한 효과가 납니다.

## 단계별로 CPU 기반 HPA 구성하기

### 1단계 — Deployment에 자원 요청 설정

```python
"""
spec:
  template:
    spec:
      containers:
      - name: app
        image: myorg/app:1.0
        resources:
          requests: {cpu: 200m, memory: 256Mi}
"""
```

HPA가 CPU 사용률을 계산하려면 기준점이 필요합니다. 그 기준이 바로 requests입니다. requests가 없으면 사용률 비율을 계산할 수 없어서 자동화가 기대한 대로 움직이지 않습니다.

### 2단계 — HPA 매니페스트 작성

```python
"""
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata: {name: web}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target: {type: Utilization, averageUtilization: 60}
"""
```

이 설정은 평균 CPU 사용률이 requests 대비 60% 수준을 유지하도록 파드 수를 조절합니다. `minReplicas: 2`는 가용성의 시작점이고, `maxReplicas: 10`은 비용과 용량의 상한선입니다.

### 3단계 — 적용

```python
import subprocess

def apply(path):
    subprocess.run(["kubectl", "apply", "-f", path], check=True)
```

리소스를 적용했다고 끝난 것은 아닙니다. HPA는 메트릭이 실제로 들어오는지 확인해야 비로소 의미가 있습니다. 객체가 있어도 메트릭이 없으면 자동화는 멈춰 있습니다.

### 4단계 — 부하 만들기

```python
def load(target):
    subprocess.run([
        "kubectl", "run", "load", "--rm", "-i", "--restart=Never",
        "--image=busybox", "--", "sh", "-c",
        f"while true; do wget -q -O- {target}; done",
    ], check=False)
```

테스트 부하를 만들어 보면 HPA가 실제로 스케일 아웃하는지 확인할 수 있습니다. 기준값을 검증하지 않고 운영에 바로 넣으면 너무 늦거나 너무 민감한 자동화가 오래 남기 쉽습니다.

### 5단계 — HPA 상태 확인

```python
def hpa_status(name):
    res = subprocess.run(
        ["kubectl", "get", "hpa", name, "-o", "wide"],
        capture_output=True, text=True, check=True,
    )
    return res.stdout
```

현재 메트릭, 목표값, 최소·최대 replicas, 실제 replicas를 함께 봐야 합니다. HPA는 숫자를 자동으로 바꾸는 기능이므로 상태 조회가 곧 디버깅의 출발점입니다.

## 검증 흐름

```bash
kubectl top pods
kubectl get hpa web -w
kubectl describe hpa web
```

**예상되는 결과:** `top` 명령이 CPU와 메모리 값을 반환해야 HPA가 읽을 메트릭이 존재한다는 뜻입니다. `get hpa -w`에서는 부하에 따라 current/target 비율과 replicas 수가 움직여야 하고, `describe`에서는 최근 scale event와 조건을 읽을 수 있어야 합니다.

**먼저 의심할 실패 모드:**

- `top pods` 자체가 비어 있거나 실패하면 HPA YAML보다 metrics-server부터 확인해야 합니다.
- HPA는 늘리려 하는데 Pod가 안 뜨면 노드 용량 부족이나 Cluster Autoscaler 부재가 더 큰 원인입니다.
- scale in/out이 계속 흔들리면 target 값보다 requests 크기와 부하 패턴을 먼저 다시 봅니다.

## 이 코드에서 먼저 봐야 할 점

- requests가 없으면 HPA는 계산 기준을 잃습니다.
- `averageUtilization`은 절대값이 아니라 requests 대비 비율입니다.
- `minReplicas >= 2`는 고가용성의 시작점입니다.

이 세 가지를 놓치면 HPA를 켰는데도 왜 반응하지 않는지, 혹은 왜 과하게 반응하는지 이해하기 어렵습니다. 자동화는 숫자를 어떻게 읽는지부터 봐야 합니다.

## 자주 하는 실수 다섯 가지

1. requests를 설정하지 않아 메트릭 계산이 꼬입니다.
2. `maxReplicas`를 너무 낮게 잡아 피크 트래픽을 못 받습니다.
3. 기본 메트릭 검증도 없이 커스텀 지표부터 붙입니다.
4. 노드 한계를 보지 않아 HPA가 늘리려 해도 파드가 뜨지 않습니다.
5. 플래핑을 방치해 비용과 안정성을 함께 잃습니다.

## 실무에서는 이렇게 봅니다

실무에서는 HPA와 Cluster Autoscaler를 함께 둬서 파드 증가가 노드 증가로 이어지게 만드는 경우가 많습니다. 파드를 늘리고 싶어도 노드 자리가 없으면 자동화의 절반만 동작하는 셈이기 때문입니다.

시니어 엔지니어는 커스텀 메트릭을 처음부터 욕심내지 않습니다. CPU와 메모리처럼 이해하기 쉬운 기준으로 먼저 안정성을 확인한 뒤, 큐 길이와 요청 수 같은 서비스별 지표로 넓혀 가는 흐름이 더 안전합니다.

## 체크리스트

- [ ] requests를 설정했는가
- [ ] `minReplicas`를 2 이상으로 둘지 검토했는가
- [ ] Cluster Autoscaler와의 조합을 검토했는가
- [ ] 플래핑 여부를 모니터링하고 있는가

## 연습 문제

1. requests가 없으면 HPA가 왜 실패하는지 한 줄로 설명해 보세요.
2. VPA와 HPA의 차이를 한 줄로 정리해 보세요.
3. Cluster Autoscaler의 역할을 한 줄로 적어 보세요.

## 마무리와 다음 글

이 글에서는 HPA를 메트릭 기반으로 Deployment의 replica 수를 자동 조절하는 계층으로 정리했습니다. 자동화의 품질은 requests 설정, 메트릭 신뢰도, 노드 확장 전략에 달려 있다는 점도 함께 봤습니다.

다음 글에서는 이렇게 늘고 줄어드는 워크로드를 더 반복 가능하게 배포하기 위한 패키징 단위, Helm을 보겠습니다.

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

## HPA 지표와 리소스 요청을 함께 설계하기

HPA는 목표 지표만 맞추면 되는 기능이 아닙니다. `requests`가 비어 있으면 CPU 기반 스케일 판단이 왜곡될 수 있습니다. 따라서 HPA 설계는 Deployment 리소스 설정과 한 세트로 봐야 합니다.

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 65
```

## 스케일링 진단 루틴

```bash
kubectl get hpa api -n prod
kubectl describe hpa api -n prod
kubectl top pod -n prod -l app=api
kubectl get deploy api -n prod -o yaml
```

`describe hpa`에서 current/target 값을 먼저 보고, scale up/down 이벤트 시점을 트래픽 변화와 비교하세요. 급격한 진동이 있으면 stabilization window와 cooldown 성격의 조정이 필요합니다.

## 과잉 스케일링을 막는 가드레일

- 최소 replica를 1이 아닌 2 이상으로 시작해 단일 파드 병목을 줄입니다.
- startup이 느린 앱은 readiness 조건을 보수적으로 잡아 premature traffic 유입을 막습니다.
- HPA와 PDB를 함께 설계해 스케일 인 중 가용성 하락을 방지합니다.

HPA는 비용 최적화 도구이면서 동시에 장애 전파를 막는 안전장치입니다.

## 운영 시뮬레이션 확장

HPA 관점의 문서를 읽고 끝내면 실제 운영에서 금방 잊힙니다. 그래서 학습 직후에 "장애를 일부러 만들어 보고 복구하는" 시뮬레이션을 반드시 권장합니다. 여기서 중요한 점은 성공 데모를 반복하는 것이 아니라, 실패 신호를 표준 절차로 읽는 훈련을 하는 것입니다. 팀이 성장할수록 기술 격차보다 절차 격차가 더 큰 장애를 만듭니다.

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

- **트래픽이 바뀔 때마다 사람이 직접 파드 수를 조절하면 왜 느리고 비싸질까요?**
  - 사람이 모니터를 보고 `kubectl scale`을 누르는 방식은 반응이 분 단위로 늦고, 야간·주말에는 아예 빈자리가 생깁니다. 본문에서 본 것처럼 트래픽 급증 5분 동안 응답이 무너지거나, 한가한 시간에 평상시 replica로 그대로 유지되어 비용이 새는 일이 반복되기 쉽습니다.
- **HPA는 어떤 지표를 보고 스케일 아웃과 스케일 인을 결정할까요?**
  - 기본은 metrics-server가 제공하는 CPU·메모리 사용률을 `requests` 대비로 계산해 목표 값과 비교하는 방식이고, 본문 예시처럼 `Resource`·`Pods`·`Object`·`External` 메트릭으로 RPS나 큐 길이까지 확장할 수 있습니다. desired/current 차이가 일정 임계를 넘으면 replica를 조정하고, 진동을 막기 위해 `behavior`로 스케일 인 쿨다운을 둡니다.
- **resource requests가 없으면 왜 제대로 동작하지 않을까요?**
  - HPA는 사용률을 "현재 사용량 ÷ requests"로 계산하므로 requests가 비어 있으면 분모가 사라져 목표 사용률을 가늠할 수 없습니다. 본문에서 강조했듯이 requests 없이 HPA를 켜면 메트릭이 0% 또는 N/A로 떠 스케일링이 아예 일어나지 않거나, 노드 자원 예약이 안 돼 스케일 아웃 자체가 실패합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Kubernetes 101 (1/10): Kubernetes란 무엇인가?](./01-what-is-kubernetes.md)
- [Kubernetes 101 (2/10): Pod](./02-pod.md)
- [Kubernetes 101 (3/10): Deployment](./03-deployment.md)
- [Kubernetes 101 (4/10): Service](./04-service.md)
- [Kubernetes 101 (5/10): Ingress](./05-ingress.md)
- [Kubernetes 101 (6/10): ConfigMap과 Secret](./06-configmap-and-secret.md)
- [Kubernetes 101 (7/10): Volume](./07-volume.md)
- **HPA (현재 글)**
- Helm (예정)
- 운영 관점의 Kubernetes (예정)

<!-- toc:end -->

## 참고 자료

- [HorizontalPodAutoscaler](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [metrics-server](https://github.com/kubernetes-sigs/metrics-server)
- [Cluster Autoscaler](https://github.com/kubernetes/autoscaler/tree/master/cluster-autoscaler)
- [VPA](https://github.com/kubernetes/autoscaler/tree/master/vertical-pod-autoscaler)
- [Walkthrough of autoscaling workloads](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale-walkthrough/)

- [Kubernetes 101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/kubernetes-101/ko)

Tags: Kubernetes, HPA, Autoscaling, Metrics, DevOps
