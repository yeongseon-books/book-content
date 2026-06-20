---
title: "바이브코딩을 위한 Azure App Service 심화 (4/6): 배포와 Kudu"
series: azure-app-service-deep-dive
episode: 4
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- AzureAppService심화
- Kudu
- 배포파이프라인
- AI코딩
seo_description: "바이브코딩을 위한 Azure App Service 심화 4편: 배포와 Kudu. 업로드, 빌드, 배치, 시작 준비의 네 단계로 배포 경로를 이해합니다."
---

# 바이브코딩을 위한 Azure App Service 심화 (4/6): 배포와 Kudu

이 글은 바이브코딩을 위한 Azure App Service 심화 시리즈의 4번째 글입니다.

"배포가 성공했다"는 말은 실제로는 꽤 많은 단계를 뭉뚱그린 표현입니다. artifact가 SCM 엔드포인트에 도착하는 것, 서버 쪽 build automation이 돌아가는 것(Oryx), 결과물이 wwwroot 또는 mounted package 형태로 놓이는 것, 그리고 앱 프로세스가 실제로 새 코드를 들고 readiness를 통과하는 것은 서로 다른 경계입니다. Kudu deployment history에 success가 찍혀 있는데 앱은 502를 내는 이유가 바로 여기 있습니다. 배포를 upload, build, placement, startup readiness라는 네 단계로 나눠 보면 어디서 성공했고 어디서 실패했는지 훨씬 빠르게 읽을 수 있습니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI에게 CI/CD 파이프라인 코드를 요청할 때 배포 성공과 앱 시작 성공을 분리하지 않으면, 배포가 성공했는데도 앱이 안 뜨는 상황을 감지하지 못하는 파이프라인이 생성되기 때문입니다.

> 배포와 Kudu의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

---

## 이 글에서 다룰 문제

- Kudu, Oryx, run-from-package는 배포 경로에서 각각 어떤 역할을 할까요?
- 배포 성공과 앱 시작 성공은 어떻게 분리해서 확인할 수 있을까요?
- slot warm-up이 cold start 비용을 줄이는 원리는 무엇일까요?
- 자주 하는 실수와 그 해결책은 무엇일까요?
- 이 개념을 실무에 적용하는 방법은 무엇일까요?

배포와 Kudu를 이해하면 AI에게 "ZIP 배포 후 Kudu 배포 히스토리와 앱 시작 로그를 각각 확인하는 CI/CD 파이프라인 스크립트"를 정확하게 요청할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "App Service CI/CD 파이프라인 코드 작성해줘"
→ 배포 명령 후 성공으로 종료
→ 앱 시작 확인 없음
→ 롤백 조건 없음
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "App Service ZIP 배포 파이프라인을 네 단계로 작성해줘.
    1) az webapp deploy로 ZIP 업로드
    2) Kudu REST API로 배포 상태 폴링
    3) /health 엔드포인트로 앱 시작 확인 (30초 간격 3회)
    4) 실패 시 이전 배포로 롤백하는 az webapp deployment rollback 실행"
→ 배포와 앱 시작을 분리 검증
→ 자동 롤백으로 운영 안전성 확보
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| 배포 명령 성공을 앱 동작 성공으로 오해 | Kudu success ≠ 앱 정상 응답 | /health 폴링으로 앱 시작 별도 확인 |
| Kudu URL과 앱 URL 혼동 | 배포 로그는 scm URL, 앱은 azurewebsites.net | SCM URL(.scm.azurewebsites.net)을 명확히 구분 |
| run-from-package 없이 배포 | 배포 중 파일 락 문제 발생 가능 | WEBSITE_RUN_FROM_PACKAGE=1 설정 권장 |
| staging slot 없이 직접 prod 배포 | 배포 중 prod 트래픽이 중단될 수 있음 | staging slot에 배포 후 swap |
| 롤백 절차 미준비 | 장애 발생 시 수동 복구로 시간 낭비 | 이전 배포 ID를 파이프라인에 저장 |

## AI 협업 팁

배포와 Kudu 관련 효과적인 AI 프롬프트 패턴:

1. **4단계 배포 파이프라인 요청**: "ZIP 업로드 → Kudu 상태 확인 → /health 폴링 → 실패 시 롤백으로 이어지는 bash 배포 스크립트 작성해줘"
2. **Kudu REST API 조회 요청**: "Kudu REST API로 최신 배포 상태를 조회하고 success/failed를 판단하는 Python 코드 작성해줘"
3. **slot swap 파이프라인 요청**: "staging slot에 배포 후 warm-up 확인하고 production으로 swap하는 CI/CD 단계를 작성해줘"

예시 프롬프트:
> "App Service 무중단 배포 스크립트를 작성해줘. staging slot에 ZIP 배포 → Kudu 배포 완료 확인 → staging /health 3회 폴링 → 모두 성공 시 swap → production /health 재확인 → 실패 시 swap 롤백."

## 운영 체크리스트

- [ ] 배포 성공과 앱 시작 성공을 별도로 확인하는가?
- [ ] WEBSITE_RUN_FROM_PACKAGE가 설정됐는가?
- [ ] staging slot을 사용해 production에 직접 배포하지 않는가?
- [ ] 배포 실패 시 이전 버전으로 롤백하는 절차가 있는가?
- [ ] 다음 글에서 스케일링 내부 동작을 이해할 준비가 됐는가?

## 처음 질문으로 돌아가기

배포와 Kudu를 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. 배포 단계를 분리해 검증하도록 명시한 사람과 그렇지 않은 사람이 AI에게 받는 CI/CD 파이프라인의 안전성은 크게 다릅니다.

## 정리

배포와 Kudu는 바이브코딩을 위한 Azure App Service 심화에서 artifact가 Worker에 도달하기까지의 전체 경로를 이해하는 핵심 단계입니다. upload, build, placement, startup readiness의 네 단계 분리와 staging slot 활용을 이해했습니다. 다음 글에서는 Scale Out 결정이 내부적으로 어떤 제어 루프를 거치는지 다룹니다.

## 참고 자료

- [Kudu documentation](https://github.com/projectkudu/kudu/wiki)
- [run-from-package deployment](https://docs.microsoft.com/azure/app-service/deploy-run-package)
- [Deployment slots](https://docs.microsoft.com/azure/app-service/deploy-staging-slots)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-app-service-deep-dive/ko/04-deployment-and-kudu)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Azure App Service 심화 (1/6): 플랫폼 아키텍처
- 바이브코딩을 위한 Azure App Service 심화 (2/6): Front-End와 ARR
- 바이브코딩을 위한 Azure App Service 심화 (3/6): Worker와 샌드박스
- **바이브코딩을 위한 Azure App Service 심화 (4/6): 배포와 Kudu (현재 글)**
- 바이브코딩을 위한 Azure App Service 심화 (5/6): 스케일링 내부 동작
- 바이브코딩을 위한 Azure App Service 심화 (6/6): 콜드 스타트와 Warmup
<!-- toc:end -->

Tags: 바이브코딩, AzureAppService심화, Kudu, AI코딩
