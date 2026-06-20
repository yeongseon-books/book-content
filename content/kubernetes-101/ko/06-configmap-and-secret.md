---
series: kubernetes-101
episode: 6
title: "Kubernetes 101 (6/10): ConfigMap과 Secret"
status: published
published_to:
  tistory:
    url: "https://yeongseonchoe.tistory.com/268"
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

> ConfigMap과 Secret은 단순한 키/값 저장소가 아니라 '이미지를 환경별 차이와 민감한 값에서 분리'하는 운영 도구입니다 — 같은 이미지를 dev·staging·prod에서 그대로 쓸 수 있어야 빌드 결정과 배포 결정이 비로소 깨끗하게 갈립니다.

## 이 글에서 다룰 문제

- 이미지 안에 설정과 비밀번호를 같이 넣으면 왜 운영이 어려워질까요?
- ConfigMap과 Secret은 무엇이 다르고 어디서 나뉠까요?
- 환경 변수 주입과 파일 마운트는 언제 다르게 선택할까요?
- 이 리소스의 설정을 잘못하면 운영에서 어떤 장애가 발생할까요?
- 프로덕션 환경에서 이 기능을 쓸 때 가장 먼저 점검할 항목은 무엇일까요?

환경 차이를 이미지 바깥으로 빼야 같은 이미지를 여러 환경에서 재현 가능하게 쓸 수 있습니다. 그래야 개발에서 검증한 이미지를 스테이징과 운영에서도 그대로 올릴 수 있습니다.

민감한 값은 더 엄격하게 다뤄야 합니다. 데이터베이스 비밀번호, API 토큰, 인증서 같은 값이 이미지나 Git에 평문으로 남으면 배포 편의성보다 훨씬 큰 리스크를 떠안게 됩니다. ConfigMap과 Secret을 구분하는 이유는 단순한 기능 차이가 아니라 운영 책임을 나누기 위해서입니다.

## ConfigMap vs Secret 비교

| 항목 | ConfigMap | Secret |
|---|---|---|
| 용도 | 민감하지 않은 설정 값 | 민감한 값 (비밀번호, 토큰, 인증서) |
| 저장 형식 | 평문 | base64 인코딩 (암호화 아님) |
| etcd 암호화 | 기본 미적용 | 추가 설정으로 암호화 가능 |
| RBAC 분리 | 일반 권한으로 접근 | 별도 RBAC로 접근 제한 가능 |
| Git 저장 | 가능 | 직접 저장 금지 (암호화 도구 사용) |
| 크기 제한 | 1MB | 1MB |

## ConfigMap YAML 완전 이해

### 기본 ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: default
data:
  LOG_LEVEL: "info"
  FEATURE_FLAG: "true"
  DB_HOST: "postgres.default.svc.cluster.local"
  DB_PORT: "5432"
  # 여러 줄 설정 파일도 가능
  app.properties: |
    server.port=8080
    spring.profiles.active=production
    logging.level.root=INFO
```

로그 레벨이나 기능 플래그처럼 민감하지 않은 설정은 ConfigMap에 두는 편이 자연스럽습니다. 바뀌어도 보안 사고로 이어질 가능성이 낮은 값들이 여기에 해당합니다.

### Secret YAML

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secret
  namespace: default
type: Opaque
stringData:          # 사람이 읽을 수 있는 형식 (권장)
  DB_PASSWORD: "s3cret"
  API_TOKEN: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
---
# data 필드는 직접 base64 인코딩된 값 입력
apiVersion: v1
kind: Secret
metadata:
  name: app-secret-raw
type: Opaque
data:
  DB_PASSWORD: czNjcmV0   # echo -n "s3cret" | base64
```

`stringData`를 사용하면 사람이 읽을 수 있는 문자열을 넣어도 Kubernetes가 내부에서 base64 인코딩을 처리해 줍니다. 다만 이 인코딩은 표현 형식일 뿐, 보안적으로 완전한 암호화와는 다릅니다.

## 주입 방식 완전 이해

### 방식 1: 환경 변수 (envFrom - 전체 묶음 주입)

