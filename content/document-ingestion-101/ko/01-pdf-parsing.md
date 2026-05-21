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

이 글은 Document Ingestion 101 시리즈의 첫 번째 글입니다.

여기서는 재현 가능한 PDF 샘플을 직접 만들고, 그 PDF에서 어떤 텍스트와 페이지 단위 메타데이터가 나오는지 검증 가능한 형태로 확인합니다.

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

### PyMuPDF와 pdfplumber를 함께 검증하는 이유

실무 PDF는 텍스트만 뽑는 경로 하나로 끝나지 않는 경우가 많습니다. 같은 파일이라도 라이브러리별로 줄바꿈, 표 셀 경계, 공백 처리 결과가 다르게 나올 수 있기 때문입니다. 그래서 초기에 한 가지 라이브러리만 고정하기보다, 대표 샘플 몇 개를 두고 결과를 비교해 기준선을 정하는 편이 안전합니다.

```python
from __future__ import annotations

from pathlib import Path

import fitz  # PyMuPDF
import pdfplumber

def extract_with_pymupdf(pdf_path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with fitz.open(pdf_path) as doc:
        for page_index in range(doc.page_count):
            page = doc.load_page(page_index)
            text = page.get_text('text').strip()
            rows.append(
                {
                    'page': page_index + 1,
                    'chars': len(text),
                    'preview': text.replace('\n', ' ')[:120],
                    'engine': 'pymupdf',
                }
            )
    return rows

def extract_with_pdfplumber(pdf_path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_index, page in enumerate(pdf.pages, start=1):
            text = (page.extract_text() or '').strip()
            rows.append(
                {
                    'page': page_index,
                    'chars': len(text),
                    'preview': text.replace('\n', ' ')[:120],
                    'engine': 'pdfplumber',
                }
            )
    return rows

def compare_extractors(pdf_path: Path) -> None:
    a = extract_with_pymupdf(pdf_path)
    b = extract_with_pdfplumber(pdf_path)
    for left, right in zip(a, b, strict=True):
        diff = abs(int(left['chars']) - int(right['chars']))
        print(
            f"page={left['page']} pymupdf={left['chars']} pdfplumber={right['chars']} diff={diff}"
        )
```

위 코드는 정답을 고르는 코드가 아니라, **차이를 기록하는 코드**입니다. 페이지별 문자 수 차이가 크게 나는 파일만 우선 수동 검토 대상으로 올리면, 전체 문서를 눈으로 읽지 않고도 위험 샘플을 빠르게 골라낼 수 있습니다.

### 표 추출 결과를 청킹 전에 평탄화하는 패턴

표는 텍스트 추출에서 가장 자주 깨지는 구조입니다. 셀 순서가 바뀌거나 열 머리글이 누락되면, 이후 검색에서 값은 나오지만 의미가 어긋나는 답변이 생깁니다. 그래서 표를 찾았을 때는 원문 문단과 분리해 별도 레코드로 저장하고, 셀을 명시적으로 직렬화하는 편이 좋습니다.

```python
from __future__ import annotations

from pathlib import Path

import pdfplumber

def flatten_table(table: list[list[str | None]], page_number: int, table_index: int) -> str:
    lines: list[str] = []
    for row_index, row in enumerate(table, start=1):
        cells = [cell.strip() if cell else '' for cell in row]
        lines.append(f"row={row_index} | " + ' | '.join(cells))
    header = f"table page={page_number} table_index={table_index}"
    return header + '\n' + '\n'.join(lines)

def extract_tables(pdf_path: Path) -> list[dict[str, object]]:
    table_docs: list[dict[str, object]] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables() or []
            for table_index, table in enumerate(tables, start=1):
                normalized = flatten_table(table, page_number, table_index)
                table_docs.append(
                    {
                        'page': page_number,
                        'table_index': table_index,
                        'content': normalized,
                        'kind': 'table',
                    }
                )
    return table_docs
```

이 방식의 장점은 단순합니다. 표를 문자열 한 덩어리로 잃어버리지 않고, `page`, `table_index`, `kind` 같은 메타데이터와 함께 보존할 수 있습니다. 그러면 청킹 단계에서 표 전용 프리셋을 따로 주거나, 검색 결과를 보여 줄 때 표 출처임을 명확히 표시할 수 있습니다.

### OCR fallback을 조건부로 붙이는 최소 구현

스캔 PDF를 다루면 텍스트 추출만으로 빈 문자열이 나오는 페이지가 반드시 생깁니다. 이때 모든 페이지를 OCR로 보내면 속도와 비용이 커지므로, 먼저 텍스트 레이어 존재 여부를 검사한 뒤 필요한 페이지만 OCR fallback으로 넘기는 전략이 실용적입니다.

