---
series: kubernetes-101
episode: 6
title: "Kubernetes 101 (6/10): ConfigMap과 Secret"
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
  - ConfigMap
  - Secret
  - Configuration
  - DevOps
seo_description: ConfigMap과 Secret으로 설정과 비밀 값을 분리하는 기본 방식을 설명합니다.
last_reviewed: '2026-05-15'
---

# Kubernetes 101 (6/10): ConfigMap과 Secret

컨테이너 이미지를 처음 만들 때는 설정값과 비밀번호를 같이 넣어도 금방 동작합니다. 하지만 환경이 늘어나고 팀이 커지면 그 방식은 빠르게 한계에 닿습니다. 같은 이미지를 개발과 운영에서 재사용하기 어렵고, 민감한 값이 이미지나 Git에 남는 위험도 커집니다.

이 글은 Kubernetes 101 시리즈의 6번째 글입니다.

여기서는 ConfigMap과 Secret을 단순한 키/값 저장소가 아니라, 이미지를 환경별 차이와 민감한 값에서 분리하기 위한 기본 운영 도구라는 관점에서 정리하겠습니다.


![Kubernetes 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/kubernetes-101/06/06-01-concept-at-a-glance.ko.png)
*Kubernetes 101 6장 흐름 개요*

## 먼저 던지는 질문

- 이미지 안에 설정과 비밀번호를 같이 넣으면 왜 운영이 어려워질까요?
- ConfigMap과 Secret은 무엇이 다르고 어디서 나뉠까요?
- 환경 변수 주입과 파일 마운트는 언제 다르게 선택할까요?

## 왜 중요한가

환경 차이를 이미지 바깥으로 빼야 같은 이미지를 여러 환경에서 재현 가능하게 쓸 수 있습니다. 그래야 개발에서 검증한 이미지를 스테이징과 운영에서도 그대로 올릴 수 있습니다.

민감한 값은 더 엄격하게 다뤄야 합니다. 데이터베이스 비밀번호, API 토큰, 인증서 같은 값이 이미지나 Git에 평문으로 남으면 배포 편의성보다 훨씬 큰 리스크를 떠안게 됩니다. ConfigMap과 Secret을 구분하는 이유는 단순한 기능 차이가 아니라 운영 책임을 나누기 위해서입니다.

## 한눈에 보는 구조

ConfigMap과 Secret은 모두 파드 안으로 들어갈 수 있지만, 같은 방식으로 다뤄도 된다는 뜻은 아닙니다. 주입 방식과 접근 제어, 변경 반영 전략까지 같이 봐야 실제 운영 모델이 완성됩니다.

## 핵심 용어

- ConfigMap: 민감하지 않은 키/값 설정 묶음입니다.
- Secret: 민감한 키/값 설정 묶음입니다.
- `envFrom`: 여러 키를 한 번에 환경 변수로 주입하는 방식입니다.
- 볼륨 마운트: 설정을 파일 형태로 연결하는 방식입니다.
- External Secrets: 외부 비밀 관리 시스템과 클러스터 Secret을 동기화하는 방식입니다.

## 도입 전과 후

이미지 안에 데이터베이스 비밀번호를 넣으면 값을 바꾸려 할 때마다 이미지를 다시 빌드해야 합니다. 환경 차이도 이미지 변형으로 흩어지기 쉽습니다.

ConfigMap과 Secret으로 나누면 이미지는 환경에 덜 묶이고, 값은 배포 시점에 주입할 수 있습니다. 운영에서는 이 차이가 매우 큽니다. 이미지 재사용성과 비밀 값 관리가 동시에 좋아지기 때문입니다.

## 단계별로 설정과 비밀 값 분리하기

### 1단계 — ConfigMap 작성

```python
"""
apiVersion: v1
kind: ConfigMap
metadata: {name: app-config}
data:
  LOG_LEVEL: "info"
  FEATURE_FLAG: "true"
"""
```

로그 레벨이나 기능 플래그처럼 민감하지 않은 설정은 ConfigMap에 두는 편이 자연스럽습니다. 바뀌어도 보안 사고로 이어질 가능성이 낮은 값들이 여기에 해당합니다.

### 2단계 — Secret 작성

```python
"""
apiVersion: v1
kind: Secret
metadata: {name: app-secret}
type: Opaque
stringData:
  DB_PASSWORD: "s3cret"
"""
```

`stringData`를 사용하면 사람이 읽을 수 있는 문자열을 넣어도 Kubernetes가 내부에서 base64 인코딩을 처리해 줍니다. 다만 이 인코딩은 표현 형식일 뿐, 보안적으로 완전한 암호화와는 다릅니다.

### 3단계 — 파드에 주입

```python
"""
spec:
  containers:
  - name: app
    image: myorg/app:1.0
    envFrom:
    - configMapRef: {name: app-config}
    - secretRef: {name: app-secret}
"""
```

`envFrom`은 환경 변수 기반 애플리케이션에서 가장 빠른 선택입니다. 다만 어떤 키가 한 번에 들어오는지 관리 기준이 함께 있어야 나중에 추적이 쉽습니다.

