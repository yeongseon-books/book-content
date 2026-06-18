---
series: kubernetes-101
episode: 4
title: "바이브코딩을 위한 Kubernetes 기초 (4/10): Service"
status: draft
targets:
  wordpress: true
language: ko
tags:
  - 바이브코딩
  - Kubernetes
  - Service
  - Networking
  - DevOps
seo_description: AI가 생성한 Service YAML을 제대로 이해하기 위해 알아야 할 ClusterIP/NodePort/LoadBalancer 차이와 DNS 기반 서비스 디스커버리를 바이브코딩 관점에서 정리합니다.
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 Kubernetes 기초 (4/10): Service

이 글은 **바이브코딩을 위한 Kubernetes 기초** 시리즈의 네 번째 글입니다. AI와 함께 K8s YAML을 만들기 전에, Kubernetes가 어떻게 동작하는지 먼저 이해하는 것을 목표로 합니다.

---

AI에게 "백엔드 API를 프론트엔드에서 호출하는 Kubernetes 구성 만들어줘"라고 하면 Deployment와 함께 Service YAML이 나옵니다. 그런데 왜 Service가 필요한지 이해하지 못하면 제대로 구성하기 어렵고, 서비스가 연결이 안 될 때 원인도 찾기 어렵습니다.

많은 바이브코딩 사용자들이 Service를 "포트 노출용"으로만 이해합니다. 하지만 Service의 진짜 역할은 내부 통신에서 더 중요합니다. 파드가 재시작되면 IP가 바뀌는데, Service는 그 변화에도 항상 같은 이름으로 파드를 찾을 수 있게 해주는 안정적인 주소입니다.

> Service는 단순 포트 노출이 아니라 '라벨로 선택된 파드 집합'에 안정적인 가상 IP와 DNS 이름을 부여하는 추상화입니다. Pod IP가 끊임없이 바뀌어도 호출자는 같은 이름으로 같은 역할을 호출할 수 있게 만든다는 점이 서비스 디스커버리의 핵심입니다.

## 이 글에서 답하는 질문들

- Service는 정확히 어떤 문제를 해결할까요?
- ClusterIP, NodePort, LoadBalancer는 언제 갈라질까요?
- selector와 labels는 왜 정확히 맞아야 할까요?
- Service를 잘못 설정하면 운영에서 어떤 장애가 생길까요?
- AI가 생성한 Service YAML에서 가장 먼저 확인할 항목은 무엇일까요?

## 바이브코딩 관점: 파드 IP를 직접 쓰면 안 되는 이유

AI에게 "프론트엔드에서 백엔드 API URL은 뭐야?"라고 물으면, Pod IP를 직접 쓰지 말고 Service 이름을 쓰라고 알려줄 것입니다. 이유는 간단합니다.

파드는 재시작하거나 재배치되면 IP가 바뀝니다. `192.168.1.100`이라고 하드코딩했다가 파드가 재시작되면 다른 IP로 바뀌어 연결이 끊깁니다. Service는 파드 IP가 바뀌어도 `backend-svc`라는 이름으로 항상 같은 파드 집합에 접근할 수 있게 해줍니다.

Kubernetes 클러스터 안에서는 `http://backend-svc`처럼 Service 이름으로 호출하는 것이 기본입니다. 이 이름이 내부 DNS를 통해 현재 살아있는 파드들의 IP로 변환됩니다.

## Service 구조: 한눈에 보기

**주요 개념**

- **ClusterIP**: 클러스터 내부에서만 사용하는 기본 가상 IP. 내부 서비스 간 통신에 사용
- **NodePort**: 모든 노드의 특정 포트를 통해 외부 접근. 개발/테스트에 유용
- **LoadBalancer**: 클라우드 로드 밸런서를 연결해 외부 진입점을 여는 방식
- **selector**: 라벨로 파드 집합을 고르는 조건. Deployment의 labels와 반드시 일치해야 함
- **DNS 이름**: `서비스명.네임스페이스.svc.cluster.local` 형태로 클러스터 내부 DNS 조회 가능

## Service 도입 전과 후

**Service 없이 Pod IP로 통신할 때**

클라이언트가 Pod IP를 직접 호출해야 합니다. 파드가 재시작되거나 재배치되는 순간 IP가 바뀌어 연결이 끊깁니다.

**Service를 두면**

클라이언트는 DNS 이름으로 Service를 호출합니다. Service가 뒤의 파드 집합으로 트래픽을 분산합니다. 파드가 바뀌어도 호출 방식은 바뀌지 않습니다.

## 단계별 Service 다루기

### 1단계: Service 매니페스트 작성

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web
spec:
  selector:
    app: web
  ports:
  - port: 80
    targetPort: 80
```

가장 중요한 값은 `selector`입니다. 여기서 `app: web`은 Deployment의 `template.metadata.labels`에 있는 `app: web`과 정확히 일치해야 합니다. 이 연결이 Service와 파드를 묶는 핵심입니다.

### 2단계: Endpoints 확인

```bash
kubectl get svc web
kubectl get endpoints web
```

Service가 생성됐더라도 `endpoints`가 비어 있으면 실제 라우팅이 안 됩니다. `selector`와 파드의 `labels`가 맞는지 먼저 확인합니다.

### 3단계: DNS 확인

```bash
kubectl run dnscheck --rm -i --restart=Never --image=busybox \
  -- nslookup web.default.svc.cluster.local
```

Service를 이해할 때 DNS 관점이 중요합니다. 내부 서비스 간 통신을 IP가 아니라 이름으로 바꾸는 핵심 고리입니다.

### 4단계: 외부 노출이 필요하면

```yaml
# NodePort: 개발/테스트용 외부 접근
spec:
  type: NodePort
  selector:
    app: web
  ports:
  - port: 80
    targetPort: 80
    nodePort: 30080  # 30000-32767 범위

