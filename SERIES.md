# Series Index

이 문서는 전체 콘텐츠 시리즈의 목록과 발행 상태를 관리한다. 단일 출처는 [`series.yaml`](./series.yaml) 이며, 본 문서는 `scripts/build_series_index.py` 가 자동 생성한다. 직접 편집 금지.

## Status Legend

| Status | Meaning |
| --- | --- |
| Planned | 기획 중 |
| Draft | 초안 작성 중 |
| Content Ready | 본문 작성 완료, 코드 검증 전 |
| Code Checked | 예제 코드 검증 완료 |
| Publish Ready | 발행 준비 완료 |
| Ready (legacy) | 발행 준비 완료 (legacy) |
| Published | 발행 완료 |
| Needs Update | 업데이트 필요 |

---

## AI

### LLM 앱 기초 / LLM App Foundations 101 (`llm-app-foundations-101`)

LLM API 기초, 토큰, 프롬프트 엔지니어링 — 6부작.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/llm-app-foundations-101/`](./content/llm-app-foundations-101/)

_articles not yet enumerated._

### LLM API 프로덕션 101 / LLM API Production 101 (`llm-api-production-101`)

Structured Output, Tool Calling, Streaming, Caching, Retry, Rate Limit — 6부작.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/llm-api-production-101/`](./content/llm-api-production-101/)

_articles not yet enumerated._

### 벡터 검색 101 / Vector Search 101 (`vector-search-101`)

임베딩, FAISS, 유사도, 청크 전략 — 6부작.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/vector-search-101/`](./content/vector-search-101/)

_articles not yet enumerated._

### LangChain 101 (`langchain-101`)

LCEL, Runnable, Retriever, Tool Calling 기본, Streaming — LangChain API 사용법 6부작.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/langchain-101/`](./content/langchain-101/)

_articles not yet enumerated._

### AI 앱 패턴 101 / AI App Patterns 101 (`ai-app-patterns-101`)

챗봇, RAG Q&A, 문서비서, Agent, Workflow, Human-in-the-loop — LLM 앱 설계 패턴 6부작.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/ai-app-patterns-101/`](./content/ai-app-patterns-101/)

_articles not yet enumerated._

### RAG Deep Dive (`rag-deep-dive`)

LangChain · FAISS · RAGAS 소스로 따라가는 RAG 파이프라인 심층 분석 6부작.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/rag-deep-dive/`](./content/rag-deep-dive/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | 문서 로딩과 청크 전략 — LangChain TextSplitter 내부 | [ko](./content/rag-deep-dive/ko/01-document-loading-and-chunking.md) | [en](./content/rag-deep-dive/en/01-document-loading-and-chunking.md) | — | Publish Ready |
| 2 | 임베딩과 벡터 인덱스 — FAISS IndexFlatL2 동작 원리 | [ko](./content/rag-deep-dive/ko/02-embeddings-and-vector-index.md) | [en](./content/rag-deep-dive/en/02-embeddings-and-vector-index.md) | — | Publish Ready |
| 3 | Retriever 설계 — VectorStoreRetriever와 MMR | [ko](./content/rag-deep-dive/ko/03-retriever-design.md) | [en](./content/rag-deep-dive/en/03-retriever-design.md) | — | Publish Ready |
| 4 | 프롬프트 구성과 컨텍스트 주입 — PromptTemplate 내부 | [ko](./content/rag-deep-dive/ko/04-prompt-construction-and-context-injection.md) | [en](./content/rag-deep-dive/en/04-prompt-construction-and-context-injection.md) | — | Publish Ready |
| 5 | RAG Chain 조립 — RetrievalQA vs LCEL | [ko](./content/rag-deep-dive/ko/05-rag-chain-assembly.md) | [en](./content/rag-deep-dive/en/05-rag-chain-assembly.md) | — | Publish Ready |
| 6 | 평가와 품질 게이트 — RAGAS 메트릭과 Faithfulness | [ko](./content/rag-deep-dive/ko/06-evaluation-and-quality-gates.md) | [en](./content/rag-deep-dive/en/06-evaluation-and-quality-gates.md) | — | Publish Ready |

### RAG 평가와 벤치마크 101 / RAG Evaluation and Benchmarking 101 (`rag-benchmark-101`)

RAG 품질 평가 6부작 — 평가 데이터셋, 임베딩/리트리버 비교, RAGAS, 의사결정 연결.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/rag-benchmark-101/`](./content/rag-benchmark-101/)

_articles not yet enumerated._

### 문서 수집과 인덱싱 101 / Document Ingestion 101 (`document-ingestion-101`)

PDF 파싱, 메타데이터, 증분 인덱싱 — 6부작.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/document-ingestion-101/`](./content/document-ingestion-101/)

_articles not yet enumerated._

### LangGraph 101 (`langgraph-101`)

