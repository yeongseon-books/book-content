# Series Index

이 문서는 전체 콘텐츠 시리즈의 목록과 발행 상태를 관리한다. 단일 출처는 [`series.yaml`](./series.yaml)이며, 본 문서는 사람이 읽기 쉬운 요약이다. 시리즈별 `series.yaml` 은 각 시리즈 디렉토리(`content/<series>/series.yaml`) 안에 article-level status 와 함께 들어 있다.

## Status Legend

| Status | Meaning |
| --- | --- |
| Planned | 기획 중 |
| Draft | 초안 작성 중 |
| Ready | 발행 준비 완료 |
| Published | 발행 완료 |
| Needs Update | 업데이트 필요 |

체크 표시 의미: `Pass` = 해당 변형(variant)이 존재함, `Plan` = 예정, 빈 칸 = 해당 없음.

---

## Azure

### Azure App Service 101 (`azure-app-service-101`)

App Service 입문자를 위한 7부작 가이드. 호스팅 모델, 설정, 로그, 스케일링까지.

| # | Title | KO | EN | Medium | MkDocs | eBook | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Azure App Service란? | Pass | Pass | Pass | Plan | Plan | Draft |
| 2 | Request lifecycle | Pass | Pass | Pass | Plan | Plan | Draft |
| 3 | Hosting models | Pass | Pass | Pass | Plan | Plan | Draft |
| 4 | First deploy | Pass | Pass | Pass | Plan | Plan | Draft |
| 5 | Configuration | Pass | Pass | Pass | Plan | Plan | Draft |
| 6 | Logging & monitoring | Pass | Pass | Pass | Plan | Plan | Draft |
| 7 | Scaling 101 | Pass | Pass | Pass | Plan | Plan | Draft |

### Azure App Service Deep Dive (`azure-app-service-deep-dive`)

App Service 내부 동작 분석 시리즈. Kudu, sandbox, 스케일링 내부.

| # | KO | EN | Medium | MkDocs | eBook | Status |
| --- | --- | --- | --- | --- | --- | --- |
| 1-N | Pass | Pass | Pass | Plan | Plan | Draft |

### Azure Functions 101 (`azure-functions-101`)

Azure Functions 입문자를 위한 7부작. 트리거/바인딩부터 콜드 스타트, 모니터링까지.

| # | KO | EN | Medium | MkDocs | eBook | Status |
| --- | --- | --- | --- | --- | --- | --- |
| 1-7 | Pass | Pass | Pass | Plan | Plan | Draft |

### Azure Functions Deep Dive (`azure-functions-deep-dive`)

Azure Functions Host 소스 분석 시리즈. Host bootstrap, Worker, gRPC, dispatcher, scaling, cold start.

| # | KO | EN | Medium | MkDocs | eBook | Status |
| --- | --- | --- | --- | --- | --- | --- |
| 1-N | Pass | Pass | Pass | Plan | Plan | Draft |

### Azure AKS 101 (`azure-aks-101`)

AKS 입문 시리즈. 클러스터/노드/워크로드 기본기.

| # | KO | EN | Medium | MkDocs | eBook | Status |
| --- | --- | --- | --- | --- | --- | --- |
| 1-N | Pass | Pass | Pass | Plan | Plan | Draft |

### Azure AKS Deep Dive (`azure-aks-deep-dive`)

AKS 내부 동작 분석.

| # | KO | EN | Medium | MkDocs | eBook | Status |
| --- | --- | --- | --- | --- | --- | --- |
| 1-N | Pass | Pass | Pass | Plan | Plan | Draft |

### Azure Container Apps 101 (`azure-aca-101`)

Container Apps 입문 시리즈.

| # | KO | EN | Medium | MkDocs | eBook | Status |
| --- | --- | --- | --- | --- | --- | --- |
| 1-N | Pass | Pass | Pass | Plan | Plan | Draft |

### Azure Container Apps Deep Dive (`azure-aca-deep-dive`)

Container Apps 내부 동작 (KEDA, Dapr, Envoy).

| # | KO | EN | Medium | MkDocs | eBook | Status |
| --- | --- | --- | --- | --- | --- | --- |
| 1-N | Pass | Pass | Pass | Plan | Plan | Draft |

---

## AI

### AI Web Dev 101 (`ai-web-dev-101`)

AI API부터 배포까지, 초급 개발자를 위한 7부작 (현재 한국어 단일 변형).

| # | Title | KO | EN | Medium | MkDocs | eBook | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | AI API 첫 걸음 | Pass | Plan | Plan | Plan | Plan | Needs Update |
| 2 | 프롬프트 엔지니어링 | Pass | Plan | Plan | Plan | Plan | Draft |
| 3 | AI 챗봇 만들기 | Pass | Plan | Plan | Plan | Plan | Draft |
| 4 | RAG 입문 | Pass | Plan | Plan | Plan | Plan | Draft |
| 5 | AI 에이전트 | Pass | Plan | Plan | Plan | Plan | Draft |
| 6 | 배포 (Vercel/Azure) | Pass | Plan | Plan | Plan | Plan | Draft |
| 7 | 평가와 개선 | Pass | Plan | Plan | Plan | Plan | Draft |

### LLM from Scratch 101 (`llm-from-scratch-101`)

PyTorch 2.x로 토크나이저부터 챗봇까지, 한 시리즈 동안 ~720 LOC 안에서 작은 GPT를 직접 만드는 9부작. TinyShakespeare, char-level vocab, ~1.2M 파라미터.

| # | Title | KO | EN | Medium | MkDocs | eBook | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 글자를 숫자로 바꾸기 | Pass | Pass | Pass | Plan | Plan | Draft |
| 2 | 정수에서 벡터로, 그리고 위치 | Pass | Pass | Pass | Plan | Plan | Draft |
| 3 | 어떤 토큰을 얼마나 볼지 스스로 정하기 | Pass | Pass | Pass | Plan | Plan | Draft |
| 4 | 블록 하나, 깊이의 단위 | Pass | Pass | Pass | Plan | Plan | Draft |
| 5 | 조립: GPT 모델 클래스 완성 | Pass | Pass | Pass | Plan | Plan | Draft |
| 6 | 기울기로 배우기 | Pass | Pass | Pass | Plan | Plan | Draft |
| 7 | 샘플링 — 학습된 모델에서 글 뽑아내기 | Pass | Pass | Pass | Plan | Plan | Draft |
| 8 | 베이스 모델을 우리 작업에 맞추기 | Pass | Pass | Pass | Plan | Plan | Draft |
| 9 | 직접 만든 LLM을 챗봇으로 — FastAPI + 스트리밍 | Pass | Pass | Pass | Plan | Plan | Draft |

---

## AX (Planned)

### AX Practical Guide (`ax-practical-guide`)

| # | Title | Status |
| --- | --- | --- |
| 1 | AX란 무엇인가 | Planned |
| 2 | AX와 업무 자동화 | Planned |
| 3 | AX 도입 전략 | Planned |

---

## Technical Writing (Planned)

### Technical Writing for Engineers (`technical-writing`)

| # | Title | Status |
| --- | --- | --- |
| 1-N | TBD | Planned |
