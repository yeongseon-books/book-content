# 로그와 모니터링 기초

> Azure App Service 101 시리즈 (6/7)

"앱이 느려요." "에러가 났대요." "언제부터 이랬죠?"

이런 질문에 답하려면 **로그와 모니터링**이 필수입니다. 이 글에서는 App Service에서 로그를 수집하고 분석하는 방법을 알아봅니다.

---

## 로그가 어디로 가는가?

App Service에서 로그의 흐름을 이해하는 것이 첫 번째입니다.

```
Flask App (logger.info) → stdout/stderr → App Service Runtime
                                              ↓
                           ┌─────────────────┴─────────────────┐
                           ↓                                   ↓
                    /home/LogFiles                    Application Insights
                    (파일 시스템)                         (장기 분석)
```

| 목적지 | 보존 기간 | 용도 |
|--------|----------|------|
| `/home/LogFiles/*_docker.log` | ~35MB 롤링 | 컨테이너 크래시, 시작 에러 |
| `/home/LogFiles/Application/` | 최대 100MB/7일 | 단기 로그 아카이브 |
| Application Insights | 90일 기본 | 장기 분석, 알람, KQL |

![IMAGE: 로그 흐름 다이어그램]
`📸 캡처: 로그 흐름도 (draw.io로 그리기)`

---

## Step 1: 파일시스템 로깅 활성화

기본적으로 stdout/stderr는 파일시스템에 저장됩니다.

### 로깅 설정

```bash
az webapp log config \
    --resource-group $RG \
    --name $APP_NAME \
    --application-logging filesystem \
    --level verbose \
    --web-server-logging filesystem
```

### 설정 확인

```bash
az webapp log config show \
    --resource-group $RG \
    --name $APP_NAME \
    --output json
```

**출력 예시:**
```json
{
  "applicationLogs": {
    "fileSystem": {
      "level": "Verbose"
    }
  },
  "httpLogs": {
    "fileSystem": {
      "enabled": true,
      "retentionInDays": 7,
      "retentionInMb": 100
    }
  }
}
```

![IMAGE: Log config 설정 화면]
`📸 캡처: Azure Portal → App Service → App Service logs`

---

## Step 2: 실시간 로그 스트림

배포 직후나 문제 발생 시 **실시간 로그**가 유용합니다.

### CLI로 스트림

```bash
az webapp log tail \
    --resource-group $RG \
    --name $APP_NAME
```

요청을 보내면 로그가 바로 표시됩니다:

```
2025-04-07T10:30:15.123Z {"level": "info", "message": "Request processed", "userId": "user-123"}
2025-04-07T10:30:15.456Z {"level": "error", "message": "Database connection failed", "error": "timeout"}
```

### JSON 로그만 필터링

```bash
az webapp log tail \
    --resource-group $RG \
    --name $APP_NAME \
    | grep --line-buffered '"level"'
```

![IMAGE: Log tail 실행 화면]
`📸 캡처: 터미널에서 az webapp log tail 실행 중`

---

## Step 3: 구조화된 로깅 (JSON)

문자열 로그보다 **JSON 로그**가 분석에 훨씬 유리합니다.

### Python 설정

```python
import logging
import json
from datetime import datetime

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname.lower(),
            "message": record.getMessage(),
            "logger": record.name,
        }
        # 추가 필드 병합
        if hasattr(record, "custom_dimensions"):
            log_obj.update(record.custom_dimensions)
        return json.dumps(log_obj)

# 핸들러 설정
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())

logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

### 사용 예시

```python
logger.info("Order created", extra={"custom_dimensions": {
    "orderId": "ORD-12345",
    "userId": "user-789",
    "totalAmount": 150.00
}})
```

**출력:**
```json
{"timestamp": "2025-04-07T10:30:15.123Z", "level": "info", "message": "Order created", "orderId": "ORD-12345", "userId": "user-789", "totalAmount": 150.0}
```

![IMAGE: 구조화된 JSON 로그 예시]
`📸 캡처: Log stream에서 JSON 형식 로그 출력`

---

## Step 4: Correlation ID로 요청 추적

하나의 요청에서 발생한 모든 로그를 연결하려면 **Correlation ID**가 필요합니다.

### Middleware 구현

```python
import uuid
from flask import Flask, request, g