```python
from __future__ import annotations

from pathlib import Path

import fitz
import pytesseract

def should_ocr(page_text: str, min_chars: int = 20) -> bool:
    return len(page_text.strip()) < min_chars

def extract_with_ocr_fallback(pdf_path: Path) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    with fitz.open(pdf_path) as doc:
        for page_index in range(doc.page_count):
            page = doc.load_page(page_index)
            text = page.get_text('text').strip()
            path = 'text-layer'
            if should_ocr(text):
                pix = page.get_pixmap(dpi=220)
                ocr_text = pytesseract.image_to_string(
                    bytes(pix.tobytes('png')),
                    lang='kor+eng',
                )
                text = ocr_text.strip()
                path = 'ocr-fallback'
            results.append(
                {
                    'page': page_index + 1,
                    'chars': len(text),
                    'extraction_path': path,
                    'preview': text.replace('\n', ' ')[:100],
                }
            )
    return results
```

핵심은 OCR 자체가 아니라 라우팅 기록입니다. 각 페이지가 `text-layer`로 처리되었는지 `ocr-fallback`으로 처리되었는지를 남겨 두면, 검색 품질이 흔들릴 때 원인을 페이지 단위로 추적하기 쉬워집니다. 또한 OCR 비율이 갑자기 증가하면 업로드 문서 형식이 바뀌었거나 스캔본이 급증한 신호로 볼 수 있습니다.

이렇게 추출 경로, 표 레코드, 페이지 메타데이터를 함께 확보해 두면 다음 단계에서 청크 전략을 문서 타입별로 나눌 근거가 생깁니다. 즉, 파싱 단계에서 만든 관측값이 청킹 단계의 설계 입력으로 이어집니다.

## 실무 확장: 파서 품질 게이트와 파이프라인 연결

PDF 파싱은 한 번 추출해서 끝나는 작업이 아닙니다. 실제 수집 시스템에서는 파싱 결과를 다음 단계로 넘기기 전에 "이 결과를 청킹과 임베딩에 써도 되는지"를 자동으로 판정해야 합니다. 이 품질 게이트가 없으면 OCR fallback 비율이 높아졌을 때도 그대로 인덱싱이 진행되어 검색 품질이 조용히 악화됩니다.

### 파싱 품질 점수를 계산하는 기준

아래 예시는 페이지별 텍스트 길이, 공백 비율, 비가시 문자 비율, OCR 사용 여부를 기준으로 점수를 계산하는 최소 구현입니다. 점수가 기준 이하인 페이지는 즉시 재처리 큐로 보냅니다.

```python
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class ParseQuality:
    page: int
    chars: int
    whitespace_ratio: float
    control_ratio: float
    extraction_path: str

    def score(self) -> float:
        score = 100.0
        if self.chars < 80:
            score -= 25.0
        if self.whitespace_ratio > 0.45:
            score -= 20.0
        if self.control_ratio > 0.03:
            score -= 20.0
        if self.extraction_path == 'ocr-fallback':
            score -= 10.0
        return max(score, 0.0)

def classify_quality(row: ParseQuality) -> str:
    if row.score() >= 85:
        return 'pass'
    if row.score() >= 65:
        return 'review'
    return 'reprocess'
```

이런 기준을 두면 단순히 "텍스트가 나왔다"가 아니라 "검색 가능한 품질의 텍스트가 나왔다"를 자동으로 구분할 수 있습니다. 특히 스캔본 비율이 높은 조직에서는 파싱 성공률보다 `reprocess` 비율 추적이 더 중요한 운영 지표가 됩니다.

### 파싱 산출물을 청킹 입력 계약으로 고정하기

파싱 단계에서 페이지를 문자열로만 넘기면 다음 단계에서 페이지 경계와 출처를 잃기 쉽습니다. 그래서 아래처럼 파싱 결과를 바로 청킹 입력 계약으로 직렬화해 두는 편이 좋습니다.

```python
from __future__ import annotations

from langchain_core.documents import Document

def to_chunk_input(parsed_rows: list[dict[str, object]], source: str) -> list[Document]:
    docs: list[Document] = []
    for row in parsed_rows:
        docs.append(
            Document(
                page_content=str(row['text']).strip(),
                metadata={
                    'source': source,
                    'page': int(row['page']),
                    'extraction_path': str(row.get('extraction_path', 'text-layer')),
                    'parser': str(row.get('parser', 'pymupdf')),
                    'doc_type': 'pdf',
                },
            )
        )
    return docs
```

핵심은 `source`, `page`, `extraction_path` 같은 필드를 파싱 경계에서 이미 고정하는 것입니다. 이렇게 하면 청킹 단계에서 문서 위치를 다시 계산할 필요가 없어지고, 검색 결과에 페이지 출처를 붙이기도 쉬워집니다.

### 표 추출과 본문 추출을 분리 저장하는 메타데이터 스키마

표를 본문과 같은 청킹 정책으로 처리하면 행 경계가 자주 깨집니다. 아래처럼 `content_kind`를 명시하면 표 전용 chunk_size를 적용하기가 훨씬 수월합니다.

```json
{
  "source": "policy-manual.pdf",
  "page": 12,
  "content_kind": "table",
  "table_index": 2,
  "parser": "pdfplumber",
  "text": "row=1 | 항목 | 값\nrow=2 | 보존기간 | 3년"
}
```