그래프 에이전트, 체크포인트, 멀티에이전트 — 6부작.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/langgraph-101/`](./content/langgraph-101/)

_articles not yet enumerated._

### AI Agent 101 (`ai-agent-101`)

AI Agent의 개념부터 Context Engineering, Tool Use, Workflow, Multi-Agent, Evaluation, 운영까지 배우는 실전 입문 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/ai-agent-101/`](./content/ai-agent-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | AI Agent란 무엇인가? | [ko](./content/ai-agent-101/ko/01-what-is-an-ai-agent.md) | [en](./content/ai-agent-101/en/01-what-is-an-ai-agent.md) | — | Publish Ready |
| 2 | 컨텍스트 엔지니어링 | [ko](./content/ai-agent-101/ko/02-context-engineering.md) | [en](./content/ai-agent-101/en/02-context-engineering.md) | — | Publish Ready |
| 3 | Tool Use 기초 | [ko](./content/ai-agent-101/ko/03-tool-use-fundamentals.md) | [en](./content/ai-agent-101/en/03-tool-use-fundamentals.md) | — | Publish Ready |
| 4 | Agent Workflow 설계 | [ko](./content/ai-agent-101/ko/04-agent-workflow-design.md) | [en](./content/ai-agent-101/en/04-agent-workflow-design.md) | — | Publish Ready |
| 5 | Memory와 State | [ko](./content/ai-agent-101/ko/05-memory-and-state.md) | [en](./content/ai-agent-101/en/05-memory-and-state.md) | — | Publish Ready |
| 6 | Multi-Agent 시스템 | [ko](./content/ai-agent-101/ko/06-multi-agent-systems.md) | [en](./content/ai-agent-101/en/06-multi-agent-systems.md) | — | Publish Ready |
| 7 | Agent 평가 | [ko](./content/ai-agent-101/ko/07-agent-evaluation.md) | [en](./content/ai-agent-101/en/07-agent-evaluation.md) | — | Publish Ready |
| 8 | 에러 처리와 안정성 | [ko](./content/ai-agent-101/ko/08-error-handling-reliability.md) | [en](./content/ai-agent-101/en/08-error-handling-reliability.md) | — | Publish Ready |
| 9 | 운영 | [ko](./content/ai-agent-101/ko/09-production-operations.md) | [en](./content/ai-agent-101/en/09-production-operations.md) | — | Publish Ready |
| 10 | 첫 Agent 만들기 | [ko](./content/ai-agent-101/ko/10-building-first-agent.md) | [en](./content/ai-agent-101/en/10-building-first-agent.md) | — | Publish Ready |

### Harness Engineering 101 (`harness-engineering-101`)

AI Agent가 안정적으로 작업하도록 task, context, constraint, tool, test, feedback, approval, observability, production harness를 설계하는 입문 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/harness-engineering-101/`](./content/harness-engineering-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Harness Engineering이란 무엇인가? | [ko](./content/harness-engineering-101/ko/01-what-is-harness-engineering.md) | [en](./content/harness-engineering-101/en/01-what-is-harness-engineering.md) | — | Content Ready |
| 2 | Task Harness — 모호한 일을 실행 가능한 작업으로 바꾸기 | [ko](./content/harness-engineering-101/ko/02-task-harness.md) | [en](./content/harness-engineering-101/en/02-task-harness.md) | — | Content Ready |
| 3 | Context Harness — Agent에게 줄 정보와 숨길 정보 설계하기 | [ko](./content/harness-engineering-101/ko/03-context-harness.md) | [en](./content/harness-engineering-101/en/03-context-harness.md) | — | Content Ready |
| 4 | Constraint Harness — 규칙, 경계, 금지 행동 정의하기 | [ko](./content/harness-engineering-101/ko/04-constraint-harness.md) | [en](./content/harness-engineering-101/en/04-constraint-harness.md) | — | Content Ready |
| 5 | Tool Harness — Agent가 사용할 도구를 안전하게 설계하기 | [ko](./content/harness-engineering-101/ko/05-tool-harness.md) | [en](./content/harness-engineering-101/en/05-tool-harness.md) | — | Content Ready |
| 6 | Test Harness — 완료 조건을 테스트로 고정하기 | [ko](./content/harness-engineering-101/ko/06-test-harness.md) | [en](./content/harness-engineering-101/en/06-test-harness.md) | — | Content Ready |
| 7 | Feedback Loop — 실패를 고치게 만드는 반복 구조 | [ko](./content/harness-engineering-101/ko/07-feedback-loop.md) | [en](./content/harness-engineering-101/en/07-feedback-loop.md) | — | Content Ready |
| 8 | Approval Gate — 사람 승인이 필요한 지점 설계하기 | [ko](./content/harness-engineering-101/ko/08-approval-gate.md) | [en](./content/harness-engineering-101/en/08-approval-gate.md) | — | Content Ready |
| 9 | Observability — Agent 작업을 추적하고 재현하기 | [ko](./content/harness-engineering-101/ko/09-observability.md) | [en](./content/harness-engineering-101/en/09-observability.md) | — | Content Ready |
| 10 | Production Harness — 운영 가능한 Agent 작업 환경 만들기 | [ko](./content/harness-engineering-101/ko/10-production-harness.md) | [en](./content/harness-engineering-101/en/10-production-harness.md) | — | Content Ready |

### AI Evaluation 101 (`ai-evaluation-101`)

LLM 애플리케이션을 정량적으로 평가하는 방법을 배우는 입문 시리즈. 평가 데이터셋 설계, 자동 채점, LLM-as-judge, 회귀 테스트, A/B 비교, 운영 평가까지 다룹니다.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/ai-evaluation-101/`](./content/ai-evaluation-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | 왜 LLM 애플리케이션을 평가해야 하는가 | [ko](./content/ai-evaluation-101/ko/01-why-evaluate-llm-apps.md) | [en](./content/ai-evaluation-101/en/01-why-evaluate-llm-apps.md) | — | Content Ready |
| 2 | 평가 데이터셋 설계하기 | [ko](./content/ai-evaluation-101/ko/02-evaluation-dataset-design.md) | [en](./content/ai-evaluation-101/en/02-evaluation-dataset-design.md) | — | Content Ready |
| 3 | 결정적 지표 — Exact Match, BLEU, ROUGE | [ko](./content/ai-evaluation-101/ko/03-deterministic-metrics.md) | [en](./content/ai-evaluation-101/en/03-deterministic-metrics.md) | — | Content Ready |
| 4 | LLM-as-Judge — 모델로 모델을 평가하기 | [ko](./content/ai-evaluation-101/ko/04-llm-as-judge.md) | [en](./content/ai-evaluation-101/en/04-llm-as-judge.md) | — | Content Ready |
| 5 | Rubric 기반 채점 설계 | [ko](./content/ai-evaluation-101/ko/05-rubric-based-scoring.md) | [en](./content/ai-evaluation-101/en/05-rubric-based-scoring.md) | — | Content Ready |
| 6 | RAG 시스템 평가하기 | [ko](./content/ai-evaluation-101/ko/06-rag-evaluation.md) | [en](./content/ai-evaluation-101/en/06-rag-evaluation.md) | — | Content Ready |
| 7 | Agent 평가하기 — 단일 응답이 아닌 trajectory | [ko](./content/ai-evaluation-101/ko/07-agent-evaluation.md) | [en](./content/ai-evaluation-101/en/07-agent-evaluation.md) | — | Content Ready |
| 8 | 회귀 테스트 — 어제 잘 되던 게 오늘 망가지지 않게 | [ko](./content/ai-evaluation-101/ko/08-regression-testing.md) | [en](./content/ai-evaluation-101/en/08-regression-testing.md) | — | Content Ready |
| 9 | LLM A/B 테스팅 — 어느 prompt가 더 나은가 | [ko](./content/ai-evaluation-101/ko/09-ab-testing-llms.md) | [en](./content/ai-evaluation-101/en/09-ab-testing-llms.md) | — | Content Ready |
| 10 | 운영 환경에서의 지속적 평가 | [ko](./content/ai-evaluation-101/ko/10-production-evaluation.md) | [en](./content/ai-evaluation-101/en/10-production-evaluation.md) | — | Content Ready |

### AI Safety & Guardrails 101 (`ai-safety-guardrails-101`)

LLM 애플리케이션에 안전 장치를 적용하는 방법을 배우는 입문 시리즈. Prompt injection 방어, 출력 필터링, PII 감지, jailbreak 탐지, hallucination 방지, 감사 로깅까지 다룹니다.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/ai-safety-guardrails-101/`](./content/ai-safety-guardrails-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | AI Safety가 왜 중요한가 | [ko](./content/ai-safety-guardrails-101/ko/01-why-ai-safety-matters.md) | [en](./content/ai-safety-guardrails-101/en/01-why-ai-safety-matters.md) | — | Content Ready |
| 2 | Prompt Injection 방어 | [ko](./content/ai-safety-guardrails-101/ko/02-prompt-injection-defense.md) | [en](./content/ai-safety-guardrails-101/en/02-prompt-injection-defense.md) | — | Content Ready |
| 3 | 출력 필터링과 콘텐츠 모더레이션 | [ko](./content/ai-safety-guardrails-101/ko/03-output-filtering.md) | [en](./content/ai-safety-guardrails-101/en/03-output-filtering.md) | — | Content Ready |
| 4 | PII 감지와 마스킹 | [ko](./content/ai-safety-guardrails-101/ko/04-pii-detection-redaction.md) | [en](./content/ai-safety-guardrails-101/en/04-pii-detection-redaction.md) | — | Content Ready |
| 5 | Jailbreak 탐지 | [ko](./content/ai-safety-guardrails-101/ko/05-jailbreak-detection.md) | [en](./content/ai-safety-guardrails-101/en/05-jailbreak-detection.md) | — | Content Ready |
| 6 | 독성과 편향 탐지 | [ko](./content/ai-safety-guardrails-101/ko/06-toxicity-bias-detection.md) | [en](./content/ai-safety-guardrails-101/en/06-toxicity-bias-detection.md) | — | Content Ready |
| 7 | Hallucination Guardrail — Grounding 검증 | [ko](./content/ai-safety-guardrails-101/ko/07-hallucination-guardrails.md) | [en](./content/ai-safety-guardrails-101/en/07-hallucination-guardrails.md) | — | Content Ready |
| 8 | Rate Limiting과 남용 방지 | [ko](./content/ai-safety-guardrails-101/ko/08-rate-limiting-abuse-prevention.md) | [en](./content/ai-safety-guardrails-101/en/08-rate-limiting-abuse-prevention.md) | — | Content Ready |
| 9 | 감사 로깅과 컴플라이언스 | [ko](./content/ai-safety-guardrails-101/ko/09-audit-logging-compliance.md) | [en](./content/ai-safety-guardrails-101/en/09-audit-logging-compliance.md) | — | Content Ready |
| 10 | 운영 가드레일 시스템 구축 | [ko](./content/ai-safety-guardrails-101/ko/10-production-guardrail-system.md) | [en](./content/ai-safety-guardrails-101/en/10-production-guardrail-system.md) | — | Content Ready |

### LLM 앱 운영 101 / LLM Apps Ops 101 (`llm-apps-ops-101`)

관측, 평가, 비용, 보안, 배포 — 6부작.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/llm-apps-ops-101/`](./content/llm-apps-ops-101/)

_articles not yet enumerated._

### AI Data Preparation 101 (`ai-data-preparation-101`)

AI 모델을 위한 데이터 준비 전 과정을 다루는 입문 시리즈. 수집, 정제, PII 익명화, 토큰화, 품질 필터링, 합성 데이터, 분할과 오염 통제, 프로덕션 파이프라인까지 배웁니다.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/ai-data-preparation-101/`](./content/ai-data-preparation-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | 데이터 준비가 모델 품질을 결정하는 이유 | [ko](./content/ai-data-preparation-101/ko/01-why-data-preparation-matters.md) | [en](./content/ai-data-preparation-101/en/01-why-data-preparation-matters.md) | — | Draft |
| 2 | 원본 데이터 수집과 카탈로깅 | [ko](./content/ai-data-preparation-101/ko/02-source-data-collection-cataloging.md) | [en](./content/ai-data-preparation-101/en/02-source-data-collection-cataloging.md) | — | Draft |
| 3 | 데이터 정제와 중복 제거 | [ko](./content/ai-data-preparation-101/ko/03-cleaning-deduplication.md) | [en](./content/ai-data-preparation-101/en/03-cleaning-deduplication.md) | — | Draft |
| 4 | 학습 데이터 PII 탐지와 익명화 | [ko](./content/ai-data-preparation-101/ko/04-pii-detection-anonymization.md) | [en](./content/ai-data-preparation-101/en/04-pii-detection-anonymization.md) | — | Draft |
| 5 | Tokenization과 Chunking 전략 | [ko](./content/ai-data-preparation-101/ko/05-tokenization-chunking.md) | [en](./content/ai-data-preparation-101/en/05-tokenization-chunking.md) | — | Draft |
| 6 | 데이터 품질 필터링 — Heuristic과 Classifier | [ko](./content/ai-data-preparation-101/ko/06-quality-filtering.md) | [en](./content/ai-data-preparation-101/en/06-quality-filtering.md) | — | Draft |
| 7 | 합성 데이터 생성 — Self-Instruct부터 Distillation까지 | [ko](./content/ai-data-preparation-101/ko/07-synthetic-data-generation.md) | [en](./content/ai-data-preparation-101/en/07-synthetic-data-generation.md) | — | Draft |
| 8 | 데이터 증강 기법 — EDA부터 Back-Translation까지 | [ko](./content/ai-data-preparation-101/ko/08-data-augmentation.md) | [en](./content/ai-data-preparation-101/en/08-data-augmentation.md) | — | Draft |
| 9 | 학습/평가/테스트 분할과 Contamination 통제 | [ko](./content/ai-data-preparation-101/ko/09-train-eval-test-splitting.md) | [en](./content/ai-data-preparation-101/en/09-train-eval-test-splitting.md) | — | Draft |
| 10 | 프로덕션 데이터 파이프라인 구축 | [ko](./content/ai-data-preparation-101/ko/10-production-data-pipeline.md) | [en](./content/ai-data-preparation-101/en/10-production-data-pipeline.md) | — | Draft |

### LLM 파인튜닝 101 / LLM Fine-tuning 101 (`llm-finetuning-101`)

LoRA, 데이터셋, 서빙 — 6부작 (선택).

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/llm-finetuning-101/`](./content/llm-finetuning-101/)

_articles not yet enumerated._

### LLM from Scratch 101 (`llm-from-scratch-101`)

