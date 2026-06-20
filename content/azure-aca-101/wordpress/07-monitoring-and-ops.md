---
title: "바이브코딩을 위한 Azure Container Apps (7/7): 모니터링과 운영"
series: azure-aca-101
episode: 7
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- AzureContainerApps
- LogAnalytics
- 관측성
- AI코딩
seo_description: "바이브코딩을 위한 Azure Container Apps 7편: 모니터링과 운영. 플랫폼, 애플리케이션, 사이드카 세 계층 관측성과 KQL 쿼리로 ACA 운영 문제를 진단합니다."
---

# 바이브코딩을 위한 Azure Container Apps (7/7): 모니터링과 운영

이 글은 바이브코딩을 위한 Azure Container Apps 시리즈의 마지막 글입니다.

운영 사고에서 어려운 지점은 데이터가 있느냐보다, 어느 계층이 답을 가지고 있느냐를 아는 일입니다. ACA 관측성은 플랫폼, 애플리케이션, 사이드카라는 세 계층으로 나뉩니다. 플랫폼 계층은 Log Analytics의 ContainerAppSystemLogs_CL에 있습니다. 앱이 5xx를 뿜기 시작했을 때 "어느 revision에서 생겼지?"라는 첫 번째 질문의 답이 여기에 있습니다. 두 번째 질문인 "어느 dependency가 느려졌지?"의 답은 Application Insights의 분산 트레이스에 있습니다. 세 번째 질문인 "replica가 몇 개까지 늘었지?"의 답은 Azure Monitor 메트릭에 있습니다. ACA는 첫 번째 질문의 답을 기본으로 제공하지만, 두 번째와 세 번째는 앱 계측이나 명시적인 Diagnostic Settings가 있어야 얻을 수 있습니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI에게 모니터링 코드를 요청할 때 계층을 명시하지 않으면, 모든 로그를 하나의 쿼리로 조회하려다 ContainerAppConsoleLogs_CL과 ContainerAppSystemLogs_CL의 차이를 모르는 코드가 생성되기 때문입니다.

> 모니터링과 운영의 핵심은 플랫폼 계층(Log Analytics), 앱 계층(Application Insights), 사이드카 계층(Dapr traces)이 각각 다른 질문에 답한다는 사실을 이해하는 데 있습니다.

---

## 이 글에서 다룰 문제

- ACA 관측성은 어떤 세 계층으로 나뉘고 각 계층은 무엇을 책임질까요?
- ContainerAppConsoleLogs_CL과 ContainerAppSystemLogs_CL은 무엇이 다를까요?
- Log Analytics에서 Revision 기준으로 로그를 묶는 KQL은 어떻게 작성할까요?
- ACA가 기본으로 주는 관측성과 앱이 직접 계측해야 하는 관측성의 경계는 어디일까요?
- 이 개념을 실무에 적용하는 방법은 무엇일까요?

ACA 관측성을 이해하면 AI에게 "Revision별 5xx 오류율 KQL 쿼리, Application Insights OpenTelemetry 연결 코드, replica 수 메트릭 알림 설정"을 정확하게 요청할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "ACA 앱 로그 보는 방법 알려줘"
→ 단순 az containerapp logs show 명령
→ ContainerAppConsoleLogs_CL vs SystemLogs_CL 구분 없음
→ Revision별 집계 없음
→ Application Insights 연결 없음
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "ACA 관측성을 세 계층으로 설정해줘.
    1) 플랫폼 계층: Log Analytics에서 ContainerAppSystemLogs_CL로
       Revision별 5xx 오류율 KQL 쿼리
    2) 앱 계층: FastAPI에 OpenTelemetry로 Application Insights 연결 코드
       (트레이스, 의존성 지연 시간 포함)
    3) 메트릭 알림: replica 수가 max에 도달하면 Azure Monitor 알림 설정"
