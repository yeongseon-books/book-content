---
series: kubernetes-101
episode: 4
title: "Kubernetes 101 (4/10): Service"
status: published
published_to:
  tistory:
    url: "https://yeongseonchoe.tistory.com/266"
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

![Kubernetes 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/kubernetes-101/04/04-01-concept-at-a-glance.ko.png)
*Kubernetes 101 4장 흐름 개요*

> Service는 단순 포트 노출이 아니라 '라벨로 선택된 파드 집합'에 안정적인 가상 IP와 DNS 이름을 부여하는 추상화입니다 — Pod IP가 끊임없이 바뀌어도 호출자는 같은 이름으로 같은 역할을 호출할 수 있게 만든다는 점이 서비스 디스커버리의 핵심입니다.

## 이 글에서 다룰 문제

- Service는 정확히 어떤 문제를 해결할까요?
- ClusterIP, NodePort, LoadBalancer는 언제 갈라질까요?
- selector와 labels는 왜 정확히 맞아야 할까요?
- 이 리소스의 설정을 잘못하면 운영에서 어떤 장애가 발생할까요?
- 프로덕션 환경에서 이 기능을 쓸 때 가장 먼저 점검할 항목은 무엇일까요?

마이크로서비스 구조에서는 애플리케이션이 다른 애플리케이션을 이름으로 호출해야 합니다. 그런데 Pod IP를 직접 쓰는 방식은 재시작 한 번으로 바로 깨집니다. Kubernetes에서 내부 통신이 안정적으로 보이려면 중간에서 변하는 파드 집합을 고정된 이름으로 가려 주는 계층이 필요합니다.

그 역할을 Service가 맡습니다. 많은 입문자가 Service를 단순히 외부 노출용으로만 이해하지만, 실제로는 내부 통신에서 더 자주 중요합니다. Service를 이해하지 못하면 Ingress도, 서비스 디스커버리도, DNS 기반 호출도 모두 흐릿하게 남습니다.

## 한눈에 보는 구조

Service는 특정 파드를 직접 고정해 가리키지 않습니다. 라벨로 선택된 파드 집합을 뒤에 두고, 앞단에는 안정적인 가상 IP와 이름을 제공합니다. 클라이언트는 뒤에서 어떤 파드가 바뀌는지 신경 쓰지 않고 Service 이름만 알면 됩니다.

- ClusterIP: 클러스터 내부에서만 쓰는 기본 가상 IP입니다.
- NodePort: 모든 노드의 특정 포트를 통해 접근하게 하는 방식입니다.
- LoadBalancer: 클라우드 로드 밸런서를 연결해 외부 진입점을 여는 방식입니다.
- selector: 라벨로 파드 집합을 고르는 조건입니다.
- DNS 이름: `svc.namespace.svc.cluster.local` 형태의 서비스 이름입니다.

## Service 타입 비교

| 타입 | 접근 범위 | 사용 시나리오 | 특징 |
|---|---|---|---|
| ClusterIP | 클러스터 내부 | 서비스 간 내부 통신 | 기본값, 외부 접근 불가 |
| NodePort | 외부 (노드 IP + 포트) | 개발/테스트 환경 외부 접근 | 30000-32767 포트 범위 |
| LoadBalancer | 외부 (클라우드 LB) | 운영 환경 외부 서비스 | 클라우드 과금 발생 |
| ExternalName | 외부 DNS 이름 | 외부 서비스를 내부 이름으로 | CNAME 매핑 |
| Headless | 파드 IP 직접 | StatefulSet, 서비스 디스커버리 | ClusterIP: None |

## Service YAML 완전 이해

### ClusterIP (기본)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web
  namespace: default
spec:
  selector:
    app: web          # 이 라벨을 가진 파드에게 트래픽 전달
  ports:
  - name: http
    protocol: TCP
    port: 80          # Service가 노출하는 포트
    targetPort: 8080  # 파드가 실제로 수신하는 포트
  type: ClusterIP     # 기본값 (생략 가능)