PyTorch 2.x 로 토크나이저부터 챗봇까지, ~720 LOC 의 작은 GPT 9부작.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/llm-from-scratch-101/`](./content/llm-from-scratch-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | 글자를 숫자로 바꾸기 | [ko](./content/llm-from-scratch-101/ko/01-tokenizer.md) | [en](./content/llm-from-scratch-101/en/01-tokenizer.md) | — | Code Checked |
| 2 | 정수에서 벡터로, 그리고 위치 | [ko](./content/llm-from-scratch-101/ko/02-embedding.md) | [en](./content/llm-from-scratch-101/en/02-embedding.md) | — | Code Checked |
| 3 | 어떤 토큰을 얼마나 볼지 스스로 정하기 | [ko](./content/llm-from-scratch-101/ko/03-attention.md) | [en](./content/llm-from-scratch-101/en/03-attention.md) | — | Code Checked |
| 4 | 블록 하나, 깊이의 단위 | [ko](./content/llm-from-scratch-101/ko/04-transformer-block.md) | [en](./content/llm-from-scratch-101/en/04-transformer-block.md) | — | Code Checked |
| 5 | 조립: GPT 모델 클래스 완성 | [ko](./content/llm-from-scratch-101/ko/05-gpt-model.md) | [en](./content/llm-from-scratch-101/en/05-gpt-model.md) | — | Code Checked |
| 6 | 기울기로 배우기 | [ko](./content/llm-from-scratch-101/ko/06-training-loop.md) | [en](./content/llm-from-scratch-101/en/06-training-loop.md) | — | Code Checked |
| 7 | 샘플링 — 학습된 모델에서 글 뽑아내기 | [ko](./content/llm-from-scratch-101/ko/07-inference.md) | [en](./content/llm-from-scratch-101/en/07-inference.md) | — | Code Checked |
| 8 | 베이스 모델을 우리 작업에 맞추기 | [ko](./content/llm-from-scratch-101/ko/08-finetuning.md) | [en](./content/llm-from-scratch-101/en/08-finetuning.md) | — | Code Checked |
| 9 | 직접 만든 LLM을 챗봇으로 — FastAPI + 스트리밍 | [ko](./content/llm-from-scratch-101/ko/09-chatbot-wrapper.md) | [en](./content/llm-from-scratch-101/en/09-chatbot-wrapper.md) | — | Code Checked |

### Multimodal AI 101 (`multimodal-ai-101`)

텍스트 + 이미지 + 오디오 + 영상을 다루는 multimodal AI 입문 시리즈. CLIP, ViT, VLM, Whisper, Diffusion, multimodal RAG, video understanding을 production 관점에서 배웁니다.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: —
- 경로: [`content/multimodal-ai-101/`](./content/multimodal-ai-101/)

| # | Title | KO | EN | Status |
| --- | --- | --- | --- | --- |
| 1 | Multimodal AI가 중요한 이유 | [ko](./content/multimodal-ai-101/ko/01-why-multimodal-matters.md) | [en](./content/multimodal-ai-101/en/01-why-multimodal-matters.md) | Content Ready |
| 2 | Image Encoder: CLIP과 ViT | [ko](./content/multimodal-ai-101/ko/02-image-encoders-clip-vit.md) | [en](./content/multimodal-ai-101/en/02-image-encoders-clip-vit.md) | Content Ready |
| 3 | Vision-Language Model 아키텍처 | [ko](./content/multimodal-ai-101/ko/03-vlm-architecture.md) | [en](./content/multimodal-ai-101/en/03-vlm-architecture.md) | Content Ready |
| 4 | Image Captioning과 OCR 파이프라인 | [ko](./content/multimodal-ai-101/ko/04-captioning-ocr-pipelines.md) | [en](./content/multimodal-ai-101/en/04-captioning-ocr-pipelines.md) | Content Ready |
| 5 | Multimodal RAG: 이미지와 텍스트를 함께 검색하기 | [ko](./content/multimodal-ai-101/ko/05-multimodal-rag.md) | [en](./content/multimodal-ai-101/en/05-multimodal-rag.md) | Content Ready |
| 6 | 오디오 처리와 Whisper STT | [ko](./content/multimodal-ai-101/ko/06-audio-whisper.md) | [en](./content/multimodal-ai-101/en/06-audio-whisper.md) | Content Ready |
| 7 | Diffusion으로 Text-to-Image 생성 | [ko](./content/multimodal-ai-101/ko/07-text-to-image-diffusion.md) | [en](./content/multimodal-ai-101/en/07-text-to-image-diffusion.md) | Content Ready |
| 8 | Multimodal Embedding과 Cross-modal 검색 | [ko](./content/multimodal-ai-101/ko/08-multimodal-embeddings.md) | [en](./content/multimodal-ai-101/en/08-multimodal-embeddings.md) | Content Ready |
| 9 | Video 이해 - Frame Sampling에서 Video-LLaVA까지 | [ko](./content/multimodal-ai-101/ko/09-video-understanding.md) | [en](./content/multimodal-ai-101/en/09-video-understanding.md) | Content Ready |
| 10 | Production Multimodal Application 구축 | [ko](./content/multimodal-ai-101/ko/10-production-multimodal-app.md) | [en](./content/multimodal-ai-101/en/10-production-multimodal-app.md) | Content Ready |

### 한국어 AI 스택 101 / Korean AI Stack 101 (`korean-ai-stack-101`)

한국어 임베딩, OCR, 국내 LLM API — 6부작.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/korean-ai-stack-101/`](./content/korean-ai-stack-101/)

_articles not yet enumerated._

### AI 웹 개발 입문 / AI Web Development 101 (`ai-web-dev-101`)

AI API 부터 배포까지, 초급 개발자를 위한 7부작.

- 상태: **Needs Update**
- 언어: ko
- 발행 대상: tistory, mkdocs, ebook
- 경로: [`content/ai-web-dev-101/`](./content/ai-web-dev-101/)

| # | Title | KO | Status |
| --- | --- | --- | --- |
| 1 | AI API 첫 걸음 — OpenAI API로 첫 번째 요청 보내기 | [ko](./content/ai-web-dev-101/ko/01-hello-ai-api.md) | Needs Update |
| 2 | 프롬프트 엔지니어링 기초 — AI에게 원하는 답을 얻는 기술 | [ko](./content/ai-web-dev-101/ko/02-prompt-engineering.md) | Needs Update |
| 3 | AI 챗봇 만들기 — Next.js와 Vercel AI SDK로 실시간 채팅 구현 | [ko](./content/ai-web-dev-101/ko/03-ai-chatbot.md) | Needs Update |
| 4 | RAG 입문 — 내 데이터로 답하는 AI 만들기 | [ko](./content/ai-web-dev-101/ko/04-rag-intro.md) | Needs Update |
| 5 | AI 에이전트 첫걸음 — Tool Use로 똑똑한 AI 만들기 | [ko](./content/ai-web-dev-101/ko/05-ai-agent.md) | Needs Update |
| 6 | AI 웹 앱 배포하기: Vercel과 Azure에 올리고 운영하기 | [ko](./content/ai-web-dev-101/ko/06-deploy.md) | Needs Update |
| 7 | AI 앱의 평가와 개선, 품질을 측정하고 더 좋게 만드는 법 | [ko](./content/ai-web-dev-101/ko/07-eval-improve.md) | Needs Update |

---

## Python

### Data Structures with Python 101 (`data-structures-python-101`)

Python으로 배우는 자료구조 입문. list, dict, set, deque, 트리, 힙, 그래프를 직접 구현합니다.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/data-structures-python-101/`](./content/data-structures-python-101/)

_articles not yet enumerated._

### Algorithms with Python 101 (`algorithms-python-101`)

Python 기반으로 시간 복잡도, 탐색, 정렬, DP, BFS/DFS, 그리디 등 알고리즘 기본기를 다지는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/algorithms-python-101/`](./content/algorithms-python-101/)

_articles not yet enumerated._

---

## CS 핵심 과목

### 컴퓨터학과 전공 학습 가이드 101 / Computer Science Major 101 (`computer-science-major-101`)

컴퓨터학과 전공 과목 구성, 핵심 영역, 학습 순서, 졸업 전 역량까지 정리한 입문 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/computer-science-major-101/`](./content/computer-science-major-101/)

_articles not yet enumerated._

### Discrete Math 101 (`discrete-math-101`)

명제, 집합, 함수, 증명, 조합, 그래프 등 컴퓨터공학에 직접 쓰이는 이산수학을 정리하는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/discrete-math-101/`](./content/discrete-math-101/)

_articles not yet enumerated._

### Math for CS 101 (`math-for-cs-101`)

논리, 증명, 집합, 함수, 그래프, 조합, 확률, 선형대수, 미분, 정보이론까지 CS와 ML의 수학을 한 번에 정리하는 입문 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/math-for-cs-101/`](./content/math-for-cs-101/)

_articles not yet enumerated._

### Calculus for ML 101 (`calculus-for-ml-101`)

함수, 기울기, 편미분, gradient, chain rule, 손실, 경사하강, backprop 직관까지 ML에 필요한 미분을 다지는 입문 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/calculus-for-ml-101/`](./content/calculus-for-ml-101/)

_articles not yet enumerated._

### Computer Architecture 101 (`computer-architecture-101`)

데이터 표현, CPU와 명령어, 레지스터, 메모리 계층, 캐시, 파이프라인, 멀티코어까지 컴퓨터가 코드를 실행하는 방식을 처음 배우는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/computer-architecture-101/`](./content/computer-architecture-101/)

_articles not yet enumerated._

### Data Structures 101 (`data-structures-101`)

배열, 리스트, 스택, 큐, 해시, 트리, 힙, 그래프까지 자료구조의 큰 그림과 선택 기준을 다루는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/data-structures-101/`](./content/data-structures-101/)

