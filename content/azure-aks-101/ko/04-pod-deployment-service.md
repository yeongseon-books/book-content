---
title: "Azure Kubernetes Service 101 (4/7): Pod·Deployment·Service — 워크로드를 표현하는 세 가지 방식"
series: azure-aks-101
episode: 4
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- Azure
- AKS
- Kubernetes
- Cloud
last_reviewed: '2026-05-12'
seo_description: 처음 Kubernetes YAML을 보면 비슷해 보이는 객체가 많습니다.
---

# Azure Kubernetes Service 101 (4/7): Pod·Deployment·Service — 워크로드를 표현하는 세 가지 방식

처음 Kubernetes 매니페스트를 보면 객체가 불필요하게 많아 보입니다. “컨테이너 하나 띄우면 되는데 왜 Pod가 있고 Deployment가 있고 Service까지 따로 있지?”라는 질문이 자연스럽습니다. 하지만 실제 운영에서는 이 셋을 분리해 둔 덕분에 배포와 복구와 네트워크 경계가 훨씬 명확해집니다.

AKS를 쓰더라도 이 구조는 Kubernetes 자체의 언어로 그대로 남습니다. 따라서 Pod, Deployment, Service가 흐릿하면 Ingress와 HPA도 함께 흐릿해집니다. 반대로 이 셋만 정확히 구분해도 워크로드 모델의 절반 이상이 정리됩니다.

이 글은 Azure AKS 101 시리즈의 4번째 글입니다.

여기서는 3화에서 실제로 사용한 Pod, Deployment, Service를 각각 어떤 문제를 푸는 객체인지 분리해서 보겠습니다. **스케줄링 단위, 원하는 상태 관리자, 안정적인 네트워크 정체성**이라는 세 층으로 나누어 이해하는 것이 핵심입니다.

![Azure Kubernetes Service 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/azure-aks-101/04/04-01-one-picture-first.ko.png)
*Azure Kubernetes Service 101 4장 흐름 개요*
> Pod·Deployment·Service — 워크로드를 표현하는 세 가지 방식의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 먼저 던지는 질문

- Pod와 컨테이너는 왜 같은 말이 아니며, 왜 Kubernetes는 Pod를 스케줄링 단위로 볼까요?
- Deployment는 Pod를 직접 여러 개 만드는 것과 무엇이 다를까요?
- Service는 왜 Pod IP를 직접 쓰지 않게 만드는 걸까요?

## 왜 이 글이 중요한가

많은 Kubernetes 장애는 생각보다 아래층에서 시작합니다. 외부 요청이 실패해도 Ingress 문제가 아니라 Service selector 오타일 수 있고, Pod가 재생성되는 이유는 애플리케이션 코드가 아니라 Deployment 전략이나 probe 설정 때문일 수 있습니다. 즉 Pod·Deployment·Service를 구분하지 못하면 장애를 항상 한 단계 위에서 잘못 보기 쉽습니다.

또한 이 셋은 Kubernetes의 가장 기본적인 책임 분리입니다. Pod는 실행 단위이고, Deployment는 그 실행 단위를 선언적으로 유지하는 관리자이며, Service는 바뀌는 Pod 집합 앞에 고정된 접근 경로를 둡니다. 이 구조 덕분에 수명주기와 네트워크 정체성을 한 객체에 억지로 몰아넣지 않게 됩니다.

이 글을 정확히 이해하면 5화의 Ingress가 왜 Service 앞에 놓이는지, 6화의 HPA가 왜 Deployment 복제본 수를 조절하는지, 7화의 운영이 왜 Pod 상태와 Service 연결을 함께 봐야 하는지 자연스럽게 이어집니다.

## 핵심 관점

Pod, Deployment, Service는 같은 일을 세 번 표현하는 중복 개념이 아닙니다. 저는 이 셋을 각각 다른 운영 문제를 맡는 층으로 보는 편이 가장 실용적이라고 생각합니다. Pod는 “무엇이 실제로 실행되는가”를, Deployment는 “그 실행 단위를 어떤 상태로 유지할 것인가”를, Service는 “그 실행 단위 집합에 어떤 안정적인 접근 지점을 둘 것인가”를 맡습니다.

이렇게 보면 왜 Deployment 안에 Pod template이 들어 있고, 왜 Service가 Pod 집합을 라벨로 고르고, 왜 Pod 수를 늘린다고 외부 진입점이 자동으로 바뀌지 않는지도 자연스럽게 이해됩니다. 한 문장으로 말하면 **실행, 수명주기, 네트워크 정체성을 분리한 모델**입니다.

