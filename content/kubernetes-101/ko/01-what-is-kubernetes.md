---
series: kubernetes-101
episode: 1
title: "Kubernetes 101 (1/10): Kubernetes란 무엇인가?"
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
  - Orchestration
  - Containers
  - DevOps
  - SRE
seo_description: Kubernetes의 기본 구조와 원하는 상태 모델을 입문자 관점에서 정리합니다.
last_reviewed: '2026-05-15'
---

# Kubernetes 101 (1/10): Kubernetes란 무엇인가?

컨테이너를 처음 다룰 때는 `docker run` 몇 번으로도 충분해 보입니다. 앱 하나, 데이터베이스 하나, 프록시 하나 정도라면 사람이 직접 상태를 맞춰도 큰 문제 없이 굴러갑니다. 하지만 서비스가 커지고 컨테이너 수가 늘어나면 상황이 달라집니다. 어느 서버에 무엇이 떠 있는지, 죽은 컨테이너를 누가 다시 띄우는지, 버전 교체를 어떻게 안전하게 할지부터 사람이 기억하고 맞추기 어려워집니다.

이 글은 Kubernetes 101 시리즈의 첫 번째 글입니다.

여기서는 Kubernetes를 단순히 "컨테이너를 많이 돌리는 도구"가 아니라, 원하는 상태를 선언하면 시스템이 그 상태로 계속 수렴하도록 만드는 오케스트레이터라는 관점에서 정리하겠습니다.

## 먼저 던지는 질문

- 오케스트레이션이라는 말은 실제로 무엇을 대신해 줄까요?
- 컨트롤 플레인과 워커 노드는 어떤 식으로 역할을 나눌까요?
- 원하는 상태 모델이 왜 Kubernetes의 핵심 철학일까요?

## 큰 그림

![Kubernetes 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/kubernetes-101/01/01-01-concept-at-a-glance.ko.png)

*Kubernetes 101 1장 흐름 개요*

## 왜 중요한가

컨테이너 몇 개는 Docker Compose만으로도 충분합니다. 하지만 수십 개가 넘어가면 누가 어떤 컨테이너를 어디에 배치할지, 장애가 나면 어떻게 복구할지, 새 버전으로 어떻게 교체할지 같은 문제가 한꺼번에 밀려옵니다. 이때부터는 컨테이너 런타임보다 오케스트레이터가 더 중요해집니다.

Kubernetes를 배우는 이유도 여기 있습니다. 많은 입문자가 Kubernetes를 "컨테이너 플랫폼" 정도로 받아들이지만, 실제로는 사람이 반복하던 운영 결정을 시스템 규칙으로 옮기는 도구에 가깝습니다. 이 관점을 먼저 잡아 두면 뒤에서 나오는 Pod, Deployment, Service도 훨씬 자연스럽게 이어집니다.

## 한눈에 보는 구조

이 그림을 볼 때 가장 먼저 기억할 점은 `kubectl`이 직접 컨테이너를 띄우지 않는다는 사실입니다. 사용자는 `kubectl`로 원하는 상태를 API 서버에 전달하고, 이후의 배치와 조정은 컨트롤 플레인 구성요소가 맡습니다. Kubernetes를 이해하려면 이 제어 흐름부터 알아야 합니다.

## 핵심 용어

- 클러스터: 컨트롤 플레인과 워커 노드를 묶은 전체 실행 환경입니다.
- 컨트롤 플레인: API 서버, etcd, scheduler, controller-manager처럼 클러스터의 제어를 맡는 영역입니다.
- 노드: 실제로 컨테이너가 실행되는 머신입니다.
- 원하는 상태: YAML에 선언한 목표 상태입니다.
- `kubectl`: 클러스터 API와 통신하는 CLI입니다.

## 도입 전과 후

Kubernetes가 없을 때는 서버마다 수동으로 `docker run`을 실행하고, 죽은 컨테이너가 있으면 사람이 다시 올립니다. 같은 환경을 다른 서버에 재현하기도 쉽지 않습니다.

