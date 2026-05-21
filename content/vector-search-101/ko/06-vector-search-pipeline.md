---
episode: 6
language: ko
last_reviewed: '2026-05-15'
series: vector-search-101
status: publish-ready
tags:
- Vector Search
- FAISS
- Embeddings
- Python
targets:
  ebook: true
  medium: false
  mkdocs: true
  tistory: true
title: "Vector Search 101 (6/6): 벡터 검색 파이프라인 — 문서 수집부터 쿼리까지"
seo_description: 문서 수집부터 FAISS 검색과 하이브리드 검색까지 벡터 검색 전체 흐름을 설명합니다.
---

# Vector Search 101 (6/6): 벡터 검색 파이프라인 — 문서 수집부터 쿼리까지

앞선 다섯 편에서는 임베딩, 유사도 척도, FAISS, 청킹을 각각 따로 봤습니다. 이번 글에서는 그 부품들을 하나의 실행 가능한 파이프라인으로 조립합니다. 문서를 불러오고, 청크로 나누고, 임베딩하고, FAISS 인덱스에 저장한 뒤, 자연어 쿼리로 결과를 검색하는 전체 흐름입니다.

마지막에는 벡터 검색과 키워드 검색을 결합하는 하이브리드 검색의 기초도 정리합니다.

이 글은 Vector Search 101 시리즈의 마지막 글입니다.

여기서는 "각 부품이 무엇인가"보다 "전체 검색 시스템이 어떤 순서로 움직이는가"에 초점을 맞춥니다.

![End to end indexing and retrieval flow](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/06/06-01-vector-search-pipeline-from-document-ing.ko.png)
*엔드 투 엔드 인덱싱 및 검색 흐름*
> 벡터 검색 파이프라인은 거대한 한 덩어리 기능이 아니라, 인덱싱 단계와 검색 단계를 분리해 각각 교체 가능하게 만드는 구조입니다.

## 먼저 던지는 질문

- 벡터 검색 파이프라인은 임베딩 한 번이 아니라 어떤 단계들의 연결일까요?
- 하이브리드 검색은 언제 단순 벡터 검색보다 안전할까요?
- 문서가 바뀌었을 때 재인덱싱과 운영 로그는 무엇을 기준으로 움직여야 할까요?

## 파이프라인 구조

![End to end indexing and retrieval flow](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/06/06-01-pipeline-structure.ko.png)

*엔드 투 엔드 인덱싱 및 검색 흐름*
![Pipeline component connection structure](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/06/06-02-pipeline-structure-2.ko.png)

*파이프라인 구성 요소 연결 구조*
벡터 검색 파이프라인은 크게 두 단계로 나뉩니다.

인덱싱은 오프라인 단계입니다. 문서를 한 번 처리해서 검색 가능한 인덱스를 만듭니다.

```text
load documents → chunk → embed → save FAISS index
```

검색은 온라인 단계입니다. 쿼리를 받아 임베딩하고 인덱스를 조회해 결과를 반환합니다.

```text
embed query → FAISS search → return ranked chunks
```

이 두 단계를 분리하면 인덱스는 한 번 만들고, 쿼리는 여러 번 처리할 수 있습니다.

---

## 완전한 파이프라인

![Build save load search execution path](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/06/06-03-complete-pipeline.ko.png)

*구축, 저장, 로드, 검색 실행 경로*
하나의 파일로 바로 실행 가능한 예제를 보겠습니다.