따라서 이 글은 객체 사전식 설명보다도, 세 객체가 함께 있을 때 어떤 운영 문제가 깔끔하게 풀리는지를 중심으로 읽는 편이 좋습니다.

> Pod는 실행 단위이고, Deployment는 그 실행 단위의 원하는 상태를 유지하며, Service는 바뀌는 Pod 집합 앞에 고정된 접근 경로를 둡니다.

## 핵심 개념

### 세 객체를 한 장으로 보면 모델이 거의 끝납니다

전체 관계를 먼저 그림으로 보는 편이 좋습니다.

이 그림이 중요한 이유는 세 객체의 역할을 한눈에 보여 주기 때문입니다.

- **Pod**는 컨테이너를 실행하는 최소 스케줄링 단위입니다.
- **Deployment**는 Pod가 몇 개 있어야 하는지와 업데이트 방식을 선언합니다.
- **Service**는 계속 바뀌는 Pod 집합 앞에 안정적인 가상 IP와 이름을 둡니다.

즉 이 셋은 각각 다른 종류의 운영 문제를 맡습니다. 같은 문제를 세 번 푸는 것이 아닙니다.

### Pod는 Kubernetes가 노드에 배치하는 최소 단위입니다

Kubernetes는 raw container가 아니라 Pod를 노드에 배치합니다. 작은 FastAPI 앱에서는 Pod 안에 컨테이너 하나만 들어가는 경우가 흔하지만, Kubernetes 관점에서 중요한 것은 여전히 컨테이너가 아니라 Pod입니다.

- Pod 안의 컨테이너는 같은 네트워크 네임스페이스를 공유합니다.
- 같은 볼륨을 마운트할 수 있습니다.
- 함께 시작하고 함께 종료되는 수명주기를 가집니다.

이 설계는 sidecar 같은 패턴을 가능하게 합니다. 다만 입문에서는 “컨테이너 하나를 위한 Pod 하나” 정도로 먼저 이해해도 충분합니다. 핵심은 **배치와 수명주기의 최소 단위가 컨테이너가 아니라 Pod**라는 점입니다.

### Pod를 직접 관리하지 않는 이유는 수명주기 관리가 필요하기 때문입니다

Pod는 영구 객체가 아닙니다. 노드가 내려가면 사라질 수 있고, 프로세스가 실패하면 다시 만들어져야 할 수 있습니다. 만약 사용자가 Pod를 직접 여러 개 만들고 직접 복구해야 한다면, 운영은 금방 번거로워집니다.

그래서 실제 운영에서는 Pod 앞에 상위 컨트롤러를 둡니다. 가장 흔한 컨트롤러가 Deployment입니다. 즉 Pod는 실행 단위이지만, **대부분의 애플리케이션은 Pod를 직접 소유하지 않고 Deployment를 통해 간접적으로 소유**합니다.

### Deployment는 원하는 상태를 선언하는 관리자입니다

Deployment는 “이 Pod template을 N개 유지하고, template이 바뀌면 안전하게 업데이트하라”는 선언입니다.

Deployment를 쓰면 다음과 같은 운영 기능이 생깁니다.

- Pod가 죽어도 다시 맞춰 줍니다.
- 복제본 수를 선언적으로 유지합니다.
- 롤링 업데이트를 지원합니다.
- revision history를 통해 롤백 단서를 남깁니다.

내부적으로는 Deployment가 ReplicaSet을 만들고, ReplicaSet이 실제 Pod 개수를 맞춥니다. 입문 단계에서 ReplicaSet을 자주 직접 다루지는 않지만, Deployment가 곧바로 Pod를 직접 세는 것이 아니라 그 사이에 컨트롤러 층이 하나 더 있다는 정도는 알고 있는 편이 좋습니다.

### Service는 불안정한 Pod 집합 앞에 안정적인 정체성을 둡니다

Pod IP는 영구 주소가 아닙니다. Pod가 교체되면 IP도 바뀔 수 있습니다. 서비스 간 통신을 Pod IP에 직접 걸면 운영이 매우 취약해집니다.

Service는 이 문제를 푸는 기본 장치입니다.

