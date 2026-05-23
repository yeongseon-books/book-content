---
series: kubernetes-101
episode: 2
title: "Kubernetes 101 (2/10): Pod"
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
  - Pod
  - Containers
  - YAML
  - DevOps
seo_description: 쿠버네티스 최소 배포 단위인 Pod를 컨테이너와 비교 정의하고, 사이드카 패턴과 네트워크 공유, 수명 주기를 통해 Pod의 구조를 이해합니다.
last_reviewed: '2026-05-15'
---

# Kubernetes 101 (2/10): Pod

Kubernetes를 처음 배우면 가장 먼저 헷갈리는 지점이 있습니다. 컨테이너를 실행하는 플랫폼이라면서 왜 가장 작은 단위가 컨테이너가 아니라 Pod인지입니다. Docker를 먼저 익힌 사람일수록 이 질문이 더 자연스럽습니다.

이 글은 Kubernetes 101 시리즈의 2번째 글입니다.

여기서는 Pod를 단순히 "컨테이너 하나를 싸는 껍데기"로 보지 않고, 함께 뜨고 함께 내려가며 네트워크와 볼륨을 공유하는 실행 묶음이라는 관점에서 정리하겠습니다.


![Kubernetes 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/kubernetes-101/02/02-01-concept-at-a-glance.ko.png)
*Kubernetes 101 2장 흐름 개요*

## 먼저 던지는 질문

- Pod와 컨테이너는 정확히 어떻게 다를까요?
- 왜 Kubernetes는 컨테이너가 아니라 Pod를 기본 단위로 삼을까요?
- 사이드카 패턴은 어떤 상황에서 필요할까요?

## 왜 중요한가

모든 워크로드는 결국 Pod 위에서 실행됩니다. Deployment를 쓰든 StatefulSet을 쓰든, 마지막에 실제로 스케줄되는 것은 Pod입니다. 그래서 Pod 모델을 이해하지 못하면 뒤에 나오는 상위 객체도 이름만 다르게 보일 뿐입니다.

특히 입문 단계에서는 "컨테이너가 하나면 Pod도 하나"라는 식으로 단순화해서 외우기 쉽습니다. 물론 그런 경우가 많기는 합니다. 하지만 그 정도로만 이해하면 사이드카, init container, 공유 볼륨, 임시 IP 같은 중요한 운영 포인트를 놓치게 됩니다.

## 한눈에 보는 구조

이 구조에서 핵심은 Pod 안의 컨테이너가 완전히 독립적이지 않다는 점입니다. 같은 Pod에 들어간 컨테이너는 네트워크 네임스페이스와 볼륨을 공유합니다. 그래서 하나의 애플리케이션 본체와 그 옆에서 돕는 보조 컨테이너를 함께 묶는 패턴이 자연스럽게 나옵니다.

## 핵심 용어

- Pod: 하나 이상의 컨테이너가 공유된 환경에서 함께 실행되는 묶음입니다.
- 사이드카: 주 컨테이너 옆에서 로그 수집, 프록시, 동기화 같은 보조 역할을 하는 컨테이너입니다.
- init container: 애플리케이션 시작 전에 한 번 실행되는 컨테이너입니다.
- 수명 주기: Pending에서 Running으로 가고, 끝나면 Succeeded 또는 Failed로 마무리되는 흐름입니다.
- 일시성: Pod는 죽은 뒤 같은 개체가 다시 살아나는 방식이 아니라 새로 만들어지는 방식에 가깝습니다.

## 도입 전과 후

컨테이너를 개별 단위로만 바라보면 리소스를 공유해야 하는 구조를 매번 사람이 직접 설계해야 합니다. 로그 프록시, 보안 에이전트, 보조 프로세스를 어떻게 함께 배치할지 일관된 기준을 잡기도 어렵습니다.

Pod 모델을 받아들이면 이야기가 단순해집니다. 함께 살아야 하는 컨테이너를 한 Pod에 두고, 네트워크와 볼륨을 자연스럽게 공유하도록 만들 수 있습니다. Kubernetes가 왜 컨테이너보다 Pod를 먼저 보는지 이해되는 지점입니다.

