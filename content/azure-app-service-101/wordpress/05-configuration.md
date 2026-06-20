---
title: "바이브코딩을 위한 Azure App Service (5/7): 설정 관리"
series: azure-app-service-101
episode: 5
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- AzureAppService
- 설정관리
- AppSettings
- AI코딩
seo_description: "바이브코딩을 위한 Azure App Service 5편: 설정 관리. App Settings, slot setting, Key Vault를 나눠 환경별 설정을 안전하게 관리하는 방법을 이해합니다."
---

# 바이브코딩을 위한 Azure App Service (5/7): 설정 관리

이 글은 바이브코딩을 위한 Azure App Service 시리즈의 5번째 글입니다.

앱 배포가 끝나면 바로 다음 문제가 시작됩니다. 환경마다 다른 연결 문자열, API 키, 로그 레벨을 어떻게 관리할지 정하지 않으면 배포는 끝나도 운영은 계속 흔들립니다. 코드에 하드코딩된 API 키가 Git에 올라가거나, dev 연결 문자열이 prod에 그대로 적용되는 실수는 이 단계에서 발생합니다. App Service의 App Settings는 런타임 환경변수로 주입되고, slot setting으로 표시된 값은 슬롯 간 스왑 시 이동하지 않습니다. 민감 정보는 App Settings에 직접 넣지 않고 Key Vault 참조로 관리하는 것이 운영 기준입니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI에게 App Service 설정 코드를 요청할 때 slot setting 구분과 Key Vault 참조를 명시하지 않으면, 스왑 시 민감 정보가 dev에서 prod로 따라가는 위험한 코드가 생성되기 때문입니다.

> 코드와 설정을 분리하고, 민감 정보와 환경별 값을 같은 바구니에 넣지 않는 것이 App Service 설정 관리의 핵심입니다.

---

## 이 글에서 다룰 문제

- App Settings와 환경변수는 어떻게 다르고 어떻게 오버라이드될까요?
- slot setting으로 표시해야 하는 값과 그렇지 않은 값은 어떻게 구분할까요?
- Key Vault 참조로 민감 정보를 관리할 때 권한 설정은 어떻게 해야 할까요?
- 자주 하는 실수와 그 해결책은 무엇일까요?
- 이 개념을 실무에 적용하는 방법은 무엇일까요?

설정 관리를 이해하면 AI에게 "App Settings로 환경 변수를 설정하고, 연결 문자열은 slot setting으로 표시하고, API 키는 Key Vault 참조로 주입하는 az CLI 스크립트"를 정확하게 요청할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "App Service에 환경변수 설정하는 방법 알려줘"
→ az webapp config appsettings set 하나만 알려줌
→ slot setting 구분 없음
→ 민감 정보를 평문으로 저장
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "App Service 설정을 세 가지로 나눠줘.
    1) 공통값(LOG_LEVEL)은 일반 App Settings
    2) 환경별 연결 문자열(DB_URL)은 slot-setting으로 표시
    3) API 키(OPENAI_KEY)는 Key Vault 참조(@Microsoft.KeyVault(VaultName=...))로 주입
    각각 az CLI 명령으로 작성해줘"
→ 스왑 안전한 slot setting
→ 민감 정보 Key Vault 분리
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| 연결 문자열을 일반 App Settings에 | 스왑 시 dev DB URL이 prod에 적용 가능 | 환경별 값은 slot-setting 플래그 필수 |
| API 키를 App Settings에 평문으로 | 포털 접근 가능한 모든 사람에게 노출 | Key Vault 참조로 민감 정보 분리 |
| 설정 변경 후 앱 재시작 없음 | 일부 설정은 재시작 없이 반영 안 됨 | 변경 후 az webapp restart 실행 |
| .env 파일을 배포 패키지에 포함 | 민감 정보가 코드 저장소에 포함 | .gitignore에 .env, App Settings로 관리 |
| 모든 환경에 같은 Key Vault 사용 | prod 시크릿이 dev에서 접근 가능 | 환경별 별도 Key Vault 사용 |

## AI 협업 팁

App Service 설정 관리 관련 효과적인 AI 프롬프트 패턴:

1. **App Settings 설정 요청**: "LOG_LEVEL=INFO, APP_ENV=production을 App Settings로 설정하는 az CLI 명령 작성해줘"
2. **slot setting 요청**: "DB_URL을 slot-setting으로 표시해 staging에서 production으로 스왑 시 DB 연결이 바뀌지 않게 하는 명령 작성해줘"
3. **Key Vault 통합 요청**: "Key Vault에서 OPENAI_KEY 시크릿을 App Service에 Key Vault 참조로 주입하고 Managed Identity로 권한을 부여하는 명령 작성해줘"

예시 프롬프트:
> "App Service 설정을 안전하게 구성하는 az CLI 스크립트를 작성해줘. LOG_LEVEL은 일반 appsetting, DB_CONNECTION_STRING은 slot-setting, OPENAI_API_KEY는 Key Vault 참조(@Microsoft.KeyVault 형식). Managed Identity로 Key Vault 접근 권한도 부여."

## 운영 체크리스트

- [ ] 환경별로 달라야 하는 값은 slot-setting으로 표시됐는가?
- [ ] API 키, 연결 문자열 패스워드는 Key Vault 참조로 관리하는가?
- [ ] .env 파일이 .gitignore에 포함됐는가?
- [ ] dev와 prod가 서로 다른 Key Vault를 사용하는가?
- [ ] 다음 글에서 이 설정 변경을 로그와 모니터링으로 추적할 준비가 됐는가?

## 처음 질문으로 돌아가기

설정 관리를 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. slot setting과 Key Vault 참조를 명시한 사람과 그렇지 않은 사람이 AI에게 받는 설정 코드의 보안 수준은 크게 다릅니다.

## 정리

설정 관리는 바이브코딩을 위한 Azure App Service에서 코드와 설정을 분리하고 민감 정보를 안전하게 다루는 핵심 운영 기준입니다. slot setting 구분, Key Vault 참조, Managed Identity 권한 부여를 이해했습니다. 다음 글에서는 이 설정 변경과 앱 동작을 로그와 모니터링으로 추적하는 방법을 다룹니다.

## 참고 자료

- [Configure app settings](https://docs.microsoft.com/azure/app-service/configure-common)
- [Key Vault references for App Service](https://docs.microsoft.com/azure/app-service/app-service-key-vault-references)
- [Managed identity for App Service](https://docs.microsoft.com/azure/app-service/overview-managed-identity)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-app-service-101/ko/05-configuration)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Azure App Service (1/7): App Service란 무엇인가
- 바이브코딩을 위한 Azure App Service (2/7): 요청 수명 주기
- 바이브코딩을 위한 Azure App Service (3/7): 호스팅 모델 선택
- 바이브코딩을 위한 Azure App Service (4/7): 첫 번째 배포
- **바이브코딩을 위한 Azure App Service (5/7): 설정 관리 (현재 글)**
- 바이브코딩을 위한 Azure App Service (6/7): 로그와 모니터링
- 바이브코딩을 위한 Azure App Service (7/7): 스케일링
<!-- toc:end -->

Tags: 바이브코딩, AzureAppService, 설정관리, AI코딩
