---
series: kubernetes-101
episode: 5
title: "바이브코딩을 위한 Kubernetes 기초 (5/10): Ingress"
status: draft
targets:
  wordpress: true
language: ko
tags:
  - 바이브코딩
  - Kubernetes
  - Ingress
  - HTTP
  - DevOps
seo_description: AI가 생성한 Ingress YAML을 제대로 이해하기 위해 알아야 할 IngressController, 경로 기반 라우팅, TLS 설정을 바이브코딩 관점에서 정리합니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 Kubernetes 기초 (5/10): Ingress

이 글은 **바이브코딩을 위한 Kubernetes 기초** 시리즈의 다섯 번째 글입니다. AI와 함께 K8s YAML을 만들기 전에, Kubernetes가 어떻게 동작하는지 먼저 이해하는 것을 목표로 합니다.

---

AI에게 "백엔드 API와 프론트엔드를 같은 도메인에서 경로로 나눠 배포하고 싶어"라고 하면 Ingress YAML이 나옵니다. 그런데 Ingress만 만들었는데 왜 외부 접근이 안 되는지, 왜 HTTPS가 안 되는지 이해하지 못하면 막막합니다.

바이브코딩 흐름에서 Ingress를 처음 접할 때 가장 많이 하는 실수가 있습니다. "Ingress YAML을 apply했는데 왜 접근이 안 되죠?" 이 경우 거의 대부분 IngressController가 클러스터에 설치되어 있지 않은 문제입니다. Ingress는 규칙 객체이고, 규칙을 실행하는 IngressController는 별도로 설치해야 합니다. 이 차이를 모르면 계속 디버깅에 헤매게 됩니다.

> Ingress는 외부 노출 기능이 아니라 '여러 서비스를 하나의 진입점 뒤에 두고 HTTP 계층에서 라우팅과 TLS를 모으는 자리'입니다. 도메인, 경로 규칙, 인증서 종료가 각 Service에 흩어지지 않고 한 곳에 모일 때 운영 일관성이 비로소 생깁니다.

## 이 글에서 답하는 질문들

- Ingress와 IngressController는 왜 따로 이해해야 할까요?
- 여러 서비스를 하나의 도메인 아래에서 어떻게 나눌 수 있을까요?
- `host`, `path`, `pathType`은 어떤 차이를 만들까요?
- Ingress를 잘못 설정하면 운영에서 어떤 장애가 생길까요?
- AI가 생성한 Ingress YAML에서 가장 먼저 확인할 항목은 무엇일까요?

## 바이브코딩 관점: Ingress가 왜 혼자서는 안 되는가

AI가 만들어준 Ingress YAML을 apply해도 트래픽이 안 들어오는 이유를 이해하려면, Ingress의 두 가지 구성 요소를 구분해야 합니다.

**Ingress 객체(규칙)**: "example.com/api로 오는 요청은 api-service로 보내라"는 선언입니다. 이것만으로는 아무것도 안 됩니다.

**IngressController(실행 엔진)**: nginx, traefik, AWS ALB 등의 실제 프록시 프로그램입니다. Ingress 규칙을 읽어서 실제 트래픽 라우팅을 수행합니다. 클러스터에 별도로 설치해야 합니다.

Ingress 객체가 있어도 IngressController가 없으면 외부 트래픽이 들어오지 않습니다. AI에게 IngressController 설치 방법도 함께 물어봐야 합니다.

## Ingress 구조: 한눈에 보기

**주요 개념**

- **Ingress**: L7 HTTP 라우팅 규칙을 담는 객체. 규칙만 선언
- **IngressController**: Ingress 규칙을 실제 프록시 설정으로 적용하는 실행체. 별도 설치 필요
- **host**: 도메인 이름(`example.com`)
- **path**: URL 경로(`/api`, `/`)
- **pathType**: 경로 매칭 방식. `Prefix`(경로 앞부분 일치)가 가장 일반적
- **TLS 종료**: HTTPS 복호화를 Ingress 지점에서 처리. 각 앱이 개별로 처리할 필요 없음

## Ingress 도입 전과 후

**Ingress 없이 서비스별 LoadBalancer를 쓸 때**

서비스마다 외부 IP가 생기고, 비용과 인증서 운영 부담이 빠르게 커집니다. 라우팅 정책, 보안 정책이 흩어집니다.

**Ingress를 사용하면**

하나의 진입점 뒤에서 `/api`는 API 서비스로, `/`는 웹 서비스로 보내는 라우팅을 중앙에서 선언할 수 있습니다. TLS 인증서도 Ingress 한 곳에서 관리합니다.

## 단계별 Ingress 다루기

### 1단계: IngressController 확인

```bash
# nginx ingress controller 설치 확인
kubectl get pods -n ingress-nginx

# 설치가 안 되어 있다면 (로컬 환경)
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml
```

Ingress YAML보다 IngressController 설치를 먼저 확인해야 합니다.

### 2단계: Ingress 매니페스트 작성

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
  - host: example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api-svc
            port:
              number: 80
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-svc
            port:
              number: 80
```

`example.com/api`는 `api-svc`로, 나머지 `/` 요청은 `web-svc`로 보냅니다. `ingressClassName`을 설치한 Controller에 맞게 설정해야 합니다.

### 3단계: HTTPS 설정

```yaml
spec:
  tls:
  - hosts:
    - example.com
    secretName: example-tls
  rules:
  - host: example.com
    # ...
```

```bash
# TLS Secret 생성 (인증서 파일이 있는 경우)
kubectl create secret tls example-tls \
  --cert=tls.crt --key=tls.key