본문은 `content_kind=text`, 표는 `content_kind=table`로 분리하면 검색 단계에서 표 질의를 별도 후보군으로 먼저 좁힐 수 있습니다. 이 구조는 나중에 벡터 DB에서 메타데이터 필터를 사용할 때도 그대로 재사용됩니다.

## 운영 노트: PDF 파싱에서 자주 쓰는 점검 쿼리

실무에서는 추출 코드보다 점검 쿼리를 더 자주 실행합니다. 배치가 끝난 뒤 아래 항목을 바로 확인하면 파싱 품질 문제를 초기에 발견할 수 있습니다.

```sql
-- 일자별 페이지 추출 품질 집계 예시
SELECT
  run_date,
  COUNT(*) AS pages,
  SUM(CASE WHEN extraction_path = 'ocr-fallback' THEN 1 ELSE 0 END) AS ocr_pages,
  AVG(char_count) AS avg_chars,
  SUM(CASE WHEN quality_status = 'reprocess' THEN 1 ELSE 0 END) AS reprocess_pages
FROM ingestion_page_metrics
GROUP BY run_date
ORDER BY run_date DESC;
```

이 집계에서 `ocr_pages` 비율이 급증하거나 `avg_chars`가 급락하면 업로드 문서 형태가 바뀌었거나 파서 설정이 깨졌을 가능성이 큽니다. 또한 `reprocess_pages` 비율을 운영 알람으로 연결하면 품질 저하를 인덱싱 전에 차단할 수 있습니다.

PDF 파싱을 안정화하려면 "텍스트를 뽑는다"를 넘어서 "파싱 품질을 측정한다"를 기본 루틴으로 가져가야 합니다. 이 습관이 있어야 다음 단계의 chunking, embedding, vector search가 예측 가능한 입력 위에서 동작합니다.

## 실전 점검 체크리스트 확장

아래 체크리스트는 배포 직전 10분 점검용으로 자주 사용합니다. 문서 수집 파이프라인은 기능이 아니라 경계 검증으로 안정성이 결정되므로, 매 실행에서 같은 항목을 반복 확인하는 습관이 중요합니다.

- 입력 파일 수가 평소 범위에서 크게 벗어나지 않는지 확인합니다.
- 실패 문서 비율이 임계치(예: 3%)를 넘지 않는지 확인합니다.
- 샘플 문서 3건 이상에 대해 source, page, chunk_id 추적이 가능한지 확인합니다.
- 메타데이터 필드 누락(`source`, `format`, `doc_type`)이 0건인지 확인합니다.
- 벡터 검색 샘플 질의에서 기대 출처가 상위 결과에 포함되는지 확인합니다.

```python
def quick_health_report(stats: dict[str, int | float]) -> None:
    print(f"files_total={stats['files_total']}")
    print(f"failed_total={stats['failed_total']}")
    print(f"chunks_total={stats['chunks_total']}")
    print(f"metadata_missing={stats['metadata_missing']}")
    print(f"smoke_passed={stats['smoke_passed']}")
```

이 정도 점검만 자동화해도 "돌아갔다"와 "운영 가능한 상태로 끝났다"를 구분할 수 있습니다. 장기적으로는 이 리포트를 누적해 주간 추세를 보고, 특정 단계에서 실패율이 증가하는 패턴을 조기에 잡는 것이 좋습니다.

## 마무리 운영 기준

문서 수집 파이프라인은 새 기능보다 기준 유지가 더 중요합니다. 그래서 팀 단위 운영에서는 아래 네 가지를 주간 기준으로 고정해 두는 편이 좋습니다.

- 파싱 품질 지표(평균 문자 수, OCR 비율, 재처리 비율)
- 청킹 품질 지표(평균 길이, 극단 길이 비율, 정책 버전 분포)
- 메타데이터 품질 지표(필수 필드 누락률, 정규화 실패 건수)
- 검색 검증 지표(샘플 질의 recall@k, 출처 회수율)

이 네 축을 함께 보면 어느 경계에서 품질이 떨어지는지 빠르게 확인할 수 있습니다. 결국 안정적인 ingestion은 화려한 모델 선택보다, 입력 품질과 단계 계약을 지속적으로 측정하는 운영 루틴에서 만들어집니다.

## 임베딩 파이프라인과의 연결 지점

파싱 산출물이 임베딩 단계로 넘어가는 경계를 정리합니다. 파싱에서 보존한 `page`, `source`, `extraction_path` 필드가 임베딩 결과에도 그대로 전달되어야 검색 시점에 원문 위치를 설명할 수 있습니다. 이 연결이 끊어지면 벡터는 존재하지만 출처를 알 수 없는 유령 청크가 생깁니다.

임베딩 모델을 바꿀 때도 파싱 산출물 형식은 유지되어야 합니다. 모델 교체가 파서 출력까지 바꾸게 만들면 재현성이 무너집니다. 그래서 파싱 → 청킹 → 임베딩 사이에 `Document` 계약을 명시적으로 두고, 각 단계의 책임 범위를 한 문장으로 정의해 두는 습관이 중요합니다.

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

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/document-ingestion-101/ko)

Tags: RAG, Document Processing, LangChain, Python
