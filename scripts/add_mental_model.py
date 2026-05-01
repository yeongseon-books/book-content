#!/usr/bin/env python3
"""
add_mental_model.py
멘탈 모델 섹션이 없는 시리즈의 ko/en 파일에
H1 다음 첫 번째 본문 ## 앞에 "한 문장 핵심" 단락을 삽입한다.

이미 '멘탈 모델', 'Mental Model', '한 문장' 키워드가 있는 파일은 건너뜀.
"""
from pathlib import Path
import re

REPO = Path(__file__).resolve().parents[1]

KO_INTRO_TEMPLATES = {
    "rag-deep-dive": [
        "이 장의 핵심: **청크 품질이 RAG 전체 성능을 결정한다.** 로더가 읽고 TextSplitter가 나눈 결과가 검색 정확도의 첫 번째 변수다.",
        "이 장의 핵심: **임베딩은 텍스트를 거리로 바꾼다.** 의미가 비슷할수록 벡터 공간에서 가깝고, FAISS는 그 거리를 빠르게 찾는다.",
        "이 장의 핵심: **리트리버는 검색 전략의 캡슐이다.** 같은 VectorStore에 어떤 search_type을 붙이느냐에 따라 결과가 달라진다.",
        "이 장의 핵심: **프롬프트는 컨텍스트와 질문을 붙이는 접착제다.** PromptTemplate이 두 입력을 하나의 LLM 호출로 만든다.",
        "이 장의 핵심: **LCEL 파이프는 컴포넌트를 순서대로 연결한다.** `retriever | prompt | llm | parser` 한 줄이 완전한 RAG 체인이다.",
        "이 장의 핵심: **평가 지표 없이는 개선 방향이 없다.** RAGAS의 faithfulness·relevancy·precision이 RAG 품질을 숫자로 만든다.",
    ],
    "langchain-101": [
        "이 장의 핵심: **LangChain은 파이프 연산자(`|`)로 컴포넌트를 연결한다.** Runnable 인터페이스가 모든 컴포넌트의 공통 언어다.",
        "이 장의 핵심: **Prompt + LLM = 가장 단순한 체인.** ChatPromptTemplate이 입력을 구조화하고 LLM이 응답을 반환한다.",
        "이 장의 핵심: **Retriever는 질문을 받아 관련 문서를 돌려준다.** VectorStore를 검색 인터페이스로 추상화한 것이다.",
        "이 장의 핵심: **Tool Calling은 LLM이 함수를 선택하게 한다.** 어떤 도구를 언제 쓸지 모델이 결정한다.",
        "이 장의 핵심: **Streaming은 토큰 단위 청크를 순서대로 흘려보낸다.** `stream()`이 제너레이터를 반환하고 클라이언트가 실시간으로 받는다.",
        "이 장의 핵심: **실전 체인은 retriever · prompt · llm · parser의 조합이다.** 각 컴포넌트가 독립적으로 교체 가능하다.",
    ],
    "llm-app-foundations-101": [
        "이 장의 핵심: **LLM API 호출은 HTTP POST 한 번이다.** 모델에 메시지를 보내고 텍스트를 받는 것이 전부다.",
        "이 장의 핵심: **토큰은 모델이 읽는 최소 단위다.** 문자 수와 토큰 수는 다르고, 비용과 컨텍스트 한계는 토큰 수로 결정된다.",
        "이 장의 핵심: **프롬프트의 구조가 응답의 품질을 결정한다.** System·User·Assistant 역할 분리가 출력을 제어하는 핵심 도구다.",
        "이 장의 핵심: **Few-shot 예제는 모델에게 패턴을 보여주는 것이다.** CoT는 중간 추론 단계를 출력하게 해 복잡한 문제를 풀게 한다.",
        "이 장의 핵심: **대화 상태는 메시지 목록을 직접 관리하는 것이다.** 모델은 무상태(stateless)이므로 매 호출에 전체 히스토리를 전달해야 한다.",
        "이 장의 핵심: **Streaming은 토큰이 생성되는 즉시 전달한다.** 사용자가 응답을 기다리지 않고 실시간으로 볼 수 있게 된다.",
    ],
    "llm-api-production-101": [
        "이 장의 핵심: **Structured Output은 모델이 JSON 스키마를 따르게 한다.** Pydantic 모델로 출력 형태를 고정하면 파싱 오류가 없어진다.",
        "이 장의 핵심: **Tool Calling은 모델이 함수 이름과 인자를 선택한다.** 실행은 코드가 하고, 결과를 다시 모델에 돌려준다.",
        "이 장의 핵심: **Streaming은 첫 토큰까지의 대기 시간(TTFT)을 없앤다.** 긴 응답일수록 사용자 체감 속도가 빨라진다.",
        "이 장의 핵심: **캐싱은 동일한 입력을 다시 보내지 않는 것이다.** Semantic cache는 유사한 질문도 캐시 히트로 처리한다.",
        "이 장의 핵심: **Retry + Exponential Backoff가 일시적 오류를 흡수한다.** 재시도 횟수와 간격을 제어하면 대부분의 429/503을 넘길 수 있다.",
        "이 장의 핵심: **Rate Limit은 토큰/분과 요청/분 두 축으로 걸린다.** 두 한도를 동시에 추적하고 큐로 평탄화해야 한다.",
    ],
    "vector-search-101": [
        "이 장의 핵심: **임베딩은 텍스트를 고차원 벡터로 압축한 것이다.** 의미가 비슷한 문장은 벡터 공간에서 가깝다.",
        "이 장의 핵심: **HuggingFace 임베딩은 로컬에서 무료로 실행된다.** `sentence-transformers`가 모델을 내려받고 벡터를 반환한다.",
        "이 장의 핵심: **코사인 유사도는 벡터 방향의 일치 정도다.** 크기는 무시하고 방향만 비교하므로 문장 길이 차이에 강건하다.",
        "이 장의 핵심: **FAISS는 벡터를 빠르게 찾는 라이브러리다.** IndexFlatL2가 가장 단순하고, 데이터가 커지면 IVF·HNSW로 전환한다.",
        "이 장의 핵심: **청크 크기와 중복(overlap)이 검색 품질을 결정한다.** 너무 크면 노이즈, 너무 작으면 맥락 손실이다.",
        "이 장의 핵심: **벡터 검색 파이프라인은 embed → index → query → retrieve 네 단계다.** 각 단계를 독립적으로 교체할 수 있어야 한다.",
    ],
    "ai-app-patterns-101": [
        "이 장의 핵심: **챗봇은 메시지 히스토리를 누적하는 루프다.** 대화 이력을 어떻게 관리하느냐가 응답 품질과 비용을 결정한다.",
        "이 장의 핵심: **RAG Q&A는 검색 → 주입 → 생성 세 단계다.** 질문으로 관련 문서를 찾고, 그 문서를 컨텍스트로 넣어 답을 만든다.",
        "이 장의 핵심: **문서 어시스턴트는 긴 텍스트를 짧은 구조로 만드는 것이다.** 요약·추출·분류는 동일한 Prompt-LLM 파이프의 변형이다.",
        "이 장의 핵심: **Agent는 도구 선택을 모델에게 위임한다.** ReAct 루프가 생각(Thought) → 행동(Action) → 관찰(Observation)을 반복한다.",
        "이 장의 핵심: **워크플로는 단계가 고정된 에이전트다.** 분기와 루프를 명시적으로 정의해 예측 가능성을 높인다.",
        "이 장의 핵심: **Human-in-the-loop는 불확실한 지점에 사람을 끼워 넣는다.** 언제 개입할지 결정하는 것이 설계의 핵심이다.",
    ],
    "korean-ai-stack-101": [
        "이 장의 핵심: **한국어 임베딩 모델은 한국어 문장의 의미를 벡터로 압축한다.** KoSimCSE·BGE-M3·Solar는 각각 다른 접근 방식을 가진다.",
        "이 장의 핵심: **KoSimCSE는 대조 학습으로 한국어 유사도를 잡는다.** 같은 의미의 문장 쌍을 가깝게, 다른 문장 쌍을 멀게 학습한다.",
        "이 장의 핵심: **BGE-M3는 한 모델로 다국어 임베딩을 처리한다.** 한국어와 영어를 같은 벡터 공간에 표현해 크로스링구얼 검색이 가능하다.",
        "이 장의 핵심: **CLOVA OCR은 이미지에서 텍스트를 추출한다.** 스캔 문서·영수증·명함을 구조화된 텍스트로 변환해 RAG 파이프라인에 연결할 수 있다.",
        "이 장의 핵심: **HyperCLOVA X와 Solar는 한국어에 특화된 LLM API다.** 법률·금융·의료처럼 한국어 뉘앙스가 중요한 도메인에 유리하다.",
        "이 장의 핵심: **한국어 RAG는 임베딩·검색·생성 각 단계를 한국어 친화적 컴포넌트로 교체한다.** 조합이 달라지면 성능 프로파일이 달라진다.",
    ],
    "document-ingestion-101": [
        "이 장의 핵심: **PDF 파싱은 텍스트 레이어 추출과 레이아웃 복원 두 문제다.** 라이브러리마다 처리 방식이 달라 결과가 다르다.",
        "이 장의 핵심: **청킹 전략은 문서 유형에 따라 달라진다.** 연속된 산문·섹션 구조·테이블·코드는 각각 다른 분할 기준이 필요하다.",
        "이 장의 핵심: **메타데이터는 검색 필터의 원천이다.** 출처·날짜·섹션 정보를 청크에 붙여야 정밀한 필터 검색이 가능하다.",
        "이 장의 핵심: **증분 인덱싱은 바뀐 문서만 재처리한다.** 해시 또는 수정 시각으로 변경을 감지하고 해당 청크만 업데이트한다.",
        "이 장의 핵심: **다중 포맷 파이프라인은 포맷별 로더를 통일된 인터페이스로 추상화한다.** Document 객체 하나로 모든 포맷을 동일하게 처리한다.",
        "이 장의 핵심: **완성된 파이프라인은 수집 → 파싱 → 청킹 → 임베딩 → 인덱싱이 자동으로 이어진다.** 각 단계를 독립 모듈로 만들어야 교체와 테스트가 쉽다.",
    ],
    "llm-apps-ops-101": [
        "이 장의 핵심: **LLM 앱의 관측은 토큰·지연·오류 세 축을 동시에 봐야 한다.** 로그만으로는 실제 품질을 알 수 없고 트레이스가 필요하다.",
        "이 장의 핵심: **LLM 비용은 토큰 수 × 단가다.** 모델별 단가·입출력 비율·캐시 히트율을 추적해야 예산을 제어할 수 있다.",
        "이 장의 핵심: **LLM 평가는 정답이 없는 출력을 점수로 만드는 것이다.** 참조 기반·LLM-as-judge·사람 평가를 목적에 맞게 조합한다.",
        "이 장의 핵심: **LLM 앱의 보안 위협은 Prompt Injection이 가장 흔하다.** 입력 검증·출력 필터·권한 분리가 기본 방어선이다.",
        "이 장의 핵심: **배포는 모델 버전·프롬프트 버전·코드 버전을 함께 관리하는 것이다.** 세 버전이 어긋나면 재현 불가능한 버그가 생긴다.",
        "이 장의 핵심: **LLMOps는 개발·배포·모니터링·재학습 루프를 자동화한다.** 피드백을 수집하고 지표가 떨어지면 트리거가 울려야 한다.",
    ],
    "rag-benchmark-101": [
        "이 장의 핵심: **RAG 평가는 검색 품질과 생성 품질을 분리해서 측정한다.** Recall@k가 검색을, Faithfulness·Answer Relevancy가 생성을 평가한다.",
        "이 장의 핵심: **검색 벤치마크는 같은 질문셋으로 리트리버를 교체하며 비교한다.** Precision@k·MRR·NDCG가 핵심 지표다.",
        "이 장의 핵심: **임베딩 비교는 동일한 코퍼스에서 같은 쿼리로 순위를 측정한다.** 모델마다 강한 도메인이 다르다.",
        "이 장의 핵심: **VectorDB 선택은 규모·지연·정확도 트레이드오프다.** FAISS·Chroma·Qdrant·Pinecone은 각자 다른 운영 특성을 가진다.",
        "이 장의 핵심: **End-to-End 평가는 질문 → 검색 → 생성 전 과정을 하나의 점수로 본다.** 병목이 어느 단계인지 찾아야 개선 방향이 보인다.",
        "이 장의 핵심: **벤치마크는 재현 가능해야 한다.** 데이터셋·모델 버전·파라미터를 고정하고 실험을 자동화해야 비교가 의미 있다.",
    ],
    "langgraph-101": [
        "이 장의 핵심: **LangGraph는 에이전트 흐름을 그래프로 표현한다.** 노드(함수)와 엣지(전환 조건)로 복잡한 루프와 분기를 명시적으로 정의한다.",
        "이 장의 핵심: **State는 그래프 전체가 공유하는 딕셔너리다.** 각 노드는 State를 읽고 업데이트하며, Checkpoint가 이를 저장한다.",
        "이 장의 핵심: **조건부 엣지는 State를 보고 다음 노드를 결정한다.** 함수가 문자열을 반환하면 그래프가 그 키에 해당하는 노드로 이동한다.",
        "이 장의 핵심: **Tool Calling Agent는 Thought → Action → Observation 루프다.** LangGraph에서는 이 루프가 노드와 엣지로 명시적으로 보인다.",
        "이 장의 핵심: **Multi-Agent는 여러 그래프가 메시지를 주고받는 것이다.** Supervisor가 Task를 분배하고 Sub-Agent가 각자 처리한다.",
        "이 장의 핵심: **LangGraph 앱의 핵심은 State 설계다.** 무엇을 공유하고 무엇을 격리할지 결정하면 나머지는 따라온다.",
    ],
    "llm-finetuning-101": [
        "이 장의 핵심: **Fine-tuning은 사전학습 모델의 가중치를 특정 태스크로 조정하는 것이다.** 전체 학습보다 훨씬 적은 데이터와 연산으로 도메인 특화 성능을 얻는다.",
        "이 장의 핵심: **데이터셋 품질이 fine-tuning 결과를 결정한다.** 양보다 일관성 있는 형식과 레이블 정확도가 더 중요하다.",
        "이 장의 핵심: **LoRA는 원본 가중치를 고정하고 저랭크 행렬만 학습한다.** 파라미터 수를 1% 이하로 줄이면서 성능은 유지한다.",
        "이 장의 핵심: **학습 루프는 손실이 수렴할 때까지 배치를 반복한다.** Learning Rate와 배치 크기가 수렴 속도와 안정성을 결정한다.",
        "이 장의 핵심: **평가는 Perplexity·BLEU보다 태스크 특화 지표가 중요하다.** 모델이 원하는 형식으로 답하는지가 핵심이다.",
        "이 장의 핵심: **Serving은 모델 가중치와 LoRA 어댑터를 함께 로드하는 것이다.** vLLM·Ollama가 추론 서버 역할을 한다.",
    ],
}

