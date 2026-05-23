---
title: "Azure Kubernetes Service 101 (3/7): 첫 클러스터 만들고 앱 배포하기 — Python/FastAPI"
series: azure-aks-101
episode: 3
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
seo_description: 개념을 오래 붙들고 있으면 Kubernetes는 필요 이상으로 추상적으로 느껴집니다.
---

# Azure Kubernetes Service 101 (3/7): 첫 클러스터 만들고 앱 배포하기 — Python/FastAPI

Kubernetes는 개념만 오래 붙들고 있으면 필요 이상으로 추상적으로 느껴집니다. 실제로는 작은 앱 하나를 올려 보면 훨씬 빨리 감이 옵니다. 리소스를 만들고, 클러스터에 적용하고, Service로 접근하고, 상태를 확인하는 흐름을 한 번 직접 밟아 보면 뒤의 네트워킹과 스케일링도 갑자기 현실적인 문제로 바뀝니다.

특히 AKS 입문에서는 `az`와 `kubectl`의 경계가 몸으로 들어오는 경험이 중요합니다. Azure 리소스를 만드는 일과 Kubernetes API에 원하는 상태를 선언하는 일은 이어져 있지만 같은 작업이 아닙니다. 이 분리가 눈에 익으면 이후 운영 문맥도 훨씬 잘 잡힙니다.

여기서는 앞의 두 글에서 본 구조를 실제 배포 흐름으로 연결하겠습니다. **작은 AKS 클러스터를 만들고, user node pool을 추가하고, FastAPI 앱을 컨테이너로 빌드해 Deployment와 Service로 올리는 과정**을 통해 AKS의 기본 운영 언어를 손에 익히겠습니다.

![Azure Kubernetes Service 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/azure-aks-101/03/03-01-today-s-flow.ko.png)
*Azure Kubernetes Service 101 3장 흐름 개요*
> 첫 클러스터 만들고 앱 배포하기 — Python/FastAPI의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 먼저 던지는 질문

- 실습용 AKS 클러스터를 만들 때 최소한 무엇을 결정해야 할까요?
- 기본 system pool 외에 user node pool을 왜 별도로 추가하는 편이 좋을까요?
- `az aks get-credentials` 이후 `kubectl`이 실제로 어떤 계층과 대화하게 될까요?

## 왜 이 글이 중요한가

AKS를 배울 때 가장 위험한 상태는 용어만 아는 상태입니다. Deployment가 무엇인지, Service가 무엇인지, node pool이 무엇인지는 설명할 수 있지만, 실제로는 어떤 순서로 만들고 어떤 명령으로 확인하며 어디에서 문제가 나는지 감이 없는 상태입니다. 플랫폼 운영은 대부분 그 감각 차이에서 갈립니다.

또한 첫 배포는 이후의 모든 주제를 묶어 줍니다. Ingress는 결국 오늘 만든 Service 앞단에 붙는 것이고, HPA는 오늘 만든 Deployment의 복제본 수를 자동으로 바꾸는 장치이며, 운영과 관측은 결국 오늘 배포한 객체의 상태를 읽는 작업입니다. 작은 예제라도 한 번 전체 흐름을 보는 것이 중요합니다.

무엇보다 이 글은 “AKS는 Azure 리소스이면서 동시에 Kubernetes 클러스터다”라는 사실을 가장 또렷하게 보여 줍니다. `az`와 `kubectl`이 각각 어느 세계를 다루는지 명확해지는 순간, AKS가 훨씬 덜 추상적으로 보이기 시작합니다.

## 핵심 관점

AKS 첫 배포에서 가장 먼저 잡아야 할 기준은 도구 구분입니다. `az`는 Azure Resource Manager 쪽에서 클러스터와 노드 풀 같은 리소스를 만듭니다. 반면 `kubectl`은 그 클러스터 안의 Kubernetes API에 Deployment, Service 같은 원하는 상태를 선언합니다.

이 둘을 한 흐름으로 묶어 보는 것은 맞지만, 같은 층으로 보는 것은 좋지 않습니다. 클러스터가 아직 없는데 `kubectl`은 아무 의미가 없고, 반대로 클러스터가 생긴 뒤 워크로드를 바꾸는 대부분의 일은 `az`보다 `kubectl`에서 일어납니다. 운영 문제도 종종 이 두 층의 경계에서 나뉩니다.

