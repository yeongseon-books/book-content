---
title: 다중 포맷 문서 파이프라인
series: document-ingestion-101
episode: 5
language: ko
status: publish-ready
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
last_reviewed: '2026-05-12'
seo_description: 다중 포맷 파이프라인의 본질은 서로 다른 입력을 하나의 공통 Document 계약으로 수렴시키는 일입니다.
---

# 다중 포맷 문서 파이프라인

실제 문서 수집 작업은 한 파일 형식 안에 머무르지 않습니다. 팀은 보통 PDF, 일반 텍스트 메모, Markdown 문서를 섞어 다루면서도 뒤 단계가 그 차이를 계속 신경 쓰지 않게 만들고 싶어 합니다.

이 글은 Document Ingestion 101 시리즈의 5번째 글입니다. 여기서는 여러 형식을 각자 다른 로더로 읽고, 최종적으로는 하나의 공통 `Document` 계약으로 정규화합니다.

## 이 글에서 다룰 문제

- PDF, TXT, MD를 하나의 파이프라인으로 어떻게 묶을 수 있을까요?
- 로더가 형식마다 달라도 공통 `Document` 형태가 왜 중요할까요?
- 형식 분기와 메타데이터 정규화는 어디에서 처리해야 할까요?

> 다중 포맷 파이프라인의 본질은 서로 다른 입력을 하나의 공통 `Document` 계약으로 밀어 넣는 데 있습니다.

예제 코드: `en/05-multi-format-pipeline/main.py`

![Questions this post answers](../../../assets/document-ingestion-101/05/05-01-questions-this-post-answers.ko.png)

*Questions this post answers*

실제 수집 시스템은 PDF만 다루지 않습니다. 운영 메모는 TXT일 수 있고, 팀 런북은 Markdown일 수 있으며, 외부 보고서는 PDF일 수 있습니다.

이 예제는 세 가지 형식을 각각 따로 읽지만, 모든 출력은 같은 `Document` 구조를 내보냅니다. 그래서 뒤의 청킹과 인덱싱 단계는 파일 형식을 모른 채로도 계속 동작할 수 있습니다.

## 파일 형식별 로더 라우팅

![Loader routing by file format](../../../assets/document-ingestion-101/05/05-01-loader-routing-by-file-format.ko.png)

*Loader routing by file format*

다중 포맷 파이프라인의 첫 단계는 뒤 단계가 파일 형식을 다시 추론하지 않도록 라우팅 책임을 한곳에 모으는 일입니다.

## 형식별 전처리

![Format-specific preprocessing branches](../../../assets/document-ingestion-101/05/05-02-format-specific-preprocessing.ko.png)

*Format-specific preprocessing branches*

전처리 방식은 형식마다 달라도 괜찮습니다. 다만 최종 출력은 하나의 본문 텍스트 계약으로 수렴해야 합니다.

## 실행 예제

```python
# pyright: reportMissingImports=false, reportMissingModuleSource=false
from __future__ import annotations

from pathlib import Path

from langchain_core.documents import Document
from pypdf import PdfReader
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
DATA_DIR.mkdir(exist_ok=True)

def create_pdf(path: Path) -> None:
    c = canvas.Canvas(str(path), pagesize=A4)
    c.setFont('Helvetica', 12)
    c.drawString(72, 780, 'PDF source: incident review and remediation steps.')
    c.drawString(72, 760, 'Store the source format in metadata so later stages stay uniform.')
    c.save()

def seed_files() -> list[Path]:
    pdf_path = DATA_DIR / 'incident.pdf'
    txt_path = DATA_DIR / 'notes.txt'
    md_path = DATA_DIR / 'runbook.md'
    create_pdf(pdf_path)
    txt_path.write_text('TXT source: queue backlog grew overnight. Scale-out reduced latency.\n', encoding='utf-8')
    md_path.write_text('# Runbook\n\nMD source: restart the worker only after checking the dead-letter queue.\n', encoding='utf-8')
    return [pdf_path, txt_path, md_path]

def load_pdf(path: Path) -> list[Document]:
    reader = PdfReader(str(path))
    text = '\n'.join((page.extract_text() or '').strip() for page in reader.pages)
    return [Document(page_content=text, metadata={'source': path.name, 'format': 'pdf'})]

def load_text_like(path: Path, fmt: str) -> list[Document]:
    return [Document(page_content=path.read_text(encoding='utf-8'), metadata={'source': path.name, 'format': fmt})]

def load_document(path: Path) -> list[Document]:
    suffix = path.suffix.lower()
    if suffix == '.pdf':
        return load_pdf(path)
    if suffix == '.txt':
        return load_text_like(path, 'txt')
    if suffix in {'.md', '.markdown'}:
        return load_text_like(path, 'md')
    raise ValueError(f'unsupported format: {suffix}')

def main() -> None:
    for path in seed_files():
        docs = load_document(path)
        for doc in docs:
            preview = doc.page_content.replace('\n', ' ')[:90]
            print(f"source={doc.metadata['source']} format={doc.metadata['format']} preview={preview}")

if __name__ == '__main__':
    main()
```

