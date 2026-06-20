---
title: "바이브코딩을 위한 Azure App Service (7/7): 스케일링"
series: azure-app-service-101
episode: 7
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- AzureAppService
- 스케일링
- Autoscale
- AI코딩
seo_description: "바이브코딩을 위한 Azure App Service 7편: 스케일링. Scale Up과 Scale Out을 언제 선택하고 Autoscale과 비용 상한을 어떻게 설계할지 이해합니다."
---

# 바이브코딩을 위한 Azure App Service (7/7): 스케일링

이 글은 바이브코딩을 위한 Azure App Service 시리즈의 마지막 글입니다.

트래픽이 늘고 앱이 느려지기 시작하면 다음 질문은 항상 같습니다. 인스턴스를 더 크게 키워야 할까, 아니면 개수를 늘려야 할까. Scale Up(수직 확장)은 vCPU와 메모리를 키우는 것이고, Scale Out(수평 확장)은 인스턴스 수를 늘리는 것입니다. CPU 바운드 작업은 Scale Out이, 메모리 부족은 Scale Up이 더 효과적입니다. 더 중요한 것은 Autoscale 규칙에 비용 상한이 없으면 한 번의 잘못된 배포가 순식간에 큰 청구서로 이어질 수 있다는 점입니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI에게 Autoscale 코드를 요청할 때 최대 인스턴스 수와 비용 상한을 명시하지 않으면, 무제한 확장이 가능한 규칙이 생성되기 때문입니다.

> 비용 상한이 없는 scale rule은, 한 번의 잘못된 배포가 순식간에 큰 청구서로 이어지는 가장 빠른 경로입니다.

---

## 이 글에서 다룰 문제

- Scale Up과 Scale Out은 어떤 병목 상황에서 각각 선택해야 할까요?
- Autoscale 규칙을 만들 때 반드시 포함해야 하는 방어 설정은 무엇일까요?
- 스케일링 이벤트가 실제로 앱에 미치는 영향을 어떻게 최소화할까요?
- 자주 하는 실수와 그 해결책은 무엇일까요?
- 이 개념을 실무에 적용하는 방법은 무엇일까요?

스케일링을 이해하면 AI에게 "CPU 70% 초과 시 Scale Out, 최대 5개 인스턴스, 비용 알림 설정을 포함한 Autoscale 규칙 az CLI 명령"을 정확하게 요청할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "App Service Autoscale 설정해줘"
→ 최대 인스턴스 수 없는 무제한 확장 규칙
→ Scale In 조건 없어 인스턴스가 줄어들지 않음
→ 비용 알림 없음
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "CPU 70% 초과 5분 지속 시 인스턴스 1개 추가(최대 5개),
    CPU 30% 미만 10분 지속 시 인스턴스 1개 제거(최소 1개)로
    Autoscale을 설정해줘.
    월 비용이 예산의 80%에 도달하면 이메일 알림도 추가해줘"
→ Scale Out/In 균형
→ 비용 상한으로 예산 보호
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| Scale In 규칙 없이 Scale Out만 | 인스턴스가 줄어들지 않아 비용 낭비 | Scale Out과 Scale In을 항상 쌍으로 설정 |
| 최대 인스턴스 수 미설정 | 무제한 확장으로 예산 초과 | max_count를 반드시 명시 |
| Scale Up으로 모든 문제 해결 시도 | 메모리 문제가 아니면 비효율적 | 병목 유형(CPU vs 메모리)을 먼저 진단 |
| Cool-down 없는 스케일 규칙 | 스케일링 진동(oscillation) 발생 | Scale Out/In 각각 5~10분 cool-down |
| 스케일링 이벤트 알림 없음 | 비정상 확장을 늦게 발견 | Autoscale 이벤트 알림 설정 |

## AI 협업 팁

App Service 스케일링 관련 효과적인 AI 프롬프트 패턴:

1. **Scale Out 규칙 요청**: "CPU 평균 70% 초과 5분 지속 시 1개 추가, 최대 5개, cool-down 5분으로 Autoscale 규칙을 az CLI로 생성해줘"
2. **Scale In 규칙 요청**: "CPU 평균 30% 미만 10분 지속 시 1개 제거, 최소 1개, cool-down 10분으로 Scale In 규칙을 추가해줘"
3. **비용 알림 요청**: "월 App Service 비용이 $200을 초과할 때 이메일로 알림을 보내는 Azure Budget Alert 설정 명령 작성해줘"

예시 프롬프트:
> "App Service Autoscale을 완전하게 설정하는 az CLI 스크립트를 작성해줘. CPU 70% 초과→1개 추가(최대5개, cool-down 5분), CPU 30% 미만→1개 제거(최소1개, cool-down 10분). Autoscale 이벤트 이메일 알림과 월 $200 예산 초과 알림 포함."

## 운영 체크리스트

- [ ] Scale Out과 Scale In 규칙이 쌍으로 설정됐는가?
- [ ] 최대 인스턴스 수(max_count)가 명시됐는가?
- [ ] Scale Out/In 각각 적절한 cool-down 시간이 설정됐는가?
- [ ] 예산 초과 알림이 설정됐는가?
- [ ] 스케일링 이벤트 로그를 Activity Log에서 확인할 수 있는가?

## 처음 질문으로 돌아가기

스케일링을 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. 최대 인스턴스 수와 비용 상한을 명시한 사람과 그렇지 않은 사람이 AI에게 받는 Autoscale 코드의 안전성은 크게 다릅니다.

## 정리

스케일링은 바이브코딩을 위한 Azure App Service 시리즈의 마지막 단계입니다. 플랫폼 아키텍처, 요청 수명 주기, 호스팅 모델, 배포, 설정, 모니터링이 Scale Up/Out 결정으로 연결됐습니다. 비용 상한과 Cool-down 설정이 없는 Autoscale은 위험하다는 것이 이 글의 핵심 메시지입니다.

## 참고 자료

- [Autoscale in Azure App Service](https://docs.microsoft.com/azure/azure-monitor/autoscale/autoscale-get-started)
- [Scale up an app in App Service](https://docs.microsoft.com/azure/app-service/manage-scale-up)
- [Azure Cost Management and Billing](https://docs.microsoft.com/azure/cost-management-billing/)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-app-service-101/ko/07-scaling-101)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Azure App Service (1/7): App Service란 무엇인가
- 바이브코딩을 위한 Azure App Service (2/7): 요청 수명 주기
- 바이브코딩을 위한 Azure App Service (3/7): 호스팅 모델 선택
- 바이브코딩을 위한 Azure App Service (4/7): 첫 번째 배포
- 바이브코딩을 위한 Azure App Service (5/7): 설정 관리
- 바이브코딩을 위한 Azure App Service (6/7): 로그와 모니터링
- **바이브코딩을 위한 Azure App Service (7/7): 스케일링 (현재 글)**
<!-- toc:end -->

Tags: 바이브코딩, AzureAppService, 스케일링, AI코딩