```python
import json
from pathlib import Path

import faiss
import numpy as np
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ── config ────────────────────────────────────────────────────────────────
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 300
CHUNK_OVERLAP = 30
INDEX_PATH = "faiss.index"
DOCS_PATH = "chunks.json"

# ── embedding model ────────────────────────────────────────────────────────
embedding_model = HuggingFaceEmbeddings(
    model_name=EMBED_MODEL,
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

# ── text splitter ──────────────────────────────────────────────────────────
splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", ". ", " ", ""],
)

# ── indexing ───────────────────────────────────────────────────────────────
def build_index(documents: list[str]) -> tuple[faiss.Index, list[str]]:
    """Chunk, embed, and index a list of document strings."""
    all_chunks: list[str] = []
    for doc in documents:
        all_chunks.extend(splitter.split_text(doc))
    print(f"total chunks: {len(all_chunks)}")

    vectors = np.array(
        embedding_model.embed_documents(all_chunks), dtype=np.float32
    )
    dimension = vectors.shape[1]
    print(f"vector shape: {vectors.shape}")

    index = faiss.IndexFlatIP(dimension)
    index.add(vectors)

    return index, all_chunks

def save_index(index: faiss.Index, chunks: list[str]) -> None:
    faiss.write_index(index, INDEX_PATH)
    with open(DOCS_PATH, "w") as f:
        json.dump(chunks, f, indent=2)
    print(f"saved: {INDEX_PATH}, {DOCS_PATH}")

def load_index() -> tuple[faiss.Index, list[str]]:
    index = faiss.read_index(INDEX_PATH)
    with open(DOCS_PATH) as f:
        chunks = json.load(f)
    print(f"loaded: {index.ntotal} vectors")
    return index, chunks

# ── retrieval ──────────────────────────────────────────────────────────────
def search(
    query: str,
    index: faiss.Index,
    chunks: list[str],
    top_k: int = 3,
) -> list[tuple[float, str]]:
    q_vec = np.array([embedding_model.embed_query(query)], dtype=np.float32)
    scores, indices = index.search(q_vec, top_k)
    return [
        (float(scores[0][i]), chunks[indices[0][i]])
        for i in range(top_k)
        if indices[0][i] != -1
    ]

# ── run ────────────────────────────────────────────────────────────────────
documents = [
    """
Vector search converts text into numeric vectors for meaning-based retrieval.
Unlike keyword search, it matches content even when phrasing differs.
Embedding models place semantically similar text close together in vector space.
""",
    """
FAISS is a high-speed vector search library developed at Facebook AI Research.
It supports both exact and approximate search and can handle billions of vectors.
IndexFlatIP is an exact inner-product index equivalent to cosine search on normalized vectors.
""",
    """
Chunking strategies split long documents into units the embedding model can process.
chunk_size and chunk_overlap must be tuned to achieve good retrieval quality.
RecursiveCharacterTextSplitter tries paragraph, sentence, and word boundaries in order.
""",
    """
RAG (Retrieval-Augmented Generation) combines retrieved documents with an LLM prompt.
The system retrieves relevant chunks for the user's question and provides them as context.
Vector search is the retrieval component in most RAG pipelines.
""",
]

index, chunks = build_index(documents)
save_index(index, chunks)

index, chunks = load_index()

queries = [
    "how vector search differs from keyword search",
    "FAISS index types",
    "choosing chunk size",
    "role of retrieval in RAG",
]

for query in queries:
    print(f"\nquery: '{query}'")
    results = search(query, index, chunks, top_k=2)
    for rank, (score, text) in enumerate(results, start=1):
        print(f"  [{rank}] {score:.4f} — {text.strip()[:70]}...")
```

<!-- injected-output:start -->
**출력 결과**

    total chunks: 4
    vector shape: (4, 384)
    saved: faiss.index, chunks.json
    loaded: 4 vectors

    query: 'how vector search differs from keyword search'
      [1] 0.7285 — Vector search converts text into numeric vectors for meaning-based ret...
      [2] 0.4562 — RAG (Retrieval-Augmented Generation) combines retrieved documents with...

    query: 'FAISS index types'
      [1] 0.5547 — FAISS is a high-speed vector search library developed at Facebook AI R...
      [2] 0.1110 — Vector search converts text into numeric vectors for meaning-based ret...

    query: 'choosing chunk size'
      [1] 0.4771 — Chunking strategies split long documents into units the embedding mode...
      [2] 0.1839 — RAG (Retrieval-Augmented Generation) combines retrieved documents with...

    query: 'role of retrieval in RAG'
      [1] 0.5931 — RAG (Retrieval-Augmented Generation) combines retrieved documents with...
      [2] 0.1908 — Chunking strategies split long documents into units the embedding mode...

