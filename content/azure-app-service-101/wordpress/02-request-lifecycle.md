---
title: "바이브코딩을 위한 Azure App Service (2/7): 요청 수명 주기"
series: azure-app-service-101
episode: 2
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- AzureAppService
- 요청수명주기
- 502에러
- AI코딩
seo_description: "바이브코딩을 위한 Azure App Service 2편: 요청 수명 주기. DNS부터 Frontend, Worker, 앱 프로세스까지 단계별로 502 에러를 추적하는 방법을 이해합니다."
---

# 바이브코딩을 위한 Azure App Service (2/7): 요청 수명 주기

이 글은 바이브코딩을 위한 Azure App Service 시리즈의 2번째 글입니다.

새벽 3시에 502 알람이 울리면 가장 먼저 해야 할 일은 로그를 많이 여는 것이 아닙니다. 요청이 앱 코드까지 오기 전에 어디에서 멈췄는지부터 구간을 나눠 보는 일입니다. App Service의 요청 경로는 DNS → Frontend(ARR) → Worker → 앱 프로세스 단계로 나뉩니다. 각 단계에서 다른 에러 코드와 다른 로그가 나타납니다. 502는 Frontend에서 Worker 응답을 못 받은 것이고, 503은 Worker 포화, 504는 타임아웃입니다. 이 구분 없이 로그를 열면 실제 원인을 찾는 데 시간이 오래 걸립니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI에게 App Service 장애 진단 코드를 요청할 때 어느 단계에서 실패했는지 지정하지 않으면, 앱 로그만 보는 불완전한 디버깅 코드가 생성되기 때문입니다.

> App Service의 요청 수명 주기는 안정적인 홉이 이어진 체인입니다. 502, 503, 504는 체인의 서로 다른 위치에서 발생합니다.

---

## 이 글에서 다룰 문제

- 502, 503, 504 에러는 요청 경로의 어느 단계에서 발생할까요?
- Frontend(ARR)와 Worker는 어떤 역할을 맡고 있을까요?
- 앱 코드에 에러가 없어도 502가 날 수 있는 이유는 무엇일까요?
- 자주 하는 실수와 그 해결책은 무엇일까요?
- 이 개념을 실무에 적용하는 방법은 무엇일까요?

요청 수명 주기를 이해하면 AI에게 "App Service에서 502가 났을 때 ARR 로그와 앱 로그를 순서대로 확인하는 진단 스크립트"를 정확하게 요청할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "App Service 502 에러 해결 방법 알려줘"
→ 앱 코드 로그만 확인하라는 일반 조언
→ 단계별 원인 구분 없음
→ ARR/Worker 레이어 무시
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "App Service에서 502가 났을 때
    1) ARR 액세스 로그에서 sc-status=502인 항목 필터링
    2) Worker 재시작 여부를 Activity Log에서 확인
    3) 앱 프로세스 시작 실패를 LogStream에서 확인
    하는 순서대로 Azure CLI 명령을 작성해줘"
→ 단계별 원인 좁히기
→ 각 레이어에 맞는 로그 조회
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| 앱 로그만 먼저 확인 | ARR이나 Worker 문제면 앱 로그에 흔적 없음 | 에러 코드로 발생 레이어 먼저 판단 |
| 502와 503을 같은 원인으로 봄 | 502=Worker 무응답, 503=Worker 포화로 원인이 다름 | 에러 코드별 진단 경로를 다르게 |
| 재시작 후 원인 없이 종료 | 일시적 해결이지만 근본 원인 미파악 | 재시작 전 필수 로그 스냅샷 확보 |
| cold start를 장애로 오인 | 첫 요청이 느린 것은 정상 (Free/Basic) | Basic 이상에서 always-on 활성화 |
| 타임아웃 기본값 230초 모름 | 장기 작업이 자동 종료됨 | 배경 작업은 WebJobs나 별도 서비스로 |

## AI 협업 팁

App Service 요청 진단 관련 효과적인 AI 프롬프트 패턴:

1. **에러 로그 조회 요청**: "az webapp log tail로 실시간 로그를 보고 5xx 에러만 필터링하는 명령 작성해줘"
2. **단계별 진단 요청**: "App Service에서 503이 났을 때 인스턴스 상태, CPU/메모리 메트릭, 큐 길이를 순서대로 확인하는 Azure Monitor 쿼리 작성해줘"
3. **알림 설정 요청**: "5분 안에 502 에러가 10회 이상 발생하면 이메일로 알림을 보내는 Azure Monitor Alert 설정 명령 작성해줘"

예시 프롬프트:
> "App Service에서 새벽에 502가 빈번하게 발생할 때 원인을 단계별로 좁히는 진단 절차를 작성해줘. ARR 로그 확인 → Worker 상태 확인 → 앱 프로세스 로그 확인 순서로 Azure CLI 명령과 확인 포인트를 포함."

## 운영 체크리스트

- [ ] 502, 503, 504 에러가 어느 레이어에서 발생하는지 구분할 수 있는가?
- [ ] ARR 액세스 로그와 앱 로그를 별도로 조회하는 방법을 아는가?
- [ ] App Service 기본 타임아웃(230초)을 초과하는 작업을 별도로 처리하는가?
- [ ] 5xx 에러 발생 시 알림이 설정됐는가?
- [ ] 다음 글에서 호스팅 모델을 선택할 때 이 수명 주기 지식을 적용할 준비가 됐는가?

## 처음 질문으로 돌아가기

요청 수명 주기를 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. 단계별 진단 경로를 명시한 사람과 그렇지 않은 사람이 AI에게 받는 장애 진단 코드의 완성도는 크게 다릅니다.

## 정리

요청 수명 주기는 바이브코딩을 위한 Azure App Service에서 장애 원인을 빠르게 좁히는 핵심 멘탈 모델입니다. 502/503/504의 발생 레이어 차이와 ARR의 역할을 이해했습니다. 다음 글에서는 호스팅 모델 선택 기준을 다룹니다.

## 참고 자료

- [Diagnose and solve problems in App Service](https://docs.microsoft.com/azure/app-service/overview-diagnostics)
- [App Service HTTP logs](https://docs.microsoft.com/azure/app-service/troubleshoot-diagnostic-logs)
- [Application Gateway and ARR](https://docs.microsoft.com/azure/app-service/networking-features)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-app-service-101/ko/02-request-lifecycle)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Azure App Service (1/7): App Service란 무엇인가
- **바이브코딩을 위한 Azure App Service (2/7): 요청 수명 주기 (현재 글)**
- 바이브코딩을 위한 Azure App Service (3/7): 호스팅 모델 선택
- 바이브코딩을 위한 Azure App Service (4/7): 첫 번째 배포
- 바이브코딩을 위한 Azure App Service (5/7): 설정 관리
- 바이브코딩을 위한 Azure App Service (6/7): 로그와 모니터링
- 바이브코딩을 위한 Azure App Service (7/7): 스케일링
<!-- toc:end -->

Tags: 바이브코딩, AzureAppService, 요청수명주기, AI코딩
