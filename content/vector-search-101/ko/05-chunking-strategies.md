---
episode: 5
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
title: "Vector Search 101 (5/6): 청크 전략 — 긴 문서를 어떻게 나눌 것인가"
seo_description: 청크 크기와 오버랩이 검색 품질에 미치는 영향과 실전 분할 전략을 설명합니다.
---

# Vector Search 101 (5/6): 청크 전략 — 긴 문서를 어떻게 나눌 것인가

임베딩 모델에는 하드 토큰 한도가 있습니다. `all-MiniLM-L6-v2`는 최대 256 서브워드 토큰만 처리합니다. PDF 한 페이지도 이 한계를 쉽게 넘깁니다. 긴 문서를 한 번에 넣으면 경계 뒤의 내용이 잘리거나, 너무 많은 정보가 하나의 벡터에 압축되어 검색 정밀도가 떨어집니다.

청킹은 긴 문서를 임베딩 가능한 크기의 조각으로 나누는 작업입니다. 어떻게 나누느냐가 검색 품질에 직접 영향을 줍니다. 청크가 너무 작으면 문맥을 잃고, 너무 크면 서로 무관한 내용이 섞입니다.

이 글은 Vector Search 101 시리즈의 다섯 번째 글입니다.

여기서는 단순히 텍스트를 자르는 법이 아니라, 검색 시스템이 어떤 문맥 단위를 기억하게 만들지 설계하는 관점으로 청킹을 봅니다.

## 먼저 던지는 질문

- 긴 문서를 그대로 임베딩하지 않고 왜 청크로 나눠야 할까요?
- chunk_size와 overlap은 검색 품질과 비용 사이에서 어떤 균형을 만들까요?
- 청크에 메타데이터를 붙이지 않으면 답변 경로에서 무엇이 막힐까요?

## 큰 그림

![Chunk size and overlap structure](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/05/05-01-chunking-strategies-how-to-split-long-do.ko.png)

*청크 크기와 오버랩 구조*

이 그림에서는 긴 문서를 작은 청크로 나누고, 각 청크를 임베딩해 검색 가능한 단위로 만드는 흐름을 봅니다. 청크 전략은 단순 전처리가 아니라 검색 단위, 비용, 출처 추적을 함께 결정합니다.

> 청킹은 전처리 부가 작업이 아니라, 검색 시스템이 어떤 문맥 단위를 기억할지 결정하는 설계 단계입니다.

## 청크 크기와 오버랩

![Chunk size and overlap structure](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/05/05-01-chunk-size-and-overlap.ko.png)

*청크 크기와 오버랩 구조*
청킹을 제어하는 핵심 파라미터는 `chunk_size`와 `chunk_overlap` 두 가지입니다.

**chunk_size**: 청크 하나의 최대 길이입니다. 문자 수나 토큰 수로 측정합니다. 흔한 시작 범위는 200~500 토큰입니다.

**chunk_overlap**: 인접한 청크가 공유하는 문자 수입니다. 오버랩이 없으면 문장이 정확히 청크 경계에 걸려 반으로 잘릴 수 있습니다. 오버랩을 두면 같은 내용이 연속된 두 청크에 모두 들어가므로, 경계 근처 내용도 검색에서 살아남습니다.

```text
original: A B C D E F G H I J (each letter represents one word)

chunk_size=4, chunk_overlap=1:
chunk 0: A B C D
chunk 1: D E F G   ← D repeats
chunk 2: G H I J   ← G repeats
```

실무에서는 오버랩을 `chunk_size`의 10~20% 정도로 잡는 경우가 많습니다. 오버랩이 너무 크면 인덱스만 불필요하게 커지고 이득은 제한적입니다.

---

## 고정 크기 청킹 직접 구현하기

![Fixed size chunking execution flow](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/05/05-02-fixed-size-chunking-from-scratch.ko.png)

*고정 크기 청킹 실행 흐름*
먼저 가장 단순한 구현으로 개념을 고정해 보겠습니다.

```python
def chunk_text(
    text: str,
    chunk_size: int = 200,
    chunk_overlap: int = 20,
) -> list[str]:
    """Fixed-size chunking by character count."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk:
            chunks.append(chunk)
        start += chunk_size - chunk_overlap
    return chunks

sample_text = (
    "Vector search converts text into numeric vectors for meaning-based retrieval. "
    "Embedding models place semantically similar text close together in vector space. "
    "FAISS is a high-speed vector search library developed at Facebook AI Research. "
    "Chunking strategies split long documents into units the embedding model can process. "
    "Choosing the right chunk size improves retrieval accuracy. "
    "Overlap settings reduce context loss at chunk boundaries."
)

chunks = chunk_text(sample_text, chunk_size=100, chunk_overlap=20)

print(f"total text length: {len(sample_text)} chars")
print(f"number of chunks: {len(chunks)}")
for i, chunk in enumerate(chunks):
    print(f"\n[{i}] {len(chunk)} chars: {chunk[:60]}...")
```

