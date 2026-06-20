---
title: "바이브코딩을 위한 Azure Functions (5/7): 어떤 플랜을 선택해야 할까"
series: azure-functions-101
episode: 5
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- AzureFunctions
- Serverless
- AI코딩
seo_description: "바이브코딩을 위한 Azure Functions 5편: 어떤 플랜을 선택해야 할까. Consumption/Flex/Premium/Dedicated 플랜을 OS, VNet, 콜드 스타트, 비용 기준으로 선택하는 방법을 이해합니다."
---

# 바이브코딩을 위한 Azure Functions (5/7): 어떤 플랜을 선택해야 할까

이 글은 바이브코딩을 위한 Azure Functions 시리즈의 5번째 글입니다.

플랜 선택은 Azure Functions에서 가장 과소평가되기 쉬운 초기 결정입니다. 코드는 나중에도 바꿀 수 있지만, 플랜이 잘못 맞춰져 있으면 콜드 스타트, 네트워크 제약, 기능 지원 범위, 비용 구조가 전부 뒤에서 문제로 돌아옵니다. 같은 서버리스라고 해도 운영 감각은 플랜마다 꽤 다릅니다. Consumption과 Flex Consumption은 scale to zero와 실행 기반 과금이 중심이고, Premium은 warm capacity를 비용으로 사는 모델이며, Dedicated는 Functions 프로그래밍 모델을 App Service 위에서 운영하는 성격입니다. "새 앱은 Flex부터 본다"는 말은 맞지만, Blob trigger 제약, Linux 전용, 슬롯 없음 같은 단서가 빠지면 실무에서는 오판이 됩니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI에게 Functions 배포 코드를 요청할 때 플랜 선택 기준을 명시하지 않으면, 모든 워크로드에 동일한 Consumption 플랜을 적용하거나 VNet 제약을 무시한 코드가 생성되기 때문입니다.

> 플랜 선택의 핵심은 가장 싼 플랜을 찾는 것이 아니라, 워크로드가 감당할 수 없는 제약(OS, VNet, 콜드 스타트, 슬롯)을 가진 플랜을 먼저 제거하는 것입니다.

---

## 이 글에서 다룰 문제

- Consumption, Flex Consumption, Premium, Dedicated는 각각 어떤 제약과 강점이 있을까요?
- OS, VNet, 콜드 스타트 중 어떤 순서로 후보를 좁혀야 할까요?
- "새 앱은 Flex가 권장된다"는 말에 어떤 단서가 붙어야 할까요?
- Premium의 warm capacity 비용과 Flex의 Always Ready 비용은 어떻게 다를까요?
- 이 개념을 실무에 적용하는 방법은 무엇일까요?

플랜 선택 기준을 이해하면 AI에게 "VNet 통합 필수 + Linux + 콜드 스타트 허용 가능 조건에서 Flex Consumption으로 Function App 생성하는 az CLI, Always Ready 0으로 scale-to-zero 활성화"를 정확하게 요청할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "Azure Functions 플랜 설정해줘"
→ 기본값 Consumption 적용
→ VNet 통합 필요성 미고려
→ Blob trigger 제약 미확인
→ 콜드 스타트 허용 범위 미설정
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "Azure Functions 플랜을 조건에 맞게 선택하고 설정해줘.
    조건:
    - Linux 전용 (Windows 불필요)
    - VNet 통합 필수 (private DB 접근)
    - 콜드 스타트: 수 초 허용 가능
    - Blob trigger 미사용
    → Flex Consumption 선택
    설정: instance-memory 2048, maximum-instance-count 100
    Always Ready 0 (scale-to-zero 활성화)
    az CLI 명령과 이유 설명 포함"
