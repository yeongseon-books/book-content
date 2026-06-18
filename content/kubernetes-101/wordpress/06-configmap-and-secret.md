---
series: kubernetes-101
episode: 6
title: "바이브코딩을 위한 Kubernetes 기초 (6/10): ConfigMap과 Secret"
status: draft
targets:
  wordpress: true
language: ko
tags:
  - 바이브코딩
  - Kubernetes
  - ConfigMap
  - Secret
  - DevOps
seo_description: AI가 생성한 ConfigMap/Secret YAML을 안전하게 활용하기 위해 알아야 할 설정 분리, 주입 방식, 보안 주의사항을 바이브코딩 관점에서 정리합니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 Kubernetes 기초 (6/10): ConfigMap과 Secret

이 글은 **바이브코딩을 위한 Kubernetes 기초** 시리즈의 여섯 번째 글입니다. AI와 함께 K8s YAML을 만들기 전에, Kubernetes가 어떻게 동작하는지 먼저 이해하는 것을 목표로 합니다.

---

AI에게 "데이터베이스 비밀번호를 환경 변수로 넘기는 Kubernetes 설정 만들어줘"라고 하면 Secret YAML이 나옵니다. 그런데 이 Secret을 Git에 커밋하면 안 된다는 걸 모르고 그냥 저장소에 올리는 경우가 많습니다. "Secret이니까 안전하겠지"라는 오해입니다.

바이브코딩 흐름에서 ConfigMap과 Secret을 처음 쓸 때 가장 중요한 점이 있습니다. Secret의 base64 인코딩은 암호화가 아닙니다. 누구나 바로 디코딩할 수 있습니다. AI가 만들어준 Secret YAML을 그대로 Git에 올리면 비밀번호가 공개됩니다.

> ConfigMap과 Secret은 단순한 키/값 저장소가 아니라 '이미지를 환경별 차이와 민감한 값에서 분리'하는 운영 도구입니다. 같은 이미지를 dev, staging, prod에서 그대로 쓸 수 있어야 빌드 결정과 배포 결정이 비로소 깨끗하게 갈립니다.

## 이 글에서 답하는 질문들

- 이미지 안에 설정과 비밀번호를 같이 넣으면 왜 운영이 어려워질까요?
- ConfigMap과 Secret은 무엇이 다르고 어디서 나뉠까요?
- 환경 변수 주입과 파일 마운트는 언제 다르게 선택할까요?
- Secret을 잘못 다루면 어떤 보안 문제가 생길까요?
- AI가 생성한 Secret YAML에서 가장 먼저 확인할 항목은 무엇일까요?

## 바이브코딩 관점: 이미지에 비밀번호를 넣으면 안 되는 이유

바이브코딩으로 빠르게 앱을 만들다 보면 컨테이너 이미지 안에 설정값과 비밀번호를 함께 넣는 실수를 합니다.

```dockerfile
# 이렇게 하면 안 됩니다
ENV DB_PASSWORD=mypassword123
ENV API_KEY=secret-api-key
```

이 방식의 문제점이 세 가지입니다. 첫째, 비밀번호를 바꾸려면 이미지를 다시 빌드해야 합니다. 둘째, 같은 이미지를 개발과 운영에서 다른 설정으로 쓸 수 없습니다. 셋째, 이미지가 레지스트리에 올라가면 이미지를 볼 수 있는 모든 사람이 비밀번호를 볼 수 있습니다.

ConfigMap과 Secret은 이 문제를 해결합니다. 이미지는 환경에 무관하게 만들고, 설정값은 배포 시점에 주입합니다.

## ConfigMap과 Secret 구조: 한눈에 보기

**주요 개념**

- **ConfigMap**: 민감하지 않은 키/값 설정 묶음. 로그 레벨, 기능 플래그, 서버 주소 등
- **Secret**: 민감한 키/값 설정 묶음. DB 비밀번호, API 키, 인증서 등. base64 인코딩(암호화 아님!)
- **`envFrom`**: ConfigMap이나 Secret의 모든 키를 한 번에 환경 변수로 주입
- **볼륨 마운트**: 설정을 파일 형태로 컨테이너 경로에 연결
- **External Secrets**: 외부 비밀 관리 시스템(Vault, AWS Secrets Manager 등)과 클러스터 Secret 동기화

