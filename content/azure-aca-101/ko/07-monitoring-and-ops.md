---
title: 모니터링과 운영 — Log Analytics와 Application Insights
series: azure-aca-101
episode: 7
language: ko
status: ready
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

# 모니터링과 운영 — Log Analytics와 Application Insights

> Azure Container Apps 101 시리즈 (7/7)

이번 글은 로그, 추적, 운영 절차를 함께 다룹니다. 여기서 가장 중요한 구분은 ACA가 기본으로 주는 플랫폼 로그와, 애플리케이션이 직접 내보내야 하는 Application Insights 추적이 같은 계층이 아니라는 점입니다.

---

## 관측성 지도

무슨 일이 있었는지는 Log Analytics에서 찾고.
요청이 어디를 거쳤는지는 Application Insights에서 따라갑니다.

![로그와 추적이 모이는 관측 경로](../../../assets/azure-aca-101/07/07-01-the-observability-map.ko.png)
---

## 두 종류 로그

- ContainerAppConsoleLogs_CL
- ContainerAppSystemLogs_CL

---

## KQL 예시

```kusto
ContainerAppConsoleLogs_CL
| where ContainerAppName_s == "fastapi-aca-demo"
| project Time=TimeGenerated, Revision=RevisionName_s, Message=Log_s
| take 100

ContainerAppSystemLogs_CL
| where ContainerAppName_s == "fastapi-aca-demo"
| project Time=TimeGenerated, Revision=RevisionName_s, Message=Log_s
| take 100
```

---

## Revision 비교

```kusto
ContainerAppConsoleLogs_CL
| where ContainerAppName_s == "fastapi-aca-demo"
| summarize count() by RevisionName_s
| order by count_ desc
```

---

## Application Insights

Application Insights는 분산 추적과 dependency 분석에 강하지만, Environment를 만들었다고 해서 앱 추적이 자동으로 완성되지는 않습니다.

- **Log Analytics**는 ACA 환경의 플랫폼 로그와 컨테이너 로그를 저장합니다.
- **Application Insights**는 앱 코드가 SDK나 OpenTelemetry를 통해 직접 텔레메트리를 보내야 의미가 생깁니다.
- **Dapr telemetry**는 별도 신호입니다. `--dapr-connection-string`은 Dapr 사이드카 텔레메트리용이지, 일반 애플리케이션 추적 설정이 아닙니다.

즉, 플랫폼 가시성은 Log Analytics로 확보하고, 애플리케이션 추적은 앱 계측으로 붙이고, Dapr 연결 문자열은 정말 사이드카 수준 텔레메트리가 필요할 때만 구분해서 써야 합니다.

---

## 운영에서 기억할 점

- 로그 조회는 항상 Revision 기준으로 시작하는 편이 빠릅니다.
- system logs는 플랫폼 판단을, console logs는 앱 동작을 읽는 데 더 적합합니다.
- Application Insights와 Dapr telemetry는 플랫폼 로그 위에 선택적으로 얹는 별도 계층으로 이해해야 합니다.

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

### 관련 시리즈
- [Azure App Service 101](../../azure-app-service-101/ko/01-what-is-app-service.md)
- [Azure AKS 101](../../azure-aks-101/ko/01-what-is-aks.md)
- [Azure Functions 101](../../azure-functions-101/ko/01-what-is-azure-functions.md)

Tags: Azure, Container Apps, Serverless, Containers
