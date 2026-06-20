# Series Index

이 문서는 전체 콘텐츠 시리즈의 목록과 발행 상태를 관리한다. 단일 출처는 [`series.yaml`](./series.yaml) 이며, 본 문서는 `scripts/build_series_index.py` 가 자동 생성한다. 직접 편집 금지.

## Status Legend

| Status | Meaning |
| --- | --- |
| Planned | 기획 중 |
| Draft | 초안 작성 중 |
| Content Ready | 본문 작성 완료 |
| Publish Ready | 발행 준비 완료 |
| Ready (legacy) | 발행 준비 완료 (legacy) |
| Published | 발행 완료 |
| Needs Update | 업데이트 필요 |

---

## AI

### LLM 앱 기초 / LLM App Foundations 101 (`llm-app-foundations-101`)

LLM API 기초, 토큰, 프롬프트 엔지니어링 — 6부작.

- 상태: **Publish Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/llm-app-foundations-101/`](./content/llm-app-foundations-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | LLM App Foundations 101 (1/6): LLM API 첫걸음 — 모델에게 첫 번째 요청 보내기 | [ko](./content/llm-app-foundations-101/ko/01-llm-api-first-call.md) | [en](./content/llm-app-foundations-101/en/01-llm-api-first-call.md) | [medium](./content/llm-app-foundations-101/medium/01.html) | Publish Ready |
| 2 | LLM App Foundations 101 (2/6): 토큰 이해하기 — 비용, 한계, 컨텍스트 창 | [ko](./content/llm-app-foundations-101/ko/02-understanding-tokens.md) | [en](./content/llm-app-foundations-101/en/02-understanding-tokens.md) | [medium](./content/llm-app-foundations-101/medium/02.html) | Publish Ready |
| 3 | LLM App Foundations 101 (3/6): 프롬프트 엔지니어링 기초 — System·User·Assistant 역할 | [ko](./content/llm-app-foundations-101/ko/03-prompt-engineering-basics.md) | [en](./content/llm-app-foundations-101/en/03-prompt-engineering-basics.md) | [medium](./content/llm-app-foundations-101/medium/03.html) | Publish Ready |
| 4 | LLM App Foundations 101 (4/6): Few-shot과 Chain-of-Thought — 더 나은 답변 유도하기 | [ko](./content/llm-app-foundations-101/ko/04-few-shot-and-cot.md) | [en](./content/llm-app-foundations-101/en/04-few-shot-and-cot.md) | [medium](./content/llm-app-foundations-101/medium/04.html) | Publish Ready |
| 5 | LLM App Foundations 101 (5/6): 대화 상태 관리 — 멀티턴 챗봇 만들기 | [ko](./content/llm-app-foundations-101/ko/05-conversation-state.md) | [en](./content/llm-app-foundations-101/en/05-conversation-state.md) | [medium](./content/llm-app-foundations-101/medium/05.html) | Publish Ready |
| 6 | LLM App Foundations 101 (6/6): 스트리밍 응답 처리 — 실시간으로 출력 받기 | [ko](./content/llm-app-foundations-101/ko/06-streaming-responses.md) | [en](./content/llm-app-foundations-101/en/06-streaming-responses.md) | [medium](./content/llm-app-foundations-101/medium/06.html) | Publish Ready |

### LLM API 프로덕션 101 / LLM API Production 101 (`llm-api-production-101`)

Structured Output, Tool Calling, Streaming, Caching, Retry, Rate Limit — 6부작.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/llm-api-production-101/`](./content/llm-api-production-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | LLM API Production 101 (1/6): 구조화 출력 — JSON 모드와 응답 스키마 | [ko](./content/llm-api-production-101/ko/01-structured-output.md) | [en](./content/llm-api-production-101/en/01-structured-output.md) | [medium](./content/llm-api-production-101/medium/01.html) | Publish Ready |
| 2 | LLM API Production 101 (2/6): 툴 호출 — 함수를 모델에 연결하기 | [ko](./content/llm-api-production-101/ko/02-tool-calling.md) | [en](./content/llm-api-production-101/en/02-tool-calling.md) | [medium](./content/llm-api-production-101/medium/02.html) | Publish Ready |
| 3 | LLM API Production 101 (3/6): 스트리밍 심화 — 청크 처리와 오류 복구 | [ko](./content/llm-api-production-101/ko/03-streaming-in-depth.md) | [en](./content/llm-api-production-101/en/03-streaming-in-depth.md) | [medium](./content/llm-api-production-101/medium/03.html) | Publish Ready |
| 4 | LLM API Production 101 (4/6): 캐싱 전략 — 비용과 지연 시간 줄이기 | [ko](./content/llm-api-production-101/ko/04-caching-strategies.md) | [en](./content/llm-api-production-101/en/04-caching-strategies.md) | [medium](./content/llm-api-production-101/medium/04.html) | Publish Ready |
| 5 | LLM API Production 101 (5/6): 재시도와 오류 처리 — 안정적인 API 호출 만들기 | [ko](./content/llm-api-production-101/ko/05-retry-and-error-handling.md) | [en](./content/llm-api-production-101/en/05-retry-and-error-handling.md) | [medium](./content/llm-api-production-101/medium/05.html) | Publish Ready |
| 6 | LLM API Production 101 (6/6): 속도 제한 관리 — Rate Limit 대응 패턴 | [ko](./content/llm-api-production-101/ko/06-rate-limit-management.md) | [en](./content/llm-api-production-101/en/06-rate-limit-management.md) | [medium](./content/llm-api-production-101/medium/06.html) | Publish Ready |

### 벡터 검색 101 / Vector Search 101 (`vector-search-101`)

임베딩, FAISS, 유사도, 청크 전략 — 6부작.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/vector-search-101/`](./content/vector-search-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Vector Search 101 (1/6): 임베딩이란 무엇인가 — 텍스트를 벡터로 변환하기 | [ko](./content/vector-search-101/ko/01-what-is-embedding.md) | [en](./content/vector-search-101/en/01-what-is-embedding.md) | [medium](./content/vector-search-101/medium/01.html) | Publish Ready |
| 2 | Vector Search 101 (2/6): HuggingFace 임베딩 실습 — sentence-transformers로 첫 벡터 만들기 | [ko](./content/vector-search-101/ko/02-huggingface-embeddings.md) | [en](./content/vector-search-101/en/02-huggingface-embeddings.md) | [medium](./content/vector-search-101/medium/02.html) | Publish Ready |
| 3 | Vector Search 101 (3/6): 코사인 유사도와 벡터 검색 — 문장 간 거리 계산하기 | [ko](./content/vector-search-101/ko/03-cosine-similarity.md) | [en](./content/vector-search-101/en/03-cosine-similarity.md) | [medium](./content/vector-search-101/medium/03.html) | Publish Ready |
| 4 | Vector Search 101 (4/6): FAISS 입문 — 고속 근사 최근접 이웃 검색 | [ko](./content/vector-search-101/ko/04-faiss-fundamentals.md) | [en](./content/vector-search-101/en/04-faiss-fundamentals.md) | [medium](./content/vector-search-101/medium/04.html) | Publish Ready |
| 5 | Vector Search 101 (5/6): 청크 전략 — 긴 문서를 어떻게 나눌 것인가 | [ko](./content/vector-search-101/ko/05-chunking-strategies.md) | [en](./content/vector-search-101/en/05-chunking-strategies.md) | [medium](./content/vector-search-101/medium/05.html) | Publish Ready |
| 6 | Vector Search 101 (6/6): 벡터 검색 파이프라인 — 문서 수집부터 쿼리까지 | [ko](./content/vector-search-101/ko/06-vector-search-pipeline.md) | [en](./content/vector-search-101/en/06-vector-search-pipeline.md) | [medium](./content/vector-search-101/medium/06.html) | Publish Ready |

### LangChain 101 (`langchain-101`)

LCEL, Runnable, Retriever, Tool Calling 기본, Streaming — LangChain API 사용법 6부작.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/langchain-101/`](./content/langchain-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | LangChain 101 (1/6): LangChain 소개 — LCEL과 Runnable 기본 | [ko](./content/langchain-101/ko/01-lcel-runnable-basics.md) | [en](./content/langchain-101/en/01-lcel-runnable-basics.md) | [medium](./content/langchain-101/medium/01.html) | Publish Ready |
| 2 | LangChain 101 (2/6): Prompt와 LLM Chain — 체인 첫 번째 구성 | [ko](./content/langchain-101/ko/02-prompt-llm-chain.md) | [en](./content/langchain-101/en/02-prompt-llm-chain.md) | [medium](./content/langchain-101/medium/02.html) | Publish Ready |
| 3 | LangChain 101 (3/6): Retriever — 문서 검색과 컨텍스트 주입 | [ko](./content/langchain-101/ko/03-retriever.md) | [en](./content/langchain-101/en/03-retriever.md) | [medium](./content/langchain-101/medium/03.html) | Publish Ready |
| 4 | LangChain 101 (4/6): Tool Calling — 외부 도구 연결하기 | [ko](./content/langchain-101/ko/04-tool-calling.md) | [en](./content/langchain-101/en/04-tool-calling.md) | [medium](./content/langchain-101/medium/04.html) | Publish Ready |
| 5 | LangChain 101 (5/6): Streaming — 실시간 출력 처리 | [ko](./content/langchain-101/ko/05-streaming.md) | [en](./content/langchain-101/en/05-streaming.md) | [medium](./content/langchain-101/medium/05.html) | Publish Ready |
| 6 | LangChain 101 (6/6): 실전 체인 조립 — 컴포넌트를 하나로 연결하기 | [ko](./content/langchain-101/ko/06-putting-it-together.md) | [en](./content/langchain-101/en/06-putting-it-together.md) | [medium](./content/langchain-101/medium/06.html) | Publish Ready |

### AI 앱 패턴 101 / AI App Patterns 101 (`ai-app-patterns-101`)

챗봇, RAG Q&A, 문서비서, Agent, Workflow, Human-in-the-loop — LLM 앱 설계 패턴 6부작.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/ai-app-patterns-101/`](./content/ai-app-patterns-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | AI App Patterns 101 (1/6): Chatbot 패턴 | [ko](./content/ai-app-patterns-101/ko/01-chatbot-pattern.md) | [en](./content/ai-app-patterns-101/en/01-chatbot-pattern.md) | [medium](./content/ai-app-patterns-101/medium/01.html) | Publish Ready |
| 2 | AI App Patterns 101 (2/6): RAG QA 패턴 | [ko](./content/ai-app-patterns-101/ko/02-rag-qa-pattern.md) | [en](./content/ai-app-patterns-101/en/02-rag-qa-pattern.md) | [medium](./content/ai-app-patterns-101/medium/02.html) | Publish Ready |
| 3 | AI App Patterns 101 (3/6): Document Assistant 패턴 | [ko](./content/ai-app-patterns-101/ko/03-document-assistant.md) | [en](./content/ai-app-patterns-101/en/03-document-assistant.md) | [medium](./content/ai-app-patterns-101/medium/03.html) | Publish Ready |
| 4 | AI App Patterns 101 (4/6): Agent Tool 패턴 | [ko](./content/ai-app-patterns-101/ko/04-agent-tool-pattern.md) | [en](./content/ai-app-patterns-101/en/04-agent-tool-pattern.md) | [medium](./content/ai-app-patterns-101/medium/04.html) | Publish Ready |
| 5 | AI App Patterns 101 (5/6): Workflow Automation 패턴 | [ko](./content/ai-app-patterns-101/ko/05-workflow-automation.md) | [en](./content/ai-app-patterns-101/en/05-workflow-automation.md) | [medium](./content/ai-app-patterns-101/medium/05.html) | Publish Ready |
| 6 | AI App Patterns 101 (6/6): Human-in-the-Loop 패턴 | [ko](./content/ai-app-patterns-101/ko/06-human-in-the-loop.md) | [en](./content/ai-app-patterns-101/en/06-human-in-the-loop.md) | [medium](./content/ai-app-patterns-101/medium/06.html) | Publish Ready |

### RAG Deep Dive (`rag-deep-dive`)

LangChain · FAISS · RAGAS 소스로 따라가는 RAG 파이프라인 심층 분석 6부작.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/rag-deep-dive/`](./content/rag-deep-dive/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | RAG Deep Dive (1/6): 문서 로딩과 청크 전략 — LangChain TextSplitter 내부 | [ko](./content/rag-deep-dive/ko/01-document-loading-and-chunking.md) | [en](./content/rag-deep-dive/en/01-document-loading-and-chunking.md) | [medium](./content/rag-deep-dive/medium/01.html) | Publish Ready |
| 2 | RAG Deep Dive (2/6): 임베딩과 벡터 인덱스 — FAISS IndexFlatL2 동작 원리 | [ko](./content/rag-deep-dive/ko/02-embeddings-and-vector-index.md) | [en](./content/rag-deep-dive/en/02-embeddings-and-vector-index.md) | [medium](./content/rag-deep-dive/medium/02.html) | Publish Ready |
| 3 | RAG Deep Dive (3/6): Retriever 설계 — VectorStoreRetriever와 MMR | [ko](./content/rag-deep-dive/ko/03-retriever-design.md) | [en](./content/rag-deep-dive/en/03-retriever-design.md) | [medium](./content/rag-deep-dive/medium/03.html) | Publish Ready |
| 4 | RAG Deep Dive (4/6): 프롬프트 구성과 컨텍스트 주입 — PromptTemplate 내부 | [ko](./content/rag-deep-dive/ko/04-prompt-construction-and-context-injection.md) | [en](./content/rag-deep-dive/en/04-prompt-construction-and-context-injection.md) | [medium](./content/rag-deep-dive/medium/04.html) | Publish Ready |
| 5 | RAG Deep Dive (5/6): RAG Chain 조립 — RetrievalQA vs LCEL | [ko](./content/rag-deep-dive/ko/05-rag-chain-assembly.md) | [en](./content/rag-deep-dive/en/05-rag-chain-assembly.md) | [medium](./content/rag-deep-dive/medium/05.html) | Publish Ready |
| 6 | RAG Deep Dive (6/6): 평가와 품질 게이트 — RAGAS 메트릭과 Faithfulness | [ko](./content/rag-deep-dive/ko/06-evaluation-and-quality-gates.md) | [en](./content/rag-deep-dive/en/06-evaluation-and-quality-gates.md) | [medium](./content/rag-deep-dive/medium/06.html) | Publish Ready |

### RAG 평가와 벤치마크 101 / RAG Evaluation and Benchmarking 101 (`rag-benchmark-101`)

RAG 품질 평가 6부작 — 평가 데이터셋, 임베딩/리트리버 비교, RAGAS, 의사결정 연결.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/rag-benchmark-101/`](./content/rag-benchmark-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | RAG Evaluation and Benchmarking 101 (1/6): RAG 평가 지표 이해 | [ko](./content/rag-benchmark-101/ko/01-evaluation-metrics.md) | [en](./content/rag-benchmark-101/en/01-evaluation-metrics.md) | [medium](./content/rag-benchmark-101/medium/01.html) | Publish Ready |
| 2 | RAG Evaluation and Benchmarking 101 (2/6): 검색 성능 측정 | [ko](./content/rag-benchmark-101/ko/02-retrieval-benchmarking.md) | [en](./content/rag-benchmark-101/en/02-retrieval-benchmarking.md) | [medium](./content/rag-benchmark-101/medium/02.html) | Publish Ready |
| 3 | RAG Evaluation and Benchmarking 101 (3/6): 임베딩 모델 비교 | [ko](./content/rag-benchmark-101/ko/03-embedding-comparison.md) | [en](./content/rag-benchmark-101/en/03-embedding-comparison.md) | [medium](./content/rag-benchmark-101/medium/03.html) | Publish Ready |
| 4 | RAG Evaluation and Benchmarking 101 (4/6): VectorDB 선택 기준 | [ko](./content/rag-benchmark-101/ko/04-vectordb-selection.md) | [en](./content/rag-benchmark-101/en/04-vectordb-selection.md) | [medium](./content/rag-benchmark-101/medium/04.html) | Publish Ready |
| 5 | RAG Evaluation and Benchmarking 101 (5/6): 종단 간 RAG 파이프라인 평가 | [ko](./content/rag-benchmark-101/ko/05-e2e-evaluation.md) | [en](./content/rag-benchmark-101/en/05-e2e-evaluation.md) | [medium](./content/rag-benchmark-101/medium/05.html) | Publish Ready |
| 6 | RAG Evaluation and Benchmarking 101 (6/6): RAG 벤치마크 완성 | [ko](./content/rag-benchmark-101/ko/06-benchmark-complete.md) | [en](./content/rag-benchmark-101/en/06-benchmark-complete.md) | [medium](./content/rag-benchmark-101/medium/06.html) | Publish Ready |

### 문서 수집과 인덱싱 101 / Document Ingestion 101 (`document-ingestion-101`)

PDF 파싱, 메타데이터, 증분 인덱싱 — 6부작.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/document-ingestion-101/`](./content/document-ingestion-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Document Ingestion 101 (1/6): PDF 파싱과 텍스트 추출 | [ko](./content/document-ingestion-101/ko/01-pdf-parsing.md) | [en](./content/document-ingestion-101/en/01-pdf-parsing.md) | [medium](./content/document-ingestion-101/medium/01.html) | Publish Ready |
| 2 | Document Ingestion 101 (2/6): 청킹 전략 — 문서 유형별 최적화 | [ko](./content/document-ingestion-101/ko/02-chunking-strategies.md) | [en](./content/document-ingestion-101/en/02-chunking-strategies.md) | [medium](./content/document-ingestion-101/medium/02.html) | Publish Ready |
| 3 | Document Ingestion 101 (3/6): 메타데이터 설계와 필터링 | [ko](./content/document-ingestion-101/ko/03-metadata-filtering.md) | [en](./content/document-ingestion-101/en/03-metadata-filtering.md) | [medium](./content/document-ingestion-101/medium/03.html) | Publish Ready |
| 4 | Document Ingestion 101 (4/6): 증분 인덱싱 — 변경된 문서만 업데이트 | [ko](./content/document-ingestion-101/ko/04-incremental-indexing.md) | [en](./content/document-ingestion-101/en/04-incremental-indexing.md) | [medium](./content/document-ingestion-101/medium/04.html) | Publish Ready |
| 5 | Document Ingestion 101 (5/6): 다중 포맷 문서 파이프라인 | [ko](./content/document-ingestion-101/ko/05-multi-format-pipeline.md) | [en](./content/document-ingestion-101/en/05-multi-format-pipeline.md) | [medium](./content/document-ingestion-101/medium/05.html) | Publish Ready |
| 6 | Document Ingestion 101 (6/6): 문서 수집 파이프라인 완성 | [ko](./content/document-ingestion-101/ko/06-pipeline-completion.md) | [en](./content/document-ingestion-101/en/06-pipeline-completion.md) | [medium](./content/document-ingestion-101/medium/06.html) | Publish Ready |

### LangGraph 101 (`langgraph-101`)

그래프 에이전트, 체크포인트, 멀티에이전트 — 6부작.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/langgraph-101/`](./content/langgraph-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | LangGraph 101 (1/6): LangGraph 소개와 그래프 기초 | [ko](./content/langgraph-101/ko/01-graph-basics.md) | [en](./content/langgraph-101/en/01-graph-basics.md) | [medium](./content/langgraph-101/medium/01.html) | Publish Ready |
| 2 | LangGraph 101 (2/6): 상태 관리와 체크포인트 | [ko](./content/langgraph-101/ko/02-state-and-checkpoints.md) | [en](./content/langgraph-101/en/02-state-and-checkpoints.md) | [medium](./content/langgraph-101/medium/02.html) | Publish Ready |
| 3 | LangGraph 101 (3/6): 조건부 엣지와 분기 흐름 | [ko](./content/langgraph-101/ko/03-conditional-edges.md) | [en](./content/langgraph-101/en/03-conditional-edges.md) | [medium](./content/langgraph-101/medium/03.html) | Publish Ready |
| 4 | LangGraph 101 (4/6): 도구 호출 에이전트 | [ko](./content/langgraph-101/ko/04-tool-calling-agent.md) | [en](./content/langgraph-101/en/04-tool-calling-agent.md) | [medium](./content/langgraph-101/medium/04.html) | Publish Ready |
| 5 | LangGraph 101 (5/6): 멀티 에이전트 시스템 | [ko](./content/langgraph-101/ko/05-multi-agent.md) | [en](./content/langgraph-101/en/05-multi-agent.md) | [medium](./content/langgraph-101/medium/05.html) | Publish Ready |
| 6 | LangGraph 101 (6/6): LangGraph 완성 | [ko](./content/langgraph-101/ko/06-langgraph-complete.md) | [en](./content/langgraph-101/en/06-langgraph-complete.md) | [medium](./content/langgraph-101/medium/06.html) | Publish Ready |

### AI Agent 101 (`ai-agent-101`)

AI Agent의 개념부터 Context Engineering, Tool Use, Workflow, Multi-Agent, Evaluation, 운영까지 배우는 실전 입문 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/ai-agent-101/`](./content/ai-agent-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | AI Agent 101 (1/10): AI Agent란 무엇인가? | [ko](./content/ai-agent-101/ko/01-what-is-an-ai-agent.md) | [en](./content/ai-agent-101/en/01-what-is-an-ai-agent.md) | [medium](./content/ai-agent-101/medium/01.html) | Publish Ready |
| 2 | AI Agent 101 (2/10): 컨텍스트 엔지니어링 | [ko](./content/ai-agent-101/ko/02-context-engineering.md) | [en](./content/ai-agent-101/en/02-context-engineering.md) | [medium](./content/ai-agent-101/medium/02.html) | Publish Ready |
| 3 | AI Agent 101 (3/10): Tool Use 기초 | [ko](./content/ai-agent-101/ko/03-tool-use-fundamentals.md) | [en](./content/ai-agent-101/en/03-tool-use-fundamentals.md) | [medium](./content/ai-agent-101/medium/03.html) | Publish Ready |
| 4 | AI Agent 101 (4/10): Agent Workflow 설계 | [ko](./content/ai-agent-101/ko/04-agent-workflow-design.md) | [en](./content/ai-agent-101/en/04-agent-workflow-design.md) | [medium](./content/ai-agent-101/medium/04.html) | Publish Ready |
| 5 | AI Agent 101 (5/10): Memory와 State | [ko](./content/ai-agent-101/ko/05-memory-and-state.md) | [en](./content/ai-agent-101/en/05-memory-and-state.md) | [medium](./content/ai-agent-101/medium/05.html) | Publish Ready |
| 6 | AI Agent 101 (6/10): Multi-Agent 시스템 | [ko](./content/ai-agent-101/ko/06-multi-agent-systems.md) | [en](./content/ai-agent-101/en/06-multi-agent-systems.md) | [medium](./content/ai-agent-101/medium/06.html) | Publish Ready |
| 7 | AI Agent 101 (7/10): Agent 평가 | [ko](./content/ai-agent-101/ko/07-agent-evaluation.md) | [en](./content/ai-agent-101/en/07-agent-evaluation.md) | [medium](./content/ai-agent-101/medium/07.html) | Publish Ready |
| 8 | AI Agent 101 (8/10): 에러 처리와 안정성 | [ko](./content/ai-agent-101/ko/08-error-handling-reliability.md) | [en](./content/ai-agent-101/en/08-error-handling-reliability.md) | [medium](./content/ai-agent-101/medium/08.html) | Publish Ready |
| 9 | AI Agent 101 (9/10): 운영 | [ko](./content/ai-agent-101/ko/09-production-operations.md) | [en](./content/ai-agent-101/en/09-production-operations.md) | [medium](./content/ai-agent-101/medium/09.html) | Publish Ready |
| 10 | AI Agent 101 (10/10): 첫 Agent 만들기 | [ko](./content/ai-agent-101/ko/10-building-first-agent.md) | [en](./content/ai-agent-101/en/10-building-first-agent.md) | [medium](./content/ai-agent-101/medium/10.html) | Publish Ready |

### Harness Engineering 101 (`harness-engineering-101`)

AI Agent가 안정적으로 작업하도록 task, context, constraint, tool, test, feedback, approval, observability, production harness를 설계하는 입문 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/harness-engineering-101/`](./content/harness-engineering-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Harness Engineering 101 (1/10): Harness Engineering이란 무엇인가? | [ko](./content/harness-engineering-101/ko/01-what-is-harness-engineering.md) | [en](./content/harness-engineering-101/en/01-what-is-harness-engineering.md) | [medium](./content/harness-engineering-101/medium/01.html) | Publish Ready |
| 2 | Harness Engineering 101 (2/10): Task Harness — 모호한 일을 실행 가능한 작업으로 바꾸기 | [ko](./content/harness-engineering-101/ko/02-task-harness.md) | [en](./content/harness-engineering-101/en/02-task-harness.md) | [medium](./content/harness-engineering-101/medium/02.html) | Publish Ready |
| 3 | Harness Engineering 101 (3/10): Context Harness — Agent에게 줄 정보와 숨길 정보 설계하기 | [ko](./content/harness-engineering-101/ko/03-context-harness.md) | [en](./content/harness-engineering-101/en/03-context-harness.md) | [medium](./content/harness-engineering-101/medium/03.html) | Publish Ready |
| 4 | Harness Engineering 101 (4/10): Constraint Harness — 규칙, 경계, 금지 행동 정의하기 | [ko](./content/harness-engineering-101/ko/04-constraint-harness.md) | [en](./content/harness-engineering-101/en/04-constraint-harness.md) | [medium](./content/harness-engineering-101/medium/04.html) | Publish Ready |
| 5 | Harness Engineering 101 (5/10): Tool Harness — Agent가 사용할 도구를 안전하게 설계하기 | [ko](./content/harness-engineering-101/ko/05-tool-harness.md) | [en](./content/harness-engineering-101/en/05-tool-harness.md) | [medium](./content/harness-engineering-101/medium/05.html) | Publish Ready |
| 6 | Harness Engineering 101 (6/10): Test Harness — 완료 조건을 테스트로 고정하기 | [ko](./content/harness-engineering-101/ko/06-test-harness.md) | [en](./content/harness-engineering-101/en/06-test-harness.md) | [medium](./content/harness-engineering-101/medium/06.html) | Publish Ready |
| 7 | Harness Engineering 101 (7/10): Feedback Loop — 실패를 고치게 만드는 반복 구조 | [ko](./content/harness-engineering-101/ko/07-feedback-loop.md) | [en](./content/harness-engineering-101/en/07-feedback-loop.md) | [medium](./content/harness-engineering-101/medium/07.html) | Publish Ready |
| 8 | Harness Engineering 101 (8/10): Approval Gate — 사람 승인이 필요한 지점 설계하기 | [ko](./content/harness-engineering-101/ko/08-approval-gate.md) | [en](./content/harness-engineering-101/en/08-approval-gate.md) | [medium](./content/harness-engineering-101/medium/08.html) | Publish Ready |
| 9 | Harness Engineering 101 (9/10): Observability — Agent 작업을 추적하고 재현하기 | [ko](./content/harness-engineering-101/ko/09-observability.md) | [en](./content/harness-engineering-101/en/09-observability.md) | [medium](./content/harness-engineering-101/medium/09.html) | Publish Ready |
| 10 | Harness Engineering 101 (10/10): Production Harness — 운영 가능한 Agent 작업 환경 만들기 | [ko](./content/harness-engineering-101/ko/10-production-harness.md) | [en](./content/harness-engineering-101/en/10-production-harness.md) | [medium](./content/harness-engineering-101/medium/10.html) | Publish Ready |

### AI Evaluation 101 (`ai-evaluation-101`)

LLM 애플리케이션을 정량적으로 평가하는 방법을 배우는 입문 시리즈. 평가 데이터셋 설계, 자동 채점, LLM-as-judge, 회귀 테스트, A/B 비교, 운영 평가까지 다룹니다.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/ai-evaluation-101/`](./content/ai-evaluation-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | AI Evaluation 101 (1/10): 왜 LLM 애플리케이션을 평가해야 하는가 | [ko](./content/ai-evaluation-101/ko/01-why-evaluate-llm-apps.md) | [en](./content/ai-evaluation-101/en/01-why-evaluate-llm-apps.md) | [medium](./content/ai-evaluation-101/medium/01.html) | Content Ready |
| 2 | AI Evaluation 101 (2/10): 평가 데이터셋 설계하기 | [ko](./content/ai-evaluation-101/ko/02-evaluation-dataset-design.md) | [en](./content/ai-evaluation-101/en/02-evaluation-dataset-design.md) | [medium](./content/ai-evaluation-101/medium/02.html) | Content Ready |
| 3 | AI Evaluation 101 (3/10): 결정적 지표 | [ko](./content/ai-evaluation-101/ko/03-deterministic-metrics.md) | [en](./content/ai-evaluation-101/en/03-deterministic-metrics.md) | [medium](./content/ai-evaluation-101/medium/03.html) | Content Ready |
| 4 | AI Evaluation 101 (4/10): LLM-as-Judge — 모델로 모델을 평가하기 | [ko](./content/ai-evaluation-101/ko/04-llm-as-judge.md) | [en](./content/ai-evaluation-101/en/04-llm-as-judge.md) | [medium](./content/ai-evaluation-101/medium/04.html) | Content Ready |
| 5 | AI Evaluation 101 (5/10): Rubric 기반 채점 설계 | [ko](./content/ai-evaluation-101/ko/05-rubric-based-scoring.md) | [en](./content/ai-evaluation-101/en/05-rubric-based-scoring.md) | [medium](./content/ai-evaluation-101/medium/05.html) | Content Ready |
| 6 | AI Evaluation 101 (6/10): RAG 시스템 평가하기 | [ko](./content/ai-evaluation-101/ko/06-rag-evaluation.md) | [en](./content/ai-evaluation-101/en/06-rag-evaluation.md) | [medium](./content/ai-evaluation-101/medium/06.html) | Content Ready |
| 7 | AI Evaluation 101 (7/10): 에이전트 평가하기 — 단일 응답이 아닌 trajectory | [ko](./content/ai-evaluation-101/ko/07-agent-evaluation.md) | [en](./content/ai-evaluation-101/en/07-agent-evaluation.md) | [medium](./content/ai-evaluation-101/medium/07.html) | Content Ready |
| 8 | AI Evaluation 101 (8/10): 회귀 테스트 — 어제 잘 되던 게 오늘 망가지지 않게 | [ko](./content/ai-evaluation-101/ko/08-regression-testing.md) | [en](./content/ai-evaluation-101/en/08-regression-testing.md) | [medium](./content/ai-evaluation-101/medium/08.html) | Content Ready |
| 9 | AI Evaluation 101 (9/10): LLM A/B 테스팅 — 어느 prompt가 더 나은가 | [ko](./content/ai-evaluation-101/ko/09-ab-testing-llms.md) | [en](./content/ai-evaluation-101/en/09-ab-testing-llms.md) | [medium](./content/ai-evaluation-101/medium/09.html) | Content Ready |
| 10 | AI Evaluation 101 (10/10): 운영 환경에서의 지속적 평가 | [ko](./content/ai-evaluation-101/ko/10-production-evaluation.md) | [en](./content/ai-evaluation-101/en/10-production-evaluation.md) | [medium](./content/ai-evaluation-101/medium/10.html) | Content Ready |

### AI Safety & Guardrails 101 (`ai-safety-guardrails-101`)

LLM 애플리케이션에 안전 장치를 적용하는 방법을 배우는 입문 시리즈. Prompt injection 방어, 출력 필터링, PII 감지, jailbreak 탐지, hallucination 방지, 감사 로깅까지 다룹니다.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/ai-safety-guardrails-101/`](./content/ai-safety-guardrails-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | AI Safety & Guardrails 101 (1/10): AI Safety가 왜 중요한가 | [ko](./content/ai-safety-guardrails-101/ko/01-why-ai-safety-matters.md) | [en](./content/ai-safety-guardrails-101/en/01-why-ai-safety-matters.md) | [medium](./content/ai-safety-guardrails-101/medium/01.html) | Content Ready |
| 2 | AI Safety & Guardrails 101 (2/10): Prompt Injection 방어 | [ko](./content/ai-safety-guardrails-101/ko/02-prompt-injection-defense.md) | [en](./content/ai-safety-guardrails-101/en/02-prompt-injection-defense.md) | [medium](./content/ai-safety-guardrails-101/medium/02.html) | Content Ready |
| 3 | AI Safety & Guardrails 101 (3/10): 출력 필터링과 콘텐츠 모더레이션 | [ko](./content/ai-safety-guardrails-101/ko/03-output-filtering.md) | [en](./content/ai-safety-guardrails-101/en/03-output-filtering.md) | [medium](./content/ai-safety-guardrails-101/medium/03.html) | Content Ready |
| 4 | AI Safety & Guardrails 101 (4/10): PII 감지와 마스킹 | [ko](./content/ai-safety-guardrails-101/ko/04-pii-detection-redaction.md) | [en](./content/ai-safety-guardrails-101/en/04-pii-detection-redaction.md) | [medium](./content/ai-safety-guardrails-101/medium/04.html) | Content Ready |
| 5 | AI Safety & Guardrails 101 (5/10): Jailbreak 탐지 | [ko](./content/ai-safety-guardrails-101/ko/05-jailbreak-detection.md) | [en](./content/ai-safety-guardrails-101/en/05-jailbreak-detection.md) | [medium](./content/ai-safety-guardrails-101/medium/05.html) | Content Ready |
| 6 | AI Safety & Guardrails 101 (6/10): 독성과 편향 탐지 | [ko](./content/ai-safety-guardrails-101/ko/06-toxicity-bias-detection.md) | [en](./content/ai-safety-guardrails-101/en/06-toxicity-bias-detection.md) | [medium](./content/ai-safety-guardrails-101/medium/06.html) | Content Ready |
| 7 | AI Safety & Guardrails 101 (7/10): Hallucination Guardrail — Grounding 검증 | [ko](./content/ai-safety-guardrails-101/ko/07-hallucination-guardrails.md) | [en](./content/ai-safety-guardrails-101/en/07-hallucination-guardrails.md) | [medium](./content/ai-safety-guardrails-101/medium/07.html) | Content Ready |
| 8 | AI Safety & Guardrails 101 (8/10): Rate Limiting과 남용 방지 | [ko](./content/ai-safety-guardrails-101/ko/08-rate-limiting-abuse-prevention.md) | [en](./content/ai-safety-guardrails-101/en/08-rate-limiting-abuse-prevention.md) | [medium](./content/ai-safety-guardrails-101/medium/08.html) | Content Ready |
| 9 | AI Safety & Guardrails 101 (9/10): 감사 로깅과 컴플라이언스 | [ko](./content/ai-safety-guardrails-101/ko/09-audit-logging-compliance.md) | [en](./content/ai-safety-guardrails-101/en/09-audit-logging-compliance.md) | [medium](./content/ai-safety-guardrails-101/medium/09.html) | Content Ready |
| 10 | AI Safety & Guardrails 101 (10/10): 운영 가드레일 시스템 구축 | [ko](./content/ai-safety-guardrails-101/ko/10-production-guardrail-system.md) | [en](./content/ai-safety-guardrails-101/en/10-production-guardrail-system.md) | [medium](./content/ai-safety-guardrails-101/medium/10.html) | Content Ready |

### LLM 앱 운영 101 / LLM Apps Ops 101 (`llm-apps-ops-101`)

관측, 평가, 비용, 보안, 배포 — 6부작.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/llm-apps-ops-101/`](./content/llm-apps-ops-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | LLM Apps Ops 101 (1/6): LLM 앱 모니터링과 로깅 | [ko](./content/llm-apps-ops-101/ko/01-monitoring-and-logging.md) | [en](./content/llm-apps-ops-101/en/01-monitoring-and-logging.md) | [medium](./content/llm-apps-ops-101/medium/01.html) | Publish Ready |
| 2 | LLM Apps Ops 101 (2/6): LLM 비용 추적과 최적화 | [ko](./content/llm-apps-ops-101/ko/02-cost-tracking.md) | [en](./content/llm-apps-ops-101/en/02-cost-tracking.md) | [medium](./content/llm-apps-ops-101/medium/02.html) | Publish Ready |
| 3 | LLM Apps Ops 101 (3/6): LLM 출력 품질 평가 | [ko](./content/llm-apps-ops-101/ko/03-evaluation.md) | [en](./content/llm-apps-ops-101/en/03-evaluation.md) | [medium](./content/llm-apps-ops-101/medium/03.html) | Publish Ready |
| 4 | LLM Apps Ops 101 (4/6): LLM 앱 보안 | [ko](./content/llm-apps-ops-101/ko/04-security.md) | [en](./content/llm-apps-ops-101/en/04-security.md) | [medium](./content/llm-apps-ops-101/medium/04.html) | Publish Ready |
| 5 | LLM Apps Ops 101 (5/6): LLM 앱 배포 전략 | [ko](./content/llm-apps-ops-101/ko/05-deployment.md) | [en](./content/llm-apps-ops-101/en/05-deployment.md) | [medium](./content/llm-apps-ops-101/medium/05.html) | Publish Ready |
| 6 | LLM Apps Ops 101 (6/6): LLM 앱 운영 완성 | [ko](./content/llm-apps-ops-101/ko/06-ops-complete.md) | [en](./content/llm-apps-ops-101/en/06-ops-complete.md) | [medium](./content/llm-apps-ops-101/medium/06.html) | Publish Ready |

### AI Data Preparation 101 (`ai-data-preparation-101`)

AI 모델을 위한 데이터 준비 전 과정을 다루는 입문 시리즈. 수집, 정제, PII 익명화, 토큰화, 품질 필터링, 합성 데이터, 분할과 오염 통제, 프로덕션 파이프라인까지 배웁니다.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/ai-data-preparation-101/`](./content/ai-data-preparation-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | AI Data Preparation 101 (1/10): 데이터 준비가 모델 품질을 결정하는 이유 | [ko](./content/ai-data-preparation-101/ko/01-why-data-preparation-matters.md) | [en](./content/ai-data-preparation-101/en/01-why-data-preparation-matters.md) | [medium](./content/ai-data-preparation-101/medium/01.html) | Publish Ready |
| 2 | AI Data Preparation 101 (2/10): 원본 데이터 수집과 카탈로깅 | [ko](./content/ai-data-preparation-101/ko/02-source-data-collection-cataloging.md) | [en](./content/ai-data-preparation-101/en/02-source-data-collection-cataloging.md) | [medium](./content/ai-data-preparation-101/medium/02.html) | Publish Ready |
| 3 | AI Data Preparation 101 (3/10): 데이터 정제와 중복 제거 | [ko](./content/ai-data-preparation-101/ko/03-cleaning-deduplication.md) | [en](./content/ai-data-preparation-101/en/03-cleaning-deduplication.md) | [medium](./content/ai-data-preparation-101/medium/03.html) | Publish Ready |
| 4 | AI Data Preparation 101 (4/10): 학습 데이터 PII 탐지와 익명화 | [ko](./content/ai-data-preparation-101/ko/04-pii-detection-anonymization.md) | [en](./content/ai-data-preparation-101/en/04-pii-detection-anonymization.md) | [medium](./content/ai-data-preparation-101/medium/04.html) | Publish Ready |
| 5 | AI Data Preparation 101 (5/10): Tokenization과 Chunking 전략 | [ko](./content/ai-data-preparation-101/ko/05-tokenization-chunking.md) | [en](./content/ai-data-preparation-101/en/05-tokenization-chunking.md) | [medium](./content/ai-data-preparation-101/medium/05.html) | Publish Ready |
| 6 | AI Data Preparation 101 (6/10): 데이터 품질 필터링 — Heuristic과 Classifier | [ko](./content/ai-data-preparation-101/ko/06-quality-filtering.md) | [en](./content/ai-data-preparation-101/en/06-quality-filtering.md) | [medium](./content/ai-data-preparation-101/medium/06.html) | Publish Ready |
| 7 | AI Data Preparation 101 (7/10): 합성 데이터 생성 — Self-Instruct부터 Distillation까지 | [ko](./content/ai-data-preparation-101/ko/07-synthetic-data-generation.md) | [en](./content/ai-data-preparation-101/en/07-synthetic-data-generation.md) | [medium](./content/ai-data-preparation-101/medium/07.html) | Publish Ready |
| 8 | AI Data Preparation 101 (8/10): 데이터 증강 기법 — EDA부터 Back-Translation까지 | [ko](./content/ai-data-preparation-101/ko/08-data-augmentation.md) | [en](./content/ai-data-preparation-101/en/08-data-augmentation.md) | [medium](./content/ai-data-preparation-101/medium/08.html) | Publish Ready |
| 9 | AI Data Preparation 101 (9/10): 학습/평가/테스트 분할과 Contamination 통제 | [ko](./content/ai-data-preparation-101/ko/09-train-eval-test-splitting.md) | [en](./content/ai-data-preparation-101/en/09-train-eval-test-splitting.md) | [medium](./content/ai-data-preparation-101/medium/09.html) | Publish Ready |
| 10 | AI Data Preparation 101 (10/10): 프로덕션 데이터 파이프라인 구축 | [ko](./content/ai-data-preparation-101/ko/10-production-data-pipeline.md) | [en](./content/ai-data-preparation-101/en/10-production-data-pipeline.md) | [medium](./content/ai-data-preparation-101/medium/10.html) | Publish Ready |

### LLM 파인튜닝 101 / LLM Fine-tuning 101 (`llm-finetuning-101`)

LoRA, 데이터셋, 서빙 — 6부작 (선택).

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/llm-finetuning-101/`](./content/llm-finetuning-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | LLM Fine-tuning 101 (1/6): LLM 파인튜닝 입문 | [ko](./content/llm-finetuning-101/ko/01-intro.md) | [en](./content/llm-finetuning-101/en/01-intro.md) | [medium](./content/llm-finetuning-101/medium/01.html) | Publish Ready |
| 2 | LLM Fine-tuning 101 (2/6): 데이터셋 준비와 전처리 | [ko](./content/llm-finetuning-101/ko/02-dataset.md) | [en](./content/llm-finetuning-101/en/02-dataset.md) | [medium](./content/llm-finetuning-101/medium/02.html) | Publish Ready |
| 3 | LLM Fine-tuning 101 (3/6): LoRA 어댑터 구성 | [ko](./content/llm-finetuning-101/ko/03-lora.md) | [en](./content/llm-finetuning-101/en/03-lora.md) | [medium](./content/llm-finetuning-101/medium/03.html) | Publish Ready |
| 4 | LLM Fine-tuning 101 (4/6): 학습 루프와 하이퍼파라미터 | [ko](./content/llm-finetuning-101/ko/04-training.md) | [en](./content/llm-finetuning-101/en/04-training.md) | [medium](./content/llm-finetuning-101/medium/04.html) | Publish Ready |
| 5 | LLM Fine-tuning 101 (5/6): 모델 평가 | [ko](./content/llm-finetuning-101/ko/05-evaluation.md) | [en](./content/llm-finetuning-101/en/05-evaluation.md) | [medium](./content/llm-finetuning-101/medium/05.html) | Publish Ready |
| 6 | LLM Fine-tuning 101 (6/6): 모델 서빙 | [ko](./content/llm-finetuning-101/ko/06-serving.md) | [en](./content/llm-finetuning-101/en/06-serving.md) | [medium](./content/llm-finetuning-101/medium/06.html) | Publish Ready |

### LLM from Scratch 101 (`llm-from-scratch-101`)

PyTorch 2.x 로 토크나이저부터 챗봇까지, ~720 LOC 의 작은 GPT 9부작.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/llm-from-scratch-101/`](./content/llm-from-scratch-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | LLM from Scratch 101 (1/9): 글자를 숫자로 바꾸기 | [ko](./content/llm-from-scratch-101/ko/01-tokenizer.md) | [en](./content/llm-from-scratch-101/en/01-tokenizer.md) | [medium](./content/llm-from-scratch-101/medium/01.html) | Draft |
| 2 | LLM from Scratch 101 (2/9): 정수에서 벡터로, 그리고 위치 | [ko](./content/llm-from-scratch-101/ko/02-embedding.md) | [en](./content/llm-from-scratch-101/en/02-embedding.md) | [medium](./content/llm-from-scratch-101/medium/02.html) | Draft |
| 3 | LLM from Scratch 101 (3/9): 어떤 토큰을 얼마나 볼지 스스로 정하기 | [ko](./content/llm-from-scratch-101/ko/03-attention.md) | [en](./content/llm-from-scratch-101/en/03-attention.md) | [medium](./content/llm-from-scratch-101/medium/03.html) | Draft |
| 4 | LLM from Scratch 101 (4/9): 블록 하나, 깊이의 단위 | [ko](./content/llm-from-scratch-101/ko/04-transformer-block.md) | [en](./content/llm-from-scratch-101/en/04-transformer-block.md) | [medium](./content/llm-from-scratch-101/medium/04.html) | Draft |
| 5 | LLM from Scratch 101 (5/9): 조립: GPT 모델 클래스 완성 | [ko](./content/llm-from-scratch-101/ko/05-gpt-model.md) | [en](./content/llm-from-scratch-101/en/05-gpt-model.md) | [medium](./content/llm-from-scratch-101/medium/05.html) | Draft |
| 6 | LLM from Scratch 101 (6/9): 기울기로 배우기 | [ko](./content/llm-from-scratch-101/ko/06-training-loop.md) | [en](./content/llm-from-scratch-101/en/06-training-loop.md) | [medium](./content/llm-from-scratch-101/medium/06.html) | Draft |
| 7 | LLM from Scratch 101 (7/9): 샘플링 — 학습된 모델에서 글 뽑아내기 | [ko](./content/llm-from-scratch-101/ko/07-inference.md) | [en](./content/llm-from-scratch-101/en/07-inference.md) | [medium](./content/llm-from-scratch-101/medium/07.html) | Draft |
| 8 | LLM from Scratch 101 (8/9): 베이스 모델을 우리 작업에 맞추기 | [ko](./content/llm-from-scratch-101/ko/08-finetuning.md) | [en](./content/llm-from-scratch-101/en/08-finetuning.md) | [medium](./content/llm-from-scratch-101/medium/08.html) | Draft |
| 9 | LLM from Scratch 101 (9/9): 직접 만든 LLM을 챗봇으로 — FastAPI + 스트리밍 | [ko](./content/llm-from-scratch-101/ko/09-chatbot-wrapper.md) | [en](./content/llm-from-scratch-101/en/09-chatbot-wrapper.md) | [medium](./content/llm-from-scratch-101/medium/09.html) | Draft |

### Multimodal AI 101 (`multimodal-ai-101`)

텍스트 + 이미지 + 오디오 + 영상을 다루는 multimodal AI 입문 시리즈. CLIP, ViT, VLM, Whisper, Diffusion, multimodal RAG, video understanding을 production 관점에서 배웁니다.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, mkdocs, ebook
- 경로: [`content/multimodal-ai-101/`](./content/multimodal-ai-101/)

| # | Title | KO | EN | Status |
| --- | --- | --- | --- | --- |
| 1 | Multimodal AI 101 (1/10): Multimodal AI가 중요한 이유 | [ko](./content/multimodal-ai-101/ko/01-why-multimodal-matters.md) | [en](./content/multimodal-ai-101/en/01-why-multimodal-matters.md) | Publish Ready |
| 2 | Multimodal AI 101 (2/10): Image Encoder: CLIP과 ViT | [ko](./content/multimodal-ai-101/ko/02-image-encoders-clip-vit.md) | [en](./content/multimodal-ai-101/en/02-image-encoders-clip-vit.md) | Publish Ready |
| 3 | Multimodal AI 101 (3/10): Vision-Language Model 아키텍처 | [ko](./content/multimodal-ai-101/ko/03-vlm-architecture.md) | [en](./content/multimodal-ai-101/en/03-vlm-architecture.md) | Publish Ready |
| 4 | Multimodal AI 101 (4/10): Image Captioning과 OCR 파이프라인 | [ko](./content/multimodal-ai-101/ko/04-captioning-ocr-pipelines.md) | [en](./content/multimodal-ai-101/en/04-captioning-ocr-pipelines.md) | Publish Ready |
| 5 | Multimodal AI 101 (5/10): Multimodal RAG: 이미지와 텍스트를 함께 검색하기 | [ko](./content/multimodal-ai-101/ko/05-multimodal-rag.md) | [en](./content/multimodal-ai-101/en/05-multimodal-rag.md) | Publish Ready |
| 6 | Multimodal AI 101 (6/10): 오디오 처리와 Whisper STT | [ko](./content/multimodal-ai-101/ko/06-audio-whisper.md) | [en](./content/multimodal-ai-101/en/06-audio-whisper.md) | Content Ready |
| 7 | Multimodal AI 101 (7/10): Diffusion으로 Text-to-Image 생성 | [ko](./content/multimodal-ai-101/ko/07-text-to-image-diffusion.md) | [en](./content/multimodal-ai-101/en/07-text-to-image-diffusion.md) | Content Ready |
| 8 | Multimodal AI 101 (8/10): Multimodal Embedding과 Cross-modal 검색 | [ko](./content/multimodal-ai-101/ko/08-multimodal-embeddings.md) | [en](./content/multimodal-ai-101/en/08-multimodal-embeddings.md) | Content Ready |
| 9 | Multimodal AI 101 (9/10): Video 이해 - Frame Sampling에서 Video-LLaVA까지 | [ko](./content/multimodal-ai-101/ko/09-video-understanding.md) | [en](./content/multimodal-ai-101/en/09-video-understanding.md) | Publish Ready |
| 10 | Multimodal AI 101 (10/10): Production Multimodal Application 구축 | [ko](./content/multimodal-ai-101/ko/10-production-multimodal-app.md) | [en](./content/multimodal-ai-101/en/10-production-multimodal-app.md) | Content Ready |

### 한국어 AI 스택 101 / Korean AI Stack 101 (`korean-ai-stack-101`)

한국어 임베딩, OCR, 국내 LLM API — 6부작.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/korean-ai-stack-101/`](./content/korean-ai-stack-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Korean AI Stack 101 (1/6): 한국어 임베딩 모델 비교 — KoSimCSE, BGE-M3, Solar | [ko](./content/korean-ai-stack-101/ko/01-korean-embedding-models.md) | [en](./content/korean-ai-stack-101/en/01-korean-embedding-models.md) | [medium](./content/korean-ai-stack-101/medium/01.html) | Publish Ready |
| 2 | Korean AI Stack 101 (2/6): KoSimCSE로 문장 유사도 구현하기 | [ko](./content/korean-ai-stack-101/ko/02-kosimcse-similarity.md) | [en](./content/korean-ai-stack-101/en/02-kosimcse-similarity.md) | [medium](./content/korean-ai-stack-101/medium/02.html) | Publish Ready |
| 3 | Korean AI Stack 101 (3/6): BGE-M3 다국어 임베딩 실전 | [ko](./content/korean-ai-stack-101/ko/03-bge-m3-multilingual.md) | [en](./content/korean-ai-stack-101/en/03-bge-m3-multilingual.md) | [medium](./content/korean-ai-stack-101/medium/03.html) | Publish Ready |
| 4 | Korean AI Stack 101 (4/6): CLOVA OCR API로 문서 텍스트 추출 | [ko](./content/korean-ai-stack-101/ko/04-clova-ocr.md) | [en](./content/korean-ai-stack-101/en/04-clova-ocr.md) | [medium](./content/korean-ai-stack-101/medium/04.html) | Publish Ready |
| 5 | Korean AI Stack 101 (5/6): HyperCLOVA X와 Solar API 사용하기 | [ko](./content/korean-ai-stack-101/ko/05-hyperclova-solar-api.md) | [en](./content/korean-ai-stack-101/en/05-hyperclova-solar-api.md) | [medium](./content/korean-ai-stack-101/medium/05.html) | Publish Ready |
| 6 | Korean AI Stack 101 (6/6): 한국어 RAG 파이프라인 조합하기 | [ko](./content/korean-ai-stack-101/ko/06-korean-rag-pipeline.md) | [en](./content/korean-ai-stack-101/en/06-korean-rag-pipeline.md) | [medium](./content/korean-ai-stack-101/medium/06.html) | Publish Ready |

### AI 이미지 생성 101 / AI Image Generation 101 (`ai-image-gen-101`)

ChatGPT 이미지 생성 프롬프트 엔지니어링 기초부터 심화까지 — 스타일, 구도, 색감, 장면 설계, 실전 워크플로우 10부작.

- 상태: **Draft**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs
- 경로: [`content/ai-image-gen-101/`](./content/ai-image-gen-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | AI 이미지 생성 101 (1/10): 첫 이미지 생성하기 | [ko](./content/ai-image-gen-101/ko/01-first-image-generation.md) | [en](./content/ai-image-gen-101/en/01-first-image-generation.md) | [medium](./content/ai-image-gen-101/medium/01.html) | Draft |
| 2 | AI 이미지 생성 101 (2/10): 좋은 프롬프트의 구조 | [ko](./content/ai-image-gen-101/ko/02-prompt-structure.md) | [en](./content/ai-image-gen-101/en/02-prompt-structure.md) | [medium](./content/ai-image-gen-101/medium/02.html) | Draft |
| 3 | AI 이미지 생성 101 (3/10): 스타일 마스터하기 | [ko](./content/ai-image-gen-101/ko/03-mastering-styles.md) | [en](./content/ai-image-gen-101/en/03-mastering-styles.md) | [medium](./content/ai-image-gen-101/medium/03.html) | Draft |
| 4 | AI 이미지 생성 101 (4/10): 구도와 시점 | [ko](./content/ai-image-gen-101/ko/04-composition-and-perspective.md) | [en](./content/ai-image-gen-101/en/04-composition-and-perspective.md) | [medium](./content/ai-image-gen-101/medium/04.html) | Draft |
| 5 | AI 이미지 생성 101 (5/10): 색감과 조명 | [ko](./content/ai-image-gen-101/ko/05-color-and-lighting.md) | [en](./content/ai-image-gen-101/en/05-color-and-lighting.md) | [medium](./content/ai-image-gen-101/medium/05.html) | Draft |
| 6 | AI 이미지 생성 101 (6/10): 복잡한 장면 설계하기 | [ko](./content/ai-image-gen-101/ko/06-complex-scene-design.md) | [en](./content/ai-image-gen-101/en/06-complex-scene-design.md) | [medium](./content/ai-image-gen-101/medium/06.html) | Draft |
| 7 | AI 이미지 생성 101 (7/10): 일관성 유지하기 | [ko](./content/ai-image-gen-101/ko/07-consistency-across-images.md) | [en](./content/ai-image-gen-101/en/07-consistency-across-images.md) | [medium](./content/ai-image-gen-101/medium/07.html) | Draft |
| 8 | AI 이미지 생성 101 (8/10): 텍스트와 타이포그래피 | [ko](./content/ai-image-gen-101/ko/08-text-and-typography.md) | [en](./content/ai-image-gen-101/en/08-text-and-typography.md) | [medium](./content/ai-image-gen-101/medium/08.html) | Draft |
| 9 | AI 이미지 생성 101 (9/10): 레퍼런스 이미지 활용 | [ko](./content/ai-image-gen-101/ko/09-reference-image-editing.md) | [en](./content/ai-image-gen-101/en/09-reference-image-editing.md) | [medium](./content/ai-image-gen-101/medium/09.html) | Draft |
| 10 | AI 이미지 생성 101 (10/10): 실전 워크플로우 | [ko](./content/ai-image-gen-101/ko/10-production-workflow.md) | [en](./content/ai-image-gen-101/en/10-production-workflow.md) | [medium](./content/ai-image-gen-101/medium/10.html) | Draft |

### AI 웹 개발 입문 / AI Web Development 101 (`ai-web-dev-101`)

AI API 부터 배포까지, 초급 개발자를 위한 7부작.

- 상태: **Needs Update**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/ai-web-dev-101/`](./content/ai-web-dev-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | AI Web Development 101 (1/7): AI API 첫 걸음 — OpenAI API로 첫 번째 요청 보내기 | [ko](./content/ai-web-dev-101/ko/01-hello-ai-api.md) | [en](./content/ai-web-dev-101/en/01-hello-ai-api.md) | [medium](./content/ai-web-dev-101/medium/01.html) | Publish Ready |
| 2 | AI Web Development 101 (2/7): 프롬프트 엔지니어링 기초 — AI에게 원하는 답을 얻는 기술 | [ko](./content/ai-web-dev-101/ko/02-prompt-engineering.md) | [en](./content/ai-web-dev-101/en/02-prompt-engineering.md) | [medium](./content/ai-web-dev-101/medium/02.html) | Publish Ready |
| 3 | AI Web Development 101 (3/7): AI 챗봇 만들기 — Next.js와 Vercel AI SDK로 실시간 채팅 구현 | [ko](./content/ai-web-dev-101/ko/03-ai-chatbot.md) | [en](./content/ai-web-dev-101/en/03-ai-chatbot.md) | [medium](./content/ai-web-dev-101/medium/03.html) | Publish Ready |
| 4 | AI Web Development 101 (4/7): RAG 입문 — 내 데이터로 답하는 AI 만들기 | [ko](./content/ai-web-dev-101/ko/04-rag-intro.md) | [en](./content/ai-web-dev-101/en/04-rag-intro.md) | [medium](./content/ai-web-dev-101/medium/04.html) | Publish Ready |
| 5 | AI Web Development 101 (5/7): AI 에이전트 첫걸음 — Tool Use로 똑똑한 AI 만들기 | [ko](./content/ai-web-dev-101/ko/05-ai-agent.md) | [en](./content/ai-web-dev-101/en/05-ai-agent.md) | [medium](./content/ai-web-dev-101/medium/05.html) | Publish Ready |
| 6 | AI Web Development 101 (6/7): AI 웹 앱 배포하기: Vercel과 Azure에 올리고 운영하기 | [ko](./content/ai-web-dev-101/ko/06-deploy.md) | [en](./content/ai-web-dev-101/en/06-deploy.md) | [medium](./content/ai-web-dev-101/medium/06.html) | Publish Ready |
| 7 | AI Web Development 101 (7/7): AI 앱의 평가와 개선, 품질을 측정하고 더 좋게 만드는 법 | [ko](./content/ai-web-dev-101/ko/07-eval-improve.md) | [en](./content/ai-web-dev-101/en/07-eval-improve.md) | [medium](./content/ai-web-dev-101/medium/07.html) | Publish Ready |

---

## 프로그래밍

### Computer Science 101 (`computer-science-101`)

컴퓨터공학 전공에서 배우는 주요 과목들이 서로 어떻게 연결되는지 보여주는 입문 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/computer-science-101/`](./content/computer-science-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Computer Science 101 (1/10): Computer Science란 무엇인가? | [ko](./content/computer-science-101/ko/01-what-is-computer-science.md) | [en](./content/computer-science-101/en/01-what-is-computer-science.md) | [medium](./content/computer-science-101/medium/01.html) | Draft |
| 2 | Computer Science 101 (2/10): 계산과 프로그램 | [ko](./content/computer-science-101/ko/02-computation-and-programs.md) | [en](./content/computer-science-101/en/02-computation-and-programs.md) | [medium](./content/computer-science-101/medium/02.html) | Draft |
| 3 | Computer Science 101 (3/10): 데이터 표현 | [ko](./content/computer-science-101/ko/03-data-representation.md) | [en](./content/computer-science-101/en/03-data-representation.md) | [medium](./content/computer-science-101/medium/03.html) | Draft |
| 4 | Computer Science 101 (4/10): 알고리즘과 복잡도 | [ko](./content/computer-science-101/ko/04-algorithms-and-complexity.md) | [en](./content/computer-science-101/en/04-algorithms-and-complexity.md) | [medium](./content/computer-science-101/medium/04.html) | Draft |
| 5 | Computer Science 101 (5/10): 컴퓨터 구조 | [ko](./content/computer-science-101/ko/05-computer-architecture.md) | [en](./content/computer-science-101/en/05-computer-architecture.md) | [medium](./content/computer-science-101/medium/05.html) | Draft |
| 6 | Computer Science 101 (6/10): 운영체제 | [ko](./content/computer-science-101/ko/06-operating-systems.md) | [en](./content/computer-science-101/en/06-operating-systems.md) | [medium](./content/computer-science-101/medium/06.html) | Draft |
| 7 | Computer Science 101 (7/10): 네트워크 | [ko](./content/computer-science-101/ko/07-networks.md) | [en](./content/computer-science-101/en/07-networks.md) | [medium](./content/computer-science-101/medium/07.html) | Draft |
| 8 | Computer Science 101 (8/10): 데이터베이스 | [ko](./content/computer-science-101/ko/08-databases.md) | [en](./content/computer-science-101/en/08-databases.md) | [medium](./content/computer-science-101/medium/08.html) | Draft |
| 9 | Computer Science 101 (9/10): 소프트웨어 엔지니어링 | [ko](./content/computer-science-101/ko/09-software-engineering.md) | [en](./content/computer-science-101/en/09-software-engineering.md) | [medium](./content/computer-science-101/medium/09.html) | Draft |
| 10 | Computer Science 101 (10/10): AI와 데이터사이언스까지의 연결 | [ko](./content/computer-science-101/ko/10-ai-and-data-science.md) | [en](./content/computer-science-101/en/10-ai-and-data-science.md) | [medium](./content/computer-science-101/medium/10.html) | Draft |

### Python 101 (`python-101`)

Python을 처음 시작하는 사람을 위한 입문 시리즈. 설치와 venv부터 변수, 자료구조, 제어 흐름, 함수, 모듈, 파일 I/O와 예외, 클래스, 표준 라이브러리까지 다룹니다.

- 상태: **Draft**
- 언어: ko, en
- 발행 대상: tistory, hashnode, mkdocs, ebook
- 경로: [`content/python-101/`](./content/python-101/)

| # | Title | KO | EN | Status |
| --- | --- | --- | --- | --- |
| 1 | Python 101 (1/10): 왜 Python인가, 그리고 설치와 venv | [ko](./content/python-101/ko/01-why-python-and-install.md) | [en](./content/python-101/en/01-why-python-and-install.md) | Draft |
| 2 | Python 101 (2/10): 변수, 타입, 연산자 | [ko](./content/python-101/ko/02-variables-types-operators.md) | [en](./content/python-101/en/02-variables-types-operators.md) | Draft |
| 3 | Python 101 (3/10): 문자열과 포매팅 | [ko](./content/python-101/ko/03-strings-and-formatting.md) | [en](./content/python-101/en/03-strings-and-formatting.md) | Draft |
| 4 | Python 101 (4/10): list, tuple, set, dict | [ko](./content/python-101/ko/04-list-tuple-set-dict.md) | [en](./content/python-101/en/04-list-tuple-set-dict.md) | Draft |
| 5 | Python 101 (5/10): 제어 흐름: if, for, while, comprehension | [ko](./content/python-101/ko/05-control-flow.md) | [en](./content/python-101/en/05-control-flow.md) | Draft |
| 6 | Python 101 (6/10): 함수와 인자: def, args, kwargs, default, lambda | [ko](./content/python-101/ko/06-functions-and-arguments.md) | [en](./content/python-101/en/06-functions-and-arguments.md) | Draft |
| 7 | Python 101 (7/10): 모듈과 패키지: import, __init__, __name__ | [ko](./content/python-101/ko/07-modules-and-packages.md) | [en](./content/python-101/en/07-modules-and-packages.md) | Draft |
| 8 | Python 101 (8/10): 파일 I/O와 예외 처리 | [ko](./content/python-101/ko/08-file-io-and-exceptions.md) | [en](./content/python-101/en/08-file-io-and-exceptions.md) | Draft |
| 9 | Python 101 (9/10): 클래스와 객체: 데이터와 동작을 함께 묶기 | [ko](./content/python-101/ko/09-classes-and-objects.md) | [en](./content/python-101/en/09-classes-and-objects.md) | Draft |
| 10 | Python 101 (10/10): 표준 라이브러리 투어: datetime, pathlib, json, collections, itertools | [ko](./content/python-101/ko/10-standard-library-tour.md) | [en](./content/python-101/en/10-standard-library-tour.md) | Draft |

### Git & GitHub 101 (`git-github-101`)

Git의 commit, branch, merge, rebase, pull request, issue, GitHub workflow를 배우는 개발 협업 입문 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, mkdocs, ebook
- 경로: [`content/git-github-101/`](./content/git-github-101/)

| # | Title | KO | EN | Status |
| --- | --- | --- | --- | --- |
| 1 | Git & GitHub 101 (1/10): Git이란 무엇인가? 버전 관리의 시작 | [ko](./content/git-github-101/ko/01-what-is-git.md) | [en](./content/git-github-101/en/01-what-is-git.md) | Draft |
| 2 | Git & GitHub 101 (2/10): 첫 commit 만들기 - init, status, add, commit | [ko](./content/git-github-101/ko/02-first-commit.md) | [en](./content/git-github-101/en/02-first-commit.md) | Draft |
| 3 | Git & GitHub 101 (3/10): 변경 사항 확인하기 - status, diff, log로 읽기 | [ko](./content/git-github-101/ko/03-status-diff-log.md) | [en](./content/git-github-101/en/03-status-diff-log.md) | Draft |
| 4 | Git & GitHub 101 (4/10): branch 기초 - 만들고 옮기고 비교하기 | [ko](./content/git-github-101/ko/04-branch-basics.md) | [en](./content/git-github-101/en/04-branch-basics.md) | Draft |
| 5 | Git & GitHub 101 (5/10): merge와 conflict 해결하기 - 두 줄기를 다시 합치기 | [ko](./content/git-github-101/ko/05-merge-and-conflict.md) | [en](./content/git-github-101/en/05-merge-and-conflict.md) | Draft |
| 6 | Git & GitHub 101 (6/10): GitHub repository 만들기 - remote, push, pull 한 번에 익히기 | [ko](./content/git-github-101/ko/06-github-repository.md) | [en](./content/git-github-101/en/06-github-repository.md) | Draft |
| 7 | Git & GitHub 101 (7/10): Pull Request로 협업하기 - branch에서 review를 거쳐 main까지 | [ko](./content/git-github-101/ko/07-pull-request.md) | [en](./content/git-github-101/en/07-pull-request.md) | Draft |
| 8 | Git & GitHub 101 (8/10): Issue와 Project로 일감 관리하기 - GitHub에서 할 일을 추적하는 법 | [ko](./content/git-github-101/ko/08-issue-and-project.md) | [en](./content/git-github-101/en/08-issue-and-project.md) | Draft |
| 9 | Git & GitHub 101 (9/10): 좋은 commit message 쓰기: Conventional Commits와 좋은 본문 | [ko](./content/git-github-101/ko/09-good-commit-message.md) | [en](./content/git-github-101/en/09-good-commit-message.md) | Draft |
| 10 | Git & GitHub 101 (10/10): 실전 Git workflow 만들기: issue부터 release까지 한 흐름으로 | [ko](./content/git-github-101/ko/10-real-world-workflow.md) | [en](./content/git-github-101/en/10-real-world-workflow.md) | Draft |

### Linux CLI 101 (`linux-cli-101`)

파일 탐색, 권한, 프로세스, grep, pipe, shell script, SSH 등 개발자가 반드시 알아야 할 Linux CLI 기본기를 다루는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, mkdocs, ebook
- 경로: [`content/linux-cli-101/`](./content/linux-cli-101/)

| # | Title | KO | EN | Status |
| --- | --- | --- | --- | --- |
| 1 | Linux CLI 101 (1/10): CLI와 Shell이란 무엇인가? | [ko](./content/linux-cli-101/ko/01-what-is-cli-and-shell.md) | [en](./content/linux-cli-101/en/01-what-is-cli-and-shell.md) | Publish Ready |
| 2 | Linux CLI 101 (2/10): 파일과 디렉터리 다루기 | [ko](./content/linux-cli-101/ko/02-files-and-directories.md) | [en](./content/linux-cli-101/en/02-files-and-directories.md) | Publish Ready |
| 3 | Linux CLI 101 (3/10): 권한과 소유자 이해하기 | [ko](./content/linux-cli-101/ko/03-permissions-and-ownership.md) | [en](./content/linux-cli-101/en/03-permissions-and-ownership.md) | Publish Ready |
| 4 | Linux CLI 101 (4/10): cat, less, head, tail — 파일 내용 보기 | [ko](./content/linux-cli-101/ko/04-viewing-files.md) | [en](./content/linux-cli-101/en/04-viewing-files.md) | Publish Ready |
| 5 | Linux CLI 101 (5/10): grep, find, xargs — 검색의 삼총사 | [ko](./content/linux-cli-101/ko/05-grep-find-xargs.md) | [en](./content/linux-cli-101/en/05-grep-find-xargs.md) | Publish Ready |
| 6 | Linux CLI 101 (6/10): pipe와 redirection | [ko](./content/linux-cli-101/ko/06-pipe-and-redirection.md) | [en](./content/linux-cli-101/en/06-pipe-and-redirection.md) | Publish Ready |
| 7 | Linux CLI 101 (7/10): 프로세스 확인과 종료 | [ko](./content/linux-cli-101/ko/07-process-management.md) | [en](./content/linux-cli-101/en/07-process-management.md) | Publish Ready |
| 8 | Linux CLI 101 (8/10): 환경변수와 PATH | [ko](./content/linux-cli-101/ko/08-environment-variables.md) | [en](./content/linux-cli-101/en/08-environment-variables.md) | Publish Ready |
| 9 | Linux CLI 101 (9/10): 간단한 shell script | [ko](./content/linux-cli-101/ko/09-shell-script-basics.md) | [en](./content/linux-cli-101/en/09-shell-script-basics.md) | Publish Ready |
| 10 | Linux CLI 101 (10/10): SSH와 원격 서버 접속 | [ko](./content/linux-cli-101/ko/10-ssh-and-remote.md) | [en](./content/linux-cli-101/en/10-ssh-and-remote.md) | Publish Ready |

### Python Package 101 (`python-package-101`)

Python 프로젝트 구조, pyproject.toml, 의존성 관리, 빌드, PyPI 배포, 버전 관리, CLI 패키지, 문서화까지 배우는 패키징 입문 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/python-package-101/`](./content/python-package-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Python Package 101 (1/10): Python Package란 무엇인가? | [ko](./content/python-package-101/ko/01-what-is-a-python-package.md) | [en](./content/python-package-101/en/01-what-is-a-python-package.md) | [medium](./content/python-package-101/medium/01.html) | Publish Ready |
| 2 | Python Package 101 (2/10): 프로젝트 구조 잡기 — src layout과 pyproject.toml | [ko](./content/python-package-101/ko/02-project-structure.md) | [en](./content/python-package-101/en/02-project-structure.md) | [medium](./content/python-package-101/medium/02.html) | Publish Ready |
| 3 | Python Package 101 (3/10): 의존성 관리 — venv, pip, uv, requirements | [ko](./content/python-package-101/ko/03-dependency-management.md) | [en](./content/python-package-101/en/03-dependency-management.md) | [medium](./content/python-package-101/medium/03.html) | Publish Ready |
| 4 | Python Package 101 (4/10): 패키지 빌드하기 — wheel과 sdist | [ko](./content/python-package-101/ko/04-building-packages.md) | [en](./content/python-package-101/en/04-building-packages.md) | [medium](./content/python-package-101/medium/04.html) | Publish Ready |
| 5 | Python Package 101 (5/10): PyPI에 배포하기 — TestPyPI부터 실제 배포까지 | [ko](./content/python-package-101/ko/05-publishing-to-pypi.md) | [en](./content/python-package-101/en/05-publishing-to-pypi.md) | [medium](./content/python-package-101/medium/05.html) | Publish Ready |
| 6 | Python Package 101 (6/10): 버전 관리와 릴리스 | [ko](./content/python-package-101/ko/06-versioning-and-releases.md) | [en](./content/python-package-101/en/06-versioning-and-releases.md) | [medium](./content/python-package-101/medium/06.html) | Publish Ready |
| 7 | Python Package 101 (7/10): CLI 패키지 만들기 | [ko](./content/python-package-101/ko/07-cli-packages.md) | [en](./content/python-package-101/en/07-cli-packages.md) | [medium](./content/python-package-101/medium/07.html) | Publish Ready |
| 8 | Python Package 101 (8/10): 타입 힌트와 정적 검사 | [ko](./content/python-package-101/ko/08-type-hints-and-static-analysis.md) | [en](./content/python-package-101/en/08-type-hints-and-static-analysis.md) | [medium](./content/python-package-101/medium/08.html) | Publish Ready |
| 9 | Python Package 101 (9/10): 문서화 — README, MkDocs, API Reference | [ko](./content/python-package-101/ko/09-documentation.md) | [en](./content/python-package-101/en/09-documentation.md) | [medium](./content/python-package-101/medium/09.html) | Publish Ready |
| 10 | Python Package 101 (10/10): 실전 패키지 템플릿 만들기 | [ko](./content/python-package-101/ko/10-package-template.md) | [en](./content/python-package-101/en/10-package-template.md) | [medium](./content/python-package-101/medium/10.html) | Publish Ready |

### pytest 101 (`pytest-101`)

pytest의 기본 문법, fixture, parametrization, mock, coverage, CI 연동까지 배우는 실전 테스트 입문 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/pytest-101/`](./content/pytest-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | pytest 101 (1/10): 왜 테스트를 작성해야 할까? | [ko](./content/pytest-101/ko/01-why-write-tests.md) | [en](./content/pytest-101/en/01-why-write-tests.md) | [medium](./content/pytest-101/medium/01.html) | Content Ready |
| 2 | pytest 101 (2/10): 첫 번째 pytest 테스트 작성하기 | [ko](./content/pytest-101/ko/02-first-pytest-test.md) | [en](./content/pytest-101/en/02-first-pytest-test.md) | [medium](./content/pytest-101/medium/02.html) | Content Ready |
| 3 | pytest 101 (3/10): assert와 예외 테스트 | [ko](./content/pytest-101/ko/03-assert-and-exceptions.md) | [en](./content/pytest-101/en/03-assert-and-exceptions.md) | [medium](./content/pytest-101/medium/03.html) | Content Ready |
| 4 | pytest 101 (4/10): fixture 이해하기 | [ko](./content/pytest-101/ko/04-fixtures.md) | [en](./content/pytest-101/en/04-fixtures.md) | [medium](./content/pytest-101/medium/04.html) | Content Ready |
| 5 | pytest 101 (5/10): parametrization으로 테스트 케이스 늘리기 | [ko](./content/pytest-101/ko/05-parametrization.md) | [en](./content/pytest-101/en/05-parametrization.md) | [medium](./content/pytest-101/medium/05.html) | Content Ready |
| 6 | pytest 101 (6/10): mock과 monkeypatch | [ko](./content/pytest-101/ko/06-mock-and-monkeypatch.md) | [en](./content/pytest-101/en/06-mock-and-monkeypatch.md) | [medium](./content/pytest-101/medium/06.html) | Content Ready |
| 7 | pytest 101 (7/10): 파일, 환경변수, 시간 테스트하기 | [ko](./content/pytest-101/ko/07-testing-files-env-time.md) | [en](./content/pytest-101/en/07-testing-files-env-time.md) | [medium](./content/pytest-101/medium/07.html) | Content Ready |
| 8 | pytest 101 (8/10): coverage와 테스트 품질 보기 | [ko](./content/pytest-101/ko/08-coverage.md) | [en](./content/pytest-101/en/08-coverage.md) | [medium](./content/pytest-101/medium/08.html) | Content Ready |
| 9 | pytest 101 (9/10): GitHub Actions에서 테스트 자동화하기 | [ko](./content/pytest-101/ko/09-ci-with-github-actions.md) | [en](./content/pytest-101/en/09-ci-with-github-actions.md) | [medium](./content/pytest-101/medium/09.html) | Content Ready |
| 10 | pytest 101 (10/10): 테스트하기 쉬운 코드 구조 만들기 | [ko](./content/pytest-101/ko/10-testable-code.md) | [en](./content/pytest-101/en/10-testable-code.md) | [medium](./content/pytest-101/medium/10.html) | Content Ready |

### Object-Oriented Programming 101 (`oop-101`)

클래스, 캡슐화, 상속, 다형성, 추상화, SOLID 원칙까지 객체지향의 핵심을 다루는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/oop-101/`](./content/oop-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Object-Oriented Programming 101 (1/10): 객체지향이란 무엇인가? | [ko](./content/oop-101/ko/01-what-is-oop.md) | [en](./content/oop-101/en/01-what-is-oop.md) | [medium](./content/oop-101/medium/01.html) | Draft |
| 2 | Object-Oriented Programming 101 (2/10): 클래스와 인스턴스 | [ko](./content/oop-101/ko/02-classes-and-instances.md) | [en](./content/oop-101/en/02-classes-and-instances.md) | [medium](./content/oop-101/medium/02.html) | Draft |
| 3 | Object-Oriented Programming 101 (3/10): 캡슐화 | [ko](./content/oop-101/ko/03-encapsulation.md) | [en](./content/oop-101/en/03-encapsulation.md) | [medium](./content/oop-101/medium/03.html) | Draft |
| 4 | Object-Oriented Programming 101 (4/10): 상속 | [ko](./content/oop-101/ko/04-inheritance.md) | [en](./content/oop-101/en/04-inheritance.md) | [medium](./content/oop-101/medium/04.html) | Draft |
| 5 | Object-Oriented Programming 101 (5/10): 다형성 | [ko](./content/oop-101/ko/05-polymorphism.md) | [en](./content/oop-101/en/05-polymorphism.md) | [medium](./content/oop-101/medium/05.html) | Draft |
| 6 | Object-Oriented Programming 101 (6/10): 추상화 | [ko](./content/oop-101/ko/06-abstraction.md) | [en](./content/oop-101/en/06-abstraction.md) | [medium](./content/oop-101/medium/06.html) | Draft |
| 7 | Object-Oriented Programming 101 (7/10): 합성과 상속 | [ko](./content/oop-101/ko/07-composition-vs-inheritance.md) | [en](./content/oop-101/en/07-composition-vs-inheritance.md) | [medium](./content/oop-101/medium/07.html) | Draft |
| 8 | Object-Oriented Programming 101 (8/10): SOLID 원칙 기초 | [ko](./content/oop-101/ko/08-solid-principles.md) | [en](./content/oop-101/en/08-solid-principles.md) | [medium](./content/oop-101/medium/08.html) | Draft |
| 9 | Object-Oriented Programming 101 (9/10): 객체지향 설계 예제 | [ko](./content/oop-101/ko/09-oop-design-example.md) | [en](./content/oop-101/en/09-oop-design-example.md) | [medium](./content/oop-101/medium/09.html) | Draft |
| 10 | Object-Oriented Programming 101 (10/10): 객체지향을 언제 피해야 할까? | [ko](./content/oop-101/ko/10-when-to-avoid-oop.md) | [en](./content/oop-101/en/10-when-to-avoid-oop.md) | [medium](./content/oop-101/medium/10.html) | Draft |

### Functional Programming 101 (`functional-programming-101`)

순수 함수, 불변 데이터, 고차 함수, 클로저, 함수 합성까지 함수형 프로그래밍의 핵심을 Python으로 배우는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/functional-programming-101/`](./content/functional-programming-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Functional Programming 101 (1/10): 함수형 프로그래밍이란 무엇인가? | [ko](./content/functional-programming-101/ko/01-what-is-fp.md) | [en](./content/functional-programming-101/en/01-what-is-fp.md) | [medium](./content/functional-programming-101/medium/01.html) | Draft |
| 2 | Functional Programming 101 (2/10): 순수 함수와 부수효과 | [ko](./content/functional-programming-101/ko/02-pure-functions.md) | [en](./content/functional-programming-101/en/02-pure-functions.md) | [medium](./content/functional-programming-101/medium/02.html) | Draft |
| 3 | Functional Programming 101 (3/10): immutable 데이터 | [ko](./content/functional-programming-101/ko/03-immutable-data.md) | [en](./content/functional-programming-101/en/03-immutable-data.md) | [medium](./content/functional-programming-101/medium/03.html) | Draft |
| 4 | Functional Programming 101 (4/10): 고차 함수 | [ko](./content/functional-programming-101/ko/04-higher-order-functions.md) | [en](./content/functional-programming-101/en/04-higher-order-functions.md) | [medium](./content/functional-programming-101/medium/04.html) | Draft |
| 5 | Functional Programming 101 (5/10): map, filter, reduce | [ko](./content/functional-programming-101/ko/05-map-filter-reduce.md) | [en](./content/functional-programming-101/en/05-map-filter-reduce.md) | [medium](./content/functional-programming-101/medium/05.html) | Draft |
| 6 | Functional Programming 101 (6/10): 클로저와 partial | [ko](./content/functional-programming-101/ko/06-closure-and-partial.md) | [en](./content/functional-programming-101/en/06-closure-and-partial.md) | [medium](./content/functional-programming-101/medium/06.html) | Draft |
| 7 | Functional Programming 101 (7/10): 재귀와 꼬리 호출 | [ko](./content/functional-programming-101/ko/07-recursion.md) | [en](./content/functional-programming-101/en/07-recursion.md) | [medium](./content/functional-programming-101/medium/07.html) | Draft |
| 8 | Functional Programming 101 (8/10): 지연 평가와 제너레이터 | [ko](./content/functional-programming-101/ko/08-lazy-evaluation.md) | [en](./content/functional-programming-101/en/08-lazy-evaluation.md) | [medium](./content/functional-programming-101/medium/08.html) | Draft |
| 9 | Functional Programming 101 (9/10): 함수 합성과 파이프라인 | [ko](./content/functional-programming-101/ko/09-function-composition.md) | [en](./content/functional-programming-101/en/09-function-composition.md) | [medium](./content/functional-programming-101/medium/09.html) | Draft |
| 10 | Functional Programming 101 (10/10): 객체지향과 함수형의 균형 | [ko](./content/functional-programming-101/ko/10-oop-and-fp-balance.md) | [en](./content/functional-programming-101/en/10-oop-and-fp-balance.md) | [medium](./content/functional-programming-101/medium/10.html) | Draft |

### Type Hints in Python 101 (`type-hints-python-101`)

Python type hint, Optional, Union, TypedDict, Protocol, Generic, mypy, Pydantic까지 타입 힌트 활용을 배우는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/type-hints-python-101/`](./content/type-hints-python-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Type Hints in Python 101 (1/10): Python type hint란 무엇인가? | [ko](./content/type-hints-python-101/ko/01-what-is-type-hint.md) | [en](./content/type-hints-python-101/en/01-what-is-type-hint.md) | [medium](./content/type-hints-python-101/medium/01.html) | Draft |
| 2 | Type Hints in Python 101 (2/10): 기본 타입과 collection 타입 | [ko](./content/type-hints-python-101/ko/02-basic-and-collection-types.md) | [en](./content/type-hints-python-101/en/02-basic-and-collection-types.md) | [medium](./content/type-hints-python-101/medium/02.html) | Draft |
| 3 | Type Hints in Python 101 (3/10): Optional과 Union | [ko](./content/type-hints-python-101/ko/03-optional-and-union.md) | [en](./content/type-hints-python-101/en/03-optional-and-union.md) | [medium](./content/type-hints-python-101/medium/03.html) | Draft |
| 4 | Type Hints in Python 101 (4/10): 함수 타입 힌트 | [ko](./content/type-hints-python-101/ko/04-function-type-hints.md) | [en](./content/type-hints-python-101/en/04-function-type-hints.md) | [medium](./content/type-hints-python-101/medium/04.html) | Draft |
| 5 | Type Hints in Python 101 (5/10): TypedDict와 dataclass | [ko](./content/type-hints-python-101/ko/05-typeddict-and-dataclass.md) | [en](./content/type-hints-python-101/en/05-typeddict-and-dataclass.md) | [medium](./content/type-hints-python-101/medium/05.html) | Draft |
| 6 | Type Hints in Python 101 (6/10): Protocol과 structural typing | [ko](./content/type-hints-python-101/ko/06-protocol-and-structural-typing.md) | [en](./content/type-hints-python-101/en/06-protocol-and-structural-typing.md) | [medium](./content/type-hints-python-101/medium/06.html) | Draft |
| 7 | Type Hints in Python 101 (7/10): Generic 이해하기 | [ko](./content/type-hints-python-101/ko/07-generic.md) | [en](./content/type-hints-python-101/en/07-generic.md) | [medium](./content/type-hints-python-101/medium/07.html) | Draft |
| 8 | Type Hints in Python 101 (8/10): mypy와 pyright 사용하기 | [ko](./content/type-hints-python-101/ko/08-mypy-and-pyright.md) | [en](./content/type-hints-python-101/en/08-mypy-and-pyright.md) | [medium](./content/type-hints-python-101/medium/08.html) | Draft |
| 9 | Type Hints in Python 101 (9/10): Pydantic과 타입 힌트 | [ko](./content/type-hints-python-101/ko/09-pydantic-and-type-hints.md) | [en](./content/type-hints-python-101/en/09-pydantic-and-type-hints.md) | [medium](./content/type-hints-python-101/medium/09.html) | Draft |
| 10 | Type Hints in Python 101 (10/10): 타입 힌트를 잘 쓰는 기준 | [ko](./content/type-hints-python-101/ko/10-type-hints-best-practices.md) | [en](./content/type-hints-python-101/en/10-type-hints-best-practices.md) | [medium](./content/type-hints-python-101/medium/10.html) | Draft |

### Data Structures with Python 101 (`data-structures-python-101`)

Python으로 배우는 자료구조 입문. list, dict, set, deque, 트리, 힙, 그래프를 직접 구현합니다.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/data-structures-python-101/`](./content/data-structures-python-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Data Structures with Python 101 (1/10): 자료구조란 무엇인가? | [ko](./content/data-structures-python-101/ko/01-what-are-data-structures.md) | [en](./content/data-structures-python-101/en/01-what-are-data-structures.md) | [medium](./content/data-structures-python-101/medium/01.html) | Draft |
| 2 | Data Structures with Python 101 (2/10): 배열과 리스트 | [ko](./content/data-structures-python-101/ko/02-arrays-and-lists.md) | [en](./content/data-structures-python-101/en/02-arrays-and-lists.md) | [medium](./content/data-structures-python-101/medium/02.html) | Draft |
| 3 | Data Structures with Python 101 (3/10): 스택과 큐 | [ko](./content/data-structures-python-101/ko/03-stacks-and-queues.md) | [en](./content/data-structures-python-101/en/03-stacks-and-queues.md) | [medium](./content/data-structures-python-101/medium/03.html) | Draft |
| 4 | Data Structures with Python 101 (4/10): 해시 테이블과 dict | [ko](./content/data-structures-python-101/ko/04-hash-tables-and-dict.md) | [en](./content/data-structures-python-101/en/04-hash-tables-and-dict.md) | [medium](./content/data-structures-python-101/medium/04.html) | Draft |
| 5 | Data Structures with Python 101 (5/10): 연결 리스트 | [ko](./content/data-structures-python-101/ko/05-linked-lists.md) | [en](./content/data-structures-python-101/en/05-linked-lists.md) | [medium](./content/data-structures-python-101/medium/05.html) | Draft |
| 6 | Data Structures with Python 101 (6/10): 트리와 이진 트리 | [ko](./content/data-structures-python-101/ko/06-trees-and-binary-trees.md) | [en](./content/data-structures-python-101/en/06-trees-and-binary-trees.md) | [medium](./content/data-structures-python-101/medium/06.html) | Draft |
| 7 | Data Structures with Python 101 (7/10): 힙과 우선순위 큐 | [ko](./content/data-structures-python-101/ko/07-heaps-and-priority-queues.md) | [en](./content/data-structures-python-101/en/07-heaps-and-priority-queues.md) | [medium](./content/data-structures-python-101/medium/07.html) | Draft |
| 8 | Data Structures with Python 101 (8/10): 그래프 표현 | [ko](./content/data-structures-python-101/ko/08-graph-representations.md) | [en](./content/data-structures-python-101/en/08-graph-representations.md) | [medium](./content/data-structures-python-101/medium/08.html) | Draft |
| 9 | Data Structures with Python 101 (9/10): set과 집합 연산 | [ko](./content/data-structures-python-101/ko/09-sets-and-set-operations.md) | [en](./content/data-structures-python-101/en/09-sets-and-set-operations.md) | [medium](./content/data-structures-python-101/medium/09.html) | Draft |
| 10 | Data Structures with Python 101 (10/10): 자료구조 선택 기준 | [ko](./content/data-structures-python-101/ko/10-choosing-data-structures.md) | [en](./content/data-structures-python-101/en/10-choosing-data-structures.md) | [medium](./content/data-structures-python-101/medium/10.html) | Draft |

### Algorithms with Python 101 (`algorithms-python-101`)

Python 기반으로 시간 복잡도, 탐색, 정렬, DP, BFS/DFS, 그리디 등 알고리즘 기본기를 다지는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/algorithms-python-101/`](./content/algorithms-python-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Algorithms with Python 101 (1/10): 알고리즘이란 무엇인가? | [ko](./content/algorithms-python-101/ko/01-what-are-algorithms.md) | [en](./content/algorithms-python-101/en/01-what-are-algorithms.md) | [medium](./content/algorithms-python-101/medium/01.html) | Draft |
| 2 | Algorithms with Python 101 (2/10): 시간 복잡도와 Big-O | [ko](./content/algorithms-python-101/ko/02-time-complexity-and-big-o.md) | [en](./content/algorithms-python-101/en/02-time-complexity-and-big-o.md) | [medium](./content/algorithms-python-101/medium/02.html) | Draft |
| 3 | Algorithms with Python 101 (3/10): 선형 탐색과 이진 탐색 | [ko](./content/algorithms-python-101/ko/03-linear-and-binary-search.md) | [en](./content/algorithms-python-101/en/03-linear-and-binary-search.md) | [medium](./content/algorithms-python-101/medium/03.html) | Draft |
| 4 | Algorithms with Python 101 (4/10): 정렬 알고리즘 | [ko](./content/algorithms-python-101/ko/04-sorting-algorithms.md) | [en](./content/algorithms-python-101/en/04-sorting-algorithms.md) | [medium](./content/algorithms-python-101/medium/04.html) | Draft |
| 5 | Algorithms with Python 101 (5/10): 재귀와 분할 정복 | [ko](./content/algorithms-python-101/ko/05-recursion-and-divide-and-conquer.md) | [en](./content/algorithms-python-101/en/05-recursion-and-divide-and-conquer.md) | [medium](./content/algorithms-python-101/medium/05.html) | Draft |
| 6 | Algorithms with Python 101 (6/10): 동적 계획법 기초 | [ko](./content/algorithms-python-101/ko/06-dynamic-programming-basics.md) | [en](./content/algorithms-python-101/en/06-dynamic-programming-basics.md) | [medium](./content/algorithms-python-101/medium/06.html) | Draft |
| 7 | Algorithms with Python 101 (7/10): 그래프 탐색 — BFS와 DFS | [ko](./content/algorithms-python-101/ko/07-graph-traversal-bfs-dfs.md) | [en](./content/algorithms-python-101/en/07-graph-traversal-bfs-dfs.md) | [medium](./content/algorithms-python-101/medium/07.html) | Draft |
| 8 | Algorithms with Python 101 (8/10): 최단 경로 기초 | [ko](./content/algorithms-python-101/ko/08-shortest-path-basics.md) | [en](./content/algorithms-python-101/en/08-shortest-path-basics.md) | [medium](./content/algorithms-python-101/medium/08.html) | Draft |
| 9 | Algorithms with Python 101 (9/10): 그리디 알고리즘 | [ko](./content/algorithms-python-101/ko/09-greedy-algorithms.md) | [en](./content/algorithms-python-101/en/09-greedy-algorithms.md) | [medium](./content/algorithms-python-101/medium/09.html) | Draft |
| 10 | Algorithms with Python 101 (10/10): 코딩 테스트 문제 접근법 | [ko](./content/algorithms-python-101/ko/10-coding-test-strategies.md) | [en](./content/algorithms-python-101/en/10-coding-test-strategies.md) | [medium](./content/algorithms-python-101/medium/10.html) | Draft |

---

## CS 핵심 과목

### 컴퓨터학과 전공 학습 가이드 101 / Computer Science Major 101 (`computer-science-major-101`)

컴퓨터학과 전공 과목 구성, 핵심 영역, 학습 순서, 졸업 전 역량까지 정리한 입문 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/computer-science-major-101/`](./content/computer-science-major-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Computer Science Major 101 (1/10): 컴퓨터학과에서는 무엇을 배우는가 | [ko](./content/computer-science-major-101/ko/01-what-cs-majors-learn.md) | [en](./content/computer-science-major-101/en/01-what-cs-majors-learn.md) | [medium](./content/computer-science-major-101/medium/01.html) | Draft |
| 2 | Computer Science Major 101 (2/10): 1학년 과목 이해하기 | [ko](./content/computer-science-major-101/ko/02-first-year-subjects.md) | [en](./content/computer-science-major-101/en/02-first-year-subjects.md) | [medium](./content/computer-science-major-101/medium/02.html) | Draft |
| 3 | Computer Science Major 101 (3/10): 자료구조와 알고리즘 | [ko](./content/computer-science-major-101/ko/03-data-structures-and-algorithms.md) | [en](./content/computer-science-major-101/en/03-data-structures-and-algorithms.md) | [medium](./content/computer-science-major-101/medium/03.html) | Draft |
| 4 | Computer Science Major 101 (4/10): 시스템 과목 이해하기 | [ko](./content/computer-science-major-101/ko/04-systems-subjects.md) | [en](./content/computer-science-major-101/en/04-systems-subjects.md) | [medium](./content/computer-science-major-101/medium/04.html) | Draft |
| 5 | Computer Science Major 101 (5/10): 데이터베이스와 네트워크 | [ko](./content/computer-science-major-101/ko/05-database-and-network.md) | [en](./content/computer-science-major-101/en/05-database-and-network.md) | [medium](./content/computer-science-major-101/medium/05.html) | Draft |
| 6 | Computer Science Major 101 (6/10): AI와 데이터사이언스 | [ko](./content/computer-science-major-101/ko/06-ai-and-data-science.md) | [en](./content/computer-science-major-101/en/06-ai-and-data-science.md) | [medium](./content/computer-science-major-101/medium/06.html) | Draft |
| 7 | Computer Science Major 101 (7/10): 프로젝트 과목 | [ko](./content/computer-science-major-101/ko/07-project-subjects.md) | [en](./content/computer-science-major-101/en/07-project-subjects.md) | [medium](./content/computer-science-major-101/medium/07.html) | Draft |
| 8 | Computer Science Major 101 (8/10): 전공 공부 방법 | [ko](./content/computer-science-major-101/ko/08-how-to-study-cs.md) | [en](./content/computer-science-major-101/en/08-how-to-study-cs.md) | [medium](./content/computer-science-major-101/medium/08.html) | Draft |
| 9 | Computer Science Major 101 (9/10): 포트폴리오로 연결하기 | [ko](./content/computer-science-major-101/ko/09-build-your-portfolio.md) | [en](./content/computer-science-major-101/en/09-build-your-portfolio.md) | [medium](./content/computer-science-major-101/medium/09.html) | Draft |
| 10 | Computer Science Major 101 (10/10): 졸업 전 갖춰야 할 역량 | [ko](./content/computer-science-major-101/ko/10-skills-before-graduation.md) | [en](./content/computer-science-major-101/en/10-skills-before-graduation.md) | [medium](./content/computer-science-major-101/medium/10.html) | Draft |

### Discrete Math 101 (`discrete-math-101`)

명제, 집합, 함수, 증명, 조합, 그래프 등 컴퓨터공학에 직접 쓰이는 이산수학을 정리하는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/discrete-math-101/`](./content/discrete-math-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Discrete Math 101 (1/10): 이산수학이란 무엇인가? | [ko](./content/discrete-math-101/ko/01-what-is-discrete-math.md) | [en](./content/discrete-math-101/en/01-what-is-discrete-math.md) | [medium](./content/discrete-math-101/medium/01.html) | Draft |
| 2 | Discrete Math 101 (2/10): 명제와 논리 | [ko](./content/discrete-math-101/ko/02-propositions-and-logic.md) | [en](./content/discrete-math-101/en/02-propositions-and-logic.md) | [medium](./content/discrete-math-101/medium/02.html) | Draft |
| 3 | Discrete Math 101 (3/10): 집합과 함수 | [ko](./content/discrete-math-101/ko/03-sets-and-functions.md) | [en](./content/discrete-math-101/en/03-sets-and-functions.md) | [medium](./content/discrete-math-101/medium/03.html) | Draft |
| 4 | Discrete Math 101 (4/10): 관계와 동치관계 | [ko](./content/discrete-math-101/ko/04-relations-and-equivalence.md) | [en](./content/discrete-math-101/en/04-relations-and-equivalence.md) | [medium](./content/discrete-math-101/medium/04.html) | Draft |
| 5 | Discrete Math 101 (5/10): 증명 방법 | [ko](./content/discrete-math-101/ko/05-proof-techniques.md) | [en](./content/discrete-math-101/en/05-proof-techniques.md) | [medium](./content/discrete-math-101/medium/05.html) | Draft |
| 6 | Discrete Math 101 (6/10): 수열과 점화식 | [ko](./content/discrete-math-101/ko/06-sequences-and-recurrence.md) | [en](./content/discrete-math-101/en/06-sequences-and-recurrence.md) | [medium](./content/discrete-math-101/medium/06.html) | Draft |
| 7 | Discrete Math 101 (7/10): 조합과 경우의 수 | [ko](./content/discrete-math-101/ko/07-combinatorics.md) | [en](./content/discrete-math-101/en/07-combinatorics.md) | [medium](./content/discrete-math-101/medium/07.html) | Draft |
| 8 | Discrete Math 101 (8/10): 그래프 이론 기초 | [ko](./content/discrete-math-101/ko/08-graph-theory-basics.md) | [en](./content/discrete-math-101/en/08-graph-theory-basics.md) | [medium](./content/discrete-math-101/medium/08.html) | Draft |
| 9 | Discrete Math 101 (9/10): 트리와 그래프 탐색 | [ko](./content/discrete-math-101/ko/09-trees-and-graph-traversal.md) | [en](./content/discrete-math-101/en/09-trees-and-graph-traversal.md) | [medium](./content/discrete-math-101/medium/09.html) | Draft |
| 10 | Discrete Math 101 (10/10): 알고리즘과 이산수학의 연결 | [ko](./content/discrete-math-101/ko/10-discrete-math-and-algorithms.md) | [en](./content/discrete-math-101/en/10-discrete-math-and-algorithms.md) | [medium](./content/discrete-math-101/medium/10.html) | Draft |

### Math for CS 101 (`math-for-cs-101`)

논리, 증명, 집합, 함수, 그래프, 조합, 확률, 선형대수, 미분, 정보이론까지 CS와 ML의 수학을 한 번에 정리하는 입문 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/math-for-cs-101/`](./content/math-for-cs-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Math for CS 101 (1/10): CS에 수학이 필요한 이유 | [ko](./content/math-for-cs-101/ko/01-why-math-for-cs.md) | [en](./content/math-for-cs-101/en/01-why-math-for-cs.md) | [medium](./content/math-for-cs-101/medium/01.html) | Draft |
| 2 | Math for CS 101 (2/10): 논리와 증명 | [ko](./content/math-for-cs-101/ko/02-logic-and-proofs.md) | [en](./content/math-for-cs-101/en/02-logic-and-proofs.md) | [medium](./content/math-for-cs-101/medium/02.html) | Draft |
| 3 | Math for CS 101 (3/10): 집합과 함수 | [ko](./content/math-for-cs-101/ko/03-sets-and-functions.md) | [en](./content/math-for-cs-101/en/03-sets-and-functions.md) | [medium](./content/math-for-cs-101/medium/03.html) | Draft |
| 4 | Math for CS 101 (4/10): 그래프 | [ko](./content/math-for-cs-101/ko/04-graphs.md) | [en](./content/math-for-cs-101/en/04-graphs.md) | [medium](./content/math-for-cs-101/medium/04.html) | Draft |
| 5 | Math for CS 101 (5/10): 조합 | [ko](./content/math-for-cs-101/ko/05-combinatorics.md) | [en](./content/math-for-cs-101/en/05-combinatorics.md) | [medium](./content/math-for-cs-101/medium/05.html) | Draft |
| 6 | Math for CS 101 (6/10): 확률 | [ko](./content/math-for-cs-101/ko/06-probability.md) | [en](./content/math-for-cs-101/en/06-probability.md) | [medium](./content/math-for-cs-101/medium/06.html) | Draft |
| 7 | Math for CS 101 (7/10): 선형대수 | [ko](./content/math-for-cs-101/ko/07-linear-algebra.md) | [en](./content/math-for-cs-101/en/07-linear-algebra.md) | [medium](./content/math-for-cs-101/medium/07.html) | Draft |
| 8 | Math for CS 101 (8/10): 미분 | [ko](./content/math-for-cs-101/ko/08-calculus.md) | [en](./content/math-for-cs-101/en/08-calculus.md) | [medium](./content/math-for-cs-101/medium/08.html) | Draft |
| 9 | Math for CS 101 (9/10): 정보이론 | [ko](./content/math-for-cs-101/ko/09-information-theory.md) | [en](./content/math-for-cs-101/en/09-information-theory.md) | [medium](./content/math-for-cs-101/medium/09.html) | Draft |
| 10 | Math for CS 101 (10/10): 알고리즘과 수학 | [ko](./content/math-for-cs-101/ko/10-algorithms-and-math.md) | [en](./content/math-for-cs-101/en/10-algorithms-and-math.md) | [medium](./content/math-for-cs-101/medium/10.html) | Draft |

### Calculus for ML 101 (`calculus-for-ml-101`)

함수, 기울기, 편미분, gradient, chain rule, 손실, 경사하강, backprop 직관까지 ML에 필요한 미분을 다지는 입문 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/calculus-for-ml-101/`](./content/calculus-for-ml-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Calculus for ML 101 (1/10): 미분이란 무엇인가 | [ko](./content/calculus-for-ml-101/ko/01-what-is-derivative.md) | [en](./content/calculus-for-ml-101/en/01-what-is-derivative.md) | [medium](./content/calculus-for-ml-101/medium/01.html) | Draft |
| 2 | Calculus for ML 101 (2/10): 함수와 기울기 | [ko](./content/calculus-for-ml-101/ko/02-functions-and-slope.md) | [en](./content/calculus-for-ml-101/en/02-functions-and-slope.md) | [medium](./content/calculus-for-ml-101/medium/02.html) | Draft |
| 3 | Calculus for ML 101 (3/10): 편미분 | [ko](./content/calculus-for-ml-101/ko/03-partial-derivatives.md) | [en](./content/calculus-for-ml-101/en/03-partial-derivatives.md) | [medium](./content/calculus-for-ml-101/medium/03.html) | Draft |
| 4 | Calculus for ML 101 (4/10): Gradient | [ko](./content/calculus-for-ml-101/ko/04-gradient.md) | [en](./content/calculus-for-ml-101/en/04-gradient.md) | [medium](./content/calculus-for-ml-101/medium/04.html) | Draft |
| 5 | Calculus for ML 101 (5/10): 연쇄 법칙 | [ko](./content/calculus-for-ml-101/ko/05-chain-rule.md) | [en](./content/calculus-for-ml-101/en/05-chain-rule.md) | [medium](./content/calculus-for-ml-101/medium/05.html) | Draft |
| 6 | Calculus for ML 101 (6/10): 손실 함수 | [ko](./content/calculus-for-ml-101/ko/06-loss-function.md) | [en](./content/calculus-for-ml-101/en/06-loss-function.md) | [medium](./content/calculus-for-ml-101/medium/06.html) | Draft |
| 7 | Calculus for ML 101 (7/10): 경사하강법 | [ko](./content/calculus-for-ml-101/ko/07-gradient-descent.md) | [en](./content/calculus-for-ml-101/en/07-gradient-descent.md) | [medium](./content/calculus-for-ml-101/medium/07.html) | Draft |
| 8 | Calculus for ML 101 (8/10): 최적화 | [ko](./content/calculus-for-ml-101/ko/08-optimization.md) | [en](./content/calculus-for-ml-101/en/08-optimization.md) | [medium](./content/calculus-for-ml-101/medium/08.html) | Draft |
| 9 | Calculus for ML 101 (9/10): 역전파 직관 | [ko](./content/calculus-for-ml-101/ko/09-backpropagation-intuition.md) | [en](./content/calculus-for-ml-101/en/09-backpropagation-intuition.md) | [medium](./content/calculus-for-ml-101/medium/09.html) | Draft |
| 10 | Calculus for ML 101 (10/10): 딥러닝에서의 미분 | [ko](./content/calculus-for-ml-101/ko/10-calculus-in-deep-learning.md) | [en](./content/calculus-for-ml-101/en/10-calculus-in-deep-learning.md) | [medium](./content/calculus-for-ml-101/medium/10.html) | Draft |

### Computer Architecture 101 (`computer-architecture-101`)

데이터 표현, CPU와 명령어, 레지스터, 메모리 계층, 캐시, 파이프라인, 멀티코어까지 컴퓨터가 코드를 실행하는 방식을 처음 배우는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/computer-architecture-101/`](./content/computer-architecture-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Computer Architecture 101 (1/10): 컴퓨터 구조란 무엇인가? | [ko](./content/computer-architecture-101/ko/01-what-is-computer-architecture.md) | [en](./content/computer-architecture-101/en/01-what-is-computer-architecture.md) | [medium](./content/computer-architecture-101/medium/01.html) | Draft |
| 2 | Computer Architecture 101 (2/10): 데이터 표현 — bit, byte, integer, floating point | [ko](./content/computer-architecture-101/ko/02-data-representation.md) | [en](./content/computer-architecture-101/en/02-data-representation.md) | [medium](./content/computer-architecture-101/medium/02.html) | Draft |
| 3 | Computer Architecture 101 (3/10): CPU와 명령어 | [ko](./content/computer-architecture-101/ko/03-cpu-and-instructions.md) | [en](./content/computer-architecture-101/en/03-cpu-and-instructions.md) | [medium](./content/computer-architecture-101/medium/03.html) | Draft |
| 4 | Computer Architecture 101 (4/10): 레지스터와 ALU | [ko](./content/computer-architecture-101/ko/04-registers-and-alu.md) | [en](./content/computer-architecture-101/en/04-registers-and-alu.md) | [medium](./content/computer-architecture-101/medium/04.html) | Draft |
| 5 | Computer Architecture 101 (5/10): 메모리 구조 | [ko](./content/computer-architecture-101/ko/05-memory-organization.md) | [en](./content/computer-architecture-101/en/05-memory-organization.md) | [medium](./content/computer-architecture-101/medium/05.html) | Draft |
| 6 | Computer Architecture 101 (6/10): 캐시와 지역성 | [ko](./content/computer-architecture-101/ko/06-cache-and-locality.md) | [en](./content/computer-architecture-101/en/06-cache-and-locality.md) | [medium](./content/computer-architecture-101/medium/06.html) | Draft |
| 7 | Computer Architecture 101 (7/10): 파이프라인 | [ko](./content/computer-architecture-101/ko/07-pipelining.md) | [en](./content/computer-architecture-101/en/07-pipelining.md) | [medium](./content/computer-architecture-101/medium/07.html) | Draft |
| 8 | Computer Architecture 101 (8/10): I/O와 장치 | [ko](./content/computer-architecture-101/ko/08-io-and-devices.md) | [en](./content/computer-architecture-101/en/08-io-and-devices.md) | [medium](./content/computer-architecture-101/medium/08.html) | Draft |
| 9 | Computer Architecture 101 (9/10): 병렬성과 멀티코어 | [ko](./content/computer-architecture-101/ko/09-parallelism-and-multicore.md) | [en](./content/computer-architecture-101/en/09-parallelism-and-multicore.md) | [medium](./content/computer-architecture-101/medium/09.html) | Draft |
| 10 | Computer Architecture 101 (10/10): 성능을 이해하는 법 | [ko](./content/computer-architecture-101/ko/10-understanding-performance.md) | [en](./content/computer-architecture-101/en/10-understanding-performance.md) | [medium](./content/computer-architecture-101/medium/10.html) | Draft |

### Data Structures 101 (`data-structures-101`)

배열, 리스트, 스택, 큐, 해시, 트리, 힙, 그래프까지 자료구조의 큰 그림과 선택 기준을 다루는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/data-structures-101/`](./content/data-structures-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Data Structures 101 (1/10): 자료구조란 무엇인가? | [ko](./content/data-structures-101/ko/01-what-are-data-structures.md) | [en](./content/data-structures-101/en/01-what-are-data-structures.md) | [medium](./content/data-structures-101/medium/01.html) | Draft |
| 2 | Data Structures 101 (2/10): 배열과 동적 배열 | [ko](./content/data-structures-101/ko/02-arrays-and-dynamic-arrays.md) | [en](./content/data-structures-101/en/02-arrays-and-dynamic-arrays.md) | [medium](./content/data-structures-101/medium/02.html) | Draft |
| 3 | Data Structures 101 (3/10): 연결 리스트 | [ko](./content/data-structures-101/ko/03-linked-lists.md) | [en](./content/data-structures-101/en/03-linked-lists.md) | [medium](./content/data-structures-101/medium/03.html) | Draft |
| 4 | Data Structures 101 (4/10): 스택과 큐 | [ko](./content/data-structures-101/ko/04-stacks-and-queues.md) | [en](./content/data-structures-101/en/04-stacks-and-queues.md) | [medium](./content/data-structures-101/medium/04.html) | Draft |
| 5 | Data Structures 101 (5/10): 해시 테이블 | [ko](./content/data-structures-101/ko/05-hash-tables.md) | [en](./content/data-structures-101/en/05-hash-tables.md) | [medium](./content/data-structures-101/medium/05.html) | Draft |
| 6 | Data Structures 101 (6/10): 트리 | [ko](./content/data-structures-101/ko/06-trees.md) | [en](./content/data-structures-101/en/06-trees.md) | [medium](./content/data-structures-101/medium/06.html) | Draft |
| 7 | Data Structures 101 (7/10): 이진 탐색 트리 | [ko](./content/data-structures-101/ko/07-binary-search-trees.md) | [en](./content/data-structures-101/en/07-binary-search-trees.md) | [medium](./content/data-structures-101/medium/07.html) | Draft |
| 8 | Data Structures 101 (8/10): 힙 | [ko](./content/data-structures-101/ko/08-heaps.md) | [en](./content/data-structures-101/en/08-heaps.md) | [medium](./content/data-structures-101/medium/08.html) | Draft |
| 9 | Data Structures 101 (9/10): 그래프 | [ko](./content/data-structures-101/ko/09-graphs.md) | [en](./content/data-structures-101/en/09-graphs.md) | [medium](./content/data-structures-101/medium/09.html) | Draft |
| 10 | Data Structures 101 (10/10): 자료구조 선택 기준 | [ko](./content/data-structures-101/ko/10-choosing-data-structures.md) | [en](./content/data-structures-101/en/10-choosing-data-structures.md) | [medium](./content/data-structures-101/medium/10.html) | Draft |

### Algorithms 101 (`algorithms-101`)

복잡도, 탐색, 정렬, 분할 정복, DP, 그리디, 그래프 알고리즘까지 알고리즘 설계 패턴을 배우는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/algorithms-101/`](./content/algorithms-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Algorithms 101 (1/10): 알고리즘이란 무엇인가? | [ko](./content/algorithms-101/ko/01-what-is-an-algorithm.md) | [en](./content/algorithms-101/en/01-what-is-an-algorithm.md) | [medium](./content/algorithms-101/medium/01.html) | Draft |
| 2 | Algorithms 101 (2/10): 시간 복잡도와 공간 복잡도 | [ko](./content/algorithms-101/ko/02-time-and-space-complexity.md) | [en](./content/algorithms-101/en/02-time-and-space-complexity.md) | [medium](./content/algorithms-101/medium/02.html) | Draft |
| 3 | Algorithms 101 (3/10): 탐색 알고리즘 | [ko](./content/algorithms-101/ko/03-search-algorithms.md) | [en](./content/algorithms-101/en/03-search-algorithms.md) | [medium](./content/algorithms-101/medium/03.html) | Draft |
| 4 | Algorithms 101 (4/10): 정렬 알고리즘 | [ko](./content/algorithms-101/ko/04-sorting-algorithms.md) | [en](./content/algorithms-101/en/04-sorting-algorithms.md) | [medium](./content/algorithms-101/medium/04.html) | Draft |
| 5 | Algorithms 101 (5/10): 재귀와 분할 정복 | [ko](./content/algorithms-101/ko/05-recursion-and-divide-and-conquer.md) | [en](./content/algorithms-101/en/05-recursion-and-divide-and-conquer.md) | [medium](./content/algorithms-101/medium/05.html) | Draft |
| 6 | Algorithms 101 (6/10): 동적 계획법 | [ko](./content/algorithms-101/ko/06-dynamic-programming.md) | [en](./content/algorithms-101/en/06-dynamic-programming.md) | [medium](./content/algorithms-101/medium/06.html) | Draft |
| 7 | Algorithms 101 (7/10): 그리디 알고리즘 | [ko](./content/algorithms-101/ko/07-greedy-algorithms.md) | [en](./content/algorithms-101/en/07-greedy-algorithms.md) | [medium](./content/algorithms-101/medium/07.html) | Draft |
| 8 | Algorithms 101 (8/10): 그래프 알고리즘 | [ko](./content/algorithms-101/ko/08-graph-algorithms.md) | [en](./content/algorithms-101/en/08-graph-algorithms.md) | [medium](./content/algorithms-101/medium/08.html) | Draft |
| 9 | Algorithms 101 (9/10): 문자열 알고리즘 기초 | [ko](./content/algorithms-101/ko/09-string-algorithms.md) | [en](./content/algorithms-101/en/09-string-algorithms.md) | [medium](./content/algorithms-101/medium/09.html) | Draft |
| 10 | Algorithms 101 (10/10): 알고리즘 문제 풀이 전략 | [ko](./content/algorithms-101/ko/10-problem-solving-strategies.md) | [en](./content/algorithms-101/en/10-problem-solving-strategies.md) | [medium](./content/algorithms-101/medium/10.html) | Draft |

### Programming Languages 101 (`programming-languages-101`)

syntax, semantics, type system, scope, closure, memory model, interpreter/compiler 차이까지 PL 기초를 다지는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/programming-languages-101/`](./content/programming-languages-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Programming Languages 101 (1/10): 프로그래밍 언어란 무엇인가? | [ko](./content/programming-languages-101/ko/01-what-is-a-programming-language.md) | [en](./content/programming-languages-101/en/01-what-is-a-programming-language.md) | [medium](./content/programming-languages-101/medium/01.html) | Draft |
| 2 | Programming Languages 101 (2/10): 구문과 의미 | [ko](./content/programming-languages-101/ko/02-syntax-and-semantics.md) | [en](./content/programming-languages-101/en/02-syntax-and-semantics.md) | [medium](./content/programming-languages-101/medium/02.html) | Draft |
| 3 | Programming Languages 101 (3/10): 타입 시스템 | [ko](./content/programming-languages-101/ko/03-type-system.md) | [en](./content/programming-languages-101/en/03-type-system.md) | [medium](./content/programming-languages-101/medium/03.html) | Draft |
| 4 | Programming Languages 101 (4/10): 스코프와 바인딩 | [ko](./content/programming-languages-101/ko/04-scope-and-binding.md) | [en](./content/programming-languages-101/en/04-scope-and-binding.md) | [medium](./content/programming-languages-101/medium/04.html) | Draft |
| 5 | Programming Languages 101 (5/10): 함수와 클로저 | [ko](./content/programming-languages-101/ko/05-functions-and-closures.md) | [en](./content/programming-languages-101/en/05-functions-and-closures.md) | [medium](./content/programming-languages-101/medium/05.html) | Draft |
| 6 | Programming Languages 101 (6/10): 객체와 프로토타입 | [ko](./content/programming-languages-101/ko/06-objects-and-prototypes.md) | [en](./content/programming-languages-101/en/06-objects-and-prototypes.md) | [medium](./content/programming-languages-101/medium/06.html) | Draft |
| 7 | Programming Languages 101 (7/10): 메모리 관리 | [ko](./content/programming-languages-101/ko/07-memory-management.md) | [en](./content/programming-languages-101/en/07-memory-management.md) | [medium](./content/programming-languages-101/medium/07.html) | Draft |
| 8 | Programming Languages 101 (8/10): 인터프리터와 컴파일러 | [ko](./content/programming-languages-101/ko/08-interpreter-and-compiler.md) | [en](./content/programming-languages-101/en/08-interpreter-and-compiler.md) | [medium](./content/programming-languages-101/medium/08.html) | Draft |
| 9 | Programming Languages 101 (9/10): 정적 언어와 동적 언어 | [ko](./content/programming-languages-101/ko/09-static-vs-dynamic.md) | [en](./content/programming-languages-101/en/09-static-vs-dynamic.md) | [medium](./content/programming-languages-101/medium/09.html) | Draft |
| 10 | Programming Languages 101 (10/10): 좋은 언어 설계란 무엇인가? | [ko](./content/programming-languages-101/ko/10-what-makes-good-language-design.md) | [en](./content/programming-languages-101/en/10-what-makes-good-language-design.md) | [medium](./content/programming-languages-101/medium/10.html) | Draft |

### Operating Systems 101 (`operating-systems-101`)

프로세스, 스레드, 스케줄링, 동시성, 메모리 관리, 가상 메모리, 파일 시스템, 시스템 콜, 컨테이너까지 운영체제의 기본 개념을 다지는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/operating-systems-101/`](./content/operating-systems-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Operating Systems 101 (1/10): 운영체제란 무엇인가? | [ko](./content/operating-systems-101/ko/01-what-is-an-operating-system.md) | [en](./content/operating-systems-101/en/01-what-is-an-operating-system.md) | [medium](./content/operating-systems-101/medium/01.html) | Draft |
| 2 | Operating Systems 101 (2/10): 프로세스와 스레드 | [ko](./content/operating-systems-101/ko/02-processes-and-threads.md) | [en](./content/operating-systems-101/en/02-processes-and-threads.md) | [medium](./content/operating-systems-101/medium/02.html) | Draft |
| 3 | Operating Systems 101 (3/10): 스케줄링 | [ko](./content/operating-systems-101/ko/03-scheduling.md) | [en](./content/operating-systems-101/en/03-scheduling.md) | [medium](./content/operating-systems-101/medium/03.html) | Draft |
| 4 | Operating Systems 101 (4/10): 동시성과 경쟁 상태 | [ko](./content/operating-systems-101/ko/04-concurrency-and-race-conditions.md) | [en](./content/operating-systems-101/en/04-concurrency-and-race-conditions.md) | [medium](./content/operating-systems-101/medium/04.html) | Draft |
| 5 | Operating Systems 101 (5/10): 락, 뮤텍스, 세마포어 | [ko](./content/operating-systems-101/ko/05-locks-mutex-semaphore.md) | [en](./content/operating-systems-101/en/05-locks-mutex-semaphore.md) | [medium](./content/operating-systems-101/medium/05.html) | Draft |
| 6 | Operating Systems 101 (6/10): 메모리 관리 | [ko](./content/operating-systems-101/ko/06-memory-management.md) | [en](./content/operating-systems-101/en/06-memory-management.md) | [medium](./content/operating-systems-101/medium/06.html) | Draft |
| 7 | Operating Systems 101 (7/10): 가상 메모리 | [ko](./content/operating-systems-101/ko/07-virtual-memory.md) | [en](./content/operating-systems-101/en/07-virtual-memory.md) | [medium](./content/operating-systems-101/medium/07.html) | Draft |
| 8 | Operating Systems 101 (8/10): 파일 시스템 | [ko](./content/operating-systems-101/ko/08-file-systems.md) | [en](./content/operating-systems-101/en/08-file-systems.md) | [medium](./content/operating-systems-101/medium/08.html) | Draft |
| 9 | Operating Systems 101 (9/10): 시스템 콜 | [ko](./content/operating-systems-101/ko/09-system-calls.md) | [en](./content/operating-systems-101/en/09-system-calls.md) | [medium](./content/operating-systems-101/medium/09.html) | Draft |
| 10 | Operating Systems 101 (10/10): 컨테이너와 운영체제 | [ko](./content/operating-systems-101/ko/10-containers-and-the-os.md) | [en](./content/operating-systems-101/en/10-containers-and-the-os.md) | [medium](./content/operating-systems-101/medium/10.html) | Draft |

### Computer Networks 101 (`computer-networks-101`)

IP, TCP, UDP, DNS, HTTP, TLS, 라우팅, 로드밸런서, WebSocket까지 인터넷 동작의 핵심을 정리하는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/computer-networks-101/`](./content/computer-networks-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Computer Networks 101 (1/10): 네트워크란 무엇인가? | [ko](./content/computer-networks-101/ko/01-what-is-a-network.md) | [en](./content/computer-networks-101/en/01-what-is-a-network.md) | [medium](./content/computer-networks-101/medium/01.html) | Draft |
| 2 | Computer Networks 101 (2/10): IP와 subnet | [ko](./content/computer-networks-101/ko/02-ip-and-subnet.md) | [en](./content/computer-networks-101/en/02-ip-and-subnet.md) | [medium](./content/computer-networks-101/medium/02.html) | Draft |
| 3 | Computer Networks 101 (3/10): TCP와 UDP | [ko](./content/computer-networks-101/ko/03-tcp-and-udp.md) | [en](./content/computer-networks-101/en/03-tcp-and-udp.md) | [medium](./content/computer-networks-101/medium/03.html) | Draft |
| 4 | Computer Networks 101 (4/10): DNS | [ko](./content/computer-networks-101/ko/04-dns.md) | [en](./content/computer-networks-101/en/04-dns.md) | [medium](./content/computer-networks-101/medium/04.html) | Draft |
| 5 | Computer Networks 101 (5/10): HTTP와 HTTPS | [ko](./content/computer-networks-101/ko/05-http-and-https.md) | [en](./content/computer-networks-101/en/05-http-and-https.md) | [medium](./content/computer-networks-101/medium/05.html) | Draft |
| 6 | Computer Networks 101 (6/10): TLS 기초 | [ko](./content/computer-networks-101/ko/06-tls-basics.md) | [en](./content/computer-networks-101/en/06-tls-basics.md) | [medium](./content/computer-networks-101/medium/06.html) | Draft |
| 7 | Computer Networks 101 (7/10): 라우팅과 NAT | [ko](./content/computer-networks-101/ko/07-routing-and-nat.md) | [en](./content/computer-networks-101/en/07-routing-and-nat.md) | [medium](./content/computer-networks-101/medium/07.html) | Draft |
| 8 | Computer Networks 101 (8/10): Load Balancer | [ko](./content/computer-networks-101/ko/08-load-balancer.md) | [en](./content/computer-networks-101/en/08-load-balancer.md) | [medium](./content/computer-networks-101/medium/08.html) | Draft |
| 9 | Computer Networks 101 (9/10): WebSocket과 실시간 통신 | [ko](./content/computer-networks-101/ko/09-websocket-and-realtime.md) | [en](./content/computer-networks-101/en/09-websocket-and-realtime.md) | [medium](./content/computer-networks-101/medium/09.html) | Draft |
| 10 | Computer Networks 101 (10/10): 네트워크 문제 디버깅 | [ko](./content/computer-networks-101/ko/10-debugging-network-problems.md) | [en](./content/computer-networks-101/en/10-debugging-network-problems.md) | [medium](./content/computer-networks-101/medium/10.html) | Draft |

### Database Systems 101 (`database-systems-101`)

관계형 모델, SQL, 인덱스, 트랜잭션, isolation, 정규화, 쿼리 최적화, 복제까지 DBMS의 핵심을 다루는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/database-systems-101/`](./content/database-systems-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Database Systems 101 (1/10): 데이터베이스 시스템이란 무엇인가? | [ko](./content/database-systems-101/ko/01-what-is-a-database.md) | [en](./content/database-systems-101/en/01-what-is-a-database.md) | [medium](./content/database-systems-101/medium/01.html) | Draft |
| 2 | Database Systems 101 (2/10): 관계형 모델 | [ko](./content/database-systems-101/ko/02-relational-model.md) | [en](./content/database-systems-101/en/02-relational-model.md) | [medium](./content/database-systems-101/medium/02.html) | Draft |
| 3 | Database Systems 101 (3/10): SQL과 쿼리 처리 | [ko](./content/database-systems-101/ko/03-sql-and-query-processing.md) | [en](./content/database-systems-101/en/03-sql-and-query-processing.md) | [medium](./content/database-systems-101/medium/03.html) | Draft |
| 4 | Database Systems 101 (4/10): 인덱스 | [ko](./content/database-systems-101/ko/04-indexes.md) | [en](./content/database-systems-101/en/04-indexes.md) | [medium](./content/database-systems-101/medium/04.html) | Draft |
| 5 | Database Systems 101 (5/10): 트랜잭션과 ACID | [ko](./content/database-systems-101/ko/05-transactions-and-acid.md) | [en](./content/database-systems-101/en/05-transactions-and-acid.md) | [medium](./content/database-systems-101/medium/05.html) | Draft |
| 6 | Database Systems 101 (6/10): 격리 수준 | [ko](./content/database-systems-101/ko/06-isolation-levels.md) | [en](./content/database-systems-101/en/06-isolation-levels.md) | [medium](./content/database-systems-101/medium/06.html) | Draft |
| 7 | Database Systems 101 (7/10): 정규화와 모델링 | [ko](./content/database-systems-101/ko/07-normalization-and-modeling.md) | [en](./content/database-systems-101/en/07-normalization-and-modeling.md) | [medium](./content/database-systems-101/medium/07.html) | Draft |
| 8 | Database Systems 101 (8/10): 쿼리 최적화 | [ko](./content/database-systems-101/ko/08-query-optimization.md) | [en](./content/database-systems-101/en/08-query-optimization.md) | [medium](./content/database-systems-101/medium/08.html) | Draft |
| 9 | Database Systems 101 (9/10): 복제와 백업 | [ko](./content/database-systems-101/ko/09-replication-and-backup.md) | [en](./content/database-systems-101/en/09-replication-and-backup.md) | [medium](./content/database-systems-101/medium/09.html) | Draft |
| 10 | Database Systems 101 (10/10): OLTP와 OLAP | [ko](./content/database-systems-101/ko/10-oltp-and-olap.md) | [en](./content/database-systems-101/en/10-oltp-and-olap.md) | [medium](./content/database-systems-101/medium/10.html) | Draft |

### Distributed Systems 101 (`distributed-systems-101`)

failure model, consistency, replication, consensus, message queue까지 분산 시스템의 핵심 개념을 처음 배우는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/distributed-systems-101/`](./content/distributed-systems-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Distributed Systems 101 (1/10): 분산 시스템이란 무엇인가? | [ko](./content/distributed-systems-101/ko/01-what-is-a-distributed-system.md) | [en](./content/distributed-systems-101/en/01-what-is-a-distributed-system.md) | [medium](./content/distributed-systems-101/medium/01.html) | Draft |
| 2 | Distributed Systems 101 (2/10): 장애 모델 | [ko](./content/distributed-systems-101/ko/02-failure-model.md) | [en](./content/distributed-systems-101/en/02-failure-model.md) | [medium](./content/distributed-systems-101/medium/02.html) | Draft |
| 3 | Distributed Systems 101 (3/10): RPC와 메시지 전달 | [ko](./content/distributed-systems-101/ko/03-rpc-and-message-passing.md) | [en](./content/distributed-systems-101/en/03-rpc-and-message-passing.md) | [medium](./content/distributed-systems-101/medium/03.html) | Draft |
| 4 | Distributed Systems 101 (4/10): 일관성과 CAP | [ko](./content/distributed-systems-101/ko/04-consistency-and-cap.md) | [en](./content/distributed-systems-101/en/04-consistency-and-cap.md) | [medium](./content/distributed-systems-101/medium/04.html) | Draft |
| 5 | Distributed Systems 101 (5/10): 복제 | [ko](./content/distributed-systems-101/ko/05-replication.md) | [en](./content/distributed-systems-101/en/05-replication.md) | [medium](./content/distributed-systems-101/medium/05.html) | Draft |
| 6 | Distributed Systems 101 (6/10): 합의와 Raft | [ko](./content/distributed-systems-101/ko/06-consensus-and-raft.md) | [en](./content/distributed-systems-101/en/06-consensus-and-raft.md) | [medium](./content/distributed-systems-101/medium/06.html) | Draft |
| 7 | Distributed Systems 101 (7/10): 리더 선출 | [ko](./content/distributed-systems-101/ko/07-leader-election.md) | [en](./content/distributed-systems-101/en/07-leader-election.md) | [medium](./content/distributed-systems-101/medium/07.html) | Draft |
| 8 | Distributed Systems 101 (8/10): 메시지 큐와 이벤트 소싱 | [ko](./content/distributed-systems-101/ko/08-message-queue-and-event-sourcing.md) | [en](./content/distributed-systems-101/en/08-message-queue-and-event-sourcing.md) | [medium](./content/distributed-systems-101/medium/08.html) | Draft |
| 9 | Distributed Systems 101 (9/10): 분산 트랜잭션 | [ko](./content/distributed-systems-101/ko/09-distributed-transaction.md) | [en](./content/distributed-systems-101/en/09-distributed-transaction.md) | [medium](./content/distributed-systems-101/medium/09.html) | Draft |
| 10 | Distributed Systems 101 (10/10): 운영 가능한 분산 시스템 패턴 | [ko](./content/distributed-systems-101/ko/10-operable-distributed-patterns.md) | [en](./content/distributed-systems-101/en/10-operable-distributed-patterns.md) | [medium](./content/distributed-systems-101/medium/10.html) | Draft |

### Compilers 101 (`compilers-101`)

lexer, parser, AST, semantic analysis, IR, optimization, code generation까지 컴파일러 파이프라인을 처음 배우는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/compilers-101/`](./content/compilers-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Compilers 101 (1/10): 컴파일러란 무엇인가? | [ko](./content/compilers-101/ko/01-what-is-a-compiler.md) | [en](./content/compilers-101/en/01-what-is-a-compiler.md) | [medium](./content/compilers-101/medium/01.html) | Draft |
| 2 | Compilers 101 (2/10): 렉시컬 분석 | [ko](./content/compilers-101/ko/02-lexical-analysis.md) | [en](./content/compilers-101/en/02-lexical-analysis.md) | [medium](./content/compilers-101/medium/02.html) | Draft |
| 3 | Compilers 101 (3/10): 파싱과 AST | [ko](./content/compilers-101/ko/03-parsing-and-ast.md) | [en](./content/compilers-101/en/03-parsing-and-ast.md) | [medium](./content/compilers-101/medium/03.html) | Draft |
| 4 | Compilers 101 (4/10): 시맨틱 분석 | [ko](./content/compilers-101/ko/04-semantic-analysis.md) | [en](./content/compilers-101/en/04-semantic-analysis.md) | [medium](./content/compilers-101/medium/04.html) | Draft |
| 5 | Compilers 101 (5/10): 심볼 테이블과 스코프 | [ko](./content/compilers-101/ko/05-symbol-table-and-scope.md) | [en](./content/compilers-101/en/05-symbol-table-and-scope.md) | [medium](./content/compilers-101/medium/05.html) | Draft |
| 6 | Compilers 101 (6/10): 중간 표현 | [ko](./content/compilers-101/ko/06-intermediate-representation.md) | [en](./content/compilers-101/en/06-intermediate-representation.md) | [medium](./content/compilers-101/medium/06.html) | Draft |
| 7 | Compilers 101 (7/10): 최적화 기초 | [ko](./content/compilers-101/ko/07-optimization-basics.md) | [en](./content/compilers-101/en/07-optimization-basics.md) | [medium](./content/compilers-101/medium/07.html) | Draft |
| 8 | Compilers 101 (8/10): 코드 생성 | [ko](./content/compilers-101/ko/08-code-generation.md) | [en](./content/compilers-101/en/08-code-generation.md) | [medium](./content/compilers-101/medium/08.html) | Draft |
| 9 | Compilers 101 (9/10): JIT vs AOT | [ko](./content/compilers-101/ko/09-jit-vs-aot.md) | [en](./content/compilers-101/en/09-jit-vs-aot.md) | [medium](./content/compilers-101/medium/09.html) | Draft |
| 10 | Compilers 101 (10/10): 작은 인터프리터 만들기 | [ko](./content/compilers-101/ko/10-building-a-tiny-interpreter.md) | [en](./content/compilers-101/en/10-building-a-tiny-interpreter.md) | [medium](./content/compilers-101/medium/10.html) | Draft |

### Information Security 101 (`information-security-101`)

인증, 인가, 암호화, TLS, 웹 보안, secret 관리, 권한 최소화, 감사 로그까지 개발자 수준의 보안 기본을 다루는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/information-security-101/`](./content/information-security-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Information Security 101 (1/10): 정보보안이란 무엇인가? | [ko](./content/information-security-101/ko/01-what-is-information-security.md) | [en](./content/information-security-101/en/01-what-is-information-security.md) | [medium](./content/information-security-101/medium/01.html) | Draft |
| 2 | Information Security 101 (2/10): 인증과 인가 | [ko](./content/information-security-101/ko/02-authentication-and-authorization.md) | [en](./content/information-security-101/en/02-authentication-and-authorization.md) | [medium](./content/information-security-101/medium/02.html) | Draft |
| 3 | Information Security 101 (3/10): 암호화와 해시 | [ko](./content/information-security-101/ko/03-cryptography-and-hash.md) | [en](./content/information-security-101/en/03-cryptography-and-hash.md) | [medium](./content/information-security-101/medium/03.html) | Draft |
| 4 | Information Security 101 (4/10): TLS와 인증서 | [ko](./content/information-security-101/ko/04-tls-and-certificates.md) | [en](./content/information-security-101/en/04-tls-and-certificates.md) | [medium](./content/information-security-101/medium/04.html) | Draft |
| 5 | Information Security 101 (5/10): 웹 보안 기초 | [ko](./content/information-security-101/ko/05-web-security-basics.md) | [en](./content/information-security-101/en/05-web-security-basics.md) | [medium](./content/information-security-101/medium/05.html) | Draft |
| 6 | Information Security 101 (6/10): SQL 인젝션과 XSS | [ko](./content/information-security-101/ko/06-sql-injection-and-xss.md) | [en](./content/information-security-101/en/06-sql-injection-and-xss.md) | [medium](./content/information-security-101/medium/06.html) | Draft |
| 7 | Information Security 101 (7/10): 비밀 정보 관리 | [ko](./content/information-security-101/ko/07-secret-management.md) | [en](./content/information-security-101/en/07-secret-management.md) | [medium](./content/information-security-101/medium/07.html) | Draft |
| 8 | Information Security 101 (8/10): 권한 최소화 | [ko](./content/information-security-101/ko/08-least-privilege.md) | [en](./content/information-security-101/en/08-least-privilege.md) | [medium](./content/information-security-101/medium/08.html) | Draft |
| 9 | Information Security 101 (9/10): 로그와 감사 | [ko](./content/information-security-101/ko/09-logging-and-audit.md) | [en](./content/information-security-101/en/09-logging-and-audit.md) | [medium](./content/information-security-101/medium/09.html) | Draft |
| 10 | Information Security 101 (10/10): 보안 사고 대응 | [ko](./content/information-security-101/ko/10-incident-response.md) | [en](./content/information-security-101/en/10-incident-response.md) | [medium](./content/information-security-101/medium/10.html) | Draft |

---

## 소프트웨어 엔지니어링

### Software Engineering 101 (`software-engineering-101`)

요구사항, 설계, 코드 리뷰, 테스트, 버전 관리, 문서화, 협업, 유지보수까지 소프트웨어 엔지니어링의 큰 그림을 다지는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/software-engineering-101/`](./content/software-engineering-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Software Engineering 101 (1/10): 소프트웨어 엔지니어링이란 무엇인가? | [ko](./content/software-engineering-101/ko/01-what-is-software-engineering.md) | [en](./content/software-engineering-101/en/01-what-is-software-engineering.md) | [medium](./content/software-engineering-101/medium/01.html) | Draft |
| 2 | Software Engineering 101 (2/10): 요구사항 이해하기 | [ko](./content/software-engineering-101/ko/02-understanding-requirements.md) | [en](./content/software-engineering-101/en/02-understanding-requirements.md) | [medium](./content/software-engineering-101/medium/02.html) | Draft |
| 3 | Software Engineering 101 (3/10): 설계와 구현의 차이 | [ko](./content/software-engineering-101/ko/03-design-vs-implementation.md) | [en](./content/software-engineering-101/en/03-design-vs-implementation.md) | [medium](./content/software-engineering-101/medium/03.html) | Draft |
| 4 | Software Engineering 101 (4/10): 코드 리뷰 | [ko](./content/software-engineering-101/ko/04-code-review.md) | [en](./content/software-engineering-101/en/04-code-review.md) | [medium](./content/software-engineering-101/medium/04.html) | Draft |
| 5 | Software Engineering 101 (5/10): 테스트 전략 | [ko](./content/software-engineering-101/ko/05-testing-strategy.md) | [en](./content/software-engineering-101/en/05-testing-strategy.md) | [medium](./content/software-engineering-101/medium/05.html) | Draft |
| 6 | Software Engineering 101 (6/10): 버전 관리와 릴리스 | [ko](./content/software-engineering-101/ko/06-version-control-and-release.md) | [en](./content/software-engineering-101/en/06-version-control-and-release.md) | [medium](./content/software-engineering-101/medium/06.html) | Draft |
| 7 | Software Engineering 101 (7/10): 문서화 | [ko](./content/software-engineering-101/ko/07-documentation.md) | [en](./content/software-engineering-101/en/07-documentation.md) | [medium](./content/software-engineering-101/medium/07.html) | Draft |
| 8 | Software Engineering 101 (8/10): 협업 프로세스 | [ko](./content/software-engineering-101/ko/08-collaboration-process.md) | [en](./content/software-engineering-101/en/08-collaboration-process.md) | [medium](./content/software-engineering-101/medium/08.html) | Draft |
| 9 | Software Engineering 101 (9/10): 유지보수와 기술부채 | [ko](./content/software-engineering-101/ko/09-maintenance-and-tech-debt.md) | [en](./content/software-engineering-101/en/09-maintenance-and-tech-debt.md) | [medium](./content/software-engineering-101/medium/09.html) | Draft |
| 10 | Software Engineering 101 (10/10): 좋은 소프트웨어의 기준 | [ko](./content/software-engineering-101/ko/10-what-makes-good-software.md) | [en](./content/software-engineering-101/en/10-what-makes-good-software.md) | [medium](./content/software-engineering-101/medium/10.html) | Draft |

### Clean Code 101 (`clean-code-101`)

이름 짓기, 함수 분리, 조건문 단순화, 중복 제거, 오류 처리부터 리팩토링 기초까지 읽기 쉬운 코드를 쓰는 법을 다지는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/clean-code-101/`](./content/clean-code-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Clean Code 101 (1/10): Clean Code란 무엇인가? | [ko](./content/clean-code-101/ko/01-what-is-clean-code.md) | [en](./content/clean-code-101/en/01-what-is-clean-code.md) | [medium](./content/clean-code-101/medium/01.html) | Draft |
| 2 | Clean Code 101 (2/10): 이름 짓기 | [ko](./content/clean-code-101/ko/02-naming.md) | [en](./content/clean-code-101/en/02-naming.md) | [medium](./content/clean-code-101/medium/02.html) | Draft |
| 3 | Clean Code 101 (3/10): 함수 작게 만들기 | [ko](./content/clean-code-101/ko/03-small-functions.md) | [en](./content/clean-code-101/en/03-small-functions.md) | [medium](./content/clean-code-101/medium/03.html) | Draft |
| 4 | Clean Code 101 (4/10): 조건문 줄이기 | [ko](./content/clean-code-101/ko/04-simplifying-conditionals.md) | [en](./content/clean-code-101/en/04-simplifying-conditionals.md) | [medium](./content/clean-code-101/medium/04.html) | Draft |
| 5 | Clean Code 101 (5/10): 중복 제거 | [ko](./content/clean-code-101/ko/05-removing-duplication.md) | [en](./content/clean-code-101/en/05-removing-duplication.md) | [medium](./content/clean-code-101/medium/05.html) | Draft |
| 6 | Clean Code 101 (6/10): 오류 처리 | [ko](./content/clean-code-101/ko/06-error-handling.md) | [en](./content/clean-code-101/en/06-error-handling.md) | [medium](./content/clean-code-101/medium/06.html) | Draft |
| 7 | Clean Code 101 (7/10): 주석과 문서화 | [ko](./content/clean-code-101/ko/07-comments-and-docs.md) | [en](./content/clean-code-101/en/07-comments-and-docs.md) | [medium](./content/clean-code-101/medium/07.html) | Draft |
| 8 | Clean Code 101 (8/10): 테스트 가능한 코드 | [ko](./content/clean-code-101/ko/08-testable-code.md) | [en](./content/clean-code-101/en/08-testable-code.md) | [medium](./content/clean-code-101/medium/08.html) | Draft |
| 9 | Clean Code 101 (9/10): 리팩토링 기초 | [ko](./content/clean-code-101/ko/09-refactoring-basics.md) | [en](./content/clean-code-101/en/09-refactoring-basics.md) | [medium](./content/clean-code-101/medium/09.html) | Draft |
| 10 | Clean Code 101 (10/10): 좋은 코드 리뷰 기준 | [ko](./content/clean-code-101/ko/10-good-code-review.md) | [en](./content/clean-code-101/en/10-good-code-review.md) | [medium](./content/clean-code-101/medium/10.html) | Draft |

### Software Design 101 (`software-design-101`)

관심사 분리, 모듈 경계, 의존성 방향, 인터페이스 설계, 계층 아키텍처를 통해 변경에 강한 코드를 설계하는 법을 다지는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/software-design-101/`](./content/software-design-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Software Design 101 (1/10): 소프트웨어 설계란 무엇인가? | [ko](./content/software-design-101/ko/01-what-is-software-design.md) | [en](./content/software-design-101/en/01-what-is-software-design.md) | [medium](./content/software-design-101/medium/01.html) | Draft |
| 2 | Software Design 101 (2/10): 관심사 분리 | [ko](./content/software-design-101/ko/02-separation-of-concerns.md) | [en](./content/software-design-101/en/02-separation-of-concerns.md) | [medium](./content/software-design-101/medium/02.html) | Draft |
| 3 | Software Design 101 (3/10): 모듈과 경계 | [ko](./content/software-design-101/ko/03-modules-and-boundaries.md) | [en](./content/software-design-101/en/03-modules-and-boundaries.md) | [medium](./content/software-design-101/medium/03.html) | Draft |
| 4 | Software Design 101 (4/10): 의존성 방향 | [ko](./content/software-design-101/ko/04-dependency-direction.md) | [en](./content/software-design-101/en/04-dependency-direction.md) | [medium](./content/software-design-101/medium/04.html) | Draft |
| 5 | Software Design 101 (5/10): 인터페이스와 추상화 | [ko](./content/software-design-101/ko/05-interfaces-and-abstraction.md) | [en](./content/software-design-101/en/05-interfaces-and-abstraction.md) | [medium](./content/software-design-101/medium/05.html) | Draft |
| 6 | Software Design 101 (6/10): 계층 아키텍처 | [ko](./content/software-design-101/ko/06-layered-architecture.md) | [en](./content/software-design-101/en/06-layered-architecture.md) | [medium](./content/software-design-101/medium/06.html) | Draft |
| 7 | Software Design 101 (7/10): 데이터 흐름 설계 | [ko](./content/software-design-101/ko/07-data-flow-design.md) | [en](./content/software-design-101/en/07-data-flow-design.md) | [medium](./content/software-design-101/medium/07.html) | Draft |
| 8 | Software Design 101 (8/10): 변경 영향 줄이기 | [ko](./content/software-design-101/ko/08-reducing-change-impact.md) | [en](./content/software-design-101/en/08-reducing-change-impact.md) | [medium](./content/software-design-101/medium/08.html) | Draft |
| 9 | Software Design 101 (9/10): 설계 원칙 모음 | [ko](./content/software-design-101/ko/09-design-principles.md) | [en](./content/software-design-101/en/09-design-principles.md) | [medium](./content/software-design-101/medium/09.html) | Draft |
| 10 | Software Design 101 (10/10): 작은 프로젝트로 설계 연습 | [ko](./content/software-design-101/ko/10-small-design-practice.md) | [en](./content/software-design-101/en/10-small-design-practice.md) | [medium](./content/software-design-101/medium/10.html) | Draft |

### Design Patterns 101 (`design-patterns-101`)

GoF 디자인 패턴을 Python 예시로 빠르게 훑고, 언제 쓰고 언제 피해야 할지 감을 잡는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/design-patterns-101/`](./content/design-patterns-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | 디자인 패턴 101 (1/10): 디자인 패턴이란 무엇인가? | [ko](./content/design-patterns-101/ko/01-what-are-design-patterns.md) | [en](./content/design-patterns-101/en/01-what-are-design-patterns.md) | [medium](./content/design-patterns-101/medium/01.html) | Draft |
| 2 | 디자인 패턴 101 (2/10): 생성 패턴 | [ko](./content/design-patterns-101/ko/02-creational-patterns.md) | [en](./content/design-patterns-101/en/02-creational-patterns.md) | [medium](./content/design-patterns-101/medium/02.html) | Draft |
| 3 | 디자인 패턴 101 (3/10): 구조 패턴 | [ko](./content/design-patterns-101/ko/03-structural-patterns.md) | [en](./content/design-patterns-101/en/03-structural-patterns.md) | [medium](./content/design-patterns-101/medium/03.html) | Draft |
| 4 | 디자인 패턴 101 (4/10): 행위 패턴 | [ko](./content/design-patterns-101/ko/04-behavioral-patterns.md) | [en](./content/design-patterns-101/en/04-behavioral-patterns.md) | [medium](./content/design-patterns-101/medium/04.html) | Draft |
| 5 | 디자인 패턴 101 (5/10): 전략 패턴 | [ko](./content/design-patterns-101/ko/05-strategy-pattern.md) | [en](./content/design-patterns-101/en/05-strategy-pattern.md) | [medium](./content/design-patterns-101/medium/05.html) | Draft |
| 6 | 디자인 패턴 101 (6/10): 어댑터 패턴 | [ko](./content/design-patterns-101/ko/06-adapter-pattern.md) | [en](./content/design-patterns-101/en/06-adapter-pattern.md) | [medium](./content/design-patterns-101/medium/06.html) | Draft |
| 7 | 디자인 패턴 101 (7/10): 옵저버 패턴 | [ko](./content/design-patterns-101/ko/07-observer-pattern.md) | [en](./content/design-patterns-101/en/07-observer-pattern.md) | [medium](./content/design-patterns-101/medium/07.html) | Draft |
| 8 | 디자인 패턴 101 (8/10): 팩토리와 의존성 주입 | [ko](./content/design-patterns-101/ko/08-factory-and-di.md) | [en](./content/design-patterns-101/en/08-factory-and-di.md) | [medium](./content/design-patterns-101/medium/08.html) | Draft |
| 9 | 디자인 패턴 101 (9/10): 패턴을 남용하지 않는 법 | [ko](./content/design-patterns-101/ko/09-avoiding-pattern-overuse.md) | [en](./content/design-patterns-101/en/09-avoiding-pattern-overuse.md) | [medium](./content/design-patterns-101/medium/09.html) | Draft |
| 10 | 디자인 패턴 101 (10/10): 파이썬에 어울리는 패턴 | [ko](./content/design-patterns-101/ko/10-pythonic-patterns.md) | [en](./content/design-patterns-101/en/10-pythonic-patterns.md) | [medium](./content/design-patterns-101/medium/10.html) | Draft |

### API Design 101 (`api-design-101`)

REST 기본부터 리소스 설계, HTTP method/status, schema, pagination, error, OpenAPI까지 쓰기 좋은 API를 설계하는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/api-design-101/`](./content/api-design-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | API Design 101 (1/10): API란 무엇인가? | [ko](./content/api-design-101/ko/01-what-is-an-api.md) | [en](./content/api-design-101/en/01-what-is-an-api.md) | [medium](./content/api-design-101/medium/01.html) | Draft |
| 2 | API Design 101 (2/10): REST 기본 | [ko](./content/api-design-101/ko/02-rest-basics.md) | [en](./content/api-design-101/en/02-rest-basics.md) | [medium](./content/api-design-101/medium/02.html) | Draft |
| 3 | API Design 101 (3/10): 리소스 설계 | [ko](./content/api-design-101/ko/03-resource-design.md) | [en](./content/api-design-101/en/03-resource-design.md) | [medium](./content/api-design-101/medium/03.html) | Draft |
| 4 | API Design 101 (4/10): HTTP method와 status code | [ko](./content/api-design-101/ko/04-http-methods-and-status.md) | [en](./content/api-design-101/en/04-http-methods-and-status.md) | [medium](./content/api-design-101/medium/04.html) | Draft |
| 5 | API Design 101 (5/10): Request와 response schema | [ko](./content/api-design-101/ko/05-request-and-response-schema.md) | [en](./content/api-design-101/en/05-request-and-response-schema.md) | [medium](./content/api-design-101/medium/05.html) | Draft |
| 6 | API Design 101 (6/10): Pagination과 filtering | [ko](./content/api-design-101/ko/06-pagination-and-filtering.md) | [en](./content/api-design-101/en/06-pagination-and-filtering.md) | [medium](./content/api-design-101/medium/06.html) | Draft |
| 7 | API Design 101 (7/10): Error response 설계 | [ko](./content/api-design-101/ko/07-error-response-design.md) | [en](./content/api-design-101/en/07-error-response-design.md) | [medium](./content/api-design-101/medium/07.html) | Draft |
| 8 | API Design 101 (8/10): OpenAPI와 Swagger | [ko](./content/api-design-101/ko/08-openapi-and-swagger.md) | [en](./content/api-design-101/en/08-openapi-and-swagger.md) | [medium](./content/api-design-101/medium/08.html) | Draft |
| 9 | API Design 101 (9/10): Versioning | [ko](./content/api-design-101/ko/09-api-versioning.md) | [en](./content/api-design-101/en/09-api-versioning.md) | [medium](./content/api-design-101/medium/09.html) | Draft |
| 10 | API Design 101 (10/10): 좋은 API 문서 만들기 | [ko](./content/api-design-101/ko/10-writing-good-api-docs.md) | [en](./content/api-design-101/en/10-writing-good-api-docs.md) | [medium](./content/api-design-101/medium/10.html) | Draft |

### Web Development 101 (`web-development-101`)

HTML/CSS/JS, 브라우저, HTTP, 프론트/백엔드, 인증, DB, 배포까지 웹 개발 전체 흐름을 한 번에 보는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/web-development-101/`](./content/web-development-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Web Development 101 (1/10): 웹은 어떻게 동작하는가? | [ko](./content/web-development-101/ko/01-how-the-web-works.md) | [en](./content/web-development-101/en/01-how-the-web-works.md) | [medium](./content/web-development-101/medium/01.html) | Draft |
| 2 | Web Development 101 (2/10): HTML, CSS, JavaScript | [ko](./content/web-development-101/ko/02-html-css-javascript.md) | [en](./content/web-development-101/en/02-html-css-javascript.md) | [medium](./content/web-development-101/medium/02.html) | Draft |
| 3 | Web Development 101 (3/10): 브라우저와 DOM | [ko](./content/web-development-101/ko/03-browser-and-dom.md) | [en](./content/web-development-101/en/03-browser-and-dom.md) | [medium](./content/web-development-101/medium/03.html) | Draft |
| 4 | Web Development 101 (4/10): HTTP와 API | [ko](./content/web-development-101/ko/04-http-and-api.md) | [en](./content/web-development-101/en/04-http-and-api.md) | [medium](./content/web-development-101/medium/04.html) | Draft |
| 5 | Web Development 101 (5/10): Frontend와 Backend | [ko](./content/web-development-101/ko/05-frontend-and-backend.md) | [en](./content/web-development-101/en/05-frontend-and-backend.md) | [medium](./content/web-development-101/medium/05.html) | Draft |
| 6 | Web Development 101 (6/10): 인증과 세션 | [ko](./content/web-development-101/ko/06-auth-and-sessions.md) | [en](./content/web-development-101/en/06-auth-and-sessions.md) | [medium](./content/web-development-101/medium/06.html) | Draft |
| 7 | Web Development 101 (7/10): 데이터베이스 연결 | [ko](./content/web-development-101/ko/07-connecting-to-database.md) | [en](./content/web-development-101/en/07-connecting-to-database.md) | [medium](./content/web-development-101/medium/07.html) | Draft |
| 8 | Web Development 101 (8/10): 배포 | [ko](./content/web-development-101/ko/08-deployment.md) | [en](./content/web-development-101/en/08-deployment.md) | [medium](./content/web-development-101/medium/08.html) | Draft |
| 9 | Web Development 101 (9/10): 성능과 캐싱 | [ko](./content/web-development-101/ko/09-performance-and-caching.md) | [en](./content/web-development-101/en/09-performance-and-caching.md) | [medium](./content/web-development-101/medium/09.html) | Draft |
| 10 | Web Development 101 (10/10): 작은 웹앱 만들기 | [ko](./content/web-development-101/ko/10-building-a-small-web-app.md) | [en](./content/web-development-101/en/10-building-a-small-web-app.md) | [medium](./content/web-development-101/medium/10.html) | Draft |

### Frontend Development 101 (`frontend-development-101`)

HTML/CSS, JavaScript, 컴포넌트, 라우팅, API 호출, 빌드까지 현대 프론트엔드 개발 전체 흐름을 다루는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/frontend-development-101/`](./content/frontend-development-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Frontend Development 101 (1/10): 프론트엔드 개발이란 무엇인가? | [ko](./content/frontend-development-101/ko/01-what-is-frontend-development.md) | [en](./content/frontend-development-101/en/01-what-is-frontend-development.md) | [medium](./content/frontend-development-101/medium/01.html) | Draft |
| 2 | Frontend Development 101 (2/10): HTML과 CSS 기본 | [ko](./content/frontend-development-101/ko/02-html-and-css-basics.md) | [en](./content/frontend-development-101/en/02-html-and-css-basics.md) | [medium](./content/frontend-development-101/medium/02.html) | Draft |
| 3 | Frontend Development 101 (3/10): JavaScript 기본 | [ko](./content/frontend-development-101/ko/03-javascript-basics.md) | [en](./content/frontend-development-101/en/03-javascript-basics.md) | [medium](./content/frontend-development-101/medium/03.html) | Draft |
| 4 | Frontend Development 101 (4/10): 컴포넌트와 상태 | [ko](./content/frontend-development-101/ko/04-components-and-state.md) | [en](./content/frontend-development-101/en/04-components-and-state.md) | [medium](./content/frontend-development-101/medium/04.html) | Draft |
| 5 | Frontend Development 101 (5/10): 라우팅과 페이지 | [ko](./content/frontend-development-101/ko/05-routing-and-pages.md) | [en](./content/frontend-development-101/en/05-routing-and-pages.md) | [medium](./content/frontend-development-101/medium/05.html) | Draft |
| 6 | Frontend Development 101 (6/10): API 호출과 비동기 | [ko](./content/frontend-development-101/ko/06-api-calls-and-async.md) | [en](./content/frontend-development-101/en/06-api-calls-and-async.md) | [medium](./content/frontend-development-101/medium/06.html) | Draft |
| 7 | Frontend Development 101 (7/10): 폼과 유효성 검사 | [ko](./content/frontend-development-101/ko/07-forms-and-validation.md) | [en](./content/frontend-development-101/en/07-forms-and-validation.md) | [medium](./content/frontend-development-101/medium/07.html) | Draft |
| 8 | Frontend Development 101 (8/10): 스타일링과 디자인 시스템 | [ko](./content/frontend-development-101/ko/08-styling-and-design-system.md) | [en](./content/frontend-development-101/en/08-styling-and-design-system.md) | [medium](./content/frontend-development-101/medium/08.html) | Draft |
| 9 | Frontend Development 101 (9/10): 빌드 도구와 번들링 | [ko](./content/frontend-development-101/ko/09-build-tools-and-bundling.md) | [en](./content/frontend-development-101/en/09-build-tools-and-bundling.md) | [medium](./content/frontend-development-101/medium/09.html) | Draft |
| 10 | Frontend Development 101 (10/10): 작은 프론트엔드 앱 만들기 | [ko](./content/frontend-development-101/ko/10-building-a-small-frontend-app.md) | [en](./content/frontend-development-101/en/10-building-a-small-frontend-app.md) | [medium](./content/frontend-development-101/medium/10.html) | Draft |

### Backend Development 101 (`backend-development-101`)

HTTP 서버/라우팅/서비스/DB layer/인증/로깅/테스트/배포까지 백엔드 개발 전체 흐름을 다루는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/backend-development-101/`](./content/backend-development-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Backend Development 101 (1/10): 백엔드 개발이란 무엇인가? | [ko](./content/backend-development-101/ko/01-what-is-backend-development.md) | [en](./content/backend-development-101/en/01-what-is-backend-development.md) | [medium](./content/backend-development-101/medium/01.html) | Draft |
| 2 | Backend Development 101 (2/10): HTTP 서버 만들기 | [ko](./content/backend-development-101/ko/02-building-an-http-server.md) | [en](./content/backend-development-101/en/02-building-an-http-server.md) | [medium](./content/backend-development-101/medium/02.html) | Draft |
| 3 | Backend Development 101 (3/10): Routing과 Controller | [ko](./content/backend-development-101/ko/03-routing-and-controllers.md) | [en](./content/backend-development-101/en/03-routing-and-controllers.md) | [medium](./content/backend-development-101/medium/03.html) | Draft |
| 4 | Backend Development 101 (4/10): Service Layer | [ko](./content/backend-development-101/ko/04-service-layer.md) | [en](./content/backend-development-101/en/04-service-layer.md) | [medium](./content/backend-development-101/medium/04.html) | Draft |
| 5 | Backend Development 101 (5/10): Database Layer | [ko](./content/backend-development-101/ko/05-database-layer.md) | [en](./content/backend-development-101/en/05-database-layer.md) | [medium](./content/backend-development-101/medium/05.html) | Draft |
| 6 | Backend Development 101 (6/10): 인증과 권한 | [ko](./content/backend-development-101/ko/06-auth-and-authorization.md) | [en](./content/backend-development-101/en/06-auth-and-authorization.md) | [medium](./content/backend-development-101/medium/06.html) | Draft |
| 7 | Backend Development 101 (7/10): Logging과 Error Handling | [ko](./content/backend-development-101/ko/07-logging-and-error-handling.md) | [en](./content/backend-development-101/en/07-logging-and-error-handling.md) | [medium](./content/backend-development-101/medium/07.html) | Draft |
| 8 | Backend Development 101 (8/10): 백엔드 테스트 | [ko](./content/backend-development-101/ko/08-testing-the-backend.md) | [en](./content/backend-development-101/en/08-testing-the-backend.md) | [medium](./content/backend-development-101/medium/08.html) | Draft |
| 9 | Backend Development 101 (9/10): 백엔드 배포 | [ko](./content/backend-development-101/ko/09-deploying-the-backend.md) | [en](./content/backend-development-101/en/09-deploying-the-backend.md) | [medium](./content/backend-development-101/medium/09.html) | Draft |
| 10 | Backend Development 101 (10/10): 운영 가능한 백엔드 구조 | [ko](./content/backend-development-101/ko/10-production-ready-backend.md) | [en](./content/backend-development-101/en/10-production-ready-backend.md) | [medium](./content/backend-development-101/medium/10.html) | Draft |

### Testing 101 (`testing-101`)

Unit, Integration, E2E, Test Double, Mock, Coverage, CI 연동까지 테스트 전략 전반을 다루는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/testing-101/`](./content/testing-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Testing 101 (1/10): 테스트란 무엇인가? | [ko](./content/testing-101/ko/01-what-is-testing.md) | [en](./content/testing-101/en/01-what-is-testing.md) | [medium](./content/testing-101/medium/01.html) | Draft |
| 2 | Testing 101 (2/10): 단위 테스트 | [ko](./content/testing-101/ko/02-unit-test.md) | [en](./content/testing-101/en/02-unit-test.md) | [medium](./content/testing-101/medium/02.html) | Draft |
| 3 | Testing 101 (3/10): 통합 테스트 | [ko](./content/testing-101/ko/03-integration-test.md) | [en](./content/testing-101/en/03-integration-test.md) | [medium](./content/testing-101/medium/03.html) | Draft |
| 4 | Testing 101 (4/10): E2E 테스트 | [ko](./content/testing-101/ko/04-e2e-test.md) | [en](./content/testing-101/en/04-e2e-test.md) | [medium](./content/testing-101/medium/04.html) | Draft |
| 5 | Testing 101 (5/10): 테스트 더블 | [ko](./content/testing-101/ko/05-test-double.md) | [en](./content/testing-101/en/05-test-double.md) | [medium](./content/testing-101/medium/05.html) | Draft |
| 6 | Testing 101 (6/10): Mock과 Stub | [ko](./content/testing-101/ko/06-mock-and-stub.md) | [en](./content/testing-101/en/06-mock-and-stub.md) | [medium](./content/testing-101/medium/06.html) | Draft |
| 7 | Testing 101 (7/10): 테스트 커버리지 | [ko](./content/testing-101/ko/07-test-coverage.md) | [en](./content/testing-101/en/07-test-coverage.md) | [medium](./content/testing-101/medium/07.html) | Draft |
| 8 | Testing 101 (8/10): 회귀 테스트 | [ko](./content/testing-101/ko/08-regression-test.md) | [en](./content/testing-101/en/08-regression-test.md) | [medium](./content/testing-101/medium/08.html) | Draft |
| 9 | Testing 101 (9/10): CI에서 테스트 실행하기 | [ko](./content/testing-101/ko/09-tests-in-ci.md) | [en](./content/testing-101/en/09-tests-in-ci.md) | [medium](./content/testing-101/medium/09.html) | Draft |
| 10 | Testing 101 (10/10): 테스트 전략 세우기 | [ko](./content/testing-101/ko/10-test-strategy.md) | [en](./content/testing-101/en/10-test-strategy.md) | [medium](./content/testing-101/medium/10.html) | Draft |

### Containers 101 (`containers-101`)

Image, runtime, layer, Dockerfile부터 보안까지 컨테이너의 큰 그림을 입문자 관점에서 다룹니다.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/containers-101/`](./content/containers-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Containers 101 (1/10): Container란 무엇인가? | [ko](./content/containers-101/ko/01-what-is-a-container.md) | [en](./content/containers-101/en/01-what-is-a-container.md) | [medium](./content/containers-101/medium/01.html) | Draft |
| 2 | Containers 101 (2/10): Image와 Layer | [ko](./content/containers-101/ko/02-image-and-layer.md) | [en](./content/containers-101/en/02-image-and-layer.md) | [medium](./content/containers-101/medium/02.html) | Draft |
| 3 | Containers 101 (3/10): Runtime | [ko](./content/containers-101/ko/03-runtime.md) | [en](./content/containers-101/en/03-runtime.md) | [medium](./content/containers-101/medium/03.html) | Draft |
| 4 | Containers 101 (4/10): Dockerfile | [ko](./content/containers-101/ko/04-dockerfile.md) | [en](./content/containers-101/en/04-dockerfile.md) | [medium](./content/containers-101/medium/04.html) | Draft |
| 5 | Containers 101 (5/10): Volume | [ko](./content/containers-101/ko/05-volume.md) | [en](./content/containers-101/en/05-volume.md) | [medium](./content/containers-101/medium/05.html) | Draft |
| 6 | Containers 101 (6/10): Network | [ko](./content/containers-101/ko/06-network.md) | [en](./content/containers-101/en/06-network.md) | [medium](./content/containers-101/medium/06.html) | Draft |
| 7 | Containers 101 (7/10): Registry | [ko](./content/containers-101/ko/07-registry.md) | [en](./content/containers-101/en/07-registry.md) | [medium](./content/containers-101/medium/07.html) | Draft |
| 8 | Containers 101 (8/10): Container Security | [ko](./content/containers-101/ko/08-container-security.md) | [en](./content/containers-101/en/08-container-security.md) | [medium](./content/containers-101/medium/08.html) | Draft |
| 9 | Containers 101 (9/10): Containers vs VMs | [ko](./content/containers-101/ko/09-container-vs-vm.md) | [en](./content/containers-101/en/09-container-vs-vm.md) | [medium](./content/containers-101/medium/09.html) | Draft |
| 10 | Containers 101 (10/10): 실전 컨테이너 앱 만들기 | [ko](./content/containers-101/ko/10-build-a-container-app.md) | [en](./content/containers-101/en/10-build-a-container-app.md) | [medium](./content/containers-101/medium/10.html) | Draft |

### Docker 101 (`docker-101`)

Image, Container, Dockerfile, Volume, Network, Compose, 환경 설정, Python 앱 컨테이너화, 이미지 최적화, 배포 구성을 다루는 입문 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/docker-101/`](./content/docker-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Docker 101 (1/10): Docker란 무엇인가? | [ko](./content/docker-101/ko/01-what-is-docker.md) | [en](./content/docker-101/en/01-what-is-docker.md) | [medium](./content/docker-101/medium/01.html) | Draft |
| 2 | Docker 101 (2/10): Image와 Container | [ko](./content/docker-101/ko/02-image-and-container.md) | [en](./content/docker-101/en/02-image-and-container.md) | [medium](./content/docker-101/medium/02.html) | Draft |
| 3 | Docker 101 (3/10): Dockerfile 작성하기 | [ko](./content/docker-101/ko/03-dockerfile.md) | [en](./content/docker-101/en/03-dockerfile.md) | [medium](./content/docker-101/medium/03.html) | Draft |
| 4 | Docker 101 (4/10): Volume과 Network | [ko](./content/docker-101/ko/04-volume-and-network.md) | [en](./content/docker-101/en/04-volume-and-network.md) | [medium](./content/docker-101/medium/04.html) | Draft |
| 5 | Docker 101 (5/10): Docker Compose | [ko](./content/docker-101/ko/05-docker-compose.md) | [en](./content/docker-101/en/05-docker-compose.md) | [medium](./content/docker-101/medium/05.html) | Draft |
| 6 | Docker 101 (6/10): 환경변수와 설정 | [ko](./content/docker-101/ko/06-env-and-config.md) | [en](./content/docker-101/en/06-env-and-config.md) | [medium](./content/docker-101/medium/06.html) | Draft |
| 7 | Docker 101 (7/10): Python 앱 컨테이너화 | [ko](./content/docker-101/ko/07-python-app-containerize.md) | [en](./content/docker-101/en/07-python-app-containerize.md) | [medium](./content/docker-101/medium/07.html) | Draft |
| 8 | Docker 101 (8/10): 데이터베이스와 함께 실행하기 | [ko](./content/docker-101/ko/08-database-with-app.md) | [en](./content/docker-101/en/08-database-with-app.md) | [medium](./content/docker-101/medium/08.html) | Draft |
| 9 | Docker 101 (9/10): Image 최적화 | [ko](./content/docker-101/ko/09-image-optimization.md) | [en](./content/docker-101/en/09-image-optimization.md) | [medium](./content/docker-101/medium/09.html) | Draft |
| 10 | Docker 101 (10/10): 배포용 Docker 구성 | [ko](./content/docker-101/ko/10-production-docker.md) | [en](./content/docker-101/en/10-production-docker.md) | [medium](./content/docker-101/medium/10.html) | Draft |

### Kubernetes 101 (`kubernetes-101`)

Pod, Deployment, Service, Ingress, ConfigMap/Secret, Volume, HPA, Helm까지 Kubernetes 기본 객체를 다루는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/kubernetes-101/`](./content/kubernetes-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Kubernetes 101 (1/10): Kubernetes란 무엇인가? | [ko](./content/kubernetes-101/ko/01-what-is-kubernetes.md) | [en](./content/kubernetes-101/en/01-what-is-kubernetes.md) | [medium](./content/kubernetes-101/medium/01.html) | Draft |
| 2 | Kubernetes 101 (2/10): Pod | [ko](./content/kubernetes-101/ko/02-pod.md) | [en](./content/kubernetes-101/en/02-pod.md) | [medium](./content/kubernetes-101/medium/02.html) | Draft |
| 3 | Kubernetes 101 (3/10): Deployment | [ko](./content/kubernetes-101/ko/03-deployment.md) | [en](./content/kubernetes-101/en/03-deployment.md) | [medium](./content/kubernetes-101/medium/03.html) | Draft |
| 4 | Kubernetes 101 (4/10): Service | [ko](./content/kubernetes-101/ko/04-service.md) | [en](./content/kubernetes-101/en/04-service.md) | [medium](./content/kubernetes-101/medium/04.html) | Draft |
| 5 | Kubernetes 101 (5/10): Ingress | [ko](./content/kubernetes-101/ko/05-ingress.md) | [en](./content/kubernetes-101/en/05-ingress.md) | [medium](./content/kubernetes-101/medium/05.html) | Draft |
| 6 | Kubernetes 101 (6/10): ConfigMap과 Secret | [ko](./content/kubernetes-101/ko/06-configmap-and-secret.md) | [en](./content/kubernetes-101/en/06-configmap-and-secret.md) | [medium](./content/kubernetes-101/medium/06.html) | Draft |
| 7 | Kubernetes 101 (7/10): Volume | [ko](./content/kubernetes-101/ko/07-volume.md) | [en](./content/kubernetes-101/en/07-volume.md) | [medium](./content/kubernetes-101/medium/07.html) | Draft |
| 8 | Kubernetes 101 (8/10): HPA | [ko](./content/kubernetes-101/ko/08-hpa.md) | [en](./content/kubernetes-101/en/08-hpa.md) | [medium](./content/kubernetes-101/medium/08.html) | Draft |
| 9 | Kubernetes 101 (9/10): Helm | [ko](./content/kubernetes-101/ko/09-helm.md) | [en](./content/kubernetes-101/en/09-helm.md) | [medium](./content/kubernetes-101/medium/09.html) | Draft |
| 10 | Kubernetes 101 (10/10): 운영 관점의 Kubernetes | [ko](./content/kubernetes-101/ko/10-kubernetes-in-operation.md) | [en](./content/kubernetes-101/en/10-kubernetes-in-operation.md) | [medium](./content/kubernetes-101/medium/10.html) | Draft |

### Cloud Computing 101 (`cloud-computing-101`)

IaaS/PaaS/SaaS, 리전, 컴퓨트, 스토리지, 네트워크, 아이덴티티, 모니터링, 비용까지 클라우드 입문 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/cloud-computing-101/`](./content/cloud-computing-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Cloud Computing 101 (1/10): Cloud Computing이란 무엇인가? | [ko](./content/cloud-computing-101/ko/01-what-is-cloud-computing.md) | [en](./content/cloud-computing-101/en/01-what-is-cloud-computing.md) | [medium](./content/cloud-computing-101/medium/01.html) | Draft |
| 2 | Cloud Computing 101 (2/10): IaaS, PaaS, SaaS | [ko](./content/cloud-computing-101/ko/02-iaas-paas-saas.md) | [en](./content/cloud-computing-101/en/02-iaas-paas-saas.md) | [medium](./content/cloud-computing-101/medium/02.html) | Draft |
| 3 | Cloud Computing 101 (3/10): Region과 Availability Zone | [ko](./content/cloud-computing-101/ko/03-region-and-availability-zone.md) | [en](./content/cloud-computing-101/en/03-region-and-availability-zone.md) | [medium](./content/cloud-computing-101/medium/03.html) | Draft |
| 4 | Cloud Computing 101 (4/10): Compute | [ko](./content/cloud-computing-101/ko/04-compute.md) | [en](./content/cloud-computing-101/en/04-compute.md) | [medium](./content/cloud-computing-101/medium/04.html) | Draft |
| 5 | Cloud Computing 101 (5/10): Storage | [ko](./content/cloud-computing-101/ko/05-storage.md) | [en](./content/cloud-computing-101/en/05-storage.md) | [medium](./content/cloud-computing-101/medium/05.html) | Draft |
| 6 | Cloud Computing 101 (6/10): Network | [ko](./content/cloud-computing-101/ko/06-network.md) | [en](./content/cloud-computing-101/en/06-network.md) | [medium](./content/cloud-computing-101/medium/06.html) | Draft |
| 7 | Cloud Computing 101 (7/10): Identity와 Security | [ko](./content/cloud-computing-101/ko/07-identity-and-security.md) | [en](./content/cloud-computing-101/en/07-identity-and-security.md) | [medium](./content/cloud-computing-101/medium/07.html) | Draft |
| 8 | Cloud Computing 101 (8/10): Monitoring | [ko](./content/cloud-computing-101/ko/08-monitoring.md) | [en](./content/cloud-computing-101/en/08-monitoring.md) | [medium](./content/cloud-computing-101/medium/08.html) | Draft |
| 9 | Cloud Computing 101 (9/10): Cost Management | [ko](./content/cloud-computing-101/ko/09-cost-management.md) | [en](./content/cloud-computing-101/en/09-cost-management.md) | [medium](./content/cloud-computing-101/medium/09.html) | Draft |
| 10 | Cloud Computing 101 (10/10): Cloud Architecture 기초 | [ko](./content/cloud-computing-101/ko/10-cloud-architecture-basics.md) | [en](./content/cloud-computing-101/en/10-cloud-architecture-basics.md) | [medium](./content/cloud-computing-101/medium/10.html) | Draft |

### Serverless 101 (`serverless-101`)

FaaS, trigger/event, cold start, scaling, state, queue, observability, cost까지 서버리스 입문 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/serverless-101/`](./content/serverless-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Serverless 101 (1/10): 서버리스란 무엇인가? | [ko](./content/serverless-101/ko/01-what-is-serverless.md) | [en](./content/serverless-101/en/01-what-is-serverless.md) | [medium](./content/serverless-101/medium/01.html) | Draft |
| 2 | Serverless 101 (2/10): 함수형 서비스(FaaS)란 무엇인가? | [ko](./content/serverless-101/ko/02-function-as-a-service.md) | [en](./content/serverless-101/en/02-function-as-a-service.md) | [medium](./content/serverless-101/medium/02.html) | Draft |
| 3 | Serverless 101 (3/10): 트리거와 이벤트 | [ko](./content/serverless-101/ko/03-trigger-and-event.md) | [en](./content/serverless-101/en/03-trigger-and-event.md) | [medium](./content/serverless-101/medium/03.html) | Draft |
| 4 | Serverless 101 (4/10): 콜드 스타트 | [ko](./content/serverless-101/ko/04-cold-start.md) | [en](./content/serverless-101/en/04-cold-start.md) | [medium](./content/serverless-101/medium/04.html) | Draft |
| 5 | Serverless 101 (5/10): 스케일링 | [ko](./content/serverless-101/ko/05-scaling.md) | [en](./content/serverless-101/en/05-scaling.md) | [medium](./content/serverless-101/medium/05.html) | Draft |
| 6 | Serverless 101 (6/10): 상태 관리 | [ko](./content/serverless-101/ko/06-state-management.md) | [en](./content/serverless-101/en/06-state-management.md) | [medium](./content/serverless-101/medium/06.html) | Draft |
| 7 | Serverless 101 (7/10): 큐와 이벤트 기반 아키텍처 | [ko](./content/serverless-101/ko/07-queue-and-event-driven.md) | [en](./content/serverless-101/en/07-queue-and-event-driven.md) | [medium](./content/serverless-101/medium/07.html) | Draft |
| 8 | Serverless 101 (8/10): 관측성 | [ko](./content/serverless-101/ko/08-observability.md) | [en](./content/serverless-101/en/08-observability.md) | [medium](./content/serverless-101/medium/08.html) | Draft |
| 9 | Serverless 101 (9/10): 비용 | [ko](./content/serverless-101/ko/09-cost.md) | [en](./content/serverless-101/en/09-cost.md) | [medium](./content/serverless-101/medium/09.html) | Draft |
| 10 | Serverless 101 (10/10): 서버리스 앱 설계 | [ko](./content/serverless-101/ko/10-serverless-app-design.md) | [en](./content/serverless-101/en/10-serverless-app-design.md) | [medium](./content/serverless-101/medium/10.html) | Draft |

### DevOps 101 (`devops-101`)

CI/CD, IaC, 환경 관리, 모니터링, 배포 전략, on-call까지 DevOps 입문 전반을 다루는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/devops-101/`](./content/devops-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | DevOps 101 (1/10): DevOps란 무엇인가? | [ko](./content/devops-101/ko/01-what-is-devops.md) | [en](./content/devops-101/en/01-what-is-devops.md) | [medium](./content/devops-101/medium/01.html) | Draft |
| 2 | DevOps 101 (2/10): CI 파이프라인 | [ko](./content/devops-101/ko/02-ci-pipeline.md) | [en](./content/devops-101/en/02-ci-pipeline.md) | [medium](./content/devops-101/medium/02.html) | Draft |
| 3 | DevOps 101 (3/10): CD와 배포 전략 | [ko](./content/devops-101/ko/03-cd-and-deployment.md) | [en](./content/devops-101/en/03-cd-and-deployment.md) | [medium](./content/devops-101/medium/03.html) | Draft |
| 4 | DevOps 101 (4/10): 환경 분리와 설정 관리 | [ko](./content/devops-101/ko/04-environments-and-config.md) | [en](./content/devops-101/en/04-environments-and-config.md) | [medium](./content/devops-101/medium/04.html) | Draft |
| 5 | DevOps 101 (5/10): Infrastructure as Code | [ko](./content/devops-101/ko/05-infrastructure-as-code.md) | [en](./content/devops-101/en/05-infrastructure-as-code.md) | [medium](./content/devops-101/medium/05.html) | Draft |
| 6 | DevOps 101 (6/10): 컨테이너와 빌드 | [ko](./content/devops-101/ko/06-containers-and-build.md) | [en](./content/devops-101/en/06-containers-and-build.md) | [medium](./content/devops-101/medium/06.html) | Draft |
| 7 | DevOps 101 (7/10): 모니터링과 알림 | [ko](./content/devops-101/ko/07-monitoring-and-alerting.md) | [en](./content/devops-101/en/07-monitoring-and-alerting.md) | [medium](./content/devops-101/medium/07.html) | Draft |
| 8 | DevOps 101 (8/10): 로그 수집과 분석 | [ko](./content/devops-101/ko/08-logging-and-analysis.md) | [en](./content/devops-101/en/08-logging-and-analysis.md) | [medium](./content/devops-101/medium/08.html) | Draft |
| 9 | DevOps 101 (9/10): 장애 대응과 on-call | [ko](./content/devops-101/ko/09-incident-and-oncall.md) | [en](./content/devops-101/en/09-incident-and-oncall.md) | [medium](./content/devops-101/medium/09.html) | Draft |
| 10 | DevOps 101 (10/10): 운영 가능한 DevOps 흐름 | [ko](./content/devops-101/ko/10-operable-devops-flow.md) | [en](./content/devops-101/en/10-operable-devops-flow.md) | [medium](./content/devops-101/medium/10.html) | Draft |

### GitHub Actions 101 (`github-actions-101`)

Workflow, Job, Trigger, 테스트 자동화, 빌드 아티팩트, 배포, secret 관리까지 GitHub Actions 전반을 다루는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/github-actions-101/`](./content/github-actions-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | GitHub Actions 101 (1/10): GitHub Actions란 무엇인가? | [ko](./content/github-actions-101/ko/01-what-is-github-actions.md) | [en](./content/github-actions-101/en/01-what-is-github-actions.md) | [medium](./content/github-actions-101/medium/01.html) | Draft |
| 2 | GitHub Actions 101 (2/10): Workflow와 Job | [ko](./content/github-actions-101/ko/02-workflow-and-job.md) | [en](./content/github-actions-101/en/02-workflow-and-job.md) | [medium](./content/github-actions-101/medium/02.html) | Draft |
| 3 | GitHub Actions 101 (3/10): Trigger 이해하기 | [ko](./content/github-actions-101/ko/03-triggers.md) | [en](./content/github-actions-101/en/03-triggers.md) | [medium](./content/github-actions-101/medium/03.html) | Draft |
| 4 | GitHub Actions 101 (4/10): Python 테스트 자동화 | [ko](./content/github-actions-101/ko/04-python-test-automation.md) | [en](./content/github-actions-101/en/04-python-test-automation.md) | [medium](./content/github-actions-101/medium/04.html) | Draft |
| 5 | GitHub Actions 101 (5/10): Lint와 Type Check | [ko](./content/github-actions-101/ko/05-lint-and-typecheck.md) | [en](./content/github-actions-101/en/05-lint-and-typecheck.md) | [medium](./content/github-actions-101/medium/05.html) | Draft |
| 6 | GitHub Actions 101 (6/10): 빌드 아티팩트 | [ko](./content/github-actions-101/ko/06-build-artifact.md) | [en](./content/github-actions-101/en/06-build-artifact.md) | [medium](./content/github-actions-101/medium/06.html) | Draft |
| 7 | GitHub Actions 101 (7/10): Docker 빌드 | [ko](./content/github-actions-101/ko/07-docker-build.md) | [en](./content/github-actions-101/en/07-docker-build.md) | [medium](./content/github-actions-101/medium/07.html) | Draft |
| 8 | GitHub Actions 101 (8/10): 배포 자동화 | [ko](./content/github-actions-101/ko/08-deploy-automation.md) | [en](./content/github-actions-101/en/08-deploy-automation.md) | [medium](./content/github-actions-101/medium/08.html) | Draft |
| 9 | GitHub Actions 101 (9/10): Secret 관리 | [ko](./content/github-actions-101/ko/09-secret-management.md) | [en](./content/github-actions-101/en/09-secret-management.md) | [medium](./content/github-actions-101/medium/09.html) | Draft |
| 10 | GitHub Actions 101 (10/10): 실전 CI/CD 파이프라인 | [ko](./content/github-actions-101/ko/10-real-world-cicd-pipeline.md) | [en](./content/github-actions-101/en/10-real-world-cicd-pipeline.md) | [medium](./content/github-actions-101/medium/10.html) | Draft |

### Observability 101 (`observability-101`)

Metric, log, trace, dashboard, alert, SLO 기초까지 운영 시스템의 가시성을 만드는 입문 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/observability-101/`](./content/observability-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Observability 101 (1/10): 관측성이란 무엇인가? | [ko](./content/observability-101/ko/01-what-is-observability.md) | [en](./content/observability-101/en/01-what-is-observability.md) | [medium](./content/observability-101/medium/01.html) | Draft |
| 2 | Observability 101 (2/10): 메트릭, 로그, 트레이스 | [ko](./content/observability-101/ko/02-metric-log-trace.md) | [en](./content/observability-101/en/02-metric-log-trace.md) | [medium](./content/observability-101/medium/02.html) | Draft |
| 3 | Observability 101 (3/10): 메트릭 수집과 시각화 | [ko](./content/observability-101/ko/03-metric-collection.md) | [en](./content/observability-101/en/03-metric-collection.md) | [medium](./content/observability-101/medium/03.html) | Draft |
| 4 | Observability 101 (4/10): 구조화된 로깅 | [ko](./content/observability-101/ko/04-structured-logging.md) | [en](./content/observability-101/en/04-structured-logging.md) | [medium](./content/observability-101/medium/04.html) | Draft |
| 5 | Observability 101 (5/10): 분산 트레이싱 기초 | [ko](./content/observability-101/ko/05-distributed-tracing.md) | [en](./content/observability-101/en/05-distributed-tracing.md) | [medium](./content/observability-101/medium/05.html) | Draft |
| 6 | Observability 101 (6/10): 대시보드 설계 | [ko](./content/observability-101/ko/06-dashboard-design.md) | [en](./content/observability-101/en/06-dashboard-design.md) | [medium](./content/observability-101/medium/06.html) | Draft |
| 7 | Observability 101 (7/10): 경보와 온콜 | [ko](./content/observability-101/ko/07-alert-and-oncall.md) | [en](./content/observability-101/en/07-alert-and-oncall.md) | [medium](./content/observability-101/medium/07.html) | Draft |
| 8 | Observability 101 (8/10): 서비스 수준 지표와 목표 기초 | [ko](./content/observability-101/ko/08-sli-and-slo.md) | [en](./content/observability-101/en/08-sli-and-slo.md) | [medium](./content/observability-101/medium/08.html) | Draft |
| 9 | Observability 101 (9/10): 비용과 카디널리티 | [ko](./content/observability-101/ko/09-cost-and-cardinality.md) | [en](./content/observability-101/en/09-cost-and-cardinality.md) | [medium](./content/observability-101/medium/09.html) | Draft |
| 10 | Observability 101 (10/10): 운영 가능한 관측성 스택 | [ko](./content/observability-101/ko/10-production-observability-stack.md) | [en](./content/observability-101/en/10-production-observability-stack.md) | [medium](./content/observability-101/medium/10.html) | Draft |

### Incident Response 101 (`incident-response-101`)

Severity 분류, 초기 대응, 커뮤니케이션, 타임라인, RCA, 완화, 포스트모템, 재발 방지, 런북 작성까지 다루는 입문 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/incident-response-101/`](./content/incident-response-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Incident Response 101 (1/10): Incident란 무엇인가? | [ko](./content/incident-response-101/ko/01-what-is-incident.md) | [en](./content/incident-response-101/en/01-what-is-incident.md) | [medium](./content/incident-response-101/medium/01.html) | Draft |
| 2 | Incident Response 101 (2/10): Severity 분류 | [ko](./content/incident-response-101/ko/02-severity.md) | [en](./content/incident-response-101/en/02-severity.md) | [medium](./content/incident-response-101/medium/02.html) | Draft |
| 3 | Incident Response 101 (3/10): 초기 대응 | [ko](./content/incident-response-101/ko/03-initial-response.md) | [en](./content/incident-response-101/en/03-initial-response.md) | [medium](./content/incident-response-101/medium/03.html) | Draft |
| 4 | Incident Response 101 (4/10): Communication | [ko](./content/incident-response-101/ko/04-communication.md) | [en](./content/incident-response-101/en/04-communication.md) | [medium](./content/incident-response-101/medium/04.html) | Draft |
| 5 | Incident Response 101 (5/10): Timeline 작성 | [ko](./content/incident-response-101/ko/05-timeline.md) | [en](./content/incident-response-101/en/05-timeline.md) | [medium](./content/incident-response-101/medium/05.html) | Draft |
| 6 | Incident Response 101 (6/10): Root Cause Analysis | [ko](./content/incident-response-101/ko/06-root-cause-analysis.md) | [en](./content/incident-response-101/en/06-root-cause-analysis.md) | [medium](./content/incident-response-101/medium/06.html) | Draft |
| 7 | Incident Response 101 (7/10): Mitigation과 Resolution | [ko](./content/incident-response-101/ko/07-mitigation-and-resolution.md) | [en](./content/incident-response-101/en/07-mitigation-and-resolution.md) | [medium](./content/incident-response-101/medium/07.html) | Draft |
| 8 | Incident Response 101 (8/10): Postmortem | [ko](./content/incident-response-101/ko/08-postmortem.md) | [en](./content/incident-response-101/en/08-postmortem.md) | [medium](./content/incident-response-101/medium/08.html) | Draft |
| 9 | Incident Response 101 (9/10): 재발 방지 | [ko](./content/incident-response-101/ko/09-prevention.md) | [en](./content/incident-response-101/en/09-prevention.md) | [medium](./content/incident-response-101/medium/09.html) | Draft |
| 10 | Incident Response 101 (10/10): Incident Runbook 만들기 | [ko](./content/incident-response-101/ko/10-incident-runbook.md) | [en](./content/incident-response-101/en/10-incident-runbook.md) | [medium](./content/incident-response-101/medium/10.html) | Draft |

### SRE 101 (`sre-101`)

신뢰성, SLI/SLO/SLA, 에러 버짓, 인시던트와 포스트모템, toil 감소, 용량 계획까지 다루는 SRE 입문 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/sre-101/`](./content/sre-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | SRE 101 (1/10): SRE란 무엇인가? | [ko](./content/sre-101/ko/01-what-is-sre.md) | [en](./content/sre-101/en/01-what-is-sre.md) | [medium](./content/sre-101/medium/01.html) | Draft |
| 2 | SRE 101 (2/10): Reliability | [ko](./content/sre-101/ko/02-reliability.md) | [en](./content/sre-101/en/02-reliability.md) | [medium](./content/sre-101/medium/02.html) | Draft |
| 3 | SRE 101 (3/10): SLI, SLO, SLA | [ko](./content/sre-101/ko/03-sli-slo-sla.md) | [en](./content/sre-101/en/03-sli-slo-sla.md) | [medium](./content/sre-101/medium/03.html) | Draft |
| 4 | SRE 101 (4/10): Error Budget | [ko](./content/sre-101/ko/04-error-budget.md) | [en](./content/sre-101/en/04-error-budget.md) | [medium](./content/sre-101/medium/04.html) | Draft |
| 5 | SRE 101 (5/10): Monitoring | [ko](./content/sre-101/ko/05-monitoring.md) | [en](./content/sre-101/en/05-monitoring.md) | [medium](./content/sre-101/medium/05.html) | Draft |
| 6 | SRE 101 (6/10): Incident Response | [ko](./content/sre-101/ko/06-incident-response.md) | [en](./content/sre-101/en/06-incident-response.md) | [medium](./content/sre-101/medium/06.html) | Draft |
| 7 | SRE 101 (7/10): Postmortem | [ko](./content/sre-101/ko/07-postmortem.md) | [en](./content/sre-101/en/07-postmortem.md) | [medium](./content/sre-101/medium/07.html) | Draft |
| 8 | SRE 101 (8/10): Toil 줄이기 | [ko](./content/sre-101/ko/08-reducing-toil.md) | [en](./content/sre-101/en/08-reducing-toil.md) | [medium](./content/sre-101/medium/08.html) | Draft |
| 9 | SRE 101 (9/10): Capacity Planning | [ko](./content/sre-101/ko/09-capacity-planning.md) | [en](./content/sre-101/en/09-capacity-planning.md) | [medium](./content/sre-101/medium/09.html) | Draft |
| 10 | SRE 101 (10/10): 운영 가능한 시스템 만들기 | [ko](./content/sre-101/ko/10-building-operable-systems.md) | [en](./content/sre-101/en/10-building-operable-systems.md) | [medium](./content/sre-101/medium/10.html) | Draft |

### Secure Coding 101 (`secure-coding-101`)

입력 검증, 인증, 인가, secret 관리, SQL Injection, XSS/CSRF, dependency 취약점, 안전한 로깅까지 시큐어 코딩 입문 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/secure-coding-101/`](./content/secure-coding-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Secure Coding 101 (1/10): Secure Coding이란 무엇인가? | [ko](./content/secure-coding-101/ko/01-what-is-secure-coding.md) | [en](./content/secure-coding-101/en/01-what-is-secure-coding.md) | [medium](./content/secure-coding-101/medium/01.html) | Draft |
| 2 | Secure Coding 101 (2/10): 입력값 검증 | [ko](./content/secure-coding-101/ko/02-input-validation.md) | [en](./content/secure-coding-101/en/02-input-validation.md) | [medium](./content/secure-coding-101/medium/02.html) | Draft |
| 3 | Secure Coding 101 (3/10): 인증과 세션 | [ko](./content/secure-coding-101/ko/03-authentication-and-session.md) | [en](./content/secure-coding-101/en/03-authentication-and-session.md) | [medium](./content/secure-coding-101/medium/03.html) | Draft |
| 4 | Secure Coding 101 (4/10): 인가와 권한 | [ko](./content/secure-coding-101/ko/04-authorization-and-permissions.md) | [en](./content/secure-coding-101/en/04-authorization-and-permissions.md) | [medium](./content/secure-coding-101/medium/04.html) | Draft |
| 5 | Secure Coding 101 (5/10): 안전한 데이터 저장 | [ko](./content/secure-coding-101/ko/05-safe-data-storage.md) | [en](./content/secure-coding-101/en/05-safe-data-storage.md) | [medium](./content/secure-coding-101/medium/05.html) | Draft |
| 6 | Secure Coding 101 (6/10): Secret과 키 관리 | [ko](./content/secure-coding-101/ko/06-secret-and-key-management.md) | [en](./content/secure-coding-101/en/06-secret-and-key-management.md) | [medium](./content/secure-coding-101/medium/06.html) | Draft |
| 7 | Secure Coding 101 (7/10): SQL Injection과 ORM 안전 사용 | [ko](./content/secure-coding-101/ko/07-sql-injection-and-orm.md) | [en](./content/secure-coding-101/en/07-sql-injection-and-orm.md) | [medium](./content/secure-coding-101/medium/07.html) | Draft |
| 8 | Secure Coding 101 (8/10): XSS와 CSRF 방어 | [ko](./content/secure-coding-101/ko/08-xss-and-csrf.md) | [en](./content/secure-coding-101/en/08-xss-and-csrf.md) | [medium](./content/secure-coding-101/medium/08.html) | Draft |
| 9 | Secure Coding 101 (9/10): Dependency 취약점 관리 | [ko](./content/secure-coding-101/ko/09-dependency-vulnerabilities.md) | [en](./content/secure-coding-101/en/09-dependency-vulnerabilities.md) | [medium](./content/secure-coding-101/medium/09.html) | Draft |
| 10 | Secure Coding 101 (10/10): 안전한 로깅과 감사 | [ko](./content/secure-coding-101/ko/10-safe-logging-and-audit.md) | [en](./content/secure-coding-101/en/10-safe-logging-and-audit.md) | [medium](./content/secure-coding-101/medium/10.html) | Draft |

### 오픈소스 101 / Open Source 101 (`open-source-101`)

라이선스부터 첫 오픈소스 프로젝트까지, 오픈소스 기여의 기본을 다지는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/open-source-101/`](./content/open-source-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Open Source 101 (1/10): 오픈소스란 무엇인가 | [ko](./content/open-source-101/ko/01-what-is-open-source.md) | [en](./content/open-source-101/en/01-what-is-open-source.md) | [medium](./content/open-source-101/medium/01.html) | Draft |
| 2 | Open Source 101 (2/10): 라이선스 이해하기 | [ko](./content/open-source-101/ko/02-understanding-licenses.md) | [en](./content/open-source-101/en/02-understanding-licenses.md) | [medium](./content/open-source-101/medium/02.html) | Draft |
| 3 | Open Source 101 (3/10): 이슈 읽기 | [ko](./content/open-source-101/ko/03-reading-issues.md) | [en](./content/open-source-101/en/03-reading-issues.md) | [medium](./content/open-source-101/medium/03.html) | Draft |
| 4 | Open Source 101 (4/10): 풀 리퀘스트 만들기 | [ko](./content/open-source-101/ko/04-creating-pull-requests.md) | [en](./content/open-source-101/en/04-creating-pull-requests.md) | [medium](./content/open-source-101/medium/04.html) | Draft |
| 5 | Open Source 101 (5/10): 좋은 리드미 문서 | [ko](./content/open-source-101/ko/05-good-readme.md) | [en](./content/open-source-101/en/05-good-readme.md) | [medium](./content/open-source-101/medium/05.html) | Draft |
| 6 | Open Source 101 (6/10): 릴리스와 버전 관리 | [ko](./content/open-source-101/ko/06-release-and-versioning.md) | [en](./content/open-source-101/en/06-release-and-versioning.md) | [medium](./content/open-source-101/medium/06.html) | Draft |
| 7 | Open Source 101 (7/10): 커뮤니티 운영 | [ko](./content/open-source-101/ko/07-community-management.md) | [en](./content/open-source-101/en/07-community-management.md) | [medium](./content/open-source-101/medium/07.html) | Draft |
| 8 | Open Source 101 (8/10): 메인테이너의 역할 | [ko](./content/open-source-101/ko/08-maintainer-role.md) | [en](./content/open-source-101/en/08-maintainer-role.md) | [medium](./content/open-source-101/medium/08.html) | Draft |
| 9 | Open Source 101 (9/10): 오픈소스 포트폴리오 | [ko](./content/open-source-101/ko/09-open-source-portfolio.md) | [en](./content/open-source-101/en/09-open-source-portfolio.md) | [medium](./content/open-source-101/medium/09.html) | Draft |
| 10 | Open Source 101 (10/10): 내 첫 오픈소스 프로젝트 | [ko](./content/open-source-101/ko/10-my-first-open-source-project.md) | [en](./content/open-source-101/en/10-my-first-open-source-project.md) | [medium](./content/open-source-101/medium/10.html) | Draft |

### Developer Career 101 (`developer-career-101`)

개발자 커리어를 설계하는 법.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/developer-career-101/`](./content/developer-career-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Developer Career 101 (1/10): 개발자 커리어란 무엇인가 | [ko](./content/developer-career-101/ko/01-what-is-developer-career.md) | [en](./content/developer-career-101/en/01-what-is-developer-career.md) | [medium](./content/developer-career-101/medium/01.html) | Draft |
| 2 | Developer Career 101 (2/10): 직무 이해하기 | [ko](./content/developer-career-101/ko/02-understanding-roles.md) | [en](./content/developer-career-101/en/02-understanding-roles.md) | [medium](./content/developer-career-101/medium/02.html) | Draft |
| 3 | Developer Career 101 (3/10): 학습 계획 세우기 | [ko](./content/developer-career-101/ko/03-learning-plan.md) | [en](./content/developer-career-101/en/03-learning-plan.md) | [medium](./content/developer-career-101/medium/03.html) | Draft |
| 4 | Developer Career 101 (4/10): 이력서와 포트폴리오 | [ko](./content/developer-career-101/ko/04-resume-and-portfolio.md) | [en](./content/developer-career-101/en/04-resume-and-portfolio.md) | [medium](./content/developer-career-101/medium/04.html) | Draft |
| 5 | Developer Career 101 (5/10): 코딩 인터뷰 준비 | [ko](./content/developer-career-101/ko/05-coding-interview.md) | [en](./content/developer-career-101/en/05-coding-interview.md) | [medium](./content/developer-career-101/medium/05.html) | Draft |
| 6 | Developer Career 101 (6/10): 시스템 디자인 인터뷰 | [ko](./content/developer-career-101/ko/06-system-design-interview.md) | [en](./content/developer-career-101/en/06-system-design-interview.md) | [medium](./content/developer-career-101/medium/06.html) | Draft |
| 7 | Developer Career 101 (7/10): 첫 직장 적응 | [ko](./content/developer-career-101/ko/07-first-job.md) | [en](./content/developer-career-101/en/07-first-job.md) | [medium](./content/developer-career-101/medium/07.html) | Draft |
| 8 | Developer Career 101 (8/10): 사이드 프로젝트와 학습 | [ko](./content/developer-career-101/ko/08-side-projects.md) | [en](./content/developer-career-101/en/08-side-projects.md) | [medium](./content/developer-career-101/medium/08.html) | Draft |
| 9 | Developer Career 101 (9/10): 멘토링과 네트워킹 | [ko](./content/developer-career-101/ko/09-mentoring-networking.md) | [en](./content/developer-career-101/en/09-mentoring-networking.md) | [medium](./content/developer-career-101/medium/09.html) | Draft |
| 10 | Developer Career 101 (10/10): 시니어로 가는 길 | [ko](./content/developer-career-101/ko/10-path-to-senior.md) | [en](./content/developer-career-101/en/10-path-to-senior.md) | [medium](./content/developer-career-101/medium/10.html) | Draft |

### Data Science Career 101 (`data-science-career-101`)

데이터 직무 커리어를 설계하는 법.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/data-science-career-101/`](./content/data-science-career-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Data Science Career 101 (1/10): 데이터 직무란 무엇인가 | [ko](./content/data-science-career-101/ko/01-what-is-data-career.md) | [en](./content/data-science-career-101/en/01-what-is-data-career.md) | [medium](./content/data-science-career-101/medium/01.html) | Draft |
| 2 | Data Science Career 101 (2/10): 분석가 vs 사이언티스트 vs 엔지니어 | [ko](./content/data-science-career-101/ko/02-analyst-scientist-engineer.md) | [en](./content/data-science-career-101/en/02-analyst-scientist-engineer.md) | [medium](./content/data-science-career-101/medium/02.html) | Draft |
| 3 | Data Science Career 101 (3/10): 학습 경로 설계 | [ko](./content/data-science-career-101/ko/03-learning-path.md) | [en](./content/data-science-career-101/en/03-learning-path.md) | [medium](./content/data-science-career-101/medium/03.html) | Draft |
| 4 | Data Science Career 101 (4/10): 데이터 포트폴리오 | [ko](./content/data-science-career-101/ko/04-data-portfolio.md) | [en](./content/data-science-career-101/en/04-data-portfolio.md) | [medium](./content/data-science-career-101/medium/04.html) | Draft |
| 5 | Data Science Career 101 (5/10): SQL과 분석 인터뷰 | [ko](./content/data-science-career-101/ko/05-sql-and-analytics-interview.md) | [en](./content/data-science-career-101/en/05-sql-and-analytics-interview.md) | [medium](./content/data-science-career-101/medium/05.html) | Draft |
| 6 | Data Science Career 101 (6/10): ML 인터뷰 | [ko](./content/data-science-career-101/ko/06-ml-interview.md) | [en](./content/data-science-career-101/en/06-ml-interview.md) | [medium](./content/data-science-career-101/medium/06.html) | Draft |
| 7 | Data Science Career 101 (7/10): 케이스 인터뷰 | [ko](./content/data-science-career-101/ko/07-case-interview.md) | [en](./content/data-science-career-101/en/07-case-interview.md) | [medium](./content/data-science-career-101/medium/07.html) | Draft |
| 8 | Data Science Career 101 (8/10): 첫 직장 적응 | [ko](./content/data-science-career-101/ko/08-first-job.md) | [en](./content/data-science-career-101/en/08-first-job.md) | [medium](./content/data-science-career-101/medium/08.html) | Draft |
| 9 | Data Science Career 101 (9/10): 도메인 전문성 쌓기 | [ko](./content/data-science-career-101/ko/09-domain-expertise.md) | [en](./content/data-science-career-101/en/09-domain-expertise.md) | [medium](./content/data-science-career-101/medium/09.html) | Draft |
| 10 | Data Science Career 101 (10/10): 시니어 데이터 직무로 가는 길 | [ko](./content/data-science-career-101/ko/10-path-to-senior.md) | [en](./content/data-science-career-101/en/10-path-to-senior.md) | [medium](./content/data-science-career-101/medium/10.html) | Draft |

### 포트폴리오 프로젝트 101 / Portfolio Project 101 (`portfolio-project-101`)

프로젝트 선정, README, 데모, 배포, 테스트, 의사결정 기록, 블로그, 면접 설명까지 다루는 입문 포트폴리오 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/portfolio-project-101/`](./content/portfolio-project-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Portfolio Project 101 (1/10): 포트폴리오 프로젝트란 무엇인가 | [ko](./content/portfolio-project-101/ko/01-what-is-a-portfolio-project.md) | [en](./content/portfolio-project-101/en/01-what-is-a-portfolio-project.md) | [medium](./content/portfolio-project-101/medium/01.html) | Draft |
| 2 | Portfolio Project 101 (2/10): 좋은 프로젝트의 조건 | [ko](./content/portfolio-project-101/ko/02-traits-of-a-good-project.md) | [en](./content/portfolio-project-101/en/02-traits-of-a-good-project.md) | [medium](./content/portfolio-project-101/medium/02.html) | Draft |
| 3 | Portfolio Project 101 (3/10): README 작성 | [ko](./content/portfolio-project-101/ko/03-writing-the-readme.md) | [en](./content/portfolio-project-101/en/03-writing-the-readme.md) | [medium](./content/portfolio-project-101/medium/03.html) | Draft |
| 4 | Portfolio Project 101 (4/10): 데모 만들기 | [ko](./content/portfolio-project-101/ko/04-building-the-demo.md) | [en](./content/portfolio-project-101/en/04-building-the-demo.md) | [medium](./content/portfolio-project-101/medium/04.html) | Draft |
| 5 | Portfolio Project 101 (5/10): 배포하기 | [ko](./content/portfolio-project-101/ko/05-deploying-the-project.md) | [en](./content/portfolio-project-101/en/05-deploying-the-project.md) | [medium](./content/portfolio-project-101/medium/05.html) | Draft |
| 6 | Portfolio Project 101 (6/10): 테스트와 문서화 | [ko](./content/portfolio-project-101/ko/06-tests-and-documentation.md) | [en](./content/portfolio-project-101/en/06-tests-and-documentation.md) | [medium](./content/portfolio-project-101/medium/06.html) | Draft |
| 7 | Portfolio Project 101 (7/10): 기술적 의사결정 기록 | [ko](./content/portfolio-project-101/ko/07-recording-tech-decisions.md) | [en](./content/portfolio-project-101/en/07-recording-tech-decisions.md) | [medium](./content/portfolio-project-101/medium/07.html) | Draft |
| 8 | Portfolio Project 101 (8/10): 블로그 글로 정리하기 | [ko](./content/portfolio-project-101/ko/08-summarizing-as-blog-posts.md) | [en](./content/portfolio-project-101/en/08-summarizing-as-blog-posts.md) | [medium](./content/portfolio-project-101/medium/08.html) | Draft |
| 9 | Portfolio Project 101 (9/10): 면접에서 설명하기 | [ko](./content/portfolio-project-101/ko/09-explaining-in-interviews.md) | [en](./content/portfolio-project-101/en/09-explaining-in-interviews.md) | [medium](./content/portfolio-project-101/medium/09.html) | Draft |
| 10 | Portfolio Project 101 (10/10): 포트폴리오 개선 체크리스트 | [ko](./content/portfolio-project-101/ko/10-portfolio-improvement-checklist.md) | [en](./content/portfolio-project-101/en/10-portfolio-improvement-checklist.md) | [medium](./content/portfolio-project-101/medium/10.html) | Draft |

### 캡스톤 프로젝트 101 / Capstone Project 101 (`capstone-project-101`)

주제 선정, 문제 정의, MVP, 팀 역할, 발표, 회고까지 캡스톤 전체 흐름을 다룬 입문 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/capstone-project-101/`](./content/capstone-project-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Capstone Project 101 (1/10): 캡스톤 프로젝트란 무엇인가 | [ko](./content/capstone-project-101/ko/01-what-is-capstone.md) | [en](./content/capstone-project-101/en/01-what-is-capstone.md) | [medium](./content/capstone-project-101/medium/01.html) | Draft |
| 2 | Capstone Project 101 (2/10): 주제 선정 | [ko](./content/capstone-project-101/ko/02-choosing-a-topic.md) | [en](./content/capstone-project-101/en/02-choosing-a-topic.md) | [medium](./content/capstone-project-101/medium/02.html) | Draft |
| 3 | Capstone Project 101 (3/10): 문제 정의 | [ko](./content/capstone-project-101/ko/03-defining-the-problem.md) | [en](./content/capstone-project-101/en/03-defining-the-problem.md) | [medium](./content/capstone-project-101/medium/03.html) | Draft |
| 4 | Capstone Project 101 (4/10): 요구사항 정리 | [ko](./content/capstone-project-101/ko/04-organizing-requirements.md) | [en](./content/capstone-project-101/en/04-organizing-requirements.md) | [medium](./content/capstone-project-101/medium/04.html) | Draft |
| 5 | Capstone Project 101 (5/10): 팀 역할 나누기 | [ko](./content/capstone-project-101/ko/05-splitting-team-roles.md) | [en](./content/capstone-project-101/en/05-splitting-team-roles.md) | [medium](./content/capstone-project-101/medium/05.html) | Draft |
| 6 | Capstone Project 101 (6/10): MVP 설계 | [ko](./content/capstone-project-101/ko/06-designing-the-mvp.md) | [en](./content/capstone-project-101/en/06-designing-the-mvp.md) | [medium](./content/capstone-project-101/medium/06.html) | Draft |
| 7 | Capstone Project 101 (7/10): 기술 스택 선택 | [ko](./content/capstone-project-101/ko/07-choosing-the-tech-stack.md) | [en](./content/capstone-project-101/en/07-choosing-the-tech-stack.md) | [medium](./content/capstone-project-101/medium/07.html) | Draft |
| 8 | Capstone Project 101 (8/10): 일정 관리 | [ko](./content/capstone-project-101/ko/08-schedule-management.md) | [en](./content/capstone-project-101/en/08-schedule-management.md) | [medium](./content/capstone-project-101/medium/08.html) | Draft |
| 9 | Capstone Project 101 (9/10): 발표 자료 만들기 | [ko](./content/capstone-project-101/ko/09-presentation-materials.md) | [en](./content/capstone-project-101/en/09-presentation-materials.md) | [medium](./content/capstone-project-101/medium/09.html) | Draft |
| 10 | Capstone Project 101 (10/10): 프로젝트 회고 | [ko](./content/capstone-project-101/ko/10-project-retrospective.md) | [en](./content/capstone-project-101/en/10-project-retrospective.md) | [medium](./content/capstone-project-101/medium/10.html) | Draft |

### 기술 글쓰기 101 / Technical Writing 101 (`technical-writing-101`)

독자 정의부터 발행 전 체크리스트까지, 기술 글쓰기의 기본을 다지는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/technical-writing-101/`](./content/technical-writing-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Technical Writing 101 (1/10): 기술 글쓰기란 무엇인가 | [ko](./content/technical-writing-101/ko/01-what-is-technical-writing.md) | [en](./content/technical-writing-101/en/01-what-is-technical-writing.md) | [medium](./content/technical-writing-101/medium/01.html) | Draft |
| 2 | Technical Writing 101 (2/10): 독자 정의하기 | [ko](./content/technical-writing-101/ko/02-defining-the-reader.md) | [en](./content/technical-writing-101/en/02-defining-the-reader.md) | [medium](./content/technical-writing-101/medium/02.html) | Draft |
| 3 | Technical Writing 101 (3/10): 제목과 구조 잡기 | [ko](./content/technical-writing-101/ko/03-title-and-structure.md) | [en](./content/technical-writing-101/en/03-title-and-structure.md) | [medium](./content/technical-writing-101/medium/03.html) | Draft |
| 4 | Technical Writing 101 (4/10): 개념 설명하기 | [ko](./content/technical-writing-101/ko/04-explaining-concepts.md) | [en](./content/technical-writing-101/en/04-explaining-concepts.md) | [medium](./content/technical-writing-101/medium/04.html) | Draft |
| 5 | Technical Writing 101 (5/10): 예제 코드 설명하기 | [ko](./content/technical-writing-101/ko/05-explaining-example-code.md) | [en](./content/technical-writing-101/en/05-explaining-example-code.md) | [medium](./content/technical-writing-101/medium/05.html) | Draft |
| 6 | Technical Writing 101 (6/10): 그림과 표 사용하기 | [ko](./content/technical-writing-101/ko/06-using-figures-and-tables.md) | [en](./content/technical-writing-101/en/06-using-figures-and-tables.md) | [medium](./content/technical-writing-101/medium/06.html) | Draft |
| 7 | Technical Writing 101 (7/10): README 작성하기 | [ko](./content/technical-writing-101/ko/07-writing-the-readme.md) | [en](./content/technical-writing-101/en/07-writing-the-readme.md) | [medium](./content/technical-writing-101/medium/07.html) | Draft |
| 8 | Technical Writing 101 (8/10): 튜토리얼 작성하기 | [ko](./content/technical-writing-101/ko/08-writing-tutorials.md) | [en](./content/technical-writing-101/en/08-writing-tutorials.md) | [medium](./content/technical-writing-101/medium/08.html) | Draft |
| 9 | Technical Writing 101 (9/10): 블로그와 문서 차이 | [ko](./content/technical-writing-101/ko/09-blog-vs-docs.md) | [en](./content/technical-writing-101/en/09-blog-vs-docs.md) | [medium](./content/technical-writing-101/medium/09.html) | Draft |
| 10 | Technical Writing 101 (10/10): 발행 전 체크리스트 | [ko](./content/technical-writing-101/ko/10-pre-publish-checklist.md) | [en](./content/technical-writing-101/en/10-pre-publish-checklist.md) | [medium](./content/technical-writing-101/medium/10.html) | Draft |

---

## 데이터

### Statistics 101 (`statistics-101`)

기술 통계, 분포, 추정, 신뢰구간, 가설검정, 회귀까지 데이터 분석에 필요한 통계의 큰 그림을 다지는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/statistics-101/`](./content/statistics-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Statistics 101 (1/10): 통계란 무엇인가? | [ko](./content/statistics-101/ko/01-what-is-statistics.md) | [en](./content/statistics-101/en/01-what-is-statistics.md) | [medium](./content/statistics-101/medium/01.html) | Draft |
| 2 | Statistics 101 (2/10): 평균, 중앙값, 분산 | [ko](./content/statistics-101/ko/02-mean-median-variance.md) | [en](./content/statistics-101/en/02-mean-median-variance.md) | [medium](./content/statistics-101/medium/02.html) | Draft |
| 3 | Statistics 101 (3/10): 분포 | [ko](./content/statistics-101/ko/03-distributions.md) | [en](./content/statistics-101/en/03-distributions.md) | [medium](./content/statistics-101/medium/03.html) | Draft |
| 4 | Statistics 101 (4/10): 표본과 모집단 | [ko](./content/statistics-101/ko/04-sample-and-population.md) | [en](./content/statistics-101/en/04-sample-and-population.md) | [medium](./content/statistics-101/medium/04.html) | Draft |
| 5 | Statistics 101 (5/10): 추정 | [ko](./content/statistics-101/ko/05-estimation.md) | [en](./content/statistics-101/en/05-estimation.md) | [medium](./content/statistics-101/medium/05.html) | Draft |
| 6 | Statistics 101 (6/10): 신뢰구간 | [ko](./content/statistics-101/ko/06-confidence-interval.md) | [en](./content/statistics-101/en/06-confidence-interval.md) | [medium](./content/statistics-101/medium/06.html) | Draft |
| 7 | Statistics 101 (7/10): 가설검정 | [ko](./content/statistics-101/ko/07-hypothesis-testing.md) | [en](./content/statistics-101/en/07-hypothesis-testing.md) | [medium](./content/statistics-101/medium/07.html) | Draft |
| 8 | Statistics 101 (8/10): 상관과 회귀 | [ko](./content/statistics-101/ko/08-correlation-and-regression.md) | [en](./content/statistics-101/en/08-correlation-and-regression.md) | [medium](./content/statistics-101/medium/08.html) | Draft |
| 9 | Statistics 101 (9/10): p-value 이해하기 | [ko](./content/statistics-101/ko/09-understanding-p-value.md) | [en](./content/statistics-101/en/09-understanding-p-value.md) | [medium](./content/statistics-101/medium/09.html) | Draft |
| 10 | Statistics 101 (10/10): 통계적 사고방식 | [ko](./content/statistics-101/ko/10-statistical-thinking.md) | [en](./content/statistics-101/en/10-statistical-thinking.md) | [medium](./content/statistics-101/medium/10.html) | Draft |

### Probability 101 (`probability-101`)

사건, 조건부확률, 베이즈 정리, 확률변수, 분포, 중심극한정리까지 ML 기초로 이어지는 확률을 다지는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/probability-101/`](./content/probability-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Probability 101 (1/10): 확률이란 무엇인가? | [ko](./content/probability-101/ko/01-what-is-probability.md) | [en](./content/probability-101/en/01-what-is-probability.md) | [medium](./content/probability-101/medium/01.html) | Draft |
| 2 | Probability 101 (2/10): 사건과 표본공간 | [ko](./content/probability-101/ko/02-events-and-sample-space.md) | [en](./content/probability-101/en/02-events-and-sample-space.md) | [medium](./content/probability-101/medium/02.html) | Draft |
| 3 | Probability 101 (3/10): 조건부확률 | [ko](./content/probability-101/ko/03-conditional-probability.md) | [en](./content/probability-101/en/03-conditional-probability.md) | [medium](./content/probability-101/medium/03.html) | Draft |
| 4 | Probability 101 (4/10): 베이즈 정리 | [ko](./content/probability-101/ko/04-bayes-theorem.md) | [en](./content/probability-101/en/04-bayes-theorem.md) | [medium](./content/probability-101/medium/04.html) | Draft |
| 5 | Probability 101 (5/10): 확률변수 | [ko](./content/probability-101/ko/05-random-variables.md) | [en](./content/probability-101/en/05-random-variables.md) | [medium](./content/probability-101/medium/05.html) | Draft |
| 6 | Probability 101 (6/10): 기대값과 분산 | [ko](./content/probability-101/ko/06-expectation-and-variance.md) | [en](./content/probability-101/en/06-expectation-and-variance.md) | [medium](./content/probability-101/medium/06.html) | Draft |
| 7 | Probability 101 (7/10): 이산분포 | [ko](./content/probability-101/ko/07-discrete-distributions.md) | [en](./content/probability-101/en/07-discrete-distributions.md) | [medium](./content/probability-101/medium/07.html) | Draft |
| 8 | Probability 101 (8/10): 연속분포 | [ko](./content/probability-101/ko/08-continuous-distributions.md) | [en](./content/probability-101/en/08-continuous-distributions.md) | [medium](./content/probability-101/medium/08.html) | Draft |
| 9 | Probability 101 (9/10): 대수의 법칙과 중심극한정리 | [ko](./content/probability-101/ko/09-lln-and-clt.md) | [en](./content/probability-101/en/09-lln-and-clt.md) | [medium](./content/probability-101/medium/09.html) | Draft |
| 10 | Probability 101 (10/10): 머신러닝에서의 확률 | [ko](./content/probability-101/ko/10-probability-in-ml.md) | [en](./content/probability-101/en/10-probability-in-ml.md) | [medium](./content/probability-101/medium/10.html) | Draft |

### Linear Algebra 101 (`linear-algebra-101`)

벡터, 행렬, 내적, 선형변환, 기저, 고유값, 행렬분해, PCA까지 ML 입문 직전 단계의 선형대수를 다지는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/linear-algebra-101/`](./content/linear-algebra-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Linear Algebra 101 (1/10): 선형대수란 무엇인가? | [ko](./content/linear-algebra-101/ko/01-what-is-linear-algebra.md) | [en](./content/linear-algebra-101/en/01-what-is-linear-algebra.md) | [medium](./content/linear-algebra-101/medium/01.html) | Draft |
| 2 | Linear Algebra 101 (2/10): 벡터 | [ko](./content/linear-algebra-101/ko/02-vectors.md) | [en](./content/linear-algebra-101/en/02-vectors.md) | [medium](./content/linear-algebra-101/medium/02.html) | Draft |
| 3 | Linear Algebra 101 (3/10): 행렬 | [ko](./content/linear-algebra-101/ko/03-matrices.md) | [en](./content/linear-algebra-101/en/03-matrices.md) | [medium](./content/linear-algebra-101/medium/03.html) | Draft |
| 4 | Linear Algebra 101 (4/10): 내적과 거리 | [ko](./content/linear-algebra-101/ko/04-inner-product-and-distance.md) | [en](./content/linear-algebra-101/en/04-inner-product-and-distance.md) | [medium](./content/linear-algebra-101/medium/04.html) | Draft |
| 5 | Linear Algebra 101 (5/10): 선형변환 | [ko](./content/linear-algebra-101/ko/05-linear-transformation.md) | [en](./content/linear-algebra-101/en/05-linear-transformation.md) | [medium](./content/linear-algebra-101/medium/05.html) | Draft |
| 6 | Linear Algebra 101 (6/10): 기저와 차원 | [ko](./content/linear-algebra-101/ko/06-basis-and-dimension.md) | [en](./content/linear-algebra-101/en/06-basis-and-dimension.md) | [medium](./content/linear-algebra-101/medium/06.html) | Draft |
| 7 | Linear Algebra 101 (7/10): 고유값과 고유벡터 | [ko](./content/linear-algebra-101/ko/07-eigenvalues-and-eigenvectors.md) | [en](./content/linear-algebra-101/en/07-eigenvalues-and-eigenvectors.md) | [medium](./content/linear-algebra-101/medium/07.html) | Draft |
| 8 | Linear Algebra 101 (8/10): 행렬 분해 | [ko](./content/linear-algebra-101/ko/08-matrix-decomposition.md) | [en](./content/linear-algebra-101/en/08-matrix-decomposition.md) | [medium](./content/linear-algebra-101/medium/08.html) | Draft |
| 9 | Linear Algebra 101 (9/10): PCA | [ko](./content/linear-algebra-101/ko/09-pca.md) | [en](./content/linear-algebra-101/en/09-pca.md) | [medium](./content/linear-algebra-101/medium/09.html) | Draft |
| 10 | Linear Algebra 101 (10/10): 머신러닝에서의 선형대수 | [ko](./content/linear-algebra-101/ko/10-linear-algebra-in-ml.md) | [en](./content/linear-algebra-101/en/10-linear-algebra-in-ml.md) | [medium](./content/linear-algebra-101/medium/10.html) | Draft |

### Data Science 101 (`data-science-101`)

문제 정의, 데이터 수집, 정제, EDA, 시각화, 모델링, 평가, 해석까지 데이터 사이언스 전체 흐름을 다지는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/data-science-101/`](./content/data-science-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Data Science 101 (1/10): Data Science란 무엇인가? | [ko](./content/data-science-101/ko/01-what-is-data-science.md) | [en](./content/data-science-101/en/01-what-is-data-science.md) | [medium](./content/data-science-101/medium/01.html) | Draft |
| 2 | Data Science 101 (2/10): 문제를 데이터 문제로 바꾸기 | [ko](./content/data-science-101/ko/02-problem-to-data-problem.md) | [en](./content/data-science-101/en/02-problem-to-data-problem.md) | [medium](./content/data-science-101/medium/02.html) | Draft |
| 3 | Data Science 101 (3/10): 데이터 수집 | [ko](./content/data-science-101/ko/03-data-collection.md) | [en](./content/data-science-101/en/03-data-collection.md) | [medium](./content/data-science-101/medium/03.html) | Draft |
| 4 | Data Science 101 (4/10): 데이터 정제 | [ko](./content/data-science-101/ko/04-data-cleaning.md) | [en](./content/data-science-101/en/04-data-cleaning.md) | [medium](./content/data-science-101/medium/04.html) | Draft |
| 5 | Data Science 101 (5/10): 탐색적 데이터 분석 | [ko](./content/data-science-101/ko/05-exploratory-data-analysis.md) | [en](./content/data-science-101/en/05-exploratory-data-analysis.md) | [medium](./content/data-science-101/medium/05.html) | Draft |
| 6 | Data Science 101 (6/10): 시각화 | [ko](./content/data-science-101/ko/06-visualization.md) | [en](./content/data-science-101/en/06-visualization.md) | [medium](./content/data-science-101/medium/06.html) | Draft |
| 7 | Data Science 101 (7/10): 모델링 | [ko](./content/data-science-101/ko/07-modeling.md) | [en](./content/data-science-101/en/07-modeling.md) | [medium](./content/data-science-101/medium/07.html) | Draft |
| 8 | Data Science 101 (8/10): 평가 | [ko](./content/data-science-101/ko/08-evaluation.md) | [en](./content/data-science-101/en/08-evaluation.md) | [medium](./content/data-science-101/medium/08.html) | Draft |
| 9 | Data Science 101 (9/10): 결과 해석 | [ko](./content/data-science-101/ko/09-result-interpretation.md) | [en](./content/data-science-101/en/09-result-interpretation.md) | [medium](./content/data-science-101/medium/09.html) | Draft |
| 10 | Data Science 101 (10/10): 데이터 프로젝트 전체 흐름 | [ko](./content/data-science-101/ko/10-data-project-end-to-end.md) | [en](./content/data-science-101/en/10-data-project-end-to-end.md) | [medium](./content/data-science-101/medium/10.html) | Draft |

### SQL 101 (`sql-101`)

SELECT, JOIN, GROUP BY, subquery, window function, DML, index 기초까지 분석/개발에 바로 쓰는 SQL 입문 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/sql-101/`](./content/sql-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | SQL 101 (1/10): SQL이란 무엇인가? | [ko](./content/sql-101/ko/01-what-is-sql.md) | [en](./content/sql-101/en/01-what-is-sql.md) | [medium](./content/sql-101/medium/01.html) | Draft |
| 2 | SQL 101 (2/10): SELECT 기본 | [ko](./content/sql-101/ko/02-select-basics.md) | [en](./content/sql-101/en/02-select-basics.md) | [medium](./content/sql-101/medium/02.html) | Draft |
| 3 | SQL 101 (3/10): WHERE와 조건 | [ko](./content/sql-101/ko/03-where-and-conditions.md) | [en](./content/sql-101/en/03-where-and-conditions.md) | [medium](./content/sql-101/medium/03.html) | Draft |
| 4 | SQL 101 (4/10): JOIN 이해하기 | [ko](./content/sql-101/ko/04-join.md) | [en](./content/sql-101/en/04-join.md) | [medium](./content/sql-101/medium/04.html) | Draft |
| 5 | SQL 101 (5/10): GROUP BY와 집계 함수 | [ko](./content/sql-101/ko/05-group-by-and-aggregate.md) | [en](./content/sql-101/en/05-group-by-and-aggregate.md) | [medium](./content/sql-101/medium/05.html) | Draft |
| 6 | SQL 101 (6/10): 서브쿼리와 CTE | [ko](./content/sql-101/ko/06-subquery.md) | [en](./content/sql-101/en/06-subquery.md) | [medium](./content/sql-101/medium/06.html) | Draft |
| 7 | SQL 101 (7/10): 윈도 함수 | [ko](./content/sql-101/ko/07-window-function.md) | [en](./content/sql-101/en/07-window-function.md) | [medium](./content/sql-101/medium/07.html) | Draft |
| 8 | SQL 101 (8/10): 데이터를 바꾸는 SQL — INSERT, UPDATE, DELETE | [ko](./content/sql-101/ko/08-insert-update-delete.md) | [en](./content/sql-101/en/08-insert-update-delete.md) | [medium](./content/sql-101/medium/08.html) | Draft |
| 9 | SQL 101 (9/10): 인덱스와 쿼리 계획 | [ko](./content/sql-101/ko/09-index-and-query-plan.md) | [en](./content/sql-101/en/09-index-and-query-plan.md) | [medium](./content/sql-101/medium/09.html) | Draft |
| 10 | SQL 101 (10/10): 실전 분석 SQL | [ko](./content/sql-101/ko/10-practical-analysis-sql.md) | [en](./content/sql-101/en/10-practical-analysis-sql.md) | [medium](./content/sql-101/medium/10.html) | Draft |

### Pandas 101 (`pandas-101`)

Series, DataFrame, 파일 입출력, filtering, missing value, groupby, merge, time series, vectorization까지 다루는 Pandas 입문 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/pandas-101/`](./content/pandas-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Pandas 101 (1/10): Pandas란 무엇인가? | [ko](./content/pandas-101/ko/01-what-is-pandas.md) | [en](./content/pandas-101/en/01-what-is-pandas.md) | [medium](./content/pandas-101/medium/01.html) | Draft |
| 2 | Pandas 101 (2/10): 시리즈와 데이터프레임 | [ko](./content/pandas-101/ko/02-series-and-dataframe.md) | [en](./content/pandas-101/en/02-series-and-dataframe.md) | [medium](./content/pandas-101/medium/02.html) | Draft |
| 3 | Pandas 101 (3/10): CSV와 Excel 읽기 | [ko](./content/pandas-101/ko/03-read-csv-and-excel.md) | [en](./content/pandas-101/en/03-read-csv-and-excel.md) | [medium](./content/pandas-101/medium/03.html) | Draft |
| 4 | Pandas 101 (4/10): 필터링과 선택 | [ko](./content/pandas-101/ko/04-filtering-and-selection.md) | [en](./content/pandas-101/en/04-filtering-and-selection.md) | [medium](./content/pandas-101/medium/04.html) | Draft |
| 5 | Pandas 101 (5/10): 결측치 처리 | [ko](./content/pandas-101/ko/05-missing-values.md) | [en](./content/pandas-101/en/05-missing-values.md) | [medium](./content/pandas-101/medium/05.html) | Draft |
| 6 | Pandas 101 (6/10): 그룹화와 집계 | [ko](./content/pandas-101/ko/06-groupby.md) | [en](./content/pandas-101/en/06-groupby.md) | [medium](./content/pandas-101/medium/06.html) | Draft |
| 7 | Pandas 101 (7/10): 병합과 조인 | [ko](./content/pandas-101/ko/07-merge-and-join.md) | [en](./content/pandas-101/en/07-merge-and-join.md) | [medium](./content/pandas-101/medium/07.html) | Draft |
| 8 | Pandas 101 (8/10): 시계열 데이터 다루기 | [ko](./content/pandas-101/ko/08-time-series.md) | [en](./content/pandas-101/en/08-time-series.md) | [medium](./content/pandas-101/medium/08.html) | Draft |
| 9 | Pandas 101 (9/10): 적용 함수와 벡터화 | [ko](./content/pandas-101/ko/09-apply-and-vectorization.md) | [en](./content/pandas-101/en/09-apply-and-vectorization.md) | [medium](./content/pandas-101/medium/09.html) | Draft |
| 10 | Pandas 101 (10/10): 실전 데이터 분석 | [ko](./content/pandas-101/ko/10-real-world-data-analysis.md) | [en](./content/pandas-101/en/10-real-world-data-analysis.md) | [medium](./content/pandas-101/medium/10.html) | Draft |

### Machine Learning 101 (`machine-learning-101`)

지도/비지도, train/test, 회귀, 분류, 트리, 군집, regularization, 평가까지 ML 전체 흐름을 다지는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/machine-learning-101/`](./content/machine-learning-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Machine Learning 101 (1/10): Machine Learning이란 무엇인가? | [ko](./content/machine-learning-101/ko/01-what-is-machine-learning.md) | [en](./content/machine-learning-101/en/01-what-is-machine-learning.md) | [medium](./content/machine-learning-101/medium/01.html) | Draft |
| 2 | Machine Learning 101 (2/10): 지도학습과 비지도학습 | [ko](./content/machine-learning-101/ko/02-supervised-and-unsupervised.md) | [en](./content/machine-learning-101/en/02-supervised-and-unsupervised.md) | [medium](./content/machine-learning-101/medium/02.html) | Draft |
| 3 | Machine Learning 101 (3/10): Train/Test Split | [ko](./content/machine-learning-101/ko/03-train-test-split.md) | [en](./content/machine-learning-101/en/03-train-test-split.md) | [medium](./content/machine-learning-101/medium/03.html) | Draft |
| 4 | Machine Learning 101 (4/10): Linear Regression | [ko](./content/machine-learning-101/ko/04-linear-regression.md) | [en](./content/machine-learning-101/en/04-linear-regression.md) | [medium](./content/machine-learning-101/medium/04.html) | Draft |
| 5 | Machine Learning 101 (5/10): Logistic Regression | [ko](./content/machine-learning-101/ko/05-logistic-regression.md) | [en](./content/machine-learning-101/en/05-logistic-regression.md) | [medium](./content/machine-learning-101/medium/05.html) | Draft |
| 6 | Machine Learning 101 (6/10): Decision Tree와 Random Forest | [ko](./content/machine-learning-101/ko/06-decision-tree-and-random-forest.md) | [en](./content/machine-learning-101/en/06-decision-tree-and-random-forest.md) | [medium](./content/machine-learning-101/medium/06.html) | Draft |
| 7 | Machine Learning 101 (7/10): Clustering | [ko](./content/machine-learning-101/ko/07-clustering.md) | [en](./content/machine-learning-101/en/07-clustering.md) | [medium](./content/machine-learning-101/medium/07.html) | Draft |
| 8 | Machine Learning 101 (8/10): Overfitting과 Regularization | [ko](./content/machine-learning-101/ko/08-overfitting-and-regularization.md) | [en](./content/machine-learning-101/en/08-overfitting-and-regularization.md) | [medium](./content/machine-learning-101/medium/08.html) | Draft |
| 9 | Machine Learning 101 (9/10): Model Evaluation | [ko](./content/machine-learning-101/ko/09-model-evaluation.md) | [en](./content/machine-learning-101/en/09-model-evaluation.md) | [medium](./content/machine-learning-101/medium/09.html) | Draft |
| 10 | Machine Learning 101 (10/10): ML 프로젝트 전체 흐름 | [ko](./content/machine-learning-101/ko/10-ml-project-workflow.md) | [en](./content/machine-learning-101/en/10-ml-project-workflow.md) | [medium](./content/machine-learning-101/medium/10.html) | Draft |

### Model Evaluation 101 (`model-evaluation-101`)

모델을 제대로 평가하는 법 — train/val/test, precision/recall, ROC, calibration, error analysis까지.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/model-evaluation-101/`](./content/model-evaluation-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Model Evaluation 101 (1/10): 모델 평가는 왜 어려운가? | [ko](./content/model-evaluation-101/ko/01-why-evaluation-is-hard.md) | [en](./content/model-evaluation-101/en/01-why-evaluation-is-hard.md) | [medium](./content/model-evaluation-101/medium/01.html) | Draft |
| 2 | Model Evaluation 101 (2/10): 훈련·검증·테스트 데이터 나누기 | [ko](./content/model-evaluation-101/ko/02-train-val-test.md) | [en](./content/model-evaluation-101/en/02-train-val-test.md) | [medium](./content/model-evaluation-101/medium/02.html) | Draft |
| 3 | Model Evaluation 101 (3/10): 정확도의 한계 | [ko](./content/model-evaluation-101/ko/03-limits-of-accuracy.md) | [en](./content/model-evaluation-101/en/03-limits-of-accuracy.md) | [medium](./content/model-evaluation-101/medium/03.html) | Draft |
| 4 | Model Evaluation 101 (4/10): 정밀도와 재현율 | [ko](./content/model-evaluation-101/ko/04-precision-and-recall.md) | [en](./content/model-evaluation-101/en/04-precision-and-recall.md) | [medium](./content/model-evaluation-101/medium/04.html) | Draft |
| 5 | Model Evaluation 101 (5/10): F1 점수 | [ko](./content/model-evaluation-101/ko/05-f1-score.md) | [en](./content/model-evaluation-101/en/05-f1-score.md) | [medium](./content/model-evaluation-101/medium/05.html) | Draft |
| 6 | Model Evaluation 101 (6/10): ROC와 AUC 이해하기 | [ko](./content/model-evaluation-101/ko/06-roc-and-auc.md) | [en](./content/model-evaluation-101/en/06-roc-and-auc.md) | [medium](./content/model-evaluation-101/medium/06.html) | Draft |
| 7 | Model Evaluation 101 (7/10): 확률 보정 이해하기 | [ko](./content/model-evaluation-101/ko/07-calibration.md) | [en](./content/model-evaluation-101/en/07-calibration.md) | [medium](./content/model-evaluation-101/medium/07.html) | Draft |
| 8 | Model Evaluation 101 (8/10): 교차 검증 이해하기 | [ko](./content/model-evaluation-101/ko/08-cross-validation.md) | [en](./content/model-evaluation-101/en/08-cross-validation.md) | [medium](./content/model-evaluation-101/medium/08.html) | Draft |
| 9 | Model Evaluation 101 (9/10): 오류 분석으로 약점 찾기 | [ko](./content/model-evaluation-101/ko/09-error-analysis.md) | [en](./content/model-evaluation-101/en/09-error-analysis.md) | [medium](./content/model-evaluation-101/medium/09.html) | Draft |
| 10 | Model Evaluation 101 (10/10): 평가 리포트 만들기 | [ko](./content/model-evaluation-101/ko/10-evaluation-report.md) | [en](./content/model-evaluation-101/en/10-evaluation-report.md) | [medium](./content/model-evaluation-101/medium/10.html) | Draft |

### MLOps 101 (`mlops-101`)

운영 가능한 ML 시스템 — 실험 관리, 모델 배포, 모니터링, drift, feature store까지.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/mlops-101/`](./content/mlops-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | MLOps 101 (1/10): MLOps란 무엇인가? | [ko](./content/mlops-101/ko/01-what-is-mlops.md) | [en](./content/mlops-101/en/01-what-is-mlops.md) | [medium](./content/mlops-101/medium/01.html) | Draft |
| 2 | MLOps 101 (2/10): 실험 관리 | [ko](./content/mlops-101/ko/02-experiment-tracking.md) | [en](./content/mlops-101/en/02-experiment-tracking.md) | [medium](./content/mlops-101/medium/02.html) | Draft |
| 3 | MLOps 101 (3/10): 데이터 버전 관리 | [ko](./content/mlops-101/ko/03-data-versioning.md) | [en](./content/mlops-101/en/03-data-versioning.md) | [medium](./content/mlops-101/medium/03.html) | Draft |
| 4 | MLOps 101 (4/10): 모델 학습 파이프라인 | [ko](./content/mlops-101/ko/04-training-pipeline.md) | [en](./content/mlops-101/en/04-training-pipeline.md) | [medium](./content/mlops-101/medium/04.html) | Draft |
| 5 | MLOps 101 (5/10): 모델 배포 | [ko](./content/mlops-101/ko/05-model-deployment.md) | [en](./content/mlops-101/en/05-model-deployment.md) | [medium](./content/mlops-101/medium/05.html) | Draft |
| 6 | MLOps 101 (6/10): 모델 모니터링 | [ko](./content/mlops-101/ko/06-model-monitoring.md) | [en](./content/mlops-101/en/06-model-monitoring.md) | [medium](./content/mlops-101/medium/06.html) | Draft |
| 7 | MLOps 101 (7/10): 데이터 드리프트와 모델 드리프트 | [ko](./content/mlops-101/ko/07-data-and-model-drift.md) | [en](./content/mlops-101/en/07-data-and-model-drift.md) | [medium](./content/mlops-101/medium/07.html) | Draft |
| 8 | MLOps 101 (8/10): 재학습 | [ko](./content/mlops-101/ko/08-retraining.md) | [en](./content/mlops-101/en/08-retraining.md) | [medium](./content/mlops-101/medium/08.html) | Draft |
| 9 | MLOps 101 (9/10): 피처 스토어 | [ko](./content/mlops-101/ko/09-feature-store.md) | [en](./content/mlops-101/en/09-feature-store.md) | [medium](./content/mlops-101/medium/09.html) | Draft |
| 10 | MLOps 101 (10/10): 운영 가능한 ML 시스템 | [ko](./content/mlops-101/ko/10-production-ml-system.md) | [en](./content/mlops-101/en/10-production-ml-system.md) | [medium](./content/mlops-101/medium/10.html) | Draft |

### Data Warehouse 101 (`data-warehouse-101`)

OLTP/OLAP, Fact와 Dimension, Star Schema, Partition, ETL/ELT, BI 연동까지 분석을 위한 데이터 저장소를 설계하는 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/data-warehouse-101/`](./content/data-warehouse-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Data Warehouse 101 (1/10): Data Warehouse란 무엇인가? | [ko](./content/data-warehouse-101/ko/01-what-is-data-warehouse.md) | [en](./content/data-warehouse-101/en/01-what-is-data-warehouse.md) | [medium](./content/data-warehouse-101/medium/01.html) | Draft |
| 2 | Data Warehouse 101 (2/10): OLTP와 OLAP | [ko](./content/data-warehouse-101/ko/02-oltp-and-olap.md) | [en](./content/data-warehouse-101/en/02-oltp-and-olap.md) | [medium](./content/data-warehouse-101/medium/02.html) | Draft |
| 3 | Data Warehouse 101 (3/10): Fact와 Dimension | [ko](./content/data-warehouse-101/ko/03-fact-and-dimension.md) | [en](./content/data-warehouse-101/en/03-fact-and-dimension.md) | [medium](./content/data-warehouse-101/medium/03.html) | Draft |
| 4 | Data Warehouse 101 (4/10): Star Schema | [ko](./content/data-warehouse-101/ko/04-star-schema.md) | [en](./content/data-warehouse-101/en/04-star-schema.md) | [medium](./content/data-warehouse-101/medium/04.html) | Draft |
| 5 | Data Warehouse 101 (5/10): Partition과 Clustering | [ko](./content/data-warehouse-101/ko/05-partition-and-clustering.md) | [en](./content/data-warehouse-101/en/05-partition-and-clustering.md) | [medium](./content/data-warehouse-101/medium/05.html) | Draft |
| 6 | Data Warehouse 101 (6/10): ETL과 ELT | [ko](./content/data-warehouse-101/ko/06-etl-and-elt.md) | [en](./content/data-warehouse-101/en/06-etl-and-elt.md) | [medium](./content/data-warehouse-101/medium/06.html) | Draft |
| 7 | Data Warehouse 101 (7/10): BI와 Dashboard | [ko](./content/data-warehouse-101/ko/07-bi-and-dashboard.md) | [en](./content/data-warehouse-101/en/07-bi-and-dashboard.md) | [medium](./content/data-warehouse-101/medium/07.html) | Draft |
| 8 | Data Warehouse 101 (8/10): Data Mart | [ko](./content/data-warehouse-101/ko/08-data-mart.md) | [en](./content/data-warehouse-101/en/08-data-mart.md) | [medium](./content/data-warehouse-101/medium/08.html) | Draft |
| 9 | Data Warehouse 101 (9/10): 성능 최적화 | [ko](./content/data-warehouse-101/ko/09-performance-optimization.md) | [en](./content/data-warehouse-101/en/09-performance-optimization.md) | [medium](./content/data-warehouse-101/medium/09.html) | Draft |
| 10 | Data Warehouse 101 (10/10): Warehouse 설계 예제 | [ko](./content/data-warehouse-101/ko/10-warehouse-design-example.md) | [en](./content/data-warehouse-101/en/10-warehouse-design-example.md) | [medium](./content/data-warehouse-101/medium/10.html) | Draft |

### Python DB-API 101 (`python-dbapi-101`)

Python의 표준 데이터베이스 인터페이스 PEP 249(DB-API 2.0)를 SQLite 기준으로 다루는 입문 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/python-dbapi-101/`](./content/python-dbapi-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Python DB-API 101 (1/10): 왜 DB-API 2.0인가 - PEP 249가 푼 문제 | [ko](./content/python-dbapi-101/ko/01-why-db-api-pep-249.md) | [en](./content/python-dbapi-101/en/01-why-db-api-pep-249.md) | [medium](./content/python-dbapi-101/medium/01.html) | Publish Ready |
| 2 | Python DB-API 101 (2/10): Connection과 Cursor Lifecycle | [ko](./content/python-dbapi-101/ko/02-connection-cursor-lifecycle.md) | [en](./content/python-dbapi-101/en/02-connection-cursor-lifecycle.md) | [medium](./content/python-dbapi-101/medium/02.html) | Publish Ready |
| 3 | Python DB-API 101 (3/10): execute, executemany, fetch 패턴 | [ko](./content/python-dbapi-101/ko/03-execute-fetch-patterns.md) | [en](./content/python-dbapi-101/en/03-execute-fetch-patterns.md) | [medium](./content/python-dbapi-101/medium/03.html) | Publish Ready |
| 4 | Python DB-API 101 (4/10): Parameter binding과 SQL injection 방어 (sqlite3, PEP 249) | [ko](./content/python-dbapi-101/ko/04-parameter-binding-sql-injection.md) | [en](./content/python-dbapi-101/en/04-parameter-binding-sql-injection.md) | [medium](./content/python-dbapi-101/medium/04.html) | Publish Ready |
| 5 | Python DB-API 101 (5/10): Transaction과 isolation level (sqlite3, PEP 249) | [ko](./content/python-dbapi-101/ko/05-transactions-isolation.md) | [en](./content/python-dbapi-101/en/05-transactions-isolation.md) | [medium](./content/python-dbapi-101/medium/05.html) | Publish Ready |
| 6 | Python DB-API 101 (6/10): Row factory와 type adapter (sqlite3, PEP 249) | [ko](./content/python-dbapi-101/ko/06-row-factories-adapters.md) | [en](./content/python-dbapi-101/en/06-row-factories-adapters.md) | [medium](./content/python-dbapi-101/medium/06.html) | Publish Ready |
| 7 | Python DB-API 101 (7/10): PEP 249 예외 계층과 SQLite 에러 처리 | [ko](./content/python-dbapi-101/ko/07-error-handling-exception-hierarchy.md) | [en](./content/python-dbapi-101/en/07-error-handling-exception-hierarchy.md) | [medium](./content/python-dbapi-101/medium/07.html) | Publish Ready |
| 8 | Python DB-API 101 (8/10): SQLite Connection 관리: thread-safety, check_same_thread, 그리고 풀링 | [ko](./content/python-dbapi-101/ko/08-connection-pooling.md) | [en](./content/python-dbapi-101/en/08-connection-pooling.md) | [medium](./content/python-dbapi-101/medium/08.html) | Publish Ready |
| 9 | Python DB-API 101 (9/10): aiosqlite로 비동기 SQLite 다루기 | [ko](./content/python-dbapi-101/ko/09-async-aiosqlite.md) | [en](./content/python-dbapi-101/en/09-async-aiosqlite.md) | [medium](./content/python-dbapi-101/medium/09.html) | Publish Ready |
| 10 | Python DB-API 101 (10/10): SQLite Production 패턴: retry, timeout, 관측성, 백업 | [ko](./content/python-dbapi-101/ko/10-production-patterns.md) | [en](./content/python-dbapi-101/en/10-production-patterns.md) | [medium](./content/python-dbapi-101/medium/10.html) | Publish Ready |

### SQLAlchemy 101 (`sqlalchemy-101`)

SQLAlchemy 2.x를 SQLite 기준으로 다루는 입문 시리즈. Engine·Connection·Core·ORM·Session·Unit of Work·Relationship·Loading 전략·Async·Production 패턴을 배웁니다.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/sqlalchemy-101/`](./content/sqlalchemy-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | SQLAlchemy 101 (1/10): SQLAlchemy 2.x 시작하기 - Engine과 Connection의 본질 | [ko](./content/sqlalchemy-101/ko/01-sqlalchemy-2x-engine-connection.md) | [en](./content/sqlalchemy-101/en/01-sqlalchemy-2x-engine-connection.md) | [medium](./content/sqlalchemy-101/medium/01.html) | Publish Ready |
| 2 | SQLAlchemy 101 (2/10): SQLAlchemy Core - MetaData, Table, Column으로 schema를 Python 객체로 만들기 | [ko](./content/sqlalchemy-101/ko/02-core-metadata-table-types.md) | [en](./content/sqlalchemy-101/en/02-core-metadata-table-types.md) | [medium](./content/sqlalchemy-101/medium/02.html) | Publish Ready |
| 3 | SQLAlchemy 101 (3/10): SQLAlchemy Core - select·insert·update·delete를 2.x style로 다루기 | [ko](./content/sqlalchemy-101/ko/03-core-select-insert-update-delete.md) | [en](./content/sqlalchemy-101/en/03-core-select-insert-update-delete.md) | [medium](./content/sqlalchemy-101/medium/03.html) | Publish Ready |
| 4 | SQLAlchemy 101 (4/10): ORM 기초: DeclarativeBase와 mapped_column으로 모델 정의하기 | [ko](./content/sqlalchemy-101/ko/04-orm-declarative-mapped-column.md) | [en](./content/sqlalchemy-101/en/04-orm-declarative-mapped-column.md) | [medium](./content/sqlalchemy-101/medium/04.html) | Publish Ready |
| 5 | SQLAlchemy 101 (5/10): Session 깊이 보기: Unit of Work와 Identity Map의 동작 원리 | [ko](./content/sqlalchemy-101/ko/05-session-unit-of-work-identity-map.md) | [en](./content/sqlalchemy-101/en/05-session-unit-of-work-identity-map.md) | [medium](./content/sqlalchemy-101/medium/05.html) | Publish Ready |
| 6 | SQLAlchemy 101 (6/10): ORM 관계 매핑: relationship과 back_populates로 양방향 탐색 안전하게 잇기 | [ko](./content/sqlalchemy-101/ko/06-relationships-back-populates.md) | [en](./content/sqlalchemy-101/en/06-relationships-back-populates.md) | [medium](./content/sqlalchemy-101/medium/06.html) | Publish Ready |
| 7 | SQLAlchemy 101 (7/10): 로딩 전략과 N+1 문제: lazy/joined/selectin을 언제 골라야 하는가 | [ko](./content/sqlalchemy-101/ko/07-loading-strategies-n-plus-one.md) | [en](./content/sqlalchemy-101/en/07-loading-strategies-n-plus-one.md) | [medium](./content/sqlalchemy-101/medium/07.html) | Publish Ready |
| 8 | SQLAlchemy 101 (8/10): 이벤트, hybrid_property, 그리고 커스텀 타입 | [ko](./content/sqlalchemy-101/ko/08-events-hybrid-types.md) | [en](./content/sqlalchemy-101/en/08-events-hybrid-types.md) | [medium](./content/sqlalchemy-101/medium/08.html) | Publish Ready |
| 9 | SQLAlchemy 101 (9/10): 비동기 SQLAlchemy: aiosqlite와 AsyncSession | [ko](./content/sqlalchemy-101/ko/09-async-aiosqlite.md) | [en](./content/sqlalchemy-101/en/09-async-aiosqlite.md) | [medium](./content/sqlalchemy-101/medium/09.html) | Publish Ready |
| 10 | SQLAlchemy 101 (10/10): 프로덕션 패턴: 풀, 관측, 마이그레이션, 배포 | [ko](./content/sqlalchemy-101/ko/10-production-patterns.md) | [en](./content/sqlalchemy-101/en/10-production-patterns.md) | [medium](./content/sqlalchemy-101/medium/10.html) | Publish Ready |

### Alembic 101 (`alembic-101`)

Alembic으로 SQLAlchemy 마이그레이션을 운영하는 입문 시리즈. autogenerate, branch와 merge, 데이터 마이그레이션, downgrade 전략, 배포 순서를 SQLite 기준으로 다룹니다.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, mkdocs, ebook
- 경로: [`content/alembic-101/`](./content/alembic-101/)

| # | Title | KO | EN | Status |
| --- | --- | --- | --- | --- |
| 1 | Alembic 101 (1/10): 왜 Alembic인가, 그리고 init까지 | [ko](./content/alembic-101/ko/01-why-alembic-and-init.md) | [en](./content/alembic-101/en/01-why-alembic-and-init.md) | Publish Ready |
| 2 | Alembic 101 (2/10): env.py와 target_metadata: 모델과 마이그레이션 연결 | [ko](./content/alembic-101/ko/02-env-py-and-target-metadata.md) | [en](./content/alembic-101/en/02-env-py-and-target-metadata.md) | Publish Ready |
| 3 | Alembic 101 (3/10): 첫 revision: upgrade와 downgrade를 손으로 작성 | [ko](./content/alembic-101/ko/03-first-revision-upgrade-downgrade.md) | [en](./content/alembic-101/en/03-first-revision-upgrade-downgrade.md) | Publish Ready |
| 4 | Alembic 101 (4/10): autogenerate: 잡는 것과 못 잡는 것의 경계 | [ko](./content/alembic-101/ko/04-autogenerate-and-its-limits.md) | [en](./content/alembic-101/en/04-autogenerate-and-its-limits.md) | Publish Ready |
| 5 | Alembic 101 (5/10): branch와 merge: 동시에 만든 revision을 합치는 법 | [ko](./content/alembic-101/ko/05-branches-and-merges.md) | [en](./content/alembic-101/en/05-branches-and-merges.md) | Publish Ready |
| 6 | Alembic 101 (6/10): 데이터 마이그레이션: schema 변경과 데이터 변경을 분리하기 | [ko](./content/alembic-101/ko/06-data-migrations.md) | [en](./content/alembic-101/en/06-data-migrations.md) | Publish Ready |
| 7 | Alembic 101 (7/10): online과 offline 모드: --sql로 DDL을 미리 보고 SQLite batch 다루기 | [ko](./content/alembic-101/ko/07-online-vs-offline-and-batch.md) | [en](./content/alembic-101/en/07-online-vs-offline-and-batch.md) | Publish Ready |
| 8 | Alembic 101 (8/10): downgrade 전략: 언제 진심으로 작성하고 언제 막을 것인가 | [ko](./content/alembic-101/ko/08-downgrade-strategy.md) | [en](./content/alembic-101/en/08-downgrade-strategy.md) | Publish Ready |
| 9 | Alembic 101 (9/10): 배포 순서와 blue/green: schema와 application code의 안전한 동기화 | [ko](./content/alembic-101/ko/09-deploy-ordering-and-blue-green.md) | [en](./content/alembic-101/en/09-deploy-ordering-and-blue-green.md) | Publish Ready |
| 10 | Alembic 101 (10/10): Production과 team workflow: PR, CI, 모니터링, 그리고 incident response | [ko](./content/alembic-101/ko/10-production-and-team-workflow.md) | [en](./content/alembic-101/en/10-production-and-team-workflow.md) | Publish Ready |

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
| 1 | Azure App Service란? - 플랫폼 아키텍처 이해하기 | [ko](./content/azure-app-service-101/ko/01-what-is-app-service.md) | [en](./content/azure-app-service-101/en/01-what-is-app-service.md) | [medium](./content/azure-app-service-101/medium/01.html) | Publish Ready |
| 2 | Request Lifecycle: 3am에 터진 502를 어디서부터 봐야 할까 | [ko](./content/azure-app-service-101/ko/02-request-lifecycle.md) | [en](./content/azure-app-service-101/en/02-request-lifecycle.md) | [medium](./content/azure-app-service-101/medium/02.html) | Publish Ready |
| 3 | Hosting Models: 어떤 플랜을 선택해야 할까? | [ko](./content/azure-app-service-101/ko/03-hosting-models.md) | [en](./content/azure-app-service-101/en/03-hosting-models.md) | [medium](./content/azure-app-service-101/medium/03.html) | Publish Ready |
| 4 | 첫 번째 배포: 로컬에서 Azure까지 (Python/Flask) | [ko](./content/azure-app-service-101/ko/04-first-deploy.md) | [en](./content/azure-app-service-101/en/04-first-deploy.md) | [medium](./content/azure-app-service-101/medium/04.html) | Publish Ready |
| 5 | Configuration 마스터하기: App Settings & 환경변수 | [ko](./content/azure-app-service-101/ko/05-configuration.md) | [en](./content/azure-app-service-101/en/05-configuration.md) | [medium](./content/azure-app-service-101/medium/05.html) | Publish Ready |
| 6 | 로그와 모니터링 기초: “앱이 느려요”에 답할 수 있는 상태 만들기 | [ko](./content/azure-app-service-101/ko/06-logging-monitoring.md) | [en](./content/azure-app-service-101/en/06-logging-monitoring.md) | [medium](./content/azure-app-service-101/medium/06.html) | Publish Ready |
| 7 | Scaling 101: 언제 Scale Up vs Scale Out? | [ko](./content/azure-app-service-101/ko/07-scaling-101.md) | [en](./content/azure-app-service-101/en/07-scaling-101.md) | [medium](./content/azure-app-service-101/medium/07.html) | Publish Ready |

### Azure App Service Deep Dive (`azure-app-service-deep-dive`)

App Service 내부 — Front-End, Worker, Sandbox, Kudu, Scaling.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/azure-app-service-deep-dive/`](./content/azure-app-service-deep-dive/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Azure App Service Deep Dive (1/6): App Service 플랫폼 아키텍처 — Front-End·Worker·File Server | [ko](./content/azure-app-service-deep-dive/ko/01-platform-architecture.md) | [en](./content/azure-app-service-deep-dive/en/01-platform-architecture.md) | [medium](./content/azure-app-service-deep-dive/medium/01.html) | Publish Ready |
| 2 | Azure App Service Deep Dive (2/6): Front-End과 ARR — 요청은 어떻게 워커에 도달하는가 | [ko](./content/azure-app-service-deep-dive/ko/02-front-end-and-arr.md) | [en](./content/azure-app-service-deep-dive/en/02-front-end-and-arr.md) | [medium](./content/azure-app-service-deep-dive/medium/02.html) | Publish Ready |
| 3 | Azure App Service Deep Dive (3/6): Worker 인스턴스와 샌드박스 — 사용자 코드를 어디에 가두는가 | [ko](./content/azure-app-service-deep-dive/ko/03-worker-and-sandbox.md) | [en](./content/azure-app-service-deep-dive/en/03-worker-and-sandbox.md) | [medium](./content/azure-app-service-deep-dive/medium/03.html) | Publish Ready |
| 4 | Azure App Service Deep Dive (4/6): 배포와 Kudu — 빌드·동기화·릴리스의 안쪽 | [ko](./content/azure-app-service-deep-dive/ko/04-deployment-and-kudu.md) | [en](./content/azure-app-service-deep-dive/en/04-deployment-and-kudu.md) | [medium](./content/azure-app-service-deep-dive/medium/04.html) | Publish Ready |
| 5 | Azure App Service Deep Dive (5/6): 스케일링 내부 동작 — Scale Out 결정과 워커 추가 경로 | [ko](./content/azure-app-service-deep-dive/ko/05-scaling-internals.md) | [en](./content/azure-app-service-deep-dive/en/05-scaling-internals.md) | [medium](./content/azure-app-service-deep-dive/medium/05.html) | Publish Ready |
| 6 | Azure App Service Deep Dive (6/6): 콜드 스타트와 Warmup — 첫 요청이 비싼 이유 | [ko](./content/azure-app-service-deep-dive/ko/06-cold-start-and-warmup.md) | [en](./content/azure-app-service-deep-dive/en/06-cold-start-and-warmup.md) | [medium](./content/azure-app-service-deep-dive/medium/06.html) | Publish Ready |

### Azure Functions 101 (`azure-functions-101`)

Azure Functions 입문 7부작 — 트리거/바인딩부터 운영까지.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/azure-functions-101/`](./content/azure-functions-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Azure Functions 101 (1/7): Azure Functions란? — 이벤트가 함수를 호출하는 세상 | [ko](./content/azure-functions-101/ko/01-what-is-azure-functions.md) | [en](./content/azure-functions-101/en/01-what-is-azure-functions.md) | [medium](./content/azure-functions-101/medium/01.html) | Publish Ready |
| 2 | Azure Functions 101 (2/7): 트리거와 바인딩 — 함수 입출력의 모든 것 | [ko](./content/azure-functions-101/ko/02-triggers-and-bindings.md) | [en](./content/azure-functions-101/en/02-triggers-and-bindings.md) | [medium](./content/azure-functions-101/medium/02.html) | Publish Ready |
| 3 | Azure Functions 101 (3/7): Host와 Worker — 함수는 누가 실행하는가 | [ko](./content/azure-functions-101/ko/03-host-and-worker.md) | [en](./content/azure-functions-101/en/03-host-and-worker.md) | [medium](./content/azure-functions-101/medium/03.html) | Publish Ready |
| 4 | Azure Functions 101 (4/7): 함수 하나 배포하기 — 로컬에서 Azure까지 | [ko](./content/azure-functions-101/ko/04-first-deploy.md) | [en](./content/azure-functions-101/en/04-first-deploy.md) | [medium](./content/azure-functions-101/medium/04.html) | Publish Ready |
| 5 | Azure Functions 101 (5/7): 어떤 플랜을 선택해야 할까 — Consumption / Flex / Premium / Dedicated | [ko](./content/azure-functions-101/ko/05-choosing-a-plan.md) | [en](./content/azure-functions-101/en/05-choosing-a-plan.md) | [medium](./content/azure-functions-101/medium/05.html) | Publish Ready |
| 6 | Azure Functions 101 (6/7): 스케일링과 콜드 스타트 — 서버리스가 빨라지는 순간과 느려지는 순간 | [ko](./content/azure-functions-101/ko/06-scaling-and-cold-start.md) | [en](./content/azure-functions-101/en/06-scaling-and-cold-start.md) | [medium](./content/azure-functions-101/medium/06.html) | Publish Ready |
| 7 | Azure Functions 101 (7/7): 모니터링과 운영 기초 | [ko](./content/azure-functions-101/ko/07-monitoring-and-ops.md) | [en](./content/azure-functions-101/en/07-monitoring-and-ops.md) | [medium](./content/azure-functions-101/medium/07.html) | Publish Ready |

### Azure Functions Deep Dive (`azure-functions-deep-dive`)

Azure Functions Host 소스 분석 시리즈 (commit-pinned).

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/azure-functions-deep-dive/`](./content/azure-functions-deep-dive/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Azure Functions Deep Dive (1/6): 호스트 부팅 — `WebJobsScriptHostService`부터 따라가기 | [ko](./content/azure-functions-deep-dive/ko/01-host-bootstrap.md) | [en](./content/azure-functions-deep-dive/en/01-host-bootstrap.md) | [medium](./content/azure-functions-deep-dive/medium/01.html) | Publish Ready |
| 2 | Azure Functions Deep Dive (2/6): Worker 프로세스 — 한 호스트에서 여러 언어 런타임이 같이 사는 법 | [ko](./content/azure-functions-deep-dive/ko/02-worker-process.md) | [en](./content/azure-functions-deep-dive/en/02-worker-process.md) | [medium](./content/azure-functions-deep-dive/medium/02.html) | Publish Ready |
| 3 | Azure Functions Deep Dive (3/6): gRPC 이벤트 스트림 — 호스트와 워커는 무엇을 주고받는가 | [ko](./content/azure-functions-deep-dive/ko/03-grpc-event-stream.md) | [en](./content/azure-functions-deep-dive/en/03-grpc-event-stream.md) | [medium](./content/azure-functions-deep-dive/medium/03.html) | Publish Ready |
| 4 | Azure Functions Deep Dive (4/6): Dispatcher와 Invocation — 함수 호출이 워커에 도달하기까지 | [ko](./content/azure-functions-deep-dive/ko/04-dispatcher-and-invocation.md) | [en](./content/azure-functions-deep-dive/en/04-dispatcher-and-invocation.md) | [medium](./content/azure-functions-deep-dive/medium/04.html) | Publish Ready |
| 5 | Azure Functions Deep Dive (5/6): 스케일링 내부 동작 — Scale Controller, ScaleMonitor, 그리고 플랜별 차이 | [ko](./content/azure-functions-deep-dive/ko/05-scaling-internals.md) | [en](./content/azure-functions-deep-dive/en/05-scaling-internals.md) | [medium](./content/azure-functions-deep-dive/medium/05.html) | Publish Ready |
| 6 | Azure Functions Deep Dive (6/6): 콜드 스타트와 Placeholder Mode — 새 인스턴스가 만들어질 때 | [ko](./content/azure-functions-deep-dive/ko/06-cold-start-placeholder.md) | [en](./content/azure-functions-deep-dive/en/06-cold-start-placeholder.md) | [medium](./content/azure-functions-deep-dive/medium/06.html) | Publish Ready |

### Azure Kubernetes Service 101 (`azure-aks-101`)

AKS 입문 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/azure-aks-101/`](./content/azure-aks-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Azure Kubernetes Service 101 (1/7): Azure Kubernetes Service란? — 직접 운영하지 않아도 되는 Kubernetes | [ko](./content/azure-aks-101/ko/01-what-is-aks.md) | [en](./content/azure-aks-101/en/01-what-is-aks.md) | [medium](./content/azure-aks-101/medium/01.html) | Publish Ready |
| 2 | Azure Kubernetes Service 101 (2/7): 클러스터 아키텍처 — Control Plane과 Node Pool | [ko](./content/azure-aks-101/ko/02-cluster-architecture.md) | [en](./content/azure-aks-101/en/02-cluster-architecture.md) | [medium](./content/azure-aks-101/medium/02.html) | Publish Ready |
| 3 | Azure Kubernetes Service 101 (3/7): 첫 클러스터 만들고 앱 배포하기 — Python/FastAPI | [ko](./content/azure-aks-101/ko/03-first-cluster-and-deploy.md) | [en](./content/azure-aks-101/en/03-first-cluster-and-deploy.md) | [medium](./content/azure-aks-101/medium/03.html) | Publish Ready |
| 4 | Azure Kubernetes Service 101 (4/7): Pod·Deployment·Service — 워크로드를 표현하는 세 가지 방식 | [ko](./content/azure-aks-101/ko/04-pod-deployment-service.md) | [en](./content/azure-aks-101/en/04-pod-deployment-service.md) | [medium](./content/azure-aks-101/medium/04.html) | Publish Ready |
| 5 | Azure Kubernetes Service 101 (5/7): 네트워킹과 Ingress — 클러스터 안과 밖을 잇는 길 | [ko](./content/azure-aks-101/ko/05-networking-and-ingress.md) | [en](./content/azure-aks-101/en/05-networking-and-ingress.md) | [medium](./content/azure-aks-101/medium/05.html) | Publish Ready |
| 6 | Azure Kubernetes Service 101 (6/7): 스케일링 — HPA, Cluster Autoscaler, KEDA | [ko](./content/azure-aks-101/ko/06-scaling-hpa-ca-keda.md) | [en](./content/azure-aks-101/en/06-scaling-hpa-ca-keda.md) | [medium](./content/azure-aks-101/medium/06.html) | Publish Ready |
| 7 | Azure Kubernetes Service 101 (7/7): 모니터링과 운영 — Container Insights, 로그, 알람 | [ko](./content/azure-aks-101/ko/07-monitoring-and-ops.md) | [en](./content/azure-aks-101/en/07-monitoring-and-ops.md) | [medium](./content/azure-aks-101/medium/07.html) | Publish Ready |

### Azure Kubernetes Service Deep Dive (`azure-aks-deep-dive`)

AKS control plane / data plane 내부 동작.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/azure-aks-deep-dive/`](./content/azure-aks-deep-dive/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Azure Kubernetes Service Deep Dive (1/6): Control Plane 해부 — AKS가 사용자에게서 가린 것 | [ko](./content/azure-aks-deep-dive/ko/01-control-plane-anatomy.md) | [en](./content/azure-aks-deep-dive/en/01-control-plane-anatomy.md) | [medium](./content/azure-aks-deep-dive/medium/01.html) | Publish Ready |
| 2 | Azure Kubernetes Service Deep Dive (2/6): kubelet과 containerd — 노드 위에서 컨테이너가 뜨기까지 | [ko](./content/azure-aks-deep-dive/ko/02-kubelet-and-containerd.md) | [en](./content/azure-aks-deep-dive/en/02-kubelet-and-containerd.md) | [medium](./content/azure-aks-deep-dive/medium/02.html) | Publish Ready |
| 3 | Azure Kubernetes Service Deep Dive (3/6): CNI와 Azure CNI Overlay — Pod IP가 어디서 오는가 | [ko](./content/azure-aks-deep-dive/ko/03-cni-and-azure-cni-overlay.md) | [en](./content/azure-aks-deep-dive/en/03-cni-and-azure-cni-overlay.md) | [medium](./content/azure-aks-deep-dive/medium/03.html) | Publish Ready |
| 4 | Azure Kubernetes Service Deep Dive (4/6): Scheduler와 Pod 배치 — 어느 노드로 갈지 누가 정하는가 | [ko](./content/azure-aks-deep-dive/ko/04-scheduler-and-pod-placement.md) | [en](./content/azure-aks-deep-dive/en/04-scheduler-and-pod-placement.md) | [medium](./content/azure-aks-deep-dive/medium/04.html) | Publish Ready |
| 5 | Azure Kubernetes Service Deep Dive (5/6): HPA와 Cluster Autoscaler 내부 — 두 컨트롤 루프 | [ko](./content/azure-aks-deep-dive/ko/05-hpa-and-cluster-autoscaler-internals.md) | [en](./content/azure-aks-deep-dive/en/05-hpa-and-cluster-autoscaler-internals.md) | [medium](./content/azure-aks-deep-dive/medium/05.html) | Publish Ready |
| 6 | Azure Kubernetes Service Deep Dive (6/6): KEDA 내부 — ScaledObject가 HPA를 만드는 방식 | [ko](./content/azure-aks-deep-dive/ko/06-keda-internals.md) | [en](./content/azure-aks-deep-dive/en/06-keda-internals.md) | [medium](./content/azure-aks-deep-dive/medium/06.html) | Publish Ready |

### Azure Container Apps 101 (`azure-aca-101`)

Container Apps 입문 시리즈.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/azure-aca-101/`](./content/azure-aca-101/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Azure Container Apps 101 (1/7): Azure Container Apps란? — Kubernetes 없이 컨테이너 운영하기 | [ko](./content/azure-aca-101/ko/01-what-is-aca.md) | [en](./content/azure-aca-101/en/01-what-is-aca.md) | [medium](./content/azure-aca-101/medium/01.html) | Publish Ready |
| 2 | Azure Container Apps 101 (2/7): Environment, Container App, Revision — ACA in three words | [ko](./content/azure-aca-101/ko/02-environment-app-revision.md) | [en](./content/azure-aca-101/en/02-environment-app-revision.md) | [medium](./content/azure-aca-101/medium/02.html) | Publish Ready |
| 3 | Azure Container Apps 101 (3/7): 첫 배포하기 — Python/FastAPI | [ko](./content/azure-aca-101/ko/03-first-deploy.md) | [en](./content/azure-aca-101/en/03-first-deploy.md) | [medium](./content/azure-aca-101/medium/03.html) | Publish Ready |
| 4 | Azure Container Apps 101 (4/7): Ingress와 트래픽 분할 — revision 기반 배포 전략 | [ko](./content/azure-aca-101/ko/04-ingress-and-traffic-split.md) | [en](./content/azure-aca-101/en/04-ingress-and-traffic-split.md) | [medium](./content/azure-aca-101/medium/04.html) | Publish Ready |
| 5 | Azure Container Apps 101 (5/7): 스케일링 — KEDA scaler와 zero-to-N | [ko](./content/azure-aca-101/ko/05-scaling-with-keda.md) | [en](./content/azure-aca-101/en/05-scaling-with-keda.md) | [medium](./content/azure-aca-101/medium/05.html) | Publish Ready |
| 6 | Azure Container Apps 101 (6/7): Dapr 통합 — 사이드카로 얻는 것 | [ko](./content/azure-aca-101/ko/06-dapr-integration.md) | [en](./content/azure-aca-101/en/06-dapr-integration.md) | [medium](./content/azure-aca-101/medium/06.html) | Publish Ready |
| 7 | Azure Container Apps 101 (7/7): 모니터링과 운영 — Log Analytics와 Application Insights | [ko](./content/azure-aca-101/ko/07-monitoring-and-ops.md) | [en](./content/azure-aca-101/en/07-monitoring-and-ops.md) | [medium](./content/azure-aca-101/medium/07.html) | Publish Ready |

### Azure Container Apps Deep Dive (`azure-aca-deep-dive`)

ACA 위에 얹힌 KEDA·Dapr·Envoy 내부 동작.

- 상태: **Content Ready**
- 언어: ko, en
- 발행 대상: tistory, hashnode, medium, mkdocs, ebook
- 경로: [`content/azure-aca-deep-dive/`](./content/azure-aca-deep-dive/)

| # | Title | KO | EN | Medium | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Azure Container Apps Deep Dive (1/6): ACA 아키텍처 — 사용자에게 보이지 않는 Kubernetes 위에 얹은 것 | [ko](./content/azure-aca-deep-dive/ko/01-aca-architecture.md) | [en](./content/azure-aca-deep-dive/en/01-aca-architecture.md) | [medium](./content/azure-aca-deep-dive/medium/01.html) | Publish Ready |
| 2 | Azure Container Apps Deep Dive (2/6): Environment 내부 — 네트워크·관측·Dapr 스코프의 경계 | [ko](./content/azure-aca-deep-dive/ko/02-environment-internals.md) | [en](./content/azure-aca-deep-dive/en/02-environment-internals.md) | [medium](./content/azure-aca-deep-dive/medium/02.html) | Publish Ready |
| 3 | Azure Container Apps Deep Dive (3/6): Revision과 트래픽 분할 — Envoy 가중치는 어디에서 오는가 | [ko](./content/azure-aca-deep-dive/ko/03-revision-and-traffic-split.md) | [en](./content/azure-aca-deep-dive/en/03-revision-and-traffic-split.md) | [medium](./content/azure-aca-deep-dive/medium/03.html) | Publish Ready |
| 4 | Azure Container Apps Deep Dive (4/6): ACA 안의 KEDA — Scale Rule이 만드는 것 | [ko](./content/azure-aca-deep-dive/ko/04-keda-in-aca.md) | [en](./content/azure-aca-deep-dive/en/04-keda-in-aca.md) | [medium](./content/azure-aca-deep-dive/medium/04.html) | Publish Ready |
| 5 | Azure Container Apps Deep Dive (5/6): Dapr 사이드카 내부 — 컨테이너 옆에 뜨는 Go 프로세스 | [ko](./content/azure-aca-deep-dive/ko/05-dapr-sidecar-internals.md) | [en](./content/azure-aca-deep-dive/en/05-dapr-sidecar-internals.md) | [medium](./content/azure-aca-deep-dive/medium/05.html) | Publish Ready |
| 6 | Azure Container Apps Deep Dive (6/6): Envoy Ingress 경로 — 첫 요청이 사용자 컨테이너에 닿기까지 | [ko](./content/azure-aca-deep-dive/ko/06-envoy-ingress-path.md) | [en](./content/azure-aca-deep-dive/en/06-envoy-ingress-path.md) | [medium](./content/azure-aca-deep-dive/medium/06.html) | Publish Ready |
