---
series: kubernetes-101
episode: 9
title: "Kubernetes 101 (9/10): Helm"
status: published
published_to:
  tistory:
    url: "https://yeongseonchoe.tistory.com/271"
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

![Kubernetes 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/kubernetes-101/09/09-01-concept-at-a-glance.ko.png)
*Kubernetes 101 9장 흐름 개요*

> Helm은 단순한 패키지 매니저가 아니라 '공통 템플릿과 환경별 값을 분리'해 Kubernetes 배포를 반복 가능하게 만드는 배포 단위입니다 — 매니페스트 복사가 늘기 시작하면 이미 차트로 묶어야 할 시점이고, values.yaml의 분리가 환경 차이를 정직하게 드러나게 합니다.

## 이 글에서 다룰 문제

- 환경마다 YAML을 복사하는 방식은 왜 드리프트를 만들까요?
- Chart와 `values.yaml`은 어떤 책임을 나눌까요?
- `install`, `upgrade`, `rollback`은 어떤 흐름으로 이어질까요?
- 이 리소스의 설정을 잘못하면 운영에서 어떤 장애가 발생할까요?
- 프로덕션 환경에서 이 기능을 쓸 때 가장 먼저 점검할 항목은 무엇일까요?

환경별 사본이 늘어나면 작은 수정 하나도 여러 파일에 반복 반영해야 합니다. 어느 환경 파일이 최신인지, 어떤 차이가 의도된 것인지도 시간이 갈수록 흐려집니다. 이 상태가 바로 배포 드리프트입니다.

Helm은 같은 구조를 반복 사용할 때 차이는 값으로만 드러나게 만듭니다. 입문 단계에서는 편한 템플릿 도구처럼 보일 수 있지만, 실무에서는 배포 단위를 어떻게 표준화할지와 직접 연결됩니다.

## YAML 복사 vs Helm 비교

| 항목 | 환경별 YAML 복사 | Helm 차트 사용 |
|---|---|---|
| 공통 구조 변경 | 모든 환경 파일 개별 수정 | 차트 템플릿 한 번 수정 |
| 환경별 차이 | 파일 비교가 어렵 | values.yaml로 명시적 표현 |
| 배포 이력 | 없음 | revision 자동 관리 |
| 롤백 | 이전 YAML 재적용 (복잡) | `helm rollback` 한 줄 |
| 패키지 공유 | 불가 | Helm 저장소로 배포 가능 |

## Helm 핵심 개념

### 차트 구조

```
my-app/
├── Chart.yaml          # 차트 메타데이터 (이름, 버전, 설명)
├── values.yaml         # 기본값
├── charts/             # 의존성 차트 (하위 차트)
└── templates/          # Go 템플릿 파일
    ├── deployment.yaml
    ├── service.yaml
    ├── ingress.yaml
    ├── configmap.yaml
    ├── _helpers.tpl    # 공통 헬퍼 함수
    └── NOTES.txt       # 설치 후 출력 메시지
```

- 차트: Helm의 패키지 단위입니다.
- `values.yaml`: 기본값을 담는 파일입니다.
- 릴리스: 차트가 실제로 설치된 인스턴스입니다.
- 저장소: 차트를 배포하고 받는 유통 채널입니다.
- 의존성: 하위 차트를 포함하는 관계입니다.

## 차트 파일 작성 예시

### Chart.yaml

```yaml
apiVersion: v2
name: my-app
description: A Helm chart for my application
type: application
version: 1.2.0          # 차트 버전 (Semantic Versioning)
appVersion: "2.5.0"     # 애플리케이션 버전
dependencies:
- name: postgresql
  version: "12.1.0"
  repository: https://charts.bitnami.com/bitnami
  condition: postgresql.enabled
```

### values.yaml (기본값)

```yaml
replicaCount: 2
image:
  repository: myorg/app
  tag: "1.0"
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 80

ingress:
  enabled: false
  className: nginx
  host: example.com

resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 256Mi

autoscaling:
  enabled: false
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 60

postgresql:
  enabled: false         # 기본적으로 PostgreSQL 비활성화
```

### templates/deployment.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "my-app.fullname" . }}
  labels:
    {{- include "my-app.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      {{- include "my-app.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "my-app.selectorLabels" . | nindent 8 }}
    spec:
      containers:
      - name: {{ .Chart.Name }}
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
        imagePullPolicy: {{ .Values.image.pullPolicy }}
        ports:
        - containerPort: {{ .Values.service.port }}
        resources:
          {{- toYaml .Values.resources | nindent 10 }}
```

여기에는 환경에 따라 달라질 수 있는 값이 `{{ .Values.* }}`로 표현됩니다. 반대로 배포 구조 자체는 차트 템플릿에 남겨 두는 편이 좋습니다.

## 단계별로 작은 차트 만들어 보기

### 1단계 — 차트 생성

```bash
helm create my-app

