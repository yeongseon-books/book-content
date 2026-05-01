---
title: '메타데이터 설계와 필터링'
series: document-ingestion-101
episode: 3
language: ko
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

# 메타데이터 설계와 필터링

> 문서 수집과 인덱싱 101 시리즈 (3/6)

예제 코드: [github.com/yeongseon-books/document-ingestion-101](https://github.com/yeongseon-books/document-ingestion-101/tree/main/ko/03-metadata-filtering)

"2024년 4분기 보고서에서 마케팅 관련 내용을 찾아줘"라는 쿼리를 생각해 보세요. 임베딩만으로는 날짜와 카테고리를 동시에 필터링하기 어렵습니다. 메타데이터 필터링은 이런 경우를 위한 것입니다. 각 청크에 구조화된 메타데이터를 붙이고, 검색 시 메타데이터 조건과 의미 유사도를 함께 적용합니다.

다룰 내용은 다음과 같습니다.

- 메타데이터 스키마 설계
- 청크에 메타데이터 붙이기
- FAISS와 메타데이터 필터링
- 날짜, 카테고리, 출처 기반 필터링

---

## 메타데이터 스키마 설계

좋은 메타데이터 스키마는 검색 시 자주 쓰이는 필터 조건을 미리 정의합니다.

```python
from dataclasses import dataclass, field
from datetime import date
from typing import Optional

@dataclass
class DocumentMetadata:
    # 식별자
    doc_id: str
    chunk_id: str

    # 출처
    source_file: str
    source_type: str          # pdf, txt, html, docx

    # 내용 분류
    category: str             # legal, news, technical, faq
    subcategory: Optional[str] = None

    # 날짜
    created_date: Optional[str] = None   # ISO 8601: "2024-01-15"
    modified_date: Optional[str] = None

    # 위치 정보
    page_num: Optional[int] = None
    chunk_idx: int = 0

    # 품질 지표
    char_count: int = 0
    language: str = "ko"

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if v is not None}

# 메타데이터 생성 예시
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
    language="ko",
)
print(meta.to_dict())
```

---

## 청크에 메타데이터 붙이기

```python
import hashlib
import os
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
    PDF를 로드하고 각 청크에 메타데이터를 붙여 LangChain Document 목록으로 반환합니다.
    """
    pdf_path = Path(pdf_path)
    doc = fitz.open(str(pdf_path))

    # PDF 수준 메타데이터
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
            # 청크별 고유 ID 생성
            chunk_hash = hashlib.md5(chunk.encode()).hexdigest()[:8]
            chunk_id = f"{pdf_path.stem}_p{page_num+1}_c{chunk_idx}_{chunk_hash}"

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

# 샘플 PDF 생성 및 로드 (앞 글에서 만든 /tmp/sample.pdf 활용)
docs = load_pdf_with_metadata("/tmp/sample.pdf", category="technical")
print(f"생성된 Document 수: {len(docs)}")
for doc in docs[:2]:
    print(f"\n청크 ID: {doc.metadata['chunk_id']}")
    print(f"메타데이터: {doc.metadata}")
    print(f"내용: {doc.page_content[:100]}...")
```

---

## FAISS 메타데이터 필터링

FAISS는 자체 메타데이터 필터링 기능이 제한적입니다. LangChain의 FAISS 통합은 메타데이터를 저장하지만 필터링은 검색 후 후처리로 수행합니다.

```python
def build_index_with_metadata(documents: list[Document]) -> FAISS:
    """메타데이터가 포함된 FAISS 인덱스를 구성합니다."""
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    vectorstore = FAISS.from_documents(documents, embedding_model)
    print(f"인덱스 구성 완료: {vectorstore.index.ntotal}개 벡터")
    return vectorstore

def filtered_search(
    vectorstore: FAISS,
    query: str,
    k: int = 10,  # 더 많이 가져온 후 필터링
    filter_fn=None,
) -> list[Document]:
    """
    의미 유사도 검색 후 메타데이터 필터를 적용합니다.
    filter_fn: Document → bool
    """
    # 충분히 많은 결과를 가져옴
    results = vectorstore.similarity_search(query, k=k)

    if filter_fn:
        results = [doc for doc in results if filter_fn(doc)]

    return results

# 인덱스 구성 (여러 카테고리 문서 시뮬레이션)
all_docs = []

# 기술 문서
tech_docs_raw = [
    Document(
        page_content="파이썬 asyncio로 비동기 HTTP 클라이언트를 구현합니다.",
        metadata={"category": "technical", "source_file": "python_async.pdf", "page_num": 1, "created_date": "2024-01-15"},
    ),
    Document(
        page_content="FAISS 인덱스의 IVF 방식은 대규모 벡터 검색을 빠르게 합니다.",
        metadata={"category": "technical", "source_file": "faiss_guide.pdf", "page_num": 3, "created_date": "2024-03-10"},
    ),
]

# 법령 문서
legal_docs_raw = [
    Document(
        page_content="개인정보는 살아 있는 개인에 관한 정보로서 개인을 식별할 수 있는 정보입니다.",
        metadata={"category": "legal", "source_file": "privacy_law.pdf", "page_num": 1, "created_date": "2023-09-01"},
    ),
    Document(
        page_content="개인정보 처리자는 정보 주체의 동의 없이 개인정보를 제3자에게 제공할 수 없습니다.",
        metadata={"category": "legal", "source_file": "privacy_law.pdf", "page_num": 5, "created_date": "2023-09-01"},
    ),
]

all_docs = tech_docs_raw + legal_docs_raw
vectorstore = build_index_with_metadata(all_docs)

# 필터링 검색 예시
# 1. 기술 문서만 검색
tech_results = filtered_search(
    vectorstore,
    query="벡터 검색 방법",
    k=10,
    filter_fn=lambda doc: doc.metadata.get("category") == "technical",
)
print(f"\n기술 문서 필터 결과: {len(tech_results)}개")
for r in tech_results:
    print(f"  [{r.metadata['category']}] {r.page_content[:60]}")

# 2. 2024년 이후 문서만 검색
recent_results = filtered_search(
    vectorstore,
    query="비동기 처리",
    k=10,
    filter_fn=lambda doc: doc.metadata.get("created_date", "0") >= "2024",
)
print(f"\n2024년 이후 문서 결과: {len(recent_results)}개")
for r in recent_results:
    print(f"  [{r.metadata['created_date']}] {r.page_content[:60]}")
```

---

## 마무리

메타데이터는 의미 검색이 닿지 않는 범위를 커버합니다. "2024년 4분기" 같은 시간 필터, "법령" 같은 카테고리 필터는 임베딩 유사도만으로는 처리할 수 없습니다. 청크를 만들 때 메타데이터를 함께 설계하면 나중에 검색 품질을 크게 높일 수 있습니다.

다음 글에서는 증분 인덱싱을 다룹니다. 문서가 추가되거나 변경될 때 전체를 다시 인덱싱하지 않고 변경분만 처리하는 방법입니다.

<!-- toc:begin -->
## 시리즈 목차

- [PDF 파싱과 텍스트 추출](./01-pdf-parsing.md)
- [청킹 전략 — 문서 유형별 최적화](./02-chunking-strategies.md)
- **메타데이터 설계와 필터링 (현재 글)**
- 증분 인덱싱 — 변경된 문서만 업데이트 (예정)
- 다중 포맷 문서 파이프라인 (예정)
- 문서 수집 파이프라인 완성 (예정)

<!-- toc:end -->

---

## 참고 자료

- [LangChain Document](https://python.langchain.com/docs/modules/data_connection/document_loaders/)
- [FAISS 메타데이터 필터링](https://python.langchain.com/docs/integrations/vectorstores/faiss/)
- [RAG 메타데이터 설계 전략](https://www.pinecone.io/learn/metadata-filtering/)

Tags: RAG, Document Processing, LangChain, Python