_articles not yet enumerated._

### Algorithms 101 (`algorithms-101`)

복잡도, 탐색, 정렬, 분할 정복, DP, 그리디, 그래프 알고리즘까지 알고리즘 설계 패턴을 배우는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/algorithms-101/`](./content/algorithms-101/)

_articles not yet enumerated._

### Programming Languages 101 (`programming-languages-101`)

syntax, semantics, type system, scope, closure, memory model, interpreter/compiler 차이까지 PL 기초를 다지는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/programming-languages-101/`](./content/programming-languages-101/)

_articles not yet enumerated._

### Operating Systems 101 (`operating-systems-101`)

프로세스, 스레드, 스케줄링, 동시성, 메모리 관리, 가상 메모리, 파일 시스템, 시스템 콜, 컨테이너까지 운영체제의 기본 개념을 다지는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/operating-systems-101/`](./content/operating-systems-101/)

_articles not yet enumerated._

### Computer Networks 101 (`computer-networks-101`)

IP, TCP, UDP, DNS, HTTP, TLS, 라우팅, 로드밸런서, WebSocket까지 인터넷 동작의 핵심을 정리하는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/computer-networks-101/`](./content/computer-networks-101/)

_articles not yet enumerated._

### Database Systems 101 (`database-systems-101`)

관계형 모델, SQL, 인덱스, 트랜잭션, isolation, 정규화, 쿼리 최적화, 복제까지 DBMS의 핵심을 다루는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/database-systems-101/`](./content/database-systems-101/)

_articles not yet enumerated._

### Distributed Systems 101 (`distributed-systems-101`)

failure model, consistency, replication, consensus, message queue까지 분산 시스템의 핵심 개념을 처음 배우는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/distributed-systems-101/`](./content/distributed-systems-101/)

_articles not yet enumerated._

### Compilers 101 (`compilers-101`)

lexer, parser, AST, semantic analysis, IR, optimization, code generation까지 컴파일러 파이프라인을 처음 배우는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/compilers-101/`](./content/compilers-101/)

_articles not yet enumerated._

### Information Security 101 (`information-security-101`)

인증, 인가, 암호화, TLS, 웹 보안, secret 관리, 권한 최소화, 감사 로그까지 개발자 수준의 보안 기본을 다루는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/information-security-101/`](./content/information-security-101/)

_articles not yet enumerated._

---

## 소프트웨어 엔지니어링

### Software Engineering 101 (`software-engineering-101`)

요구사항, 설계, 코드 리뷰, 테스트, 버전 관리, 문서화, 협업, 유지보수까지 소프트웨어 엔지니어링의 큰 그림을 다지는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/software-engineering-101/`](./content/software-engineering-101/)

_articles not yet enumerated._

### Clean Code 101 (`clean-code-101`)

이름 짓기, 함수 분리, 조건문 단순화, 중복 제거, 오류 처리부터 리팩토링 기초까지 읽기 쉬운 코드를 쓰는 법을 다지는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/clean-code-101/`](./content/clean-code-101/)

_articles not yet enumerated._

### Software Design 101 (`software-design-101`)

관심사 분리, 모듈 경계, 의존성 방향, 인터페이스 설계, 계층 아키텍처를 통해 변경에 강한 코드를 설계하는 법을 다지는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/software-design-101/`](./content/software-design-101/)

_articles not yet enumerated._

### Design Patterns 101 (`design-patterns-101`)

GoF 디자인 패턴을 Python 예시로 빠르게 훑고, 언제 쓰고 언제 피해야 할지 감을 잡는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/design-patterns-101/`](./content/design-patterns-101/)

_articles not yet enumerated._

### API Design 101 (`api-design-101`)

REST 기본부터 리소스 설계, HTTP method/status, schema, pagination, error, OpenAPI까지 쓰기 좋은 API를 설계하는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/api-design-101/`](./content/api-design-101/)

_articles not yet enumerated._

### Web Development 101 (`web-development-101`)

HTML/CSS/JS, 브라우저, HTTP, 프론트/백엔드, 인증, DB, 배포까지 웹 개발 전체 흐름을 한 번에 보는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/web-development-101/`](./content/web-development-101/)

_articles not yet enumerated._

### Frontend Development 101 (`frontend-development-101`)

HTML/CSS, JavaScript, 컴포넌트, 라우팅, API 호출, 빌드까지 현대 프론트엔드 개발 전체 흐름을 다루는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/frontend-development-101/`](./content/frontend-development-101/)

_articles not yet enumerated._

### Backend Development 101 (`backend-development-101`)

HTTP 서버/라우팅/서비스/DB layer/인증/로깅/테스트/배포까지 백엔드 개발 전체 흐름을 다루는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/backend-development-101/`](./content/backend-development-101/)

_articles not yet enumerated._

### Testing 101 (`testing-101`)

Unit, Integration, E2E, Test Double, Mock, Coverage, CI 연동까지 테스트 전략 전반을 다루는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/testing-101/`](./content/testing-101/)

_articles not yet enumerated._

### Containers 101 (`containers-101`)

Image, runtime, layer, Dockerfile부터 보안까지 컨테이너의 큰 그림을 입문자 관점에서 다룹니다.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/containers-101/`](./content/containers-101/)

_articles not yet enumerated._

### Docker 101 (`docker-101`)

Image, Container, Dockerfile, Volume, Network, Compose, 환경 설정, Python 앱 컨테이너화, 이미지 최적화, 배포 구성을 다루는 입문 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/docker-101/`](./content/docker-101/)

_articles not yet enumerated._

### Kubernetes 101 (`kubernetes-101`)

Pod, Deployment, Service, Ingress, ConfigMap/Secret, Volume, HPA, Helm까지 Kubernetes 기본 객체를 다루는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/kubernetes-101/`](./content/kubernetes-101/)

_articles not yet enumerated._

### Cloud Computing 101 (`cloud-computing-101`)

IaaS/PaaS/SaaS, 리전, 컴퓨트, 스토리지, 네트워크, 아이덴티티, 모니터링, 비용까지 클라우드 입문 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/cloud-computing-101/`](./content/cloud-computing-101/)

_articles not yet enumerated._

### Serverless 101 (`serverless-101`)

FaaS, trigger/event, cold start, scaling, state, queue, observability, cost까지 서버리스 입문 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/serverless-101/`](./content/serverless-101/)

_articles not yet enumerated._

### DevOps 101 (`devops-101`)

CI/CD, IaC, 환경 관리, 모니터링, 배포 전략, on-call까지 DevOps 입문 전반을 다루는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/devops-101/`](./content/devops-101/)

_articles not yet enumerated._

### GitHub Actions 101 (`github-actions-101`)

Workflow, Job, Trigger, 테스트 자동화, 빌드 아티팩트, 배포, secret 관리까지 GitHub Actions 전반을 다루는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/github-actions-101/`](./content/github-actions-101/)

_articles not yet enumerated._

### Observability 101 (`observability-101`)

Metric, log, trace, dashboard, alert, SLO 기초까지 운영 시스템의 가시성을 만드는 입문 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/observability-101/`](./content/observability-101/)

_articles not yet enumerated._

### Incident Response 101 (`incident-response-101`)

Severity 분류, 초기 대응, 커뮤니케이션, 타임라인, RCA, 완화, 포스트모템, 재발 방지, 런북 작성까지 다루는 입문 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/incident-response-101/`](./content/incident-response-101/)

_articles not yet enumerated._

### SRE 101 (`sre-101`)

신뢰성, SLI/SLO/SLA, 에러 버짓, 인시던트와 포스트모템, toil 감소, 용량 계획까지 다루는 SRE 입문 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/sre-101/`](./content/sre-101/)

_articles not yet enumerated._

### Secure Coding 101 (`secure-coding-101`)

입력 검증, 인증, 인가, secret 관리, SQL Injection, XSS/CSRF, dependency 취약점, 안전한 로깅까지 시큐어 코딩 입문 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/secure-coding-101/`](./content/secure-coding-101/)

_articles not yet enumerated._

### 오픈소스 101 / Open Source 101 (`open-source-101`)

라이선스부터 첫 오픈소스 프로젝트까지, 오픈소스 기여의 기본을 다지는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/open-source-101/`](./content/open-source-101/)

_articles not yet enumerated._

### Developer Career 101 (`developer-career-101`)

개발자 커리어를 설계하는 법.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/developer-career-101/`](./content/developer-career-101/)

_articles not yet enumerated._

### Data Science Career 101 (`data-science-career-101`)

데이터 직무 커리어를 설계하는 법.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/data-science-career-101/`](./content/data-science-career-101/)

_articles not yet enumerated._

### 포트폴리오 프로젝트 101 / Portfolio Project 101 (`portfolio-project-101`)

프로젝트 선정, README, 데모, 배포, 테스트, 의사결정 기록, 블로그, 면접 설명까지 다루는 입문 포트폴리오 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/portfolio-project-101/`](./content/portfolio-project-101/)

_articles not yet enumerated._

### 측스톤 프로젝트 101 / Capstone Project 101 (`capstone-project-101`)

