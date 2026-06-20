---
title: "바이브코딩을 위한 Azure App Service (6/7): 로그와 모니터링"
series: azure-app-service-101
episode: 6
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- AzureAppService
- 로그모니터링
- ApplicationInsights
- AI코딩
seo_description: "바이브코딩을 위한 Azure App Service 6편: 로그와 모니터링. App Service 로그 경로와 Application Insights, KQL로 앱 상태를 추적하는 방법을 이해합니다."
---

# 바이브코딩을 위한 Azure App Service (6/7): 로그와 모니터링

이 글은 바이브코딩을 위한 Azure App Service 시리즈의 6번째 글입니다.

"앱이 느려요." "에러가 나요." "언제부터 시작된 거죠?" 이런 질문에 답하지 못하면 App Service는 관리형 플랫폼이 아니라 보이지 않는 상자처럼 느껴집니다. App Service의 로그는 여러 곳에 흩어집니다. 앱 stdout/stderr은 LogStream과 Blob으로, HTTP 액세스 로그는 별도 경로로, 플랫폼 이벤트는 Activity Log로 갑니다. Application Insights를 연결하면 요청 추적, 의존성 지도, 예외 분석을 KQL 쿼리로 한곳에서 볼 수 있습니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI에게 모니터링 설정 코드를 요청할 때 로그 저장 위치, Application Insights 연결, 알림 조건을 명시하지 않으면, 로그가 어디로 가는지 모르는 상태로 운영하게 되기 때문입니다.

> 로그가 어디로 가는지, 실시간 디버깅과 장기 분석을 어떻게 나눌지, 어떤 알림 기준이 실제로 유용한지가 App Service 모니터링의 핵심입니다.

---

## 이 글에서 다룰 문제

- App Service 로그는 어디에 쌓이고 어떻게 꺼내 볼 수 있을까요?
- Application Insights를 연결하면 무엇을 추가로 볼 수 있을까요?
- KQL 쿼리로 느린 요청과 에러 패턴을 어떻게 찾을까요?
- 자주 하는 실수와 그 해결책은 무엇일까요?
- 이 개념을 실무에 적용하는 방법은 무엇일까요?

로그와 모니터링을 이해하면 AI에게 "Application Insights에서 p95 응답 시간이 2초를 넘는 요청을 찾는 KQL 쿼리와 알림 규칙 설정 명령"을 정확하게 요청할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "App Service 로그 보는 방법 알려줘"
→ az webapp log tail 하나만 알려줌
→ Application Insights 연결 없음
→ 알림 규칙 없음
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "App Service 모니터링을 세 단계로 설정해줘.
    1) az webapp log config로 앱 로그를 Blob에 저장 활성화
    2) az monitor app-insights component create로 Insights 생성 후 연결
    3) Application Insights에서 5xx 에러가 1분에 10건 초과 시 이메일 알림
    각각 az CLI 명령으로 작성해줘"
→ 로그 영속 저장
→ 자동 알림으로 장애 조기 감지
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| LogStream만 사용 | 실시간이지만 기록이 남지 않음 | Blob Storage로 로그 영속 저장 활성화 |
| Application Insights 없이 운영 | 요청 추적, 의존성 분석 불가 | 반드시 Insights 연결 후 운영 시작 |
| 알림 없이 수동 확인 | 장애를 늦게 발견 | 5xx 에러, 응답 시간 임계치 알림 설정 |
| 로그 보존 기간 미설정 | 기본값 짧아 과거 장애 분석 불가 | 최소 30일 보존 정책 설정 |
| 앱 로그와 플랫폼 로그를 같다고 혼동 | 원인 찾는 위치가 달라짐 | stdout/stderr vs Activity Log 구분 |

## AI 협업 팁

App Service 로그와 모니터링 관련 효과적인 AI 프롬프트 패턴:

1. **로그 저장 설정 요청**: "App Service 앱 로그를 Azure Blob Storage에 저장하고 30일 보존하는 az CLI 명령 작성해줘"
2. **KQL 쿼리 요청**: "Application Insights에서 지난 24시간 동안 p50/p95/p99 응답 시간을 엔드포인트별로 집계하는 KQL 쿼리 작성해줘"
3. **알림 규칙 요청**: "5분 내 5xx 에러 10건 초과 시 이메일로 알림을 보내는 Azure Monitor Alert 설정 az CLI 명령 작성해줘"

예시 프롬프트:
> "App Service 모니터링을 완성하는 스크립트를 작성해줘. 1) 앱 로그 Blob 저장 활성화 2) Application Insights 생성 및 연결 3) requests 테이블에서 duration > 2000ms인 요청 상위 10개를 찾는 KQL 쿼리 4) 5xx 에러 알림 규칙."

## 운영 체크리스트

- [ ] 앱 로그가 Blob Storage에 30일 이상 보존되는가?
- [ ] Application Insights가 연결되어 요청 추적이 가능한가?
- [ ] 5xx 에러와 응답 시간 임계치에 대한 알림이 설정됐는가?
- [ ] KQL로 느린 요청 패턴을 조회할 수 있는가?
- [ ] 다음 글에서 모니터링 데이터를 기반으로 스케일링 결정을 내릴 준비가 됐는가?

## 처음 질문으로 돌아가기

로그와 모니터링을 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. 로그 저장 위치와 알림 조건을 명시한 사람과 그렇지 않은 사람이 AI에게 받는 모니터링 설정 코드의 완성도는 크게 다릅니다.

## 정리

로그와 모니터링은 바이브코딩을 위한 Azure App Service에서 앱 상태를 지속적으로 관찰하는 핵심 운영 기반입니다. 로그 경로 구분, Application Insights 연결, KQL 쿼리, 알림 규칙을 이해했습니다. 다음 글에서는 모니터링 메트릭을 기반으로 스케일링 결정을 내리는 방법을 다룹니다.

## 참고 자료

- [Enable diagnostics logging in App Service](https://docs.microsoft.com/azure/app-service/troubleshoot-diagnostic-logs)
- [Application Insights for App Service](https://docs.microsoft.com/azure/azure-monitor/app/azure-web-apps)
- [KQL reference](https://docs.microsoft.com/azure/data-explorer/kusto/query/)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-app-service-101/ko/06-logging-monitoring)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Azure App Service (1/7): App Service란 무엇인가
- 바이브코딩을 위한 Azure App Service (2/7): 요청 수명 주기
- 바이브코딩을 위한 Azure App Service (3/7): 호스팅 모델 선택
- 바이브코딩을 위한 Azure App Service (4/7): 첫 번째 배포
- 바이브코딩을 위한 Azure App Service (5/7): 설정 관리
- **바이브코딩을 위한 Azure App Service (6/7): 로그와 모니터링 (현재 글)**
- 바이브코딩을 위한 Azure App Service (7/7): 스케일링
<!-- toc:end -->

Tags: 바이브코딩, AzureAppService, 로그모니터링, AI코딩