- 안정적인 가상 IP를 제공합니다.
- 클러스터 내부 DNS 이름을 제공합니다.
- 라벨 셀렉터로 대상 Pod 집합을 고릅니다.

즉 다른 워크로드는 “지금 살아 있는 Pod가 어느 것인지”를 직접 알 필요가 없습니다. **이 Service 이름으로 보내면 된다**는 인터페이스를 사용하게 됩니다. 이 추상화 덕분에 Pod 교체와 트래픽 연결이 느슨하게 분리됩니다.

### 가장 작은 예시를 보면 세 역할이 한 번에 보입니다

아래 예시는 Deployment와 Service의 가장 작은 유용한 조합입니다.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-hello
spec:
  replicas: 2
  selector:
    matchLabels:
      app: fastapi-hello
  template:
    metadata:
      labels:
        app: fastapi-hello
    spec:
      containers:
        - name: app
          image: <your-registry>/fastapi-hello:latest
          ports:
            - containerPort: 8000
---
apiVersion: v1
kind: Service
metadata:
  name: fastapi-hello
spec:
  selector:
    app: fastapi-hello
  ports:
    - port: 80
      targetPort: 8000
  type: ClusterIP
```

이 예시에서 Pod 객체가 직접 보이지 않는 이유도 중요합니다. Deployment의 `template` 자체가 “이런 모양의 Pod를 만들라”는 뜻이기 때문입니다. 즉 실제 실행 단위는 Pod지만, 사용자는 보통 Deployment 선언을 통해 간접적으로 Pod를 다루게 됩니다.

### 라벨은 단순 장식이 아니라 배포와 라우팅의 접착제입니다

Deployment와 Service는 둘 다 라벨을 통해 대상 집합을 정의합니다.

- Deployment는 어떤 Pod가 자기 소유인지 라벨로 구분합니다.
- Service는 어떤 Pod 집합으로 트래픽을 보낼지 라벨로 고릅니다.

따라서 `app: fastapi-hello` 같은 라벨 한 줄은 메타데이터 장식이 아니라 실제 배포와 라우팅의 연결점입니다. 라벨이 꼬이면 흔히 두 종류의 문제가 납니다.

1. Deployment가 의도한 Pod를 제대로 관리하지 못합니다.
2. Service가 엉뚱한 Pod를 선택하거나 아무 Pod도 찾지 못합니다.

운영에서 selector mismatch는 생각보다 자주 보이는 실수입니다. 단순한 오타지만, 외부에서 보면 장애처럼 보입니다.

### Service 타입은 노출 범위를 결정합니다

입문 단계에서는 세 가지 Service 타입만 확실히 기억해도 충분합니다.

#### ClusterIP

- 클러스터 내부 접근용입니다.
- 서비스 간 통신에 가장 많이 쓰입니다.
- 기본값입니다.

#### NodePort

- 각 노드의 특정 포트를 열어 서비스에 연결합니다.
- 구조를 이해하는 데는 도움이 되지만, 장기 운영 진입점으로는 다소 거칠 수 있습니다.

#### LoadBalancer

- 클라우드 로드 밸런서를 연결합니다.
- AKS에서는 Azure Load Balancer와 이어집니다.
- 단일 서비스를 빠르게 외부에 공개할 때 편합니다.

| 타입 | 접근 범위 | 주 용도 | AKS에서의 느낌 |
|---|---|---|---|
| ClusterIP | 클러스터 내부 | 서비스 간 통신 | 기본값 |
| NodePort | 노드 IP + 포트 | 학습, 특수 접근 | 직접 운영 부담이 큼 |
| LoadBalancer | 클러스터 외부 | 단일 외부 공개 | Azure LB와 연결 |

이 비교를 보면 5화의 Ingress가 왜 필요한지도 읽힙니다. LoadBalancer만으로 외부 공개는 가능하지만, 여러 서비스에 대한 HTTP 라우팅을 깔끔하게 표현하기에는 부족합니다.

### Pod 수를 늘리는 일과 트래픽을 분산하는 일은 다른 문제입니다

초반에 가장 자주 섞이는 개념이 바로 이것입니다.

- Deployment의 `replicas`를 늘리는 일은 Pod 수를 바꾸는 일입니다.
- Service는 현재 살아 있는 Pod 집합에 요청을 분산하는 일입니다.

즉 Service는 Pod를 만들지 않습니다. Deployment가 Pod를 만들고, Service는 라벨이 맞는 Pod 집합에 붙습니다. 이 분리 덕분에 수명주기 제어와 네트워크 정체성이 서로 느슨하게 결합됩니다.

### 업데이트를 상상하면 Deployment의 역할이 더 잘 보입니다

새 버전 이미지를 배포한다고 생각해 보겠습니다. Deployment는 기존 Pod를 한 번에 모두 지우지 않고 보통 점진적으로 새 Pod로 교체합니다.

![롤링 업데이트 중 Deployment와 Service의 연결](https://yeongseon-books.github.io/book-public-assets/assets/azure-aks-101/04/04-02-deployment-becomes-clearer-when-you-imag.ko.png)

*롤링 업데이트 중 Deployment와 Service의 연결*

이때 Service는 Ready 상태가 된 새 Pod로 자연스럽게 붙습니다. 그래서 readiness probe가 매우 중요합니다. 프로세스가 단순히 떠 있는 것과 실제로 트래픽을 받아도 되는 상태는 다를 수 있기 때문입니다. Service는 readiness 결과를 바탕으로 backend 집합을 해석하므로, probe 품질이 곧 배포 안정성으로 이어집니다.

### Pod 안에 컨테이너를 여러 개 넣는 경우도 있습니다

입문에서는 앱 컨테이너 하나만 쓰는 편이 가장 깔끔합니다. 그래도 Pod가 왜 컨테이너 하나만을 가리키는 개념이 아닌지는 알아 둘 필요가 있습니다.

대표적인 multi-container Pod 패턴은 다음과 같습니다.

- 로깅 sidecar
- 프록시 sidecar
- 앱과 강하게 결합된 helper process

다만 서로 무관한 두 서비스를 한 Pod에 넣는 것은 보통 좋지 않습니다. 같이 스케줄되고 같이 죽는다는 뜻이기 때문입니다. Pod 공유는 강한 결합을 의미합니다.

### AKS에서 이 셋을 볼 때의 실무 순서가 있습니다

AKS는 관리형 Kubernetes지만, Pod·Deployment·Service의 의미 자체를 바꾸지는 않습니다. 그래서 장애를 볼 때도 순서를 아래처럼 잡는 편이 좋습니다.

1. Pod가 정상인가
2. Deployment가 원하는 복제본 수를 유지하는가
3. Service가 올바른 라벨의 Pod를 잡고 있는가

외부 요청이 실패한다고 해서 항상 Ingress부터 보는 것은 아닙니다. 실제로는 Service selector 오타, readiness probe 실패, 이미지 pull 문제 같은 더 아래층에서 막히는 경우가 많습니다.

### 장애를 줄이는 선언 패턴: rollout 전략과 service endpoints 확인

Pod·Deployment·Service를 아는 것과 운영 품질은 한 단계 차이가 있습니다. 운영 품질은 “변경 중에도 서비스가 유지되도록 선언했는가”에서 갈립니다. 최소한 Deployment의 rollout 전략과 Service endpoint 확인 습관은 초반부터 가져가는 편이 좋습니다.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-hello
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: fastapi-hello
  template:
    metadata:
      labels:
        app: fastapi-hello
    spec:
      containers:
        - name: app
          image: <your-registry>/fastapi-hello:v2
          ports:
            - containerPort: 8000
```

