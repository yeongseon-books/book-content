---
series: kubernetes-101
episode: 5
title: "Kubernetes 101 (5/10): Ingress"
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

## 먼저 던지는 질문

- Ingress와 IngressController는 왜 따로 이해해야 할까요?
- 여러 서비스를 하나의 도메인 아래에서 어떻게 나눌 수 있을까요?
- `host`, `path`, `pathType`은 어떤 차이를 만들까요?

## 큰 그림

![Kubernetes 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/kubernetes-101/05/05-01-concept-at-a-glance.ko.png)

*Kubernetes 101 5장 흐름 개요*

이 그림에서는 Ingress를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> Ingress의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 중요한가

서비스 수가 적을 때는 앱마다 LoadBalancer Service를 하나씩 두는 방법도 가능해 보입니다. 하지만 서비스가 늘어나면 외부 IP, 인증서, 라우팅 정책, 보안 정책이 모두 흩어집니다. 구조가 단순해 보이는 대신 운영 부담과 비용이 빠르게 커집니다.

Ingress는 이 문제를 해결하기 위한 공통 진입점입니다. 중요한 점은 Ingress 자체가 프록시가 아니라 규칙 객체라는 사실입니다. 규칙과 실행체를 분리해서 이해해야, 왜 규칙은 있는데 트래픽이 안 들어오는지 같은 문제를 빠르게 파악할 수 있습니다.

## 한눈에 보는 구조

외부 로드 밸런서는 보통 클러스터 앞단에서 트래픽을 받아들이고, IngressController는 Ingress 규칙을 실제 프록시 동작으로 바꿉니다. 결국 Ingress는 "어디로 보낼지"를 선언하고, Controller는 "어떻게 보낼지"를 실행합니다.

## 핵심 용어

- Ingress: L7 HTTP 라우팅 규칙을 담는 객체입니다.
- IngressController: Ingress 규칙을 실제 프록시 설정으로 적용하는 실행체입니다.
- host: 도메인 이름입니다.
- path: URL 경로입니다.
- TLS 종료: HTTPS 복호화를 Ingress 지점에서 처리하는 방식입니다.

## 도입 전과 후

Ingress가 없으면 서비스마다 외부 LoadBalancer를 따로 두기 쉽습니다. 처음에는 이해하기 쉽지만, 비용과 인증서 운영 부담이 빠르게 커집니다.

Ingress를 두면 하나의 진입점 뒤에서 `/api`는 API 서비스로, `/`는 웹 서비스로 보내는 식의 라우팅을 중앙에서 선언할 수 있습니다. 외부 노출 구조가 훨씬 읽기 쉬워지는 이유입니다.

## 단계별로 호스트와 경로 라우팅 구성하기

### 1단계 — Ingress 매니페스트 작성

```python
"""
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata: {name: web}
spec:
  rules:
  - host: example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service: {name: api, port: {number: 80}}
      - path: /
        pathType: Prefix
        backend:
          service: {name: web, port: {number: 80}}
"""
```

이 예제는 `example.com/api`를 `api` 서비스로 보내고, 나머지 `/` 요청은 `web` 서비스로 보냅니다. 여기서 먼저 볼 값은 `host`, `path`, `pathType`입니다.

### 2단계 — 적용

```python
import subprocess

def apply(path):
    subprocess.run(["kubectl", "apply", "-f", path], check=True)
```

Ingress를 적용했다고 해서 바로 트래픽이 흐르지는 않습니다. 클러스터 안에 IngressController가 있어야 이 규칙이 실제 프록시 동작으로 이어집니다.

### 3단계 — TLS 시크릿 생성

```python
def tls_secret(name, cert, key):
    subprocess.run([
        "kubectl", "create", "secret", "tls", name,
        "--cert", cert, "--key", key,
    ], check=True)
```

TLS는 보통 Secret으로 관리합니다. 인증서와 개인 키는 해당 Ingress와 같은 네임스페이스에 둬야 HTTPS가 제대로 붙습니다.

### 4단계 — TLS 적용

```python
"""
spec:
  tls:
  - hosts: [example.com]
    secretName: example-tls
"""
```

이 설정을 추가하면 애플리케이션 컨테이너마다 인증서를 따로 둘 필요 없이, 공통 진입점에서 HTTPS를 종료할 수 있습니다. 운영 관점에서 큰 단순화입니다.

### 5단계 — 확인