EN_INTRO_TEMPLATES = {
    "rag-deep-dive": [
        "**The key idea**: chunk quality determines RAG performance. What the loader reads and the TextSplitter splits is the first variable in retrieval accuracy.",
        "**The key idea**: embeddings turn text into distances. Similar meanings end up close in vector space, and FAISS finds those distances fast.",
        "**The key idea**: a retriever encapsulates a search strategy. The same VectorStore returns different results depending on which `search_type` you attach.",
        "**The key idea**: a prompt is the glue between context and question. PromptTemplate turns two inputs into a single LLM call.",
        "**The key idea**: an LCEL pipe connects components in order. `retriever | prompt | llm | parser` in one line is a complete RAG chain.",
        "**The key idea**: without evaluation metrics there is no improvement direction. RAGAS faithfulness, relevancy, and precision turn RAG quality into numbers.",
    ],
    "langchain-101": [
        "**The key idea**: LangChain connects components with the pipe operator (`|`). The Runnable interface is the shared language of every component.",
        "**The key idea**: Prompt + LLM is the simplest possible chain. ChatPromptTemplate structures the input and the LLM returns a response.",
        "**The key idea**: a Retriever takes a question and returns relevant documents. It abstracts a VectorStore into a search interface.",
        "**The key idea**: Tool Calling lets the model choose which function to call. The code executes it and returns the result back to the model.",
        "**The key idea**: Streaming sends tokens as they are generated. `stream()` returns a generator and the client receives output in real time.",
        "**The key idea**: a production chain is a composition of retriever, prompt, LLM, and parser. Each component can be swapped independently.",
    ],
    "llm-app-foundations-101": [
        "**The key idea**: an LLM API call is a single HTTP POST. Send messages, receive text — that is the entire contract.",
        "**The key idea**: a token is the smallest unit a model reads. Character count and token count differ; cost and context limits are denominated in tokens.",
        "**The key idea**: prompt structure determines response quality. The System / User / Assistant role split is the primary control lever.",
        "**The key idea**: few-shot examples show the model a pattern. Chain-of-Thought exposes intermediate reasoning steps so the model can solve harder problems.",
        "**The key idea**: conversation state is a list of messages you manage yourself. The model is stateless — you must send the full history on every call.",
        "**The key idea**: streaming delivers tokens as they are produced. Users see output immediately instead of waiting for the full response.",
    ],
    "llm-api-production-101": [
        "**The key idea**: Structured Output constrains the model to a JSON schema. A Pydantic model locks the output shape and eliminates parsing errors.",
        "**The key idea**: Tool Calling lets the model choose a function name and arguments. The code runs it; the result goes back to the model.",
        "**The key idea**: streaming eliminates time-to-first-token (TTFT). The longer the response, the greater the perceived speed improvement.",
        "**The key idea**: caching means never sending the same input twice. Semantic cache extends this to similar — not just identical — questions.",
        "**The key idea**: retry with exponential backoff absorbs transient errors. Controlling retry count and interval handles most 429 and 503 responses.",
        "**The key idea**: rate limits hit on two axes — tokens per minute and requests per minute. Track both and use a queue to smooth the load.",
    ],
    "vector-search-101": [
        "**The key idea**: an embedding compresses text into a high-dimensional vector. Sentences with similar meaning land close together in that space.",
        "**The key idea**: HuggingFace embeddings run locally for free. `sentence-transformers` downloads the model and returns vectors.",
        "**The key idea**: cosine similarity measures the alignment of two vector directions. It ignores magnitude, so sentence length differences do not matter.",
        "**The key idea**: FAISS finds vectors fast. IndexFlatL2 is the simplest option; switch to IVF or HNSW when the dataset grows.",
        "**The key idea**: chunk size and overlap control retrieval quality. Too large adds noise; too small loses context.",
        "**The key idea**: a vector search pipeline is four steps — embed, index, query, retrieve. Each step should be independently replaceable.",
    ],
    "ai-app-patterns-101": [
        "**The key idea**: a chatbot is a loop that accumulates message history. How you manage that history determines response quality and cost.",
        "**The key idea**: RAG Q&A is retrieve → inject → generate. Find relevant documents, put them in context, then generate an answer.",
        "**The key idea**: a document assistant turns long text into short structure. Summarization, extraction, and classification are all variations on the same Prompt-LLM pipe.",
        "**The key idea**: an agent delegates tool selection to the model. The ReAct loop cycles through Thought → Action → Observation.",
        "**The key idea**: a workflow is an agent with fixed steps. Explicit branches and loops make behavior predictable.",
        "**The key idea**: Human-in-the-loop inserts a person at uncertain decision points. The design challenge is deciding when to intervene.",
    ],
    "korean-ai-stack-101": [
        "**The key idea**: Korean embedding models compress Korean sentence meaning into vectors. KoSimCSE, BGE-M3, and Solar each take a different approach.",
        "**The key idea**: KoSimCSE uses contrastive learning to capture Korean similarity. Same-meaning sentence pairs are pushed together; different ones are pushed apart.",
        "**The key idea**: BGE-M3 handles multiple languages in a single model. Korean and English share the same vector space, enabling cross-lingual retrieval.",
        "**The key idea**: CLOVA OCR extracts text from images. It turns scanned documents, receipts, and business cards into structured text for RAG pipelines.",
        "**The key idea**: HyperCLOVA X and Solar are LLM APIs specialized for Korean. They are advantageous in domains where Korean nuance matters.",
        "**The key idea**: a Korean RAG pipeline swaps each stage for a Korean-friendly component. Different combinations produce different performance profiles.",
    ],
    "document-ingestion-101": [
        "**The key idea**: PDF parsing is two problems — extracting the text layer and reconstructing layout. Different libraries produce different results.",
        "**The key idea**: chunking strategy depends on document type. Continuous prose, sectioned docs, tables, and code each need different split criteria.",
        "**The key idea**: metadata is the source of search filters. Attaching source, date, and section info to each chunk enables precise filtered retrieval.",
        "**The key idea**: incremental indexing reprocesses only changed documents. Hash or modification time detects changes; only the affected chunks are updated.",
        "**The key idea**: a multi-format pipeline abstracts format-specific loaders behind a unified interface. One Document object handles every format the same way.",
        "**The key idea**: a complete pipeline runs ingest → parse → chunk → embed → index automatically. Independent modules make each stage replaceable and testable.",
    ],
    "llm-apps-ops-101": [
        "**The key idea**: observing an LLM app means watching tokens, latency, and errors together. Logs alone are not enough; you need traces.",
        "**The key idea**: LLM cost is token count × price per token. Track per-model pricing, input/output ratio, and cache hit rate to control the budget.",
        "**The key idea**: LLM evaluation turns open-ended output into scores. Combine reference-based, LLM-as-judge, and human evaluation based on the goal.",
        "**The key idea**: the most common LLM security threat is Prompt Injection. Input validation, output filtering, and permission separation are the baseline defenses.",
        "**The key idea**: deployment means managing model version, prompt version, and code version together. Misalignment across the three creates irreproducible bugs.",
        "**The key idea**: LLMOps automates the develop → deploy → monitor → retrain loop. Collect feedback and trigger alerts when metrics degrade.",
    ],
    "rag-benchmark-101": [
        "**The key idea**: RAG evaluation separates retrieval quality from generation quality. Recall@k measures retrieval; Faithfulness and Answer Relevancy measure generation.",
        "**The key idea**: a retrieval benchmark swaps retrievers on the same question set. Precision@k, MRR, and NDCG are the core metrics.",
        "**The key idea**: embedding comparison runs the same queries on the same corpus with different models. Each model has domain strengths.",
        "**The key idea**: VectorDB selection is a tradeoff among scale, latency, and accuracy. FAISS, Chroma, Qdrant, and Pinecone have different operational profiles.",
        "**The key idea**: end-to-end evaluation scores the full pipeline from question to generated answer. You need to pinpoint which stage is the bottleneck.",
        "**The key idea**: benchmarks must be reproducible. Fix the dataset, model versions, and parameters, and automate the experiment so comparisons are meaningful.",
    ],
    "langgraph-101": [
        "**The key idea**: LangGraph represents agent flow as a graph. Nodes (functions) and edges (transition conditions) define loops and branches explicitly.",
        "**The key idea**: State is a dictionary shared across the entire graph. Each node reads and updates it; Checkpoints persist it.",
        "**The key idea**: a conditional edge inspects State and decides the next node. The function returns a string key; the graph routes to the matching node.",
        "**The key idea**: a Tool Calling Agent loops through Thought → Action → Observation. In LangGraph that loop is visible as nodes and edges.",
        "**The key idea**: Multi-Agent is multiple graphs exchanging messages. A Supervisor distributes tasks and Sub-Agents handle each one.",
        "**The key idea**: the heart of a LangGraph app is State design. Decide what to share and what to isolate; everything else follows.",
    ],
    "llm-finetuning-101": [
        "**The key idea**: fine-tuning adjusts a pretrained model's weights for a specific task. Far less data and compute than pretraining; domain-specific performance is the payoff.",
        "**The key idea**: dataset quality determines fine-tuning results. Consistent format and accurate labels matter more than volume.",
        "**The key idea**: LoRA freezes the original weights and trains only low-rank matrices. Under 1% of parameters are updated; performance holds.",
        "**The key idea**: the training loop repeats batches until loss converges. Learning rate and batch size control convergence speed and stability.",
        "**The key idea**: task-specific metrics matter more than perplexity or BLEU. The real test is whether the model answers in the expected format.",
        "**The key idea**: serving means loading the base model weights together with the LoRA adapter. vLLM and Ollama act as inference servers.",
    ],
}