`maxUnavailable: 0`은 업데이트 중에도 기존 가용 Pod를 유지하겠다는 강한 의도입니다. 트래픽이 작은 실습 환경에서는 차이가 덜 보이지만, 실제 트래픽이 있는 운영에서는 이 한 줄이 체감 품질을 크게 바꿉니다.

또한 Service는 선언만 맞는다고 끝나지 않습니다. 아래처럼 endpoint를 반드시 확인해야 selector 불일치와 readiness 누락을 빨리 찾을 수 있습니다.

```bash
kubectl get svc fastapi-hello
kubectl get endpoints fastapi-hello
kubectl describe svc fastapi-hello
```

`endpoints`가 비어 있으면 Service 자체가 아니라 Pod 선택 조건 또는 Pod 준비 상태 문제일 가능성이 큽니다. 이 분리만 잘해도 “네트워크 문제”로 보이던 장애 상당수를 더 정확한 층으로 보낼 수 있습니다.

### ConfigMap과 Secret을 붙이면 세 객체의 경계가 더 선명해집니다

Pod·Deployment·Service를 배운 직후에는 “설정값은 어디에 둬야 하나”라는 질문이 바로 따라옵니다. 이때 ConfigMap과 Secret을 연결해 보면 객체 책임 분리가 더 명확해집니다. Deployment는 실행 단위와 버전을 관리하고, ConfigMap/Secret은 실행 시점 설정을 관리하며, Service는 접근 경로를 관리합니다.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fastapi-hello-config
data:
  APP_NAME: "fastapi-hello"
  LOG_LEVEL: "info"
