---
title: "Document Ingestion 101 (3/6): Metadata design and filtering"
series: document-ingestion-101
episode: 3
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- RAG
- Document Processing
- LangChain
- Python
last_reviewed: '2026-05-15'
seo_description: Metadata is not decoration around the text; it is the first index
  that shrinks the candidate set.
---

# Document Ingestion 101 (3/6): Metadata design and filtering

Good retrieval is not only about semantic similarity. In production, engineers also need explicit ways to narrow results by scope, source, and time window before ranking becomes useful.

This is the third post in the Document Ingestion 101 series. Here, we design a practical metadata shape and show how filtering changes retrieval behavior in a visible way.

![Retrieval metadata schema flow](https://yeongseon-books.github.io/book-public-assets/assets/document-ingestion-101/03/03-01-metadata-schema-design.en.png)
*Retrieval metadata schema flow*
> Metadata is not decoration around the text; it is the first index that shrinks the candidate set.

## Questions to Keep in Mind

- Why should metadata schema be designed during ingestion rather than after embedding?
- How do filters change the candidate set before vector similarity search?
- What breaks in retrieval and citation when required metadata is missing?

## Metadata schema design

The schema is less about collecting many fields and more about keeping the few keys that actually shrink the candidate set.

## How filters narrow the candidate set

![Filtered retrieval candidate flow](https://yeongseon-books.github.io/book-public-assets/assets/document-ingestion-101/03/03-02-how-filters-narrow-the-candidate-set.en.png)

*Filtered retrieval candidate flow*
Even when multiple chunks are semantically similar, filters stabilize retrieval by narrowing scope before ranking.

## Runnable example

```python
from __future__ import annotations

import hashlib
from dataclasses import dataclass

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

class SimpleHashEmbeddings(Embeddings):
    def __init__(self, size: int = 32):
        self.size = size

    def _embed(self, text: str) -> list[float]:
        vector = [0.0] * self.size
        for token in text.lower().split():
            digest = hashlib.sha256(token.encode('utf-8')).digest()
            for index in range(self.size):
                vector[index] += digest[index] / 255.0
        return vector

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)

@dataclass
class ChunkSpec:
    title: str
    text: str
    category: str
    quarter: str
    source: str

    def to_document(self) -> Document:
        metadata = {
            'title': self.title,
            'category': self.category,
            'quarter': self.quarter,
            'source': self.source,
        }
        return Document(page_content=self.text, metadata=metadata)

def build_vectorstore() -> FAISS:
    docs = [
        ChunkSpec(
            title='Q4 marketing budget',
            text='The 2024 Q4 marketing budget focuses on campaign spend and partner events.',
            category='marketing',
            quarter='2024Q4',
            source='q4-report.pdf',
        ).to_document(),
        ChunkSpec(
            title='Q4 infrastructure cost',
            text='The 2024 Q4 infrastructure budget focuses on storage migration and backup cost.',
            category='engineering',
            quarter='2024Q4',
            source='q4-report.pdf',
        ).to_document(),
        ChunkSpec(
            title='Q3 marketing review',
            text='The 2024 Q3 marketing review summarizes webinar leads and conversion rate.',
            category='marketing',
            quarter='2024Q3',
            source='q3-review.md',
        ).to_document(),
    ]
    return FAISS.from_documents(docs, SimpleHashEmbeddings())

def main() -> None:
    vectorstore = build_vectorstore()
    query = 'marketing budget'

    print('[filter=category:marketing]')
    for doc in vectorstore.similarity_search(query, k=3, filter={'category': 'marketing'}):
        print(doc.metadata['title'], doc.metadata['quarter'], '-', doc.page_content)

    print('\n[filter=quarter:2024Q4]')
    for doc in vectorstore.similarity_search(query, k=3, filter={'quarter': '2024Q4'}):
        print(doc.metadata['title'], doc.metadata['category'], '-', doc.page_content)

if __name__ == '__main__':
    main()
```

## How to run it

```bash
python main.py
```

## Verified run output

```text
[filter=category:marketing]
Q3 marketing review 2024Q3 - ...
Q4 marketing budget 2024Q4 - ...

[filter=quarter:2024Q4]
Q4 marketing budget marketing - ...
Q4 infrastructure cost engineering - ...
```

## What to notice in this code

### How similarity and filters combine

![Similarity and filter processing flow](https://yeongseon-books.github.io/book-public-assets/assets/document-ingestion-101/03/03-01-how-similarity-and-filters-combine.en.png)

*Similarity and filter processing flow*
Similarity and filtering work best as separate stages with a visible order, not as one opaque retrieval step.

- `ChunkSpec` keeps text and metadata together, so the retrieval schema is visible in one place.
- `SimpleHashEmbeddings` keeps the demo offline while still exercising the real `filter` path.
- The key observation is that the same query yields different result sets once the filter changes.

## Where engineers get confused

### How source tracking supports audits

![Source tracking and audit path](https://yeongseon-books.github.io/book-public-assets/assets/document-ingestion-101/03/03-02-how-source-tracking-supports-audits.en.png)

*Source tracking and audit path*
When an answer looks wrong, source and scope metadata usually explain the failure faster than the chunk text alone.

- More metadata is not automatically better. Keep the fields you will actually filter on.
- When retrieval looks wrong, the issue may be the candidate set rather than the embedding model.
- FAISS is not a relational database, so richer conditions still need application-level design around it.

## Checklist

- [ ] Your chunk metadata includes at least category, quarter, and source.
- [ ] You compared different filter results against the same query.
- [ ] Field names stay consistent between document creation and retrieval.
- [ ] You trimmed the schema to fields that are operationally useful.

## VectorDB filter design and auditable schema

Metadata filters are not simple search options — they are access-scope controls. In multi-tenant environments, a missing filter lets other organizations' documents leak into search candidates. Schema and query builder must be managed together.

### Separating filterable fields from display-only fields

Putting every metadata field into the filter index inflates indexing cost and query complexity. In production, split roles:

- Filterable: `tenant`, `doc_type`, `category`, `quarter`, `language`, `version`
- Display-only: `title`, `author`, `uploaded_by`, `summary`

Filterable fields require value normalization. Display-only fields extend user experience. Without this separation, filter expressions grow unnecessarily complex and query performance becomes unpredictable.

### Enforcing filter conditions at the application layer

The example below is a filter compiler that always includes the tenant condition. Even if a client omits it, the server enforces it.

```python
from __future__ import annotations

from typing import Any

def compile_filter(
    *, tenant: str, category: str | None, quarter: str | None
) -> dict[str, Any]:
    clauses: list[dict[str, str]] = [{'tenant': tenant.lower()}]
    if category:
        clauses.append({'category': category.lower()})
    if quarter:
        clauses.append({'quarter': quarter.upper().replace('-', '')})
    return {'$and': clauses}

def search_with_guard(
    vectorstore: Any, query: str, tenant: str
) -> list[Any]:
    filter_query = compile_filter(
        tenant=tenant, category='marketing', quarter='2024Q4'
    )
    return vectorstore.similarity_search(query, k=8, filter=filter_query)
```

The critical point: do not build filters only in the UI. The backend must enforce minimum security/scope conditions so that search boundaries hold even on exception paths.

### Why metadata schema versioning matters

Field structure changes over time. The moment you merge `department` into `category` or add `region`, old and new index entries can mix. A schema version field enables migration path separation.

```json
{
  "source": "q4-report.pdf",
  "tenant": "acme",
  "category": "marketing",
  "quarter": "2024Q4",
  "language": "ko",
  "version": "v3",
  "schema_version": "metadata-v2"
}
```

The search service can select compatible filters by `schema_version` or classify old-version documents as re-indexing targets. Without this mechanism, field name changes immediately become search outages.

### Connecting audit logs to search logs

Recording how metadata filters were actually used accelerates incident response.

```python
def emit_search_audit(
    *, query: str, filter_query: dict[str, object],
    user_id: str, request_id: str,
) -> None:
    print(
        {
            'event': 'vector_search',
            'request_id': request_id,
            'user_id': user_id,
            'query': query,
            'filter': filter_query,
        }
    )
```

This log is the minimum material for reproducing "why did this result appear." Filter design must consider auditability alongside search accuracy.

## Metadata filters and permission boundaries

Metadata filters protect not just relevance but permission boundaries. In B2B environments, omitting `tenant`, `workspace`, or `visibility` fields risks mixing other customers' documents into the candidate set.

```python
def build_access_filter(
    *, tenant: str, workspace: str, visibility: str = 'internal'
) -> dict[str, object]:
    return {
        '$and': [
            {'tenant': tenant.lower()},
            {'workspace': workspace.lower()},
            {'visibility': visibility.lower()},
        ]
    }
```

This filter is not a "search option" — it is minimum access control. The application layer must always attach it, and audit logs must always record it.

Also check filter-value cardinality early in operations. If `quarter` should have 5 distinct values but has grown to 27, normalization is broken. Metadata quality caught strictly at indexing time greatly improves subsequent search stability.

## Extended deployment checklist

- Input file count within normal range.
- Failed document ratio below threshold (e.g. 3%).
- At least 3 sample documents traceable by source, page, chunk_id.
- Zero missing required metadata fields (`source`, `format`, `doc_type`).
- Smoke-test queries return expected sources in top results.

```python
def quick_health_report(stats: dict[str, int | float]) -> None:
    print(f"files_total={stats['files_total']}")
    print(f"failed_total={stats['failed_total']}")
    print(f"chunks_total={stats['chunks_total']}")
    print(f"metadata_missing={stats['metadata_missing']}")
    print(f"smoke_passed={stats['smoke_passed']}")
```

## Operational baseline metrics

- Parsing quality: average character count, OCR ratio, reprocessing ratio
- Chunking quality: average length, extreme-length ratio, policy version distribution
- Metadata quality: required-field miss rate, normalization failure count
- Retrieval verification: sample query recall@k, source hit rate

Stable ingestion comes from continuously measuring input quality and stage contracts, not from model selection.

## Combining filters and similarity scores in VectorDB queries

After filters narrow the candidate set, adding a similarity-score threshold removes one more layer of noise. In practice, fixing `score_threshold` as a single constant is less stable than varying it by query type.

```python
from __future__ import annotations

from typing import Any

def search_with_threshold(
    vectorstore: Any,
    query: str,
    filter_query: dict[str, Any],
    score_threshold: float = 0.72,
    k: int = 8,
) -> list[Any]:
    docs_and_scores = vectorstore.similarity_search_with_score(
        query, k=k, filter=filter_query
    )
    return [
        (doc, score)
        for doc, score in docs_and_scores
        if score >= score_threshold
    ]
```

This prevents chunks that pass the filter but are semantically distant from contaminating final answers. Setting the threshold too high drops recall, so validate with a sample query set first.

## Answering the Opening Questions

- **Why should metadata schema be designed during ingestion rather than after embedding?**
  Fields such as source, doc_type, date, and owner must be assigned during ingestion so every chunk and index shares the same filter contract.

- **How do filters change the candidate set before vector similarity search?**
  Filters reduce the document candidate set before similarity scoring, preventing unrelated records from competing in the top results.

- **What breaks in retrieval and citation when required metadata is missing?**
  Missing metadata makes scoped retrieval, citation, page reference, and version tracking unreliable.

<!-- toc:begin -->
## In this series

- [Document Ingestion 101 (1/6): PDF parsing and text extraction](./01-pdf-parsing.md)
- [Document Ingestion 101 (2/6): Chunking strategies — optimizing by document type](./02-chunking-strategies.md)
- **Document Ingestion 101 (3/6): Metadata design and filtering (current)**
- Document Ingestion 101 (4/6): Incremental indexing — updating only changed documents (upcoming)
- Document Ingestion 101 (5/6): Multi-format document pipeline (upcoming)
- Document Ingestion 101 (6/6): Completing the document ingestion pipeline (upcoming)

<!-- toc:end -->

## References

### Official docs

- [LangChain FAISS integration guide](https://python.langchain.com/docs/integrations/vectorstores/faiss/)
- [LangChain Document object concepts](https://python.langchain.com/docs/concepts/documents/)

### Verification-friendly sources

- [FAISS documentation](https://faiss.ai/)
- [FAISS GitHub repository](https://github.com/facebookresearch/faiss)

Tags: RAG, Document Processing, LangChain, Python
