---
title: "바이브코딩을 위한 Azure App Service 심화 (3/6): Worker와 샌드박스"
series: azure-app-service-deep-dive
episode: 3
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- AzureAppService심화
- Worker
- 샌드박스
- AI코딩
seo_description: "바이브코딩을 위한 Azure App Service 심화 3편: Worker와 샌드박스. Windows 샌드박스와 Linux 컨테이너 경계의 차이와 실행 제약을 이해합니다."
---

# 바이브코딩을 위한 Azure App Service 심화 (3/6): Worker와 샌드박스

이 글은 바이브코딩을 위한 Azure App Service 심화 시리즈의 3번째 글입니다.

"로컬에서는 잘 되는데 App Service에서는 실패한다"는 말은 흔하지만, 원인은 생각보다 자주 프레임워크 내부가 아니라 실행 경계에 있습니다. Windows App Service에서는 sandbox가 OS 기능 접근, 라이브러리 호환성, 파일시스템 경로, 프로세스 생명주기를 바꾸는 실행 계약으로 작용합니다. Linux App Service에서는 같은 질문이 컨테이너 startup 계약과 /home 스토리지 의미론으로 옮겨갑니다. Worker를 포털의 인스턴스 수라는 추상어가 아니라, 사용자 코드가 실제로 갇혀 실행되는 경계로 이해해야 배포는 성공했는데 특정 라이브러리만 실패하는 문제를 올바르게 진단할 수 있습니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI에게 App Service 배포 코드를 요청할 때 OS와 샌드박스 제약을 명시하지 않으면, 로컬에서만 동작하는 가정을 그대로 가져오는 코드가 생성되기 때문입니다.

> Worker와 샌드박스의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

---

## 이 글에서 다룰 문제

- Windows 샌드박스와 Linux 컨테이너 경계는 어떻게 다를까요?
- 로컬에서 가능한 OS 기능이 App Service에서 제한되는 예시는 무엇일까요?
- /home 스토리지는 여러 인스턴스에서 어떻게 공유될까요?
- 자주 하는 실수와 그 해결책은 무엇일까요?
- 이 개념을 실무에 적용하는 방법은 무엇일까요?

Worker와 샌드박스를 이해하면 AI에게 "Linux App Service에서 /home 스토리지를 올바르게 사용하고 컨테이너 startup 제약을 고려한 초기화 코드"를 정확하게 요청할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "App Service에서 파일을 저장하는 코드 작성해줘"
→ 로컬 파일시스템 경로 하드코딩
→ 재시작 시 데이터 소실
→ 다중 인스턴스 동시 쓰기 위험
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "Linux App Service에서 파일을 안전하게 저장하는 코드를 작성해줘.
    /tmp는 인스턴스 재시작 시 소실되고
    /home은 여러 인스턴스가 공유하므로
    동시 쓰기 충돌을 피하기 위해 Azure Blob Storage를 사용해줘.
    임시 처리용 파일만 /tmp에 쓰는 패턴도 포함해줘"
→ 재시작에도 안전한 파일 처리
→ 다중 인스턴스 환경에 맞는 패턴
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| /tmp에 중요 데이터 저장 | 인스턴스 재시작 시 소실 | 영속 데이터는 Azure Blob Storage 사용 |
| /home에 동시 쓰기 | 여러 인스턴스가 공유하는 경로에서 충돌 | 읽기 전용 또는 고유 파일명으로 분리 |
| Windows 전용 라이브러리를 Linux에서 실행 | 런타임 에러, Python GDI 관련 패키지 등 | Linux 호환 패키지 사용 또는 OS 맞게 선택 |
| 프로세스 포크나 배경 데몬 시작 | 샌드박스에서 제한됨 | App Service WebJobs나 별도 리소스 사용 |
| 로컬 포트를 직접 열기 | 샌드박스 네트워크 제약으로 불가 | PORT 환경변수로 플랫폼이 지정한 포트 사용 |

## AI 협업 팁

Worker와 샌드박스 관련 효과적인 AI 프롬프트 패턴:

1. **안전한 파일 처리 요청**: "Linux App Service에서 임시 파일은 /tmp, 영속 파일은 Azure Blob Storage를 사용하는 파일 처리 클래스 작성해줘"
2. **샌드박스 제약 확인 요청**: "App Service Linux 컨테이너에서 외부 바이너리 실행, subprocess, 추가 포트 바인딩이 가능한지 확인하는 테스트 코드 작성해줘"
3. **다중 인스턴스 안전 설계 요청**: "여러 인스턴스가 동시에 실행될 때 /home 경로 파일 충돌을 피하는 패턴 작성해줘"

예시 프롬프트:
> "Linux App Service에서 이미지 처리 앱을 만들어줘. 업로드된 이미지를 /tmp에 임시 저장 후 처리하고 결과를 Azure Blob Storage에 영속 저장하는 패턴. 재시작 시 /tmp 파일 소실을 전제로 설계해줘."

## 운영 체크리스트

- [ ] 영속 데이터를 Azure Blob Storage나 Database에 저장하는가?
- [ ] /tmp 사용 시 재시작 소실을 전제로 설계됐는가?
- [ ] 여러 인스턴스가 동시에 /home에 쓰는 경우가 없는가?
- [ ] 앱이 사용하는 라이브러리가 대상 OS(Linux/Windows)와 호환되는가?
- [ ] 다음 글에서 배포와 Kudu의 내부 동작을 이해할 준비가 됐는가?

## 처음 질문으로 돌아가기

Worker와 샌드박스를 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. 실행 경계와 스토리지 의미론을 이해한 사람과 그렇지 않은 사람이 AI에게 받는 파일 처리 코드의 안전성은 크게 다릅니다.

## 정리

Worker와 샌드박스는 바이브코딩을 위한 Azure App Service 심화에서 사용자 코드가 실제로 갇혀 실행되는 경계를 이해하는 핵심 단계입니다. Windows/Linux 실행 제약 차이와 /tmp, /home, Blob Storage의 용도를 이해했습니다. 다음 글에서는 배포 artifact가 Worker에 도달하는 Kudu의 내부 경로를 다룹니다.

## 참고 자료

- [App Service sandbox overview](https://github.com/projectkudu/kudu/wiki/Azure-Web-App-sandbox)
- [App Service persistent storage](https://docs.microsoft.com/azure/app-service/configure-connect-to-azure-storage)
- [Linux containers in App Service](https://docs.microsoft.com/azure/app-service/configure-custom-container)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-app-service-deep-dive/ko/03-worker-and-sandbox)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Azure App Service 심화 (1/6): 플랫폼 아키텍처
- 바이브코딩을 위한 Azure App Service 심화 (2/6): Front-End와 ARR
- **바이브코딩을 위한 Azure App Service 심화 (3/6): Worker와 샌드박스 (현재 글)**
- 바이브코딩을 위한 Azure App Service 심화 (4/6): 배포와 Kudu
- 바이브코딩을 위한 Azure App Service 심화 (5/6): 스케일링 내부 동작
- 바이브코딩을 위한 Azure App Service 심화 (6/6): 콜드 스타트와 Warmup
<!-- toc:end -->

Tags: 바이브코딩, AzureAppService심화, Worker, AI코딩
