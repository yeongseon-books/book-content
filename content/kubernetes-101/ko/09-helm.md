---
series: kubernetes-101
episode: 9
title: "Kubernetes 101 (9/10): Helm"
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
  - Helm
  - Chart
  - PackageManager
  - DevOps
seo_description: Helm의 차트와 values 분리, 릴리스 관리, 롤백 전략을 학습해 쿠버네티스 배포 체계를 반복 가능하게 관리하는 실무 방법을 정리합니다.
last_reviewed: '2026-05-15'
---

# Kubernetes 101 (9/10): Helm

Kubernetes를 실제로 쓰기 시작하면 YAML이 빠르게 늘어납니다. 개발, 스테이징, 운영 환경이 갈라지고, 이미지 태그와 replica 수, 서비스 타입이 조금씩 달라지면 복사한 매니페스트가 금방 쌓입니다. 시간이 지나면 어떤 파일이 기준인지조차 흐려지기 쉽습니다.

이 글은 Kubernetes 101 시리즈의 9번째 글입니다.

여기서는 Helm을 단순한 패키지 매니저가 아니라, 공통 템플릿과 환경별 값을 분리해 Kubernetes 배포를 반복 가능하게 만드는 배포 단위라는 관점에서 정리하겠습니다.

## 먼저 던지는 질문

- 환경마다 YAML을 복사하는 방식은 왜 드리프트를 만들까요?
- Chart와 `values.yaml`은 어떤 책임을 나눌까요?
- `install`, `upgrade`, `rollback`은 어떤 흐름으로 이어질까요?

## 큰 그림

![Kubernetes 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/kubernetes-101/09/09-01-concept-at-a-glance.ko.png)

*Kubernetes 101 9장 흐름 개요*

## 왜 중요한가

환경별 사본이 늘어나면 작은 수정 하나도 여러 파일에 반복 반영해야 합니다. 어느 환경 파일이 최신인지, 어떤 차이가 의도된 것인지도 시간이 갈수록 흐려집니다. 이 상태가 바로 배포 드리프트입니다.

Helm은 같은 구조를 반복 사용할 때 차이는 값으로만 드러나게 만듭니다. 입문 단계에서는 편한 템플릿 도구처럼 보일 수 있지만, 실무에서는 배포 단위를 어떻게 표준화할지와 직접 연결됩니다.

## 한눈에 보는 구조

Helm은 값을 받아 템플릿을 렌더링하고, 그 결과를 Kubernetes API에 적용합니다. 그래서 Helm을 이해할 때는 결과 YAML과 입력 값, 그리고 공통 템플릿의 책임을 분리해서 보는 편이 좋습니다.

## 핵심 용어

- 차트: Helm의 패키지 단위입니다.
- `values.yaml`: 기본값을 담는 파일입니다.
- 릴리스: 차트가 실제로 설치된 인스턴스입니다.
- 저장소: 차트를 배포하고 받는 유통 채널입니다.
- 의존성: 하위 차트를 포함하는 관계입니다.

## 도입 전과 후

Helm이 없으면 개발, 스테이징, 운영별 YAML 사본이 따로 생기기 쉽습니다. 처음에는 단순하지만, 시간이 지나면 공통 구조와 환경 차이가 뒤섞입니다.

Helm을 도입하면 공통 구조는 차트에 두고, 환경별 차이는 values로만 관리할 수 있습니다. 배포 반복성이 좋아지고, 어떤 값이 어디서 달라지는지도 훨씬 선명해집니다.

## 단계별로 작은 차트 만들어 보기

### 1단계 — 차트 생성

```python
import subprocess

def create(name):
    subprocess.run(["helm", "create", name], check=True)
```

Helm은 기본 차트 구조를 빠르게 만들어 줍니다. 물론 생성 직후 템플릿이 그대로 운영 품질이라는 뜻은 아니고, 공통 구조를 어떤 기준으로 다듬을지가 더 중요합니다.

### 2단계 — `values.yaml` 작성

```python
"""
replicaCount: 2
image:
  repository: myorg/app
  tag: "1.0"
service:
  type: ClusterIP
  port: 80
"""
```

여기에는 환경에 따라 달라질 수 있는 값이 들어갑니다. 반대로 배포 구조 자체는 차트 템플릿에 남겨 두는 편이 좋습니다.

### 3단계 — 설치

```python
def install(release, chart, values):
    subprocess.run(
        ["helm", "install", release, chart, "-f", values],
        check=True,
    )
```

릴리스는 같은 차트를 실제로 설치한 인스턴스입니다. 이 개념을 이해해야 Helm이 템플릿 저장소가 아니라 배포 단위라는 사실이 보입니다.

### 4단계 — 업그레이드

```python
def upgrade(release, chart, values):
    subprocess.run(
        ["helm", "upgrade", release, chart, "-f", values, "--atomic"],
        check=True,
    )
```