## 단계별로 Pod YAML 다뤄 보기

### 1단계 — Pod 매니페스트 작성

```python
"""
apiVersion: v1
kind: Pod
metadata:
  name: web
spec:
  containers:
  - name: app
    image: nginx:1.25
    ports: [{containerPort: 80}]
"""
```

가장 작은 형태의 Pod입니다. 여기서는 컨테이너가 하나뿐이지만, `containers`가 배열이라는 사실이 중요합니다. Kubernetes는 처음부터 "하나 이상"을 전제로 설계돼 있습니다.

### 2단계 — 적용

```python
import subprocess

def apply(path):
    subprocess.run(["kubectl", "apply", "-f", path], check=True)
```

Pod를 직접 적용하는 과정은 학습용으로는 좋습니다. 다만 실무에서는 이 단계에서 끝나지 않고, 보통 Deployment 같은 상위 객체가 Pod 생성을 대신 맡습니다.

### 3단계 — 상세 상태 확인

```python
def describe(name):
    res = subprocess.run(
        ["kubectl", "describe", "pod", name],
        capture_output=True, text=True, check=True,
    )
    return res.stdout
```

`describe`는 Pod를 처음 배울 때 가장 유용한 명령 중 하나입니다. 스케줄링 이벤트, 이미지 풀 상태, 컨테이너 시작 여부까지 함께 보여 주기 때문입니다. 단순히 떴는지 아닌지만 볼 때보다 훨씬 많은 정보를 읽을 수 있습니다.

### 4단계 — 로그 확인

```python
def logs(name):
    res = subprocess.run(
        ["kubectl", "logs", name],
        capture_output=True, text=True, check=True,
    )
    return res.stdout
```

Pod 안의 컨테이너 로그는 기본적으로 표준 출력으로 보는 흐름이 중요합니다. 컨테이너 안에 직접 들어가 로그 파일을 뒤지는 방식은 Kubernetes의 기본 운영 모델과 잘 맞지 않습니다.

### 5단계 — 삭제

```python
def delete(name):
    subprocess.run(["kubectl", "delete", "pod", name], check=True)
```

직접 만든 Pod는 지우면 끝입니다. 다시 살아나지 않습니다. 이 지점이 바로 "Pod를 직접 만들지 말라"는 조언의 핵심과 이어집니다. 자동 복구와 재시작은 Pod 자체가 아니라 상위 컨트롤러의 책임입니다.

## 검증 흐름

```bash
kubectl get pod web -o wide
kubectl describe pod web
kubectl logs web
```

**예상되는 결과:** `get pod`에서는 `Running` 또는 준비 직전 상태가 보여야 하고, `describe`에서는 이미지 풀·스케줄링·컨테이너 시작 이벤트가 시간순으로 보여야 합니다. 로그는 애플리케이션이 표준 출력으로 남긴 초기화 메시지를 확인하는 용도로 읽습니다.

**먼저 의심할 실패 모드:**

- `Pending`이 길면 이미지가 아니라 스케줄링 자원 부족이나 taint를 먼저 봅니다.
- `ImagePullBackOff`면 YAML 문법보다 레지스트리 인증과 이미지 태그를 우선 확인합니다.
- 로그가 비어 있으면 애플리케이션이 파일 로그만 쓰는지, 혹은 컨테이너가 시작 직후 죽는지 나눠서 봐야 합니다.

## 이 코드에서 먼저 봐야 할 점

- Pod 이름은 고유해야 합니다.
- `containers`는 배열이므로 하나 이상의 컨테이너를 둘 수 있습니다.
- 직접 만든 Pod는 학습용으로는 괜찮지만 운영 기본값은 아닙니다.

여기서 중요한 감각은 Pod를 애플리케이션 인스턴스 자체로 보는 것이 아니라, 상위 객체가 만들고 교체하는 실행 단위로 보는 것입니다. 이 관점을 잡아야 Deployment가 왜 필요한지 자연스럽게 이어집니다.

## 자주 하는 실수 다섯 가지

