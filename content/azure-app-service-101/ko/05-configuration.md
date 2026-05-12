---
title: 'Configuration 마스터하기: App Settings & 환경변수'
series: azure-app-service-101
episode: 5
language: ko
status: publish-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- Azure
- App Service
- Cloud
- Web Apps
last_reviewed: '2026-05-12'
seo_description: App Settings, slot setting, Key Vault를 나눠 App Service 설정을 안전하게 관리하는 방법을 정리합니다.
---

# Configuration 마스터하기: App Settings & 환경변수

앱 배포가 끝나면 바로 다음 문제가 시작됩니다. 환경마다 다른 연결 문자열, API 키, 로그 레벨을 어떻게 관리할지 정하지 않으면 배포는 끝나도 운영은 계속 흔들립니다.

이 글은 Azure App Service 101 시리즈의 5번째 글입니다.

여기서는 개발, 스테이징, 프로덕션을 가로질러 설정 변경을 예측 가능하고 안전하게 만드는 방법을 다룹니다. 핵심은 코드와 설정을 분리하고, 민감 정보와 환경별 값을 같은 바구니에 넣지 않는 것입니다.

---

## 이 글에서 다룰 문제

- app setting, connection string, 환경 변수(env var)는 런타임(runtime)에서 어떤 방식으로 노출될까요?
- slot-sticky 설정은 실제로 어떤 상황에서 도움이 될까요?
- Key Vault reference는 일반 app setting과 무엇이 다르고, 권한(permission)은 어떤 흐름으로 연결될까요?
- 어떤 설정 변경은 앱을 자동으로 재시작시키고, 어떤 변경은 그렇지 않을까요?
- App Settings가 저장 시 암호화(encrypted at rest)되더라도, 왜 진짜 비밀 정보(secret)는 여기에 두면 안 될까요?

## Why Configuration Matters

### The Twelve-Factor App Principle

> "Separate configuration from code"

- Settings hardcoded in code
- Different code branches per environment
- Settings injected via environment variables
- Same code, different settings

### App Service's Approach

App Service는 **App Settings**를 통해 환경 변수를 주입합니다.

![Settings injected into app environment](../../../assets/azure-app-service-101/05/configuration-flow.en.png)

*설정이 앱 환경 변수로 주입되는 흐름*

```text
[Azure Portal/CLI] → App Settings → [Environment Variables] → [App Process]
```

> 설정은 값 저장소가 아니라 런타임 이벤트입니다. App Service에서 설정을 바꾸는 순간, 그 변경은 곧 프로세스 재시작과 동작 변화로 이어질 수 있습니다.

---

## App Settings Basics

### Setting App Settings

**Azure CLI:**
```bash
az webapp config appsettings set \
 --resource-group $RG \
 --name $APP_NAME \
 --settings FLASK_DEBUG=0 APP_ENV=production LOG_LEVEL=INFO
```

**Azure Portal:**
1. App Service → Configuration
2. Application settings tab
3. Click "+ New application setting"

### Reading in Your App

```python
import os

# Access directly as environment variables
FLASK_DEBUG = os.environ.get("FLASK_DEBUG", "0")
APP_ENV = os.environ.get("APP_ENV", "production")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
DB_HOST = os.environ.get("DB_HOST", "localhost")
```

### Verify Current Settings

```bash
az webapp config appsettings list \
 --resource-group $RG \
 --name $APP_NAME \
 --output table
```

**Example output:**
```
Name Value
----------------------------- -----------------
FLASK_DEBUG 0
APP_ENV production
LOG_LEVEL INFO
SCM_DO_BUILD_DURING_DEPLOYMENT true
```

---

## Local vs Production Strategy

### Environment Separation Pattern

![Configuration strategy by environment stage](../../../assets/azure-app-service-101/05/environment-strategy.en.png)

*환경 단계별 설정 전략*

```python
# config.py
import os

class Config:
 """Base configuration"""
 SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
 LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

class DevelopmentConfig(Config):
 """Local development"""
 DEBUG = True
 DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///dev.db")

class ProductionConfig(Config):
 """Azure App Service"""
 DEBUG = False
 DATABASE_URL = os.environ.get("DATABASE_URL") # Required

# Select based on environment
config = {
 "development": DevelopmentConfig,
 "production": ProductionConfig,
}

def get_config():
 env = os.environ.get("APP_ENV", "development")
 return config.get(env, DevelopmentConfig)
```

### Local Development: .env File

