---
series: kubernetes-101
episode: 5
title: "Kubernetes 101 (5/10): Ingress"
status: published
published_to:
  tistory:
    url: "https://yeongseonchoe.tistory.com/267"
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
  - Ingress
  - HTTP
  - TLS
  - DevOps
seo_description: Ingress와 IngressController, 경로 기반 라우팅과 TLS 종료를 설명합니다.
last_reviewed: '2026-05-15'
---

# Kubernetes 101 (5/10): Ingress

Service까지 배우면 클러스터 내부 통신은 어느 정도 정리됩니다. 하지만 사용자가 브라우저나 앱에서 요청을 보내기 시작하면 다른 질문이 생깁니다. 외부 트래픽을 어디서 받을지, 여러 서비스를 어떤 규칙으로 나눌지, TLS 인증서를 어디에서 종료할지를 정해야 합니다.

이 글은 Kubernetes 101 시리즈의 5번째 글입니다.

여기서는 Ingress를 단순한 외부 노출 기능이 아니라, 여러 서비스를 하나의 진입점 뒤에 두고 HTTP 계층에서 라우팅 규칙과 TLS 종료를 모으는 구조로 정리하겠습니다.

![Kubernetes 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/kubernetes-101/05/05-01-concept-at-a-glance.ko.png)
*Kubernetes 101 5장 흐름 개요*

> Ingress는 외부 노출 기능이 아니라 '여러 서비스를 하나의 진입점 뒤에 두고 HTTP 계층에서 라우팅과 TLS를 모으는 자리'입니다 — 도메인·경로 규칙·인증서 종료가 각 Service에 흩어지지 않고 한 곳에 모일 때 운영 일관성이 비로소 생깁니다.

## 이 글에서 다룰 문제

- Ingress와 IngressController는 왜 따로 이해해야 할까요?
- 여러 서비스를 하나의 도메인 아래에서 어떻게 나눌 수 있을까요?
- `host`, `path`, `pathType`은 어떤 차이를 만들까요?
- 이 리소스의 설정을 잘못하면 운영에서 어떤 장애가 발생할까요?
- 프로덕션 환경에서 이 기능을 쓸 때 가장 먼저 점검할 항목은 무엇일까요?

서비스 수가 적을 때는 앱마다 LoadBalancer Service를 하나씩 두는 방법도 가능해 보입니다. 하지만 서비스가 늘어나면 외부 IP, 인증서, 라우팅 정책, 보안 정책이 모두 흩어집니다. 구조가 단순해 보이는 대신 운영 부담과 비용이 빠르게 커집니다.

Ingress는 이 문제를 해결하기 위한 공통 진입점입니다. 중요한 점은 Ingress 자체가 프록시가 아니라 규칙 객체라는 사실입니다. 규칙과 실행체를 분리해서 이해해야, 왜 규칙은 있는데 트래픽이 안 들어오는지 같은 문제를 빠르게 파악할 수 있습니다.

## 한눈에 보는 구조

외부 로드 밸런서는 보통 클러스터 앞단에서 트래픽을 받아들이고, IngressController는 Ingress 규칙을 실제 프록시 동작으로 바꿉니다. 결국 Ingress는 "어디로 보낼지"를 선언하고, Controller는 "어떻게 보낼지"를 실행합니다.

- Ingress: L7 HTTP 라우팅 규칙을 담는 객체입니다.
- IngressController: Ingress 규칙을 실제 프록시 설정으로 적용하는 실행체입니다.
- host: 도메인 이름입니다.
- path: URL 경로입니다.
- TLS 종료: HTTPS 복호화를 Ingress 지점에서 처리하는 방식입니다.

## Ingress vs LoadBalancer Service 비교

| 항목 | LoadBalancer Service (서비스마다) | Ingress (중앙 집중) |
|---|---|---|
| 외부 IP 수 | 서비스마다 별도 IP | 단일 진입점 |
| TLS 관리 | 서비스마다 인증서 설정 | 한 곳에서 인증서 종료 |
| 도메인/경로 라우팅 | 불가 | 가능 (host, path 기반) |
| 클라우드 비용 | LB 개수만큼 과금 | LB 1개 + Ingress 규칙 |
| 변경 용이성 | 서비스별 개별 변경 | Ingress 규칙 수정으로 일괄 반영 |

## Ingress YAML 완전 이해

