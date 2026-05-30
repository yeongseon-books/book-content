---
title: "Document Ingestion 101 (1/6): PDF parsing and text extraction"
series: document-ingestion-101
episode: 1
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
seo_description: The first goal of PDF parsing is to turn a visual document into a
  verifiable list of strings.
---

# Document Ingestion 101 (1/6): PDF parsing and text extraction

Most document ingestion pipelines fail earlier than people expect. If the very first extraction step is hard to reproduce or hard to inspect, every later chunking and indexing discussion rests on shaky ground.

This is the first post in the Document Ingestion 101 series. Here, we start with a reproducible PDF sample and inspect what useful text and page-level metadata come out of it.

![PDF generation and extraction flow](https://yeongseon-books.github.io/book-public-assets/assets/document-ingestion-101/01/01-01-pdf-parsing-flow.en.png)
*PDF generation and extraction flow*
> The first goal of PDF parsing is to turn a visual document into a verifiable list of strings.

## Questions to Keep in Mind

- Why can a PDF not be treated like a plain text file?
- What breaks in RAG when page structure and metadata are not preserved during extraction?
- What should be validated even when extracted text looks good?

## PDF parsing flow

Keeping generation and extraction in one script makes the demo reproducible and the output easy to verify.

## Page structure and extraction points

![Page structure and table detection path](https://yeongseon-books.github.io/book-public-assets/assets/document-ingestion-101/01/01-02-page-structure-and-extraction-points.en.png)

*Page structure and table detection path*
A real PDF often mixes plain text, tables, and images, so extraction quality depends on which branch each page element takes.

## Runnable example

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

## How to run it

```bash
python main.py
```

## Verified run output

```text
created: sample.pdf
page_count: 2
total_chars: 363
page=1 chars=190 preview=Page 1 Document ingestion notes ...
page=2 chars=173 preview=Page 2 Operational checks ...
```

## What to notice in this code

### How page metadata carries forward

![Page metadata fields per document](https://yeongseon-books.github.io/book-public-assets/assets/document-ingestion-101/01/01-01-how-page-metadata-carries-forward.en.png)

*Page metadata fields per document*
Once page number and character count are preserved together, later chunking and debugging steps stay much easier to reason about.

- `create_sample_pdf()` creates the input data, so the example has no hidden file dependency.
- `extract_pages()` returns page number, character count, and preview together, which maps cleanly to later metadata work.
- The output stays human-readable, so layout failures are easy to catch by inspection.

## Where engineers get confused

### When OCR becomes the fallback

![Text-layer check and OCR fallback flow](https://yeongseon-books.github.io/book-public-assets/assets/document-ingestion-101/01/01-02-when-ocr-becomes-the-fallback.en.png)

*Text-layer check and OCR fallback flow*
OCR is safer as a fallback path after a text-layer check, not as the default path for every PDF.

- PDF parsing is not the same as OCR. If the PDF already has a text layer, verify plain extraction first.
- A high character count does not automatically mean high quality. Reading order and repeated headers still matter.
- Complex layouts do require library comparison, but the first tutorial should start with a reproducible simple sample.

## Checklist

- [ ] The script creates its own PDF.
- [ ] It prints both page count and character count.
- [ ] The page preview is enough to verify extraction order by eye.
- [ ] You identified which metadata should flow into the next stage.

## Parse Quality Gate

PDF parsing is not a one-shot task. In a real ingestion system, you need to automatically decide "is this result good enough to pass to chunking and embedding?" before forwarding. Without this gate, a spike in OCR fallback rate silently degrades search quality downstream.

### Quality Score Calculation

Score each page based on text length, whitespace ratio, control character ratio, and extraction path. Pages below threshold go to the reprocessing queue immediately.

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

This lets you distinguish "text was extracted" from "search-quality text was extracted." In organizations with high scan-document ratios, tracking the `reprocess` rate matters more than tracking overall parse success.

### Fixing Parse Output as a Chunk Input Contract

Passing only raw strings to the next stage loses page boundaries and provenance. Serialize parse results into a chunk input contract instead:

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

Fixing `source`, `page`, and `extraction_path` at the parse boundary means the chunking stage never needs to re-derive document positions, and search results can easily cite page-level provenance.

### Separating Table and Body Extraction

Tables processed with the same chunking policy as body text often break row boundaries. Marking `content_kind` explicitly makes it straightforward to apply table-specific chunk sizes.

```json
{
  "source": "policy-manual.pdf",
  "page": 12,
  "content_kind": "table",
  "table_index": 2,
  "parser": "pdfplumber",
  "text": "row=1 | Item | Value\nrow=2 | Retention | 3 years"
}
```

Splitting body (`content_kind=text`) from tables (`content_kind=table`) lets the search layer narrow table queries to a dedicated candidate set first. This metadata structure reuses directly when applying vector DB metadata filters later.

## Operational Inspection Queries

In practice, inspection queries run more often than extraction code. After a batch completes, checking these items catches quality problems early:

```sql
-- Daily page extraction quality summary
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

If `ocr_pages` ratio spikes or `avg_chars` drops sharply, either uploaded document formats changed or parser configuration broke. Wiring `reprocess_pages` ratio to an operational alert blocks quality degradation before indexing proceeds.

Stabilizing PDF parsing requires going beyond "text was extracted" to "parse quality is measured" as a default routine. Only then can downstream chunking, embedding, and vector search operate on predictable input.

## Extended Deployment Checklist

Use this as a 10-minute pre-deployment check. Document ingestion pipelines stabilize through boundary verification rather than feature additions — repeating the same items every run matters.

- Confirm input file count is within normal range.
- Confirm failure document ratio stays below threshold (e.g., 3%).
- Verify source, page, and chunk_id traceability on at least 3 sample documents.
- Confirm zero missing metadata fields (`source`, `format`, `doc_type`).
- Confirm expected sources appear in top results for sample vector search queries.

```python
def quick_health_report(stats: dict[str, int | float]) -> None:
    print(f"files_total={stats['files_total']}")
    print(f"failed_total={stats['failed_total']}")
    print(f"chunks_total={stats['chunks_total']}")
    print(f"metadata_missing={stats['metadata_missing']}")
    print(f"smoke_passed={stats['smoke_passed']}")
```

Automating even this minimal check separates "it ran" from "it finished in an operable state." Over time, accumulate these reports to track weekly trends and catch failure-rate increases at specific stages early.

## Operational Baseline Metrics

Document ingestion pipelines need standard maintenance over new features. Fix these four axes as weekly baselines:

- **Parse quality**: average character count, OCR ratio, reprocess ratio.
- **Chunk quality**: average length, extreme-length ratio, policy version distribution.
- **Metadata quality**: required field missing rate, normalization failure count.
- **Search verification**: sample query recall@k, source retrieval rate.

Monitoring all four together reveals which boundary is degrading. Stable ingestion comes from continuously measuring input quality and stage contracts — not from flashy model selection.

## Comparing PyMuPDF and pdfplumber

Real-world PDFs rarely work with a single extraction path. The same file can produce different line breaks, table cell boundaries, and whitespace handling across libraries. Rather than committing to one library upfront, compare results on representative samples to establish a baseline.

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

This code does not pick a winner — it records differences. Prioritize manual review only for pages where character count diverges significantly. This lets you find risky samples fast without reading every document by eye.

## Table Flattening Before Chunking

Tables are the most frequently broken structure in text extraction. When cell order scrambles or column headers drop, downstream search returns values without correct meaning. Extract tables as separate records with explicit cell serialization:

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

The benefit is straightforward: tables are preserved with `page`, `table_index`, and `kind` metadata intact. The chunking stage can apply a table-specific preset, and search results can clearly indicate table provenance.

## Conditional OCR Fallback

Scanned PDFs inevitably produce empty strings on some pages. Sending every page through OCR is slow and expensive. Check for a text layer first, then route only empty pages to OCR:

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

The key insight is not OCR itself but routing records. Recording whether each page used `text-layer` or `ocr-fallback` makes it easy to trace quality issues page by page when search results degrade. A sudden spike in OCR ratio signals either a format change in uploaded documents or a surge in scanned submissions.

## Connection to the Embedding Pipeline

The parse output flows into the embedding stage. The `page`, `source`, and `extraction_path` fields preserved during parsing must carry through to embedding results — otherwise you get ghost chunks that exist in the vector store but cannot explain their origin.

Even when swapping embedding models, the parse output format should remain stable. If a model change forces parser output changes, reproducibility breaks. Define an explicit `Document` contract between parsing → chunking → embedding, and state each stage's responsibility in one sentence.

## Answering the Opening Questions

- **Why can a PDF not be treated like a plain text file?**
  PDFs are closer to layout documents than plain text, so reading order, page boundaries, tables, headers, and footers need explicit handling.

- **What breaks in RAG when page structure and metadata are not preserved during extraction?**
  Without page numbers, source paths, and section metadata, retrieval results cannot reliably link back to source evidence.

- **What should be validated even when extracted text looks good?**
  Check empty pages, broken encoding, repeated headers, table order, per-page text length, and metadata samples before trusting the output.

<!-- toc:begin -->
## In this series

- **Document Ingestion 101 (1/6): PDF parsing and text extraction (current)**
- Document Ingestion 101 (2/6): Chunking strategies — optimizing by document type (upcoming)
- Document Ingestion 101 (3/6): Metadata design and filtering (upcoming)
- Document Ingestion 101 (4/6): Incremental indexing — updating only changed documents (upcoming)
- Document Ingestion 101 (5/6): Multi-format document pipeline (upcoming)
- Document Ingestion 101 (6/6): Completing the document ingestion pipeline (upcoming)

<!-- toc:end -->

## References

### Official docs

- [pypdf user guide](https://pypdf.readthedocs.io/)
- [ReportLab User Guide - Getting Started](https://docs.reportlab.com/reportlab/userguide/ch1_intro/)

### Verification-friendly sources

- [pypdf extract-text guide](https://pypdf.readthedocs.io/en/stable/user/extract-text.html)
- [PDF 32000-1:2008 overview (Adobe-hosted index)](https://opensource.adobe.com/dc-acrobat-sdk-docs/standards/pdfstandards/pdf/PDF32000_2008.pdf)

Tags: RAG, Document Processing, LangChain, Python
