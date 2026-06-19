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


# 사용 예시
count = index_document("product_manual.txt", "manual_v1")
print(f"Indexed {count} chunks")
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
컨텍스트에 없는 내용은 "제공된 문서에서 해당 정보를 찾을 수 없습니다"라고 답하세요."""


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
                "chunk_index": meta.get("chunk_index", 0),
                "similarity": 1 - dist,  # distance를 유사도로 변환
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
            "answer": "관련 문서를 찾을 수 없습니다.",
            "sources": [],
            "chunks_used": 0,
        }

    context = "\n\n---\n\n".join(
        f"[출처: {c['source']} 청크 {c['chunk_index']}]\n{c['content']}"
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
    }
```

## 실습 3: 검색 품질 검증

검색된 청크가 실제로 질문에 관련 있는지 LLM으로 2차 검증합니다.

```python
from openai import OpenAI

client = OpenAI()


def validate_relevance(query: str, chunk: str) -> tuple[bool, float]:
    """LLM을 사용해 청크가 질문과 관련 있는지 검증합니다."""
    prompt = f"""다음 텍스트 청크가 질문에 답하는 데 도움이 되는지 판단하세요.

질문: {query}

청크:
{chunk}

JSON으로만 응답하세요: {{"relevant": true/false, "confidence": 0.0-1.0, "reason": "한 줄 이유"}}"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=128,
        response_format={"type": "json_object"},
    )

    import json
    result = json.loads(response.choices[0].message.content)
    return result.get("relevant", False), result.get("confidence", 0.0)


def retrieve_and_validate(
    query: str,
    top_k: int = 8,
    min_similarity: float = 0.4,
    validate: bool = True,
) -> list[dict]:
    """검색 후 LLM 검증으로 관련 청크만 남깁니다."""
    chunks = retrieve_chunks(query, top_k)
    filtered = [c for c in chunks if c["similarity"] >= min_similarity]

    if not validate:
        return filtered

    validated = []
    for chunk in filtered:
        relevant, confidence = validate_relevance(query, chunk["content"])
        if relevant and confidence >= 0.6:
            chunk["llm_confidence"] = confidence
            validated.append(chunk)

    return validated
```

## 운영 체크리스트

- [ ] 청크 크기와 오버랩이 도메인 문서 특성에 맞게 설정되었습니다.
- [ ] 임베딩 모델이 영어/한국어 혼합 문서를 충분히 처리합니다.
- [ ] 검색 결과에 유사도 임계값 필터가 적용되어 있습니다.
- [ ] 답변에 출처 정보가 항상 포함됩니다.
- [ ] 문서 업데이트 시 인덱스 재생성 파이프라인이 자동화되어 있습니다.

## 자주 하는 실수

| 실수 | 증상 | 해결 방법 |
|---|---|---|
| 청크 오버랩 없이 분할 | 문장이 잘린 청크로 맥락 손실 | 50-100 토큰 오버랩 적용 |
| 유사도 임계값 없음 | 관련 없는 청크가 컨텍스트에 포함 | min_similarity 0.4-0.6으로 필터링 |
| 출처 정보 미반환 | 답변 신뢰성 저하, 검증 불가 | 모든 답변에 source 메타데이터 포함 |
| 인덱스 자동 갱신 미구현 | 최신 문서가 검색에 반영 안 됨 | 문서 변경 시 재인덱싱 트리거 구현 |
| Top-K만 사용, 재순위화 없음 | 관련도 낮은 청크가 상위에 오름 | Cross-encoder reranker 추가 검토 |

## 처음 질문으로 돌아가기

- **오프라인 인덱싱과 온라인 QA는 왜 분리해서 설계해야 할까요?**
  인덱싱은 비용이 높고 시간이 걸리는 작업이므로 문서 변경 시에만 실행합니다. 온라인 QA는 실시간 요청을 처리하므로 레이턴시가 낮아야 합니다. 두 파이프라인을 분리하면 인덱싱 실패가 서비스 응답에 영향을 주지 않습니다.

- **검색된 청크가 질문에 관련 있는지 어떻게 검증할 수 있을까요?**
  벡터 유사도 임계값으로 1차 필터링하고, LLM 기반 관련성 판단으로 2차 검증합니다. 두 단계 필터를 적용하면 노이즈 청크가 컨텍스트에 포함되는 문제를 크게 줄일 수 있습니다.

- **답변에 출처를 함께 반환하려면 어떤 구조가 필요할까요?**
  청크 메타데이터에 source, chunk_index를 저장하고, 답변 생성 후 사용된 청크의 출처를 집합으로 추출해 반환합니다. 사용자가 원본 문서를 직접 확인할 수 있어야 신뢰도가 높아집니다.

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
