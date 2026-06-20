---
title: "바이브코딩을 위한 Azure App Service 심화 (2/6): Front-End와 ARR"
series: azure-app-service-deep-dive
episode: 2
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- AzureAppService심화
- ARRAffinity
- 라우팅
- AI코딩
seo_description: "바이브코딩을 위한 Azure App Service 심화 2편: Front-End와 ARR. ARR Affinity와 슬롯이 요청 라우팅에 미치는 영향을 이해합니다."
---

# 바이브코딩을 위한 Azure App Service 심화 (2/6): Front-End와 ARR

이 글은 바이브코딩을 위한 Azure App Service 심화 시리즈의 2번째 글입니다.

App Service 장애를 애플리케이션 코드부터 의심하는 습관은 생각보다 자주 시간을 낭비하게 만듭니다. 실제로는 요청이 사용자 코드에 닿기 전에 이미 Front-End에서 앱과 슬롯이 식별되고, ARR이 worker를 선택하며, affinity 여부에 따라 같은 사용자가 같은 인스턴스에 계속 붙을 수 있기 때문입니다. 일부 사용자만 계속 느리거나 에러를 보는 부분 장애의 원인은 앱 로직보다 요청이 어떤 worker에 고정됐는지와 깊은 관련이 있을 때가 많습니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI에게 App Service 라우팅 관련 코드를 요청할 때 ARR Affinity 설정과 그 영향을 명시하지 않으면, stateless 앱에서 불필요한 세션 스티킹이 발생하는 코드가 생성되기 때문입니다.

> Front-End와 ARR의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

---

## 이 글에서 다룰 문제

- ARR Affinity는 어떤 상황에서 켜야 하고 언제 꺼야 할까요?
- 부분 장애(일부 사용자만 에러)가 ARR과 관련된 이유는 무엇일까요?
- 슬롯과 커스텀 도메인이 Front-End 라우팅 결정에 어떻게 개입할까요?
- 자주 하는 실수와 그 해결책은 무엇일까요?
- 이 개념을 실무에 적용하는 방법은 무엇일까요?

ARR 라우팅을 이해하면 AI에게 "stateless API 앱에서 ARR Affinity를 비활성화하고 부분 장애 시 특정 인스턴스를 격리하는 명령"을 정확하게 요청할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "App Service에서 일부 사용자만 에러 날 때 원인은?"
→ 앱 코드 버그 의심 조언
→ ARR Affinity와 인스턴스 고정 개념 없음
→ 해결 방법 불명확
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "App Service에서 일부 사용자만 에러를 볼 때
    ARR Affinity 쿠키(ARRAffinity)가 특정 인스턴스에 고정되어 있는지 확인하고
    az webapp update로 ARR Affinity를 비활성화하는 명령을 작성해줘.
    stateless API 앱에서 ARR Affinity가 필요 없는 이유도 설명해줘"
→ 부분 장애 원인 정확히 파악
→ Affinity 설정 변경으로 해결
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| stateless 앱에 ARR Affinity 켜두기 | 불균등 부하 분산, 특정 인스턴스 과부하 | `az webapp update --client-affinity-enabled false` |
| ARR Affinity 쿠키를 클라이언트에서 보존 | 서버 재시작 후도 특정 인스턴스에 고정 | 쿠키 없이 요청하거나 Affinity 비활성화 |
| 슬롯 URL과 앱 URL을 혼용 | 다른 슬롯으로 라우팅될 수 있음 | 슬롯별 URL 구분 명확히 |
| 모든 요청이 고르게 분산된다고 가정 | Affinity 쿠키로 고정된 요청이 있을 수 있음 | 인스턴스별 요청 수 메트릭 확인 |
| 커스텀 도메인 라우팅과 슬롯 스왑 연동 무시 | 스왑 후 트래픽 분산 예상과 다를 수 있음 | 스왑 전 라우팅 설정 확인 |

## AI 협업 팁

ARR 라우팅 관련 효과적인 AI 프롬프트 패턴:

1. **Affinity 비활성화 요청**: "stateless API 앱에서 ARR Affinity를 비활성화하는 az webapp update 명령과 비활성화해야 하는 이유를 작성해줘"
2. **인스턴스 분산 확인 요청**: "Application Insights에서 인스턴스별 요청 수를 집계해 불균등 분산을 확인하는 KQL 쿼리 작성해줘"
3. **부분 장애 진단 요청**: "특정 인스턴스에서만 5xx 에러가 날 때 해당 인스턴스를 격리하는 진단 절차를 작성해줘"

예시 프롬프트:
> "App Service REST API 앱에서 ARR Affinity 설정을 최적화해줘. 1) 현재 Affinity 설정 확인 명령 2) stateless 앱에서 비활성화하는 이유와 명령 3) 인스턴스별 요청 분산을 KQL로 확인하는 쿼리."

## 운영 체크리스트

- [ ] 앱이 stateless인 경우 ARR Affinity가 비활성화됐는가?
- [ ] 인스턴스별 요청 분산 메트릭을 모니터링하는가?
- [ ] 슬롯별 URL과 트래픽 라우팅 설정을 구분하고 있는가?
- [ ] 부분 장애 시 특정 인스턴스를 격리하는 절차가 있는가?
- [ ] 다음 글에서 Worker 샌드박스 내부의 실행 경계를 이해할 준비가 됐는가?

## 처음 질문으로 돌아가기

ARR 라우팅을 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. ARR Affinity 설정의 영향을 이해한 사람과 그렇지 않은 사람이 AI에게 받는 부분 장애 진단 코드의 완성도는 크게 다릅니다.

## 정리

Front-End와 ARR은 바이브코딩을 위한 Azure App Service 심화에서 요청이 Worker에 도달하는 경로를 제어하는 핵심 계층입니다. ARR Affinity의 영향과 stateless 앱에서의 비활성화 필요성을 이해했습니다. 다음 글에서는 Worker 내부의 샌드박스 실행 경계를 다룹니다.

## 참고 자료

- [Disable ARR Affinity](https://docs.microsoft.com/azure/app-service/configure-common#configure-general-settings)
- [App Service deployment slots](https://docs.microsoft.com/azure/app-service/deploy-staging-slots)
- [Custom domain routing](https://docs.microsoft.com/azure/app-service/manage-custom-dns-buy-domain)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-app-service-deep-dive/ko/02-front-end-and-arr)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Azure App Service 심화 (1/6): 플랫폼 아키텍처
- **바이브코딩을 위한 Azure App Service 심화 (2/6): Front-End와 ARR (현재 글)**
- 바이브코딩을 위한 Azure App Service 심화 (3/6): Worker와 샌드박스
- 바이브코딩을 위한 Azure App Service 심화 (4/6): 배포와 Kudu
- 바이브코딩을 위한 Azure App Service 심화 (5/6): 스케일링 내부 동작
- 바이브코딩을 위한 Azure App Service 심화 (6/6): 콜드 스타트와 Warmup
<!-- toc:end -->

Tags: 바이브코딩, AzureAppService심화, ARRAffinity, AI코딩
