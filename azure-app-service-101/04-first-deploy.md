# 첫 번째 배포: 로컬에서 Azure까지 (Python/Flask)

> Azure App Service 101 시리즈 (4/7)

이론은 충분합니다. 이제 실제로 **Flask 앱을 Azure App Service에 배포**해 봅시다.

이 글에서는 로컬 개발 환경 설정부터 Azure 배포, 그리고 정상 동작 확인까지 전 과정을 다룹니다.

---

## 목표

이 튜토리얼을 마치면:

- ✅ 로컬에서 Flask 앱을 프로덕션 모드로 실행
- ✅ Azure에 App Service Plan과 Web App 생성
- ✅ 소스 코드를 Azure에 배포
- ✅ Health 엔드포인트로 정상 동작 확인

---

## 사전 준비

| 항목 | 버전/요구사항 |
|------|--------------|
| Python | 3.11 이상 |
| Azure CLI | 최신 버전, 로그인 완료 |
| Azure 구독 | 활성화된 구독 |

```bash
# Azure CLI 버전 확인 및 로그인
az --version
az login
```

![IMAGE: az login 성공 화면]
`📸 캡처: 터미널에서 az login 성공 후 구독 목록 출력`

---

## Step 1: 프로젝트 구조 준비

### 최소 Flask 앱 구조

```
my-flask-app/
├── src/
│   └── app.py
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

```
Flask==3.0.0
gunicorn==21.2.0
```

![IMAGE: VS Code에서 프로젝트 구조]
`📸 캡처: VS Code 또는 에디터에서 프로젝트 폴더 구조`

---

## Step 2: 로컬에서 실행 (개발 모드)

### 가상환경 생성 및 활성화

```bash
cd my-flask-app
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

### 의존성 설치

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Flask 개발 서버 실행

```bash
export FLASK_APP=src.app:app
export FLASK_ENV=development
flask run --port 8000
```

### 테스트

```bash
curl http://localhost:8000/
curl http://localhost:8000/health
```

**예상 출력:**
```json
{"message": "Hello from Azure App Service!", "environment": "development"}
{"status": "healthy"}
```

![IMAGE: 로컬 Flask 서버 실행 화면]
`📸 캡처: 터미널에서 flask run 실행 후 curl 테스트`

---

## Step 3: 로컬에서 실행 (프로덕션 모드)

Azure App Service는 **Gunicorn**으로 Python 앱을 실행합니다. 배포 전에 로컬에서 동일하게 테스트하세요.

```bash
export PORT=8000
gunicorn --bind=0.0.0.0:$PORT src.app:app
```

### 워커 및 타임아웃 설정 테스트

```bash
gunicorn --bind=0.0.0.0:$PORT --workers 2 --timeout 120 src.app:app
```

```bash
curl http://localhost:8000/health
```

**왜 중요한가?**
- Flask 개발 서버와 Gunicorn의 동작이 다를 수 있음
- 타임아웃, 워커 수에 따른 동시성 차이
- 배포 후 "로컬에선 됐는데..." 문제 예방

![IMAGE: Gunicorn 실행 화면]
`📸 캡처: gunicorn 실행 로그 (Starting gunicorn, worker 정보)`

---

## Step 4: Azure 리소스 생성

### 변수 설정

```bash
RG="rg-flask-tutorial"
APP_NAME="app-flask-demo-$(openssl rand -hex 4)"  # 유니크한 이름
PLAN_NAME="plan-flask-tutorial"
LOCATION="koreacentral"

echo "App Name: $APP_NAME"
```

### Resource Group 생성

```bash
az group create \
    --name $RG \
    --location $LOCATION
```

### App Service Plan 생성

```bash
az appservice plan create \
    --resource-group $RG \
    --name $PLAN_NAME \
    --is-linux \
    --sku B1
```

### Web App 생성

```bash
az webapp create \
    --resource-group $RG \
    --plan $PLAN_NAME \
    --name $APP_NAME \
    --runtime "PYTHON|3.11"
```

![IMAGE: Azure Portal에서 생성된 리소스들]
`📸 캡처: Azure Portal → Resource Group → 생성된 Plan과 Web App`

---

## Step 5: 배포 설정

### Oryx 빌드 활성화

App Service의 Oryx 빌드 시스템이 `requirements.txt`를 감지하고 자동으로 의존성을 설치하게 합니다.

```bash
az webapp config appsettings set \
    --resource-group $RG \
    --name $APP_NAME \
    --settings SCM_DO_BUILD_DURING_DEPLOYMENT=true
```

### Startup Command 설정

```bash
az webapp config set \
    --resource-group $RG \
    --name $APP_NAME \
    --startup-file "gunicorn --bind=0.0.0.0:\$PORT src.app:app"
```

> ⚠️ `$PORT`는 App Service가 자동으로 주입하는 환경변수입니다. 백슬래시로 이스케이프하세요.

![IMAGE: Configuration에서 Startup Command 확인]
`📸 캡처: Azure Portal → App Service → Configuration → General settings → Startup Command`