따라서 이번 글은 명령어를 암기하는 글이 아니라, **Azure 리소스 생성 → kubeconfig 연결 → 워크로드 선언 → 외부 노출 → 상태 확인**이라는 기본 실행 루프를 몸에 익히는 글로 읽는 편이 좋습니다.

> AKS 첫 배포의 핵심은 클러스터를 만드는 것보다, Azure 리소스 관리와 Kubernetes 상태 선언이 어떤 순서로 이어지는지 체감하는 데 있습니다.

## 핵심 개념

### 오늘의 흐름을 먼저 한 장으로 봅니다

실습은 세부 명령보다 순서가 중요합니다.

이 그림이 보여 주는 핵심은 간단합니다. `az`는 Azure 쪽 리소스를 만들고, `kubectl`은 Kubernetes API에 원하는 상태를 선언합니다. 이 분리를 체감하는 것이 오늘 실습의 절반입니다.

### 0. 준비물

- Azure CLI
- `kubectl`
- Azure 구독
- 컨테이너 이미지를 올릴 레지스트리

실습의 초점은 AKS 흐름이므로 레지스트리는 Azure Container Registry나 Docker Hub 어느 쪽이어도 됩니다. 다만 Azure 환경 안에서 이어서 운영할 생각이라면 ACR이 가장 자연스럽습니다.

### 1. 리소스 그룹을 만듭니다

AKS도 결국 Azure Resource Manager 아래에 놓이는 Azure 리소스입니다. 그래서 출발점은 리소스 그룹입니다.

```bash
export RESOURCE_GROUP="rg-aks-101"
export LOCATION="koreacentral"
export CLUSTER_NAME="aks-101-cluster"
export USER_POOL="userpool1"

az group create --name $RESOURCE_GROUP --location $LOCATION
```

이 단계는 Kubernetes 그 자체와 직접 관련되지는 않지만, AKS가 Azure 리소스라는 사실을 가장 단순하게 보여 줍니다.

### 2. 작은 AKS 클러스터를 만듭니다

가장 단순한 시작 명령은 아래와 같습니다.

```bash
az aks create \
  --resource-group $RESOURCE_GROUP \
  --name $CLUSTER_NAME \
  --node-count 1 \
  --generate-ssh-keys
```

여기서 먼저 볼 포인트는 네 가지입니다.

- `az aks create`는 AKS 클러스터를 만듭니다.
- `--node-count 1`은 비용을 줄이기 위한 실습용 선택입니다.
- 현재 Learn 빠른 시작 흐름에서는 system-assigned managed identity가 기본 경로입니다.
- `--generate-ssh-keys`는 필요한 키가 없을 때 생성해 줍니다.

운영 환경이라면 VM 크기, 네트워킹 방식, 모니터링, 업그레이드 전략까지 먼저 설계해야 합니다. 하지만 첫 실습의 목적은 완벽한 설계가 아니라 **실제 클러스터 하나를 만들고 그 위에 Kubernetes 객체를 올리는 감각**을 얻는 데 있습니다.

### 3. user node pool을 추가합니다

AKS 실습에서도 애플리케이션 워크로드는 user node pool에서 돌린다는 기본 원칙을 한 번 밟아 보는 편이 좋습니다.

```bash
az aks nodepool add \
  --resource-group $RESOURCE_GROUP \
  --cluster-name $CLUSTER_NAME \
  --name $USER_POOL \
  --node-count 1 \
  --mode User
```

이제 클러스터에는 기본 system pool과 새 user pool이 함께 있게 됩니다. 2화에서 본 구조가 실제 리소스로 드러나는 순간입니다.

확인은 아래처럼 합니다.

```bash
az aks nodepool list \
  --resource-group $RESOURCE_GROUP \
  --cluster-name $CLUSTER_NAME \
  --query "[].{Name:name, Mode:mode, Count:count}"
```

출력에서 `System`과 `User`가 나뉘는 것을 보면, Control Plane 아래의 실행 계층이 어떤 식으로 구분되는지 더 구체적으로 보입니다.

### 4. `kubectl`이 클러스터를 보게 만듭니다

Azure 리소스를 만든 것과 로컬 Kubernetes 클라이언트를 연결한 것은 별개입니다. 이제 kubeconfig를 받아 와야 합니다.

