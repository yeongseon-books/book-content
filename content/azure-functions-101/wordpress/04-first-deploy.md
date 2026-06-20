---
title: "바이브코딩을 위한 Azure Functions (4/7): 함수 하나 배포하기"
series: azure-functions-101
episode: 4
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- AzureFunctions
- Serverless
- AI코딩
seo_description: "바이브코딩을 위한 Azure Functions 4편: 함수 하나 배포하기. 로컬 함수를 Azure까지 배포하는 흐름에서 Storage Account 역할, App Settings 분리, Flex Consumption 선택을 이해합니다."
---

# 바이브코딩을 위한 Azure Functions (4/7): 함수 하나 배포하기

이 글은 바이브코딩을 위한 Azure Functions 시리즈의 4번째 글입니다.

Azure Functions 배포는 "코드를 서버에 복사한다"는 느낌보다 로컬에서 확인한 Functions 실행 환경을 Azure의 Function App 리소스로 옮기는 과정에 가깝습니다. 함수만 올라가는 것이 아니라, 실행 모델 전체가 클라우드로 이전됩니다. Function App만 만들면 끝나는 것이 아니라 Storage Account라는 필수 인프라가 필요합니다. Storage Account는 비즈니스 데이터 저장소가 아니라 Functions 플랫폼 자체의 상태 유지에 필요합니다. 트리거 락, invocation 메타데이터, Timer 스케줄 상태가 여기에 들어갑니다. local.settings.json에 있던 설정은 배포해 주는 것이 아니라, 같은 역할의 App Settings를 Azure에 다시 구성해야 합니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI에게 Functions 배포 코드를 요청할 때 세 층(프로젝트, Azure 리소스, 설정)을 명시하지 않으면, Storage Account 없이 Function App만 만들거나, local.settings.json 설정을 App Settings로 마이그레이션하지 않는 배포 코드가 생성되기 때문입니다.

> 함수 배포의 핵심은 프로젝트, Azure 리소스(Resource Group/Storage Account/Function App), 설정 계층(local.settings.json → App Settings)이라는 세 층을 분리해서 이해하는 데 있습니다.

---

## 이 글에서 다룰 문제

- Function App을 만들기 전에 어떤 Azure 리소스가 필수인가요?
- Storage Account는 왜 Functions 필수 인프라인가요?
- local.settings.json과 Azure App Settings는 어떤 관계인가요?
- Flex Consumption을 기본 출발점으로 잡는 이유는 무엇인가요?
- 이 개념을 실무에 적용하는 방법은 무엇일까요?

Functions 배포 흐름을 이해하면 AI에게 "Python v2 함수 프로젝트 생성, Resource Group/Storage Account/Flex Consumption Function App 생성, local.settings.json을 App Settings로 마이그레이션, func azure functionapp publish 배포 명령"을 정확하게 요청할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "Azure Functions 배포해줘"
→ Function App만 생성 (Storage Account 누락)
→ local.settings.json을 배포 파일에 포함 시도
→ Consumption plan vs Flex Consumption 구분 없음
→ 배포 성공 후 App Settings 미설정으로 함수 실패
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "Azure Functions Python v2 배포 az CLI 명령 작성해줘.
    1) 필수 리소스: Resource Group, Storage Account(플랫폼 인프라),
       Flex Consumption Function App (Python 3.11, instance-memory 2048)
    2) 설정 계층: local.settings.json의 StorageConnection,
       CosmosConnection을 App Settings로 마이그레이션
    3) 배포: func azure functionapp publish --build remote
    배포 후 함수 목록과 URL 확인 명령 포함"