---

## Step 6: 소스 코드 배포

### az webapp up 사용 (가장 간단)

```bash
az webapp up \
    --resource-group $RG \
    --name $APP_NAME \
    --runtime "PYTHON:3.11"
```

이 명령은:
1. 현재 디렉토리를 ZIP으로 패키징
2. App Service에 업로드
3. Oryx가 빌드 실행 (pip install)
4. 앱 재시작

### 배포 완료 확인

```bash
az webapp show \
    --resource-group $RG \
    --name $APP_NAME \
    --query "state" \
    --output tsv
```

**출력:** `Running`

![IMAGE: 배포 진행 중 터미널 출력]
`📸 캡처: az webapp up 실행 시 출력되는 배포 로그`

---

## Step 7: 배포 검증

### 앱 URL 확인

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

**예상 출력:**
```json
{"status": "healthy"}
```

### 메인 페이지 확인

```bash
curl $APP_URL/
```

**예상 출력:**
```json
{"message": "Hello from Azure App Service!", "environment": "development"}
```

![IMAGE: 브라우저에서 앱 접속 화면]
`📸 캡처: 브라우저에서 https://<app-name>.azurewebsites.net 접속`

---

## Step 8: 로그 확인

### 로깅 활성화

```bash
az webapp log config \
    --resource-group $RG \
    --name $APP_NAME \
    --application-logging filesystem \
    --level information
```

### 실시간 로그 스트림

```bash
az webapp log tail \
    --resource-group $RG \
    --name $APP_NAME
```

요청을 보내면 로그가 실시간으로 표시됩니다.

![IMAGE: Log stream 화면]
`📸 캡처: az webapp log tail 실행 중 로그 출력`

---

## Step 9: Azure Portal에서 확인

### Deployment Center

배포 이력과 상태를 확인할 수 있습니다.

**경로:** App Service → Deployment Center

![IMAGE: Deployment Center 화면]
`📸 캡처: Azure Portal → App Service → Deployment Center`

### Kudu (SCM) 사이트

고급 진단 및 파일 브라우저:

```
https://<app-name>.scm.azurewebsites.net
```

**주요 기능:**
- 파일 브라우저: `/home/site/wwwroot` 확인
- Bash 콘솔: 컨테이너 내부 명령 실행
- 환경 변수 확인

![IMAGE: Kudu 파일 브라우저]
`📸 캡처: Kudu → Debug console → Bash → /home/site/wwwroot`

---

## 문제 해결

### 502 Bad Gateway

| 원인 | 해결 |
|------|------|
| 포트 바인딩 오류 | `$PORT` 환경변수 사용 확인 |
| Startup command 오류 | 경로와 모듈명 확인 |
| 의존성 설치 실패 | 배포 로그에서 pip 에러 확인 |

### 로그에서 확인

```bash
# 배포 로그
az webapp log deployment list \
    --resource-group $RG \
    --name $APP_NAME \
    --output table

# 앱 로그
az webapp log tail --resource-group $RG --name $APP_NAME
```

### Kudu SSH로 직접 확인

```bash
az webapp ssh --resource-group $RG --name $APP_NAME
# 컨테이너 내부에서:
ls /home/site/wwwroot
cat /home/LogFiles/*docker*.log
```

---

## Clean Up (선택)

테스트가 끝나면 리소스를 삭제하여 비용을 절약하세요:

```bash
az group delete --name $RG --yes --no-wait
```

---

## 정리

이 튜토리얼에서 배운 것:

1. **로컬 개발**: Flask + Gunicorn으로 프로덕션 패리티 유지
2. **Azure 리소스**: Resource Group → Plan → Web App 생성 흐름
3. **배포**: `az webapp up`으로 간단 배포
4. **검증**: Health endpoint와 로그로 상태 확인

다음 글에서는 **App Settings와 환경변수 관리** - Configuration 마스터하기를 다룹니다.

---

## 시리즈 목차

1. Azure App Service란? - 플랫폼 아키텍처 이해하기
2. Request Lifecycle: 요청이 앱에 도달하기까지
3. Hosting Models: 어떤 플랜을 선택해야 할까?
4. **[현재 글] 첫 번째 배포: 로컬에서 Azure까지 (Python/Flask)**
5. Configuration 마스터하기: App Settings & 환경변수
6. 로그와 모니터링 기초
7. Scaling 101: 언제 Scale Up vs Scale Out?

---

## 참고 자료

- [Quickstart: Deploy a Python web app (Microsoft Learn)](https://learn.microsoft.com/azure/app-service/quickstart-python)
- [Configure a Linux Python app (Microsoft Learn)](https://learn.microsoft.com/azure/app-service/configure-language-python)
- [Kudu service overview (Microsoft Learn)](https://learn.microsoft.com/azure/app-service/resources-kudu)

---

**태그:** `Azure` `App Service` `Python` `Flask` `DevOps` `Tutorial`