```bash
az aks get-credentials --resource-group $RESOURCE_GROUP --name $CLUSTER_NAME
```

그다음 연결을 확인합니다.

```bash
kubectl get nodes
```

보통 노드가 두 개 보이면 system pool 1개, user pool 1개인 상황입니다. 이 시점부터 대부분의 작업은 Azure CLI보다 `kubectl`에서 이루어집니다.

### 5. 작은 FastAPI 앱을 준비합니다

애플리케이션 코드는 최대한 작게 두겠습니다.

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "hello from aks"}

@app.get("/healthz")
def healthz():
    return {"status": "ok"}
```

이 앱은 두 가지 목적을 가집니다. `/`는 실제 응답을 확인하는 데 쓰고, `/healthz`는 probe 경로로 사용합니다. 즉 예제는 작지만 운영 기본 문법은 그대로 담고 있습니다.

컨테이너를 위한 `Dockerfile`은 다음처럼 둡니다.

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

`requirements.txt`는 최소한으로 갑니다.

```text
fastapi==0.115.0
uvicorn[standard]==0.30.6
```

이미지를 빌드하고 레지스트리에 push한 뒤, Deployment에서 그 이미지를 참조하게 하면 됩니다.

### 6. Deployment와 Service를 작성합니다

이번 글에서는 가장 작은 두 객체만 사용합니다. 그래도 probe와 resource request는 넣어 두는 편이 좋습니다. 실습에서도 운영 감각을 너무 희석하지 않는 편이 낫기 때문입니다.

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
      nodeSelector:
        kubernetes.azure.com/mode: user
      containers:
        - name: app
          image: <your-registry>/fastapi-hello:latest
          ports:
            - containerPort: 8000
          startupProbe:
            httpGet:
              path: /healthz
              port: 8000
            periodSeconds: 5
            failureThreshold: 12
          readinessProbe:
            httpGet:
              path: /healthz
              port: 8000
            initialDelaySeconds: 3
            periodSeconds: 5
          livenessProbe:
            httpGet:
              path: /healthz
              port: 8000
            initialDelaySeconds: 15
            periodSeconds: 10
            failureThreshold: 3
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 300m
              memory: 256Mi
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
  type: LoadBalancer
```

여기서 기억할 라인은 네 개면 충분합니다.

- `replicas: 2`는 같은 앱 Pod를 두 개 원한다는 선언입니다.
- `nodeSelector`는 user node pool에 올리겠다는 의도를 드러냅니다.
- `startupProbe`는 느린 초기 기동 동안 과한 재시작을 막아 줍니다.
- `type: LoadBalancer`는 Azure Load Balancer를 붙여 외부 진입점을 만들겠다는 선언입니다.

특히 probe는 입문 단계부터 구분해서 보는 편이 좋습니다. readiness는 트래픽 수용 가능 여부를, liveness는 장기적으로 살아 있는지 여부를, startup은 초기 부팅 기간의 예외를 다룹니다. 셋을 한데 뭉개면 장애 해석이 어려워집니다.

### 7. 클러스터에 적용합니다

매니페스트를 `fastapi-hello.yaml`로 저장했다면 적용은 한 줄입니다.

```bash
kubectl apply -f fastapi-hello.yaml
```

그다음 상태를 확인합니다.

```bash
kubectl get deployments
kubectl get pods -o wide
kubectl get services
```

`-o wide`를 붙이면 어느 노드에 올라갔는지까지 보입니다. user node pool 노드에 앱 Pod가 올라갔다면, placement 의도도 제대로 반영된 것입니다.

### 8. 요청이 들어가고 응답이 나오는 경로를 확인합니다

배포가 끝나면 요청 경로를 한 번 그림으로 다시 보는 편이 좋습니다.

