---
title: "Document Ingestion 101 (1/6): PDF 파싱과 텍스트 추출"
series: document-ingestion-101
episode: 1
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- RAG
- Document Processing
- LangChain
- Python
last_reviewed: '2026-05-15'
seo_description: PDF 파싱의 첫 목표는 시각 문서를 검증 가능한 문자열 목록으로 바꾸는 일입니다.
---

# Document Ingestion 101 (1/6): PDF 파싱과 텍스트 추출

문서 수집 파이프라인은 생각보다 훨씬 앞단에서 흔들립니다. 첫 추출 단계가 재현되지 않거나, 추출 결과를 눈으로 확인하기 어렵다면 뒤에서 청킹과 인덱싱을 아무리 정교하게 붙여도 기반이 약합니다.

이 글은 Document Ingestion 101 시리즈의 첫 번째 글입니다. 여기서는 재현 가능한 PDF 샘플을 직접 만들고, 그 PDF에서 어떤 텍스트와 페이지 단위 메타데이터가 나오는지 검증 가능한 형태로 확인합니다.

## 먼저 던지는 질문

- PDF 파일은 왜 단순한 텍스트 파일처럼 읽을 수 없을까요?
- 페이지 구조와 메타데이터를 추출 단계에서 보존하지 않으면 RAG에서 무엇이 막힐까요?
- 파싱 결과가 좋아 보일 때도 어떤 검증을 먼저 해야 할까요?

## 큰 그림

