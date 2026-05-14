---
title: Logging and Monitoring Basics
series: azure-app-service-101
episode: 6
language: en
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
last_reviewed: '2026-04-29'
seo_description: Master Azure App Service logging and monitoring. Learn to collect filesystem logs, use Application Insights, and write KQL queries for debugging.
---

# Logging and Monitoring Basics

"The app is slow." "There's an error." "When did this start?"

To answer these questions, **logging and monitoring** are essential. In this post, we'll explore how to collect and analyze logs in App Service.

This is the sixth post in the Azure App Service 101 series. It shows how to turn App Service from a black box into a system you can observe, query, and debug under pressure.

---

## Questions this chapter answers

- Where do App Service diagnostic logs (HTTP, application, container) actually land?
- How do Application Insights, Log Analytics, and Diagnostic Settings split responsibilities?
- When does live tail or log streaming help, and where does it hit its limits?
- What thresholds make memory, HTTP 5xx, and response-time alerts useful?
- Which signals warn you about disk-quota or dependency failures first?

## Where Do Logs Go?

Understanding the log flow in App Service is the first step.

![App logs flowing to files and monitoring](../../../assets/azure-app-service-101/06/01-log-flow-architecture.en.png)

*App logs flowing to files and monitoring*

```text
Flask App (logger.info) → stdout/stderr → App Service Runtime
 ↓
 ┌─────────────────┴─────────────────┐
 ↓ ↓
 /home/LogFiles Application Insights
 (Filesystem) (Long-term analysis)
```

| Destination | Retention | Purpose |
|-------------|-----------|---------|
| `/home/LogFiles/*_docker.log` | ~35MB rolling | Container crashes, startup errors |
| `/home/LogFiles/Application/` | Max 100MB/7 days | Short-term log archive |
| Application Insights | 90 days default | Long-term analysis, alerts, KQL |

![Observability stages from logs to tracing](../../../assets/azure-app-service-101/06/02-observability-maturity.en.png)

*Observability stages from logs to tracing*

---

## Step 1: Enable Filesystem Logging

App Service writes application stdout/stderr to `/home/LogFiles/` only after you enable filesystem logging. Until then, the application log pipeline is off and `az webapp log tail` has nothing to stream from application logs.

### Configure Logging

```bash
az webapp log config \
 --resource-group $RG \
 --name $APP_NAME \
 --application-logging filesystem \
 --level verbose \
 --web-server-logging filesystem
```

### Verify Configuration

```bash
az webapp log show \
 --resource-group $RG \
 --name $APP_NAME \
 --output json
```

**Example output:**
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

---

## Step 2: Real-time Log Stream

**Real-time logs** are useful right after deployment or when issues occur.

### Stream via CLI

```bash
az webapp log tail \
 --resource-group $RG \
 --name $APP_NAME
```

Send a request and logs appear immediately:

```text
2025-04-07T10:30:15.123Z {"level": "info", "message": "Request processed", "userId": "user-123"}
2025-04-07T10:30:15.456Z {"level": "error", "message": "Database connection failed", "error": "timeout"}
```

### Filter JSON Logs Only

```bash
az webapp log tail \
 --resource-group $RG \
 --name $APP_NAME \
 | grep --line-buffered '"level"'
```

---

## Step 3: Structured Logging (JSON)

**JSON logs** are much better for analysis than string logs.

### Python Configuration

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
 # Merge additional fields
 if hasattr(record, "custom_dimensions"):
 log_obj.update(record.custom_dimensions)
 return json.dumps(log_obj)

# Handler setup
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())

logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

### Usage Example

```python
logger.info("Order created", extra={"custom_dimensions": {
 "orderId": "ORD-12345",
 "userId": "user-789",
 "totalAmount": 150.00
}})
```

**Output:**
```json
{"timestamp": "2025-04-07T10:30:15.123Z", "level": "info", "message": "Order created", "orderId": "ORD-12345", "userId": "user-789", "totalAmount": 150.0}
```