1. Pod를 컨테이너 하나와 완전히 같은 뜻으로 이해합니다.
2. 직접 만든 Pod가 장애 시 자동으로 복구될 것이라고 기대합니다.
3. Pod IP가 안정적으로 유지된다고 가정합니다.
4. 함께 붙어 있어야 할 컨테이너를 억지로 분리해 공유 이점을 잃습니다.
5. 로그를 컨테이너 내부 파일 기준으로만 보려 합니다.

## 실무에서는 이렇게 봅니다

실무에서는 로그 수집기, 프록시, 비밀 동기화기 같은 보조 컨테이너를 사이드카 형태로 붙이는 경우가 많습니다. 이때 Pod는 단순 배포 단위가 아니라 결합 경계를 결정하는 도구가 됩니다.

시니어 엔지니어는 Pod를 볼 때 "무엇이 함께 살아야 하는가"를 먼저 생각합니다. 동시에 사이드카는 편리한 도구이면서 결합 비용이기도 하다는 점도 함께 봅니다. 너무 쉽게 같은 Pod에 넣으면 배포와 스케일링 단위까지 함께 묶이기 때문입니다.

## 체크리스트

- [ ] Pod 직접 생성은 학습이나 디버깅 상황으로 한정했는가
- [ ] 사이드카가 정말 같은 수명 주기를 가져야 하는가
- [ ] 로그가 표준 출력으로 나가도록 구성했는가
- [ ] Pod 수명 주기를 상위 객체와 함께 이해하고 있는가

## 연습 문제

1. Pod와 컨테이너의 차이를 한 줄로 설명해 보세요.
2. 사이드카의 실제 예시를 하나 적어 보세요.
3. 왜 직접 Pod를 만들고 운영 기본값으로 삼으면 안 되는지 한 줄로 정리해 보세요.

## 마무리와 다음 글

이 글에서는 Pod를 Kubernetes의 최소 실행 단위로 정리했습니다. 컨테이너 하나와 비슷해 보일 때도 있지만, 실제로는 여러 컨테이너가 네트워크와 볼륨을 공유하며 함께 수명을 가지는 묶음이라는 점이 핵심입니다.

다음 글에서는 이 Pod를 사람이 직접 관리하지 않고, 원하는 개수를 유지하고 롤링 업데이트까지 맡는 Deployment를 보겠습니다.


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


## 운영 관찰 지표 추가

클러스터 상태를 확인할 때 단순 성공 여부만 보지 말고 재시작 횟수, 스케줄링 지연, 이미지 풀 시간 같은 신호를 함께 봐야 합니다. `kubectl get pod -A -o wide`와 `kubectl top pod -A`를 주기적으로 확인하면 자원 부족으로 인한 지연을 조기에 발견할 수 있습니다. 또한 배포 직후 `kubectl rollout status`와 `kubectl get events`를 묶어 실행하면 문제를 애플리케이션 로그로만 좁혀 보는 실수를 줄일 수 있습니다.

```bash
kubectl get pod -A -o wide
kubectl top pod -A
kubectl rollout status deploy/<name> -n <ns>
```

운영 문서에는 위 명령의 기대 출력과 비정상 패턴을 함께 기록해 두는 편이 대응 품질을 높입니다.

## Pod 스펙을 운영 관점으로 읽는 법

Pod는 단순 실행 단위가 아니라 운영 계약서입니다. 특히 `securityContext`, `resources`, `probe`, `terminationGracePeriodSeconds`는 장애 시 행동을 좌우하므로 반드시 명시해야 합니다. 빠르게 배포하는 것보다, 실패했을 때 예측 가능한 방식으로 실패하게 만드는 쪽이 중요합니다.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: api-pod
  labels:
    app: api
spec:
  terminationGracePeriodSeconds: 30
  containers:
    - name: api
      image: ghcr.io/example/api:1.3.1
      ports:
        - containerPort: 8000
      resources:
        requests:
          cpu: "200m"
          memory: "256Mi"
        limits:
          cpu: "500m"
          memory: "512Mi"
      livenessProbe:
        httpGet:
          path: /livez
          port: 8000
      readinessProbe:
        httpGet:
          path: /readyz
          port: 8000