<!-- injected-output:end -->

위 예제에서 청크 수가 4개로 끝나는 이유는 입력 문서 자체가 짧기 때문입니다. 실제 운영에서는 문서 길이와 `chunk_size`, `chunk_overlap` 설정에 따라 결과 청크 수가 크게 달라집니다. 따라서 출력 숫자 하나를 외우기보다, **문서 수 → 청크 수 → 인덱스 벡터 수가 일관되게 연결되는지**를 확인하는 편이 더 중요합니다.

---

## 하이브리드 검색

![Combining vector scores with BM25 scores](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/06/06-04-hybrid-search.ko.png)

*벡터 점수와 BM25 점수 결합 구조*
벡터 검색만으로는 정확한 용어가 중요한 상황에 약합니다. 오류 코드, 제품 ID, 고유명사처럼 정확 일치가 중요한 경우에는 키워드 검색이 더 강합니다. 하이브리드 검색은 두 방식을 결합합니다.

가장 표준적인 접근은 각 점수를 [0, 1] 범위로 정규화한 뒤 가중합을 계산하는 방식입니다.

```python
from rank_bm25 import BM25Okapi

def hybrid_search(
    query: str,
    index: faiss.Index,
    chunks: list[str],
    top_k: int = 3,
    alpha: float = 0.5,
) -> list[tuple[float, str]]:
    """Combine vector search and BM25 keyword search.
    alpha: weight of vector score (0 = keyword only, 1 = vector only)
    """
    # 벡터 점수(정규화된 벡터로 이미 0–1 범위)
    q_vec = np.array([embedding_model.embed_query(query)], dtype=np.float32)
    vec_scores, vec_indices = index.search(q_vec, len(chunks))
    vec_score_map = {
        int(idx): float(score)
        for idx, score in zip(vec_indices[0], vec_scores[0])
        if idx != -1
    }

    # BM25 점수를 0–1로 정규화
    tokenized = [chunk.split() for chunk in chunks]
    bm25 = BM25Okapi(tokenized)
    bm25_scores = bm25.get_scores(query.split())
    max_bm25 = max(bm25_scores) if max(bm25_scores) > 0 else 1.0
    bm25_norm = bm25_scores / max_bm25

    # weighted combination
    combined = {
        i: alpha * vec_score_map.get(i, 0.0) + (1 - alpha) * float(bm25_norm[i])
        for i in range(len(chunks))
    }

    top_indices = sorted(combined, key=combined.__getitem__, reverse=True)[:top_k]
    return [(combined[i], chunks[i]) for i in top_indices]
```

`alpha=0.5`는 두 방식에 같은 가중치를 둡니다. 의미 기반 가중치를 더 높이고 싶다면 1.0 쪽으로 올리고, 키워드 일치를 더 중시하고 싶다면 0.0 쪽으로 낮추면 됩니다.

바로 실행해 보면 하이브리드 검색이 어떤 문제를 푸는지 더 분명해집니다.

```python
bm25_ready_chunks = [
    "FAISS IndexFlatIP supports exact inner-product search on normalized vectors.",
    "Error code ERR_CONNECTION_REFUSED is usually better handled by exact keyword search.",
    "Chunking strategy changes how much context each vector carries.",
]

bm25_index = BM25Okapi([chunk.split() for chunk in bm25_ready_chunks])
vector_index, _ = build_index(bm25_ready_chunks)

for query in ["IndexFlatIP cosine search", "ERR_CONNECTION_REFUSED"]:
    results = hybrid_search(query, vector_index, bm25_ready_chunks, top_k=2, alpha=0.5)
    print(f"\nquery: {query}")
    for score, text in results:
        print(f"  {score:.4f} — {text}")
```

<!-- injected-output:start -->
**출력 결과**

    query: IndexFlatIP cosine search
      0.9087 — FAISS IndexFlatIP supports exact inner-product search on normalized vectors.
      0.2173 — Chunking strategy changes how much context each vector carries.

    query: ERR_CONNECTION_REFUSED
      0.7421 — Error code ERR_CONNECTION_REFUSED is usually better handled by exact keyword search.
      0.1036 — FAISS IndexFlatIP supports exact inner-product search on normalized vectors.

