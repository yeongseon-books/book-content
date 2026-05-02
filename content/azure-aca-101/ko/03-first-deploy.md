---
title: 첫 앱 배포하기 — Python/FastAPI
series: azure-aca-101
episode: 3
language: ko
status: publish-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- Azure
- Container Apps
- Serverless
- Containers
last_reviewed: '2026-04-29'
---

# 첫 앱 배포하기 — Python/FastAPI

> Azure Container Apps 101 시리즈 (3/7)

이번 글은 첫 FastAPI 배포 경로를 처음부터 끝까지 잇습니다. ACA는 코드를 대신 빌드해 주는 서비스가 아니라, 이미 만들어 둔 컨테이너 이미지를 Revision으로 실행하는 플랫폼입니다. 그래서 첫 배포를 이해하려면 이미지 빌드, 레지스트리 푸시, 환경 생성, 앱 생성이 한 흐름으로 이어져야 합니다.

---

## 배포 경로 전체 보기

경로를 먼저 보면 배포가 훨씬 단순하게 느껴집니다.

![로컬 코드가 ACA 배포로 이어지는 경로](../../../assets/azure-aca-101/03/03-01-the-end-to-end-path.ko.png)
---

## 준비 명령

```bash
az extension add --name containerapp --upgrade
az provider register --namespace Microsoft.App
az provider register --namespace Microsoft.OperationalInsights
```

첫 배포가 실제로 끝나려면 아래 네 가지가 필요합니다.

- 리소스 그룹
- Azure Container Apps 환경
- ACA가 이미지를 가져갈 컨테이너 레지스트리
- 그 레지스트리에 실제로 올라가 있는 이미지 태그

변수를 먼저 잡아 두면 뒤 명령이 훨씬 읽기 쉬워집니다.

```bash
RG="rg-aca-101-demo"
LOCATION="eastus"
ACA_ENV="aca-env-101-demo"
ACR_NAME="aca101demo$RANDOM"
APP_NAME="fastapi-aca-demo"
IMAGE="$ACR_NAME.azurecr.io/fastapi-hello:v1"
```

---

## FastAPI 앱

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "hello from azure container apps"}

@app.get("/healthz")
def healthz():
    return {"status": "ok"}
```

---

## Dockerfile

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 먼저 이미지를 빌드하고 올리기

실제 첫 배포에서는 레지스트리 단계가 숨은 전제가 아니라 핵심 단계입니다.

```bash
az acr create --name $ACR_NAME --resource-group $RG --location $LOCATION --sku Basic
az acr build --registry $ACR_NAME --image fastapi-hello:v1 .
```

이미 CI 파이프라인이 있다면 그 파이프라인이 이미지를 빌드해도 됩니다. 중요한 건 하나입니다. ACA는 "기존 이미지 참조"를 배포한다는 점입니다.

---

## ACA 환경 만들기

```bash
az containerapp env create \
  --name $ACA_ENV \
  --resource-group $RG \
  --location $LOCATION
```

Environment는 네트워크, 로그, 선택적 통합 기능을 공유하는 경계입니다. 뒤에서 만드는 앱 Revision은 이 Environment 안에서 실행됩니다.

---

## 첫 앱 Revision 만들기

- ingress external
- target-port 8000
- min-replicas 0

```bash
az containerapp create   --name $APP_NAME   --resource-group $RG   --environment $ACA_ENV   --image $IMAGE   --ingress external   --target-port 8000   --cpu 0.5   --memory 1.0Gi   --min-replicas 0   --max-replicas 3
```

이 지점부터 ACA가 단순한 컨테이너 실행기가 아니라 Revision 플랫폼으로 보이기 시작합니다. 하나의 이미지 태그와 하나의 앱 설정이 결합되고, ACA는 그 조합으로 새 Revision을 만듭니다.

---

## 확인 명령

```bash
az containerapp show --name $APP_NAME --resource-group $RG --query properties.configuration.ingress.fqdn --output tsv
curl https://<YOUR_FQDN>/
```

---

## 첫 배포에서 남겨야 할 감각

- ACA가 무엇을 실행하는지는 결국 이미지 태그가 결정합니다.
- Environment와 App는 책임이 다른 계층이므로 같은 것으로 취급하면 안 됩니다.
- 배포 확인도 항상 Revision 기준으로 읽어야 합니다. 어떤 Revision이 만들어졌고, 정상화됐고, 어떤 FQDN이 응답하는지를 확인해야 합니다.

---

<!-- toc:begin -->
## 시리즈 목차

- [Azure Container Apps란? — Kubernetes 없이 컨테이너 운영하기](./01-what-is-aca.md)
- [Environment·Container App·Revision — 세 단어로 보는 ACA](./02-environment-app-revision.md)
- **첫 앱 배포하기 — Python/FastAPI (현재 글)**
- Ingress와 트래픽 분할 — Revision 기반 배포 전략 (예정)
- 스케일링 — KEDA scaler와 0-to-N (예정)
- Dapr 통합 — 사이드카로 얻는 것 (예정)
- 모니터링과 운영 — Log Analytics와 Application Insights (예정)

<!-- toc:end -->

---

## 참고 자료

### 공식 문서
- [Quickstart: Deploy your first container app with containerapp up — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/get-started)
- [az containerapp create — Microsoft Learn](https://learn.microsoft.com/en-us/cli/azure/containerapp#az-containerapp-create)
- [Azure Container Apps environments — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/environment)
- [Run containers from any registry — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/containers)

### 관련 시리즈
- [Azure App Service 101](../../azure-app-service-101/ko/01-what-is-app-service.md)
- [Azure AKS 101](../../azure-aks-101/ko/01-what-is-aks.md)
- [Azure Functions 101](../../azure-functions-101/ko/01-what-is-azure-functions.md)

Tags: Azure, Container Apps, Serverless, Containers
