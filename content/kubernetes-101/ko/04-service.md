---
series: kubernetes-101
episode: 4
title: "Kubernetes 101 (4/10): Service"
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
  - Service
  - Networking
  - DNS
  - DevOps
seo_description: Service가 Pod 집합에 안정적인 주소와 이름을 주는 방식을 설명합니다.
last_reviewed: '2026-05-15'
---

# Kubernetes 101 (4/10): Service

Pod를 여러 개 띄우기 시작하면 다음 문제가 바로 등장합니다. Pod IP가 계속 바뀌는데, 다른 서비스나 사용자는 그 파드를 어떻게 안정적으로 찾아야 할까 하는 문제입니다. 파드가 재시작되거나 새로 생성될 때마다 주소가 달라지면 애플리케이션끼리 서로를 부르기가 금방 불안정해집니다.

이 글은 Kubernetes 101 시리즈의 4번째 글입니다.

여기서는 Service를 단순한 포트 노출 기능이 아니라, 라벨로 선택된 파드 집합에 안정적인 가상 IP와 DNS 이름을 부여하는 네트워킹 기본 객체라는 관점에서 정리하겠습니다.

## 먼저 던지는 질문

- Service는 정확히 어떤 문제를 해결할까요?
- ClusterIP, NodePort, LoadBalancer는 언제 갈라질까요?
- selector와 labels는 왜 정확히 맞아야 할까요?

## 큰 그림

![Kubernetes 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/kubernetes-101/04/04-01-concept-at-a-glance.ko.png)

*Kubernetes 101 4장 흐름 개요*

이 그림에서는 Service를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> Service의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 중요한가

마이크로서비스 구조에서는 애플리케이션이 다른 애플리케이션을 이름으로 호출해야 합니다. 그런데 Pod IP를 직접 쓰는 방식은 재시작 한 번으로 바로 깨집니다. Kubernetes에서 내부 통신이 안정적으로 보이려면 중간에서 변하는 파드 집합을 고정된 이름으로 가려 주는 계층이 필요합니다.

그 역할을 Service가 맡습니다. 많은 입문자가 Service를 단순히 외부 노출용으로만 이해하지만, 실제로는 내부 통신에서 더 자주 중요합니다. Service를 이해하지 못하면 Ingress도, 서비스 디스커버리도, DNS 기반 호출도 모두 흐릿하게 남습니다.

## 한눈에 보는 구조

Service는 특정 파드를 직접 고정해 가리키지 않습니다. 라벨로 선택된 파드 집합을 뒤에 두고, 앞단에는 안정적인 가상 IP와 이름을 제공합니다. 클라이언트는 뒤에서 어떤 파드가 바뀌는지 신경 쓰지 않고 Service 이름만 알면 됩니다.

## 핵심 용어

- ClusterIP: 클러스터 내부에서만 쓰는 기본 가상 IP입니다.
- NodePort: 모든 노드의 특정 포트를 통해 접근하게 하는 방식입니다.
- LoadBalancer: 클라우드 로드 밸런서를 연결해 외부 진입점을 여는 방식입니다.
- selector: 라벨로 파드 집합을 고르는 조건입니다.
- DNS 이름: `svc.namespace.svc.cluster.local` 형태의 서비스 이름입니다.

## 도입 전과 후

Service가 없으면 클라이언트가 Pod IP를 직접 호출해야 합니다. 이 방식은 파드 재시작이나 재배치가 일어나는 순간 바로 깨집니다.

Service를 두면 클라이언트는 DNS 이름으로 Service를 호출하고, Service가 뒤의 파드 집합으로 트래픽을 보냅니다. 파드가 바뀌어도 호출 방식은 바뀌지 않습니다. 이것이 내부 통신 안정성의 출발점입니다.

## 단계별로 Service 노출해 보기

### 1단계 — Service 매니페스트 작성

```python
"""
apiVersion: v1
kind: Service
metadata: {name: web}
spec:
  selector: {app: web}
  ports:
  - port: 80
    targetPort: 80
"""
```

이 설정은 `app: web` 라벨을 가진 파드 집합을 `web`이라는 이름의 Service 뒤에 묶습니다. 여기서 가장 중요한 값은 `selector`입니다.

### 2단계 — 적용 후 조회

```python
import subprocess

def apply_and_get(path):
    subprocess.run(["kubectl", "apply", "-f", path], check=True)
    return subprocess.run(
        ["kubectl", "get", "svc", "web"],
        capture_output=True, text=True, check=True,
    ).stdout
```

적용 후 바로 상태를 보는 습관이 중요합니다. Service 자체는 생성됐더라도 뒤에 연결된 파드가 없으면 실제 라우팅은 되지 않기 때문입니다.

### 3단계 — DNS 확인

```python
def dns_check(target):
    res = subprocess.run([
        "kubectl", "run", "tmp", "--rm", "-i", "--restart=Never",
        "--image=busybox", "--", "nslookup", target,
    ], capture_output=True, text=True, check=True)
    return res.stdout
```

Service를 이해할 때는 DNS 관점이 중요합니다. 내부 서비스 간 통신을 IP가 아니라 이름으로 바꾸는 핵심 고리가 바로 여기입니다.

### 4단계 — NodePort로 변경

```python
def to_nodeport(svc):
    subprocess.run([
        "kubectl", "patch", "svc", svc, "-p",
        '{"spec": {"type": "NodePort"}}',
    ], check=True)
```