Flask 2.3과 3.x는 더 이상 `FLASK_ENV`를 쓰지 않으므로, 환경 선택은 `APP_ENV` 같은 자체 설정으로 유지하고 debugger는 로컬에서만 `FLASK_DEBUG=1`로 명시적으로 켭니다.

```bash
# .env (local only, add to .gitignore!)
FLASK_DEBUG=1
APP_ENV=development
LOG_LEVEL=DEBUG
DATABASE_URL=postgresql://localhost:5432/myapp
SECRET_KEY=local-dev-key
```

```python
# Using python-dotenv
from dotenv import load_dotenv
load_dotenv() # Load .env file
```

```bash
pip install python-dotenv
```

### .gitignore is required

```gitignore
# .gitignore
.env
.env.local
*.env
```

---

## Connection Strings

데이터베이스 연결 문자열은 별도 섹션으로 관리할 수 있습니다.

### Setting Connection Strings

```bash
az webapp config connection-string set \
 --resource-group $RG \
 --name $APP_NAME \
 --connection-string-type PostgreSQL \
 --settings "DATABASE=Server=myserver.postgres.database.azure.com;Database=mydb;..."
```

### App Settings vs Connection Strings

| Item | App Settings | Connection Strings |
|------|-------------|-------------------|
| Purpose | General settings | DB connections only |
| Format | `KEY=VALUE` | Type can be specified |
| App Access | `os.environ["KEY"]` | `os.environ["SQLAZURECONNSTR_NAME"]` |

> **실무 팁:** 대부분의 경우 App Settings만으로도 충분합니다.

---

## Slot Settings (Sticky Settings)

Deployment Slot을 쓰는 경우, 어떤 설정은 **slot에 고정**되어야 합니다.

### When Slot Settings Are Needed

| Setting | Sticky? | Reason |
|---------|---------|--------|
| `APP_ENV` | Yes | Staging은 staging, production은 production이어야 함 |
| `DATABASE_URL` | Yes | 환경별 DB가 달라야 함 |
| `LOG_LEVEL` | No | 대개 동일함 |
| `FEATURE_FLAG_X` | Depends | slot별 테스트면 sticky 필요 |

![Settings that stay during slot swap](../../../assets/azure-app-service-101/05/slot-settings-behavior.en.png)

*slot swap 중에도 유지되는 설정*

### Configuring Slot Settings

```bash
az webapp config appsettings set \
 --resource-group $RG \
 --name $APP_NAME \
 --slot-settings APP_ENV=production
```

`--slot-settings`는 `--settings`와 같은 `KEY=VALUE` 형식을 씁니다. 여기에 넘긴 값은 slot에 sticky로 표시되어 swap 후에도 그 slot에 남습니다.

**Azure Portal:**
1. Configuration → Application settings
2. Check "Deployment slot setting" checkbox next to setting

---

## Key Vault References: Secrets Done Right

비밀번호와 API 키 같은 민감 값은 **Key Vault**에 저장하고 참조합니다.

![Secrets flowing from Key Vault to app](../../../assets/azure-app-service-101/05/key-vault-reference-flow.en.png)

*Key Vault에서 앱으로 흘러가는 secret 참조 흐름*

### Why Key Vault?

| Direct App Settings | Key Vault Reference |
|--------------------|---------------------|
| Values visible in Portal | Values hidden |
| No version control | Automatic versioning |
| No audit logs | Access audit logs |
| Hard to share | Reference from multiple apps |

### Step 1: Create Key Vault

```bash
KEYVAULT_NAME="kv-myapp-$(openssl rand -hex 4)"

az keyvault create \
 --resource-group $RG \
 --name $KEYVAULT_NAME \
 --location $LOCATION
```

### Step 2: Store Secret

```bash
az keyvault secret set \
 --vault-name $KEYVAULT_NAME \
 --name "DbPassword" \
 --value "super-secret-password"
```

### Step 3: Enable Managed Identity

```bash
az webapp identity assign \
 --resource-group $RG \
 --name $APP_NAME
```

### Step 4: Grant Key Vault Access (RBAC)

```bash
PRINCIPAL_ID=$(az webapp identity show \
 --resource-group $RG \
 --name $APP_NAME \
 --query principalId \
 --output tsv)

KEYVAULT_ID=$(az keyvault show \
 --name $KEYVAULT_NAME \
 --query id \
 --output tsv)

az role assignment create \
 --role "Key Vault Secrets User" \
 --assignee $PRINCIPAL_ID \
 --scope $KEYVAULT_ID
```

### Step 5: Configure Key Vault Reference

