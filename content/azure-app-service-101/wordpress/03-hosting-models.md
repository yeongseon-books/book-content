---
title: "바이브코딩을 위한 Azure App Service (3/7): 호스팅 모델 선택"
series: azure-app-service-101
episode: 3
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- AzureAppService
- 호스팅모델
- AppServicePlan
- AI코딩
seo_description: "바이브코딩을 위한 Azure App Service 3편: 호스팅 모델 선택. OS, 배포 모델, 가격 티어를 어떤 순서와 기준으로 고르는지 실무 의사결정 프레임을 이해합니다."
---

# 바이브코딩을 위한 Azure App Service (3/7): 호스팅 모델 선택

이 글은 바이브코딩을 위한 Azure App Service 시리즈의 3번째 글입니다.

App Service를 처음 만들 때 가장 먼저 부딪히는 질문은 "어떤 플랜을 골라야 하지?"입니다. Free, Basic, Standard, Premium에 Linux와 Windows, Code와 Container까지 선택지가 많아 보여도 기준이 보이지 않으면 결국 기본값을 선택하게 됩니다. 기본값은 대개 Free 티어 Windows이며, 이는 always-on이 없어 cold start가 빈번하고 커스텀 도메인도 불가한 설정입니다. 호스팅 모델 선택은 OS → 배포 방식 → 티어 순서로 좁히는 것이 실무에서 가장 효율적입니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI에게 App Service 생성 코드를 요청할 때 이 세 가지 선택 기준을 명시하지 않으면, 운영 요구사항과 맞지 않는 기본값 플랜이 선택되기 때문입니다.

> 호스팅 모델 선택은 OS, 배포 방식, 가격 티어를 순서대로 좁히는 의사결정입니다. 기본값은 대부분 운영 환경에 맞지 않습니다.

---

## 이 글에서 다룰 문제

- Linux와 Windows 호스팅은 어떤 상황에서 각각 선택해야 할까요?
- Code 배포와 Container 배포는 언제 어떤 것을 선택하는 게 유리할까요?
- Free, Basic, Standard, Premium 티어는 어떤 기준으로 구분할까요?
- 자주 하는 실수와 그 해결책은 무엇일까요?
- 이 개념을 실무에 적용하는 방법은 무엇일까요?

호스팅 모델 선택 기준을 이해하면 AI에게 "Python 3.11 FastAPI 앱을 Linux Standard S1에 Code 배포로 설정하는 App Service 생성 명령"을 정확하게 요청할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "App Service 플랜 선택 방법 알려줘"
→ 기능 목록 비교표만 생성
→ 실제 선택 순서 없음
→ 운영 요구사항 고려 없음
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "Python FastAPI 운영 앱을 배포할 때
    1) Linux 선택 이유
    2) Code vs Container 판단 기준
    3) always-on, custom domain, staging slot 필요 여부로
    Basic B2 vs Standard S1 중 선택 방법을 설명해줘"
→ 체계적인 의사결정 프레임
→ 요구사항 기반 선택 근거
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| Free 티어로 운영 배포 | always-on 없어 cold start, 커스텀 도메인 불가 | 운영은 Basic 이상 사용 |
| Windows에 Python/Node 배포 | Linux 대비 지원 기능과 성능 차이 | Python/Node는 Linux 우선 선택 |
| 티어를 나중에 올리면 된다고 방치 | 일부 기능은 상위 티어에서만 활성화 | 초기부터 요구사항 기반 티어 선택 |
| Container vs Code 고민 없이 선택 | Container는 이미지 관리 오버헤드 추가 | 팀 CI/CD 역량에 맞는 배포 모델 선택 |
| Plan 공유 남용 | 한 Plan의 부하가 다른 App에 영향 | 운영 App은 별도 Plan 사용 권장 |

## AI 협업 팁

호스팅 모델 선택 관련 효과적인 AI 프롬프트 패턴:

1. **티어 비교 요청**: "App Service Free, Basic B1, Standard S1, Premium P1v2의 always-on, custom domain, staging slot, autoscale 지원 여부를 표로 비교해줘"
2. **선택 가이드 요청**: "월 트래픽 100만 요청, 2개 staging slot, SSL 커스텀 도메인이 필요한 앱에 최적인 App Service Plan 티어와 이유를 설명해줘"
3. **생성 명령 요청**: "Linux Standard S1 Plan과 Python 3.11 웹앱을 Korea Central에 만드는 az CLI 명령을 작성해줘"

예시 프롬프트:
> "FastAPI Python 앱을 위한 App Service 설정을 추천해줘. 요구사항: Linux, always-on, 커스텀 도메인, staging slot 1개, 월 예산 $100 이하. 추천 Plan 티어, OS, Code/Container 배포 방식을 이유와 함께 설명해줘."

## 운영 체크리스트

- [ ] OS가 사용하는 런타임(Python/Node/Java)에 최적화됐는가?
- [ ] always-on이 필요한 운영 앱은 Basic 이상인가?
- [ ] staging slot이 필요하면 Standard 이상인가?
- [ ] 운영 App은 개발/테스트 App과 별도 Plan을 사용하는가?
- [ ] 다음 글에서 이 호스팅 모델로 실제 첫 배포를 진행할 준비가 됐는가?

## 처음 질문으로 돌아가기

호스팅 모델 선택 기준을 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. OS, 배포 방식, 티어를 명시한 사람과 그렇지 않은 사람이 AI에게 받는 App Service 설정 코드의 운영 적합성은 크게 다릅니다.

## 정리

호스팅 모델 선택은 바이브코딩을 위한 Azure App Service에서 운영 환경을 올바르게 출발하는 핵심 결정입니다. OS → 배포 방식 → 티어 순서로 좁히는 의사결정 프레임을 이해했습니다. 다음 글에서는 선택한 호스팅 모델로 첫 번째 배포를 진행합니다.

## 참고 자료

- [App Service pricing tiers](https://azure.microsoft.com/pricing/details/app-service/linux/)
- [Choose an App Service plan](https://docs.microsoft.com/azure/app-service/overview-hosting-plans)
- [Linux vs Windows for App Service](https://docs.microsoft.com/azure/app-service/overview)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-app-service-101/ko/03-hosting-models)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Azure App Service (1/7): App Service란 무엇인가
- 바이브코딩을 위한 Azure App Service (2/7): 요청 수명 주기
- **바이브코딩을 위한 Azure App Service (3/7): 호스팅 모델 선택 (현재 글)**
- 바이브코딩을 위한 Azure App Service (4/7): 첫 번째 배포
- 바이브코딩을 위한 Azure App Service (5/7): 설정 관리
- 바이브코딩을 위한 Azure App Service (6/7): 로그와 모니터링
- 바이브코딩을 위한 Azure App Service (7/7): 스케일링
<!-- toc:end -->

Tags: 바이브코딩, AzureAppService, 호스팅모델, AI코딩
