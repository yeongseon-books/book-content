---
title: 모니터링과 운영 — Log Analytics와 Application Insights
series: azure-aca-101
episode: 7
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- Azure
- Container Apps
- Log Analytics
- Application Insights
- Observability
- Monitoring
last_reviewed: '2026-05-12'
seo_description: ACA 관측성은 플랫폼, 애플리케이션, 사이드카라는 세 계층으로 나뉩니다.
---

# 모니터링과 운영 — Log Analytics와 Application Insights

운영 사고에서 어려운 지점은 데이터가 있느냐보다, 어느 계층이 답을 가지고 있느냐를 아는 일입니다. ACA는 로그, 트레이스, 메트릭을 서로 다른 시스템에 나눠 두고, 그 경계를 이해하느냐가 프로덕션 문제를 얼마나 빨리 진단하는지를 좌우합니다.

이 글은 Azure Container Apps 101 시리즈의 마지막 글입니다. 여기서는 Log Analytics와 Application Insights를 중심으로 그 계층을 지도처럼 정리하겠습니다.

## 이 글에서 다룰 문제

- ACA 관측성은 어떤 계층 구조로 나뉠까요?
- `ContainerAppConsoleLogs_CL`와 `ContainerAppSystemLogs_CL`는 무엇이 다를까요?
- Log Analytics에서 Revision 기준으로 로그를 묶는 KQL 쿼리는 어떻게 작성할까요?
- OpenTelemetry를 통해 FastAPI 앱을 Application Insights에 연결하는 가장 짧은 경로는 무엇일까요?

## 이 글이 답할 질문

- ACA 관측성은 어떤 세 계층으로 나뉘고, 각 계층은 무엇을 책임질까요?
- `ContainerAppConsoleLogs_CL`는 무엇을 담고, `ContainerAppSystemLogs_CL`는 무엇을 담을까요?
- Log Analytics에서 Revision 기준으로 로그를 묶는 KQL은 어떻게 쓸까요?
- OpenTelemetry를 통해 FastAPI 앱을 Application Insights에 연결하는 가장 짧은 경로는 무엇일까요?
- ACA가 기본으로 주는 관측성과, 앱이 직접 계측해야 하는 관측성의 경계는 어디일까요?

## 왜 이 글이 중요한가

프로덕션 ACA 앱이 5xx를 뿜기 시작했다고 가정해 보겠습니다.
첫 번째 질문은 "어느 revision에서 생겼지?"입니다. 이 답은 Log Analytics의 `RevisionName_s`가 줍니다.
두 번째 질문은 "어느 dependency가 느려졌지?"입니다. 이 답은 Application Insights의 분산 트레이스가 줍니다.
세 번째 질문은 "replica가 몇 개까지 늘었지?"입니다. 이 답은 Azure Monitor 메트릭이 줍니다.

**ACA가 첫 번째 질문의 답은 기본으로 제공합니다.** 두 번째와 세 번째는 앱 계측이나 명시적인 Diagnostic Settings가 있어야 얻을 수 있습니다.
이 경계를 놓치면 사고 중에 "왜 trace가 안 보이지?"를 한 시간씩 묻게 됩니다.

## 멘탈 모델

ACA 관측성은 세 개의 독립된 계층으로 나뉩니다.

1. **Platform layer (Log Analytics)** — ACA가 자동으로 내보냅니다. 컨테이너 stdout/stderr와 시스템 이벤트입니다.
2. **Application layer (Application Insights)** — SDK나 OpenTelemetry를 통해 앱 코드가 직접 내보냅니다. 분산 트레이스, custom metrics, dependency map이 여기에 있습니다.
3. **Sidecar layer (Dapr telemetry)** — Dapr를 쓸 때만 의미가 있습니다. `--dapr-connection-string`은 일반 앱 트레이싱이 아니라 이 계층 설정입니다.

세 계층은 같은 Application Insights 인스턴스로 모일 수도 있고 따로 남을 수도 있습니다.
중요한 규율은 항상 "이 신호는 어느 계층에서 왔는가?"를 아는 것입니다.

> 관측성에서 가장 먼저 할 일은 데이터를 더 모으는 것이 아니라, 지금 보고 있는 신호가 플랫폼 로그인지, 앱 트레이스인지, 사이드카 텔레메트리인지 먼저 구분하는 일입니다.

