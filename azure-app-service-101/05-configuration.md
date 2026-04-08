# Configuration 마스터하기: App Settings & 환경변수

> Azure App Service 101 시리즈 (5/7)

앱이 배포되었습니다. 이제 **환경별 설정을 어떻게 관리**할까요?

로컬, 스테이징, 프로덕션 환경마다 다른 DB 연결 문자열, API 키, 로그 레벨... 이런 설정들을 안전하고 효율적으로 관리하는 방법을 알아봅니다.

---

## 왜 Configuration이 중요한가?

### The Twelve-Factor App 원칙

> "설정을 코드에서 분리하라"

- ❌ 코드에 하드코딩된 설정
- ❌ 환경별 다른 코드 브랜치
- ✅ 환경변수로 주입되는 설정
- ✅ 동일한 코드, 다른 설정

### App Service의 접근 방식

App Service는 **App Settings**를 통해 환경변수를 주입합니다:

```
[Azure Portal/CLI] → App Settings → [환경변수] → [앱 프로세스]
```

![IMAGE: Configuration 개요 화면]
`📸 캡처: Azure Portal → App Service → Configuration 메인 화면`

---

## App Settings 기본

### App Settings 설정하기

**Azure CLI:**
```bash
az webapp config appsettings set \
    --resource-group $RG \
    --name $APP_NAME \
    --settings FLASK_ENV=production APP_ENV=production LOG_LEVEL=INFO
```

**Azure Portal:**
1. App Service → Configuration
2. Application settings 탭
3. "+ New application setting" 클릭

![IMAGE: App Settings 추가 화면]
`📸 캡처: Azure Portal → Configuration → Application settings → New application setting`

### 앱에서 읽기

```python
import os

# 환경변수로 직접 접근
FLASK_ENV = os.environ.get("FLASK_ENV", "production")
APP_ENV = os.environ.get("APP_ENV", "production")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
DB_HOST = os.environ.get("DB_HOST", "localhost")
```

### 현재 설정 확인

```bash
az webapp config appsettings list \
    --resource-group $RG \
    --name $APP_NAME \
    --output table
```

**출력 예시:**
```
Name                           Value
-----------------------------  -----------------
FLASK_ENV                      production
APP_ENV                        production
LOG_LEVEL                      INFO
SCM_DO_BUILD_DURING_DEPLOYMENT true
```

---

## 로컬 vs 프로덕션 전략

### 환경 분리 패턴

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
    DATABASE_URL = os.environ.get("DATABASE_URL")  # 필수

# 환경에 따라 선택
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}

def get_config():
    env = os.environ.get("APP_ENV", "development")
    return config.get(env, DevelopmentConfig)
```

### 로컬 개발: .env 파일

```bash
# .env (로컬 전용, .gitignore에 추가!)
FLASK_ENV=development
APP_ENV=development
LOG_LEVEL=DEBUG
DATABASE_URL=postgresql://localhost:5432/myapp
SECRET_KEY=local-dev-key
```

```python
# python-dotenv 사용
from dotenv import load_dotenv
load_dotenv()  # .env 파일 로드
```

```bash
pip install python-dotenv
```

### ⚠️ .gitignore 필수!

```gitignore
# .gitignore
.env
.env.local
*.env
```

![IMAGE: .env 파일 예시]
`📸 캡처: VS Code에서 .env 파일과 .gitignore 설정`

---

## Connection Strings

데이터베이스 연결 문자열은 별도 섹션에서 관리됩니다.

### Connection String 설정

```bash
az webapp config connection-string set \
    --resource-group $RG \
    --name $APP_NAME \
    --connection-string-type PostgreSQL \
    --settings "DATABASE=Server=myserver.postgres.database.azure.com;Database=mydb;..."
```

### App Settings vs Connection Strings

| 항목 | App Settings | Connection Strings |
|------|-------------|-------------------|
| 용도 | 일반 설정 | DB 연결 전용 |
| 형식 | `KEY=VALUE` | 타입 지정 가능 |
| 앱 접근 | `os.environ["KEY"]` | `os.environ["SQLAZURECONNSTR_NAME"]` |

> 💡 **실전 팁:** 대부분의 경우 App Settings만으로 충분합니다.

![IMAGE: Connection Strings 설정 화면]
`📸 캡처: Azure Portal → Configuration → Connection strings`

---

## Slot Settings (슬롯 고정 설정)

Deployment Slots를 사용할 때, 일부 설정은 **슬롯에 고정**되어야 합니다.

### Slot Setting이 필요한 경우

| 설정 | Slot 고정? | 이유 |
|------|----------|------|
| `APP_ENV` | ✅ | 스테이징은 staging, 프로덕션은 production |
| `DATABASE_URL` | ✅ | 환경별 다른 DB |
| `LOG_LEVEL` | ❌ | 보통 동일 |
| `FEATURE_FLAG_X` | 상황에 따라 | 슬롯별 테스트 시 고정 |

### Slot Setting 설정

```bash
az webapp config appsettings set \
    --resource-group $RG \
    --name $APP_NAME \
    --settings APP_ENV=production \
    --slot-settings APP_ENV