### 4단계 — 파일로 마운트

```python
"""
volumes:
- name: cfg
  configMap: {name: app-config}
volumeMounts:
- name: cfg
  mountPath: /etc/app
"""
```

설정을 파일 형태로 읽는 애플리케이션이라면 마운트 방식이 더 자연스럽습니다. 여러 줄짜리 설정이나 특정 경로를 기대하는 라이브러리에서는 환경 변수보다 파일이 잘 맞습니다.

### 5단계 — 변경 후 재시작

```python
import subprocess

def restart(dep):
    subprocess.run(
        ["kubectl", "rollout", "restart", f"deployment/{dep}"],
        check=True,
    )
```

설정값을 바꿨다고 애플리케이션이 항상 자동 반영되는 것은 아닙니다. 특히 환경 변수 기반 주입은 새 파드가 떠야 적용되므로, 설정 변경과 재시작을 함께 생각해야 합니다.

## 검증 흐름

```bash
kubectl get configmap app-config -o yaml
kubectl get secret app-secret -o yaml
kubectl exec deploy/web -- env | grep 'LOG_LEVEL\|DB_PASSWORD'
```

**예상되는 결과:** ConfigMap에는 사람이 읽을 수 있는 일반 설정이, Secret에는 base64 인코딩된 데이터가 보여야 합니다. `exec` 결과에서는 환경 변수 주입이 실제 컨테이너 프로세스까지 전달됐는지 확인할 수 있어야 합니다.

**먼저 의심할 실패 모드:**

- Secret 값이 평문처럼 보이면 `stringData`와 `data` 구분을 다시 확인해야 합니다.
- 객체 값은 바뀌었는데 앱이 예전 값을 쓰면 rollout restart가 빠졌을 가능성이 큽니다.
- 환경 변수 대신 파일을 읽는 앱이라면 `envFrom` 자체보다 volume mount 여부가 문제일 수 있습니다.

## 이 코드에서 먼저 봐야 할 점

- `stringData`를 쓰면 base64 인코딩을 직접 만들 필요가 없습니다.
- `envFrom`은 전체 묶음을 한 번에 넣습니다.
- 값이 바뀌면 재시작 전략도 함께 봐야 합니다.

이 세 가지를 같이 이해하면 ConfigMap과 Secret을 단순 객체 생성으로 끝내지 않게 됩니다. 실제 운영은 주입 방식, 반영 방식, 접근 권한까지 이어집니다.

## 자주 하는 실수 다섯 가지

1. Secret이면 곧 암호화라고 오해합니다.
2. Secret 값을 Git에 평문으로 올립니다.
3. ConfigMap 값을 바꾸면 애플리케이션이 즉시 자동 반영된다고 기대합니다.
4. 긴 설정도 모두 환경 변수만으로 처리하려 합니다.
5. Secret에 대한 RBAC를 느슨하게 둡니다.

## 실무에서는 이렇게 봅니다

실무에서는 Vault, AWS Secrets Manager, Azure Key Vault 같은 외부 비밀 관리 시스템을 진실 원천으로 두고, External Secrets Operator가 클러스터 Secret을 동기화하는 구조를 자주 씁니다. 이렇게 해야 값 회전과 접근 감사, 권한 분리가 더 쉬워집니다.

시니어 엔지니어는 ConfigMap과 Secret을 만들 때 객체 생성만 보지 않습니다. 누가 값을 바꾸는지, 값이 바뀌면 어떤 워크로드를 재시작할지, Git에는 어떤 형태로 남길지까지 함께 봅니다. 그래야 비로소 운영 가능한 구성이 됩니다.

## 체크리스트

- [ ] Secret 값을 Git에 평문으로 두지 않았는가
- [ ] Secret 접근에 RBAC를 적용했는가
- [ ] 변경 후 `rollout restart` 절차를 준비했는가
- [ ] 외부 비밀 관리 시스템을 먼저 검토했는가

## 연습 문제

1. ConfigMap과 Secret의 차이를 한 줄로 설명해 보세요.
2. "Secret은 암호화가 아니다"라는 말을 한 줄로 풀어 보세요.
3. External Secrets를 쓰는 장점을 하나 적어 보세요.

## 마무리와 다음 글

이 글에서는 ConfigMap과 Secret을 이미지를 환경 차이와 민감한 값에서 분리하는 기본 도구로 정리했습니다. ConfigMap은 일반 설정을, Secret은 민감한 값을 담고, 둘 다 환경 변수나 파일 마운트로 파드에 주입할 수 있습니다.

다음 글에서는 설정값이 아니라 실제 데이터를 오래 보존하는 방법을 보겠습니다. 주제는 Volume입니다.


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

## 설정과 비밀을 분리해 배포하기

ConfigMap과 Secret은 파일 포맷이 비슷하지만 운영 의미가 다릅니다. 변경 빈도가 높고 공개 가능한 값은 ConfigMap, 접근 통제가 필요한 값은 Secret으로 분리해야 감사와 롤백이 쉬워집니다.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: api-config
data:
  LOG_LEVEL: "info"
  FEATURE_PAYMENT_V2: "true"