```yaml
spec:
  containers:
  - name: app
    image: myorg/app:1.0
    envFrom:
    - configMapRef:
        name: app-config     # ConfigMap 전체를 환경 변수로
    - secretRef:
        name: app-secret     # Secret 전체를 환경 변수로
```

`envFrom`은 환경 변수 기반 애플리케이션에서 가장 빠른 선택입니다. 다만 어떤 키가 한 번에 들어오는지 관리 기준이 함께 있어야 나중에 추적이 쉽습니다.

### 방식 2: 환경 변수 (env - 개별 키 선택)

```yaml
spec:
  containers:
  - name: app
    image: myorg/app:1.0
    env:
    - name: LOG_LEVEL                  # 컨테이너 안에서 보이는 변수 이름
      valueFrom:
        configMapKeyRef:
          name: app-config
          key: LOG_LEVEL               # ConfigMap의 특정 키
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: app-secret
          key: DB_PASSWORD
```

### 방식 3: 볼륨 마운트 (파일 형태)

```yaml
spec:
  containers:
  - name: app
    image: myorg/app:1.0
    volumeMounts:
    - name: config-vol
      mountPath: /etc/app              # 컨테이너 안에서 접근할 경로
    - name: secret-vol
      mountPath: /etc/secret
      readOnly: true                   # Secret은 읽기 전용 권장
  volumes:
  - name: config-vol
    configMap:
      name: app-config
  - name: secret-vol
    secret:
      secretName: app-secret
```

설정을 파일 형태로 읽는 애플리케이션이라면 마운트 방식이 더 자연스럽습니다. 여러 줄짜리 설정이나 특정 경로를 기대하는 라이브러리에서는 환경 변수보다 파일이 잘 맞습니다.

### 주입 방식 선택 기준

| 상황 | 권장 방식 |
|---|---|
| 단순 키/값 설정 | 환경 변수 (env 또는 envFrom) |
| 많은 설정을 한 번에 | envFrom |
| 특정 키만 선택적으로 | env (valueFrom) |
| 파일 형식 설정 (yaml, properties 등) | 볼륨 마운트 |
| 인증서, 개인 키 | 볼륨 마운트 (파일 경로 필요) |
| 동적 갱신이 필요한 설정 | 볼륨 마운트 (환경 변수는 재시작 필요) |

## 단계별로 설정과 비밀 값 분리하기

### 1단계 — 리소스 생성

```bash
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
```

### 2단계 — 파드에 주입 확인

```bash
# 환경 변수 주입 확인
kubectl exec deploy/web -- env | grep LOG_LEVEL
kubectl exec deploy/web -- env | grep DB_PASSWORD

# 파일 마운트 확인
kubectl exec deploy/web -- ls /etc/app
kubectl exec deploy/web -- cat /etc/app/LOG_LEVEL
```

### 3단계 — 값 변경 후 재시작

```bash
# ConfigMap 값 변경
kubectl edit configmap app-config
# 또는
kubectl patch configmap app-config -p '{"data":{"LOG_LEVEL":"debug"}}'

# 환경 변수 기반 주입은 재시작 필요
kubectl rollout restart deployment/web
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

## 트러블슈팅 시나리오

### 시나리오 1: 환경 변수가 적용되지 않음

```bash
# 파드 안 환경 변수 직접 확인
kubectl exec <pod-name> -- env

# 파드 스펙에서 envFrom/env 확인
kubectl get pod <pod-name> -o jsonpath='{.spec.containers[0].env}'
kubectl get pod <pod-name> -o jsonpath='{.spec.containers[0].envFrom}'

# ConfigMap/Secret 존재 여부 확인
kubectl get configmap app-config
kubectl get secret app-secret

# 재시작 후 확인
kubectl rollout restart deployment/web
```

### 시나리오 2: Secret 값이 예상과 다름

```bash
# Secret 실제 값 디코딩
kubectl get secret app-secret -o jsonpath='{.data.DB_PASSWORD}' | base64 -d
echo ""

# stringData로 설정했지만 조회할 때는 data(base64)로 나옴 - 정상 동작
```

### 시나리오 3: 볼륨 마운트 파일이 없음

```bash
# 볼륨 마운트 확인
kubectl describe pod <pod-name> | grep -A 10 Volumes