```

이 설정은 `app: web` 라벨을 가진 파드 집합을 `web`이라는 이름의 Service 뒤에 묶습니다. 여기서 가장 중요한 값은 `selector`입니다.

### NodePort

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-nodeport
spec:
  selector:
    app: web
  ports:
  - port: 80
    targetPort: 8080
    nodePort: 30080   # 30000-32767 범위에서 지정 (생략하면 자동 할당)
  type: NodePort
```

### LoadBalancer

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-lb
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: "nlb"  # AWS NLB 사용
spec:
  selector:
    app: web
  ports:
  - port: 80
    targetPort: 8080
  type: LoadBalancer
```

### Headless Service (StatefulSet용)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: db-headless
spec:
  clusterIP: None   # Headless: DNS가 파드 IP를 직접 반환
  selector:
    app: db
  ports:
  - port: 5432
    targetPort: 5432
```

## 단계별로 Service 노출해 보기

### 1단계 — 적용 후 조회

```bash
kubectl apply -f service.yaml
kubectl get svc web
```

출력 예시:
```
NAME   TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)   AGE
web    ClusterIP   10.96.150.200   <none>        80/TCP    5s
```

적용 후 바로 상태를 보는 습관이 중요합니다. Service 자체는 생성됐더라도 뒤에 연결된 파드가 없으면 실제 라우팅은 되지 않기 때문입니다.

### 2단계 — Endpoints 확인 (핵심)

```bash
kubectl get endpoints web
```

출력 예시:
```
NAME   ENDPOINTS                       AGE
web    10.244.1.5:8080,10.244.2.3:8080   5s
```

Endpoints가 비어 있으면 selector와 파드 라벨이 일치하지 않는다는 신호입니다. Service 문제의 절반 이상이 여기서 시작됩니다.

### 3단계 — DNS 확인

```bash
# 임시 파드로 DNS 조회
kubectl run dnscheck --rm -i --restart=Never --image=busybox -- \
  nslookup web.default.svc.cluster.local
```

출력 예시:
```
Server:    10.96.0.10
Address 1: 10.96.0.10 kube-dns.kube-system.svc.cluster.local

Name:      web.default.svc.cluster.local
Address 1: 10.96.150.200 web.default.svc.cluster.local
```

Service를 이해할 때는 DNS 관점이 중요합니다. 내부 서비스 간 통신을 IP가 아니라 이름으로 바꾸는 핵심 고리가 바로 여기입니다.

### 4단계 — 실제 통신 테스트

```bash
# 같은 네임스페이스에서 서비스 이름으로 호출
kubectl run curltest --rm -i --restart=Never --image=curlimages/curl -- \
  curl http://web:80

# 다른 네임스페이스에서 전체 이름으로 호출
kubectl run curltest -n other-ns --rm -i --restart=Never --image=curlimages/curl -- \
  curl http://web.default.svc.cluster.local:80
```

### 5단계 — 정리

```bash
kubectl delete svc web
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

## 트러블슈팅 시나리오

### 시나리오 1: Endpoints 비어 있음

```bash
# 문제 확인
kubectl get endpoints web
# NAME   ENDPOINTS   AGE
# web    <none>      1m

# 원인 분석: selector와 파드 라벨 비교
kubectl get svc web -o jsonpath='{.spec.selector}'
# {"app":"web"}

kubectl get pods -l app=web
# 파드가 없거나 라벨이 다른 경우

# 해결: 파드 라벨과 Service selector를 일치시킴
kubectl label pod <pod-name> app=web --overwrite
```

### 시나리오 2: targetPort 불일치

```bash
# 파드가 실제로 리스닝하는 포트 확인
kubectl exec <pod-name> -- ss -tlnp
# 또는
kubectl exec <pod-name> -- netstat -tlnp

# Service targetPort와 비교 후 수정
kubectl patch svc web -p '{"spec":{"ports":[{"port":80,"targetPort":8080}]}}'
```

### 시나리오 3: 다른 네임스페이스에서 접근 실패

```bash
# 전체 DNS 이름 형식 확인
# <서비스명>.<네임스페이스>.svc.cluster.local
# 예: web.production.svc.cluster.local