---
apiVersion: v1
kind: Secret
metadata:
  name: api-secret
type: Opaque
stringData:
  DB_PASSWORD: "replace-me"
  API_KEY: "replace-me"
```

## 반영 전략: 재시작 기준을 명시하기

환경 변수로 주입한 값은 Pod 재시작 전까지 반영되지 않는 경우가 많습니다. 반영 기준을 문서화하지 않으면 "적용했다"와 "동작한다"가 어긋납니다.

```bash
kubectl apply -f config.yaml
kubectl rollout restart deploy/api -n prod
kubectl rollout status deploy/api -n prod
kubectl exec -n prod deploy/api -- printenv | grep LOG_LEVEL
```

## 시크릿 운영 수칙

1. Git에는 평문 Secret을 절대 커밋하지 않습니다.
2. `stringData`는 작성 편의를 위해서만 쓰고, 배포 파이프라인에서 암호화 체계를 붙입니다.
3. Secret 접근 RBAC를 최소 권한으로 제한합니다.
4. 교체 주기(rotation)와 만료 정책을 런북으로 고정합니다.

설정/비밀 경계를 초기에 잘 잡으면 배포 속도와 보안 수준을 동시에 유지할 수 있습니다.

## 운영 시뮬레이션 확장

ConfigMap/Secret 관점의 문서를 읽고 끝내면 실제 운영에서 금방 잊힙니다. 그래서 학습 직후에 "장애를 일부러 만들어 보고 복구하는" 시뮬레이션을 반드시 권장합니다. 여기서 중요한 점은 성공 데모를 반복하는 것이 아니라, 실패 신호를 표준 절차로 읽는 훈련을 하는 것입니다. 팀이 성장할수록 기술 격차보다 절차 격차가 더 큰 장애를 만듭니다.

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

## 운영 한 줄 원칙

운영에서 가장 중요한 원칙은 "원인 추정 전에 상태 증거를 먼저 수집한다"입니다. `describe`, `events`, `rollout` 세 신호를 먼저 확보하면 잘못된 가정으로 시간을 쓰는 일을 줄일 수 있습니다.

운영 중에는 변경 직후 10분 관찰 창을 두고 경고 이벤트를 반드시 확인합니다.

## 처음 질문으로 돌아가기

- **이미지 안에 설정과 비밀번호를 같이 넣으면 왜 운영이 어려워질까요?**
  - 환경별 설정값이 이미지 안에 박히면 dev·staging·prod마다 별도 이미지를 빌드해야 하고, 비밀번호 회전 한 번에 이미지를 다시 만들어 재배포해야 합니다. 본문에서 본 것처럼 설정은 ConfigMap·Secret으로 빼고 이미지에는 코드만 남겨야 환경 분리와 보안 회전이 가능합니다.
- **ConfigMap과 Secret은 무엇이 다르고 어디서 나뉠까요?**
  - 둘 다 키-값 형태로 설정을 Pod에 주입하지만, ConfigMap은 평문 설정용이고 Secret은 base64 인코딩된 민감 데이터용입니다. 본문에서 강조했듯이 Secret은 RBAC과 etcd 암호화로 접근을 제한해야 하며, "민감하면 Secret, 그 외에는 ConfigMap"이 첫 분기점입니다.
- **환경 변수 주입과 파일 마운트는 언제 다르게 선택할까요?**
  - 짧은 값(`LOG_LEVEL`, `API_KEY` 같은 한 줄)은 환경 변수가 단순하고 빠르지만, TLS 인증서나 JSON 설정 파일처럼 길거나 갱신 시 핫리로드가 필요한 경우에는 볼륨 마운트가 낫습니다. 본문 예시처럼 환경 변수는 컨테이너 재시작이 있어야 반영되고, 파일 마운트는 kubelet이 주기적으로 동기화한다는 점이 갈림길입니다.

<!-- toc:begin -->
## 시리즈 목차

- [Kubernetes 101 (1/10): Kubernetes란 무엇인가?](./01-what-is-kubernetes.md)
- [Kubernetes 101 (2/10): Pod](./02-pod.md)
- [Kubernetes 101 (3/10): Deployment](./03-deployment.md)
- [Kubernetes 101 (4/10): Service](./04-service.md)
- [Kubernetes 101 (5/10): Ingress](./05-ingress.md)
- **ConfigMap과 Secret (현재 글)**
- Volume (예정)
- HPA (예정)
- Helm (예정)
- 운영 관점의 Kubernetes (예정)

<!-- toc:end -->

## 참고 자료

- [ConfigMap](https://kubernetes.io/docs/concepts/configuration/configmap/)
- [Secret](https://kubernetes.io/docs/concepts/configuration/secret/)
- [External Secrets Operator](https://external-secrets.io/)
- [RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
- [Distribute credentials securely using Secrets](https://kubernetes.io/docs/tasks/inject-data-application/distribute-credentials-secure/)

- [Kubernetes 101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/kubernetes-101/ko)

Tags: Kubernetes, ConfigMap, Secret, Configuration, DevOps