![Where logs and traces converge](https://yeongseon-books.github.io/book-public-assets/assets/azure-aca-101/07/07-01-the-observability-map.ko.png)

*Where logs and traces converge*

## 핵심 개념

### 1. 두 개의 플랫폼 로그 테이블

| Table | 내용 | 주된 용도 |
| --- | --- | --- |
| `ContainerAppConsoleLogs_CL` | 컨테이너 stdout/stderr | 앱 동작, 비즈니스 로그 추적 |
| `ContainerAppSystemLogs_CL` | ACA 플랫폼 이벤트(스케일링, revision 변경, probe 실패 등) | 플랫폼 결정 추적 |

`_CL` 접미사는 "Custom Log"를 뜻합니다. 두 테이블은 모두 Log Analytics workspace에 들어가고, KQL로 조회합니다.

### 2. Revision이 가장 강한 그룹 키

ACA는 모든 로그 행에 `RevisionName_s`를 채워 줍니다.
사고가 났을 때 첫 쿼리는 거의 항상 "어느 revision에서 에러가 치솟았는가?"입니다.

### 3. Application Insights로 가는 두 경로

- **App-level instrumentation** — `APPLICATIONINSIGHTS_CONNECTION_STRING`을 주입하고 OpenTelemetry SDK로 export합니다.
- **Dapr telemetry** — `az containerapp env update --dapr-instrumentation-key`를 설정해 사이드카가 자체 telemetry를 내보내게 합니다. 앱 코드 트레이스와는 독립적입니다.

## Before / After

### Before (관측성이 없는 경우)

```bash
az containerapp create \
  --name fastapi-aca-demo --resource-group $RG --environment $ACA_ENV \
  --image $IMAGE --ingress external --target-port 8000
```

사고가 나면:
- "5xx가 어디서 나는 거지?" → SSH도 없고 디버깅도 어렵습니다
- 컨테이너 재시작이 한 번만 일어나도 stdout 기록이 사라집니다

### After (Log Analytics + App Insights를 연결한 경우)

```bash
# 1. Connect a Log Analytics workspace when creating the Environment
az containerapp env create \
  --name $ACA_ENV --resource-group $RG --location koreacentral \
  --logs-workspace-id $LOG_WORKSPACE_ID \
  --logs-workspace-key $LOG_WORKSPACE_KEY

# 2. Inject the App Insights connection string
az containerapp create \
  --name fastapi-aca-demo --resource-group $RG --environment $ACA_ENV \
  --image $IMAGE --ingress external --target-port 8000 \
  --env-vars "APPLICATIONINSIGHTS_CONNECTION_STRING=$AI_CONN"
```

사고가 나면:
- KQL 한 줄로 revision별 에러 수를 볼 수 있습니다
- App Insights가 trace, dependency, exception을 자동 수집합니다

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

### Step 2: ACA Environment에 연결하기

```bash
az containerapp env create \
  --name aca-env-demo --resource-group $RG --location koreacentral \
  --logs-workspace-id $LOG_WORKSPACE_ID \
  --logs-workspace-key $LOG_WORKSPACE_KEY
```

### Step 3: KQL로 조회하기

Azure Portal → Log Analytics workspace → Logs에서 아래를 실행합니다.

```kusto
// Most recent 100 console logs
ContainerAppConsoleLogs_CL
| where ContainerAppName_s == "fastapi-aca-demo"
| project Time=TimeGenerated, Revision=RevisionName_s, Message=Log_s
| top 100 by Time desc

// Errors per revision
ContainerAppConsoleLogs_CL
| where ContainerAppName_s == "fastapi-aca-demo"
| where Log_s contains "ERROR"
| summarize ErrorCount=count() by RevisionName_s
| order by ErrorCount desc

// Scaling events
ContainerAppSystemLogs_CL
| where ContainerAppName_s == "fastapi-aca-demo"
| where Log_s contains "Scal"
| project Time=TimeGenerated, Message=Log_s
| top 50 by Time desc
```

### Step 4: Application Insights 연결하기(FastAPI)

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

FastAPI 앱 코드는 다음과 같습니다.

```python
from azure.monitor.opentelemetry import configure_azure_monitor
from fastapi import FastAPI

configure_azure_monitor()  # Auto-detects APPLICATIONINSIGHTS_CONNECTION_STRING
app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok"}
```

`requirements.txt`에 `azure-monitor-opentelemetry`를 추가하면 trace, request, dependency가 자동 수집됩니다.

## 자주 하는 실수

- **Environment에 Log Analytics를 연결하지 않는 것** — 로그가 ACA 포털 블레이드에는 보여도 KQL에서는 바로 보이지 않습니다.
- **App Insights connection string을 평문 env-var로 두는 것** — 프로덕션에서는 `--secrets`로 보호해야 합니다.
- **App Insights가 trace를 자동 수집한다고 생각하는 것** — connection string만 주입해서는 충분하지 않습니다. 앱이 OpenTelemetry SDK로 export해야 합니다.
- **Dapr telemetry와 앱 telemetry를 혼동하는 것** — `--dapr-instrumentation-key`는 사이드카 전용입니다.
- **로그 보존 기간을 기본값으로 방치하는 것** — Log Analytics 기본 보존 기간은 30일입니다. 규정상 더 길어야 할 수 있습니다.

## 프로덕션에서는 이렇게 본다

프로덕션 체크리스트는 대개 아래와 같습니다.

- Diagnostic Settings 활성화 — Log Analytics와 Storage Account를 함께 연결해 장기 보존을 확보합니다.
- 알림 규칙 구성 — 예: "특정 revision의 5xx 비율 > 5%" 같은 KQL 기반 알림.
- Workbook 구성 — revision별 지연 시간, 에러율, replica 수를 한 화면에 모읍니다.
- 비용 관리 — App Insights는 수집량 기준 과금이므로 sampling 비율을 조정합니다.
- OpenTelemetry 표준화 — OTel SDK + Azure Monitor exporter 조합이 벤더 종속 SDK보다 이식성이 좋습니다.

## 체크리스트

- [ ] ACA Environment가 Log Analytics workspace에 연결돼 있습니까?
- [ ] `ContainerAppConsoleLogs_CL`와 `ContainerAppSystemLogs_CL` 모두 데이터가 들어오고 있습니까?
- [ ] App Insights connection string을 secret으로 관리하고 있습니까?
- [ ] FastAPI 앱이 OpenTelemetry로 trace를 export하고 있습니까?
- [ ] revision 기준으로 에러를 묶는 KQL 알림이 있습니까?
- [ ] 로그 보존 기간이 규정 요구사항과 맞습니까?

## 연습 문제

1. 새 revision 배포 직후 5xx 비율이 급증했습니다. 이전 revision과 현재 revision의 에러율을 비교하는 KQL을 직접 작성해 보세요.
2. App Insights connection string을 평문 env-var로 노출하는 것과 secret으로 주입하는 것의 차이는 무엇일까요?
3. 평범한 FastAPI 앱(Dapr 없음)이라면 `--dapr-instrumentation-key`를 설정해야 할까요? 왜 그럴까요?

## 정리

- ACA 관측성은 platform / application / sidecar 세 계층으로 나뉩니다.
- Log Analytics는 `_CL` 테이블에 console log와 system log를 자동으로 수집합니다.
- Application Insights는 앱이 OpenTelemetry로 export할 때 비로소 의미가 생깁니다.
- 사고 초기 대응에서는 Revision이 가장 강한 그룹 키입니다.

이것으로 **Azure Container Apps 101 시리즈 7편**을 모두 마칩니다.
1화에서는 개념을, 2화에서는 구조를, 3화에서는 첫 배포를, 4화에서는 트래픽 분할을, 5화에서는 스케일링을, 6화에서는 Dapr 통합을, 그리고 이번 글에서는 관측성을 정리했습니다.

다음 단계로는 **Azure App Service 101**, **Azure AKS 101**, **Azure Functions 101**과 같은 방식으로 비교해 보면서 서버리스 컨테이너 플랫폼의 트레이드오프를 입체적으로 보는 것이 좋습니다.

---

<!-- toc:begin -->
## 시리즈 목차

- [Azure Container Apps란? — Kubernetes 없이 컨테이너 운영하기](./01-what-is-aca.md)
- [Environment, Container App, Revision — ACA in three words](./02-environment-app-revision.md)
- [첫 배포하기 — Python/FastAPI](./03-first-deploy.md)
- [Ingress와 트래픽 분할 — revision 기반 배포 전략](./04-ingress-and-traffic-split.md)
- [스케일링 — KEDA scaler와 zero-to-N](./05-scaling-with-keda.md)
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