# 짧은 이름은 같은 네임스페이스에서만 작동
# 다른 네임스페이스에서는 반드시 전체 이름 또는 네임스페이스 포함 이름 사용
```

## 자주 하는 실수

| 실수 | 문제 | 올바른 방법 |
|---|---|---|
| selector와 labels 불일치 | Endpoints 비어 트래픽 전달 안 됨 | `kubectl get endpoints`로 항상 확인 |
| NodePort를 운영 외부 진입점으로 사용 | 보안·관리 어려움 | 운영 환경에는 LoadBalancer + Ingress 조합 |
| Pod IP 직접 호출 | 재시작 시 통신 단절 | Service DNS 이름으로 호출 |
| 불필요한 Headless Service 사용 | 부하 분산 이점 상실 | StatefulSet 등 특수 목적에만 사용 |
| 네임스페이스 미포함 DNS 이름 사용 | 다른 네임스페이스에서 실패 | 전체 DNS 이름 또는 네임스페이스 명시 |

## 실무에서는 이렇게 봅니다

실무에서는 ClusterIP가 내부 통신의 기본값이고, 외부 진입은 LoadBalancer와 Ingress가 나눠 맡는 구성이 흔합니다. Service는 그 사이에서 안정적인 서비스 이름과 백엔드 파드 집합을 연결하는 핵심 고리입니다.

시니어 엔지니어는 Service 이름을 사실상 API 계약처럼 봅니다. 파드가 어떻게 바뀌든, 내부 호출자가 기대하는 이름과 포트는 오래 유지되기 때문입니다. 그래서 라벨 설계와 네이밍이 운영 품질에 직접 영향을 줍니다.

```bash
# 실무에서 Service 운영 시 자주 쓰는 명령 모음
kubectl get svc -A                                   # 전체 네임스페이스 서비스 목록
kubectl get endpoints -A                             # 전체 Endpoints 확인
kubectl describe svc web                             # 상세 이벤트 포함
kubectl port-forward svc/web 8080:80                 # 로컬에서 서비스 접근
kubectl run tmp --rm -it --image=busybox -- wget -qO- http://web  # 클러스터 내 접근 테스트
```

## 운영 체크리스트

- [ ] selector가 실제 파드 라벨과 맞는가
- [ ] Service 타입을 명시했는가
- [ ] 내부 호출이 DNS 이름 기준으로 이뤄지는가
- [ ] 외부 노출은 Ingress 중심으로 검토했는가
- [ ] Endpoints에 실제 파드 IP가 연결됐는가
- [ ] targetPort가 컨테이너 실제 수신 포트와 일치하는가

## 연습 문제

1. ClusterIP와 LoadBalancer의 차이를 한 줄로 설명해 보세요.
2. selector가 왜 중요한지 한 줄로 적어 보세요.
3. Headless Service의 대표적인 사용 예를 하나 떠올려 보세요.
4. `kubectl get endpoints web`에서 `<none>`이 나오면 무엇을 먼저 확인해야 하나요?
5. 같은 네임스페이스와 다른 네임스페이스에서의 DNS 이름 형식 차이를 설명해 보세요.

## Kubernetes DNS 작동 원리

ClusterDNS(CoreDNS)는 Service 이름을 ClusterIP로 변환해 줍니다. 이 흐름을 이해하면 통신 오류를 빠르게 진단할 수 있습니다.

```
DNS 조회 흐름:

애플리케이션이 "web" 호출
  ↓
/etc/resolv.conf 에서 search 도메인 확인
  └─ search default.svc.cluster.local svc.cluster.local cluster.local
  ↓
CoreDNS가 web.default.svc.cluster.local 조회
  ↓
ClusterIP 10.96.150.200 반환
  ↓
kube-proxy(iptables/IPVS)가 실제 Pod IP로 로드밸런싱
```

```bash
# 파드 안의 DNS 설정 확인
kubectl exec <pod-name> -- cat /etc/resolv.conf