SKIP_KEYWORDS_KO = ["멘탈 모델", "한 문장 정의", "한 문장 결론", "핵심:", "이 장의 핵심"]
SKIP_KEYWORDS_EN = ["The key idea", "mental model", "one-sentence", "key takeaway"]

FRONTMATTER_RE = re.compile(r"^---\n.*?\n---\n", re.DOTALL)


def needs_mental_model(text: str, lang: str) -> bool:
    keywords = SKIP_KEYWORDS_KO if lang == "ko" else SKIP_KEYWORDS_EN
    return not any(kw in text for kw in keywords)


def find_first_h2(lines: list[str], start: int) -> int:
    for i in range(start, len(lines)):
        if lines[i].strip().startswith("## "):
            return i
    return -1


def find_h1(lines: list[str]) -> int:
    in_fm = False
    fm_count = 0
    for i, line in enumerate(lines):
        s = line.strip()
        if s == "---" and i == 0:
            in_fm = True
            fm_count += 1
            continue
        if in_fm and s == "---":
            fm_count += 1
            if fm_count == 2:
                in_fm = False
            continue
        if not in_fm:
            if s.startswith("# ") and not s.startswith("## "):
                return i
    return -1


def insert_mental_model(path: Path, intro: str) -> bool:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)

    h1_idx = find_h1(lines)
    if h1_idx == -1:
        return False

    h2_idx = find_first_h2(lines, h1_idx + 1)
    insert_at = h2_idx if h2_idx != -1 else h1_idx + 2

    new_line = f"\n{intro}\n\n"
    new_lines = lines[:insert_at] + [new_line] + lines[insert_at:]
    path.write_text("".join(new_lines), encoding="utf-8")
    return True