<!-- injected-output:start -->
**출력 결과**

    total text length: 439 chars
    number of chunks: 6

    [0] 100 chars: Vector search converts text into numeric vectors for meaning...

    [1] 100 chars: bedding models place semantically similar text close togethe...

    [2] 100 chars: AISS is a high-speed vector search library developed at Face...

    [3] 100 chars: unking strategies split long documents into units the embedd...

    [4] 100 chars: s. Choosing the right chunk size improves retrieval accuracy...

    [5] 39 chars: educe context loss at chunk boundaries....

<!-- injected-output:end -->

이 구현은 설명용으로는 좋지만, 실제 서비스용으로는 부족합니다. 문자 수 기준으로 자르기 때문에 문장을 중간에서 잘라 버릴 수 있기 때문입니다. 실전에서는 다음 방식이 더 낫습니다.

---

## RecursiveCharacterTextSplitter

![Separator priority fallback path](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/05/05-03-recursivecharactertextsplitter.ko.png)

*분리자 우선순위 하향 경로*
LangChain의 `RecursiveCharacterTextSplitter`는 자연스러운 경계에서 나누려고 시도합니다. 먼저 `\n\n`, 그다음 `\n`, 그다음 `. `, 공백, 마지막으로 개별 문자 순으로 우선순위를 내려갑니다. 그래서 대부분의 경우 문장을 온전히 유지할 수 있습니다.

```bash
pip install langchain-text-splitters
```

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=30,
    length_function=len,
    separators=["\n\n", "\n", ". ", " ", ""],
)

document = """
Vector search converts text into numeric vectors for meaning-based retrieval.
Unlike keyword search, it matches content even when phrasing differs.

Embedding models place semantically similar text close together in vector space.
The sentence-transformers library provides models specialized for sentence-level embeddings.
all-MiniLM-L6-v2 is a lightweight model practical for CPU inference.

FAISS is a high-speed vector search library developed at Facebook AI Research.
It supports both exact and approximate search and can handle billions of vectors.
IndexFlatIP is an exact inner-product index equivalent to cosine search on normalized vectors.
"""

chunks = splitter.split_text(document)

print(f"number of chunks: {len(chunks)}")
for i, chunk in enumerate(chunks):
    print(f"\n[{i}] {len(chunk)} chars:")
    print(f"  {chunk[:80]}...")
```

<!-- injected-output:start -->
**출력 결과**

    number of chunks: 5

    [0] 147 chars:
      Vector search converts text into numeric vectors for meaning-based retrieval.
    Un...

    [1] 173 chars:
      Embedding models place semantically similar text close together in vector space....

    [2] 68 chars:
      all-MiniLM-L6-v2 is a lightweight model practical for CPU inference....

    [3] 160 chars:
      FAISS is a high-speed vector search library developed at Facebook AI Research.
    I...

    [4] 94 chars:
      IndexFlatIP is an exact inner-product index equivalent to cosine search on norma...

<!-- injected-output:end -->

`separators` 리스트는 순서대로 시도됩니다. `\n\n`으로 나눈 결과가 `chunk_size` 안에 들어오면 그 분할을 사용하고, 아니면 다음 분리자를 시도합니다. 결과적으로 문단이나 문장 경계에서 끝나는 청크를 만들 가능성이 높아집니다.

---

## 전체 흐름: 청킹에서 FAISS까지

![Execution path from chunking to FAISS search](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/05/05-04-full-pipeline-chunking-to-faiss.ko.png)

*청킹에서 FAISS 검색까지의 실행 경로*
청킹, 임베딩, 인덱싱을 한 블록으로 연결해 보겠습니다.

```python
import json

import faiss
import numpy as np
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=30,
    separators=["\n\n", "\n", ". ", " ", ""],
)

document = """
Vector search converts text into numeric vectors for meaning-based retrieval.
Unlike keyword search, it matches content even when phrasing differs.

Embedding models place semantically similar text close together in vector space.
The sentence-transformers library provides models specialized for sentence-level embeddings.

FAISS is a high-speed vector search library developed at Facebook AI Research.
It supports both exact and approximate search and can handle billions of vectors.

Chunking strategies split long documents into units the embedding model can process.
Tuning chunk_size and chunk_overlap is necessary to achieve good retrieval quality.
"""

chunks = splitter.split_text(document)
print(f"chunks: {len(chunks)}")

vectors = np.array(embedding_model.embed_documents(chunks), dtype=np.float32)
dimension = vectors.shape[1]

index = faiss.IndexFlatIP(dimension)
index.add(vectors)