```

## 디버깅 워크플로: Pending, CrashLoopBackOff, OOMKilled

Pod 장애는 상태 문자열만 봐도 초동 대응이 가능합니다. `Pending`이면 스케줄링 조건을, `CrashLoopBackOff`면 시작 명령과 의존성, `OOMKilled`면 메모리 한계를 먼저 봐야 합니다.

```bash
kubectl get pod api-pod -n prod -o wide
kubectl describe pod api-pod -n prod
kubectl logs api-pod -n prod --previous
kubectl top pod api-pod -n prod
```

`describe`의 Events는 원인 분리를 빠르게 해 줍니다. 이미지 pull 실패인지, 노드 자원 부족인지, probe 실패인지 먼저 구분하고 로그를 읽어야 시간을 아낄 수 있습니다.

## Pod 레벨 운영 수칙

1. 단일 Pod를 장기 운영 단위로 쓰지 않고, Deployment 같은 상위 컨트롤러로 감쌉니다.
2. `latest` 태그를 금지하고 버전 고정 태그를 사용합니다.
3. 종료 훅과 grace period를 설정해 롤링 업데이트 중 연결 끊김을 줄입니다.
4. 디버깅용 `kubectl exec`는 임시 조치로만 사용하고, 원인은 매니페스트로 반영합니다.

Pod를 잘 설계하면 나중에 Deployment, HPA, PDB를 붙일 때 추가 비용이 크게 줄어듭니다.

## 운영 시뮬레이션 확장

Pod 관점의 문서를 읽고 끝내면 실제 운영에서 금방 잊힙니다. 그래서 학습 직후에 "장애를 일부러 만들어 보고 복구하는" 시뮬레이션을 반드시 권장합니다. 여기서 중요한 점은 성공 데모를 반복하는 것이 아니라, 실패 신호를 표준 절차로 읽는 훈련을 하는 것입니다. 팀이 성장할수록 기술 격차보다 절차 격차가 더 큰 장애를 만듭니다.

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

## 처음 질문으로 돌아가기

- **Pod와 컨테이너는 정확히 어떻게 다를까요?**
  - 컨테이너가 격리된 프로세스 단위라면, Pod는 그런 컨테이너 하나 이상이 같은 네트워크 네임스페이스와 볼륨을 공유하며 함께 뜨고 함께 내려가는 묶음입니다. 본문 1단계 YAML에서 `containers`가 배열로 정의된 점이 이 차이를 가장 잘 보여 줍니다.
- **왜 Kubernetes는 컨테이너가 아니라 Pod를 기본 단위로 삼을까요?**
  - 로그 수집기, 프록시, 비밀 동기화기처럼 본체와 같은 수명 주기를 가져야 하는 보조 프로세스를 자연스럽게 묶어야 하기 때문입니다. 본문에서 본 것처럼 컨테이너만 단위로 두면 결합 경계와 공유 자원을 매번 사람이 직접 설계해야 합니다.
- **사이드카 패턴은 어떤 상황에서 필요할까요?**
  - 주 컨테이너 옆에서 로그 수집·프록시·동기화 같은 보조 역할이 필요하고, 그 역할이 본체와 같은 시점에 시작·종료돼야 할 때입니다. 본문은 동시에 같은 Pod에 넣으면 배포·스케일링 단위까지 함께 묶이는 결합 비용이 생긴다는 점도 함께 강조했습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Kubernetes 101 (1/10): Kubernetes란 무엇인가?](./01-what-is-kubernetes.md)
- **Pod (현재 글)**
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

- [Pods (Kubernetes)](https://kubernetes.io/docs/concepts/workloads/pods/)
- [Pod lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)
- [Init containers](https://kubernetes.io/docs/concepts/workloads/pods/init-containers/)
- [Sidecar containers](https://kubernetes.io/blog/2023/08/25/native-sidecar-containers/)
- [Debug Pods](https://kubernetes.io/docs/tasks/debug/debug-application/debug-pods/)

- [Kubernetes 101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/kubernetes-101/ko)

Tags: Kubernetes, Pod, Containers, YAML, DevOps
