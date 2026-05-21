---
title: '첫 번째 배포: 로컬에서 Azure까지 (Python/Flask)'
series: azure-app-service-101
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
- App Service
- Cloud
- Web Apps
last_reviewed: '2026-05-12'
seo_description: Flask 앱을 로컬에서 검증하고 Azure App Service에 첫 배포한 뒤 상태와 로그까지 확인하는 흐름을 정리합니다.
---

# 첫 번째 배포: 로컬에서 Azure까지 (Python/Flask)

이제 시리즈를 실제 배포로 연결할 차례입니다. 로컬에서 잘 돌던 Flask 앱을 App Service에 올리고, 런타임 경로가 제대로 열렸는지 직접 확인해 보겠습니다.

이 글은 Azure App Service 101 시리즈의 4번째 글입니다.

여기서는 로컬 개발 환경 준비부터 Azure 리소스 생성, 첫 배포, 상태 검증, 로그 확인까지 한 번에 따라가겠습니다. 목표는 “배포가 됐다”에서 끝나지 않고, 왜 이 설정이 필요한지까지 이해하는 것입니다.

---

## 이 글에서 다룰 문제

- 첫 번째 App Service 배포 전에 반드시 확정해 두어야 할 파라미터는 무엇일까요?
- run-from-package 방식은 content deploy 방식과 무엇이 다를까요?
- dev/stage/prod 환경에서 deployment slot 전략은 어디서부터 시작하는 것이 좋을까요?
- 첫 배포 직후 health check가 자동으로 돌게 하려면 무엇을 켜 두어야 할까요?
- 첫 배포에서 가장 자주 부딪히는 인증(auth)·권한(permission) 실패는 어떤 것들일까요?

## Goals

이 글을 마치면 Flask 앱을 로컬에서 실행하고, Azure App Service에 배포하고, 로그와 health endpoint로 배포가 정상인지 반복 가능하게 검증할 수 있습니다.

