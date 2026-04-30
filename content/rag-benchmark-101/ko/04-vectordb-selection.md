# VectorDB 선택 기준

> RAG 벤치마크 101 (4/6)

FAISS, Chroma, Qdrant — 벡터 DB마다 트레이드오프가 다릅니다. 이 포스트에서는 인덱싱 속도, 쿼리 속도, 메모리 사용량, 필터링 지원을 기준으로 FAISS와 Chroma를 직접 비교하고 선택 기준을 정립합니다.

---

## 비교 기준

벡터 DB를 선택할 때 고려해야 할 네 가지 축입니다.

- **인덱싱 속도**: 문서를 얼마나 빠르게 추가할 수 있는가
- **쿼리 속도**: 검색에 걸리는 시간
- **메모리 효율**: 코퍼스 크기 대비 RAM 점유
- **필터링 지원**: 메타데이터 기반 조건부 검색

---

## FAISS vs Chroma 벤치마크

```python
import json
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from langchain.schema import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS, Chroma

@dataclass
class VectorDBBenchResult:
    name: str
    index_time_s: float
    query_time_ms: float
    precision_at_3: float
    recall_at_3: float
    supports_filter: bool
    notes: str = ""

    def summary(self) -> dict:
        return {
            "db": self.name,
            "index_time_s": round(self.index_time_s, 2),
            "query_time_ms": round(self.query_time_ms, 1),
            "precision@3": round(self.precision_at_3, 4),
            "recall@3": round(self.recall_at_3, 4),
            "supports_filter": self.supports_filter,
            "notes": self.notes,
        }

def _get_embedding():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

def _prm(retrieved_ids: list[str], relevant_ids: set[str], k: int) -> tuple[float, float, float]:
    top_k = retrieved_ids[:k]
    hits = [d for d in top_k if d in relevant_ids]
    precision = len(hits) / k if k > 0 else 0.0
    recall = len(hits) / len(relevant_ids) if relevant_ids else 0.0
    mrr = next((1.0 / (i + 1) for i, d in enumerate(top_k) if d in relevant_ids), 0.0)
    return precision, recall, mrr

def benchmark_faiss(corpus: list[Document], queries: list, k: int = 3) -> VectorDBBenchResult:
    embedding = _get_embedding()

    t0 = time.perf_counter()
    vectorstore = FAISS.from_documents(corpus, embedding)
    index_time = time.perf_counter() - t0

    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    precisions, recalls, query_times = [], [], []

    for qt in queries:
        t0 = time.perf_counter()
        docs = retriever.invoke(qt.query)
        query_times.append((time.perf_counter() - t0) * 1000)
        ids = [d.metadata.get("id", "") for d in docs]
        p, r, _ = _prm(ids, qt.relevant_ids, k)
        precisions.append(p)
        recalls.append(r)

    def avg(lst):
        return sum(lst) / len(lst) if lst else 0.0

    return VectorDBBenchResult(
        name="FAISS",
        index_time_s=index_time,
        query_time_ms=avg(query_times),
        precision_at_3=avg(precisions),
        recall_at_3=avg(recalls),
        supports_filter=False,
        notes="메모리 상주, 영구 저장 시 직렬화 필요",
    )

def benchmark_chroma(corpus: list[Document], queries: list, k: int = 3) -> VectorDBBenchResult:
    import tempfile
    embedding = _get_embedding()

    with tempfile.TemporaryDirectory() as tmpdir:
        t0 = time.perf_counter()
        vectorstore = Chroma.from_documents(
            corpus, embedding, persist_directory=tmpdir, collection_name="bench"
        )
        index_time = time.perf_counter() - t0

        retriever = vectorstore.as_retriever(search_kwargs={"k": k})
        precisions, recalls, query_times = [], [], []

        for qt in queries:
            t0 = time.perf_counter()
            docs = retriever.invoke(qt.query)
            query_times.append((time.perf_counter() - t0) * 1000)
            ids = [d.metadata.get("id", "") for d in docs]
            p, r, _ = _prm(ids, qt.relevant_ids, k)
            precisions.append(p)
            recalls.append(r)

        def avg(lst):
            return sum(lst) / len(lst) if lst else 0.0

        return VectorDBBenchResult(
            name="Chroma",
            index_time_s=index_time,
            query_time_ms=avg(query_times),
            precision_at_3=avg(precisions),
            recall_at_3=avg(recalls),
            supports_filter=True,
            notes="SQLite 기반 영구 저장, 메타데이터 필터 지원",
        )
```