# 파일 시스템 확인
kubectl exec <pod-name> -- ls -la /etc/app

# ConfigMap 키 이름과 파일명 일치 확인
kubectl get configmap app-config -o yaml
```

## 자주 하는 실수

| 실수 | 문제 | 올바른 방법 |
|---|---|---|
| Secret을 암호화로 오해 | 보안 취약점 간과 | base64는 인코딩, 실제 암호화는 etcd encryption 또는 외부 시스템 |
| Secret 값을 Git에 평문 저장 | 비밀 정보 유출 | Sealed Secrets, SOPS, 외부 Secret 관리 시스템 사용 |
| ConfigMap 변경 후 재시작 누락 | 앱이 이전 설정 사용 | rollout restart 또는 자동 재시작 메커니즘 구현 |
| 긴 설정을 모두 환경 변수로 | 관리 어려움, 크기 제한 | 파일 형식 설정은 볼륨 마운트 사용 |
| Secret RBAC 느슨하게 설정 | 불필요한 접근 허용 | 네임스페이스별, 역할별 최소 권한 원칙 적용 |

## 실무에서는 이렇게 봅니다

실무에서는 Vault, AWS Secrets Manager, Azure Key Vault 같은 외부 비밀 관리 시스템을 진실 원천으로 두고, External Secrets Operator가 클러스터 Secret을 동기화하는 구조를 자주 씁니다. 이렇게 해야 값 회전과 접근 감사, 권한 분리가 더 쉬워집니다.

시니어 엔지니어는 ConfigMap과 Secret을 만들 때 객체 생성만 보지 않습니다. 누가 값을 바꾸는지, 값이 바뀌면 어떤 워크로드를 재시작할지, Git에는 어떤 형태로 남길지까지 함께 봅니다. 그래야 비로소 운영 가능한 구성이 됩니다.

```yaml
# External Secrets Operator 사용 예시
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: app-secret
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secretsmanager
    kind: ClusterSecretStore
  target:
    name: app-secret        # 생성될 Kubernetes Secret 이름
  data:
  - secretKey: DB_PASSWORD  # Kubernetes Secret 키
    remoteRef:
      key: prod/app/db      # AWS Secrets Manager 경로
      property: password    # 해당 경로의 JSON 필드
```

## 운영 체크리스트

- [ ] Secret 값을 Git에 평문으로 두지 않았는가
- [ ] Secret 접근에 RBAC를 적용했는가
- [ ] 변경 후 `rollout restart` 절차를 준비했는가
- [ ] 외부 비밀 관리 시스템을 먼저 검토했는가
- [ ] etcd at-rest encryption을 활성화했는가 (민감 환경)
- [ ] Secret 값 회전 주기를 정의했는가

## 연습 문제

1. ConfigMap과 Secret의 차이를 한 줄로 설명해 보세요.
2. "Secret은 암호화가 아니다"라는 말을 한 줄로 풀어 보세요.
3. External Secrets를 쓰는 장점을 하나 적어 보세요.
4. 환경 변수 주입과 볼륨 마운트 중 어떤 상황에서 볼륨 마운트를 선택하나요?
5. ConfigMap 변경 후 애플리케이션에 즉시 반영되지 않는 이유를 설명해 보세요.

## 설정 변경 반영 전략

ConfigMap이나 Secret을 바꾼 후 파드에 반영하는 방법은 주입 방식에 따라 다릅니다.

```
환경 변수 주입 (envFrom / env):
  → 새 파드가 떠야 새 값 반영
  → kubectl rollout restart deployment/<name> 필요

볼륨 마운트:
  → kubelet이 주기적으로 ConfigMap/Secret 내용을 파일에 반영
  → 대략 1~2분 내 자동 갱신 (kubelet sync period)
  → 단, 애플리케이션이 파일 변경을 감지하고 다시 읽어야 함
```

```bash
# 현재 적용된 ConfigMap 값 확인
kubectl exec deploy/web -- env | grep LOG_LEVEL

# ConfigMap 값 변경
kubectl patch configmap app-config --type=merge \
  -p '{"data":{"LOG_LEVEL":"debug"}}'

