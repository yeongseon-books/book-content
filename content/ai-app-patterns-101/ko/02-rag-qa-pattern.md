---
series: ai-app-patterns-101
episode: 2
title: "AI App Patterns 101 (2/6): RAG QA 패턴"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - RAG
  - VectorSearch
  - LLM
  - DocumentQA
  - Retrieval
seo_description: 오프라인 인덱싱과 온라인 QA 파이프라인, 검색 품질 검증, 출처 귀속까지 RAG 문서 QA 패턴의 핵심을 정리합니다
last_reviewed: '2026-06-20'
---

# AI App Patterns 101 (2/6): RAG QA 패턴

LLM은 훈련 데이터 범위 밖의 질문에는 정확히 답하지 못합니다. 사내 문서, 최신 제품 매뉴얼, 내부 정책처럼 모델이 본 적 없는 정보를 다루려면 RAG(Retrieval-Augmented Generation)가 필요합니다. RAG는 질문이 들어오면 먼저 관련 문서 청크를 검색하고, 그 내용을 컨텍스트에 포함해 LLM이 답변을 생성하게 하는 패턴입니다.

RAG를 "더 똑똑한 LLM"으로 보면 설계가 흐려집니다. RAG의 핵심은 모델 능력이 아니라, 적절한 청크를 적절한 시점에 찾아 주입하는 검색 파이프라인에 있습니다. 답변 품질을 높이려면 프롬프트보다 청크 품질과 검색 전략을 먼저 살펴야 합니다.

이 글은 AI App Patterns 101 시리즈의 2번째 글입니다.

