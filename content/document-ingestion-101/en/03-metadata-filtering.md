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