# 환경 변수 기반이면 재시작 필요
kubectl rollout restart deployment/web

# 볼륨 마운트 기반이면 파일 자동 갱신 확인
kubectl exec deploy/web -- cat /etc/app/LOG_LEVEL
```

## Secret 보안 강화 방법

기본 Kubernetes Secret은 etcd에 base64로만 저장됩니다. 보안 수준을 높이는 방법들이 있습니다.

| 방법 | 설명 | 적용 복잡도 |
|---|---|---|
| etcd 암호화 | API 서버 설정으로 etcd at-rest 암호화 | 중간 |
| Sealed Secrets | 암호화된 YAML을 Git에 커밋 가능 | 낮음 |
| External Secrets Operator | Vault, AWS SM 등 외부 시스템과 동기화 | 중간 |
| CSI Secret Store | 파드에 외부 비밀을 파일로 직접 마운트 | 높음 |

```bash
# etcd 암호화 적용 여부 확인
kubectl get secrets -n kube-system | grep encryption-config

# Sealed Secrets 사용 예시
# 1. kubeseal CLI로 암호화
kubeseal --format=yaml < secret.yaml > sealed-secret.yaml

# 2. 암호화된 파일을 Git에 커밋 (안전)
git add sealed-secret.yaml

# 3. 클러스터에 적용 (Controller가 자동 복호화)
kubectl apply -f sealed-secret.yaml
```

## 마무리와 다음 글

이 글에서는 ConfigMap과 Secret을 이미지를 환경 차이와 민감한 값에서 분리하는 기본 도구로 정리했습니다. ConfigMap은 일반 설정을, Secret은 민감한 값을 담고, 둘 다 환경 변수나 파일 마운트로 파드에 주입할 수 있습니다.

다음 글에서는 설정값이 아니라 실제 데이터를 오래 보존하는 방법을 보겠습니다. 주제는 Volume입니다.

## 정리

ConfigMap과 Secret은 단순한 키/값 저장소가 아니라 '이미지를 환경별 차이와 민감한 값에서 분리'하는 운영 도구입니다 — 같은 이미지를 dev·staging·prod에서 그대로 쓸 수 있어야 빌드 결정과 배포 결정이 비로소 깨끗하게 갈립니다. 이 글에서는 한눈에 보는 구조부터 마무리와 다음 글까지 이 원칙을 구체적으로 살펴봤습니다. 핵심은 개념을 외우는 것이 아니라 실무에서 어떤 판단을 바꾸는지 이해하는 데 있습니다.

## 처음 질문으로 돌아가기

- **이미지 안에 설정과 비밀번호를 같이 넣으면 왜 운영이 어려워질까요?**
  - 값을 바꾸려면 이미지를 다시 빌드해야 합니다. 환경별 차이도 이미지 변형으로 표현하게 돼 재현성이 깨집니다.
- **ConfigMap과 Secret은 무엇이 다르고 어디서 나뉠까요?**
  - 민감도가 기준입니다. 노출돼도 보안 사고가 없으면 ConfigMap, 비밀번호·토큰·인증서처럼 노출 시 위험한 값은 Secret입니다.
- **환경 변수 주입과 파일 마운트는 언제 다르게 선택할까요?**
  - 단순 키/값은 환경 변수, 파일 경로를 기대하는 설정이나 동적 갱신이 필요한 경우는 볼륨 마운트를 선택합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Kubernetes 101 (1/10): Kubernetes란 무엇인가?](./01-what-is-kubernetes.md)
- [Kubernetes 101 (2/10): Pod](./02-pod.md)
- [Kubernetes 101 (3/10): Deployment](./03-deployment.md)
- [Kubernetes 101 (4/10): Service](./04-service.md)
- [Kubernetes 101 (5/10): Ingress](./05-ingress.md)
- **Kubernetes 101 (6/10): ConfigMap과 Secret (현재 글)**
- [Kubernetes 101 (7/10): Volume](./07-volume.md)
- [Kubernetes 101 (8/10): HPA](./08-hpa.md)
- [Kubernetes 101 (9/10): Helm](./09-helm.md)
- [운영 관점의 Kubernetes](./10-kubernetes-in-operation.md)

<!-- toc:end -->