---
apiVersion: v1
kind: Secret
metadata:
  name: fastapi-hello-secret
type: Opaque
stringData:
  DB_PASSWORD: "replace-me"
```

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-hello
spec:
  replicas: 2
  selector:
    matchLabels:
      app: fastapi-hello
  template:
    metadata:
      labels:
        app: fastapi-hello
    spec:
      containers:
        - name: app
          image: <your-registry>/fastapi-hello:v1
          envFrom:
            - configMapRef:
                name: fastapi-hello-config
            - secretRef:
                name: fastapi-hello-secret
```

이 구조를 쓰면 “코드 배포”와 “환경값 변경”을 분리할 수 있어 롤백 판단이 쉬워집니다. 운영에서 자주 생기는 문제는 버그와 설정 오류가 동시에 섞일 때인데, 경계가 분리되어 있으면 조사 순서가 훨씬 단순해집니다.

### 서비스 연결 문제를 재현 가능한 방식으로 점검합니다

아래처럼 임시 디버그 Pod에서 Service DNS를 호출해 보면 Ingress 앞단 문제인지 Service/Pod 내부 문제인지 빠르게 분리할 수 있습니다.

```bash
kubectl run net-debug --rm -it --image=busybox:1.36 --restart=Never -- sh
# 컨테이너 안에서
wget -qO- http://fastapi-hello.default.svc.cluster.local/
```

클러스터 내부 호출이 성공하면 Service와 Pod 경로는 살아 있는 것입니다. 그 상태에서 외부 요청만 실패하면 Ingress, DNS, TLS 같은 상위 계층을 보는 편이 맞습니다. 이 한 번의 분리만으로 장애 대응 시간이 크게 줄어듭니다.

또한 rollout 중에는 아래 두 명령을 같이 보는 편이 좋습니다.

```bash
kubectl rollout status deployment/fastapi-hello
kubectl get pods -l app=fastapi-hello -w
```

첫 명령은 선언한 버전이 정상 수렴하는지, 두 번째 명령은 개별 Pod가 어떤 속도로 Ready로 전환되는지 보여 줍니다. Service는 결국 Ready Pod 집합을 대상으로 라우팅하므로, rollout 속도와 readiness 품질은 곧 사용자 체감 품질로 이어집니다.

## 흔히 헷갈리는 지점

- Pod와 컨테이너를 같은 개념으로 생각하기 쉽지만, Kubernetes는 Pod를 스케줄링 단위로 봅니다.
- Deployment가 단순히 Pod 여러 개를 대신 만들어 주는 도구라고만 생각하기 쉽지만, 핵심은 원하는 상태 유지와 업데이트 전략입니다.
- Service가 Pod를 생성한다고 오해하기 쉽지만, Service는 오직 접근 경로와 선택 기준만 제공합니다.
- 라벨을 부가 정보 정도로 보기 쉽지만, 실제로는 소유 관계와 트래픽 라우팅을 결정합니다.
- Running 상태인 Pod만 있으면 서비스가 정상이라고 생각하기 쉽지만, Service selector와 readiness까지 함께 맞아야 합니다.

## 운영 체크리스트

- [ ] Pod, Deployment, Service가 각각 어떤 운영 문제를 푸는지 한 문장씩 설명할 수 있는가
- [ ] 모든 워크로드에 대해 Deployment selector와 Pod label이 정확히 일치하는가
- [ ] Service selector가 의도한 Pod 집합만 선택하는지 검증했는가
- [ ] readiness probe가 실제 트래픽 수용 가능 시점을 반영하도록 설계됐는가
- [ ] Pod 수 변경과 네트워크 노출이 서로 다른 객체 책임이라는 점을 팀이 공통적으로 이해하는가

## 정리