→ 계층별 질문에 계층별 도구로 답변
→ 사고 시 원인 계층 빠르게 특정 가능
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| ConsoleLogs와 SystemLogs를 혼용 | 앱 출력과 플랫폼 이벤트가 섞여 노이즈 증가 | ConsoleLogs=앱 stdout, SystemLogs=플랫폼 이벤트 |
| Application Insights 미연결 | 분산 트레이스와 의존성 지연 시간 조회 불가 | OpenTelemetry로 앱 계측 + APPLICATIONINSIGHTS_CONNECTION_STRING 설정 |
| Revision 필터 없이 로그 집계 | 어느 버전에서 오류가 났는지 파악 불가 | KQL에서 RevisionName_s로 필터/집계 |
| 메트릭 알림 미설정 | 스케일 상한 도달 및 오류율 급등 인지 지연 | Azure Monitor 알림 규칙 설정 |
| Log Analytics workspace를 서비스마다 분리 | 크로스 서비스 KQL 조회 불가 | Environment당 workspace 하나로 통합 |

## AI 협업 팁

모니터링과 운영 관련 효과적인 AI 프롬프트 패턴:

1. **KQL 쿼리 요청**: "Log Analytics에서 ContainerAppSystemLogs_CL로 Revision별 5xx 오류율을 지난 1시간 집계하는 KQL 쿼리 작성해줘"
2. **Application Insights 연결 요청**: "FastAPI 앱에 OpenTelemetry로 Application Insights 분산 트레이스를 설정하는 코드 작성해줘 (APPLICATIONINSIGHTS_CONNECTION_STRING 환경 변수 사용)"
3. **알림 규칙 요청**: "ACA replica 수가 max에 도달하거나 5xx 오류율이 5%를 넘으면 Azure Monitor 알림을 보내는 az monitor 명령 작성해줘"

예시 프롬프트:
> "ACA 운영 관측성 설정을 완성해줘. 1) Revision별 5xx 오류율 KQL 2) FastAPI OpenTelemetry + Application Insights 연결 코드 3) replica max 도달 알림 규칙. 세 계층(플랫폼/앱/메트릭)을 각각 다루는 코드 포함."

## 운영 체크리스트

- [ ] Log Analytics workspace가 ACA Environment에 연결됐는가?
- [ ] Application Insights가 앱에 OpenTelemetry로 연결됐는가?
- [ ] KQL 쿼리에 RevisionName_s 필터가 포함됐는가?
- [ ] replica 수 상한 도달 및 5xx 오류율 알림이 설정됐는가?
- [ ] ContainerAppConsoleLogs_CL과 SystemLogs_CL의 용도를 구분하고 있는가?

## 처음 질문으로 돌아가기

ACA 모니터링과 운영을 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. 관측성 계층을 명시한 사람과 그렇지 않은 사람이 AI에게 받는 모니터링 설정 코드의 완성도는 크게 다릅니다.

## 정리

모니터링과 운영은 바이브코딩을 위한 Azure Container Apps 시리즈의 마지막 단계입니다. 플랫폼 계층(Log Analytics), 앱 계층(Application Insights), 메트릭 계층(Azure Monitor)의 역할 분리와 Revision별 KQL 쿼리를 이해했습니다. 이 시리즈에서 배운 ACA의 구조, 배포, 스케일링, Dapr, 관측성 개념을 명시해서 AI에게 요청하면 훨씬 완성도 높은 코드를 얻을 수 있습니다.

## 참고 자료

- [Log Analytics in Container Apps](https://docs.microsoft.com/azure/container-apps/log-monitoring)
- [Application Insights with Container Apps](https://docs.microsoft.com/azure/azure-monitor/app/app-insights-overview)
- [Monitor metrics in Azure Container Apps](https://docs.microsoft.com/azure/container-apps/metrics)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-aca-101/ko/07-monitoring-and-ops)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Azure Container Apps (1/7): Azure Container Apps란?
- 바이브코딩을 위한 Azure Container Apps (2/7): Environment, Container App, Revision
- 바이브코딩을 위한 Azure Container Apps (3/7): 첫 배포하기
- 바이브코딩을 위한 Azure Container Apps (4/7): Ingress와 트래픽 분할
- 바이브코딩을 위한 Azure Container Apps (5/7): 스케일링과 KEDA
- 바이브코딩을 위한 Azure Container Apps (6/7): Dapr 통합
- **바이브코딩을 위한 Azure Container Apps (7/7): 모니터링과 운영 (현재 글)**
<!-- toc:end -->

Tags: 바이브코딩, AzureContainerApps, LogAnalytics, AI코딩
