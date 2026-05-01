---
title: 'PDF 파싱과 텍스트 추출'
series: document-ingestion-101
episode: 1
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

# PDF 파싱과 텍스트 추출

> 문서 수집과 인덱싱 101 시리즈 (1/6)

예제 코드: [github.com/yeongseon-books/document-ingestion-101](https://github.com/yeongseon-books/document-ingestion-101/tree/main/ko/01-pdf-parsing)

RAG 파이프라인의 첫 단계는 문서에서 텍스트를 꺼내는 것입니다. 텍스트 파일은 바로 읽으면 되지만, 실무에서 마주치는 문서의 대부분은 PDF입니다. PDF는 텍스트, 이미지, 표, 레이아웃 정보가 뒤섞인 복잡한 포맷이어서 단순 읽기로는 충분하지 않습니다. 이번 글에서는 PDF에서 텍스트를 추출하는 방법을 단계별로 다룹니다.

다룰 내용은 다음과 같습니다.

- pymupdf로 PDF 텍스트 추출
- pypdf 대안 비교
- 페이지별 메타데이터 보존
- 표와 멀티컬럼 레이아웃 처리

---

## PDF 파싱 라이브러리 선택

Python의 주요 PDF 파싱 라이브러리는 세 가지입니다.

**pymupdf** (`fitz`): 가장 빠르고 정확합니다. 텍스트 블록 위치, 폰트 크기, 이미지 정보까지 추출할 수 있습니다. 복잡한 레이아웃에서도 텍스트 순서를 잘 보존합니다.

**pypdf**: 순수 Python 구현으로 의존성이 가볍습니다. 단순한 PDF에는 충분하지만 복잡한 레이아웃에서 텍스트 순서가 깨질 수 있습니다.

**pdfplumber**: 표 추출에 강점이 있습니다. pymupdf보다 느리지만 표가 많은 문서에 적합합니다.

일반적인 RAG 파이프라인에는 pymupdf를 기본으로 사용하고, 표가 많은 문서에는 pdfplumber를 추가합니다.

---

## pymupdf 기본 사용

```bash
pip install pymupdf pypdf pdfplumber langchain-community
```

```python
from pathlib import Path

import fitz  # pymupdf

def extract_text_pymupdf(pdf_path: str) -> list[dict]:
    """
    PDF에서 페이지별 텍스트를 추출합니다.
    각 페이지: {"page_num": int, "text": str, "char_count": int}
    """
    doc = fitz.open(pdf_path)
    pages = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")  # 기본 텍스트 추출
        pages.append({
            "page_num": page_num + 1,
            "text": text.strip(),
            "char_count": len(text.strip()),
        })

    doc.close()
    return pages

def extract_blocks_pymupdf(pdf_path: str) -> list[dict]:
    """
    텍스트 블록 단위로 추출합니다.
    블록: {"page_num", "block_num", "text", "bbox", "block_type"}
    block_type: 0=텍스트, 1=이미지
    """
    doc = fitz.open(pdf_path)
    all_blocks = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text("blocks")

        for block_idx, block in enumerate(blocks):
            x0, y0, x1, y1, text, block_no, block_type = block
            if block_type == 0 and text.strip():  # 텍스트 블록만
                all_blocks.append({
                    "page_num": page_num + 1,
                    "block_num": block_idx,
                    "text": text.strip(),
                    "bbox": (x0, y0, x1, y1),
                    "block_type": block_type,
                })

    doc.close()
    return all_blocks

# 샘플 PDF 생성 (테스트용)
def create_sample_pdf(output_path: str) -> None:
    """테스트용 샘플 PDF를 생성합니다."""
    doc = fitz.open()

    page = doc.new_page()
    page.insert_text(
        (50, 50),
        "파이썬 프로그래밍 가이드\n\n"
        "1장: 소개\n"
        "파이썬은 1991년 귀도 반 로섬이 만든 프로그래밍 언어입니다.\n"
        "가독성을 최우선으로 설계되었으며, 들여쓰기로 코드 블록을 구분합니다.\n\n"
        "2장: 특징\n"
        "동적 타이핑, 자동 메모리 관리, 풍부한 라이브러리가 특징입니다.\n"
        "웹 개발, 데이터 과학, AI 분야에서 널리 사용됩니다.",
        fontsize=12,
        fontname="helv",
    )

    page2 = doc.new_page()
    page2.insert_text(
        (50, 50),
        "3장: 설치\n"
        "python.org에서 최신 버전을 다운로드할 수 있습니다.\n"
        "현재 권장 버전은 Python 3.10 이상입니다.\n\n"
        "4장: 패키지 관리\n"
        "pip install <패키지명> 명령으로 패키지를 설치합니다.\n"
        "가상환경(venv)으로 프로젝트별 의존성을 격리합니다.",
        fontsize=12,
        fontname="helv",
    )

    doc.save(output_path)
    doc.close()
    print(f"샘플 PDF 생성: {output_path}")

create_sample_pdf("/tmp/sample.pdf")
pages = extract_text_pymupdf("/tmp/sample.pdf")
for page in pages:
    print(f"\n=== 페이지 {page['page_num']} ({page['char_count']}자) ===")
    print(page["text"][:200])
```

---

## pypdf 비교

```python
from pypdf import PdfReader

def extract_text_pypdf(pdf_path: str) -> list[dict]:
    """pypdf로 페이지별 텍스트 추출."""
    reader = PdfReader(pdf_path)
    pages = []

    for page_num, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        pages.append({
            "page_num": page_num + 1,
            "text": text.strip(),
            "char_count": len(text.strip()),
        })

    return pages

# 같은 PDF로 비교
pymupdf_pages = extract_text_pymupdf("/tmp/sample.pdf")
pypdf_pages = extract_text_pypdf("/tmp/sample.pdf")

print("pymupdf 추출 문자 수:", sum(p["char_count"] for p in pymupdf_pages))
print("pypdf 추출 문자 수:", sum(p["char_count"] for p in pypdf_pages))
```

---

## PDF 메타데이터 추출

```python
def extract_metadata(pdf_path: str) -> dict:
    """PDF 파일 메타데이터를 추출합니다."""
    doc = fitz.open(pdf_path)

    metadata = {
        "file_path": str(pdf_path),
        "file_name": Path(pdf_path).name,
        "page_count": len(doc),
        "title": doc.metadata.get("title", ""),
        "author": doc.metadata.get("author", ""),
        "subject": doc.metadata.get("subject", ""),
        "creator": doc.metadata.get("creator", ""),
        "creation_date": doc.metadata.get("creationDate", ""),
        "modification_date": doc.metadata.get("modDate", ""),
        "file_size_kb": Path(pdf_path).stat().st_size // 1024,
    }

    doc.close()
    return metadata

meta = extract_metadata("/tmp/sample.pdf")
for key, value in meta.items():
    if value:
        print(f"  {key}: {value}")
```

---

## LangChain DocumentLoader 통합

```python
import os

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

# LangChain의 PyMuPDFLoader 사용
loader = PyMuPDFLoader("/tmp/sample.pdf")
documents = loader.load()

print(f"로드된 페이지 수: {len(documents)}")
for doc in documents:
    print(f"\n페이지 {doc.metadata.get('page', '?')+1}:")
    print(f"  메타데이터: {doc.metadata}")
    print(f"  텍스트 앞 100자: {doc.page_content[:100]}")

# 청킹 + 임베딩 + 인덱싱
splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
chunks = splitter.split_documents(documents)
print(f"\n청크 수: {len(chunks)}")

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

vectorstore = FAISS.from_documents(chunks, embedding_model)
print(f"인덱스 완료: {vectorstore.index.ntotal}개 벡터")
```

---

## 마무리

PDF 파싱에서 가장 중요한 선택은 라이브러리입니다. 대부분의 경우 pymupdf가 속도와 정확도에서 최선입니다. LangChain의 `PyMuPDFLoader`를 사용하면 메타데이터 보존과 청킹을 간편하게 처리할 수 있습니다.

다음 글에서는 청킹 전략을 집중적으로 다룹니다. 문서 유형별로 최적의 청크 크기와 겹침(overlap) 설정을 찾는 방법입니다.

<!-- toc:begin -->
## 시리즈 목차

- **PDF 파싱과 텍스트 추출 (현재 글)**
- 청킹 전략 — 문서 유형별 최적화 (예정)
- 메타데이터 설계와 필터링 (예정)
- 증분 인덱싱 — 변경된 문서만 업데이트 (예정)
- 다중 포맷 문서 파이프라인 (예정)
- 문서 수집 파이프라인 완성 (예정)

<!-- toc:end -->

---

## 참고 자료

- [pymupdf 공식 문서](https://pymupdf.readthedocs.io/)
- [pypdf 공식 문서](https://pypdf.readthedocs.io/)
- [LangChain PyMuPDFLoader](https://python.langchain.com/docs/integrations/document_loaders/pymupdf/)
- [pdfplumber](https://github.com/jsvine/pdfplumber)

Tags: RAG, Document Processing, LangChain, Python