![RAG QA 패턴 개요](https://yeongseon-books.github.io/book-public-assets/assets/ai-app-patterns-101/02/02-01-concept-at-a-glance.ko.png)
*오프라인 인덱싱과 온라인 검색 생성을 분리하는 RAG 파이프라인 구조*

## 이 글에서 다룰 문제

- 오프라인 인덱싱과 온라인 QA는 왜 분리해서 설계해야 할까요?
- 검색된 청크가 실제로 질문에 관련 있는지 어떻게 검증할 수 있을까요?
- 답변에 출처를 함께 반환하려면 어떤 구조가 필요할까요?
- 청크 크기와 오버랩은 검색 품질에 어떤 영향을 미칠까요?
- 프로덕션 RAG에서 반드시 모니터링해야 할 지표는 무엇일까요?

## 핵심 개념 한 줄 정리

- **Chunking**: 긴 문서를 LLM 컨텍스트에 들어갈 수 있는 크기로 분할하는 작업입니다.
- **Embedding**: 텍스트를 의미 유사도 검색이 가능한 벡터로 변환하는 과정입니다.
- **Vector Store**: 임베딩 벡터를 저장하고 ANN 검색을 제공하는 데이터베이스입니다.
- **Retrieval**: 질문 임베딩과 가장 유사한 청크를 찾아오는 단계입니다.
- **Source Attribution**: 답변에 사용된 원본 문서와 위치를 명시하는 설계 원칙입니다.

## RAG 구성요소 비교

| 구성요소 | 선택지 | 트레이드오프 |
|---|---|---|
| Chunking 전략 | Fixed size / Semantic / Recursive | Fixed size는 단순하지만 의미 경계를 무시할 수 있음 |
| 임베딩 모델 | text-embedding-3-small / BGE / E5 | 더 큰 모델은 품질이 높지만 비용과 레이턴시 증가 |
| Vector Store | ChromaDB / Pinecone / Weaviate / pgvector | 오픈소스 vs 관리형 서비스 트레이드오프 |
| 재순위화 | Cross-encoder reranker | 검색 품질 향상, 레이턴시 추가 |
| 컨텍스트 조립 | Top-K / MMR / HyDE | 다양성과 관련성 균형 |

## 구체적인 시나리오: 사내 HR 정책 QA 봇

회사 직원들이 "연차 신청은 어떻게 하나요?", "재택근무 규정이 어떻게 되나요?"처럼 내부 정책을 자주 묻습니다. HR 팀이 수동으로 답변하는 데 하루 2시간을 씁니다. RAG를 적용하면 정책 문서를 인덱싱해 두고, 질문이 들어올 때마다 관련 조항을 검색해 답변을 생성합니다.

핵심 설계 결정:
- 청크 크기: 정책 조항 단위 (300~512자)
- 오버랩: 64자 — 조항 경계에서 맥락이 잘리지 않도록
- 폴백 기준: 관련도 0.50 미만 시 "해당 정책을 문서에서 찾을 수 없습니다" 반환
- 출처 표시: 답변마다 참조 문서명과 청크 인덱스 명시

## 실습 1: 오프라인 인덱싱 파이프라인

문서를 수집해 청크로 분할하고, 임베딩해 벡터 스토어에 저장하는 단계입니다. 이 파이프라인은 문서가 변경될 때마다 실행합니다.

```python
from pathlib import Path
from openai import OpenAI
import chromadb
from chromadb.utils import embedding_functions

client = OpenAI()
chroma_client = chromadb.PersistentClient(path="./chroma_db")

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    model_name="text-embedding-3-small",
)
collection = chroma_client.get_or_create_collection(
    name="documents",
    embedding_function=openai_ef,
)


def chunk_text(text: str, chunk_size: int = 512, overlap: int = 64) -> list[str]:
    """텍스트를 겹치는 청크로 분할합니다."""
    words = text.split()
    chunks = []
    step = chunk_size - overlap
    for i in range(0, len(words), step):
        chunk = " ".join(words[i : i + chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks


def index_document(doc_path: str, doc_id: str) -> int:
    """문서를 청크로 분할해 벡터 스토어에 인덱싱합니다."""
    text = Path(doc_path).read_text(encoding="utf-8")
    chunks = chunk_text(text)

    collection.add(
        documents=chunks,
        ids=[f"{doc_id}_{i}" for i in range(len(chunks))],
        metadatas=[
            {"source": doc_path, "chunk_index": i, "doc_id": doc_id}
            for i in range(len(chunks))
        ],
    )
    return len(chunks)


# 사내 HR 정책 문서 인덱싱
# count = index_document("hr_policy.txt", "hr_policy_v2")
# print(f"인덱싱 완료: {count}개 청크")


# 인메모리 테스트용: 텍스트를 직접 인덱싱
sample_docs = [
    {
        "text": "연차 유급휴가는 입사 1년 미만은 1개월 개근 시 1일 발생합니다. 입사 1년 이상부터는 연간 15일이 주어집니다. 연차 신청은 결재 시스템에서 최소 3일 전에 제출해야 합니다.",
        "id": "hr_001",
        "metadata": {"source": "hr_leave_policy.txt", "section": "연차"},
    },
    {
        "text": "재택근무는 직무별 허용 비율이 다릅니다. 개발직군은 주 3일, 운영직군은 주 2일까지 재택이 허용됩니다. 재택근무 신청은 팀장 사전 승인이 필요합니다.",
        "id": "hr_002",
        "metadata": {"source": "remote_work_policy.txt", "section": "재택근무"},
    },
    {
        "text": "출장 경비는 교통비, 숙박비, 식비로 구분됩니다. 국내 출장 식비는 1일 3만원, 숙박비는 1박 10만원을 지원합니다. 출장 보고서는 복귀 후 5일 이내 제출해야 합니다.",
        "id": "hr_003",
        "metadata": {"source": "travel_expense_policy.txt", "section": "출장경비"},
    },
]

collection.add(
    documents=[d["text"] for d in sample_docs],
    ids=[d["id"] for d in sample_docs],
    metadatas=[d["metadata"] for d in sample_docs],
)
print(f"샘플 문서 {len(sample_docs)}개 인덱싱 완료")
```

## 실습 2: 온라인 QA 파이프라인

질문이 들어오면 관련 청크를 검색하고, 컨텍스트를 조립해 LLM으로 답변을 생성합니다.

```python
from openai import OpenAI
import chromadb
from chromadb.utils import embedding_functions

client = OpenAI()
chroma_client = chromadb.PersistentClient(path="./chroma_db")
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    model_name="text-embedding-3-small",
)
collection = chroma_client.get_collection(
    name="documents",
    embedding_function=openai_ef,
)

RAG_SYSTEM_PROMPT = """당신은 제공된 문서를 기반으로 질문에 답하는 어시스턴트입니다.
답변은 반드시 제공된 컨텍스트에 근거해야 합니다.
컨텍스트에 없는 내용은 '제공된 문서에서 해당 정보를 찾을 수 없습니다'라고 답하세요.
추측하거나 외부 지식을 사용하지 마세요."""


def retrieve_chunks(query: str, top_k: int = 5) -> list[dict]:
    """질문과 가장 관련 있는 청크를 검색합니다."""
    results = collection.query(
        query_texts=[query],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )
    chunks = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        chunks.append(
            {
                "content": doc,
                "source": meta.get("source", "unknown"),
                "section": meta.get("section", ""),
                "chunk_index": meta.get("chunk_index", 0),
                "similarity": 1 - dist,
            }
        )
    return chunks


def answer_with_sources(
    query: str,
    top_k: int = 5,
    min_similarity: float = 0.5,
) -> dict:
    """검색 기반으로 답변을 생성하고 출처를 함께 반환합니다."""
    chunks = retrieve_chunks(query, top_k)

    # 낮은 유사도 청크 필터링
    relevant = [c for c in chunks if c["similarity"] >= min_similarity]
    if not relevant:
        return {
            "answer": "관련 문서를 찾을 수 없습니다. 질문을 구체적으로 바꿔 다시 시도해 주세요.",
            "sources": [],
            "chunks_used": 0,
            "top_similarity": chunks[0]["similarity"] if chunks else None,
        }

    context = "\n\n---\n\n".join(
        f"[출처: {c['source']} | 섹션: {c['section']}]\n{c['content']}"
        for c in relevant
    )

    messages = [
        {"role": "system", "content": RAG_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"컨텍스트:\n{context}\n\n질문: {query}",
        },
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=1024,
    )

    return {
        "answer": response.choices[0].message.content,
        "sources": list({c["source"] for c in relevant}),
        "chunks_used": len(relevant),
        "top_similarity": relevant[0]["similarity"],
    }


# QA 파이프라인 테스트
test_questions = [
    "연차는 어떻게 신청하나요?",
    "재택근무 일수 제한이 있나요?",
    "출장 식비는 얼마나 지원되나요?",
    "복지 포인트는 어떻게 사용하나요?",  # 문서에 없음
]

for q in test_questions:
    result = answer_with_sources(q)
    print(f"\n질문: {q}")
    print(f"답변: {result['answer'][:100]}...")
    print(f"출처: {result['sources']}")
    print(f"유사도: {result['top_similarity']:.3f}")
```

## 실습 3: 검색 품질 검증

검색된 청크가 실제로 질문에 관련 있는지 LLM으로 2차 검증합니다. 이 단계는 노이즈 청크가 컨텍스트를 오염시키는 것을 방지합니다.

```python
import json
from openai import OpenAI

client = OpenAI()


def validate_relevance(query: str, chunk: str) -> tuple[bool, float, str]:
    """LLM으로 청크가 질문과 관련 있는지 판단합니다."""
    prompt = f"""다음 텍스트 청크가 질문에 답하는 데 도움이 되는지 판단하세요.

질문: {query}

청크:
{chunk}

JSON으로만 응답하세요:
{{"relevant": true/false, "confidence": 0.0-1.0, "reason": "한 줄 이유"}}"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=128,
        response_format={"type": "json_object"},
    )

    result = json.loads(response.choices[0].message.content)
    return (
        result.get("relevant", False),
        result.get("confidence", 0.0),
        result.get("reason", ""),
    )


def retrieve_and_validate(
    query: str,
    top_k: int = 8,
    min_similarity: float = 0.4,
    min_llm_confidence: float = 0.6,
) -> list[dict]:
    """벡터 검색 후 LLM 검증으로 관련 청크만 남깁니다."""
    chunks = retrieve_chunks(query, top_k)
    filtered = [c for c in chunks if c["similarity"] >= min_similarity]

    validated = []
    for chunk in filtered:
        relevant, confidence, reason = validate_relevance(query, chunk["content"])
        if relevant and confidence >= min_llm_confidence:
            chunk["llm_confidence"] = confidence
            chunk["llm_reason"] = reason
            validated.append(chunk)

    return validated


# 검증 결과 비교
query = "재택근무 신청 절차"
raw_chunks = retrieve_chunks(query, top_k=5)
validated_chunks = retrieve_and_validate(query, top_k=5)

print(f"벡터 검색 결과: {len(raw_chunks)}개")
print(f"LLM 검증 후: {len(validated_chunks)}개")
for c in validated_chunks:
    print(f"  - {c['source']}: 벡터={c['similarity']:.3f}, LLM={c['llm_confidence']:.3f}")
```

## 실습 4: 검색 품질 측정

QA 품질을 수치로 추적하면 프롬프트 변경이나 임베딩 모델 교체가 실제로 도움이 됐는지 알 수 있습니다.

```python
def evaluate_retrieval(
    eval_dataset: list[dict],
    retriever_fn,
    top_k: int = 5,
) -> dict:
    """검색 품질을 Hit@K와 MRR로 측정합니다.

    eval_dataset 형식:
    [{"question": "...", "gold_source": "hr_leave_policy.txt"}, ...]
    """
    hits = 0
    reciprocal_ranks = []

    for item in eval_dataset:
        chunks = retriever_fn(item["question"], top_k)
        rank = None
        for i, c in enumerate(chunks, start=1):
            if c["source"] == item["gold_source"]:
                rank = i
                break
        if rank:
            hits += 1
            reciprocal_ranks.append(1 / rank)
        else:
            reciprocal_ranks.append(0.0)

    total = len(eval_dataset)
    return {
        f"hit_at_{top_k}": hits / total,
        "mrr": sum(reciprocal_ranks) / total,
        "total_queries": total,
    }


# 평가 데이터셋
eval_set = [
    {"question": "연차 신청 방법", "gold_source": "hr_leave_policy.txt"},
    {"question": "재택근무 일수", "gold_source": "remote_work_policy.txt"},
    {"question": "출장 식비 지원", "gold_source": "travel_expense_policy.txt"},
]

metrics = evaluate_retrieval(eval_set, retrieve_chunks)
print(f"Hit@5: {metrics['hit_at_5']:.2%}")
print(f"MRR: {metrics['mrr']:.3f}")
```

## 청크 크기 실험: 최적 설정 찾기

청크 크기와 오버랩은 "설정 한 번 하고 잊는" 값이 아닙니다. 도메인에 따라 달라지며, 직접 실험해서 찾아야 합니다.

```python
def test_chunk_configs(
    text: str,
    query: str,
    configs: list[dict],
) -> None:
    """다양한 청크 설정의 검색 품질을 비교합니다."""
    for config in configs:
        size = config["chunk_size"]
        overlap = config["overlap"]
        chunks = chunk_text(text, chunk_size=size, overlap=overlap)

        # 임시 컬렉션에 인덱싱
        temp_name = f"test_c{size}_o{overlap}"
        # ... 실제 구현에서는 임시 컬렉션 생성/삭제
        print(f"chunk_size={size}, overlap={overlap}: {len(chunks)}개 청크")


# 실험할 설정
configs = [
    {"chunk_size": 256, "overlap": 32},
    {"chunk_size": 512, "overlap": 64},
    {"chunk_size": 1024, "overlap": 128},
]
```

일반적으로 짧은 정책 조항이나 FAQ는 작은 청크(256~512), 긴 기술 문서나 논문은 큰 청크(512~1024)가 더 좋은 결과를 냅니다.

## FastAPI RAG 엔드포인트

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class QARequest(BaseModel):
    question: str
    top_k: int = 5
    min_similarity: float = 0.5


class QAResponse(BaseModel):
    answer: str
    sources: list[str]
    chunks_used: int
    top_similarity: float | None
    route: str  # "answer" | "fallback"


@app.post("/rag/qa", response_model=QAResponse)
def rag_qa(req: QARequest):
    result = answer_with_sources(
        query=req.question,
        top_k=req.top_k,
        min_similarity=req.min_similarity,
    )
    route = "answer" if result["chunks_used"] > 0 else "fallback"
    return QAResponse(
        answer=result["answer"],
        sources=result["sources"],
        chunks_used=result["chunks_used"],
        top_similarity=result.get("top_similarity"),
        route=route,
    )
```

## 재인덱싱 전략

```text
트리거 1: 문서 변경 건수 >= 50건
트리거 2: 핵심 정책 문서 업데이트 발생
트리거 3: hit_at_5가 최근 7일 평균 대비 10%p 하락
실행: 변경된 source만 증분 재인덱싱
```

이 정책이 없으면 RAG는 초기에 잘 동작하다가, 문서 현실과 인덱스 현실이 어긋나는 순간 급격히 신뢰를 잃습니다.

## 운영 체크리스트

- [ ] 청크 크기와 오버랩이 도메인 문서 특성에 맞게 설정되었습니다.
- [ ] 임베딩 모델이 영어/한국어 혼합 문서를 충분히 처리합니다.
- [ ] 검색 결과에 유사도 임계값 필터가 적용되어 있습니다.
- [ ] 모든 답변에 출처(source) 정보가 포함됩니다.
- [ ] 폴백 경로에서 사용자에게 다음 행동 안내가 제공됩니다.
- [ ] 문서 업데이트 시 재인덱싱 파이프라인이 자동으로 실행됩니다.
- [ ] 검색 지표(hit@k, MRR)를 주기적으로 측정합니다.

## 자주 하는 실수

| 실수 | 증상 | 해결 방법 |
|---|---|---|
| 청크 오버랩 없이 분할 | 문장이 잘린 청크로 맥락 손실, 검색 품질 저하 | 50-100 토큰 오버랩 적용 |
| 유사도 임계값 없음 | 관련 없는 청크가 컨텍스트에 포함되어 환각 유발 | min_similarity 0.4-0.6으로 필터링 |
| 출처 정보 미반환 | 답변 신뢰성 저하, 사실 검증 불가 | 모든 답변에 source 메타데이터 포함 |
| 인덱스 자동 갱신 미구현 | 최신 문서가 검색에 반영 안 됨 | 문서 변경 시 재인덱싱 트리거 구현 |
| Top-K만 사용, 재순위화 없음 | 벡터 거리만으로 순위 결정, 관련도 낮은 청크 상위 노출 | Cross-encoder reranker 추가 검토 |
| 임베딩 모델 도메인 불일치 | 한국어 문서에 영어 임베딩 사용 시 유사도 계산 오류 | ko-sbert 등 한국어 특화 임베딩 사용 |
| 검색 지표 미측정 | 어떤 변경이 품질에 영향을 주는지 알 수 없음 | hit@k, MRR 주기적 측정 파이프라인 구축 |
| 폴백 경로 미설계 | 근거 없어도 답변 생성, 환각 위험 | MIN_SIMILARITY 이하 시 명확한 폴백 응답 반환 |

## 처음 질문으로 돌아가기

- **오프라인 인덱싱과 온라인 QA는 왜 분리해서 설계해야 할까요?**
  인덱싱은 비용이 높고 시간이 걸리는 작업이므로 문서 변경 시에만 실행합니다. 온라인 QA는 실시간 요청을 처리하므로 레이턴시가 낮아야 합니다. 두 파이프라인을 분리하면 인덱싱 실패가 서비스 응답에 영향을 주지 않습니다.

- **검색된 청크가 질문에 관련 있는지 어떻게 검증할 수 있을까요?**
  벡터 유사도 임계값으로 1차 필터링하고, 필요하면 LLM 기반 관련성 판단으로 2차 검증합니다. 두 단계 필터를 적용하면 노이즈 청크가 컨텍스트에 포함되는 문제를 크게 줄일 수 있습니다.

- **답변에 출처를 함께 반환하려면 어떤 구조가 필요할까요?**
  청크 메타데이터에 source, section, chunk_index를 저장하고, 답변 생성 후 사용된 청크의 출처를 집합으로 추출해 반환합니다. 사용자가 원본 문서를 직접 확인할 수 있어야 신뢰도가 높아집니다.

- **청크 크기와 오버랩은 검색 품질에 어떤 영향을 미칠까요?**
  청크가 너무 작으면 중요한 맥락이 분리되고, 너무 크면 관련 없는 내용이 섞입니다. 도메인에 따라 256~1024 범위에서 직접 실험하고 hit@k로 측정해야 합니다. 오버랩은 청크 경계에서 맥락이 잘리는 문제를 줄입니다.

- **프로덕션 RAG에서 반드시 모니터링해야 할 지표는 무엇일까요?**
  hit@k(정답 청크 검색 성공률), MRR(순위 품질), no_evidence_rate(폴백 비율), 평균 응답 지연 시간을 최소한 주간 단위로 추적해야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [AI App Patterns 101 (1/6): Chatbot 패턴](./01-chatbot-pattern.md)
- **AI App Patterns 101 (2/6): RAG QA 패턴 (현재 글)**
- [AI App Patterns 101 (3/6): Document Assistant 패턴](./03-document-assistant.md)
- [AI App Patterns 101 (4/6): Agent Tool 패턴](./04-agent-tool-pattern.md)
- [AI App Patterns 101 (5/6): Workflow Automation 패턴](./05-workflow-automation.md)
- [AI App Patterns 101 (6/6): Human-in-the-Loop 패턴](./06-human-in-the-loop.md)

<!-- toc:end -->

## 참고 자료

- [LangChain — RAG](https://python.langchain.com/docs/use_cases/question_answering/)
- [ChromaDB — Getting Started](https://docs.trychroma.com/getting-started)
- [OpenAI — Embeddings](https://platform.openai.com/docs/guides/embeddings)
- [RAGAS — RAG Evaluation](https://docs.ragas.io/)
- [book-examples — ai-app-patterns-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/ai-app-patterns-101/ko)

Tags: RAG, VectorSearch, LLM, DocumentQA, Retrieval