![From local development to Azure deployment](https://yeongseon-books.github.io/book-public-assets/assets/azure-app-service-101/04/01-deployment-pipeline.ko.png)

*로컬 개발에서 Azure 배포까지 이어지는 흐름*

> 첫 배포의 핵심은 “코드를 올리는 것”이 아니라 “로컬에서 확인한 실행 계약을 Azure에서도 그대로 재현하는 것”입니다.

---

## Prerequisites

| Item | Version/Requirement |
|------|---------------------|
| Python | 3.11 or higher |
| Azure CLI | Latest version, logged in |
| Azure Subscription | Active subscription |

```bash
# Check Azure CLI version and login
az --version
az login
```

---

## Step 1: Prepare Project Structure

### Minimal Flask App Structure

```text
my-flask-app/
├── src/
│ └── app.py
├── requirements.txt
└── README.md
```

### app.py

```python
# src/app.py
import os
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
 return jsonify({
 "message": "Hello from Azure App Service!",
 "environment": os.environ.get("APP_ENV", "development")
 })

@app.route('/health')
def health():
 return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
 port = int(os.environ.get("PORT", 8000))
 app.run(host="0.0.0.0", port=port)
```

### requirements.txt

```text
Flask==3.1.3
gunicorn==25.3.0
```

---

## Step 2: Run Locally (Development Mode)

### Create and Activate Virtual Environment

```bash
cd my-flask-app
python -m venv .venv
source .venv/bin/activate # Windows: .venv\Scripts\activate
```

### Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Run Flask Development Server

```bash
export FLASK_APP=src.app:app
export FLASK_DEBUG=1
flask run --port 8000
```

### Test

```bash
curl http://localhost:8000/
curl http://localhost:8000/health
```

**Expected output:**
```json
{"message": "Hello from Azure App Service!", "environment": "development"}
{"status": "healthy"}
```

---

## Step 3: Run Locally (Production Mode)

Azure App Service는 Python 앱을 **Gunicorn**으로 실행합니다. 배포 전에 같은 구성을 로컬에서도 확인해야 합니다.

```bash
export PORT=8000
gunicorn --bind=0.0.0.0:$PORT src.app:app
```

### Test with Workers and Timeout Settings

```bash
gunicorn --bind=0.0.0.0:$PORT --workers 2 --timeout 120 src.app:app
```

```bash
curl http://localhost:8000/health
```

**Why is this important?**
- Flask dev server and Gunicorn behave differently
- Concurrency varies with timeout and worker count
- Prevents "works locally but not in Azure" issues

---

## Step 4: Create Azure Resources

![Azure resource hierarchy from subscription to web app](https://yeongseon-books.github.io/book-public-assets/assets/azure-app-service-101/04/02-resource-hierarchy.ko.png)

*구독에서 web app까지 이어지는 Azure 리소스 계층*

### Set Variables

```bash
RG="rg-flask-tutorial"
APP_NAME="app-flask-demo-$(openssl rand -hex 4)" # Unique name
PLAN_NAME="plan-flask-tutorial"
LOCATION="koreacentral"

echo "App Name: $APP_NAME"
```

### Create Resource Group

```bash
az group create \
 --name $RG \
 --location $LOCATION
```

### Create App Service Plan

```bash
az appservice plan create \
 --resource-group $RG \
 --name $PLAN_NAME \
 --is-linux \
 --sku B1
```

### Create Web App

```bash
az webapp create \
 --resource-group $RG \
 --plan $PLAN_NAME \
 --name $APP_NAME \
 --runtime "PYTHON|3.11"
```

---

## Step 5: Configure Deployment

### Enable Oryx Build

App Service의 Oryx build 시스템을 켜서 `requirements.txt`를 감지하고 의존성을 자동으로 설치하게 합니다.

```bash
az webapp config appsettings set \
 --resource-group $RG \
 --name $APP_NAME \
 --settings SCM_DO_BUILD_DURING_DEPLOYMENT=true
```

### Set Startup Command

```bash
az webapp config set \
 --resource-group $RG \
 --name $APP_NAME \
 --startup-file "gunicorn --bind=0.0.0.0:\$PORT src.app:app"
```

> `$PORT`는 App Service가 자동으로 주입하는 환경 변수입니다. 백슬래시로 escape해야 합니다.

---

## Step 6: Deploy Source Code

### Using az webapp up (Simplest Method)

```bash
az webapp up \
 --resource-group $RG \
 --name $APP_NAME \
 --runtime "PYTHON|3.11"
```

이 명령은 다음을 수행합니다.

1. 현재 디렉터리를 ZIP으로 패키징
2. App Service에 업로드
3. Oryx가 build 실행 (`pip install`)
4. 앱 재시작

### Verify Deployment Completion

```bash
az webapp show \
 --resource-group $RG \
 --name $APP_NAME \
 --query "state" \
 --output tsv
```

**Output:** `Running`

---

## Step 7: Verify Deployment

### Get App URL

```bash
APP_URL="https://$(az webapp show \
 --resource-group $RG \
 --name $APP_NAME \
 --query defaultHostName \
 --output tsv)"

echo "App URL: $APP_URL"
```

### Health Check

```bash
curl $APP_URL/health
```

**Expected output:**
```json
{"status": "healthy"}
```

### Check Main Page

```bash
curl $APP_URL/
```

**Expected output:**
```json
{"message": "Hello from Azure App Service!", "environment": "development"}
```

---

## Step 8: Check Logs

### Enable Logging

```bash
az webapp log config \
 --resource-group $RG \
 --name $APP_NAME \
 --docker-container-logging filesystem
```

### Real-time Log Stream

```bash
az webapp log tail \
 --resource-group $RG \
 --name $APP_NAME
```

요청을 보내면 로그가 실시간으로 보입니다.

---

## Step 9: Verify in Azure Portal

### Deployment Center

배포 이력과 상태를 확인합니다.

**Path:** App Service → Deployment Center

### Kudu (SCM) Site

고급 진단과 파일 브라우저는 여기서 봅니다.

```text
https://<app-name>.scm.azurewebsites.net
```

**Key features:**
- File browser: Check `/home/site/wwwroot`
- Bash console: Run commands inside container
- Environment variables

---

## Troubleshooting

### 502 Bad Gateway

![Stepwise path to isolate 502 causes](https://yeongseon-books.github.io/book-public-assets/assets/azure-app-service-101/04/03-troubleshooting-502.ko.png)

*502 원인을 단계별로 좁혀 가는 흐름*

| Cause | Solution |
|-------|----------|
| Port binding error | Verify `$PORT` environment variable usage |
| Startup command error | Check path and module name |
| Dependency install failed | Check deployment logs for pip errors |

### Check Logs

```bash
# Deployment logs
az webapp log deployment list \
 --resource-group $RG \
 --name $APP_NAME \
 --output table

# App logs
az webapp log tail --resource-group $RG --name $APP_NAME
```

### Direct Check via Kudu SSH

```bash
az webapp ssh --resource-group $RG --name $APP_NAME
# Inside container:
ls /home/site/wwwroot
cat /home/LogFiles/*docker*.log
```

### 배포 방식별 검증 포인트를 분리해 두면 복구 속도가 빨라집니다

첫 배포 이후에는 ZIP 기반 배포와 컨테이너 배포를 혼용하는 경우가 많습니다. 이때 "배포가 실패했다"는 같은 증상이라도 확인해야 할 로그 경로가 다릅니다.

| 배포 방식 | 우선 확인 | 대표 실패 신호 | 1차 대응 |
| --- | --- | --- | --- |
| ZIP + Oryx | Deployment logs, Oryx build output | `pip install` 실패, 모듈 import 오류 | `requirements.txt`와 Python 버전 재확인 |
| Container(ACR) | Container startup logs, image pull 상태 | image pull 인증 실패, startup command 실패 | Managed Identity/ACR 권한과 태그 확인 |

아래 명령을 배포 직후 체크리스트에 넣어 두면 어떤 레이어에서 실패했는지 빠르게 좁힐 수 있습니다.

```bash
# 최근 배포 이력 확인
az webapp log deployment list \
  --resource-group $RG \
  --name $APP_NAME \
  --output table

# 앱 설정에서 startup command, build 플래그 확인
az webapp config show \
  --resource-group $RG \
  --name $APP_NAME \
  --query "{linuxFxVersion:linuxFxVersion, appCommandLine:appCommandLine}" \
  --output json

az webapp config appsettings list \
  --resource-group $RG \
  --name $APP_NAME \
  --query "[?name=='SCM_DO_BUILD_DURING_DEPLOYMENT' || name=='WEBSITE_RUN_FROM_PACKAGE'].[name,value]" \
  --output table
```

### 첫 배포부터 slot 기반 검증 루틴을 준비하면 이후 운영이 쉬워집니다

초기에는 단일 슬롯으로 시작해도 되지만, staging 슬롯을 일찍 도입하면 배포 검증과 롤백이 단순해집니다. 특히 트래픽이 생기기 시작한 시점부터는 slot swap 전략이 장애 시간을 크게 줄여 줍니다.

```bash
# staging 슬롯 생성
az webapp deployment slot create \
  --resource-group $RG \
  --name $APP_NAME \
  --slot staging

# staging에만 환경변수 주입
az webapp config appsettings set \
  --resource-group $RG \
  --name $APP_NAME \
  --slot staging \
  --settings APP_ENV=staging

# 슬롯 URL 확인 후 health 체크
STAGING_URL="https://$(az webapp show \
  --resource-group $RG \
  --name $APP_NAME \
  --slot staging \
  --query defaultHostName \
  --output tsv)"

curl "$STAGING_URL/health"
```

staging에서 헬스체크와 기본 API smoke test를 통과한 뒤 swap하면, 프로덕션 슬롯에서 바로 실패를 발견하는 위험을 줄일 수 있습니다. 첫 배포 단계에서 이 루틴을 습관화해 두면 이후 CI/CD로 확장할 때도 구조를 거의 그대로 재사용할 수 있습니다.

---

## Clean Up (Optional)

테스트 후 비용을 줄이려면 리소스를 삭제합니다.

```bash
az group delete --name $RG --yes --no-wait
```

---

## 운영 체크리스트

- [ ] region, SKU, runtime version을 처음부터 확정했다
- [ ] deploy method(zip, ACR, GitHub Actions)를 명시적으로 골랐다
- [ ] Managed Identity와 Key Vault 접근을 구성했다
- [ ] health-check 경로와 timeout 기준을 정했다
- [ ] 운영 전 slot-swap rollback을 한 번 연습했다

---

## 정리

이 튜토리얼에서 가져가야 할 핵심은 네 가지입니다.

1. **Local Development**: Flask와 Gunicorn으로 production parity를 미리 확인합니다.
2. **Azure Resources**: Resource Group → Plan → Web App 순서로 리소스를 만듭니다.
3. **Deployment**: `az webapp up`으로 가장 단순한 첫 배포를 수행합니다.
4. **Verification**: Health endpoint와 로그로 실제 실행 상태를 검증합니다.

첫 배포는 성공 메시지보다 검증 루틴이 더 중요합니다. 상태 확인과 로그 확인까지 습관으로 만들면 다음 배포부터 훨씬 안정적으로 움직일 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Azure App Service란? - 플랫폼 아키텍처 이해하기](./01-what-is-app-service.md)
- [Request Lifecycle: 3am에 터진 502를 어디서부터 봐야 할까](./02-request-lifecycle.md)
- [Hosting Models: 어떤 플랜을 선택해야 할까?](./03-hosting-models.md)
- **첫 번째 배포: 로컬에서 Azure까지 (Python/Flask) (현재 글)**
- Configuration 마스터하기: App Settings & 환경변수 (예정)
- 로그와 모니터링 기초: “앱이 느려요”에 답할 수 있는 상태 만들기 (예정)
- Scaling 101: 언제 Scale Up vs Scale Out? (예정)

<!-- toc:end -->

---

## 참고 자료

### 공식 문서
- [Quickstart: Deploy a Python web app (Microsoft Learn)](https://learn.microsoft.com/azure/app-service/quickstart-python)
- [Configure a Linux Python app (Microsoft Learn)](https://learn.microsoft.com/azure/app-service/configure-language-python)
- [Kudu service overview (Microsoft Learn)](https://learn.microsoft.com/azure/app-service/resources-kudu)

### 관련 시리즈
- [Azure Functions 101](../../azure-functions-101/ko/)

---

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-app-service-101/ko/04-first-deploy)

Tags: Azure, App Service, Cloud, Web Apps