def search(query: str, top_k: int = 3) -> list[tuple[float, str]]:
    q_vec = np.array([embedding_model.embed_query(query)], dtype=np.float32)
    scores, indices = index.search(q_vec, top_k)
    return [
        (float(scores[0][i]), chunks[indices[0][i]])
        for i in range(top_k)
        if indices[0][i] != -1
    ]

for query in ["how vector search works", "FAISS library features", "setting chunk size"]:
    print(f"\nquery: '{query}'")
    for rank, (score, text) in enumerate(search(query, top_k=2), start=1):
        print(f"  [{rank}] {score:.4f} — {text[:60]}...")
```

<!-- injected-output:start -->
**출력 결과**

    chunks: 4

    query: 'how vector search works'
      [1] 0.6897 — Vector search converts text into numeric vectors for meaning...
      [2] 0.5140 — FAISS is a high-speed vector search library developed at Fac...

    query: 'FAISS library features'
      [1] 0.5687 — FAISS is a high-speed vector search library developed at Fac...
      [2] 0.1739 — Chunking strategies split long documents into units the embe...

    query: 'setting chunk size'
      [1] 0.5347 — Chunking strategies split long documents into units the embe...
      [2] 0.0345 — FAISS is a high-speed vector search library developed at Fac...

<!-- injected-output:end -->

---

## 청크에 메타데이터를 함께 저장하기

검색 결과를 사용자에게 보여 주려면 텍스트 조각만 있어서는 부족한 경우가 많습니다. 어느 문서에서 왔는지, 몇 번째 섹션인지, 원문 안에서 어느 위치인지 같은 정보가 함께 있어야 인용과 디버깅이 쉬워집니다.

```python
from dataclasses import asdict, dataclass

@dataclass
class ChunkRecord:
    chunk_id: str
    source: str
    section: str
    offset: int
    text: str

def build_chunk_records(chunks: list[str]) -> list[dict]:
    records = []
    for idx, chunk in enumerate(chunks):
        records.append(
            asdict(
                ChunkRecord(
                    chunk_id=f"doc-001-{idx}",
                    source="vector-search-notes.md",
                    section="FAISS basics" if idx < 2 else "chunking",
                    offset=idx * 170,
                    text=chunk,
                )
            )
        )
    return records

records = build_chunk_records(chunks)
print(records[0])
```

<!-- injected-output:start -->
**출력 결과**

    {'chunk_id': 'doc-001-0', 'source': 'vector-search-notes.md', 'section': 'FAISS basics', 'offset': 0, 'text': 'Vector search converts text into numeric vectors for meaning-based retrieval.\nUnlike keyword search, it matches content even when phrasing differs.'}

<!-- injected-output:end -->

이런 메타데이터는 검색 정확도를 직접 올리지는 않지만, 운영 품질을 크게 높입니다. 같은 결과라도 "어디에서 왔는지"가 보이면 사람이 훨씬 빠르게 검토할 수 있기 때문입니다.

## chunk_size를 바꾸면 결과가 어떻게 달라지는가

청킹 전략은 결국 검색 결과로 검증해야 합니다. 작은 예제로 `chunk_size`를 두 개만 바꿔도 어떤 차이가 나는지 확인해 보겠습니다.

```python
import faiss
import numpy as np
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

document = """
Vector search converts text into numeric vectors for meaning-based retrieval.
Unlike keyword search, it matches content even when phrasing differs.

FAISS is a high-speed vector search library developed at Facebook AI Research.
It supports both exact and approximate search.

Chunking strategies decide how much context each vector should carry.
Large chunks preserve context but can mix unrelated details.
Small chunks are precise but may lose the sentence that explains the point.
"""

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

def run_experiment(chunk_size: int) -> None:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=30,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_text(document)
    vectors = np.array(embedding_model.embed_documents(chunks), dtype=np.float32)
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)

    query = "why chunk size affects retrieval quality"
    q_vec = np.array([embedding_model.embed_query(query)], dtype=np.float32)
    scores, indices = index.search(q_vec, 2)

    print(f"\nchunk_size={chunk_size}, chunks={len(chunks)}")
    for score, idx in zip(scores[0], indices[0]):
        print(f"  {score:.4f} | {chunks[idx][:70]}")