<!-- injected-output:end -->

첫 번째 질의는 의미 기반과 키워드 기반이 같은 결과를 밀어 올립니다. 두 번째 질의는 정확 문자열이 핵심이라 BM25 쪽 신호가 더 강하게 작동합니다. 하이브리드 검색이 필요한 이유가 이 두 쿼리의 차이에 그대로 드러납니다.

## 재인덱싱을 언제 트리거할 것인가

운영에서 자주 놓치는 지점은 인덱스를 "한 번 만들고 끝"이라고 생각하는 것입니다. 실제로는 다음 같은 이벤트가 생기면 재인덱싱 기준을 분명히 정해 두어야 합니다.

- 임베딩 모델 이름이나 버전이 바뀌었을 때
- 청크 규칙(`chunk_size`, `chunk_overlap`, 분리자)이 바뀌었을 때
- 문서 원본이 수정되었을 때
- 메타데이터 스키마가 바뀌었을 때

아래처럼 작은 매니페스트 파일을 함께 저장해 두면, 파이프라인이 시작될 때 현재 설정과 기존 인덱스가 호환되는지 바로 비교할 수 있습니다.

```python
import json

manifest = {
    "embedding_model": EMBED_MODEL,
    "chunk_size": CHUNK_SIZE,
    "chunk_overlap": CHUNK_OVERLAP,
    "document_count": len(documents),
    "index_type": "IndexFlatIP",
}

with open("index-manifest.json", "w") as f:
    json.dump(manifest, f, indent=2)

print(manifest)
```

<!-- injected-output:start -->
**출력 결과**

    {'embedding_model': 'sentence-transformers/all-MiniLM-L6-v2', 'chunk_size': 300, 'chunk_overlap': 30, 'document_count': 4, 'index_type': 'IndexFlatIP'}

<!-- injected-output:end -->

이 매니페스트는 거창한 기능이 아닙니다. 하지만 운영 중 "왜 검색 결과가 어제와 다르지?"라는 질문이 나왔을 때 가장 먼저 비교할 근거를 만들어 줍니다.

---

## 운영 관점에서 볼 점

![Index update and deletion constraint path](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/06/06-05-operational-considerations.ko.png)

*인덱스 갱신과 삭제 제약 경로*
**인덱스 업데이트.** 새 문서를 추가하는 일 자체는 단순합니다. 임베딩한 뒤 `index.add()`를 호출하면 됩니다. 다만 `IndexFlatIP`는 삭제를 지원하지 않습니다. 벡터를 제거해야 한다면 주기적으로 인덱스를 재구축하거나, `IndexIDMap`으로 식별자를 관리하면서 삭제된 항목을 건너뛰는 방식을 사용해야 합니다.

**메모리.** `IndexFlatIP`는 모든 벡터를 메모리에 유지합니다. 차원 384, 4바이트 float 기준으로 10만 벡터는 약 147MB이고, 100만 벡터면 약 1.5GB입니다. 그 이상에서는 `IndexIVFFlat`이나 `IndexPQ` 같은 압축형 인덱스가 필요합니다.

**지연 시간.** CPU에서 10만 벡터를 검색하면 수십 밀리초 수준이 걸립니다. 서비스 지연 시간이 민감하다면 GPU 빌드나 근사 인덱스를 고려해야 합니다.

---

## 마무리

이 글에서는 전체 벡터 검색 파이프라인을 조립했습니다. 문서를 불러오고, `RecursiveCharacterTextSplitter`로 청크를 만들고, `HuggingFaceEmbeddings`로 임베딩하고, FAISS로 인덱싱하고, 디스크에 저장한 뒤, 자연어 쿼리로 검색했습니다.

다음으로 자연스러운 확장은 이 파이프라인을 LLM과 연결해 RAG 시스템으로 만드는 일입니다. `langchain-101` 시리즈에서는 LCEL, Retriever, Chain 조합을 다룹니다.