```

TLS는 인증서를 Secret으로 관리하고 Ingress에 연결합니다. cert-manager를 사용하면 Let's Encrypt 인증서 발급과 갱신을 자동화할 수 있습니다.

### 4단계: 상태 확인

```bash
kubectl get ingress web
kubectl describe ingress web
```

`get ingress`에서 ADDRESS가 비어 있으면 IngressController가 없거나 클라우드 로드 밸런서 연결이 안 된 상태입니다.

## 자주 하는 실수 5가지

| 실수 | 실제 문제 | 올바른 접근 |
|------|-----------|-------------|
| IngressController 없이 Ingress만 생성 | ADDRESS가 비어 외부 접근 불가 | IngressController 먼저 설치 확인 |
| `pathType` 생략 | IngressController 구현체마다 다르게 해석 | 항상 명시적으로 `Prefix` 또는 `Exact` 지정 |
| TLS Secret을 다른 네임스페이스에 생성 | HTTPS 인증서가 적용 안 됨 | Ingress와 같은 네임스페이스에 Secret 생성 |
| 서비스마다 LoadBalancer 계속 생성 | 비용과 IP 관리가 복잡해짐 | Ingress로 통합 |
| 경로 우선순위 오해 | `/`가 `/api`보다 먼저 매칭됨 | 구체적인 경로를 먼저 배치 |

## AI 팁: Ingress YAML 요청과 검토

```
# Ingress 생성 요청 예시
"example.com 도메인에서 /api 경로는 api-svc(port 80)로,
/ 경로는 web-svc(port 80)로 라우팅하는 Ingress YAML을 만들어줘.
nginx ingress controller를 사용하고 pathType을 명시해줘."

# HTTPS 설정 요청 예시
"위 Ingress에 TLS를 추가하고 싶어.
cert-manager를 사용해서 Let's Encrypt 인증서를 자동 발급받는
설정도 함께 만들어줘."

# 문제 진단 요청 예시
"kubectl get ingress 결과에서 ADDRESS가 비어 있어.
이유와 해결 방법을 알려줘."
```

## 운영 체크리스트

- [ ] IngressController가 클러스터에 설치되어 있는가
- [ ] `ingressClassName`을 명시했는가
- [ ] `pathType`을 명시했는가(`Prefix` 또는 `Exact`)
- [ ] TLS Secret이 Ingress와 같은 네임스페이스에 있는가
- [ ] TLS 인증서 자동 갱신 방안을 준비했는가(cert-manager 등)

## 처음 질문으로 돌아가기

**Ingress와 IngressController는 왜 따로 이해해야 할까요?**
Ingress는 "어디로 보낼지"를 선언하는 규칙 객체입니다. IngressController는 그 규칙을 읽어서 "어떻게 보낼지"를 실행하는 프로그램입니다. 규칙은 있는데 실행체가 없으면 트래픽이 흐르지 않습니다.

**여러 서비스를 하나의 도메인 아래에서 어떻게 나눌 수 있을까요?**
Ingress의 `rules`에 같은 `host` 아래 여러 `path`를 정의해서 나눕니다. `/api`는 api-service로, `/admin`은 admin-service로, `/`는 web-service로 보내는 식입니다.

**`host`, `path`, `pathType`은 어떤 차이를 만들까요?**
`host`는 어떤 도메인 요청인지 구분합니다. `path`는 URL 경로를 구분합니다. `pathType`은 경로를 어떻게 매칭할지 결정합니다. `Prefix`는 해당 경로로 시작하는 모든 URL, `Exact`는 정확히 일치하는 URL만 라우팅합니다.

## 정리

이번 글에서 다룬 핵심은 세 가지입니다. 첫째, Ingress는 규칙이고 IngressController는 그 규칙을 실행하는 별도 컴포넌트입니다. 둘째, AI가 생성한 Ingress YAML을 apply하기 전에 클러스터에 IngressController가 있는지 확인해야 합니다. 셋째, TLS는 Ingress에서 한 번에 처리하면 각 앱이 인증서를 개별 관리할 필요가 없습니다.

다음 글에서는 애플리케이션 설정값과 민감한 비밀 값을 이미지에서 분리하는 ConfigMap과 Secret을 바이브코딩 관점에서 살펴보겠습니다.

## 참고 자료

- [Kubernetes 공식 문서: Ingress](https://kubernetes.io/ko/docs/concepts/services-networking/ingress/)
- [nginx Ingress Controller 공식 문서](https://kubernetes.github.io/ingress-nginx/)
- [cert-manager 공식 문서](https://cert-manager.io/docs/)
- [Kubernetes 101 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/kubernetes-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Kubernetes 기초 (1/10): Kubernetes란 무엇인가?
- 바이브코딩을 위한 Kubernetes 기초 (2/10): Pod
- 바이브코딩을 위한 Kubernetes 기초 (3/10): Deployment
- 바이브코딩을 위한 Kubernetes 기초 (4/10): Service
- **바이브코딩을 위한 Kubernetes 기초 (5/10): Ingress (현재 글)**
- 바이브코딩을 위한 Kubernetes 기초 (6/10): ConfigMap과 Secret
- 바이브코딩을 위한 Kubernetes 기초 (7/10): Volume
- 바이브코딩을 위한 Kubernetes 기초 (8/10): HPA
- 바이브코딩을 위한 Kubernetes 기초 (9/10): Helm
- 바이브코딩을 위한 Kubernetes 기초 (10/10): 운영 관점의 Kubernetes

<!-- toc:end -->

Tags: 바이브코딩, Kubernetes, Ingress, HTTP, DevOps
