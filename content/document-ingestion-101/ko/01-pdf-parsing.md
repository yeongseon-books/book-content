---
title: PDF 파싱과 텍스트 추출
series: document-ingestion-101
episode: 1
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
seo_description: PDF 파싱의 첫 목표는 시각 문서를 검증 가능한 문자열 목록으로 바꾸는 일입니다.
---

# PDF 파싱과 텍스트 추출

문서 수집 파이프라인은 생각보다 훨씬 앞단에서 흔들립니다. 첫 추출 단계가 재현되지 않거나, 추출 결과를 눈으로 확인하기 어렵다면 뒤에서 청킹과 인덱싱을 아무리 정교하게 붙여도 기반이 약합니다.

이 글은 Document Ingestion 101 시리즈의 첫 번째 글입니다. 여기서는 재현 가능한 PDF 샘플을 직접 만들고, 그 PDF에서 어떤 텍스트와 페이지 단위 메타데이터가 나오는지 검증 가능한 형태로 확인합니다.

## 이 글에서 다룰 문제

- 샘플 파일이 없어도 PDF 추출 데모를 어떻게 재현 가능하게 만들 수 있을까요?
- `pypdf`로 페이지별 텍스트와 문자 수를 어떻게 확인할 수 있을까요?
- 문서 수집의 첫 단계에서 어떤 메타데이터를 남겨 두는 편이 좋을까요?

> PDF 파싱의 첫 목표는 시각 문서를 검증 가능한 문자열 목록으로 바꾸는 일입니다.

예제 코드: `en/01-pdf-parsing/main.py`

![Questions this post answers](../../../assets/document-ingestion-101/01/01-01-questions-this-post-answers.ko.png)

*Questions this post answers*

PDF 파싱 튜토리얼에서 가장 먼저 부딪히는 실무 문제는 종종 샘플 파일입니다. 독자가 예제를 처음부터 그대로 재현할 수 없다면, 파이프라인 이야기는 시작부터 마찰을 안고 갑니다.

이 예제는 `reportlab`으로 PDF를 직접 만든 뒤, 그 파일을 `pypdf`로 다시 읽고 페이지별 텍스트 요약을 출력합니다. 문서 수집의 첫 단계는 바로 이런 모양이어야 합니다. 입력도 통제되고, 출력도 사람이 검증할 수 있어야 합니다.

## PDF 파싱 흐름

![PDF generation and extraction flow](../../../assets/document-ingestion-101/01/01-01-pdf-parsing-flow.ko.png)

*PDF generation and extraction flow*

생성과 추출을 한 스크립트에 묶어 두면 예제를 다시 돌리기 쉽고, 출력 검증도 간단해집니다.

## 페이지 구조와 추출 포인트

![Page structure and table detection path](../../../assets/document-ingestion-101/01/01-02-page-structure-and-extraction-points.ko.png)

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

![Page metadata fields per document](../../../assets/document-ingestion-101/01/01-01-how-page-metadata-carries-forward.ko.png)

*Page metadata fields per document*

페이지 번호와 문자 수를 함께 보존해 두면, 이후 청킹과 디버깅 단계에서도 맥락을 훨씬 쉽게 추적할 수 있습니다.

- `create_sample_pdf()`가 입력 데이터를 직접 만들기 때문에 숨겨진 파일 의존성이 없습니다.
- `extract_pages()`는 페이지 번호, 문자 수, 미리보기를 함께 반환하므로 다음 메타데이터 설계 단계와 자연스럽게 연결됩니다.
- 출력이 사람이 읽기 쉬운 형태라서 레이아웃이 깨졌을 때 육안으로 바로 확인할 수 있습니다.

## 실무에서 자주 헷갈리는 지점

### OCR이 대체 경로가 되는 시점

![Text-layer check and OCR fallback flow](../../../assets/document-ingestion-101/01/01-02-when-ocr-becomes-the-fallback.ko.png)

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

<!-- toc:begin -->
## 시리즈 목차

- **PDF 파싱과 텍스트 추출 (현재 글)**
- 청킹 전략 — 문서 유형별 최적화 (예정)
- 메타데이터 설계와 필터링 (예정)
- 증분 인덱싱 — 변경된 문서만 업데이트 (예정)
- 다중 포맷 문서 파이프라인 (예정)
- 문서 수집 파이프라인 완성 (예정)

<!-- toc:end -->

## 참고 자료

- https://pypdf.readthedocs.io/
- https://docs.reportlab.com/reportlab/userguide/ch1_intro/

Tags: RAG, Document Processing, LangChain, Python