# LoadBalancer: 클라우드 환경 운영용 외부 접근
spec:
  type: LoadBalancer
  selector:
    app: web
  ports:
  - port: 80
    targetPort: 80
```

운영 환경에서 외부 트래픽은 보통 LoadBalancer + Ingress 조합으로 처리합니다. NodePort는 테스트 목적 이외에는 잘 사용하지 않습니다.

## 자주 하는 실수 5가지

| 실수 | 실제 문제 | 올바른 접근 |
|------|-----------|-------------|
| selector와 labels 불일치 | Endpoints가 비어있어 트래픽이 안 감 | AI YAML에서 selector-labels 연결 반드시 확인 |
| Pod IP를 직접 호출 | 파드 재시작 시 연결 끊김 | 항상 Service 이름으로 호출 |
| NodePort를 운영 외부 진입점으로 사용 | 포트 관리 복잡, 보안 취약 | LoadBalancer + Ingress 사용 |
| 다른 네임스페이스에서 짧은 이름으로 호출 | DNS 해석 실패 | 네임스페이스 포함한 FQDN 사용 |
| targetPort와 컨테이너 실제 포트 불일치 | DNS 성공해도 응답 실패 | 컨테이너가 실제 listen하는 포트 확인 |

## AI 팁: Service YAML 요청과 검토

```
# Service 생성 요청 예시
"이 Deployment(이름: backend, labels: app: backend)를
내부에서 port 8080으로 접근할 수 있는 ClusterIP Service를 만들어줘.
selector가 Deployment의 labels와 정확히 일치하도록 해줘."

# 타입 선택 질문 예시
"클러스터 내부 통신, 개발 환경 테스트, 운영 외부 노출
각각 어떤 Service 타입을 써야 해? 이유도 설명해줘."

# 연결 문제 진단 요청 예시
"kubectl get endpoints 결과가 비어 있어.
Service YAML과 Deployment YAML을 보고 문제 원인을 찾아줘."
```

## 운영 체크리스트

- [ ] selector가 실제 파드 labels와 정확히 일치하는가
- [ ] targetPort가 컨테이너가 실제로 listen하는 포트와 같은가
- [ ] Service 타입을 명시했는가(기본값은 ClusterIP)
- [ ] 내부 호출이 Pod IP가 아닌 Service DNS 이름 기준으로 이뤄지는가
- [ ] 외부 노출은 Ingress 중심으로 검토했는가

## 처음 질문으로 돌아가기

**Service는 정확히 어떤 문제를 해결할까요?**
Pod IP가 재시작마다 바뀌는 문제를 해결합니다. Service는 라벨로 선택한 파드 집합 앞에 안정적인 가상 IP와 DNS 이름을 붙여, 클라이언트가 파드 변화와 무관하게 항상 같은 이름으로 서비스를 찾을 수 있게 합니다.

**ClusterIP, NodePort, LoadBalancer는 언제 갈라질까요?**
클러스터 내부 통신만 필요하면 ClusterIP(기본값)를 씁니다. 외부에서 직접 접근하는 개발/테스트가 필요하면 NodePort를 씁니다. 운영 환경에서 외부 트래픽을 받아야 하면 LoadBalancer를 씁니다. 다만 운영에서는 여러 서비스를 하나의 진입점으로 묶는 Ingress와 함께 쓰는 경우가 많습니다.

**selector와 labels는 왜 정확히 맞아야 할까요?**
Service는 특정 파드를 직접 고정해 가리키지 않고, selector에 맞는 labels를 가진 파드들을 동적으로 선택합니다. 두 값이 어긋나면 Endpoints가 비어 Serivce가 있어도 트래픽이 어디도 가지 않습니다.

## 정리

이번 글에서 다룬 핵심은 세 가지입니다. 첫째, Service는 변하는 Pod IP 문제를 해결하는 안정적인 네트워크 추상화입니다. 둘째, selector와 labels가 정확히 일치해야 Service가 파드와 연결됩니다. 셋째, 내부 통신은 Service DNS 이름을 쓰고, 외부 노출은 목적에 따라 타입을 구분해야 합니다.

다음 글에서는 외부 트래픽을 도메인과 경로 기준으로 여러 Service에 나누는 Ingress를 바이브코딩 관점에서 살펴보겠습니다.

## 참고 자료

- [Kubernetes 공식 문서: Service](https://kubernetes.io/ko/docs/concepts/services-networking/service/)
- [Kubernetes 공식 문서: DNS](https://kubernetes.io/ko/docs/concepts/services-networking/dns-pod-service/)
- [Kubernetes 101 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/kubernetes-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Kubernetes 기초 (1/10): Kubernetes란 무엇인가?
- 바이브코딩을 위한 Kubernetes 기초 (2/10): Pod
- 바이브코딩을 위한 Kubernetes 기초 (3/10): Deployment
- **바이브코딩을 위한 Kubernetes 기초 (4/10): Service (현재 글)**
- 바이브코딩을 위한 Kubernetes 기초 (5/10): Ingress
- 바이브코딩을 위한 Kubernetes 기초 (6/10): ConfigMap과 Secret
- 바이브코딩을 위한 Kubernetes 기초 (7/10): Volume
- 바이브코딩을 위한 Kubernetes 기초 (8/10): HPA
- 바이브코딩을 위한 Kubernetes 기초 (9/10): Helm
- 바이브코딩을 위한 Kubernetes 기초 (10/10): 운영 관점의 Kubernetes

<!-- toc:end -->

Tags: 바이브코딩, Kubernetes, Service, Networking, DevOps