이 글의 핵심은 Pod·Deployment·Service를 중복된 객체로 보지 않는 것입니다. Pod는 실행 단위이고, Deployment는 그 실행 단위를 선언적으로 유지하는 관리자이며, Service는 바뀌는 Pod 집합 앞에 안정적인 네트워크 정체성을 두는 추상화입니다. 이 세 층이 분리되어 있기 때문에 Kubernetes는 수명주기와 트래픽을 유연하게 관리할 수 있습니다.

또한 라벨과 selector는 이 모델의 접착제입니다. Deployment와 Service는 모두 라벨을 통해 대상 집합을 해석하므로, 작은 라벨 설계가 실제로는 배포와 라우팅 안정성에 직결됩니다. 운영에서 사소한 오타가 큰 장애처럼 보이는 이유도 여기에 있습니다.

이제 5화로 넘어가면 Service 앞단에 Ingress가 붙습니다. 즉 오늘 이해한 Service의 안정적인 내부 정체성 위에, 외부 HTTP 요청을 정리하는 한 층이 더 생기게 됩니다. 그때부터 AKS 네트워킹이 훨씬 덜 추상적으로 읽힐 것입니다.

## 처음 질문으로 돌아가기

- **Pod와 컨테이너는 왜 같은 말이 아니며, 왜 Kubernetes는 Pod를 스케줄링 단위로 볼까요?**
  - Kubernetes는 `containerPort: 8000` 같은 컨테이너 설정을 담더라도 실제 배치는 Pod 단위로 합니다. Pod는 네트워크 네임스페이스와 볼륨, 수명주기를 함께 공유하므로, 컨테이너 하나 예제라도 스케줄링과 복구의 최소 단위는 컨테이너가 아니라 Pod입니다.
- **Deployment는 Pod를 직접 여러 개 만드는 것과 무엇이 다를까요?**
  - `replicas: 3`, `strategy.rollingUpdate.maxSurge: 1`, `maxUnavailable: 0`처럼 원하는 개수와 업데이트 방식을 선언하는 것이 Deployment의 역할입니다. Pod를 손으로 여러 개 띄우는 방식과 달리 Deployment는 죽은 Pod 복구, 롤링 업데이트, `kubectl rollout status deployment/fastapi-hello` 같은 운영 경로를 함께 제공합니다.
- **Service는 왜 Pod IP를 직접 쓰지 않게 만드는 걸까요?**
  - Pod IP는 교체될 수 있지만 `Service`는 `selector: app: fastapi-hello`와 `targetPort: 8000`으로 안정적인 접근 지점을 남깁니다. 그래서 `kubectl get endpoints fastapi-hello`를 보면 현재 Ready Pod 집합이 바뀌어도 클라이언트는 `fastapi-hello`라는 이름으로 계속 붙을 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Azure Kubernetes Service 101 (1/7): Azure Kubernetes Service란? — 직접 운영하지 않아도 되는 Kubernetes](./01-what-is-aks.md)
- [Azure Kubernetes Service 101 (2/7): 클러스터 아키텍처 — Control Plane과 Node Pool](./02-cluster-architecture.md)
- [Azure Kubernetes Service 101 (3/7): 첫 클러스터 만들고 앱 배포하기 — Python/FastAPI](./03-first-cluster-and-deploy.md)
- **Azure Kubernetes Service 101 (4/7): Pod·Deployment·Service — 워크로드를 표현하는 세 가지 방식 (현재 글)**
- Azure Kubernetes Service 101 (5/7): 네트워킹과 Ingress — 클러스터 안과 밖을 잇는 길 (예정)
- Azure Kubernetes Service 101 (6/7): 스케일링 — HPA, Cluster Autoscaler, KEDA (예정)
- Azure Kubernetes Service 101 (7/7): 모니터링과 운영 — Container Insights, 로그, 알람 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [Kubernetes core concepts for Azure Kubernetes Service (AKS)](https://learn.microsoft.com/en-us/azure/aks/concepts-clusters-workloads)
- [Services, load balancing, and networking in Kubernetes](https://kubernetes.io/docs/concepts/services-networking/service/)
- [Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)

### 관련 시리즈

- [Azure App Service 101](../../azure-app-service-101/ko/02-request-lifecycle.md) — 요청이 앱 인스턴스로 들어가는 흐름과 비교할 때
- [Azure Functions 101](../../azure-functions-101/ko/02-triggers-and-bindings.md) — 함수 단위 실행 모델과 비교할 때

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-aks-101/ko/04-pod-deployment-service)

Tags: Azure, AKS, Kubernetes, Cloud