주제 선정, 문제 정의, MVP, 팀 역할, 발표, 회고까지 측스톤 전체 흐름을 다룬 입문 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/capstone-project-101/`](./content/capstone-project-101/)

_articles not yet enumerated._

---

## 데이터 사이언스 / ML 기초

### Python DB-API 101 (`python-dbapi-101`)

Python의 표준 데이터베이스 인터페이스 PEP 249(DB-API 2.0)를 SQLite 기준으로 다루는 입문 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: —
- 경로: [`content/python-dbapi-101/`](./content/python-dbapi-101/)

| # | Title | KO | EN | Status |
| --- | --- | --- | --- | --- |
| 1 | 왜 DB-API 2.0인가 - PEP 249가 푼 문제 | [ko](./content/python-dbapi-101/ko/01-why-db-api-pep-249.md) | [en](./content/python-dbapi-101/en/01-why-db-api-pep-249.md) | Publish Ready |
| 2 | Connection과 Cursor Lifecycle | [ko](./content/python-dbapi-101/ko/02-connection-cursor-lifecycle.md) | [en](./content/python-dbapi-101/en/02-connection-cursor-lifecycle.md) | Publish Ready |
| 3 | execute, executemany, fetch 패턴 | [ko](./content/python-dbapi-101/ko/03-execute-fetch-patterns.md) | [en](./content/python-dbapi-101/en/03-execute-fetch-patterns.md) | Publish Ready |
| 4 | Parameter binding과 SQL injection 방어 (sqlite3, PEP 249) | [ko](./content/python-dbapi-101/ko/04-parameter-binding-sql-injection.md) | [en](./content/python-dbapi-101/en/04-parameter-binding-sql-injection.md) | Publish Ready |
| 5 | Transaction과 isolation level (sqlite3, PEP 249) | [ko](./content/python-dbapi-101/ko/05-transactions-isolation.md) | [en](./content/python-dbapi-101/en/05-transactions-isolation.md) | Publish Ready |
| 6 | Row factory와 type adapter (sqlite3, PEP 249) | [ko](./content/python-dbapi-101/ko/06-row-factories-adapters.md) | [en](./content/python-dbapi-101/en/06-row-factories-adapters.md) | Publish Ready |
| 7 | PEP 249 예외 계층과 SQLite 에러 처리 | [ko](./content/python-dbapi-101/ko/07-error-handling-exception-hierarchy.md) | [en](./content/python-dbapi-101/en/07-error-handling-exception-hierarchy.md) | Publish Ready |
| 8 | SQLite Connection 관리: thread-safety, check_same_thread, 그리고 풀링 | [ko](./content/python-dbapi-101/ko/08-connection-pooling.md) | [en](./content/python-dbapi-101/en/08-connection-pooling.md) | Publish Ready |
| 9 | aiosqlite로 비동기 SQLite 다루기 | [ko](./content/python-dbapi-101/ko/09-async-aiosqlite.md) | [en](./content/python-dbapi-101/en/09-async-aiosqlite.md) | Publish Ready |
| 10 | SQLite Production 패턴: retry, timeout, 관측성, 백업 | [ko](./content/python-dbapi-101/ko/10-production-patterns.md) | [en](./content/python-dbapi-101/en/10-production-patterns.md) | Publish Ready |

### SQLAlchemy 101 (`sqlalchemy-101`)

SQLAlchemy 2.x를 SQLite 기준으로 다루는 입문 시리즈. Engine·Connection·Core·ORM·Session·Unit of Work·Relationship·Loading 전략·Async·Production 패턴을 배웁니다.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: —
- 경로: [`content/sqlalchemy-101/`](./content/sqlalchemy-101/)

| # | Title | KO | EN | Status |
| --- | --- | --- | --- | --- |
| 1 | SQLAlchemy 2.x 시작하기 - Engine과 Connection의 본질 | [ko](./content/sqlalchemy-101/ko/01-sqlalchemy-2x-engine-connection.md) | [en](./content/sqlalchemy-101/en/01-sqlalchemy-2x-engine-connection.md) | Publish Ready |
| 2 | SQLAlchemy Core - MetaData, Table, Column으로 schema를 Python 객체로 만들기 | [ko](./content/sqlalchemy-101/ko/02-core-metadata-table-types.md) | [en](./content/sqlalchemy-101/en/02-core-metadata-table-types.md) | Publish Ready |
| 3 | SQLAlchemy Core - select·insert·update·delete를 2.x style로 다루기 | [ko](./content/sqlalchemy-101/ko/03-core-select-insert-update-delete.md) | [en](./content/sqlalchemy-101/en/03-core-select-insert-update-delete.md) | Publish Ready |
| 4 | ORM 기초: DeclarativeBase와 mapped_column으로 모델 정의하기 | [ko](./content/sqlalchemy-101/ko/04-orm-declarative-mapped-column.md) | [en](./content/sqlalchemy-101/en/04-orm-declarative-mapped-column.md) | Publish Ready |
| 5 | Session 깊이 보기: Unit of Work와 Identity Map의 동작 원리 | [ko](./content/sqlalchemy-101/ko/05-session-unit-of-work-identity-map.md) | [en](./content/sqlalchemy-101/en/05-session-unit-of-work-identity-map.md) | Publish Ready |
| 6 | ORM Relationships: relationship과 back_populates로 양방향 탐색 안전하게 잇기 | [ko](./content/sqlalchemy-101/ko/06-relationships-back-populates.md) | [en](./content/sqlalchemy-101/en/06-relationships-back-populates.md) | Publish Ready |
| 7 | 로딩 전략과 N+1 문제: lazy/joined/selectin을 언제 골라야 하는가 | [ko](./content/sqlalchemy-101/ko/07-loading-strategies-n-plus-one.md) | [en](./content/sqlalchemy-101/en/07-loading-strategies-n-plus-one.md) | Publish Ready |
| 8 | 이벤트, hybrid_property, 그리고 커스텀 타입 | [ko](./content/sqlalchemy-101/ko/08-events-hybrid-types.md) | [en](./content/sqlalchemy-101/en/08-events-hybrid-types.md) | Publish Ready |
| 9 | 비동기 SQLAlchemy: aiosqlite와 AsyncSession | [ko](./content/sqlalchemy-101/ko/09-async-aiosqlite.md) | [en](./content/sqlalchemy-101/en/09-async-aiosqlite.md) | Publish Ready |
| 10 | production 패턴: 풀, 관측, 마이그레이션, 배포 | [ko](./content/sqlalchemy-101/ko/10-production-patterns.md) | [en](./content/sqlalchemy-101/en/10-production-patterns.md) | Publish Ready |

### Alembic 101 (`alembic-101`)

Alembic으로 SQLAlchemy 마이그레이션을 운영하는 입문 시리즈. autogenerate, branch와 merge, 데이터 마이그레이션, downgrade 전략, 배포 순서를 SQLite 기준으로 다룹니다.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: —
- 경로: [`content/alembic-101/`](./content/alembic-101/)

| # | Title | KO | EN | Status |
| --- | --- | --- | --- | --- |
| 1 | 왜 Alembic인가, 그리고 init까지 | [ko](./content/alembic-101/ko/01-why-alembic-and-init.md) | [en](./content/alembic-101/en/01-why-alembic-and-init.md) | Publish Ready |
| 2 | env.py와 target_metadata: 모델과 마이그레이션 연결 | [ko](./content/alembic-101/ko/02-env-py-and-target-metadata.md) | [en](./content/alembic-101/en/02-env-py-and-target-metadata.md) | Publish Ready |
| 3 | 첫 revision: upgrade와 downgrade를 손으로 작성 | [ko](./content/alembic-101/ko/03-first-revision-upgrade-downgrade.md) | [en](./content/alembic-101/en/03-first-revision-upgrade-downgrade.md) | Publish Ready |
| 4 | autogenerate: 잡는 것과 못 잡는 것의 경계 | [ko](./content/alembic-101/ko/04-autogenerate-and-its-limits.md) | [en](./content/alembic-101/en/04-autogenerate-and-its-limits.md) | Publish Ready |
| 5 | branch와 merge: 동시에 만든 revision을 합치는 법 | [ko](./content/alembic-101/ko/05-branches-and-merges.md) | [en](./content/alembic-101/en/05-branches-and-merges.md) | Publish Ready |
| 6 | 데이터 마이그레이션: schema 변경과 데이터 변경을 분리하기 | [ko](./content/alembic-101/ko/06-data-migrations.md) | [en](./content/alembic-101/en/06-data-migrations.md) | Publish Ready |
| 7 | online과 offline 모드: --sql로 DDL을 미리 보고 SQLite batch 다루기 | [ko](./content/alembic-101/ko/07-online-vs-offline-and-batch.md) | [en](./content/alembic-101/en/07-online-vs-offline-and-batch.md) | Publish Ready |
| 8 | downgrade 전략: 언제 진심으로 작성하고 언제 막을 것인가 | [ko](./content/alembic-101/ko/08-downgrade-strategy.md) | [en](./content/alembic-101/en/08-downgrade-strategy.md) | Publish Ready |
| 9 | 배포 순서와 blue/green: schema와 application code의 안전한 동기화 | [ko](./content/alembic-101/ko/09-deploy-ordering-and-blue-green.md) | [en](./content/alembic-101/en/09-deploy-ordering-and-blue-green.md) | Publish Ready |
| 10 | Production과 team workflow: PR, CI, 모니터링, 그리고 incident response | [ko](./content/alembic-101/ko/10-production-and-team-workflow.md) | [en](./content/alembic-101/en/10-production-and-team-workflow.md) | Publish Ready |

---

## 데이터베이스 · ORM

### Statistics 101 (`statistics-101`)

기술 통계, 분포, 추정, 신뢰구간, 가설검정, 회귀까지 데이터 분석에 필요한 통계의 큰 그림을 다지는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/statistics-101/`](./content/statistics-101/)

_articles not yet enumerated._

### Probability 101 (`probability-101`)

사건, 조건부확률, 베이즈 정리, 확률변수, 분포, 중심극한정리까지 ML 기초로 이어지는 확률을 다지는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/probability-101/`](./content/probability-101/)

_articles not yet enumerated._

### Linear Algebra 101 (`linear-algebra-101`)

벡터, 행렬, 내적, 선형변환, 기저, 고유값, 행렬분해, PCA까지 ML 입문 직전 단계의 선형대수를 다지는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/linear-algebra-101/`](./content/linear-algebra-101/)