app = Flask(__name__)

@app.before_request
def set_correlation_id():
    # 헤더에서 가져오거나 새로 생성
    g.correlation_id = request.headers.get(
        "X-Correlation-ID", 
        str(uuid.uuid4())
    )

@app.after_request
def add_correlation_header(response):
    response.headers["X-Correlation-ID"] = g.correlation_id
    return response
```

### 로깅에 자동 포함

```python
class CorrelationFilter(logging.Filter):
    def filter(self, record):
        record.correlation_id = getattr(g, 'correlation_id', 'N/A')
        return True

logger.addFilter(CorrelationFilter())
```

### 활용

사용자가 에러를 신고하면 `X-Correlation-ID` 헤더 값을 요청해서 해당 요청의 모든 로그를 조회할 수 있습니다.

```bash
# 특정 Correlation ID로 로그 필터링
az webapp log tail --resource-group $RG --name $APP_NAME \
    | grep --line-buffered "a1b2c3d4"
```

---

## Step 5: Application Insights 연동

장기 분석과 알람을 위해 **Application Insights**를 설정합니다.

### Application Insights 생성

```bash
az monitor app-insights component create \
    --resource-group $RG \
    --app $APP_NAME-insights \
    --location $LOCATION \
    --kind web
```

### Connection String 가져오기

```bash
APPINSIGHTS_CS=$(az monitor app-insights component show \
    --resource-group $RG \
    --app $APP_NAME-insights \
    --query connectionString \
    --output tsv)
```

### App Settings에 추가

```bash
az webapp config appsettings set \
    --resource-group $RG \
    --name $APP_NAME \
    --settings APPLICATIONINSIGHTS_CONNECTION_STRING=$APPINSIGHTS_CS
```

### Python SDK 설치

```bash
pip install azure-monitor-opentelemetry
```

### 앱에서 초기화

```python
from azure.monitor.opentelemetry import configure_azure_monitor
import os

if os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING"):
    configure_azure_monitor(
        connection_string=os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
    )
```

![IMAGE: Application Insights 개요 화면]
`📸 캡처: Azure Portal → Application Insights → Overview`

---

## Step 6: KQL로 로그 분석

Application Insights에 저장된 로그는 **KQL(Kusto Query Language)**로 분석합니다.

### 최근 에러 조회

```kql
AppTraces
| where TimeGenerated > ago(1h)
| where SeverityLevel == 3  // Error
| project TimeGenerated, Message, Properties
| order by TimeGenerated desc
| take 20
```

### 에러율 시계열

```kql
AppRequests
| where TimeGenerated > ago(6h)
| summarize 
    total = count(),
    failed = countif(Success == false)
  by bin(TimeGenerated, 5m)
| extend errorRate = (failed * 100.0) / total
| render timechart
```

### 느린 요청 Top 10

```kql
AppRequests
| where TimeGenerated > ago(1h)
| top 10 by DurationMs desc
| project TimeGenerated, Name, DurationMs, ResultCode
```

### Correlation ID로 추적

```kql
AppTraces
| where TimeGenerated > ago(24h)
| extend correlationId = tostring(Properties["correlationId"])
| where correlationId == "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
| project TimeGenerated, SeverityLevel, Message
| order by TimeGenerated asc
```

![IMAGE: Application Insights Logs 화면]
`📸 캡처: Azure Portal → Application Insights → Logs → KQL 쿼리 실행`

---

## Step 7: 알람 설정

문제가 발생하면 자동으로 알림을 받도록 설정합니다.

### 에러율 알람

```bash
az monitor metrics alert create \
    --resource-group $RG \
    --name "High Error Rate" \
    --scopes "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RG/providers/Microsoft.Web/sites/$APP_NAME" \
    --condition "avg Http5xx > 10" \
    --window-size 5m \
    --evaluation-frequency 1m