### 기본 경로 기반 라우팅

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /   # nginx-ingress 어노테이션
spec:
  ingressClassName: nginx    # 사용할 IngressController 지정
  rules:
  - host: example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api
            port:
              number: 80
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web
            port:
              number: 80
```

이 예제는 `example.com/api`를 `api` 서비스로 보내고, 나머지 `/` 요청은 `web` 서비스로 보냅니다. `ingressClassName`으로 어떤 Controller가 이 규칙을 처리할지 명시하는 것이 중요합니다.

### pathType 종류

```yaml
# Exact: 정확히 일치하는 경로만
- path: /api
  pathType: Exact       # /api 만 매칭, /api/users 는 불매칭

# Prefix: 경로 접두사 기준 매칭
- path: /api
  pathType: Prefix      # /api, /api/users, /api/v1/... 모두 매칭

# ImplementationSpecific: 구현체마다 다름
- path: /api/*
  pathType: ImplementationSpecific  # Controller가 해석 방식 결정
```

### TLS 설정

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web-tls
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - example.com
    secretName: example-tls    # TLS 인증서가 담긴 Secret
  rules:
  - host: example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web
            port:
              number: 80
```

### 다중 도메인 Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: multi-host
spec:
  ingressClassName: nginx
  tls:
  - hosts: [app1.example.com]
    secretName: app1-tls
  - hosts: [app2.example.com]
    secretName: app2-tls
  rules:
  - host: app1.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: app1
            port:
              number: 80
  - host: app2.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: app2
            port:
              number: 80
```

## 단계별로 호스트와 경로 라우팅 구성하기

### 1단계 — IngressController 설치 확인

```bash
# nginx IngressController 설치 확인
kubectl get pods -n ingress-nginx

# IngressClass 확인
kubectl get ingressclass
```

Ingress를 적용했다고 해서 바로 트래픽이 흐르지는 않습니다. 클러스터 안에 IngressController가 있어야 이 규칙이 실제 프록시 동작으로 이어집니다.

### 2단계 — TLS Secret 생성

```bash
# 자체 서명 인증서 생성 (테스트용)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout tls.key -out tls.crt \
  -subj "/CN=example.com/O=example"

# Secret 생성
kubectl create secret tls example-tls \
  --cert=tls.crt --key=tls.key
```

TLS는 보통 Secret으로 관리합니다. 인증서와 개인 키는 해당 Ingress와 같은 네임스페이스에 둬야 HTTPS가 제대로 붙습니다.

### 3단계 — Ingress 적용

```bash
kubectl apply -f ingress.yaml
kubectl get ingress web
```

출력 예시:
```
NAME   CLASS   HOSTS         ADDRESS         PORTS     AGE
web    nginx   example.com   192.168.1.100   80, 443   1m
```

ADDRESS 필드에 실제 IP 또는 호스트명이 나타나야 IngressController가 이 규칙을 감지했다는 뜻입니다.

### 4단계 — 확인

```bash
# /api 경로 테스트
curl -sk -H 'Host: example.com' http://<ingress-address>/api

# / 경로 테스트
curl -sk -H 'Host: example.com' http://<ingress-address>/

# TLS 테스트
curl -sk https://example.com/api
```

실제 요청을 보내 보면 경로별 라우팅과 TLS 적용 여부를 함께 검증할 수 있습니다. `/api`와 `/`를 각각 호출해 다른 응답이 오는지 보는 방식이 가장 직관적입니다.

## 검증 흐름

```bash
kubectl get ingress web
kubectl describe ingress web
curl -sk -H 'Host: example.com' https://<ingress-address>/api
```

**예상되는 결과:** `get ingress`에는 address 또는 controller가 붙인 엔드포인트가 보이고, `describe`에는 호스트·경로·백엔드 서비스가 명시돼야 합니다. 마지막 `curl`에서는 `/api` 요청이 웹 루트와 다른 백엔드로 흘렀다는 흔적을 응답으로 확인합니다.

**먼저 의심할 실패 모드:**

- Ingress 객체만 있고 address가 비어 있으면 규칙이 아니라 controller 설치 상태를 먼저 봐야 합니다.
- TLS handshake가 실패하면 인증서 자체보다 Secret 네임스페이스와 secretName 오타를 먼저 점검합니다.
- `/`는 되는데 `/api`가 엉뚱한 서비스로 가면 path 우선순위와 pathType 해석이 어긋난 경우가 많습니다.

## 트러블슈팅 시나리오

### 시나리오 1: Ingress address가 비어 있음

```bash
# IngressController 파드 상태 확인
kubectl get pods -n ingress-nginx

# IngressController 로그 확인
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller

# IngressClass 연결 확인
kubectl get ingress web -o jsonpath='{.spec.ingressClassName}'
kubectl get ingressclass

# 원인: Controller가 없거나, ingressClassName이 잘못됨
```

### 시나리오 2: 경로 라우팅 오작동

```bash
# Ingress 규칙 상세 확인
kubectl describe ingress web

# nginx-ingress의 경우 설정 확인
kubectl exec -n ingress-nginx <controller-pod> -- nginx -T | grep location

# 경로 우선순위 주의
# Exact > Prefix 순으로 처리됨
# 더 구체적인 경로를 위에 두어야 함
```

### 시나리오 3: TLS 인증서 오류

```bash
# Secret 존재 여부 확인
kubectl get secret example-tls

# 인증서 내용 확인
kubectl get secret example-tls -o jsonpath='{.data.tls\.crt}' | base64 -d | openssl x509 -text -noout

# cert-manager 사용 시 Certificate 상태 확인
kubectl get certificate
kubectl describe certificate example-tls
```

## 자주 하는 실수

| 실수 | 문제 | 올바른 방법 |
|---|---|---|
| IngressController 없이 Ingress만 생성 | 트래픽 미전달, address 없음 | Controller 먼저 설치 후 Ingress 생성 |
| pathType 생략 | 구현체마다 다른 동작 | Prefix 또는 Exact 명시 |
| TLS Secret을 다른 네임스페이스에 생성 | TLS 미적용 | Ingress와 같은 네임스페이스에 Secret 위치 |
| 서비스마다 LoadBalancer 생성 | 비용 증가, 관리 어려움 | Ingress로 통합 |
| 경로 우선순위 오해 | 의도치 않은 서비스로 라우팅 | 구체적인 경로를 먼저, Exact 우선 |

## 실무에서는 이렇게 봅니다

실무에서는 nginx-ingress, AWS Load Balancer Controller 같은 구현이 Ingress 객체를 읽어 실제 프록시와 외부 로드 밸런서 구성을 맞춥니다. TLS는 cert-manager와 묶어 자동 발급과 자동 갱신까지 연결하는 경우가 많습니다.

시니어 엔지니어는 Ingress 문법만 보지 않고, 지금 쓰는 Controller가 어떤 기능과 제약을 갖는지도 함께 봅니다. 같은 Ingress 객체라도 구현체마다 동작 범위가 다를 수 있기 때문입니다. Gateway API가 주목받는 이유도 이 지점과 이어집니다.

```bash
# 실무에서 Ingress 운영 시 자주 쓰는 명령 모음
kubectl get ingress -A                                    # 전체 Ingress 목록
kubectl describe ingress <name>                           # 규칙 및 이벤트 상세
kubectl get events --field-selector reason=Sync           # Controller 동기화 이벤트
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller --tail=50
# cert-manager 인증서 상태
kubectl get certificate -A
kubectl get certificaterequest -A
```

## 운영 체크리스트

- [ ] IngressController가 설치되어 있는가
- [ ] `pathType`을 명시했는가
- [ ] TLS 자동화 방안을 준비했는가
- [ ] 외부 진입점을 가능한 한 통합했는가
- [ ] `ingressClassName`을 명시했는가
- [ ] 백엔드 Service가 동일 네임스페이스에 있는가

## 연습 문제

1. Ingress와 IngressController의 차이를 한 줄로 설명해 보세요.
2. TLS 종료를 Ingress에서 처리할 때 좋은 점을 하나 적어 보세요.
3. Gateway API가 해결하려는 한계를 한 줄로 정리해 보세요.
4. `pathType: Prefix`와 `pathType: Exact`의 차이를 예시와 함께 설명해 보세요.
5. Ingress address가 비어 있을 때 가장 먼저 확인할 것은 무엇인가요?

## cert-manager로 TLS 자동화

운영 환경에서 TLS 인증서를 수동으로 관리하는 것은 갱신 누락 위험이 큽니다. cert-manager를 사용하면 Let's Encrypt 인증서를 자동으로 발급하고 갱신할 수 있습니다.

```yaml
# cert-manager ClusterIssuer 설정 (Let's Encrypt)
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@example.com
    privateKeySecretRef:
      name: letsencrypt-prod-key
    solvers:
    - http01:
        ingress:
          class: nginx
---
# cert-manager와 연동된 Ingress
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"  # 자동 인증서 발급
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - example.com
    secretName: example-tls    # cert-manager가 자동으로 채워줌
  rules:
  - host: example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web
            port:
              number: 80
```

```bash
# cert-manager 인증서 상태 확인
kubectl get certificate
kubectl describe certificate example-tls

# 인증서 만료일 확인
kubectl get secret example-tls -o jsonpath='{.data.tls\.crt}' | \
  base64 -d | openssl x509 -noout -dates
```

## Ingress 어노테이션으로 고급 기능 설정

IngressController마다 어노테이션으로 다양한 기능을 제어할 수 있습니다.

```yaml
metadata:
  annotations:
    # nginx-ingress 주요 어노테이션
    nginx.ingress.kubernetes.io/proxy-body-size: "50m"       # 요청 바디 최대 크기
    nginx.ingress.kubernetes.io/proxy-read-timeout: "120"     # 읽기 타임아웃(초)
    nginx.ingress.kubernetes.io/rate-limit: "100"             # 초당 요청 제한
    nginx.ingress.kubernetes.io/ssl-redirect: "true"          # HTTP → HTTPS 리디렉션
    nginx.ingress.kubernetes.io/use-regex: "true"             # 경로에 정규식 사용
    nginx.ingress.kubernetes.io/cors-allow-origin: "*"        # CORS 허용 도메인
```

## 마무리와 다음 글

이 글에서는 Ingress를 여러 서비스를 하나의 외부 진입점 뒤에 두고, 도메인과 경로 기준으로 HTTP 요청을 나누는 규칙 객체로 정리했습니다. 실제 동작은 IngressController가 책임지고, TLS 종료까지 이 지점에 모으면 외부 노출 구조가 훨씬 단순해집니다.

다음 글에서는 네트워크 경로가 아니라 애플리케이션 설정과 민감한 값을 어떻게 분리하는지, ConfigMap과 Secret을 보겠습니다.

## 정리

Ingress는 외부 노출 기능이 아니라 '여러 서비스를 하나의 진입점 뒤에 두고 HTTP 계층에서 라우팅과 TLS를 모으는 자리'입니다 — 도메인·경로 규칙·인증서 종료가 각 Service에 흩어지지 않고 한 곳에 모일 때 운영 일관성이 비로소 생깁니다. 이 글에서는 한눈에 보는 구조부터 마무리와 다음 글까지 이 원칙을 구체적으로 살펴봤습니다. 핵심은 개념을 외우는 것이 아니라 실무에서 어떤 판단을 바꾸는지 이해하는 데 있습니다.

## 처음 질문으로 돌아가기

- **Ingress와 IngressController는 왜 따로 이해해야 할까요?**
  - Ingress는 규칙 객체이고 IngressController는 그 규칙을 실제 프록시 동작으로 변환하는 실행체입니다. 규칙이 있어도 Controller 없이는 아무 일도 일어나지 않습니다.
- **여러 서비스를 하나의 도메인 아래에서 어떻게 나눌 수 있을까요?**
  - `host`와 `path` 규칙으로 같은 도메인의 다른 경로를 각각 다른 Service로 라우팅합니다. `pathType`으로 일치 방식을 제어합니다.
- **`host`, `path`, `pathType`은 어떤 차이를 만들까요?**
  - `host`는 도메인 기반 분기, `path`는 URL 경로 기반 분기를 담당합니다. `pathType`은 경로 일치 방식(Exact/Prefix)을 결정해 라우팅 정확도에 직접 영향을 줍니다.

<!-- toc:begin -->
## 시리즈 목차

- [Kubernetes 101 (1/10): Kubernetes란 무엇인가?](./01-what-is-kubernetes.md)
- [Kubernetes 101 (2/10): Pod](./02-pod.md)
- [Kubernetes 101 (3/10): Deployment](./03-deployment.md)
- [Kubernetes 101 (4/10): Service](./04-service.md)
- **Kubernetes 101 (5/10): Ingress (현재 글)**
- [Kubernetes 101 (6/10): ConfigMap과 Secret](./06-configmap-and-secret.md)
- [Kubernetes 101 (7/10): Volume](./07-volume.md)
- [Kubernetes 101 (8/10): HPA](./08-hpa.md)
- [Kubernetes 101 (9/10): Helm](./09-helm.md)
- [운영 관점의 Kubernetes](./10-kubernetes-in-operation.md)

<!-- toc:end -->
