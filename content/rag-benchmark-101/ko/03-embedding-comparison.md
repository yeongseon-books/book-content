# 임베딩 모델 비교

> RAG 벤치마크 101 (3/6)

임베딩 모델은 RAG 파이프라인의 핵심입니다. 같은 검색기와 LLM을 써도 임베딩 모델이 바뀌면 검색 품질이 크게 달라집니다. 이 포스트에서는 여러 임베딩 모델을 동일한 쿼리 집합으로 벤치마킹해 모델 선택 기준을 정립합니다.

---

## 비교할 임베딩 모델

실제 프로덕션에서 자주 쓰이는 모델 세 가지를 비교합니다.

| 모델 | 차원 | 크기 | 특징 |
|------|-----|-----|------|
| all-MiniLM-L6-v2 | 384 | 80MB | 경량, 빠름 |
| all-mpnet-base-v2 | 768 | 420MB | 높은 품질 |
| paraphrase-multilingual-MiniLM-L12-v2 | 384 | 120MB | 다국어 지원 |

---

## 임베딩 모델 벤치마크

```python
import json
import time
from dataclasses import dataclass, field

import numpy as np
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document

@dataclass
class EmbeddingBenchResult:
    model_name: str
    index_time_s: float
    query_time_ms: float
    precision_at_3: float
    recall_at_3: float
    mrr: float

    def summary(self) -> dict:
        return {
            "model": self.model_name.split("/")[-1],
            "index_time_s": round(self.index_time_s, 2),
            "query_time_ms": round(self.query_time_ms, 1),
            "precision@3": round(self.precision_at_3, 4),
            "recall@3": round(self.recall_at_3, 4),
            "mrr": round(self.mrr, 4),
        }

def _metrics(retrieved_ids: list[str], relevant_ids: set[str], k: int) -> tuple[float, float, float]:
    top_k = retrieved_ids[:k]
    hits = [d for d in top_k if d in relevant_ids]
    precision = len(hits) / k if k > 0 else 0.0
    recall = len(hits) / len(relevant_ids) if relevant_ids else 0.0
    mrr = next((1.0 / (i + 1) for i, d in enumerate(top_k) if d in relevant_ids), 0.0)
    return precision, recall, mrr

def benchmark_embedding_model(
    model_name: str,
    corpus: list[Document],
    queries: list,  # list[QueryGroundTruth]
    k: int = 3,
) -> EmbeddingBenchResult:
    embedding = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    # 인덱싱 시간 측정
    t0 = time.perf_counter()
    vectorstore = FAISS.from_documents(corpus, embedding)
    index_time = time.perf_counter() - t0

    retriever = vectorstore.as_retriever(search_kwargs={"k": k})

    # 쿼리 시간 + 검색 품질 측정
    precisions, recalls, mrrs = [], [], []
    query_times = []

    for qt in queries:
        t0 = time.perf_counter()
        retrieved_docs = retriever.invoke(qt.query)
        query_times.append((time.perf_counter() - t0) * 1000)

        retrieved_ids = [d.metadata.get("id", "") for d in retrieved_docs]
        p, r, m = _metrics(retrieved_ids, qt.relevant_ids, k)
        precisions.append(p)
        recalls.append(r)
        mrrs.append(m)

    return EmbeddingBenchResult(
        model_name=model_name,
        index_time_s=index_time,
        query_time_ms=sum(query_times) / len(query_times) if query_times else 0,
        precision_at_3=sum(precisions) / len(precisions) if precisions else 0,
        recall_at_3=sum(recalls) / len(recalls) if recalls else 0,
        mrr=sum(mrrs) / len(mrrs) if mrrs else 0,
    )
```

---

## 코사인 유사도 분포 분석

