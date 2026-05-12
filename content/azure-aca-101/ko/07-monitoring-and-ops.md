---
title: 모니터링과 운영 — Log Analytics와 Application Insights
series: azure-aca-101
episode: 7
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
- Log Analytics
- Application Insights
- Observability
- Monitoring
last_reviewed: '2026-04-29'
seo_description: ACA 관측성은 세 개의 독립된 계층으로 나뉩니다.
---

# 모니터링과 운영 — Log Analytics와 Application Insights

운영 사고가 나면 로그가 있는지보다 먼저 어디서 답을 찾아야 하는지가 중요합니다. ACA는 플랫폼 로그, 애플리케이션 추적, 메트릭이 서로 다른 계층에 흩어져 있어서 경계를 모르면 진단 시간이 길어집니다.

이 글은 Azure Container Apps 101 시리즈의 마지막 글입니다. 여기서는 Log Analytics와 Application Insights를 기준으로 운영 가시성의 경계를 정리합니다.

## 핵심 질문

ACA 앱의 운영 가시성을 어떻게 구축해야 사고 시 빠르게 대응할 수 있을까요?

이 글은 그 질문에 답하기 위해 모니터링과 운영의 핵심 결정과 운영 함정을 살펴봅니다.

## 이 글에서 다룰 문제

production에서 ACA 앱이 5xx를 뱉기 시작했다고 가정해 봅시다.
첫 번째 질문: "어느 revision에서 발생했는가?" — Log Analytics의 `RevisionName_s` 컬럼이 답합니다.
두 번째 질문: "어느 dependency에서 막혔는가?" — Application Insights의 distributed trace가 답합니다.
세 번째 질문: "replica가 몇 개까지 늘었는가?" — Azure Monitor metrics가 답합니다.

**ACA가 자동으로 주는 것은 첫 번째 질문의 답까지입니다.** 두 번째와 세 번째는 앱이 직접 계측하거나 Diagnostic Settings를 켜야 합니다.
이 경계를 이해하지 못하면 production incident에서 "왜 trace가 안 보이지?"를 한 시간씩 헤매게 됩니다.

## Mental Model

ACA 관측성은 세 개의 독립된 계층으로 나뉩니다.

1. **Platform layer (Log Analytics)** — ACA가 자동으로 보냅니다. 컨테이너 stdout/stderr와 시스템 이벤트.
2. **Application layer (Application Insights)** — 앱 코드가 SDK 또는 OpenTelemetry로 직접 보냅니다. distributed trace, custom metrics, dependency map.
3. **Sidecar layer (Dapr telemetry)** — Dapr를 쓸 때만 의미가 있습니다. `--dapr-connection-string`은 이 계층 전용이지 일반 앱 추적이 아닙니다.

세 계층은 같은 Application Insights 인스턴스로 합쳐서 볼 수도 있고 분리할 수도 있습니다.
중요한 건 "이 신호가 어느 계층에서 오는가?"를 항상 의식하는 것입니다.

![로그와 추적이 모이는 관측 경로](../../../assets/azure-aca-101/07/07-01-the-observability-map.ko.png)

*로그와 추적이 모이는 관측 경로*

## 핵심 개념

### 1. 두 종류의 platform log

| 테이블 | 내용 | 주 사용처 |
| --- | --- | --- |
| `ContainerAppConsoleLogs_CL` | 컨테이너의 stdout/stderr | 앱 동작, 비즈니스 로그 추적 |
| `ContainerAppSystemLogs_CL` | ACA 플랫폼 이벤트 (scaling, revision change, probe failure 등) | 플랫폼 의사결정 추적 |

`_CL` 접미사는 "Custom Log"의 약자입니다. 두 테이블 모두 Log Analytics workspace에 저장되며 KQL로 조회합니다.

### 2. Revision은 가장 강력한 grouping key

ACA는 모든 로그에 `RevisionName_s` 컬럼을 자동으로 채웁니다.
production incident가 발생하면 첫 쿼리는 거의 항상 "어느 revision에서 에러가 늘었는가"입니다.

### 3. Application Insights connection의 두 경로

- **앱 직접 계측** — `APPLICATIONINSIGHTS_CONNECTION_STRING` 환경변수로 connection string을 주고, OpenTelemetry SDK로 export.
- **Dapr telemetry** — `az containerapp env update --dapr-instrumentation-key`로 사이드카가 보내는 텔레메트리. 앱 코드 추적과는 별개.

## Before-After

### Before (관측 없이 운영)

```bash
az containerapp create \
  --name fastapi-aca-demo --resource-group $RG --environment $ACA_ENV \
  --image $IMAGE --ingress external --target-port 8000
```

incident 발생 시:
- "어디서 5xx가 나는지 모름" → SSH도 안 되는 ACA에서 디버깅 불가능.
- 컨테이너 재시작되면 stdout 로그도 사라짐.

### After (Log Analytics + App Insights 연결)