→ OS/VNet/콜드스타트 기준 후보 축소
→ 선택 이유 명시
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| Windows 필요 없는데 Consumption 사용 (Linux 미지원) | Linux Consumption은 Retired 상태 | 신규 Linux 앱은 Flex Consumption 사용 |
| VNet 통합 필요한데 classic Consumption 사용 | Consumption에는 VNet 통합 없음 | VNet 필수면 Flex/Premium/Dedicated 선택 |
| "Flex면 항상 warm하다" 오해 | Always Ready 0이면 scale-to-zero 발생, 콜드 스타트 가능 | Always Ready 설정값과 콜드 스타트 허용 범위를 함께 결정 |
| Blob trigger와 Flex Consumption 조합 시도 | Flex는 Event Grid 기반 Blob trigger만 지원 | 기존 Blob trigger 코드는 Consumption 또는 Premium 사용 |
| 플랜을 비용 표로만 비교 | VNet, Blob trigger, 슬롯 기능 제약이 먼저 후보를 좁힘 | OS → VNet → 콜드 스타트 순서로 제약 필터링 후 비용 비교 |

## AI 협업 팁

플랜 선택 관련 효과적인 AI 프롬프트 패턴:

1. **플랜 선택 판단 요청**: "VNet 통합 필수, Linux, 콜드 스타트 수 초 허용 조건에서 Flex/Premium/Consumption 중 어떤 플랜이 맞는지 제약 기준으로 설명해줘"
2. **Flex Consumption 생성 요청**: "VNet 통합 Flex Consumption Function App을 Python 3.11, instance-memory 2048, VNet 연결 포함해서 생성하는 az CLI 작성해줘"
3. **Always Ready 설정 요청**: "Flex Consumption에서 핵심 함수 경로만 Always Ready 1로 예열하고 나머지는 scale-to-zero 유지하는 설정 작성해줘"

예시 프롬프트:
> "Azure Functions 플랜 선택 및 설정 명령 작성해줘. 조건: Linux, VNet 통합 필수, 콜드 스타트 수 초 허용. 결론: Flex Consumption. az functionapp create로 memory 2048, max-instances 100, VNet 통합 포함. Always Ready 0 (scale-to-zero). 선택 이유도 설명."

## 운영 체크리스트

- [ ] OS(Windows/Linux) 요구사항을 먼저 확인하고 플랜 후보를 좁혔는가?
- [ ] VNet 통합 필요 여부를 플랜 선택 1차 필터로 사용했는가?
- [ ] 콜드 스타트 허용 범위에 맞게 Always Ready 설정을 결정했는가?
- [ ] Blob trigger 사용 시 Flex의 Event Grid 기반 제약을 확인했는가?
- [ ] 다음 글에서 스케일링과 콜드 스타트의 두 축을 이해할 준비가 됐는가?

## 처음 질문으로 돌아가기

플랜 선택 기준을 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. OS/VNet/콜드 스타트 제약 기준을 명시한 사람과 그렇지 않은 사람이 AI에게 받는 플랜 설정 코드의 완성도는 크게 다릅니다.

## 정리

플랜 선택 편은 바이브코딩을 위한 Azure Functions에서 운영 trade-off를 이해하는 핵심 단계입니다. Consumption(레거시)/Flex(새 기본 후보)/Premium(warm capacity)/Dedicated(App Service 방식)의 OS, VNet, 콜드 스타트, 슬롯 제약을 이해했습니다. 다음 글에서는 선택한 플랜이 실제 스케일링과 콜드 스타트에서 어떻게 동작하는지 다룹니다.

## 참고 자료

- [Azure Functions Flex Consumption plan hosting](https://learn.microsoft.com/azure/azure-functions/flex-consumption-plan)
- [Function scale and hosting options](https://learn.microsoft.com/azure/azure-functions/functions-scale)
- [Azure Functions Premium plan](https://learn.microsoft.com/azure/azure-functions/functions-premium-plan)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-functions-101/ko/05-choosing-a-plan)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Azure Functions (1/7): Azure Functions란?
- 바이브코딩을 위한 Azure Functions (2/7): 트리거와 바인딩
- 바이브코딩을 위한 Azure Functions (3/7): Host와 Worker
- 바이브코딩을 위한 Azure Functions (4/7): 함수 하나 배포하기
- **바이브코딩을 위한 Azure Functions (5/7): 어떤 플랜을 선택해야 할까 (현재 글)**
- 바이브코딩을 위한 Azure Functions (6/7): 스케일링과 콜드 스타트
- 바이브코딩을 위한 Azure Functions (7/7): 모니터링과 운영 기초
<!-- toc:end -->

Tags: 바이브코딩, AzureFunctions, Serverless, AI코딩