```

### Azure Portal에서 설정

1. App Service → Alerts → + Create alert rule
2. 조건: HTTP 5xx > 10
3. 액션 그룹: 이메일/SMS/웹훅

![IMAGE: Alert rule 설정 화면]
`📸 캡처: Azure Portal → Alerts → Create alert rule`

---

## 파일시스템에서 로그 확인

### Kudu로 접근

```
https://<app-name>.scm.azurewebsites.net
```

**경로:**
```
/home/LogFiles/
├── <hostname>_docker.log       ← 컨테이너 stdout
├── Application/
│   └── <date>_<hostname>_default_docker.log
└── kudu/
    └── deployment/             ← 배포 로그
```

### SSH로 접근

```bash
az webapp ssh --resource-group $RG --name $APP_NAME

# 컨테이너 내부에서
tail -f /home/LogFiles/*_docker.log
```

### 로그 다운로드

```bash
az webapp log download \
    --resource-group $RG \
    --name $APP_NAME \
    --log-file ./logs.zip

unzip logs.zip -d ./logs
```

![IMAGE: Kudu 파일 브라우저에서 LogFiles]
`📸 캡처: Kudu → Debug console → /home/LogFiles`

---

## 로그 레벨 관리

### 레벨별 용도

| 레벨 | 용도 | 프로덕션 권장 |
|------|------|-------------|
| DEBUG | 상세 디버깅 | ❌ |
| INFO | 정상 운영 정보 | ✅ |
| WARNING | 잠재적 문제 | ✅ |
| ERROR | 에러 발생 | ✅ |
| CRITICAL | 심각한 장애 | ✅ |

### 동적 레벨 변경

```bash
# 장애 조사 시 DEBUG 활성화
az webapp config appsettings set \
    --resource-group $RG \
    --name $APP_NAME \
    --settings LOG_LEVEL=DEBUG

# 조사 완료 후 원복
az webapp config appsettings set \
    --resource-group $RG \
    --name $APP_NAME \
    --settings LOG_LEVEL=INFO
```

> ⚠️ DEBUG 레벨은 **비용 증가**와 **민감 정보 노출** 위험이 있으므로 조사 후 반드시 원복하세요.

---

## 트러블슈팅 시나리오

### "로그가 안 보여요"

1. 로깅 활성화 확인: `az webapp log config show`
2. 앱이 stdout에 출력하는지 확인
3. Log stream 활성화 후 요청 발생시키기

### "Application Insights에 데이터가 없어요"

1. `APPLICATIONINSIGHTS_CONNECTION_STRING` 설정 확인
2. SDK 초기화 코드 확인
3. 2-3분 대기 (데이터 수집 지연)

### "특정 에러만 찾고 싶어요"

```kql
// Correlation ID로 추적
AppTraces
| where Properties contains "correlation-id-here"

// 특정 시간대 에러
AppTraces
| where TimeGenerated between(datetime(2025-04-07 10:00)..datetime(2025-04-07 11:00))
| where SeverityLevel >= 3
```

---

## 정리

로그와 모니터링의 핵심:

- **파일시스템 로그**: 즉각적인 디버깅
- **구조화된 JSON 로그**: 분석 용이성
- **Correlation ID**: 요청 단위 추적
- **Application Insights**: 장기 분석과 알람
- **KQL**: 강력한 쿼리 언어

다음 마지막 글에서는 **Scaling 101** - 언제 Scale Up하고 언제 Scale Out할지 알아봅니다.

---

## 시리즈 목차

1. Azure App Service란? - 플랫폼 아키텍처 이해하기
2. Request Lifecycle: 요청이 앱에 도달하기까지
3. Hosting Models: 어떤 플랜을 선택해야 할까?
4. 첫 번째 배포: 로컬에서 Azure까지 (Python/Flask)
5. Configuration 마스터하기: App Settings & 환경변수
6. **[현재 글] 로그와 모니터링 기초**
7. Scaling 101: 언제 Scale Up vs Scale Out?

---

## 참고 자료

- [Enable diagnostics logging (Microsoft Learn)](https://learn.microsoft.com/azure/app-service/troubleshoot-diagnostic-logs)
- [Application Insights for Python (Microsoft Learn)](https://learn.microsoft.com/azure/azure-monitor/app/opencensus-python)
- [KQL Quick Reference](https://learn.microsoft.com/azure/data-explorer/kql-quick-reference)

---

**태그:** `Azure` `App Service` `Monitoring` `Logging` `Application Insights` `DevOps`