Service 타입을 바꾸면 접근 경로가 달라집니다. 다만 NodePort는 외부 접근 실험에는 편해도, 보통 운영의 최종 외부 진입점으로 삼는 경우는 드뭅니다.

### 5단계 — 정리

```python
def delete(svc):
    subprocess.run(["kubectl", "delete", "svc", svc], check=True)
```

리소스를 지울 때는 Service 삭제 자체보다, 이 Service를 바라보는 다른 애플리케이션이 있는지 먼저 보는 편이 중요합니다. 이름 기반 호출 구조에서는 이름 하나가 계약이 되기 때문입니다.

## 검증 흐름

```bash
kubectl get svc web
kubectl get endpoints web
kubectl run dnscheck --rm -i --restart=Never --image=busybox -- nslookup web.default.svc.cluster.local
```

**예상되는 결과:** Service에는 ClusterIP가 할당돼야 하고, Endpoints에는 실제 Pod IP가 하나 이상 연결돼 있어야 합니다. DNS 조회는 서비스 이름이 클러스터 내부에서 해석된다는 사실을 확인하는 가장 빠른 점검입니다.

**먼저 의심할 실패 모드:**

- Service는 있는데 Endpoints가 비어 있으면 selector와 labels 불일치를 먼저 봅니다.
- DNS는 되는데 응답이 실패하면 `targetPort`와 컨테이너 listen port가 다른지 확인합니다.
- 다른 네임스페이스에서 실패하면 Service 자체보다 호출 이름에 네임스페이스를 빠뜨린 경우가 흔합니다.

## 이 코드에서 먼저 봐야 할 점

- `selector`는 Deployment가 붙인 라벨과 정확히 맞아야 합니다.
- `targetPort`는 컨테이너가 실제로 듣는 포트입니다.
- DNS 이름이 서비스 호출의 표준 경로가 됩니다.

이 셋이 연결되면 Service를 단순 프록시가 아니라 네트워크 계약으로 볼 수 있습니다. 호출하는 쪽은 이름만 알고, 실제 파드 교체는 뒤에서 계속 일어나도 괜찮아집니다.

## 자주 하는 실수 다섯 가지

1. selector와 labels가 어긋나는데도 Service가 동작할 것이라 기대합니다.
2. NodePort를 운영 환경의 최종 외부 진입점으로 씁니다.
3. Pod IP를 직접 호출합니다.
4. 일반적인 경우에도 Headless Service부터 꺼내 듭니다.
5. DNS 이름에서 네임스페이스 개념을 무시합니다.

## 실무에서는 이렇게 봅니다

실무에서는 ClusterIP가 내부 통신의 기본값이고, 외부 진입은 LoadBalancer와 Ingress가 나눠 맡는 구성이 흔합니다. Service는 그 사이에서 안정적인 서비스 이름과 백엔드 파드 집합을 연결하는 핵심 고리입니다.

시니어 엔지니어는 Service 이름을 사실상 API 계약처럼 봅니다. 파드가 어떻게 바뀌든, 내부 호출자가 기대하는 이름과 포트는 오래 유지되기 때문입니다. 그래서 라벨 설계와 네이밍이 운영 품질에 직접 영향을 줍니다.

## 체크리스트

- [ ] selector가 실제 파드 라벨과 맞는가
- [ ] Service 타입을 명시했는가
- [ ] 내부 호출이 DNS 이름 기준으로 이뤄지는가
- [ ] 외부 노출은 Ingress 중심으로 검토했는가

## 연습 문제

1. ClusterIP와 LoadBalancer의 차이를 한 줄로 설명해 보세요.
2. selector가 왜 중요한지 한 줄로 적어 보세요.
3. Headless Service의 대표적인 사용 예를 하나 떠올려 보세요.

## 마무리와 다음 글

이 글에서는 Service를 변하는 파드 집합 앞에 안정적인 주소와 이름을 붙여 주는 객체로 정리했습니다. Kubernetes 네트워킹이 복잡해 보일 때도, 먼저 Service가 어떤 파드 집합을 어떤 이름으로 대표하는지부터 보면 흐름이 빠르게 정리됩니다.

다음 글에서는 내부 통신을 넘어서, 외부에서 들어오는 HTTP 요청을 도메인과 경로 기준으로 어떻게 나누는지 Ingress를 보겠습니다.

## 처음 질문으로 돌아가기

- **Service는 정확히 어떤 문제를 해결할까요?**
  - 본문의 기준은 Service를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **ClusterIP, NodePort, LoadBalancer는 언제 갈라질까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **selector와 labels는 왜 정확히 맞아야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Kubernetes 101 (1/10): Kubernetes란 무엇인가?](./01-what-is-kubernetes.md)
- [Kubernetes 101 (2/10): Pod](./02-pod.md)
- [Kubernetes 101 (3/10): Deployment](./03-deployment.md)
- **Service (현재 글)**
- Ingress (예정)
- ConfigMap과 Secret (예정)
- Volume (예정)
- HPA (예정)
- Helm (예정)
- 운영 관점의 Kubernetes (예정)

<!-- toc:end -->

## 참고 자료

- [Service (Kubernetes)](https://kubernetes.io/docs/concepts/services-networking/service/)
- [DNS for Services and Pods](https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/)
- [Service types](https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types)
- [Headless Services](https://kubernetes.io/docs/concepts/services-networking/service/#headless-services)
- [Debug Services](https://kubernetes.io/docs/tasks/debug/debug-application/debug-service/)

Tags: Kubernetes, Service, Networking, DNS, DevOps