def process_series(series_id: str, series_dir: Path):
    ko_templates = KO_INTRO_TEMPLATES.get(series_id, [])
    en_templates = EN_INTRO_TEMPLATES.get(series_id, [])

    for lang, templates, lang_dir in [
        ("ko", ko_templates, series_dir / "ko"),
        ("en", en_templates, series_dir / "en"),
    ]:
        if not lang_dir.is_dir() or not templates:
            continue
        files = sorted(f for f in lang_dir.iterdir() if f.suffix == ".md")
        modified = skipped = 0
        for i, path in enumerate(files):
            if i >= len(templates):
                break
            text = path.read_text(encoding="utf-8")
            if not needs_mental_model(text, lang):
                skipped += 1
                continue
            if insert_mental_model(path, templates[i]):
                print(f"  + {lang}/{path.name}")
                modified += 1
            else:
                skipped += 1
        print(f"  {lang}: {modified} modified, {skipped} skipped")


def main():
    target_series = list(KO_INTRO_TEMPLATES.keys())
    for series_id in target_series:
        series_dir = REPO / "content" / series_id
        if not series_dir.is_dir():
            print(f"[SKIP] {series_id}")
            continue
        print(f"\n[{series_id}]")
        process_series(series_id, series_dir)


if __name__ == "__main__":
    main()