---

## 메타데이터 필터링 비교

```python
def demo_metadata_filter(corpus: list[Document]):
    """Chroma의 메타데이터 필터 vs FAISS의 후처리 필터."""
    import tempfile
    embedding = _get_embedding()
    query = "벡터 검색이란?"

    # Chroma: 네이티브 필터
    with tempfile.TemporaryDirectory() as tmpdir:
        chroma_vs = Chroma.from_documents(corpus, embedding, persist_directory=tmpdir)
        retriever = chroma_vs.as_retriever(
            search_kwargs={"k": 3, "filter": {"topic": "faiss"}}
        )
        chroma_results = retriever.invoke(query)
        print("Chroma 필터 결과 (topic=faiss):")
        for doc in chroma_results:
            print(f"  [{doc.metadata.get('id')}] {doc.metadata.get('topic')} — {doc.page_content[:60]}")

    # FAISS: 후처리 필터 (LangChain EnsembleRetriever 또는 수동 필터)
    faiss_vs = FAISS.from_documents(corpus, embedding)
    all_results = faiss_vs.similarity_search(query, k=len(corpus))
    filtered = [d for d in all_results if d.metadata.get("topic") == "faiss"][:3]
    print("\nFAISS 후처리 필터 결과 (topic=faiss):")
    for doc in filtered:
        print(f"  [{doc.metadata.get('id')}] {doc.metadata.get('topic')} — {doc.page_content[:60]}")
```

---

## 선택 기준 정리

```python
if __name__ == "__main__":
    from rag_benchmark_post2 import CORPUS, QUERIES

    faiss_result = benchmark_faiss(CORPUS, QUERIES)
    chroma_result = benchmark_chroma(CORPUS, QUERIES)

    print("=== VectorDB 비교 ===")
    for result in [faiss_result, chroma_result]:
        print(json.dumps(result.summary(), indent=2, ensure_ascii=False))

    demo_metadata_filter(CORPUS)
```

**FAISS를 선택하는 경우**
- 인메모리 처리가 우선이고 영구 저장이 불필요한 경우
- 단순 쿼리만 필요하고 메타데이터 필터가 없는 경우
- 코퍼스 크기가 수백만 벡터 이하인 경우

**Chroma를 선택하는 경우**
- 메타데이터 기반 조건부 검색이 필요한 경우
- 영구 저장과 재시작 후 인덱스 복원이 필요한 경우
- 소규모에서 중규모 코퍼스 (수십만 문서 이하)

**Qdrant/Weaviate를 고려하는 경우**
- 수억 개 이상의 벡터가 필요한 경우
- 분산 배포와 수평 확장이 필요한 경우
- 복잡한 페이로드 필터와 하이브리드 검색이 필요한 경우

<!-- toc:begin -->
## 시리즈 목차

- [RAG 평가 지표 이해](./01-evaluation-metrics.md)
- [검색 성능 측정](./02-retrieval-benchmarking.md)
- [임베딩 모델 비교](./03-embedding-comparison.md)
- **VectorDB 선택 기준 (현재 글)**
- 종단 간 RAG 파이프라인 평가 (예정)
- RAG 벤치마크 완성 (예정)

<!-- toc:end -->

---

## 참고 자료

- [FAISS 위키](https://github.com/facebookresearch/faiss/wiki)
- [Chroma 공식 문서](https://docs.trychroma.com/)
- [ANN 벤치마크](https://ann-benchmarks.com/)

Tags: RAG, VectorDB, Benchmarking, LLM