---

## Step 4: Request Tracing with Correlation ID

To link all logs from a single request, you need a **Correlation ID**.

![Correlation ID across a single request](../../../assets/azure-app-service-101/06/03-correlation-id-flow.en.png)

*Correlation ID across a single request*

### Middleware Implementation

```python
import uuid
from flask import Flask, request, g, has_request_context

app = Flask(__name__)

@app.before_request
def set_correlation_id():
 # Get from header or generate new
 g.correlation_id = request.headers.get(
 "X-Correlation-ID", 
 str(uuid.uuid4())
 )

@app.after_request
def add_correlation_header(response):
 response.headers["X-Correlation-ID"] = g.correlation_id
 return response
```

### Auto-include in Logging

```python
class CorrelationFilter(logging.Filter):
 def filter(self, record):
  if has_request_context():
   record.correlation_id = g.get('correlation_id', '-')
  else:
   record.correlation_id = '-'
  return True

logger.addFilter(CorrelationFilter())
```

### Usage

When a user reports an error, request the `X-Correlation-ID` header value to query all logs for that request.

```bash
# Filter logs by specific Correlation ID
az webapp log tail --resource-group $RG --name $APP_NAME \
 | grep --line-buffered "a1b2c3d4"
```

---

## Step 5: Application Insights Integration

Set up **Application Insights** for long-term analysis and alerting.

### Create Application Insights

```bash
az monitor app-insights component create \
 --resource-group $RG \
 --app $APP_NAME-insights \
 --location $LOCATION \
 --kind web
```

### Get Connection String

```bash
APPINSIGHTS_CS=$(az monitor app-insights component show \
 --resource-group $RG \
 --app $APP_NAME-insights \
 --query connectionString \
 --output tsv)
```

### Add to App Settings

```bash
az webapp config appsettings set \
 --resource-group $RG \
 --name $APP_NAME \
 --settings APPLICATIONINSIGHTS_CONNECTION_STRING=$APPINSIGHTS_CS
```

### Install Python SDK

```bash
pip install azure-monitor-opentelemetry
```

### Initialize in App

```python
from azure.monitor.opentelemetry import configure_azure_monitor
import os

if os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING"):
 configure_azure_monitor(
 connection_string=os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
 )
```

---

## Step 6: Log Analysis with KQL

Logs stored in Application Insights are analyzed with **KQL (Kusto Query Language)**.

### Query Recent Errors

```kql
AppTraces
| where TimeGenerated > ago(1h)
| where SeverityLevel == 3 // Error
| project TimeGenerated, Message, Properties
| order by TimeGenerated desc
| take 20
```

### Error Rate Time Series

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

### Top 10 Slowest Requests

```kql
AppRequests
| where TimeGenerated > ago(1h)
| top 10 by DurationMs desc
| project TimeGenerated, Name, DurationMs, ResultCode
```

### Trace by Correlation ID

```kql
AppTraces
| where TimeGenerated > ago(24h)
| extend correlationId = tostring(Properties["correlationId"])
| where correlationId == "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
| project TimeGenerated, SeverityLevel, Message
| order by TimeGenerated asc
```

---

## Step 7: Configure Alerts

Set up automatic notifications when issues occur.

### Error Rate Alert

```bash
az monitor metrics alert create \
 --resource-group $RG \
 --name "High Error Rate" \
 --scopes "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RG/providers/Microsoft.Web/sites/$APP_NAME" \
 --condition "avg Http5xx > 10" \
 --window-size 5m \
 --evaluation-frequency 1m
```

### Configure in Azure Portal

1. App Service → Alerts → + Create alert rule
2. Condition: HTTP 5xx > 10
3. Action group: Email/SMS/Webhook

---

## Checking Logs in Filesystem

### Access via Kudu

```text
https://<app-name>.scm.azurewebsites.net
```