```python
def curl(host, path):
    res = subprocess.run(
        ["curl", "-sk", f"https://{host}{path}"],
        capture_output=True, text=True, check=True,
    )
    return res.stdout
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

## 이 코드에서 먼저 봐야 할 점

- Ingress는 규칙이고 Controller는 실행체입니다.
- `pathType: Prefix`는 가장 흔한 기본 선택입니다.
- TLS는 Ingress 지점에서 종료할 수 있습니다.

이 세 가지를 구분하면 Ingress를 단순 포워더로 보지 않게 됩니다. 규칙 객체, 실행 컨트롤러, 외부 진입점이 서로 다른 역할을 갖고 있다는 사실이 보입니다.

## 자주 하는 실수 다섯 가지

1. IngressController가 없는데도 Ingress만 만들면 외부 요청이 들어올 것이라 생각합니다.
2. `pathType`을 생략해 구현체별 차이와 호환성 문제를 만납니다.
3. TLS Secret을 잘못된 네임스페이스에 둡니다.
4. 서비스마다 LoadBalancer를 계속 만들어 비용 문제를 키웁니다.
5. 경로 우선순위를 잘못 이해해 다른 백엔드로 요청을 보냅니다.

## 실무에서는 이렇게 봅니다

실무에서는 nginx-ingress, AWS Load Balancer Controller 같은 구현이 Ingress 객체를 읽어 실제 프록시와 외부 로드 밸런서 구성을 맞춥니다. TLS는 cert-manager와 묶어 자동 발급과 자동 갱신까지 연결하는 경우가 많습니다.

시니어 엔지니어는 Ingress 문법만 보지 않고, 지금 쓰는 Controller가 어떤 기능과 제약을 갖는지도 함께 봅니다. 같은 Ingress 객체라도 구현체마다 동작 범위가 다를 수 있기 때문입니다. Gateway API가 주목받는 이유도 이 지점과 이어집니다.

## 체크리스트

- [ ] IngressController가 설치되어 있는가
- [ ] `pathType`을 명시했는가
- [ ] TLS 자동화 방안을 준비했는가
- [ ] 외부 진입점을 가능한 한 통합했는가

## 연습 문제

1. Ingress와 IngressController의 차이를 한 줄로 설명해 보세요.
2. TLS 종료를 Ingress에서 처리할 때 좋은 점을 하나 적어 보세요.
3. Gateway API가 해결하려는 한계를 한 줄로 정리해 보세요.

## 마무리와 다음 글

이 글에서는 Ingress를 여러 서비스를 하나의 외부 진입점 뒤에 두고, 도메인과 경로 기준으로 HTTP 요청을 나누는 규칙 객체로 정리했습니다. 실제 동작은 IngressController가 책임지고, TLS 종료까지 이 지점에 모으면 외부 노출 구조가 훨씬 단순해집니다.

다음 글에서는 네트워크 경로가 아니라 애플리케이션 설정과 민감한 값을 어떻게 분리하는지, ConfigMap과 Secret을 보겠습니다.

## 처음 질문으로 돌아가기

- **Ingress와 IngressController는 왜 따로 이해해야 할까요?**
  - 본문의 기준은 Ingress를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **여러 서비스를 하나의 도메인 아래에서 어떻게 나눌 수 있을까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **`host`, `path`, `pathType`은 어떤 차이를 만들까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Kubernetes 101 (1/10): Kubernetes란 무엇인가?](./01-what-is-kubernetes.md)
- [Kubernetes 101 (2/10): Pod](./02-pod.md)
- [Kubernetes 101 (3/10): Deployment](./03-deployment.md)
- [Kubernetes 101 (4/10): Service](./04-service.md)
- **Ingress (현재 글)**
- ConfigMap과 Secret (예정)
- Volume (예정)
- HPA (예정)
- Helm (예정)
- 운영 관점의 Kubernetes (예정)

<!-- toc:end -->

## 참고 자료

- [Ingress (Kubernetes)](https://kubernetes.io/docs/concepts/services-networking/ingress/)
- [Ingress Controllers](https://kubernetes.io/docs/concepts/services-networking/ingress-controllers/)
- [cert-manager](https://cert-manager.io/docs/)
- [Gateway API](https://gateway-api.sigs.k8s.io/)
- [Troubleshooting Ingress](https://kubernetes.io/docs/tasks/access-application-cluster/ingress-minikube/)

Tags: Kubernetes, Ingress, HTTP, TLS, DevOps