```bash
# 1. Environment 만들 때 Log Analytics workspace 연결
az containerapp env create \
  --name $ACA_ENV --resource-group $RG --location koreacentral \
  --logs-workspace-id $LOG_WORKSPACE_ID \
  --logs-workspace-key $LOG_WORKSPACE_KEY

# 2. 앱에 App Insights connection string 주입
az containerapp create \
  --name fastapi-aca-demo --resource-group $RG --environment $ACA_ENV \
  --image $IMAGE --ingress external --target-port 8000 \
  --env-vars "APPLICATIONINSIGHTS_CONNECTION_STRING=$AI_CONN"
```

incident 발생 시:
- KQL 한 줄로 revision 단위 에러 추적.
- App Insights에서 trace, dependency, exception 자동 수집.

## 단계별 실습

### Step 1: Log Analytics workspace 만들기

```bash
RG=rg-aca-demo
LOG_WS=aca-logs

az monitor log-analytics workspace create \
  --resource-group $RG --workspace-name $LOG_WS

LOG_WORKSPACE_ID=$(az monitor log-analytics workspace show \
  --resource-group $RG --workspace-name $LOG_WS \
  --query customerId -o tsv)

LOG_WORKSPACE_KEY=$(az monitor log-analytics workspace get-shared-keys \
  --resource-group $RG --workspace-name $LOG_WS \
  --query primarySharedKey -o tsv)
```

### Step 2: ACA Environment에 연결

```bash
az containerapp env create \
  --name aca-env-demo --resource-group $RG --location koreacentral \
  --logs-workspace-id $LOG_WORKSPACE_ID \
  --logs-workspace-key $LOG_WORKSPACE_KEY
```

### Step 3: KQL로 로그 조회

Azure Portal → Log Analytics workspace → Logs 에서:

```kusto
// 최근 100건의 console 로그
ContainerAppConsoleLogs_CL
| where ContainerAppName_s == "fastapi-aca-demo"
| project Time=TimeGenerated, Revision=RevisionName_s, Message=Log_s
| top 100 by Time desc

// Revision별 에러 카운트
ContainerAppConsoleLogs_CL
| where ContainerAppName_s == "fastapi-aca-demo"
| where Log_s contains "ERROR"
| summarize ErrorCount=count() by RevisionName_s
| order by ErrorCount desc

// Scaling 이벤트
ContainerAppSystemLogs_CL
| where ContainerAppName_s == "fastapi-aca-demo"
| where Log_s contains "Scal"
| project Time=TimeGenerated, Message=Log_s
| top 50 by Time desc
```

### Step 4: Application Insights 연결 (FastAPI)

```bash
AI_NAME=aca-appinsights
az monitor app-insights component create \
  --app $AI_NAME --location koreacentral --resource-group $RG \
  --workspace $LOG_WORKSPACE_ID

AI_CONN=$(az monitor app-insights component show \
  --app $AI_NAME --resource-group $RG --query connectionString -o tsv)

az containerapp update \
  --name fastapi-aca-demo --resource-group $RG \
  --set-env-vars "APPLICATIONINSIGHTS_CONNECTION_STRING=$AI_CONN"
```

FastAPI 앱 코드:

```python
from azure.monitor.opentelemetry import configure_azure_monitor
from fastapi import FastAPI

configure_azure_monitor()  # APPLICATIONINSIGHTS_CONNECTION_STRING 자동 인식
app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok"}
```

`requirements.txt`에 `azure-monitor-opentelemetry`를 추가하면 trace, request, dependency가 자동 수집됩니다.

## 자주 하는 실수

- **Environment 만든 뒤 Log Analytics 연결을 잊음** — 로그가 ACA portal blade에서만 보이고 KQL로 조회 불가.
- **App Insights connection string을 secret이 아닌 env-var로만 관리** — 운영 환경에서는 `--secrets`로 보호하는 편이 안전합니다.
- **Application Insights를 켜면 trace가 자동 수집된다고 오해** — connection string 주입만으로는 부족합니다. 앱이 OpenTelemetry SDK로 export해야 합니다.
- **Dapr telemetry와 앱 telemetry를 혼동** — `--dapr-instrumentation-key`는 사이드카 전용이지 앱 추적 설정이 아닙니다.
- **Log retention을 기본값으로 둠** — Log Analytics 기본 retention은 30일입니다. 컴플라이언스 요구가 있으면 늘려야 합니다.

## 실무에서

production checklist:

- **Diagnostic Settings 활성화** — Log Analytics + Storage Account(장기 보관) 둘 다 연결.
- **Alert rule 구성** — KQL 기반 alert로 "특정 revision에서 5xx 비율 5% 초과" 같은 조건을 트리거.
- **Workbook 만들기** — Revision별 latency, error rate, replica count를 한 화면에 정리.
- **Cost 관리** — Application Insights는 ingestion 양으로 과금됩니다. sampling rate 조정 필수.
- **OpenTelemetry 표준** — Azure Monitor 전용 SDK보다 OTel SDK + Azure Monitor exporter가 vendor lock-in을 줄입니다.