**Paths:**
```text
/home/LogFiles/
├── <hostname>_docker.log ← Container stdout
├── Application/
│ └── <date>_<hostname>_default_docker.log
└── kudu/
 └── deployment/ ← Deployment logs
```

### Access via SSH

```bash
az webapp ssh --resource-group $RG --name $APP_NAME

# Inside container
tail -f /home/LogFiles/*_docker.log
```

### Download Logs

```bash
az webapp log download \
 --resource-group $RG \
 --name $APP_NAME \
 --log-file ./logs.zip

unzip logs.zip -d ./logs
```

---

## Log Level Management

### Purpose by Level

| Level | Purpose | Recommended for Production |
|-------|---------|---------------------------|
| DEBUG | Detailed debugging | No |
| INFO | Normal operation info | Yes |
| WARNING | Potential issues | Yes |
| ERROR | Error occurred | Yes |
| CRITICAL | Severe failure | Yes |

### Dynamic Level Change

```bash
# Enable DEBUG during incident investigation
az webapp config appsettings set \
 --resource-group $RG \
 --name $APP_NAME \
 --settings LOG_LEVEL=DEBUG

# Revert after investigation
az webapp config appsettings set \
 --resource-group $RG \
 --name $APP_NAME \
 --settings LOG_LEVEL=INFO
```

> DEBUG level increases **costs** and risks **sensitive information exposure**, so always revert after investigation.

---

## Troubleshooting Scenarios

### "Logs aren't showing"

1. Verify logging is enabled: `az webapp log show`
2. Check if app outputs to stdout
3. Enable Log stream then trigger a request

### "No data in Application Insights"

1. Check `APPLICATIONINSIGHTS_CONNECTION_STRING` setting
2. Verify SDK initialization code
3. Wait 2-3 minutes (data collection delay)

### "Want to find specific errors"

```kql
// Trace by Correlation ID
AppTraces
| where Properties contains "correlation-id-here"

// Errors in specific time range
AppTraces
| where TimeGenerated between(datetime(2025-04-07 10:00)..datetime(2025-04-07 11:00))
| where SeverityLevel >= 3
```

---

## Summary

Logging and monitoring essentials:

- **Filesystem Logs**: Immediate debugging
- **Structured JSON Logs**: Easy analysis
- **Correlation ID**: Per-request tracing
- **Application Insights**: Long-term analysis and alerting
- **KQL**: Powerful query language

---

## Operational checklist

- [ ] Centralized App Service diagnostic logs in Log Analytics
- [ ] Enabled Application Insights and decided on a sampling policy
- [ ] Set thresholds for memory, 5xx, and latency alerts
- [ ] Wired alerts on disk quota and dependency failures
- [ ] Documented the first-five-minutes actions in the incident runbook

<!-- toc:begin -->
## In this series

- [What is Azure App Service? - Understanding the Platform Architecture](./01-what-is-app-service.md)
- [Request Lifecycle: How Requests Reach Your App](./02-request-lifecycle.md)
- [Hosting Models: Which Plan Should You Choose?](./03-hosting-models.md)
- [First Deployment: From Local to Azure (Python/Flask)](./04-first-deploy.md)
- [Mastering Configuration: App Settings & Environment Variables](./05-configuration.md)
- **Logging and Monitoring Basics (current)**
- Scaling 101: When to Scale Up vs Scale Out? (upcoming)

<!-- toc:end -->

---

## References

### Official Docs
- [Enable diagnostics logging (Microsoft Learn)](https://learn.microsoft.com/azure/app-service/troubleshoot-diagnostic-logs)
- [Azure Monitor OpenTelemetry for Python (Microsoft Learn)](https://learn.microsoft.com/azure/azure-monitor/app/opentelemetry-enable?tabs=python)
- [KQL Quick Reference](https://learn.microsoft.com/azure/data-explorer/kql-quick-reference)

### Related Series
- [Azure Functions 101](../../azure-functions-101/en/)

---

Tags: Azure, App Service, Cloud, Web Apps