`--atomic`은 실패 시 자동 롤백을 함께 수행합니다. 야간 배포에서 특히 의미가 큰 옵션입니다. 업그레이드가 끝나지 않았는데도 릴리스 상태를 정상처럼 남겨 두는 일을 줄여 줍니다.

### 5단계 — 롤백

```python
def rollback(release, revision):
    subprocess.run(
        ["helm", "rollback", release, str(revision)],
        check=True,
    )
```

롤백은 Helm을 쓸 때도 여전히 중요합니다. 템플릿과 값이 분리돼 있어도, 실제 운영에서는 이전 정상 상태로 돌아가는 절차를 알고 있어야 복구 속도가 달라집니다.

## 검증 흐름

```bash
helm template web ./chart -f values.yaml
helm lint ./chart
helm history web
```

**예상되는 결과:** `helm template` 출력은 실제로 적용될 YAML 구조를 보여 주고, `helm lint`는 차트 문법과 기본 규칙을 먼저 걸러 줍니다. 이미 설치한 릴리스라면 `helm history`에서 revision이 쌓이는지 확인해 rollback 가능한 상태인지 판단할 수 있습니다.

**먼저 의심할 실패 모드:**

- template 결과가 이미 이상하면 클러스터 문제가 아니라 values와 템플릿 책임 분리가 깨진 것입니다.
- lint가 통과해도 Secret을 평문 values로 넣었다면 운영 품질 문제는 여전히 남아 있습니다.
- rollback이 안 되면 Helm 자체보다 release history가 남도록 설치·업그레이드 절차를 점검해야 합니다.

## 이 코드에서 먼저 봐야 할 점

- `--atomic`은 실패 시 자동 롤백을 수행합니다.
- `helm template`으로 렌더 결과를 적용 전에 볼 수 있습니다.
- 환경별 차이는 values에 두고 차트는 공유해야 합니다.

이 세 가지를 같이 잡아 두면 Helm을 단순 생성기처럼 쓰지 않게 됩니다. Helm의 가치는 템플릿 재사용과 배포 복구 흐름을 함께 묶는 데 있습니다.

## 자주 하는 실수 다섯 가지

1. values와 차트 책임을 같은 파일에 섞습니다.
2. Secret 값을 values에 평문으로 넣습니다.
3. 버전 고정 없이 `latest`에 기대어 배포합니다.
4. 롤백 절차를 모른 채 업그레이드만 반복합니다.
5. 의존성 갱신을 잊습니다.

## 실무에서는 이렇게 봅니다

실무에서는 GitOps와 Helm을 함께 써서 values 변경만으로 배포가 이뤄지는 흐름을 자주 만듭니다. 이때 차트는 공통 계약이 되고, 환경별 values는 운영 차이를 담는 얇은 레이어가 됩니다.

시니어 엔지니어는 Helm을 쓸 때 values에 무엇을 넣지 않을지도 같이 정합니다. 민감한 값은 외부 비밀 관리 시스템으로 넘기고, 차트에는 구조만 남겨 두는 편이 장기적으로 훨씬 안정적입니다.

## 체크리스트

- [ ] 차트와 values 책임을 분리했는가
- [ ] 버전을 고정했는가
- [ ] `--atomic` 사용 여부를 검토했는가
- [ ] Secret 처리를 외부화했는가

## 연습 문제

1. `helm template`의 목적을 한 줄로 설명해 보세요.
2. values와 차트의 책임 차이를 한 줄로 적어 보세요.
3. `--atomic`이 왜 더 안전한지 한 줄로 정리해 보세요.

## 마무리와 다음 글

이 글에서는 Helm을 공통 배포 구조와 환경별 차이를 분리하는 도구로 정리했습니다. 차트는 공유되는 계약이고, values는 환경별 차이를 담는 입력값이라는 감각을 잡아 두면 YAML 복사본이 빠르게 줄어듭니다.

다음 글에서는 시리즈를 마무리하며, 실제 운영 관점에서 probes, RBAC, 관측성, GitOps를 어떻게 함께 봐야 하는지 정리하겠습니다.


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

## kubectl 운영 명령 세트

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

## 처음 질문으로 돌아가기

- **환경마다 YAML을 복사하는 방식은 왜 드리프트를 만들까요?**
  - 본문의 기준은 Helm를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **Chart와 `values.yaml`은 어떤 책임을 나눌까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **`install`, `upgrade`, `rollback`은 어떤 흐름으로 이어질까요?**
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
- **Helm (현재 글)**
- 운영 관점의 Kubernetes (예정)

<!-- toc:end -->

## 참고 자료

- [Helm official docs](https://helm.sh/docs/)
- [Chart structure](https://helm.sh/docs/topics/charts/)
- [Helm best practices](https://helm.sh/docs/chart_best_practices/)
- [Artifact Hub](https://artifacthub.io/)
- [helm lint](https://helm.sh/docs/helm/helm_lint/)

Tags: Kubernetes, Helm, Chart, PackageManager, DevOps