# 생성된 구조 확인
ls my-app/
# Chart.yaml  charts/  templates/  values.yaml
```

Helm은 기본 차트 구조를 빠르게 만들어 줍니다. 생성 직후 템플릿이 그대로 운영 품질이라는 뜻은 아니고, 공통 구조를 어떤 기준으로 다듬을지가 더 중요합니다.

### 2단계 — 환경별 values 파일 작성

```bash
# 개발 환경 values
cat > values-dev.yaml << 'EOF'
replicaCount: 1
image:
  tag: "latest"
resources:
  requests:
    cpu: 50m
    memory: 64Mi
EOF

# 운영 환경 values
cat > values-prod.yaml << 'EOF'
replicaCount: 3
image:
  tag: "2.5.0"
ingress:
  enabled: true
  host: app.example.com
autoscaling:
  enabled: true
  maxReplicas: 20
resources:
  requests:
    cpu: 500m
    memory: 512Mi
EOF
```

### 3단계 — 렌더 결과 미리 보기

```bash
# 적용 전 YAML 출력으로 확인
helm template my-app ./my-app -f values-prod.yaml

# 문법 검사
helm lint ./my-app
```

`helm template`으로 렌더 결과를 미리 보는 것은 적용 전 필수 단계입니다. 클러스터에 반영하기 전에 어떤 YAML이 생성될지 확인할 수 있습니다.

### 4단계 — 설치

```bash
# 개발 환경에 설치
helm install my-app-dev ./my-app -f values-dev.yaml -n dev --create-namespace

# 운영 환경에 설치
helm install my-app-prod ./my-app -f values-prod.yaml -n prod --create-namespace

# 설치된 릴리스 확인
helm list -A
```

릴리스는 같은 차트를 실제로 설치한 인스턴스입니다. 이 개념을 이해해야 Helm이 템플릿 저장소가 아니라 배포 단위라는 사실이 보입니다.

### 5단계 — 업그레이드

```bash
# 이미지 태그 변경 후 업그레이드
helm upgrade my-app-prod ./my-app -f values-prod.yaml \
  --set image.tag=2.6.0 \
  --atomic \          # 실패 시 자동 롤백
  --timeout 5m \      # 타임아웃 설정
  -n prod

# 업그레이드 후 이력 확인
helm history my-app-prod -n prod
```

`--atomic`은 실패 시 자동 롤백을 함께 수행합니다. 야간 배포에서 특히 의미가 큰 옵션입니다.

### 6단계 — 롤백

```bash
# 이력 확인
helm history my-app-prod -n prod
# REVISION  UPDATED                   STATUS     CHART         DESCRIPTION
# 1         2026-06-01 10:00:00       superseded  my-app-1.2.0  Install complete
# 2         2026-06-10 14:00:00       deployed    my-app-1.2.0  Upgrade complete

# 이전 revision으로 롤백
helm rollback my-app-prod 1 -n prod
```

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

## 트러블슈팅 시나리오

### 시나리오 1: 업그레이드 실패 후 롤백

```bash
# 업그레이드 실패 시 (--atomic 없는 경우)
helm status my-app-prod -n prod
# STATUS: failed

# 수동 롤백
helm rollback my-app-prod -n prod

# --atomic 사용 시 자동으로 이전 버전으로 복구됨
helm upgrade my-app-prod ./my-app -f values-prod.yaml --atomic -n prod
```

### 시나리오 2: values와 템플릿 불일치

```bash
# 렌더 결과 직접 확인
helm template my-app ./my-app -f values-prod.yaml --debug

# 특정 값이 어떻게 처리되는지 확인
helm get values my-app-prod -n prod          # 현재 릴리스에 적용된 values
helm get manifest my-app-prod -n prod        # 현재 릴리스의 실제 YAML
```

### 시나리오 3: Secret 평문 노출

```bash
# values에 민감한 값이 있는지 확인
helm get values my-app-prod -n prod | grep -i password

# 해결 방안 1: External Secrets Operator 연동
# 해결 방안 2: Sealed Secrets로 암호화
# 해결 방안 3: Helm Secrets 플러그인 사용

# Helm Secrets 플러그인 설치
helm plugin install https://github.com/jkroepke/helm-secrets