![외부 요청이 Service와 Pod로 흐르는 경로](https://yeongseon-books.github.io/book-public-assets/assets/azure-aks-101/03/03-02-8-the-request-path.ko.png)

*외부 요청이 Service와 Pod로 흐르는 경로*

지금 단계에서는 Service가 외부 진입점 역할까지 맡고 있습니다. 5화에서 Ingress를 붙이면 이 앞단에 HTTP 라우팅 계층이 하나 더 생기게 됩니다. 즉 오늘 실습은 이후 네트워킹의 바닥 구조이기도 합니다.

### 9. 외부 IP를 확인하고 테스트합니다

LoadBalancer 타입 Service는 외부 IP가 붙는 데 시간이 조금 걸릴 수 있습니다.

```bash
kubectl get service fastapi-hello
```

`EXTERNAL-IP`가 잡히면 테스트합니다.

```bash
curl http://<external-ip>/
```

예상 응답은 아래와 같습니다.

```json
{"message":"hello from aks"}
```

이 응답이 돌아오면 세 가지가 동시에 확인된 것입니다.

- 컨테이너가 정상 기동합니다.
- Deployment가 원하는 수의 Pod를 유지합니다.
- Service가 외부 요청을 올바른 Pod 집합으로 연결합니다.

### 10. 초반에 자주 막히는 지점을 미리 봅니다

#### 이미지 pull 실패

가장 흔한 원인은 레지스트리 인증 또는 이미지 이름 오타입니다.

```bash
kubectl describe pod <pod-name>
```

#### Service 외부 IP가 오래 안 붙음

Azure Load Balancer 프로비저닝이 아직 진행 중일 수 있습니다.

```bash
kubectl describe service fastapi-hello
```

#### Pod는 뜨는데 Ready가 안 됨

이 경우는 `/healthz` 경로나 포트, 또는 readiness probe 타이밍을 먼저 보는 편이 좋습니다. 프로세스가 살아 있는 것과 트래픽을 받을 준비가 된 것은 같은 말이 아닙니다.

### 11. 실습이 끝난 뒤 남아야 하는 감각

이번 글의 목적은 YAML 문법 암기가 아닙니다. 아래 순서를 몸으로 기억하는 데 있습니다.

1. `az aks create`로 Azure 쪽 클러스터를 만든다.
2. `az aks get-credentials`로 Kubernetes API에 붙는다.
3. `kubectl apply -f`로 원하는 상태를 선언한다.
4. Deployment와 Service가 그 상태를 실제 Pod와 엔드포인트로 만든다.

이 흐름만 분명하면 이후 Ingress를 붙이거나 HPA를 켜거나 관측 도구를 추가하는 일도 모두 같은 언어로 이어집니다.

### 12. ConfigMap과 Secret을 붙여 실제 운영 형태에 가깝게 만듭니다

첫 배포가 끝났다면 다음으로 해야 할 일은 설정과 비밀값을 컨테이너 이미지에서 분리하는 것입니다. 실습 단계에서도 이 습관을 일찍 붙이면 배포 파이프라인과 운영 경계가 훨씬 명확해집니다.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fastapi-hello-config
data:
  APP_ENV: "dev"
  LOG_LEVEL: "info"
---
apiVersion: v1
kind: Secret
metadata:
  name: fastapi-hello-secret
type: Opaque
stringData:
  API_KEY: "replace-me"
```

그리고 Deployment의 컨테이너에 `envFrom` 또는 `env`를 연결합니다.

```yaml
envFrom:
  - configMapRef:
      name: fastapi-hello-config
  - secretRef:
      name: fastapi-hello-secret
```

이 구조의 장점은 명확합니다. 이미지 재빌드 없이도 환경값을 조정할 수 있고, 민감 정보의 변경 이력을 애플리케이션 코드 변경과 분리할 수 있습니다. AKS 운영에서 “배포 실패”와 “설정 오류”를 구분하는 데도 큰 도움이 됩니다.

### 13. 실패 상황을 일부러 만들어 보고 확인 포인트를 익힙니다

입문 실습에서도 한 번쯤은 의도적으로 실패를 만들어 보는 편이 좋습니다. 예를 들어 이미지 태그를 존재하지 않는 값으로 바꾼 뒤 `kubectl describe pod`를 보면 `ImagePullBackOff` 흐름을 실제로 확인할 수 있습니다. 이 경험은 이후 장애 대응 속도를 크게 올려 줍니다.

```bash
kubectl set image deployment/fastapi-hello app=<your-registry>/fastapi-hello:not-exist
kubectl get pods -w
kubectl describe pod <pod-name>
kubectl rollout undo deployment/fastapi-hello
```

핵심은 실패를 피하는 것이 아니라, 실패를 빠르게 분류하고 되돌리는 루프를 팀 표준으로 만드는 일입니다. 첫 클러스터 실습의 완성도는 성공 화면보다 복구 동작에서 더 명확하게 드러납니다.

### 14. Ingress 전환의 첫 단추까지 함께 경험해 봅니다

실습을 한 단계 더 확장하면 5화 내용을 훨씬 쉽게 이해할 수 있습니다. `LoadBalancer` Service로 바로 노출했던 구조를 `ClusterIP + Ingress` 구조로 바꿔 보면, 외부 공개 모델이 어떻게 정리되는지 즉시 체감됩니다.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: fastapi-hello
spec:
  type: ClusterIP
  selector:
    app: fastapi-hello
  ports:
    - port: 80
      targetPort: 8000
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: fastapi-hello
spec:
  ingressClassName: webapprouting.kubernetes.azure.com
  rules:
    - host: hello.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: fastapi-hello
                port:
                  number: 80
```

이 전환의 핵심은 공개 표면을 줄이는 것입니다. 서비스가 늘어날수록 `LoadBalancer`를 서비스마다 하나씩 두는 방식은 운영 부담이 빠르게 커집니다. 반면 Ingress를 사용하면 인증서와 도메인 라우팅을 한 계층에서 통제할 수 있습니다.

### 15. 배포 후 확인 명령을 표준화합니다

첫 클러스터 실습에서 가장 큰 실수는 “성공했다”를 `kubectl get pods` 한 줄로 판단하는 것입니다. 실제로는 rollout, endpoint, 요청 검증까지 같이 봐야 운영 관점에서 완료입니다.

```bash
kubectl rollout status deployment/fastapi-hello
kubectl get endpoints fastapi-hello
kubectl get ingress
kubectl get events -A --sort-by=.lastTimestamp
```

`rollout status`는 선언한 버전이 실제로 배치됐는지를, `endpoints`는 Service가 실제 Pod를 잡았는지를, `events`는 보이지 않는 실패 힌트를 보여 줍니다. 이 네 줄을 습관화하면 “보기에 Running인데 서비스는 안 되는” 상황에서 진단 속도가 크게 올라갑니다.

## 흔히 헷갈리는 지점

- `az aks create`만 끝나면 앱 배포까지 끝난 것처럼 느끼기 쉽지만, 그다음부터가 Kubernetes 객체 작업입니다.
- system pool이 있으니 앱도 거기에 바로 올려도 된다고 생각하기 쉽지만, 기본 원칙은 user pool 분리입니다.
- readiness와 liveness를 같은 체크로만 이해하기 쉽지만, 운영상 의미가 다릅니다.
- Service를 만들면 곧바로 외부 IP가 즉시 생길 것이라 기대하기 쉽지만, 클라우드 리소스 프로비저닝 시간이 필요할 수 있습니다.
- Pod가 Running이면 곧바로 정상 서비스라고 생각하기 쉽지만, Ready 여부와 실제 응답 확인이 따로 필요합니다.

## 운영 체크리스트

- [ ] 리전, 노드 SKU, Kubernetes 버전 같은 최소 설계 값을 사전에 정했는가
- [ ] system pool과 user pool을 분리하는 이유를 이해한 상태에서 클러스터를 만들었는가
- [ ] `az aks get-credentials` 이후 `kubectl get nodes`로 실제 연결을 검증했는가
- [ ] 첫 Deployment에도 startup/readiness/liveness probe를 구분해 정의했는가
- [ ] Service 노출 방식을 `LoadBalancer`로 둘지, 이후 `ClusterIP + Ingress`로 바꿀지 의도를 가지고 선택했는가

## 정리

이번 글의 실습은 작지만 AKS 운영의 핵심 축이 이미 다 들어 있습니다. Azure CLI로 클러스터와 node pool을 만들고, `kubectl`로 Kubernetes 객체를 선언하고, user node pool에 워크로드를 배치하고, Service로 외부 노출을 만들었습니다. 즉 AKS의 두 세계인 Azure 리소스 관리와 Kubernetes 상태 선언이 한 번에 연결된 셈입니다.

또한 오늘 등장한 Deployment와 Service는 이후 모든 글의 기본 문법이 됩니다. 4화에서는 이 두 객체와 Pod가 각각 어떤 문제를 푸는지 더 또렷하게 분리해서 보게 되고, 5화에서는 오늘 만든 Service 앞단에 Ingress가 추가됩니다.

첫 배포에서 가장 중요하게 남아야 할 감각은 명령어가 아니라 흐름입니다. **클러스터를 만든다, 연결한다, 원하는 상태를 선언한다, 상태를 확인한다.** 이 반복 루프가 AKS 운영의 가장 기본적인 손동작입니다.

## 처음 질문으로 돌아가기

- **실습용 AKS 클러스터를 만들 때 최소한 무엇을 결정해야 할까요?**
  - 최소한 `RESOURCE_GROUP`, `LOCATION`, `CLUSTER_NAME`, `USER_POOL`과 `az aks create --node-count 1`로 시작할 노드 규모는 정해야 합니다. 이후 `--generate-ssh-keys`, 레지스트리 위치, 그리고 `LoadBalancer`로 공개할지 `ClusterIP + Ingress`로 갈지도 같이 잡아야 배포 흐름이 흔들리지 않습니다.
- **기본 system pool 외에 user node pool을 왜 별도로 추가하는 편이 좋을까요?**
  - 본문 예시의 `nodeSelector: kubernetes.azure.com/mode: user`처럼 앱 Pod를 user pool에 올리면 system pool과 역할이 분리됩니다. `az aks nodepool add --mode User`를 먼저 밟아 두면 이후 `fastapi-hello` Deployment가 어디에 배치되어야 하는지와 운영 기준이 함께 선명해집니다.
- **`az aks get-credentials` 이후 `kubectl`이 실제로 어떤 계층과 대화하게 될까요?**
  - `az aks get-credentials --resource-group $RESOURCE_GROUP --name $CLUSTER_NAME` 이후의 `kubectl`은 Azure CLI가 아니라 Kubernetes API와 대화합니다. 그래서 `kubectl apply -f fastapi-hello.yaml`, `kubectl get deployments`, `kubectl get service fastapi-hello`는 클러스터 안 원하는 상태와 실제 배치 결과를 확인하는 단계입니다.

<!-- toc:begin -->
## 시리즈 목차

- [Azure Kubernetes Service 101 (1/7): Azure Kubernetes Service란? — 직접 운영하지 않아도 되는 Kubernetes](./01-what-is-aks.md)
- [Azure Kubernetes Service 101 (2/7): 클러스터 아키텍처 — Control Plane과 Node Pool](./02-cluster-architecture.md)
- **Azure Kubernetes Service 101 (3/7): 첫 클러스터 만들고 앱 배포하기 — Python/FastAPI (현재 글)**
- Azure Kubernetes Service 101 (4/7): Pod·Deployment·Service — 워크로드를 표현하는 세 가지 방식 (예정)
- Azure Kubernetes Service 101 (5/7): 네트워킹과 Ingress — 클러스터 안과 밖을 잇는 길 (예정)
- Azure Kubernetes Service 101 (6/7): 스케일링 — HPA, Cluster Autoscaler, KEDA (예정)
- Azure Kubernetes Service 101 (7/7): 모니터링과 운영 — Container Insights, 로그, 알람 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [Deploy an Azure Kubernetes Service (AKS) Cluster Using Azure CLI](https://learn.microsoft.com/en-us/azure/aks/learn/quick-kubernetes-deploy-cli)
- [Create node pools in Azure Kubernetes Service (AKS)](https://learn.microsoft.com/en-us/azure/aks/create-node-pools)
- [Use system node pools in Azure Kubernetes Service (AKS)](https://learn.microsoft.com/en-us/azure/aks/use-system-pools)
- [az aks create](https://learn.microsoft.com/en-us/cli/azure/aks#az-aks-create)
- [az aks get-credentials](https://learn.microsoft.com/en-us/cli/azure/aks#az-aks-get-credentials)

### 관련 시리즈

- [Azure App Service 101](../../azure-app-service-101/ko/04-first-deploy.md) — 같은 FastAPI 앱을 더 높은 수준의 PaaS에 올리는 흐름과 비교할 때
- [Azure Functions 101](../../azure-functions-101/ko/) — 코드 배포 단위가 컨테이너와 어떻게 다른지 비교할 때

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-aks-101/ko/03-first-cluster-and-deploy)

Tags: Azure, AKS, Kubernetes, Cloud