## 도입 전과 후

**이미지에 설정을 하드코딩할 때**

비밀번호 하나 바꾸려면 이미지 재빌드와 재배포가 필요합니다. 개발/스테이징/운영 환경마다 다른 이미지를 유지해야 합니다.

**ConfigMap과 Secret을 사용하면**

이미지는 환경에 무관하게 만들고, 설정은 배포 시점에 주입합니다. 같은 이미지를 모든 환경에서 쓸 수 있고, 설정 변경 시 이미지 재빌드가 불필요합니다.

## 단계별 설정과 비밀 값 분리하기

### 1단계: ConfigMap 작성

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  LOG_LEVEL: "info"
  FEATURE_FLAG: "true"
  DB_HOST: "postgres-svc"
```

민감하지 않은 설정은 ConfigMap에 넣습니다. 바뀌어도 보안 사고로 이어질 가능성이 낮은 값들입니다.

### 2단계: Secret 작성

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secret
type: Opaque
stringData:
  DB_PASSWORD: "your-actual-password"
  API_KEY: "your-api-key"
```

`stringData`를 쓰면 Kubernetes가 내부에서 base64 인코딩을 처리합니다. 하지만 이 YAML 파일 자체는 Git에 올리면 안 됩니다. 비밀번호가 그대로 보입니다.

### 3단계: 파드에 주입 (환경 변수 방식)

```yaml
spec:
  containers:
  - name: app
    image: myorg/app:1.0
    envFrom:
    - configMapRef:
        name: app-config
    - secretRef:
        name: app-secret
```

`envFrom`은 ConfigMap이나 Secret의 모든 키를 환경 변수로 한 번에 주입합니다.

### 4단계: 파드에 주입 (파일 마운트 방식)

```yaml
spec:
  containers:
  - name: app
    volumeMounts:
    - name: config
      mountPath: /etc/app
  volumes:
  - name: config
    configMap:
      name: app-config
```

설정을 파일 형태로 읽는 애플리케이션에 사용합니다. `/etc/app/LOG_LEVEL` 같은 경로로 파일이 생깁니다.

### 5단계: 설정 변경 후 재시작

```bash
kubectl rollout restart deployment/web
```

환경 변수 기반 주입은 파드가 새로 뜰 때 적용됩니다. ConfigMap/Secret을 수정한 후에는 Deployment를 재시작해야 합니다.

## 자주 하는 실수 5가지

| 실수 | 실제 문제 | 올바른 접근 |
|------|-----------|-------------|
| Secret이 암호화되어 있다고 오해 | base64는 누구나 바로 디코딩 가능 | Secret은 접근 제어(RBAC)로 보호해야 함 |
| Secret YAML을 Git에 그대로 커밋 | 비밀번호가 저장소에 공개됨 | .gitignore 처리 또는 External Secrets 사용 |
| ConfigMap 변경 후 재시작 안 함 | 앱이 여전히 예전 값을 사용 | 변경 후 `rollout restart` 필수 |
| 긴 설정을 모두 환경 변수로만 처리 | 수십 개 환경 변수로 관리 복잡 | 파일 마운트 방식 활용 |
| Secret에 RBAC 적용 안 함 | 클러스터 접근 권한이 있으면 누구나 Secret 조회 | 네임스페이스 단위 접근 제어 설정 |

## AI 팁: ConfigMap/Secret 요청과 보안 검토

```
# ConfigMap 생성 요청 예시
"로그 레벨(info), 기능 플래그(true), DB 호스트(postgres-svc)를
ConfigMap으로 만들고, 이 값을 Deployment 환경 변수로
주입하는 YAML을 만들어줘."

# Secret 보안 주의사항 확인
"이 Secret YAML을 안전하게 관리하려면 어떻게 해야 해?
Git에 올리면 안 되는 이유와 대안을 설명해줘."

# External Secrets 도입 방법 질문
"AWS Secrets Manager에 있는 DB 비밀번호를
Kubernetes Secret으로 자동 동기화하는 방법을 알려줘.
External Secrets Operator를 사용하는 예제도 포함해줘."
```

