---
title: '다중 포맷 문서 파이프라인'
series: document-ingestion-101
episode: 5
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

# 다중 포맷 문서 파이프라인

> 문서 수집과 인덱싱 101 시리즈 (5/6)

예제 코드: [github.com/yeongseon-books/document-ingestion-101](https://github.com/yeongseon-books/document-ingestion-101/tree/main/ko/05-multi-format-pipeline)

실제 서비스에서는 PDF 하나만 처리하지 않습니다. Word 문서, HTML 페이지, Markdown 파일, 텍스트 파일이 한 번에 들어옵니다. 각 포맷마다 적절한 파서를 선택하고 공통 포맷으로 변환하는 파이프라인이 필요합니다.

다룰 내용은 다음과 같습니다.

- 포맷별 LangChain DocumentLoader
- 포맷 자동 감지
- 통합 문서 처리 파이프라인
- HTML에서 불필요한 태그 제거

---

## LangChain DocumentLoader 목록

LangChain은 다양한 포맷을 위한 DocumentLoader를 제공합니다.

```python
# 주요 DocumentLoader
from langchain_community.document_loaders import (
    PyMuPDFLoader,           # PDF — 가장 정확
    Docx2txtLoader,          # Word (.docx)
    UnstructuredHTMLLoader,  # HTML (unstructured 패키지 필요)
    BSHTMLLoader,            # HTML (BeautifulSoup4)
    TextLoader,              # 텍스트 파일
    UnstructuredMarkdownLoader,  # Markdown
    CSVLoader,               # CSV
    JSONLoader,              # JSON
)
```

---

## 포맷별 로더 구현

```python
import os
from pathlib import Path

from langchain.schema import Document
from langchain_community.document_loaders import (
    BSHTMLLoader,
    Docx2txtLoader,
    PyMuPDFLoader,
    TextLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter

def load_pdf(file_path: str) -> list[Document]:
    """PDF 파일을 로드합니다."""
    loader = PyMuPDFLoader(file_path)
    docs = loader.load()
    # source 메타데이터 표준화
    for doc in docs:
        doc.metadata["format"] = "pdf"
        doc.metadata["source"] = Path(file_path).name
    return docs

def load_word(file_path: str) -> list[Document]:
    """Word (.docx) 파일을 로드합니다."""
    loader = Docx2txtLoader(file_path)
    docs = loader.load()
    for doc in docs:
        doc.metadata["format"] = "docx"
        doc.metadata["source"] = Path(file_path).name
    return docs

def load_html(file_path: str) -> list[Document]:
    """HTML 파일에서 텍스트를 추출합니다. 스크립트와 스타일 태그를 제거합니다."""
    loader = BSHTMLLoader(file_path, bs_kwargs={"features": "html.parser"})
    docs = loader.load()
    for doc in docs:
        doc.metadata["format"] = "html"
        doc.metadata["source"] = Path(file_path).name
    return docs

def load_text(file_path: str, encoding: str = "utf-8") -> list[Document]:
    """텍스트 파일을 로드합니다."""
    loader = TextLoader(file_path, encoding=encoding)
    docs = loader.load()
    for doc in docs:
        doc.metadata["format"] = "txt"
        doc.metadata["source"] = Path(file_path).name
    return docs

def load_markdown(file_path: str) -> list[Document]:
    """Markdown 파일을 로드합니다."""
    # Markdown은 TextLoader로 충분
    loader = TextLoader(file_path, encoding="utf-8")
    docs = loader.load()
    for doc in docs:
        doc.metadata["format"] = "md"
        doc.metadata["source"] = Path(file_path).name
    return docs
```

---

## 포맷 자동 감지 라우터

```python
LOADER_MAP = {
    ".pdf": load_pdf,
    ".docx": load_word,
    ".doc": load_word,
    ".html": load_html,
    ".htm": load_html,
    ".txt": load_text,
    ".md": load_markdown,
    ".markdown": load_markdown,
}

def load_document(file_path: str) -> list[Document]:
    """
    파일 확장자를 보고 적절한 로더를 선택해서 문서를 로드합니다.
    """
    suffix = Path(file_path).suffix.lower()
    loader_fn = LOADER_MAP.get(suffix)

    if loader_fn is None:
        raise ValueError(f"지원하지 않는 파일 포맷: {suffix}\n지원 포맷: {list(LOADER_MAP.keys())}")

    docs = loader_fn(file_path)
    print(f"  [{suffix[1:].upper()}] {Path(file_path).name}: {len(docs)}개 페이지/섹션 로드")
    return docs
```

---

## 통합 파이프라인

```python
import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

def process_directory(
    directory: str,
    patterns: list[str] = None,
    chunk_size: int = 400,
    chunk_overlap: int = 80,
) -> FAISS:
    """
    디렉터리의 모든 지원 문서를 로드, 청킹, 인덱싱합니다.
    """
    if patterns is None:
        patterns = ["*.pdf", "*.docx", "*.html", "*.txt", "*.md"]

    directory = Path(directory)
    all_files = []
    for pattern in patterns:
        all_files.extend(directory.glob(pattern))

    print(f"발견된 파일: {len(all_files)}개")

    all_docs = []
    for file_path in all_files:
        try:
            docs = load_document(str(file_path))
            all_docs.extend(docs)
        except Exception as e:
            print(f"  [오류] {file_path.name}: {e}")

    if not all_docs:
        raise ValueError("처리할 문서가 없습니다.")

    # 청킹
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " "],
    )
    chunks = splitter.split_documents(all_docs)
    print(f"총 청크 수: {len(chunks)}")

    # 포맷별 통계
    format_counts = {}
    for chunk in chunks:
        fmt = chunk.metadata.get("format", "unknown")
        format_counts[fmt] = format_counts.get(fmt, 0) + 1
    print(f"포맷별 청크 분포: {format_counts}")

    # 인덱싱
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
    vectorstore = FAISS.from_documents(chunks, embedding_model)
    print(f"인덱스 완료: {vectorstore.index.ntotal}개 벡터")
    return vectorstore

# 테스트: 임시 파일들 생성
import tempfile

with tempfile.TemporaryDirectory() as tmpdir:
    tmpdir = Path(tmpdir)

    (tmpdir / "guide.txt").write_text(
        "파이썬 설치 가이드\n\n파이썬 3.10 이상을 python.org에서 다운로드하세요.\npip install 명령으로 패키지를 설치합니다.",
        encoding="utf-8",
    )
    (tmpdir / "readme.md").write_text(
        "# 프로젝트 소개\n\n이 프로젝트는 RAG 파이프라인을 구현합니다.\n\n## 기능\n\n- 문서 인덱싱\n- 질의응답",
        encoding="utf-8",
    )
    (tmpdir / "index.html").write_text(
        "<html><body><h1>제품 소개</h1><p>이 제품은 AI 기반 문서 검색 시스템입니다.</p></body></html>",
        encoding="utf-8",
    )

    vectorstore = process_directory(str(tmpdir))

    # 검색 테스트
    results = vectorstore.similarity_search("파이썬 설치", k=2)
    print("\n검색 결과:")
    for r in results:
        print(f"  [{r.metadata.get('format')}] {r.page_content[:80]}")
```

---

## 마무리

다양한 포맷의 문서를 하나의 파이프라인으로 처리하는 핵심은 공통 인터페이스(`list[Document]`)로 변환하는 것입니다. 포맷별 파서를 라우터로 연결하면 새 포맷을 추가할 때 파서 함수 하나와 LOADER_MAP 한 줄만 추가하면 됩니다.

다음 글에서는 지금까지 다룬 모든 요소를 하나의 프로덕션 파이프라인으로 조합합니다.

<!-- blog-only:start -->
다음 글: [문서 수집 파이프라인 완성](./06-pipeline-completion.md)
<!-- blog-only:end -->

<!-- toc:begin -->
## 시리즈 목차

- [PDF 파싱과 텍스트 추출](./01-pdf-parsing.md)
- [청킹 전략 — 문서 유형별 최적화](./02-chunking-strategies.md)
- [메타데이터 설계와 필터링](./03-metadata-filtering.md)
- [증분 인덱싱 — 변경된 문서만 업데이트](./04-incremental-indexing.md)
- **다중 포맷 문서 파이프라인 (현재 글)**
- 문서 수집 파이프라인 완성 (예정)

<!-- toc:end -->

---

## 참고 자료

- [LangChain DocumentLoaders](https://python.langchain.com/docs/integrations/document_loaders/)
- [Unstructured.io 라이브러리](https://unstructured.io/)
- [python-docx](https://python-docx.readthedocs.io/)

Tags: RAG, Document Processing, LangChain, Python