# 서비스 DNS 조회 형식 정리
# 같은 네임스페이스:  web
# 다른 네임스페이스:  web.production
# 완전한 이름:        web.production.svc.cluster.local

# CoreDNS 파드 확인
kubectl get pods -n kube-system -l k8s-app=kube-dns
```

## NetworkPolicy로 Service 접근 제한

Service는 기본적으로 클러스터 안의 모든 파드에서 접근할 수 있습니다. NetworkPolicy를 더하면 누가 어떤 Service에 접근할 수 있는지 제한할 수 있습니다.

```yaml
# web Service에는 frontend 파드만 접근 허용
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-web
spec:
  podSelector:
    matchLabels:
      app: web            # 이 라벨의 파드에 적용
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend   # 이 라벨의 파드만 접근 허용
    ports:
    - protocol: TCP
      port: 80
```

```bash
# NetworkPolicy 확인
kubectl get networkpolicy
kubectl describe networkpolicy allow-frontend-to-web
```

## 마무리와 다음 글

이 글에서는 Service를 변하는 파드 집합 앞에 안정적인 주소와 이름을 붙여 주는 객체로 정리했습니다. Kubernetes 네트워킹이 복잡해 보일 때도, 먼저 Service가 어떤 파드 집합을 어떤 이름으로 대표하는지부터 보면 흐름이 빠르게 정리됩니다.

다음 글에서는 내부 통신을 넘어서, 외부에서 들어오는 HTTP 요청을 도메인과 경로 기준으로 어떻게 나누는지 Ingress를 보겠습니다.

## 정리

Service는 단순 포트 노출이 아니라 '라벨로 선택된 파드 집합'에 안정적인 가상 IP와 DNS 이름을 부여하는 추상화입니다 — Pod IP가 끊임없이 바뀌어도 호출자는 같은 이름으로 같은 역할을 호출할 수 있게 만든다는 점이 서비스 디스커버리의 핵심입니다. 이 글에서는 한눈에 보는 구조부터 마무리와 다음 글까지 이 원칙을 구체적으로 살펴봤습니다. 핵심은 개념을 외우는 것이 아니라 실무에서 어떤 판단을 바꾸는지 이해하는 데 있습니다.

## 처음 질문으로 돌아가기

- **Service는 정확히 어떤 문제를 해결할까요?**
  - Pod IP가 재시작마다 바뀌는 문제를 해결합니다. 라벨로 선택된 파드 집합을 고정된 이름과 가상 IP로 추상화해, 호출자가 파드 변화를 신경 쓰지 않아도 됩니다.
- **ClusterIP, NodePort, LoadBalancer는 언제 갈라질까요?**
  - 내부 통신이면 ClusterIP, 개발·테스트 외부 접근이면 NodePort, 운영 외부 서비스이면 LoadBalancer를 선택합니다.
- **selector와 labels는 왜 정확히 맞아야 할까요?**
  - selector가 맞지 않으면 Endpoints가 비어 트래픽이 전달되지 않습니다. Service가 만들어졌다고 동작하는 것이 아니라, 파드와 연결됐을 때 비로소 의미가 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Kubernetes 101 (1/10): Kubernetes란 무엇인가?](./01-what-is-kubernetes.md)
- [Kubernetes 101 (2/10): Pod](./02-pod.md)
- [Kubernetes 101 (3/10): Deployment](./03-deployment.md)
- **Kubernetes 101 (4/10): Service (현재 글)**
- [Kubernetes 101 (5/10): Ingress](./05-ingress.md)
- [Kubernetes 101 (6/10): ConfigMap과 Secret](./06-configmap-and-secret.md)
- [Kubernetes 101 (7/10): Volume](./07-volume.md)
- [Kubernetes 101 (8/10): HPA](./08-hpa.md)
- [Kubernetes 101 (9/10): Helm](./09-helm.md)
- [운영 관점의 Kubernetes](./10-kubernetes-in-operation.md)

<!-- toc:end -->