## 운영 체크리스트

- [ ] ingest, embed, index, search를 각각 독립 배포 가능한 단계로 분리했다
- [ ] 임베딩 모델 버전과 인덱스 버전에 맞춰 재인덱싱 트리거를 자동화했다
- [ ] lexical 점수와 vector 점수를 어떻게 결합할지 정의했다
- [ ] 운영에서 평가 셋과 자동 품질 검증 스크립트를 유지했다
- [ ] 지연 시간, recall, 비용을 같은 대시보드에서 보이게 했다

## 벡터 DB로 교체 가능한 파이프라인 경계

6편의 핵심은 특정 라이브러리에 종속되지 않는 경계를 세우는 것입니다. 아래처럼 인터페이스를 먼저 두면, 로컬 FAISS에서 Chroma/Qdrant/Pinecone으로 이동해도 상위 검색 로직은 유지됩니다.

```python
from typing import Protocol

class VectorStore(Protocol):
    def upsert(self, ids: list[str], vectors: list[list[float]], payloads: list[dict]) -> None:
        ...

    def search(self, query_vector: list[float], top_k: int) -> list[tuple[str, float, dict]]:
        ...
```

파이프라인이 이 인터페이스를 기준으로 작성되어 있으면, 저장소 선택은 구현 세부로 내려갑니다.

## 저장소별 구현 예시

```python
# Chroma adapter (요약)
class ChromaStore:
    def __init__(self, collection):
        self.collection = collection

    def upsert(self, ids, vectors, payloads):
        self.collection.upsert(ids=ids, embeddings=vectors, metadatas=payloads)

    def search(self, query_vector, top_k):
        out = self.collection.query(query_embeddings=[query_vector], n_results=top_k)
        return list(zip(out["ids"][0], out["distances"][0], out["metadatas"][0]))
```

```python
# Qdrant adapter (요약)
class QdrantStore:
    def __init__(self, client, collection_name):
        self.client = client
        self.collection_name = collection_name

    def upsert(self, ids, vectors, payloads):
        points = [{"id": i, "vector": v, "payload": p} for i, v, p in zip(ids, vectors, payloads)]
        self.client.upsert(collection_name=self.collection_name, points=points)

    def search(self, query_vector, top_k):
        hits = self.client.search(collection_name=self.collection_name, query_vector=query_vector, limit=top_k)
        return [(str(h.id), float(h.score), h.payload) for h in hits]
```

```python
# Pinecone adapter (요약)
class PineconeStore:
    def __init__(self, index):
        self.index = index

    def upsert(self, ids, vectors, payloads):
        self.index.upsert(vectors=[(i, v, p) for i, v, p in zip(ids, vectors, payloads)])

    def search(self, query_vector, top_k):
        out = self.index.query(vector=query_vector, top_k=top_k, include_metadata=True)
        return [(m.id, float(m.score), m.metadata) for m in out.matches]
```

## 하이브리드 검색 가중치 실험 루프

하이브리드 검색은 한 번 구현하고 끝나는 기능이 아닙니다. `alpha` 값을 바꿔 평가셋에서 반복 측정해야 합니다.

```python
def evaluate_alpha(candidates, alpha_values):
    rows = []
    for alpha in alpha_values:
        metrics = run_eval(candidates=candidates, alpha=alpha)  # precision/recall 계산 함수
        rows.append((alpha, metrics["recall@5"], metrics["mrr@10"], metrics["p95_ms"]))
    return rows
```

| alpha(vector weight) | Recall@5 | MRR@10 | p95(ms) |
|---:|---:|---:|---:|
| 0.2 | 0.81 | 0.63 | 38 |
| 0.5 | 0.88 | 0.69 | 42 |
| 0.7 | 0.90 | 0.71 | 44 |
| 0.9 | 0.87 | 0.67 | 43 |

이런 결과가 나오면 0.7 근처를 기본값으로 두고, 식별자 중심 질의에는 0.5 이하를 적용하는 정책 분기가 가능합니다.

