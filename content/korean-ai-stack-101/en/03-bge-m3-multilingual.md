---
title: 'BGE-M3 multilingual embedding in practice'
series: korean-ai-stack-101
episode: 3
language: en
status: draft
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- Korean NLP
- LLM
- Embeddings
- OCR
last_reviewed: '2026-05-01'
---

# BGE-M3 multilingual embedding in practice

> Korean AI Stack 101 (3/6)

Technical documents, research papers, and API references often mix English terms into Korean sentences — "트랜스포머(Transformer) 모델의 어텐션(Attention) 메커니즘". KoSimCSE is optimized for pure Korean, but BGE-M3 handles this code-switching text better. BGE-M3 supports over 100 languages and delivers dense, sparse, and multi-vector retrieval from a single model.

Topics:

- BGE-M3's three output types: dense, sparse, ColBERT
- performance on Korean-English mixed documents
- dense + sparse hybrid retrieval
- LangChain integration

---

## BGE-M3's three output types

BGE-M3 produces three different embedding forms from the same input.

**Dense**: a standard high-dimensional vector (1024 dims). Used with ANN indexes like FAISS.

**Sparse (Lexical Weight)**: a sparse vector assigning weight to each token. Similar to BM25, strong on exact keyword matching.

**ColBERT (Multi-vector)**: a separate vector per token, scored via Late Interaction. Most accurate but expensive in storage and compute.

Dense + sparse hybrid is the practical sweet spot for most production systems.

---

## Dense embeddings with mixed Korean/English text

```python
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BAAI/bge-m3")

mixed_docs = [
    "트랜스포머(Transformer) 모델의 어텐션(Attention) 메커니즘은 시퀀스 내 각 위치 간 의존성을 학습합니다.",
    "FAISS는 Facebook AI Research에서 개발한 벡터 유사도 검색 라이브러리입니다.",
    "파이썬의 asyncio 모듈을 사용하면 비동기 I/O 작업을 효율적으로 처리할 수 있습니다.",
    "LangChain의 LCEL(LangChain Expression Language)은 체인을 선언적으로 구성하는 방법입니다.",
    "RAG(Retrieval-Augmented Generation)는 검색과 생성을 결합해 LLM의 지식 한계를 보완합니다.",
    "Docker 컨테이너를 Kubernetes 클러스터에 배포하는 방법을 알아봅니다.",
]

embeddings = model.encode(mixed_docs, normalize_embeddings=True)
print(f"dense embedding shape: {embeddings.shape}")  # (6, 1024)

def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b))

# queries mixing Korean and English
queries = [
    "Attention mechanism이 어떻게 작동하나요?",  # English keyword in Korean sentence
    "벡터 검색 라이브러리",                       # pure Korean query
    "async I/O 처리 방법",                        # mixed
]

for query in queries:
    query_vec = model.encode([query], normalize_embeddings=True)[0]
    sims = [(cosine_sim(query_vec, emb), doc) for emb, doc in zip(embeddings, mixed_docs)]
    sims.sort(reverse=True)

    print(f"\nquery: {query}")
    for score, doc in sims[:3]:
        print(f"  [{score:.3f}] {doc[:70]}...")
```

---

## Dense + sparse hybrid retrieval

Dense retrieval is strong on semantic similarity. Sparse retrieval is strong on exact keyword matching. Combining the two scores with a weighted sum captures both advantages.

```python
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BAAI/bge-m3")

tech_docs = [
    "Python asyncio를 사용한 비동기 HTTP 요청 처리",
    "FAISS IndexIVFFlat으로 대규모 벡터 검색 최적화",
    "Kubernetes Pod 스케줄링과 리소스 제한 설정",
    "LangChain Retriever와 FAISS 벡터스토어 통합",
    "트랜스포머 모델의 Self-Attention 구현",
    "Redis를 이용한 API 응답 캐싱 전략",
    "PostgreSQL 인덱스 최적화와 쿼리 플랜 분석",
    "Docker multi-stage build로 이미지 크기 줄이기",
]

dense_embeddings = model.encode(tech_docs, normalize_embeddings=True).astype(np.float32)
dim = dense_embeddings.shape[1]
dense_index = faiss.IndexFlatIP(dim)
dense_index.add(dense_embeddings)

def sparse_sim(query: str, doc: str) -> float:
    """Word-overlap sparse similarity (BM25 approximation)."""
    query_tokens = set(query.lower().split())
    doc_tokens = set(doc.lower().split())
    overlap = query_tokens & doc_tokens
    return len(overlap) / len(query_tokens) if query_tokens else 0.0

def hybrid_search(query: str, alpha: float = 0.7, k: int = 3) -> list[dict]:
    """
    Hybrid search: alpha * dense_score + (1 - alpha) * sparse_score.
    alpha=1.0 is pure dense, alpha=0.0 is pure sparse.
    """
    query_vec = model.encode([query], normalize_embeddings=True).astype(np.float32)
    distances, indices = dense_index.search(query_vec, len(tech_docs))
    dense_scores = {int(idx): float(dist) for idx, dist in zip(indices[0], distances[0])}

    results = []
    for i, doc in enumerate(tech_docs):
        d_score = dense_scores.get(i, 0.0)
        s_score = sparse_sim(query, doc)
        combined = alpha * d_score + (1 - alpha) * s_score
        results.append({"score": combined, "dense": d_score, "sparse": s_score, "doc": doc})

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:k]

queries = [
    "FAISS 벡터 인덱스 구성 방법",
    "asyncio HTTP",
    "Kubernetes 리소스 관리",
]

for query in queries:
    print(f"\nquery: {query}")
    results = hybrid_search(query, alpha=0.7)
    for r in results:
        print(f"  [{r['score']:.3f}] dense={r['dense']:.3f} sparse={r['sparse']:.3f}")
        print(f"       {r['doc']}")
```

---

## LangChain integration

```python
import os

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_groq import ChatGroq

embedding_model = HuggingFaceEmbeddings(
    model_name="BAAI/bge-m3",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

vectorstore = FAISS.from_texts(texts=tech_docs, embedding=embedding_model)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
)

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "Answer the question using the technical documents below.\n\n"
        "Documents:\n{context}",
    ),
    ("human", "{question}"),
])

def format_docs(docs: list) -> str:
    return "\n".join(doc.page_content for doc in docs)

chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

answer = chain.invoke("How do I optimize vector search with FAISS?")
print(f"answer: {answer}")
```

---

## Conclusion

BGE-M3 is well suited for technical services that mix Korean and English. Dense retrieval alone handles most cases, but when exact keyword matching matters — searching code identifiers, model names, or API terms — add the sparse component. The `alpha` parameter lets you tune the trade-off without reindexing.

The next post covers CLOVA OCR API: extracting text from images and PDFs to feed into the embedding pipeline.

<!-- toc:begin -->
## In this series

- [Korean embedding models compared — KoSimCSE, BGE-M3, Solar](./01-korean-embedding-models.md)
- [Building sentence similarity search with KoSimCSE](./02-kosimcse-similarity.md)
- **BGE-M3 multilingual embedding in practice (current)**
- Document text extraction with CLOVA OCR API (upcoming)
- Using HyperCLOVA X and Solar API (upcoming)
- Assembling a Korean RAG pipeline (upcoming)

<!-- toc:end -->

---

## References

- [BGE-M3 paper](https://arxiv.org/abs/2309.07597)
- [FlagEmbedding library](https://github.com/FlagOpen/FlagEmbedding)
- [Hybrid search introduction](https://www.pinecone.io/learn/hybrid-search-intro/)

Tags: Korean NLP, LLM, Embeddings, OCR