## 실무에서는 이렇게 생각한다

관측성 도구를 도입할 때 가장 위험한 함정은 "모든 것을 수집하면 문제가 보일 것"이라는 망상입니다. 실제로는 수집하는 데이터가 많을수록 노이즈도 많아집니다. 초기에는 세 가지만 보는 것이 효과적입니다. 에러율(5xx), 응답 시간(p95), 컨테이너 재시작 횟수. 이 세 가지가 정상이면 대부분의 운영 문제는 감지할 수 있습니다.

Alert fatigue는 모니터링의 가장 큰 적입니다. 경고가 하루에 50건씩 오면 팀은 전부 무시하게 됩니다. 실무에서는 "이 경고가 올 때 누가 무엇을 해야 하는가"를 답할 수 없는 경고는 만들지 않는 것이 원칙입니다. action item이 없는 경고는 대시보드 차트로 내리고, 경고는 즉시 대응이 필요한 항목만 남겼습니다.

Log Analytics 비용은 예상보다 빠르게 늘어납니다. 특히 모든 컨테이너의 stdout를 수집하면 GB 단위 비용이 발생합니다. 프로덕션에서는 로그 레벨을 WARNING 이상으로 올리고, DEBUG 로그는 샘플링하거나 아예 끄는 것이 일반적입니다. 분석이 필요한 때만 일시적으로 레벨을 내리는 운영 패턴을 미리 마련해두는 것이 좋습니다.

## 체크리스트

- [ ] ACA Environment에 Log Analytics workspace가 연결되어 있는가?
- [ ] `ContainerAppConsoleLogs_CL`과 `ContainerAppSystemLogs_CL` 모두 데이터가 들어오고 있는가?
- [ ] Application Insights connection string이 secret으로 관리되고 있는가?
- [ ] FastAPI 앱이 OpenTelemetry로 trace를 export하는가?
- [ ] Revision 단위로 에러를 grouping하는 KQL alert이 구성되어 있는가?
- [ ] Log retention 기간이 컴플라이언스 요구에 맞는가?

## 정리·다음 글

이번 글의 핵심:

- ACA 관측성은 platform / application / sidecar 세 계층으로 나뉩니다.
- Log Analytics는 `_CL` 테이블로 console과 system 로그를 자동 저장합니다.
- Application Insights는 앱이 직접 OpenTelemetry로 export해야 의미가 생깁니다.
- Revision은 가장 강력한 incident grouping key입니다.

이로써 **Azure Container Apps 101 시리즈 7편이 모두 끝났습니다.**
지금까지 ACA의 개념(1편), 구조(2편), 첫 배포(3편), 트래픽 분할(4편), 스케일링(5편), Dapr 통합(6편), 그리고 이번 7편의 관측성을 다뤘습니다.

다음 단계로는 동일한 접근을 **Azure App Service 101**, **Azure AKS 101**, **Azure Functions 101**에서 비교하며 학습하실 수 있습니다.
서버리스 컨테이너 플랫폼 선택의 trade-off를 이해하는 데 도움이 됩니다.

---

<!-- toc:begin -->
## 시리즈 목차

- [Azure Container Apps란? — Kubernetes 없이 컨테이너 운영하기](./01-what-is-aca.md)
- [Environment·Container App·Revision — 세 단어로 보는 ACA](./02-environment-app-revision.md)
- [첫 앱 배포하기 — Python/FastAPI](./03-first-deploy.md)
- [Ingress와 트래픽 분할 — Revision 기반 배포 전략](./04-ingress-and-traffic-split.md)
- [스케일링 — KEDA scaler와 0-to-N](./05-scaling-with-keda.md)
- [Dapr 통합 — 사이드카로 얻는 것](./06-dapr-integration.md)
- **모니터링과 운영 — Log Analytics와 Application Insights (현재 글)**

<!-- toc:end -->

---

## 참고 자료

### 공식 문서
- [Monitor logs in Azure Container Apps with Log Analytics — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/log-monitoring)
- [Observability in Azure Container Apps — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/observability)
- [Azure Monitor Application Insights overview — Microsoft Learn](https://learn.microsoft.com/en-us/azure/azure-monitor/app/app-insights-overview)
- [Azure Container Apps environments — Microsoft Learn](https://learn.microsoft.com/en-us/azure/container-apps/environment)
- [Azure Monitor OpenTelemetry distro for Python](https://learn.microsoft.com/en-us/azure/azure-monitor/app/opentelemetry-enable?tabs=python)

### 관련 시리즈
- [Azure App Service 101](../../azure-app-service-101/ko/01-what-is-app-service.md)
- [Azure AKS 101](../../azure-aks-101/ko/01-what-is-aks.md)
- [Azure Functions 101](../../azure-functions-101/ko/01-what-is-azure-functions.md)

Tags: Azure, Container Apps, Serverless, Containers