Kubernetes를 도입하면 상황이 달라집니다. 원하는 상태를 YAML로 선언하면 같은 구성을 다른 환경에 반복해서 적용할 수 있고, 시스템이 현재 상태를 계속 목표 상태에 맞추려 합니다. 재현성과 자동 복구가 여기서 시작됩니다.

## 단계별로 첫 클러스터 둘러보기

### 1단계 — 현재 컨텍스트 확인

```python
import subprocess

def current_context():
    res = subprocess.run(
        ["kubectl", "config", "current-context"],
        capture_output=True, text=True, check=True,
    )
    return res.stdout.strip()
```

가장 먼저 볼 값은 현재 컨텍스트입니다. `kubectl`은 단일 클러스터 전용 도구가 아니므로, 지금 어떤 클러스터를 바라보는지부터 확인해야 합니다. 입문 단계에서도 이 습관이 중요합니다.

### 2단계 — 노드 목록 확인

```python
def get_nodes():
    res = subprocess.run(
        ["kubectl", "get", "nodes", "-o", "wide"],
        capture_output=True, text=True, check=True,
    )
    return res.stdout
```

노드 목록은 이 클러스터가 실제로 어떤 실행 자원을 갖고 있는지 보여 줍니다. Kubernetes가 논리적인 제어 시스템처럼 보여도, 결국 워크로드는 워커 노드 위에서 돌아갑니다.

### 3단계 — 네임스페이스 확인

```python
def list_namespaces():
    res = subprocess.run(
        ["kubectl", "get", "ns"],
        capture_output=True, text=True, check=True,
    )
    return res.stdout
```

네임스페이스는 Kubernetes에서 가장 기본적인 격리 단위입니다. 워크로드를 그냥 한곳에 모두 넣는 대신, 환경이나 팀 단위로 나눠 운영하기 시작하는 출발점이라고 보면 됩니다.

### 4단계 — 시스템 파드 보기

```python
def system_pods():
    res = subprocess.run(
        ["kubectl", "-n", "kube-system", "get", "pods"],
        capture_output=True, text=True, check=True,
    )
    return res.stdout
```

`kube-system` 네임스페이스를 보면 클러스터가 스스로를 운영하기 위해 어떤 구성요소를 띄우는지 감이 옵니다. Kubernetes는 단일 바이너리 하나가 아니라 여러 컴포넌트가 함께 움직이는 시스템이라는 점이 여기서 드러납니다.

### 5단계 — 클러스터 상태 확인

```python
def cluster_info():
    res = subprocess.run(
        ["kubectl", "cluster-info"],
        capture_output=True, text=True, check=True,
    )
    return res.stdout
```

`cluster-info`는 클러스터 접근 경로를 빠르게 확인할 때 유용합니다. 처음에는 단순 조회처럼 보이지만, 실제 운영에서는 API 서버 접근 문제를 확인하는 첫 단계가 되기도 합니다.

## 검증 흐름

```bash
kubectl config current-context
kubectl get nodes -o wide
kubectl cluster-info
```

**예상되는 결과:** 현재 컨텍스트 이름이 먼저 보이고, 이어서 노드 목록과 API 서버 엔드포인트가 정상적으로 출력돼야 합니다. 최소한 `Ready` 상태 노드 한 개 이상과 접근 가능한 control plane 주소를 확인할 수 있어야 합니다.

**먼저 의심할 실패 모드:**

- `current-context`가 예상한 클러스터가 아니면 잘못된 kubeconfig를 보고 있을 가능성이 큽니다.
- `kubectl get nodes`가 timeout 나면 인증 정보보다 네트워크 경로나 API 서버 가용성을 먼저 확인하는 편이 빠릅니다.
- `cluster-info`는 되는데 노드가 `NotReady`면 Kubernetes 개념 문제가 아니라 클러스터 상태 문제입니다.

## 이 코드에서 먼저 봐야 할 점

- `kubectl`은 API 서버와 통신합니다.
- `etcd`를 직접 만지는 흐름은 일반적인 운영 경로가 아닙니다.
- 네임스페이스가 기본 격리 단위라는 감각을 일찍 익히는 편이 좋습니다.

