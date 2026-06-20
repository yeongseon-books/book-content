---
title: "바이브코딩을 위한 Azure Functions (3/7): Host와 Worker"
series: azure-functions-101
episode: 3
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- AzureFunctions
- Serverless
- AI코딩
seo_description: "바이브코딩을 위한 Azure Functions 3편: Host와 Worker. Host가 트리거를 감지하고 gRPC로 Worker에 호출을 넘기는 두 프로세스 구조와 계층별 장애 진단을 이해합니다."
---

# 바이브코딩을 위한 Azure Functions (3/7): Host와 Worker

이 글은 바이브코딩을 위한 Azure Functions 시리즈의 3번째 글입니다.

Python, Node.js, Java로 함수를 작성하는데 Azure Functions Host 자체는 .NET으로 작성되어 있습니다. 이 두 언어가 어떻게 연결되는지 모르면, 로컬 실행과 Azure 배포가 무엇을 실제로 띄우는지, 장애가 났을 때 어디 로그를 봐야 하는지, 스케일아웃 시 어떤 프로세스가 늘어나는지가 전부 흐릿하게 남습니다. Azure Functions는 Host 프로세스와 언어별 Worker 프로세스를 분리해 띄우고, 둘은 gRPC로 대화합니다. Host는 트리거 감지, 바인딩 해석, 스케일 신호, 로깅을 담당하고 Worker는 실제 사용자 코드를 언어 런타임에서 실행합니다. 서비스 Bus 연결 문제는 Host 쪽 로그에서 먼저 드러나고, Python 코드의 무한 루프나 import 오류는 Worker 쪽에서 먼저 보입니다. 같은 "함수가 안 돈다"는 현상도 원인 층이 완전히 다를 수 있습니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI에게 Functions 진단 코드를 요청할 때 Host/Worker 구조를 명시하지 않으면, 모든 문제를 앱 코드 문제로 가정하거나 프로세스 로컬 캐시를 전역 공유라고 오해하는 코드가 생성되기 때문입니다.

> Host와 Worker의 핵심은 Host=플랫폼 오케스트레이션(트리거, 바인딩, 스케일), Worker=언어 코드 실행이라는 역할 분리와, 인스턴스 스케일아웃 시 각 인스턴스가 자기 Host와 Worker를 따로 가진다는 구조를 이해하는 데 있습니다.

---

## 이 글에서 다룰 문제

- Functions Host와 언어 Worker는 왜 분리된 프로세스일까요?
- Host와 Worker 사이의 gRPC 채널에서는 어떤 메시지 흐름이 오갈까요?
- 스케일아웃 시 복제되는 것은 코드만이 아닌 이유는 무엇일까요?
- 장애 시 Host 쪽과 Worker 쪽 로그를 어떻게 구분해서 볼까요?
- 이 개념을 실무에 적용하는 방법은 무엇일까요?

Host와 Worker 구조를 이해하면 AI에게 "Functions 함수 실패 진단 시 트리거 감지 전인지 후인지 먼저 구분, Host 로그(바인딩 확장, 연결 오류)와 Worker 로그(import 오류, 앱 예외)를 계층별로 탐색하는 진단 명령"을 정확하게 요청할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "Functions 함수가 실패하는데 원인 찾는 방법?"
→ 무조건 앱 코드 로그부터 확인
→ Host/Worker 구조 모름
→ 트리거 감지 실패와 코드 실행 실패 구분 없음
→ 전역 캐시가 모든 인스턴스에서 공유된다고 가정
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "Functions 함수 실패를 Host/Worker 계층으로 진단해줘.
    1) 트리거 감지 전 실패:
       Host 로그에서 바인딩 확장 로드, 연결 문자열 오류 확인
    2) 트리거 감지 후 코드 실패:
       Worker 로그에서 import 오류, 앱 예외 확인
    3) 스케일아웃 시 인스턴스당 독립 캐시 주의
    az webapp log tail 명령과 Application Insights KQL 포함"