→ 세 층(리소스/설정/코드) 분리 명확
→ 배포 후 검증 명령 포함
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| Function App만 생성, Storage Account 누락 | Functions 플랫폼 자체가 동작하지 않음 | Resource Group → Storage Account → Function App 순서로 생성 |
| local.settings.json을 배포 파일로 오해 | Azure 환경에서는 App Settings를 별도 구성해야 함 | az functionapp config appsettings set으로 App Settings 설정 |
| Storage Account를 비즈니스 데이터 저장소로 사용 | 플랫폼 인프라 용도와 충돌 | 비즈니스 데이터는 별도 Storage Account 사용 |
| 배포 성공 = 운영 준비 완료로 오해 | 인증, 관측, 롤백 경로가 아직 남아 있음 | 배포 후 Application Insights 연결, 알람 설정 추가 |
| Flex Consumption과 Consumption 차이 미고려 | 새 앱에서 VNet, 메모리 선택, scale 차이 발생 | 신규 앱은 Flex Consumption 먼저 검토 |

## AI 협업 팁

Functions 배포 관련 효과적인 AI 프롬프트 패턴:

1. **리소스 생성 요청**: "Azure Functions Python v2 배포를 위한 Resource Group, Storage Account, Flex Consumption Function App 생성 az CLI 명령 작성해줘"
2. **App Settings 마이그레이션 요청**: "local.settings.json의 StorageConnection, CosmosConnection을 Azure App Settings로 마이그레이션하는 az CLI 명령 작성해줘"
3. **배포 후 검증 요청**: "func azure functionapp publish 배포 후 함수 목록, URL, App Settings를 확인하는 명령 작성해줘"

예시 프롬프트:
> "Azure Functions Python v2 배포 전체 흐름 az CLI로 작성해줘. 1) RG+Storage Account+Flex Consumption(Python 3.11, memory 2048) 생성 2) StorageConnection/CosmosConnection App Settings 설정 3) func azure functionapp publish --build remote 배포 4) 배포 후 함수 URL 확인."

## 운영 체크리스트

- [ ] Resource Group → Storage Account → Function App 순서로 필수 리소스를 생성했는가?
- [ ] local.settings.json 설정을 Azure App Settings로 마이그레이션했는가?
- [ ] Storage Account 이름의 전역 고유 제약을 확인했는가?
- [ ] 배포 후 Application Insights를 연결하고 기본 관측 경로를 확보했는가?
- [ ] 다음 글에서 Flex/Premium/Dedicated 플랜을 워크로드 기준으로 선택하는 방법을 이해할 준비가 됐는가?

## 처음 질문으로 돌아가기

Functions 배포 흐름을 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. 세 층(리소스/설정/코드)을 명시한 사람과 그렇지 않은 사람이 AI에게 받는 배포 스크립트의 완성도는 크게 다릅니다.

## 정리

함수 하나 배포하기 편은 바이브코딩을 위한 Azure Functions에서 개념을 실제 배포로 연결하는 핵심 단계입니다. Storage Account 필수 인프라, local.settings.json과 App Settings의 관계, Flex Consumption 기본 출발점을 이해했습니다. 다음 글에서는 Consumption/Flex/Premium/Dedicated 플랜을 워크로드 기준으로 선택하는 방법을 다룹니다.

## 참고 자료

- [Azure Functions Core Tools](https://learn.microsoft.com/azure/azure-functions/functions-run-local)
- [Azure Functions Flex Consumption plan hosting](https://learn.microsoft.com/azure/azure-functions/flex-consumption-plan)
- [Run from package deployment](https://learn.microsoft.com/azure/azure-functions/run-functions-from-deployment-package)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-functions-101/ko/04-first-deploy)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Azure Functions (1/7): Azure Functions란?
- 바이브코딩을 위한 Azure Functions (2/7): 트리거와 바인딩
- 바이브코딩을 위한 Azure Functions (3/7): Host와 Worker
- **바이브코딩을 위한 Azure Functions (4/7): 함수 하나 배포하기 (현재 글)**
- 바이브코딩을 위한 Azure Functions (5/7): 어떤 플랜을 선택해야 할까
- 바이브코딩을 위한 Azure Functions (6/7): 스케일링과 콜드 스타트
- 바이브코딩을 위한 Azure Functions (7/7): 모니터링과 운영 기초
<!-- toc:end -->

Tags: 바이브코딩, AzureFunctions, Serverless, AI코딩