## 운영 체크리스트

- [ ] Secret YAML을 Git에 평문으로 저장하지 않았는가
- [ ] Secret 접근에 RBAC를 적용했는가
- [ ] ConfigMap/Secret 변경 후 `rollout restart` 절차를 준비했는가
- [ ] 외부 비밀 관리 시스템(Vault, AWS Secrets Manager 등) 사용을 검토했는가
- [ ] 민감한 값(비밀번호, API 키)과 일반 설정(로그 레벨)을 올바르게 구분했는가

## 처음 질문으로 돌아가기

**이미지 안에 설정과 비밀번호를 같이 넣으면 왜 운영이 어려워질까요?**
비밀번호를 바꿀 때마다 이미지를 재빌드해야 하고, 환경마다 다른 이미지를 유지해야 합니다. 이미지가 유출되면 비밀번호도 유출됩니다.

**ConfigMap과 Secret은 무엇이 다르고 어디서 나뉠까요?**
ConfigMap은 누출되어도 보안 문제가 없는 설정(로그 레벨, 서버 주소 등)에 씁니다. Secret은 누출되면 문제가 되는 값(비밀번호, API 키 등)에 씁니다. 기능적으로는 비슷하지만 운영 책임과 접근 제어 방식이 다릅니다.

**환경 변수 주입과 파일 마운트는 언제 다르게 선택할까요?**
앱이 `os.environ`이나 `process.env`로 설정을 읽으면 환경 변수 주입이 편합니다. 앱이 특정 경로의 설정 파일(`.env` 파일, `config.yaml` 등)을 읽으면 파일 마운트가 더 맞습니다. 여러 줄짜리 설정이나 인증서 파일은 파일 마운트가 자연스럽습니다.

## 정리

이번 글에서 다룬 핵심은 세 가지입니다. 첫째, Secret의 base64 인코딩은 암호화가 아니므로 Secret YAML을 Git에 커밋하면 안 됩니다. 둘째, ConfigMap과 Secret으로 이미지를 환경 차이와 분리해야 같은 이미지를 모든 환경에서 쓸 수 있습니다. 셋째, 설정 변경 후 파드를 재시작해야 새 값이 적용됩니다.

다음 글에서는 파드가 재시작되어도 데이터가 사라지지 않도록 하는 Volume을 바이브코딩 관점에서 살펴보겠습니다.

## 참고 자료

- [Kubernetes 공식 문서: ConfigMap](https://kubernetes.io/ko/docs/concepts/configuration/configmap/)
- [Kubernetes 공식 문서: Secret](https://kubernetes.io/ko/docs/concepts/configuration/secret/)
- [External Secrets Operator](https://external-secrets.io/)
- [Kubernetes 101 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/kubernetes-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Kubernetes 기초 (1/10): Kubernetes란 무엇인가?
- 바이브코딩을 위한 Kubernetes 기초 (2/10): Pod
- 바이브코딩을 위한 Kubernetes 기초 (3/10): Deployment
- 바이브코딩을 위한 Kubernetes 기초 (4/10): Service
- 바이브코딩을 위한 Kubernetes 기초 (5/10): Ingress
- **바이브코딩을 위한 Kubernetes 기초 (6/10): ConfigMap과 Secret (현재 글)**
- 바이브코딩을 위한 Kubernetes 기초 (7/10): Volume
- 바이브코딩을 위한 Kubernetes 기초 (8/10): HPA
- 바이브코딩을 위한 Kubernetes 기초 (9/10): Helm
- 바이브코딩을 위한 Kubernetes 기초 (10/10): 운영 관점의 Kubernetes

<!-- toc:end -->

Tags: 바이브코딩, Kubernetes, ConfigMap, Secret, DevOps