```

**Azure Portal:**
1. Configuration → Application settings
2. 설정 옆 "Deployment slot setting" 체크박스

![IMAGE: Slot Setting 체크박스]
`📸 캡처: Azure Portal → Configuration에서 Deployment slot setting 체크박스`

---

## Key Vault References: 비밀 값 안전하게

비밀번호, API 키 같은 민감한 값은 **Key Vault**에 저장하고 참조하세요.

### 왜 Key Vault인가?

| App Settings 직접 저장 | Key Vault Reference |
|-----------------------|---------------------|
| Portal에서 값 노출 | 값 숨김 |
| 버전 관리 없음 | 자동 버전 관리 |
| 감사 로그 없음 | 접근 감사 로그 |
| 공유 어려움 | 여러 앱에서 참조 가능 |

### Step 1: Key Vault 생성

```bash
KEYVAULT_NAME="kv-myapp-$(openssl rand -hex 4)"

az keyvault create \
    --resource-group $RG \
    --name $KEYVAULT_NAME \
    --location $LOCATION
```

### Step 2: Secret 저장

```bash
az keyvault secret set \
    --vault-name $KEYVAULT_NAME \
    --name "DbPassword" \
    --value "super-secret-password"
```

### Step 3: Managed Identity 활성화

```bash
az webapp identity assign \
    --resource-group $RG \
    --name $APP_NAME
```

### Step 4: Key Vault 접근 권한 부여 (RBAC)

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

### Step 5: Key Vault Reference 설정

```bash
az webapp config appsettings set \
    --resource-group $RG \
    --name $APP_NAME \
    --settings "DB_PASSWORD=@Microsoft.KeyVault(SecretUri=https://$KEYVAULT_NAME.vault.azure.net/secrets/DbPassword/)"
```

### 앱에서 사용

```python
# Key Vault Reference는 일반 환경변수처럼 접근
DB_PASSWORD = os.environ.get("DB_PASSWORD")
# 값이 자동으로 주입됨!
```

![IMAGE: Key Vault Reference 설정 화면]
`📸 캡처: Azure Portal → Configuration에서 Key Vault Reference 형식의 값`

---

## 설정 변경의 영향

### ⚠️ 중요: 설정 변경 = 앱 재시작

App Settings를 변경하면 **앱이 재시작**됩니다.

**영향:**
- 진행 중인 요청이 끊길 수 있음
- Cold start 발생
- 캐시 초기화

### 변경 최소화 전략

1. **배치 업데이트**: 여러 설정을 한 번에 변경
2. **Deployment Slots**: 스테이징에서 먼저 테스트
3. **점검 시간**: 트래픽이 적은 시간에 변경

```bash
# 한 번에 여러 설정 변경 (재시작 1회)
az webapp config appsettings set \
    --resource-group $RG \
    --name $APP_NAME \
    --settings KEY1=value1 KEY2=value2 KEY3=value3
```

---

## 설정 검증

### 현재 설정 확인

```bash
# 모든 설정 조회
az webapp config appsettings list \
    --resource-group $RG \
    --name $APP_NAME \
    --output json

# 특정 설정만 확인
az webapp config appsettings list \
    --resource-group $RG \
    --name $APP_NAME \
    --query "[?name=='LOG_LEVEL']"
```

### 앱 내부에서 확인 (디버깅용)

```python
@app.route('/debug/config')
def debug_config():
    # 프로덕션에서는 비활성화하세요!
    if os.environ.get("APP_ENV") != "development":
        return {"error": "Not allowed"}, 403
    
    return {
        "APP_ENV": os.environ.get("APP_ENV"),
        "LOG_LEVEL": os.environ.get("LOG_LEVEL"),
        # 민감한 값은 마스킹
        "DB_PASSWORD": "***" if os.environ.get("DB_PASSWORD") else None
    }
```

![IMAGE: Kudu에서 환경변수 확인]
`📸 캡처: Kudu → Environment에서 환경변수 목록`

---

## Best Practices 체크리스트

### ✅ DO

- [ ] 민감한 값은 Key Vault에 저장
- [ ] 환경별 설정은 Slot Setting으로
- [ ] .env 파일은 .gitignore에 추가
- [ ] 설정 변경은 배치로 한 번에
- [ ] 필수 설정은 앱 시작 시 검증

### ❌ DON'T

- [ ] 코드에 비밀 값 하드코딩
- [ ] .env 파일을 Git에 커밋
- [ ] 프로덕션에서 디버그 엔드포인트 노출
- [ ] 설정 하나씩 따로따로 변경

---

## 정리

Configuration 관리의 핵심:

- **App Settings**: 환경변수로 주입, 변경 시 재시작
- **환경 분리**: .env (로컬) + App Settings (Azure)
- **Slot Settings**: 환경별로 고정되어야 할 설정
- **Key Vault**: 민감한 값은 반드시 여기에

다음 글에서는 **로그와 모니터링** - 앱 상태를 관찰하고 문제를 진단하는 방법을 다룹니다.

---

## 시리즈 목차

1. Azure App Service란? - 플랫폼 아키텍처 이해하기
2. Request Lifecycle: 요청이 앱에 도달하기까지
3. Hosting Models: 어떤 플랜을 선택해야 할까?
4. 첫 번째 배포: 로컬에서 Azure까지 (Python/Flask)
5. **[현재 글] Configuration 마스터하기: App Settings & 환경변수**
6. 로그와 모니터링 기초
7. Scaling 101: 언제 Scale Up vs Scale Out?

---

## 참고 자료

- [Configure an App Service app (Microsoft Learn)](https://learn.microsoft.com/azure/app-service/configure-common)
- [Use Key Vault references (Microsoft Learn)](https://learn.microsoft.com/azure/app-service/app-service-key-vault-references)
- [The Twelve-Factor App - Config](https://12factor.net/config)

---

**태그:** `Azure` `App Service` `Configuration` `Security` `DevOps`