```python
def analyze_similarity_distribution(
    model_name: str,
    corpus: list[Document],
    queries: list,
    k: int = 5,
) -> dict:
    """관련/비관련 문서 간 유사도 분포를 분석합니다."""
    embedding = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
    vectorstore = FAISS.from_documents(corpus, embedding)

    relevant_scores, irrelevant_scores = [], []
    for qt in queries:
        results = vectorstore.similarity_search_with_score(qt.query, k=k)
        for doc, score in results:
            doc_id = doc.metadata.get("id", "")
            if doc_id in qt.relevant_ids:
                relevant_scores.append(float(score))
            else:
                irrelevant_scores.append(float(score))

    def stats(scores: list[float]) -> dict:
        if not scores:
            return {}
        arr = np.array(scores)
        return {
            "mean": round(float(arr.mean()), 4),
            "std": round(float(arr.std()), 4),
            "min": round(float(arr.min()), 4),
            "max": round(float(arr.max()), 4),
        }

    return {
        "model": model_name.split("/")[-1],
        "relevant": stats(relevant_scores),
        "irrelevant": stats(irrelevant_scores),
        "gap": round(
            abs(np.mean(relevant_scores) - np.mean(irrelevant_scores)) if (relevant_scores and irrelevant_scores) else 0,
            4,
        ),
    }
```

---

## 비교 실행

```python
# 이전 포스트에서 정의한 CORPUS, QUERIES 재사용
MODELS = [
    "sentence-transformers/all-MiniLM-L6-v2",
    "sentence-transformers/all-mpnet-base-v2",
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
]

def run_embedding_comparison(corpus, queries, models):
    results = []
    for model_name in models:
        print(f"벤치마킹: {model_name.split('/')[-1]} ...")
        result = benchmark_embedding_model(model_name, corpus, queries)
        results.append(result.summary())
    return results

if __name__ == "__main__":
    from rag_benchmark_101_02 import CORPUS, QUERIES  # 이전 포스트 임포트

    comparison = run_embedding_comparison(CORPUS, QUERIES, MODELS)
    print("\n=== 임베딩 모델 비교 ===")
    for result in comparison:
        print(json.dumps(result, indent=2, ensure_ascii=False))

    print("\n=== 유사도 분포 분석 ===")
    for model in MODELS:
        dist = analyze_similarity_distribution(model, CORPUS, QUERIES)
        print(json.dumps(dist, indent=2, ensure_ascii=False))
```

---

## 모델 선택 기준

임베딩 모델을 고를 때 단일 지표에 의존하면 안 됩니다. 상황에 맞게 다음을 고려해야 합니다.

- **쿼리 속도가 중요한 경우**: `all-MiniLM-L6-v2`. 품질보다 처리량이 우선인 실시간 시스템에 적합합니다.
- **품질이 중요한 경우**: `all-mpnet-base-v2`. 모델 크기와 인덱싱 시간을 감수할 수 있다면 최선입니다.
- **다국어 지원이 필요한 경우**: `paraphrase-multilingual-MiniLM-L12-v2`. 한국어와 영어가 혼재하는 코퍼스에서 유리합니다.

유사도 분포 분석에서 관련/비관련 문서 간 점수 차이(gap)가 클수록 모델의 변별력이 높습니다. gap이 작으면 임계값 기반 필터링이 어렵고 노이즈가 많은 검색 결과가 나옵니다.

<!-- toc:begin -->
## 시리즈 목차

- [RAG 평가 지표 이해](./01-evaluation-metrics.md)
- [검색 성능 측정](./02-retrieval-benchmarking.md)
- **임베딩 모델 비교 (현재 글)**
- VectorDB 선택 기준 (예정)
- 종단 간 RAG 파이프라인 평가 (예정)
- RAG 벤치마크 완성 (예정)

<!-- toc:end -->

---

## 참고 자료

- [MTEB 임베딩 벤치마크](https://huggingface.co/spaces/mteb/leaderboard)
- [Sentence Transformers 모델 허브](https://www.sbert.net/docs/pretrained_models.html)
- [FAISS 인덱스 타입 가이드](https://github.com/facebookresearch/faiss/wiki/Faiss-indexes)

Tags: RAG, VectorDB, Benchmarking, LLM
