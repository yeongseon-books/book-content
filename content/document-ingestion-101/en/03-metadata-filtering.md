---
title: 'Metadata design and filtering'
series: document-ingestion-101
episode: 3
language: en
status: draft
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- RAG
- Document Processing
- LangChain
- Python
last_reviewed: '2026-05-01'
---

# Metadata design and filtering

> Document Ingestion 101 (3/6)

Consider the query "find marketing-related content from the Q4 2024 report." Embedding similarity alone cannot filter by date and category simultaneously. Metadata filtering handles this: attach structured metadata to each chunk, then apply metadata conditions alongside semantic similarity at query time.

Topics:

- designing a metadata schema
- attaching metadata to chunks
- post-retrieval metadata filtering with FAISS
- filtering by date, category, and source

---

## Designing a metadata schema

A good schema predefines the filter conditions you will use at query time.

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class DocumentMetadata:
    # identifiers
    doc_id: str
    chunk_id: str

    # source
    source_file: str
    source_type: str          # pdf, txt, html, docx

    # content classification
    category: str             # legal, news, technical, faq
    subcategory: Optional[str] = None

    # dates
    created_date: Optional[str] = None   # ISO 8601: "2024-01-15"
    modified_date: Optional[str] = None

    # position
    page_num: Optional[int] = None
    chunk_idx: int = 0

    # quality signals
    char_count: int = 0
    language: str = "en"

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if v is not None}

meta = DocumentMetadata(
    doc_id="doc_001",
    chunk_id="doc_001_chunk_003",
    source_file="2024q4_report.pdf",
    source_type="pdf",
    category="business",
    subcategory="marketing",
    created_date="2024-10-01",
    page_num=5,
    chunk_idx=3,
    char_count=320,
    language="en",
)
print(meta.to_dict())
```

---

## Attaching metadata to chunks

```python
import hashlib
from datetime import datetime
from pathlib import Path

import fitz
from langchain.schema import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

def load_pdf_with_metadata(
    pdf_path: str,
    category: str,
    chunk_size: int = 400,
    chunk_overlap: int = 80,
) -> list[Document]:
    """
    Load a PDF and return LangChain Documents with per-chunk metadata.
    """
    pdf_path = Path(pdf_path)
    doc = fitz.open(str(pdf_path))

    file_stat = pdf_path.stat()
    pdf_meta = {
        "source_file": pdf_path.name,
        "source_type": "pdf",
        "category": category,
        "page_count": len(doc),
        "file_size_kb": file_stat.st_size // 1024,
        "modified_date": datetime.fromtimestamp(file_stat.st_mtime).strftime("%Y-%m-%d"),
    }

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". "],
    )

    langchain_docs = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text").strip()
        if not text:
            continue

        chunks = splitter.split_text(text)
        for chunk_idx, chunk in enumerate(chunks):
            chunk_hash = hashlib.md5(chunk.encode()).hexdigest()[:8]
            chunk_id = f"{pdf_path.stem}_p{page_num + 1}_c{chunk_idx}_{chunk_hash}"

            metadata = {
                **pdf_meta,
                "page_num": page_num + 1,
                "chunk_idx": chunk_idx,
                "chunk_id": chunk_id,
                "char_count": len(chunk),
            }
            langchain_docs.append(Document(page_content=chunk, metadata=metadata))

    doc.close()
    return langchain_docs

docs = load_pdf_with_metadata("/tmp/sample_en.pdf", category="technical")
print(f"documents created: {len(docs)}")
for doc in docs[:2]:
    print(f"\nchunk id: {doc.metadata['chunk_id']}")
    print(f"metadata: {doc.metadata}")
    print(f"content: {doc.page_content[:100]}...")
```

---

## Post-retrieval metadata filtering

FAISS's native metadata filtering is limited. The standard approach is to retrieve more candidates than needed, then filter by metadata in Python.

```python
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document

def build_index_with_metadata(documents: list[Document]) -> FAISS:
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
    vectorstore = FAISS.from_documents(documents, embedding_model)
    print(f"index ready: {vectorstore.index.ntotal} vectors")
    return vectorstore

def filtered_search(
    vectorstore: FAISS,
    query: str,
    k: int = 10,
    filter_fn=None,
) -> list[Document]:
    """
    Semantic search followed by metadata filter.
    filter_fn: Document -> bool
    """
    results = vectorstore.similarity_search(query, k=k)
    if filter_fn:
        results = [doc for doc in results if filter_fn(doc)]
    return results

# Build a mixed-category index
all_docs = [
    Document(
        page_content="Implementing async HTTP clients with Python asyncio.",
        metadata={"category": "technical", "source_file": "python_async.pdf", "page_num": 1, "created_date": "2024-01-15"},
    ),
    Document(
        page_content="FAISS IVF indexing speeds up large-scale vector search.",
        metadata={"category": "technical", "source_file": "faiss_guide.pdf", "page_num": 3, "created_date": "2024-03-10"},
    ),
    Document(
        page_content="Personal information means any information that identifies a living individual.",
        metadata={"category": "legal", "source_file": "privacy_law.pdf", "page_num": 1, "created_date": "2023-09-01"},
    ),
    Document(
        page_content="A controller may not provide personal information to a third party without consent.",
        metadata={"category": "legal", "source_file": "privacy_law.pdf", "page_num": 5, "created_date": "2023-09-01"},
    ),
]

vectorstore = build_index_with_metadata(all_docs)

# Filter: technical documents only
tech_results = filtered_search(
    vectorstore,
    query="vector search methods",
    k=10,
    filter_fn=lambda doc: doc.metadata.get("category") == "technical",
)
print(f"\ntechnical filter results: {len(tech_results)}")
for r in tech_results:
    print(f"  [{r.metadata['category']}] {r.page_content[:60]}")

# Filter: documents from 2024 or later
recent_results = filtered_search(
    vectorstore,
    query="async processing",
    k=10,
    filter_fn=lambda doc: doc.metadata.get("created_date", "0") >= "2024",
)
print(f"\n2024+ documents: {len(recent_results)}")
for r in recent_results:
    print(f"  [{r.metadata['created_date']}] {r.page_content[:60]}")
```

---

## Conclusion

Metadata covers the cases where semantic similarity fails: time ranges, category constraints, source filters. Design the schema when designing the chunking pipeline — adding metadata retroactively requires reindexing every document. The next post covers incremental indexing: processing only documents that have changed rather than rebuilding the index from scratch.

<!-- toc:begin -->
## In this series

- [PDF parsing and text extraction](./01-pdf-parsing.md)
- [Chunking strategies — optimizing by document type](./02-chunking-strategies.md)
- **Metadata design and filtering (current)**
- Incremental indexing — updating only changed documents (upcoming)
- Multi-format document pipeline (upcoming)
- Completing the document ingestion pipeline (upcoming)

<!-- toc:end -->

---

## References

- [LangChain Document loaders](https://python.langchain.com/docs/modules/data_connection/document_loaders/)
- [FAISS metadata filtering](https://python.langchain.com/docs/integrations/vectorstores/faiss/)
- [RAG metadata filtering strategy (Pinecone)](https://www.pinecone.io/learn/metadata-filtering/)

Tags: RAG, Document Processing, LangChain, Python