# 암호화된 values 파일로 업그레이드
helm secrets upgrade my-app-prod ./my-app -f secrets.yaml.enc -n prod
```

## 자주 하는 실수

| 실수 | 문제 | 올바른 방법 |
|---|---|---|
| values와 차트 책임 혼용 | 재사용 어려움, 드리프트 발생 | 구조는 차트, 환경 차이는 values에만 |
| Secret 값을 values에 평문 저장 | 비밀 정보 Git 노출 | External Secrets, Sealed Secrets, Helm Secrets 사용 |
| `latest` 태그 사용 | 재현 불가, 무엇이 배포됐는지 불명확 | 정확한 버전 태그 고정 |
| rollback 절차 미숙지 | 장애 시 복구 지연 | `helm history`와 `helm rollback` 정기 연습 |
| 의존성 갱신 누락 | 오래된 하위 차트 사용 | `helm dependency update` 실행 |

## 실무에서는 이렇게 봅니다

실무에서는 GitOps와 Helm을 함께 써서 values 변경만으로 배포가 이뤄지는 흐름을 자주 만듭니다. 이때 차트는 공통 계약이 되고, 환경별 values는 운영 차이를 담는 얇은 레이어가 됩니다.

시니어 엔지니어는 Helm을 쓸 때 values에 무엇을 넣지 않을지도 같이 정합니다. 민감한 값은 외부 비밀 관리 시스템으로 넘기고, 차트에는 구조만 남겨 두는 편이 장기적으로 훨씬 안정적입니다.

```bash
# 실무에서 Helm 운영 시 자주 쓰는 명령 모음
helm list -A                                         # 전체 릴리스 목록
helm status <release> -n <namespace>                 # 릴리스 상태
helm get values <release> -n <namespace>             # 현재 values
helm get manifest <release> -n <namespace>           # 현재 적용된 YAML
helm history <release> -n <namespace>                # 배포 이력
helm diff upgrade <release> ./chart -f values.yaml   # 변경 사항 미리 보기 (플러그인)
```

### ArgoCD와 Helm 연동

```yaml
# ArgoCD Application 예시
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app-prod
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/myorg/helm-charts
    targetRevision: HEAD
    path: my-app
    helm:
      valueFiles:
      - values-prod.yaml
  destination:
    server: https://kubernetes.default.svc
    namespace: prod
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

## 운영 체크리스트

- [ ] 차트와 values 책임을 분리했는가
- [ ] 버전을 고정했는가
- [ ] `--atomic` 사용 여부를 검토했는가
- [ ] Secret 처리를 외부화했는가
- [ ] `helm lint`를 CI에 포함했는가
- [ ] 롤백 절차를 팀이 알고 있는가

## 연습 문제

1. `helm template`의 목적을 한 줄로 설명해 보세요.
2. values와 차트의 책임 차이를 한 줄로 적어 보세요.
3. `--atomic`이 왜 더 안전한지 한 줄로 정리해 보세요.
4. 같은 차트를 개발/운영 환경에 각각 설치할 때 어떻게 구분하나요?
5. `helm lint`가 통과했는데도 운영에서 문제가 생길 수 있는 경우를 하나 떠올려 보세요.

## 마무리와 다음 글

이 글에서는 Helm을 공통 배포 구조와 환경별 차이를 분리하는 도구로 정리했습니다. 차트는 공유되는 계약이고, values는 환경별 차이를 담는 입력값이라는 감각을 잡아 두면 YAML 복사본이 빠르게 줄어듭니다.

다음 글에서는 시리즈를 마무리하며, 실제 운영 관점에서 probes, RBAC, 관측성, GitOps를 어떻게 함께 봐야 하는지 정리하겠습니다.

## 정리

Helm은 단순한 패키지 매니저가 아니라 '공통 템플릿과 환경별 값을 분리'해 Kubernetes 배포를 반복 가능하게 만드는 배포 단위입니다 — 매니페스트 복사가 늘기 시작하면 이미 차트로 묶어야 할 시점이고, values.yaml의 분리가 환경 차이를 정직하게 드러나게 합니다. 이 글에서는 한눈에 보는 구조부터 마무리와 다음 글까지 이 원칙을 구체적으로 살펴봤습니다. 핵심은 개념을 외우는 것이 아니라 실무에서 어떤 판단을 바꾸는지 이해하는 데 있습니다.

## 처음 질문으로 돌아가기

- **환경마다 YAML을 복사하는 방식은 왜 드리프트를 만들까요?**
  - 공통 구조 변경이 모든 사본에 반영되지 않으면 환경마다 차이가 쌓입니다. 어떤 차이가 의도된 것인지 알 수 없게 되는 상태가 드리프트입니다.
- **Chart와 `values.yaml`은 어떤 책임을 나눌까요?**
  - 차트는 "어떻게 배포하는가"라는 공통 구조를 담고, values는 "이 환경에서 어떤 값을 쓰는가"라는 차이를 담습니다.
- **`install`, `upgrade`, `rollback`은 어떤 흐름으로 이어질까요?**
  - install로 첫 릴리스를 만들고, upgrade로 revision을 쌓으며, 문제가 생기면 rollback으로 이전 revision으로 돌아갑니다. 이 이력이 Helm의 핵심 가치입니다.

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
- **Kubernetes 101 (9/10): Helm (현재 글)**
- [운영 관점의 Kubernetes](./10-kubernetes-in-operation.md)

<!-- toc:end -->