## 프로덕션 스케일링 패턴

마지막으로 실제 운영에서 자주 사용하는 확장 패턴을 정리합니다.

- 인덱싱 파이프라인은 배치 작업으로 분리하고, 서비스 검색 노드는 읽기 전용으로 유지
- 인덱스 버전을 `blue/green`으로 운영해 무중단 교체
- 쿼리 로그에서 실패 질의를 추출해 주기적으로 평가셋에 편입
- latency budget을 초과하면 top-k 축소, ANN 파라미터 하향, 리랭커 비활성화 순으로 완화
- 모델 교체 시 shadow traffic으로 점수 분포를 먼저 비교하고 본 배포 진행

이 규칙을 자동화하면 "검색 품질"과 "서비스 안정성"이 충돌할 때도 대응 절차가 명확해집니다.

추가로 운영 초기에 꼭 넣어야 할 항목은 "관측 가능성 계약"입니다. 최소한 `query_id`, `index_version`, `embedding_version`, `top_k`, `latency_ms`, `result_doc_ids`를 구조화 로그로 남기면 문제 재현 속도가 크게 올라갑니다. 벡터 검색 문제는 원인이 인덱스인지, 모델인지, 하이브리드 가중치인지 섞여 나타나는 경우가 많기 때문에, 이 필드가 없으면 원인 분리가 거의 불가능합니다.

요약하면 파이프라인의 완성도는 단일 알고리즘보다 경계 설계와 운영 계측에서 결정됩니다.

## 처음 질문으로 돌아가기

- **벡터 검색 파이프라인은 임베딩 한 번이 아니라 어떤 단계들의 연결일까요?**
  수집, 정제, 청킹, 임베딩, 인덱싱, 쿼리 임베딩, 검색, 재조립이 모두 연결되어야 사용자 질문에 답할 수 있습니다.

- **하이브리드 검색은 언제 단순 벡터 검색보다 안전할까요?**
  정확한 식별자, 최신 키워드, 필터 조건이 중요한 문서는 벡터만으로 놓칠 수 있으므로 키워드 검색과 결합한 하이브리드 검색이 더 안전합니다.

- **문서가 바뀌었을 때 재인덱싱과 운영 로그는 무엇을 기준으로 움직여야 할까요?**
  문서 버전, 입력 해시, 모델 버전, 청크 설정 변경을 기준으로 재인덱싱을 트리거하고, 쿼리·결과·지연 시간·인덱스 버전을 로그로 남겨야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Vector Search 101 (1/6): 임베딩이란 무엇인가 — 텍스트를 벡터로 변환하기](./01-what-is-embedding.md)
- [Vector Search 101 (2/6): HuggingFace 임베딩 실습 — sentence-transformers로 첫 벡터 만들기](./02-huggingface-embeddings.md)
- [Vector Search 101 (3/6): 코사인 유사도와 벡터 검색 — 문장 간 거리 계산하기](./03-cosine-similarity.md)
- [Vector Search 101 (4/6): FAISS 입문 — 고속 근사 최근접 이웃 검색](./04-faiss-fundamentals.md)
- [Vector Search 101 (5/6): 청크 전략 — 긴 문서를 어떻게 나눌 것인가](./05-chunking-strategies.md)
- **Vector Search 101 (6/6): 벡터 검색 파이프라인 — 문서 수집부터 쿼리까지 (현재 글)**

<!-- toc:end -->

---

## 참고 자료

- [FAISS documentation](https://faiss.ai/)
- [LangChain FAISS integration](https://python.langchain.com/docs/integrations/vectorstores/faiss/)
- [rank-bm25 library](https://github.com/dorianbrown/rank_bm25)
- [Hybrid search introduction — Pinecone](https://www.pinecone.io/learn/hybrid-search-intro/)
- [Sentence Transformers pretrained models](https://www.sbert.net/docs/sentence_transformer/pretrained_models.html)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/vector-search-101/ko/06-vector-search-pipeline)

Tags: Vector Search, FAISS, Embeddings, Python