run_experiment(120)
run_experiment(260)
```

<!-- injected-output:start -->
**출력 결과**

    chunk_size=120, chunks=5
      0.6908 | Chunking strategies decide how much context each vector should carry.
      0.3707 | Large chunks preserve context but can mix unrelated details.

    chunk_size=260, chunks=3
      0.6402 | Chunking strategies decide how much context each vector should carry.
      0.4684 | FAISS is a high-speed vector search library developed at Facebook AI Research.

<!-- injected-output:end -->

작은 청크는 더 직접적인 답을 올려 주지만, 큰 청크는 주변 문맥을 더 많이 끌고 옵니다. 실제 데이터에서 어느 쪽이 더 좋은지는 질문 유형에 따라 달라집니다. FAQ처럼 짧고 정확한 답을 찾는 시스템과 정책 문서를 길게 읽는 시스템은 최적값이 다를 수밖에 없습니다.

## 청크 크기가 검색 품질에 미치는 영향

![Retrieval quality across chunk sizes](https://yeongseon-books.github.io/book-public-assets/assets/vector-search-101/05/05-05-how-chunk-size-affects-retrieval.ko.png)

*청크 크기별 검색 품질 비교*
청크가 너무 작으면 쿼리와 정확히 매칭될 만큼의 문맥이 없습니다. 반대로 청크가 너무 크면 관련 없는 내용이 섞여 의미 신호가 희석됩니다.

일반적인 시작값은 다음과 같습니다.

| 문서 유형 | chunk_size | chunk_overlap |
|---|---|---|
| 짧은 문단, 뉴스 | 200–300 | 20–30 |
| 기술 문서, 매뉴얼 | 300–500 | 30–50 |
| 법률 문서, 논문 | 500–800 | 50–100 |

적당한 기본값에서 시작한 뒤 실제 데이터로 검색 품질을 측정하고 조정하는 것이 정석입니다. 청킹 파라미터에는 모든 상황에 통하는 보편적 최적값이 없습니다.

---

## 마무리

청킹은 벡터 검색 시스템에서 검색 품질을 바꾸는 가장 큰 레버인 경우가 많습니다. 임베딩 모델과 인덱스 유형도 중요하지만, 입력 자체를 잘못 나누면 어떤 모델도 좋은 결과를 내기 어렵습니다.

마지막 글에서는 문서 로딩, 청킹, 임베딩, 인덱싱, 쿼리를 하나의 엔드 투 엔드 파이프라인으로 조립합니다.

## 운영 체크리스트

- [ ] 청크 크기와 오버랩을 임베딩 모델의 토큰 한도 기준으로 정했다
- [ ] 헤딩, 페이지 같은 구조 정보를 청크 메타데이터에 보존했다
- [ ] 코드와 표는 일반 문단과 다른 청킹 규칙을 적용했다
- [ ] 같은 문서에서 나온 거의 동일한 청크를 중복 제거했다
- [ ] 출처 추적을 위해 문서 ID와 오프셋을 함께 저장했다

## 처음 질문으로 돌아가기

- **긴 문서를 그대로 임베딩하지 않고 왜 청크로 나눠야 할까요?**
  모델에는 토큰 한도가 있고, 긴 문서 하나를 통째로 임베딩하면 필요한 부분이 희석되거나 잘릴 수 있습니다. 청크는 검색 단위를 작게 만들어 관련 위치를 찾게 합니다.

- **chunk_size와 overlap은 검색 품질과 비용 사이에서 어떤 균형을 만들까요?**
  큰 chunk_size는 맥락을 많이 담지만 비용과 노이즈가 커지고, 작은 chunk_size는 정확한 위치를 찾기 쉽지만 맥락이 끊길 수 있습니다. overlap은 그 끊김을 줄이는 비용입니다.

- **청크에 메타데이터를 붙이지 않으면 답변 경로에서 무엇이 막힐까요?**
  문서 ID, 제목, 위치, URL 같은 메타데이터가 없으면 검색된 청크를 사용자에게 설명하거나 원문으로 되돌아가는 경로가 막힙니다.

<!-- toc:begin -->
## 시리즈 목차

- [Vector Search 101 (1/6): 임베딩이란 무엇인가 — 텍스트를 벡터로 변환하기](./01-what-is-embedding.md)
- [Vector Search 101 (2/6): HuggingFace 임베딩 실습 — sentence-transformers로 첫 벡터 만들기](./02-huggingface-embeddings.md)
- [Vector Search 101 (3/6): 코사인 유사도와 벡터 검색 — 문장 간 거리 계산하기](./03-cosine-similarity.md)
- [Vector Search 101 (4/6): FAISS 입문 — 고속 근사 최근접 이웃 검색](./04-faiss-fundamentals.md)
- **Vector Search 101 (5/6): 청크 전략 — 긴 문서를 어떻게 나눌 것인가 (현재 글)**
- Vector Search 101 (6/6): 벡터 검색 파이프라인 — 문서 수집부터 쿼리까지 (예정)

<!-- toc:end -->

---

## 참고 자료

- [LangChain RecursiveCharacterTextSplitter](https://python.langchain.com/docs/modules/data_connection/document_transformers/recursive_text_splitter/)
- [Chunking strategies for LLM applications — Pinecone](https://www.pinecone.io/learn/chunking-strategies/)
- [Sentence Transformers pretrained models](https://www.sbert.net/docs/sentence_transformer/pretrained_models.html)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/vector-search-101/ko/05-chunking-strategies)

Tags: Vector Search, FAISS, Embeddings, Python