## 실행 방법

```bash
python main.py
```

## 검증된 실행 결과

```text
source=incident.pdf format=pdf preview=PDF source: incident review and remediation steps. ...
source=notes.txt format=txt preview=TXT source: queue backlog grew overnight. ...
source=runbook.md format=md preview=# Runbook MD source: restart the worker ...
```

## 이 코드에서 먼저 봐야 할 점

### 공통 Document 계약 스키마

![Shared Document contract schema](../../../assets/document-ingestion-101/05/05-01-shared-document-contract-schema.ko.png)

*Shared Document contract schema*

`page_content`, `source`, `format`이 정규화되면 뒤 단계는 훨씬 오래 형식 비종속적으로 유지될 수 있습니다.

- `load_document()`는 확장자 라우팅을 한곳에 모읍니다.
- 모든 로더가 `source`와 `format`을 공통 키로 맞추기 때문에 뒤 코드가 다시 분기하지 않습니다.
- PDF는 `pypdf`, TXT와 MD는 일반 파일 읽기를 쓰지만, 출력 계약은 같습니다.

## 실무에서 자주 헷갈리는 지점

### 파일 형식별 오류 처리

![Format error handling fallback flow](../../../assets/document-ingestion-101/05/05-02-error-handling-across-file-formats.ko.png)

*Format error handling fallback flow*

지원 형식이 늘어날수록, 모든 로더가 똑같이 실패한다고 가정하는 것보다 명시적인 우회 경로를 두는 편이 중요합니다.

- 여러 형식을 지원하는 일의 핵심은 로더 추가보다 메타데이터 키 표준화에 있습니다.
- Markdown은 일반 텍스트처럼 읽을 수 있지만, 헤더를 살린 청킹은 나중에 별도 정책이 필요할 수 있습니다.
- PDF 로더와 텍스트 로더는 반환 단위가 다를 수 있으므로, 계약을 페이지 기준으로 할지 파일 기준으로 할지 먼저 정해야 합니다.

## 체크리스트

- [ ] PDF, TXT, MD를 한 번의 실행에서 처리했습니다.
- [ ] 모든 출력 문서에 `source`와 `format` 메타데이터가 있습니다.
- [ ] 확장자 라우팅이 한 함수에 모여 있습니다.
- [ ] 뒤 단계가 형식별 분기 없이도 동작하는지 확인했습니다.

## 정리

다중 포맷 파이프라인의 핵심은 로더를 많이 붙이는 데 있지 않습니다. 서로 다른 입력을 공통 `Document` 계약으로 수렴시켜서, 뒤 단계가 파일 형식 차이를 잊게 만드는 데 있습니다.

형식별 전처리는 얼마든지 달라질 수 있습니다. 다만 `page_content`, `source`, `format` 같은 공통 계약이 안정적이어야 청킹, 메타데이터 처리, 인덱싱이 단순해집니다. 다음 글에서는 이 계약을 끝까지 이어 붙여 엔드투엔드 파이프라인을 완성해 보겠습니다.

<!-- toc:begin -->
## 시리즈 목차

- [PDF 파싱과 텍스트 추출](./01-pdf-parsing.md)
- [청킹 전략 — 문서 유형별 최적화](./02-chunking-strategies.md)
- [메타데이터 설계와 필터링](./03-metadata-filtering.md)
- [증분 인덱싱 — 변경된 문서만 업데이트](./04-incremental-indexing.md)
- **다중 포맷 문서 파이프라인 (현재 글)**
- 문서 수집 파이프라인 완성 (예정)

<!-- toc:end -->

## 참고 자료

- https://python.langchain.com/docs/concepts/document_loaders/

Tags: RAG, Document Processing, LangChain, Python