이 세 가지를 먼저 잡아 두면 Kubernetes를 "명령을 내리면 즉시 컨테이너가 뜨는 도구"로 오해하지 않게 됩니다. 사용자가 하는 일은 대부분 선언이고, 실제 조정은 컨트롤 플레인이 맡습니다.

## 자주 하는 실수 다섯 가지

1. Kubernetes를 단순히 컨테이너와 같은 뜻으로 받아들입니다.
2. 노드 수만 늘리면 운영 문제가 자동으로 해결된다고 생각합니다.
3. `etcd`를 일반 데이터 저장소처럼 직접 다루려 합니다.
4. `kubectl` 컨텍스트를 확인하지 않고 잘못된 클러스터에 적용합니다.
5. 워크로드 규모가 아주 작은데도 Kubernetes부터 도입합니다.

## 실무에서는 이렇게 봅니다

실무에서는 EKS, GKE, AKS 같은 관리형 Kubernetes를 기본 선택지로 두는 경우가 많습니다. 이유는 단순합니다. 팀이 직접 운영하고 싶은 것은 대개 애플리케이션이지, 컨트롤 플레인 자체가 아니기 때문입니다.

시니어 엔지니어는 Kubernetes를 볼 때 기능 목록보다 멘탈 모델을 먼저 봅니다. 원하는 상태를 선언하는 도구인지, 현재 상태를 그쪽으로 계속 밀어 붙이는 제어 시스템인지, 그리고 그 제어를 사람이 어디까지 직접 맡아야 하는지부터 구분합니다. 이 관점이 있어야 뒤에서 Deployment와 HPA를 볼 때도 흐름이 이어집니다.

## 체크리스트

- [ ] 적용 전 현재 컨텍스트를 확인했는가
- [ ] 워크로드를 네임스페이스로 나눌 계획이 있는가
- [ ] 원하는 상태를 YAML로 관리할 준비가 되었는가
- [ ] 관리형 Kubernetes를 먼저 검토했는가

## 연습 문제

1. 컨트롤 플레인의 역할을 한 줄로 설명해 보세요.
2. 원하는 상태가 왜 Kubernetes의 핵심인지 한 줄로 적어 보세요.
3. Kubernetes 도입을 미루는 편이 나은 상황을 하나 떠올려 보세요.

## 마무리와 다음 글

이 글에서는 Kubernetes를 컨테이너 실행 도구가 아니라 원하는 상태를 유지하는 오케스트레이터로 보는 기본 관점을 잡았습니다. 컨트롤 플레인, 워커 노드, `kubectl`, 네임스페이스 같은 용어도 결국 이 모델 안에서 이해해야 서로 연결됩니다.

다음 글에서는 이 전체 시스템이 실제로 다루는 가장 작은 배포 단위인 Pod를 보겠습니다. Kubernetes의 많은 추상화는 결국 Pod를 중심으로 쌓여 있습니다.


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

- **오케스트레이션이라는 말은 실제로 무엇을 대신해 줄까요?**
  - 본문의 기준은 Kubernetes란 무엇인가?를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **컨트롤 플레인과 워커 노드는 어떤 식으로 역할을 나눌까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **원하는 상태 모델이 왜 Kubernetes의 핵심 철학일까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- **Kubernetes란 무엇인가? (현재 글)**
- Pod (예정)
- Deployment (예정)
- Service (예정)
- Ingress (예정)
- ConfigMap과 Secret (예정)
- Volume (예정)
- HPA (예정)
- Helm (예정)
- 운영 관점의 Kubernetes (예정)

<!-- toc:end -->

## 참고 자료

- [Kubernetes Overview](https://kubernetes.io/docs/concepts/overview/)
- [Kubernetes components](https://kubernetes.io/docs/concepts/overview/components/)
- [kubectl reference](https://kubernetes.io/docs/reference/kubectl/)
- [CNCF landscape](https://landscape.cncf.io/)
- [kubectl cheat sheet](https://kubernetes.io/ko/docs/reference/kubectl/cheatsheet/)

Tags: Kubernetes, Orchestration, Containers, DevOps, SRE
