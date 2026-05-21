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

## 먼저 던지는 질문

- 이미지 안에 설정과 비밀번호를 같이 넣으면 왜 운영이 어려워질까요?
- ConfigMap과 Secret은 무엇이 다르고 어디서 나뉠까요?
- 환경 변수 주입과 파일 마운트는 언제 다르게 선택할까요?

## 큰 그림

![Kubernetes 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/kubernetes-101/06/06-01-concept-at-a-glance.ko.png)

*Kubernetes 101 6장 흐름 개요*

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

## 처음 질문으로 돌아가기

- **이미지 안에 설정과 비밀번호를 같이 넣으면 왜 운영이 어려워질까요?**
  - 본문의 기준은 ConfigMap과 Secret를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **ConfigMap과 Secret은 무엇이 다르고 어디서 나뉠까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **환경 변수 주입과 파일 마운트는 언제 다르게 선택할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

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

Tags: Kubernetes, ConfigMap, Secret, Configuration, DevOps