→ 계층별 장애 분류로 탐색 범위 절반 이하 축소
→ 캐시 전략 오해 방지
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| 모든 함수 실패를 앱 코드 문제로 가정 | 트리거 감지 실패, 바인딩 확장 오류는 Host 쪽 문제 | 트리거 감지 전/후 구분 후 Host/Worker 로그 분리 확인 |
| 전역 캐시가 모든 인스턴스에서 공유된다고 가정 | 인스턴스마다 Host와 Worker가 독립적으로 실행됨 | 전역 캐시는 프로세스 로컬, 인스턴스 간 공유 상태는 외부 저장소 사용 |
| func start가 단순한 개발 서버라고 오해 | 로컬에서도 Host와 Worker가 실제로 분리 실행됨 | ps 명령으로 Host/Worker 두 프로세스 확인 |
| host.json을 단순 개발 설정 파일로 취급 | functionTimeout, maxConcurrentRequests 등 운영 행동을 바꿈 | host.json을 IaC로 관리하고 배포 검토에 포함 |
| Worker 동시성을 인스턴스 수로만 설명 | Python sync 함수는 thread pool, async는 event loop 특성이 다름 | FUNCTIONS_WORKER_PROCESS_COUNT와 concurrency 설정 함께 검토 |

## AI 협업 팁

Host/Worker 구조 관련 효과적인 AI 프롬프트 패턴:

1. **계층별 장애 진단 요청**: "Azure Functions 함수 실패 시 Host 로그(트리거/바인딩)와 Worker 로그(앱 코드)를 분리해서 확인하는 진단 명령 작성해줘"
2. **로컬 구조 확인 요청**: "func start 실행 후 Host와 Worker 두 프로세스가 분리 실행되는지 ps 명령으로 확인하는 방법 설명해줘"
3. **concurrency 설정 요청**: "Azure Functions Python에서 FUNCTIONS_WORKER_PROCESS_COUNT와 maxConcurrentRequests를 조합해 인스턴스당 동시성을 높이는 설정 작성해줘"

예시 프롬프트:
> "Azure Functions 함수 장애 진단 런북 작성해줘. 1) 트리거 감지 전(Host 로그: 바인딩 확장, 연결 오류) 2) 트리거 감지 후(Worker 로그: import 오류, 앱 예외) 3) 성능(인스턴스 동시성, Worker 프로세스 수). az webapp log tail 명령과 Application Insights KQL 포함."

## 운영 체크리스트

- [ ] Host 로그와 Worker 로그를 분리해서 볼 수 있는 관측 경로를 만들었는가?
- [ ] 장애 시 트리거 감지 전/후를 먼저 구분하는 진단 순서를 런북에 포함했는가?
- [ ] 전역 캐시가 인스턴스 로컬임을 이해하고 스케일아웃 전략을 설계했는가?
- [ ] host.json을 IaC로 관리하고 배포 파이프라인에 포함했는가?
- [ ] 다음 글에서 함수를 로컬에서 Azure까지 배포하는 흐름을 이해할 준비가 됐는가?

## 처음 질문으로 돌아가기

Host와 Worker 구조를 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. Host/Worker 계층 분리와 프로세스 로컬 캐시를 이해한 사람과 그렇지 않은 사람이 AI에게 받는 Functions 진단 코드와 캐시 설계의 완성도는 크게 다릅니다.

## 정리

Host와 Worker 편은 바이브코딩을 위한 Azure Functions에서 실행 구조를 이해하는 핵심 단계입니다. Host=플랫폼 오케스트레이션, Worker=언어 코드 실행이라는 gRPC 기반 두 프로세스 분리, 인스턴스별 독립 실행 구조를 이해했습니다. 다음 글에서는 로컬에서 Azure까지 함수를 배포하는 실제 흐름을 다룹니다.

## 참고 자료

- [Azure Functions runtime versions overview](https://learn.microsoft.com/azure/azure-functions/functions-versions)
- [.NET isolated worker model](https://learn.microsoft.com/azure/azure-functions/dotnet-isolated-process-guide)
- [azure-functions-host (GitHub)](https://github.com/Azure/azure-functions-host)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/azure-functions-101/ko/03-host-and-worker)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Azure Functions (1/7): Azure Functions란?
- 바이브코딩을 위한 Azure Functions (2/7): 트리거와 바인딩
- **바이브코딩을 위한 Azure Functions (3/7): Host와 Worker (현재 글)**
- 바이브코딩을 위한 Azure Functions (4/7): 함수 하나 배포하기
- 바이브코딩을 위한 Azure Functions (5/7): 어떤 플랜을 선택해야 할까
- 바이브코딩을 위한 Azure Functions (6/7): 스케일링과 콜드 스타트
- 바이브코딩을 위한 Azure Functions (7/7): 모니터링과 운영 기초
<!-- toc:end -->

Tags: 바이브코딩, AzureFunctions, Serverless, AI코딩