![PDF generation and extraction flow](https://yeongseon-books.github.io/book-public-assets/assets/document-ingestion-101/01/01-01-pdf-parsing-flow.ko.png)

*PDF generation and extraction flow*

이 그림에서는 PDF가 페이지 단위 구조와 메타데이터를 가진 문서로 로딩되고, 텍스트 추출 결과가 이후 청킹과 검색의 입력이 되는 흐름을 봅니다. 문서 수집의 첫 실패는 보통 모델이 아니라 원문을 잘못 읽는 경계에서 시작됩니다.

> PDF 파싱의 첫 목표는 시각 문서를 검증 가능한 문자열 목록으로 바꾸는 일입니다.

## PDF 파싱 흐름

생성과 추출을 한 스크립트에 묶어 두면 예제를 다시 돌리기 쉽고, 출력 검증도 간단해집니다.

## 페이지 구조와 추출 포인트

![Page structure and table detection path](https://yeongseon-books.github.io/book-public-assets/assets/document-ingestion-101/01/01-02-page-structure-and-extraction-points.ko.png)

*Page structure and table detection path*

실제 PDF는 순수 텍스트만 담지 않는 경우가 많습니다. 텍스트, 표, 이미지가 섞여 있기 때문에 각 요소가 어떤 경로로 처리되는지에 따라 추출 품질이 달라집니다.

## 실행 예제

```python
# pyright: reportMissingImports=false, reportMissingModuleSource=false
from __future__ import annotations

from pathlib import Path
from typing import TypedDict

from pypdf import PdfReader
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
DATA_DIR.mkdir(exist_ok=True)
PDF_PATH = DATA_DIR / 'sample.pdf'

def create_sample_pdf(pdf_path: Path) -> None:
    c = canvas.Canvas(str(pdf_path), pagesize=A4)
    _, height = A4
    pages = [
        [
            'Document ingestion notes',
            '',
            '1. PDF text extraction is the first pipeline step.',
            '2. pypdf is reliable when the layout is simple.',
            '3. Keeping page numbers in metadata makes debugging easier.',
        ],
        [
            'Operational checks',
            '',
            '1. The script creates its own sample PDF.',
            '2. Re-reading the file should stay reproducible.',
            '3. Verify both page count and extracted character count.',
        ],
    ]
    for page_index, lines in enumerate(pages, start=1):
        y = height - 72
        c.setFont('Helvetica-Bold', 16)
        c.drawString(72, y, f'Page {page_index}')
        y -= 36
        c.setFont('Helvetica', 12)
        for line in lines:
            c.drawString(72, y, line)
            y -= 20
        c.showPage()
    c.save()

class PageSummary(TypedDict):
    page: int
    chars: int
    preview: str

def extract_pages(pdf_path: Path) -> list[PageSummary]:
    reader = PdfReader(str(pdf_path))
    pages: list[PageSummary] = []
    for index, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or '').strip()
        pages.append(
            {
                'page': index,
                'chars': len(text),
                'preview': text.replace('\n', ' ')[:100],
            }
        )
    return pages

def main() -> None:
    create_sample_pdf(PDF_PATH)
    pages = extract_pages(PDF_PATH)
    print(f'created: {PDF_PATH.name}')
    print(f'page_count: {len(pages)}')
    total_chars = sum(int(page['chars']) for page in pages)
    print(f'total_chars: {total_chars}')
    for page in pages:
        print(f"page={page['page']} chars={page['chars']} preview={page['preview']}")

if __name__ == '__main__':
    main()
```

## 실행 방법

```bash
python main.py
```

## 검증된 실행 결과

```text
created: sample.pdf
page_count: 2
total_chars: 363
page=1 chars=190 preview=Page 1 Document ingestion notes ...
page=2 chars=173 preview=Page 2 Operational checks ...
```

## 이 코드에서 먼저 봐야 할 점

### 페이지 메타데이터가 다음 단계로 이어지는 방식

![Page metadata fields per document](https://yeongseon-books.github.io/book-public-assets/assets/document-ingestion-101/01/01-01-how-page-metadata-carries-forward.ko.png)

*Page metadata fields per document*

페이지 번호와 문자 수를 함께 보존해 두면, 이후 청킹과 디버깅 단계에서도 맥락을 훨씬 쉽게 추적할 수 있습니다.

- `create_sample_pdf()`가 입력 데이터를 직접 만들기 때문에 숨겨진 파일 의존성이 없습니다.
- `extract_pages()`는 페이지 번호, 문자 수, 미리보기를 함께 반환하므로 다음 메타데이터 설계 단계와 자연스럽게 연결됩니다.
- 출력이 사람이 읽기 쉬운 형태라서 레이아웃이 깨졌을 때 육안으로 바로 확인할 수 있습니다.

## 실무에서 자주 헷갈리는 지점

### OCR이 대체 경로가 되는 시점

![Text-layer check and OCR fallback flow](https://yeongseon-books.github.io/book-public-assets/assets/document-ingestion-101/01/01-02-when-ocr-becomes-the-fallback.ko.png)

*Text-layer check and OCR fallback flow*

OCR은 모든 PDF의 기본 경로가 아니라, 텍스트 레이어를 확인한 뒤 필요할 때만 쓰는 우회 경로로 두는 편이 안전합니다.

- PDF 파싱과 OCR은 같은 작업이 아닙니다. PDF에 이미 텍스트 레이어가 있다면 먼저 일반 추출 품질부터 확인해야 합니다.
- 문자 수가 많다고 해서 자동으로 품질이 좋은 것은 아닙니다. 읽기 순서와 반복 머리글 문제도 함께 봐야 합니다.
- 복잡한 레이아웃에서는 라이브러리 비교가 필요하지만, 첫 튜토리얼은 재현 가능한 단순 샘플에서 시작하는 편이 좋습니다.

## 체크리스트

- [ ] 스크립트가 PDF를 직접 생성합니다.
- [ ] 페이지 수와 문자 수를 함께 출력합니다.
- [ ] 페이지 미리보기만으로도 추출 순서를 눈으로 검증할 수 있습니다.
- [ ] 다음 단계로 넘길 메타데이터를 정했습니다.

## 정리

이 글의 핵심은 PDF 파싱을 복잡한 라이브러리 비교 문제로 시작하지 않는 데 있습니다. 먼저 재현 가능한 입력을 만들고, 페이지별 텍스트와 문자 수를 확인하고, 사람이 읽을 수 있는 로그를 남겨야 합니다.

여기까지 정리하면 다음 단계로 넘길 최소 계약도 분명해집니다. 페이지 텍스트, 페이지 번호, 문자 수 같은 기본 메타데이터가 확보되어야 이후 청킹과 인덱싱이 흔들리지 않습니다.

## 처음 질문으로 돌아가기

- **PDF 파일은 왜 단순한 텍스트 파일처럼 읽을 수 없을까요?**
  PDF는 화면 배치를 저장한 형식에 가깝기 때문에 읽기 순서, 페이지 경계, 표·머리글·꼬리글 처리가 일반 텍스트보다 복잡합니다.

- **페이지 구조와 메타데이터를 추출 단계에서 보존하지 않으면 RAG에서 무엇이 막힐까요?**
  페이지 번호, source, 섹션 같은 정보가 없으면 검색 결과를 원문 위치로 되돌리거나 답변 출처를 설명하기 어렵습니다.

- **파싱 결과가 좋아 보일 때도 어떤 검증을 먼저 해야 할까요?**
  빈 페이지, 깨진 인코딩, 반복 머리글, 표 순서, 페이지별 문자 수와 메타데이터를 샘플로 확인해야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- **Document Ingestion 101 (1/6): PDF 파싱과 텍스트 추출 (현재 글)**
- Document Ingestion 101 (2/6): 청킹 전략 — 문서 유형별 최적화 (예정)
- Document Ingestion 101 (3/6): 메타데이터 설계와 필터링 (예정)
- Document Ingestion 101 (4/6): 증분 인덱싱 — 변경된 문서만 업데이트 (예정)
- Document Ingestion 101 (5/6): 다중 포맷 문서 파이프라인 (예정)
- Document Ingestion 101 (6/6): 문서 수집 파이프라인 완성 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [pypdf user guide](https://pypdf.readthedocs.io/)
- [ReportLab User Guide - Getting Started](https://docs.reportlab.com/reportlab/userguide/ch1_intro/)

### 검증에 도움 되는 자료

- [pypdf extract-text guide](https://pypdf.readthedocs.io/en/stable/user/extract-text.html)
- [PDF 32000-1:2008 overview (Adobe-hosted index)](https://opensource.adobe.com/dc-acrobat-sdk-docs/standards/pdfstandards/pdf/PDF32000_2008.pdf)

Tags: RAG, Document Processing, LangChain, Python