_articles not yet enumerated._

### Data Science 101 (`data-science-101`)

문제 정의, 데이터 수집, 정제, EDA, 시각화, 모델링, 평가, 해석까지 데이터 사이언스 전체 흐름을 다지는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/data-science-101/`](./content/data-science-101/)

_articles not yet enumerated._

### SQL 101 (`sql-101`)

SELECT, JOIN, GROUP BY, subquery, window function, DML, index 기초까지 분석/개발에 바로 쓰는 SQL 입문 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/sql-101/`](./content/sql-101/)

_articles not yet enumerated._

### Pandas 101 (`pandas-101`)

Series, DataFrame, 파일 입출력, filtering, missing value, groupby, merge, time series, vectorization까지 다루는 Pandas 입문 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/pandas-101/`](./content/pandas-101/)

_articles not yet enumerated._

### Machine Learning 101 (`machine-learning-101`)

지도/비지도, train/test, 회귀, 분류, 트리, 군집, regularization, 평가까지 ML 전체 흐름을 다지는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/machine-learning-101/`](./content/machine-learning-101/)

_articles not yet enumerated._

### Model Evaluation 101 (`model-evaluation-101`)

모델을 제대로 평가하는 법 — train/val/test, precision/recall, ROC, calibration, error analysis까지.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/model-evaluation-101/`](./content/model-evaluation-101/)

_articles not yet enumerated._

### MLOps 101 (`mlops-101`)

운영 가능한 ML 시스템 — 실험 관리, 모델 배포, 모니터링, drift, feature store까지.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/mlops-101/`](./content/mlops-101/)

_articles not yet enumerated._

### Data Warehouse 101 (`data-warehouse-101`)

OLTP/OLAP, Fact와 Dimension, Star Schema, Partition, ETL/ELT, BI 연동까지 분석을 위한 데이터 저장소를 설계하는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/data-warehouse-101/`](./content/data-warehouse-101/)

_articles not yet enumerated._

---

## 프로그래밍 일반

### Computer Science 101 (`computer-science-101`)

컴퓨터공학 전공에서 배우는 주요 과목들이 서로 어떻게 연결되는지 보여주는 입문 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/computer-science-101/`](./content/computer-science-101/)

_articles not yet enumerated._

### Python 101 (`python-101`)

Python을 처음 시작하는 사람을 위한 입문 시리즈. 설치와 venv부터 변수, 자료구조, 제어 흐름, 함수, 모듈, 파일 I/O와 예외, 클래스, 표준 라이브러리까지 다룹니다.

- 상태: **Draft**
- 언어: ko, en
- 발행 대상: —
- 경로: [`content/python-101/`](./content/python-101/)

| # | Title | KO | EN | Status |
| --- | --- | --- | --- | --- |
| 1 | why-python-and-install | — | — | Draft |
| 2 | variables-types-operators | — | — | Draft |
| 3 | strings-and-formatting | — | — | Draft |
| 4 | list-tuple-set-dict | — | — | Draft |
| 5 | control-flow | — | — | Draft |
| 6 | functions-and-arguments | — | — | Draft |
| 7 | modules-and-packages | — | — | Draft |
| 8 | file-io-and-exceptions | — | — | Draft |
| 9 | classes-and-objects | — | — | Draft |
| 10 | standard-library-tour | — | — | Draft |

### Git & GitHub 101 (`git-github-101`)

Git의 commit, branch, merge, rebase, pull request, issue, GitHub workflow를 배우는 개발 협업 입문 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: —
- 경로: [`content/git-github-101/`](./content/git-github-101/)

| # | Title | KO | EN | Status |
| --- | --- | --- | --- | --- |
| 1 | what-is-git | — | — | Draft |
| 2 | first-commit | — | — | Draft |
| 3 | status-diff-log | — | — | Draft |
| 4 | branch-basics | — | — | Draft |
| 5 | merge-and-conflict | — | — | Draft |
| 6 | github-repository | — | — | Draft |
| 7 | pull-request | — | — | Draft |
| 8 | issue-and-project | — | — | Draft |
| 9 | good-commit-message | — | — | Draft |
| 10 | real-world-workflow | — | — | Draft |

### Linux CLI 101 (`linux-cli-101`)

파일 탐색, 권한, 프로세스, grep, pipe, shell script, SSH 등 개발자가 반드시 알아야 할 Linux CLI 기본기를 다루는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: —
- 경로: [`content/linux-cli-101/`](./content/linux-cli-101/)

| # | Title | KO | EN | Status |
| --- | --- | --- | --- | --- |
| 1 | CLI와 Shell이란 무엇인가? | [ko](./content/linux-cli-101/ko/01-what-is-cli-and-shell.md) | [en](./content/linux-cli-101/en/01-what-is-cli-and-shell.md) | Content Ready |
| 2 | 파일과 디렉터리 다루기 | [ko](./content/linux-cli-101/ko/02-files-and-directories.md) | [en](./content/linux-cli-101/en/02-files-and-directories.md) | Content Ready |
| 3 | 권한과 소유자 이해하기 | [ko](./content/linux-cli-101/ko/03-permissions-and-ownership.md) | [en](./content/linux-cli-101/en/03-permissions-and-ownership.md) | Content Ready |
| 4 | cat, less, head, tail — 파일 내용 보기 | [ko](./content/linux-cli-101/ko/04-viewing-files.md) | [en](./content/linux-cli-101/en/04-viewing-files.md) | Content Ready |
| 5 | grep, find, xargs — 검색의 삼총사 | [ko](./content/linux-cli-101/ko/05-grep-find-xargs.md) | [en](./content/linux-cli-101/en/05-grep-find-xargs.md) | Content Ready |
| 6 | pipe와 redirection | [ko](./content/linux-cli-101/ko/06-pipe-and-redirection.md) | [en](./content/linux-cli-101/en/06-pipe-and-redirection.md) | Content Ready |
| 7 | 프로세스 확인과 종료 | [ko](./content/linux-cli-101/ko/07-process-management.md) | [en](./content/linux-cli-101/en/07-process-management.md) | Content Ready |
| 8 | 환경변수와 PATH | [ko](./content/linux-cli-101/ko/08-environment-variables.md) | [en](./content/linux-cli-101/en/08-environment-variables.md) | Content Ready |
| 9 | 간단한 shell script | [ko](./content/linux-cli-101/ko/09-shell-script-basics.md) | [en](./content/linux-cli-101/en/09-shell-script-basics.md) | Content Ready |
| 10 | SSH와 원격 서버 접속 | [ko](./content/linux-cli-101/ko/10-ssh-and-remote.md) | [en](./content/linux-cli-101/en/10-ssh-and-remote.md) | Content Ready |

### Python Package 101 (`python-package-101`)

Python 프로젝트 구조, pyproject.toml, 의존성 관리, 빌드, PyPI 배포, 버전 관리, CLI 패키지, 문서화까지 배우는 패키징 입문 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/python-package-101/`](./content/python-package-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Python Package란 무엇인가? | [ko](./content/python-package-101/ko/01-what-is-a-python-package.md) | [en](./content/python-package-101/en/01-what-is-a-python-package.md) | — | Content Ready |
| 2 | 프로젝트 구조 잡기 — src layout과 pyproject.toml | [ko](./content/python-package-101/ko/02-project-structure.md) | [en](./content/python-package-101/en/02-project-structure.md) | — | Content Ready |
| 3 | 의존성 관리 — venv, pip, uv, requirements | [ko](./content/python-package-101/ko/03-dependency-management.md) | [en](./content/python-package-101/en/03-dependency-management.md) | — | Content Ready |
| 4 | 패키지 빌드하기 — wheel과 sdist | [ko](./content/python-package-101/ko/04-building-packages.md) | [en](./content/python-package-101/en/04-building-packages.md) | — | Content Ready |
| 5 | PyPI에 배포하기 — TestPyPI부터 실제 배포까지 | [ko](./content/python-package-101/ko/05-publishing-to-pypi.md) | [en](./content/python-package-101/en/05-publishing-to-pypi.md) | — | Content Ready |
| 6 | 버전 관리와 릴리스 | [ko](./content/python-package-101/ko/06-versioning-and-releases.md) | [en](./content/python-package-101/en/06-versioning-and-releases.md) | — | Content Ready |
| 7 | CLI 패키지 만들기 | [ko](./content/python-package-101/ko/07-cli-packages.md) | [en](./content/python-package-101/en/07-cli-packages.md) | — | Content Ready |
| 8 | 타입 힌트와 정적 검사 | [ko](./content/python-package-101/ko/08-type-hints-and-static-analysis.md) | [en](./content/python-package-101/en/08-type-hints-and-static-analysis.md) | — | Content Ready |
| 9 | 문서화 — README, MkDocs, API Reference | [ko](./content/python-package-101/ko/09-documentation.md) | [en](./content/python-package-101/en/09-documentation.md) | — | Content Ready |
| 10 | 실전 패키지 템플릿 만들기 | [ko](./content/python-package-101/ko/10-package-template.md) | [en](./content/python-package-101/en/10-package-template.md) | — | Content Ready |

### pytest 101 (`pytest-101`)

pytest의 기본 문법, fixture, parametrization, mock, coverage, CI 연동까지 배우는 실전 테스트 입문 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/pytest-101/`](./content/pytest-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | 왜 테스트를 작성해야 할까? | [ko](./content/pytest-101/ko/01-why-write-tests.md) | [en](./content/pytest-101/en/01-why-write-tests.md) | — | Content Ready |
| 2 | 첫 번째 pytest 테스트 작성하기 | [ko](./content/pytest-101/ko/02-first-pytest-test.md) | [en](./content/pytest-101/en/02-first-pytest-test.md) | — | Content Ready |
| 3 | assert와 예외 테스트 | [ko](./content/pytest-101/ko/03-assert-and-exceptions.md) | [en](./content/pytest-101/en/03-assert-and-exceptions.md) | — | Content Ready |
| 4 | fixture 이해하기 | [ko](./content/pytest-101/ko/04-fixtures.md) | [en](./content/pytest-101/en/04-fixtures.md) | — | Content Ready |
| 5 | parametrization으로 테스트 케이스 늘리기 | [ko](./content/pytest-101/ko/05-parametrization.md) | [en](./content/pytest-101/en/05-parametrization.md) | — | Content Ready |
| 6 | mock과 monkeypatch | [ko](./content/pytest-101/ko/06-mock-and-monkeypatch.md) | [en](./content/pytest-101/en/06-mock-and-monkeypatch.md) | — | Content Ready |
| 7 | 파일, 환경변수, 시간 테스트하기 | [ko](./content/pytest-101/ko/07-testing-files-env-time.md) | [en](./content/pytest-101/en/07-testing-files-env-time.md) | — | Content Ready |
| 8 | coverage와 테스트 품질 보기 | [ko](./content/pytest-101/ko/08-coverage.md) | [en](./content/pytest-101/en/08-coverage.md) | — | Content Ready |
| 9 | GitHub Actions에서 테스트 자동화하기 | [ko](./content/pytest-101/ko/09-ci-with-github-actions.md) | [en](./content/pytest-101/en/09-ci-with-github-actions.md) | — | Content Ready |
| 10 | 테스트하기 쉬운 코드 구조 만들기 | [ko](./content/pytest-101/ko/10-testable-code.md) | [en](./content/pytest-101/en/10-testable-code.md) | — | Content Ready |

---

## 프로그래밍 기초

### Object-Oriented Programming 101 (`oop-101`)

클래스, 캡슐화, 상속, 다형성, 추상화, SOLID 원칙까지 객체지향의 핵심을 다루는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/oop-101/`](./content/oop-101/)

_articles not yet enumerated._

### Functional Programming 101 (`functional-programming-101`)

순수 함수, 불변 데이터, 고차 함수, 클로저, 함수 합성까지 함수형 프로그래밍의 핵심을 Python으로 배우는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/functional-programming-101/`](./content/functional-programming-101/)