```bash
az webapp config appsettings set \
 --resource-group $RG \
 --name $APP_NAME \
 --settings "DB_PASSWORD=@Microsoft.KeyVault(SecretUri=https://$KEYVAULT_NAME.vault.azure.net/secrets/DbPassword/)"
```

### Using in Your App

```python
# Key Vault Reference accessed like regular environment variable
DB_PASSWORD = os.environ.get("DB_PASSWORD")
# Value automatically injected!
```

---

## Impact of Configuration Changes

### Configuration changes are runtime events

App Settings를 바꾸면 **앱이 재시작**됩니다.

**Impact:**
- 진행 중인 요청이 끊길 수 있음
- cold start 발생
- cache 초기화

### Minimizing Change Impact

1. **Batch Updates**: 여러 설정을 한 번에 변경
2. **Deployment Slots**: staging에서 먼저 테스트
3. **Maintenance Window**: 트래픽이 낮을 때 변경

```bash
# Change multiple settings at once (single restart)
az webapp config appsettings set \
 --resource-group $RG \
 --name $APP_NAME \
 --settings KEY1=value1 KEY2=value2 KEY3=value3
```

---

## Verifying Configuration

### Check Current Settings

```bash
# List all settings
az webapp config appsettings list \
 --resource-group $RG \
 --name $APP_NAME \
 --output json

# Check specific setting
az webapp config appsettings list \
 --resource-group $RG \
 --name $APP_NAME \
 --query "[?name=='LOG_LEVEL']"
```

### Verify Inside App (Debugging)

```python
@app.route('/debug/config')
def debug_config():
 # Disable in production!
 if os.environ.get("APP_ENV") != "development":
 return {"error": "Not allowed"}, 403
 
 return {
 "APP_ENV": os.environ.get("APP_ENV"),
 "LOG_LEVEL": os.environ.get("LOG_LEVEL"),
 # Mask sensitive values
 "DB_PASSWORD": "***" if os.environ.get("DB_PASSWORD") else None
 }
```

---

## Best Practices Checklist

### DO

- [ ] Store sensitive values in Key Vault
- [ ] Use Slot Settings for environment-specific config
- [ ] Add .env files to .gitignore
- [ ] Batch configuration changes
- [ ] Validate required settings at app startup

### DON'T

- [ ] Hardcode secrets in code
- [ ] Commit .env files to Git
- [ ] Expose debug endpoints in production
- [ ] Change settings one at a time

---

## 정리

Configuration 관리에서 기억할 기본 원칙은 아래와 같습니다.

- **App Settings**: 환경 변수로 주입되며, 변경 시 앱이 재시작됩니다.
- **Environment Separation**: 로컬은 `.env`, Azure는 App Settings로 나눕니다.
- **Slot Settings**: 환경별로 고정되어야 하는 값은 sticky로 둡니다.
- **Key Vault**: 진짜 민감 값은 여기로 보냅니다.

설정은 배포 부가 기능이 아니라 운영 안정성과 보안의 중심입니다. 같은 코드를 여러 환경에 올리더라도, 무엇이 바뀌고 무엇이 그대로여야 하는지 명확하면 운영이 훨씬 예측 가능해집니다.

<!-- toc:begin -->
## 시리즈 목차

- [Azure App Service란? - 플랫폼 아키텍처 이해하기](./01-what-is-app-service.md)
- [Request Lifecycle: 3am에 터진 502를 어디서부터 봐야 할까](./02-request-lifecycle.md)
- [Hosting Models: 어떤 플랜을 선택해야 할까?](./03-hosting-models.md)
- [첫 번째 배포: 로컬에서 Azure까지 (Python/Flask)](./04-first-deploy.md)
- **Configuration 마스터하기: App Settings & 환경변수 (현재 글)**
- 로그와 모니터링 기초: “앱이 느려요”에 답할 수 있는 상태 만들기 (예정)
- Scaling 101: 언제 Scale Up vs Scale Out? (예정)

<!-- toc:end -->

---

## 참고 자료

### 공식 문서
- [Configure an App Service app (Microsoft Learn)](https://learn.microsoft.com/azure/app-service/configure-common)
- [Use Key Vault references (Microsoft Learn)](https://learn.microsoft.com/azure/app-service/app-service-key-vault-references)
- [The Twelve-Factor App - Config](https://12factor.net/config)

### 관련 시리즈
- [Azure Functions 101](../../azure-functions-101/ko/)

---

Tags: Azure, App Service, Cloud, Web Apps