_articles not yet enumerated._

### Type Hints in Python 101 (`type-hints-python-101`)

Python type hint, Optional, Union, TypedDict, Protocol, Generic, mypy, Pydantic까지 타입 힌트 활용을 배우는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/type-hints-python-101/`](./content/type-hints-python-101/)

_articles not yet enumerated._

---

## Azure

### Azure App Service 101 (`azure-app-service-101`)

Azure App Service 입문 7부작 — 호스팅, 설정, 로그, 스케일링.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/azure-app-service-101/`](./content/azure-app-service-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Azure App Service란? - 플랫폼 아키텍처 이해하기 | [ko](./content/azure-app-service-101/ko/01-what-is-app-service.md) | [en](./content/azure-app-service-101/en/01-what-is-app-service.md) | — | Publish Ready |
| 2 | Request Lifecycle: 3am에 터진 502를 어디서부터 봐야 할까 | [ko](./content/azure-app-service-101/ko/02-request-lifecycle.md) | [en](./content/azure-app-service-101/en/02-request-lifecycle.md) | — | Publish Ready |
| 3 | Hosting Models: 어떤 플랜을 선택해야 할까? | [ko](./content/azure-app-service-101/ko/03-hosting-models.md) | [en](./content/azure-app-service-101/en/03-hosting-models.md) | — | Publish Ready |
| 4 | 첫 번째 배포: 로컬에서 Azure까지 (Python/Flask) | [ko](./content/azure-app-service-101/ko/04-first-deploy.md) | [en](./content/azure-app-service-101/en/04-first-deploy.md) | — | Publish Ready |
| 5 | Configuration 마스터하기: App Settings & 환경변수 | [ko](./content/azure-app-service-101/ko/05-configuration.md) | [en](./content/azure-app-service-101/en/05-configuration.md) | — | Publish Ready |
| 6 | 로그와 모니터링 기초: “앱이 느려요”에 답할 수 있는 상태 만들기 | [ko](./content/azure-app-service-101/ko/06-logging-monitoring.md) | [en](./content/azure-app-service-101/en/06-logging-monitoring.md) | — | Publish Ready |
| 7 | Scaling 101: 언제 Scale Up vs Scale Out? | [ko](./content/azure-app-service-101/ko/07-scaling-101.md) | [en](./content/azure-app-service-101/en/07-scaling-101.md) | — | Publish Ready |

### Azure App Service Deep Dive (`azure-app-service-deep-dive`)

App Service 내부 — Front-End, Worker, Sandbox, Kudu, Scaling.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/azure-app-service-deep-dive/`](./content/azure-app-service-deep-dive/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | App Service 플랫폼 아키텍처 — Front-End·Worker·File Server | [ko](./content/azure-app-service-deep-dive/ko/01-platform-architecture.md) | [en](./content/azure-app-service-deep-dive/en/01-platform-architecture.md) | — | Publish Ready |
| 2 | Front-End과 ARR — 요청은 어떻게 워커에 도달하는가 | [ko](./content/azure-app-service-deep-dive/ko/02-front-end-and-arr.md) | [en](./content/azure-app-service-deep-dive/en/02-front-end-and-arr.md) | — | Publish Ready |
| 3 | Worker 인스턴스와 샌드박스 — 사용자 코드를 어디에 가두는가 | [ko](./content/azure-app-service-deep-dive/ko/03-worker-and-sandbox.md) | [en](./content/azure-app-service-deep-dive/en/03-worker-and-sandbox.md) | — | Publish Ready |
| 4 | 배포와 Kudu — 빌드·동기화·릴리스의 안쪽 | [ko](./content/azure-app-service-deep-dive/ko/04-deployment-and-kudu.md) | [en](./content/azure-app-service-deep-dive/en/04-deployment-and-kudu.md) | — | Publish Ready |
| 5 | 스케일링 내부 동작 — Scale Out 결정과 워커 추가 경로 | [ko](./content/azure-app-service-deep-dive/ko/05-scaling-internals.md) | [en](./content/azure-app-service-deep-dive/en/05-scaling-internals.md) | — | Publish Ready |
| 6 | 콜드 스타트와 Warmup — 첫 요청이 비싼 이유 | [ko](./content/azure-app-service-deep-dive/ko/06-cold-start-and-warmup.md) | [en](./content/azure-app-service-deep-dive/en/06-cold-start-and-warmup.md) | — | Publish Ready |

### Azure Functions 101 (`azure-functions-101`)

Azure Functions 입문 7부작 — 트리거/바인딩부터 운영까지.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/azure-functions-101/`](./content/azure-functions-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Azure Functions란? — 이벤트가 함수를 호출하는 세상 | [ko](./content/azure-functions-101/ko/01-what-is-azure-functions.md) | [en](./content/azure-functions-101/en/01-what-is-azure-functions.md) | — | Publish Ready |
| 2 | 트리거와 바인딩 — 함수 입출력의 모든 것 | [ko](./content/azure-functions-101/ko/02-triggers-and-bindings.md) | [en](./content/azure-functions-101/en/02-triggers-and-bindings.md) | — | Publish Ready |
| 3 | Host와 Worker — 함수는 누가 실행하는가 | [ko](./content/azure-functions-101/ko/03-host-and-worker.md) | [en](./content/azure-functions-101/en/03-host-and-worker.md) | — | Publish Ready |
| 4 | 함수 하나 배포하기 — 로컬에서 Azure까지 | [ko](./content/azure-functions-101/ko/04-first-deploy.md) | [en](./content/azure-functions-101/en/04-first-deploy.md) | — | Publish Ready |
| 5 | 어떤 플랜을 선택해야 할까 — Consumption / Flex / Premium / Dedicated | [ko](./content/azure-functions-101/ko/05-choosing-a-plan.md) | [en](./content/azure-functions-101/en/05-choosing-a-plan.md) | — | Publish Ready |
| 6 | 스케일링과 콜드 스타트 — 서버리스가 빨라지는 순간과 느려지는 순간 | [ko](./content/azure-functions-101/ko/06-scaling-and-cold-start.md) | [en](./content/azure-functions-101/en/06-scaling-and-cold-start.md) | — | Publish Ready |
| 7 | 모니터링과 운영 기초 | [ko](./content/azure-functions-101/ko/07-monitoring-and-ops.md) | [en](./content/azure-functions-101/en/07-monitoring-and-ops.md) | — | Publish Ready |

### Azure Functions Deep Dive (`azure-functions-deep-dive`)

Azure Functions Host 소스 분석 시리즈 (commit-pinned).

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/azure-functions-deep-dive/`](./content/azure-functions-deep-dive/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | 호스트 부팅 — `WebJobsScriptHostService`부터 따라가기 | [ko](./content/azure-functions-deep-dive/ko/01-host-bootstrap.md) | [en](./content/azure-functions-deep-dive/en/01-host-bootstrap.md) | — | Publish Ready |
| 2 | Worker 프로세스 — 한 호스트에서 여러 언어 런타임이 같이 사는 법 | [ko](./content/azure-functions-deep-dive/ko/02-worker-process.md) | [en](./content/azure-functions-deep-dive/en/02-worker-process.md) | — | Publish Ready |
| 3 | gRPC 이벤트 스트림 — 호스트와 워커는 무엇을 주고받는가 | [ko](./content/azure-functions-deep-dive/ko/03-grpc-event-stream.md) | [en](./content/azure-functions-deep-dive/en/03-grpc-event-stream.md) | — | Publish Ready |
| 4 | Dispatcher와 Invocation — 함수 호출이 워커에 도달하기까지 | [ko](./content/azure-functions-deep-dive/ko/04-dispatcher-and-invocation.md) | [en](./content/azure-functions-deep-dive/en/04-dispatcher-and-invocation.md) | — | Publish Ready |
| 5 | 스케일링 내부 동작 — Scale Controller, ScaleMonitor, 그리고 플랜별 차이 | [ko](./content/azure-functions-deep-dive/ko/05-scaling-internals.md) | [en](./content/azure-functions-deep-dive/en/05-scaling-internals.md) | — | Publish Ready |
| 6 | 콜드 스타트와 Placeholder Mode — 새 인스턴스가 만들어질 때 | [ko](./content/azure-functions-deep-dive/ko/06-cold-start-placeholder.md) | [en](./content/azure-functions-deep-dive/en/06-cold-start-placeholder.md) | — | Publish Ready |

### Azure Kubernetes Service 101 (`azure-aks-101`)

AKS 입문 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/azure-aks-101/`](./content/azure-aks-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Azure Kubernetes Service란? — 직접 운영하지 않아도 되는 Kubernetes | [ko](./content/azure-aks-101/ko/01-what-is-aks.md) | [en](./content/azure-aks-101/en/01-what-is-aks.md) | — | Publish Ready |
| 2 | 클러스터 아키텍처 — Control Plane과 Node Pool | [ko](./content/azure-aks-101/ko/02-cluster-architecture.md) | [en](./content/azure-aks-101/en/02-cluster-architecture.md) | — | Publish Ready |
| 3 | 첫 클러스터 만들고 앱 배포하기 — Python/FastAPI | [ko](./content/azure-aks-101/ko/03-first-cluster-and-deploy.md) | [en](./content/azure-aks-101/en/03-first-cluster-and-deploy.md) | — | Publish Ready |
| 4 | Pod·Deployment·Service — 워크로드를 표현하는 세 가지 방식 | [ko](./content/azure-aks-101/ko/04-pod-deployment-service.md) | [en](./content/azure-aks-101/en/04-pod-deployment-service.md) | — | Publish Ready |
| 5 | 네트워킹과 Ingress — 클러스터 안과 밖을 잇는 길 | [ko](./content/azure-aks-101/ko/05-networking-and-ingress.md) | [en](./content/azure-aks-101/en/05-networking-and-ingress.md) | — | Publish Ready |
| 6 | 스케일링 — HPA, Cluster Autoscaler, KEDA | [ko](./content/azure-aks-101/ko/06-scaling-hpa-ca-keda.md) | [en](./content/azure-aks-101/en/06-scaling-hpa-ca-keda.md) | — | Publish Ready |
| 7 | 모니터링과 운영 — Container Insights, 로그, 알람 | [ko](./content/azure-aks-101/ko/07-monitoring-and-ops.md) | [en](./content/azure-aks-101/en/07-monitoring-and-ops.md) | — | Publish Ready |

### Azure Kubernetes Service Deep Dive (`azure-aks-deep-dive`)

AKS control plane / data plane 내부 동작.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/azure-aks-deep-dive/`](./content/azure-aks-deep-dive/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Control Plane 해부 — AKS가 사용자에게서 가린 것 | [ko](./content/azure-aks-deep-dive/ko/01-control-plane-anatomy.md) | [en](./content/azure-aks-deep-dive/en/01-control-plane-anatomy.md) | — | Publish Ready |
| 2 | kubelet과 containerd — 노드 위에서 컨테이너가 뜨기까지 | [ko](./content/azure-aks-deep-dive/ko/02-kubelet-and-containerd.md) | [en](./content/azure-aks-deep-dive/en/02-kubelet-and-containerd.md) | — | Publish Ready |
| 3 | CNI와 Azure CNI Overlay — Pod IP가 어디서 오는가 | [ko](./content/azure-aks-deep-dive/ko/03-cni-and-azure-cni-overlay.md) | [en](./content/azure-aks-deep-dive/en/03-cni-and-azure-cni-overlay.md) | — | Publish Ready |
| 4 | Scheduler와 Pod 배치 — 어느 노드로 갈지 누가 정하는가 | [ko](./content/azure-aks-deep-dive/ko/04-scheduler-and-pod-placement.md) | [en](./content/azure-aks-deep-dive/en/04-scheduler-and-pod-placement.md) | — | Publish Ready |
| 5 | HPA와 Cluster Autoscaler 내부 — 두 컨트롤 루프 | [ko](./content/azure-aks-deep-dive/ko/05-hpa-and-cluster-autoscaler-internals.md) | [en](./content/azure-aks-deep-dive/en/05-hpa-and-cluster-autoscaler-internals.md) | — | Publish Ready |
| 6 | KEDA 내부 — ScaledObject가 HPA를 만드는 방식 | [ko](./content/azure-aks-deep-dive/ko/06-keda-internals.md) | [en](./content/azure-aks-deep-dive/en/06-keda-internals.md) | — | Publish Ready |

### Azure Container Apps 101 (`azure-aca-101`)

Container Apps 입문 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/azure-aca-101/`](./content/azure-aca-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Azure Container Apps란? — Kubernetes 없이 컨테이너 운영하기 | [ko](./content/azure-aca-101/ko/01-what-is-aca.md) | [en](./content/azure-aca-101/en/01-what-is-aca.md) | — | Publish Ready |
| 2 | Environment·Container App·Revision — 세 단어로 보는 ACA | [ko](./content/azure-aca-101/ko/02-environment-app-revision.md) | [en](./content/azure-aca-101/en/02-environment-app-revision.md) | — | Publish Ready |
| 3 | 첫 앱 배포하기 — Python/FastAPI | [ko](./content/azure-aca-101/ko/03-first-deploy.md) | [en](./content/azure-aca-101/en/03-first-deploy.md) | — | Publish Ready |
| 4 | Ingress와 트래픽 분할 — Revision 기반 배포 전략 | [ko](./content/azure-aca-101/ko/04-ingress-and-traffic-split.md) | [en](./content/azure-aca-101/en/04-ingress-and-traffic-split.md) | — | Publish Ready |
| 5 | 스케일링 — KEDA scaler와 0-to-N | [ko](./content/azure-aca-101/ko/05-scaling-with-keda.md) | [en](./content/azure-aca-101/en/05-scaling-with-keda.md) | — | Publish Ready |
| 6 | Dapr 통합 — 사이드카로 얻는 것 | [ko](./content/azure-aca-101/ko/06-dapr-integration.md) | [en](./content/azure-aca-101/en/06-dapr-integration.md) | — | Publish Ready |
| 7 | 모니터링과 운영 — Log Analytics와 Application Insights | [ko](./content/azure-aca-101/ko/07-monitoring-and-ops.md) | [en](./content/azure-aca-101/en/07-monitoring-and-ops.md) | — | Publish Ready |

### Azure Container Apps Deep Dive (`azure-aca-deep-dive`)

ACA 위에 얹힌 KEDA·Dapr·Envoy 내부 동작.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/azure-aca-deep-dive/`](./content/azure-aca-deep-dive/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | ACA 아키텍처 — 사용자에게 보이지 않는 Kubernetes 위에 얹은 것 | [ko](./content/azure-aca-deep-dive/ko/01-aca-architecture.md) | [en](./content/azure-aca-deep-dive/en/01-aca-architecture.md) | — | Publish Ready |
| 2 | Environment 내부 — 네트워크·관측·Dapr 스코프의 경계 | [ko](./content/azure-aca-deep-dive/ko/02-environment-internals.md) | [en](./content/azure-aca-deep-dive/en/02-environment-internals.md) | — | Publish Ready |
| 3 | Revision과 트래픽 분할 — Envoy 가중치는 어디에서 오는가 | [ko](./content/azure-aca-deep-dive/ko/03-revision-and-traffic-split.md) | [en](./content/azure-aca-deep-dive/en/03-revision-and-traffic-split.md) | — | Publish Ready |
| 4 | ACA 안의 KEDA — Scale Rule이 만드는 것 | [ko](./content/azure-aca-deep-dive/ko/04-keda-in-aca.md) | [en](./content/azure-aca-deep-dive/en/04-keda-in-aca.md) | — | Publish Ready |
| 5 | Dapr 사이드카 내부 — 컨테이너 옆에 뜨는 Go 프로세스 | [ko](./content/azure-aca-deep-dive/ko/05-dapr-sidecar-internals.md) | [en](./content/azure-aca-deep-dive/en/05-dapr-sidecar-internals.md) | — | Publish Ready |
| 6 | Envoy Ingress 경로 — 첫 요청이 사용자 컨테이너에 닿기까지 | [ko](./content/azure-aca-deep-dive/ko/06-envoy-ingress-path.md) | [en](./content/azure-aca-deep-dive/en/06-envoy-ingress-path.md) | — | Publish Ready |

---

## 기술 글쓰기

### 기술 글쓰기 101 / Technical Writing 101 (`technical-writing-101`)

독자 정의부터 발행 전 체크리스트까지, 기술 글쓰기의 기본을 다지는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/technical-writing-101/`](./content/technical-writing-101/)

_articles not yet enumerated._

### 엔지니어를 위한 기술 글쓰기 / Technical Writing for Engineers (`technical-writing`)

시리즈를 설계하고, 한 편을 다듬는 법.

- 상태: **Planned**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/technical-writing/`](./content/technical-writing/)

_articles not yet enumerated._

---

## AX

### AX 실전 가이드 / AI Transformation Practical Guide (`ax-practical-guide`)

AX 도입 전략, 업무 자동화 사례, 조직 변화 관리.

- 상태: **Planned**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/ax-practical-guide/`](./content/ax-practical-guide/)

_articles not yet enumerated._
